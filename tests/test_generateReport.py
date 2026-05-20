import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock


def makeDb(metrics_rows=None, posts_rows=None):
    db = MagicMock()
    def query_side_effect(sql, params=None):
        sql_lower = sql.lower()
        if "from metrics" in sql_lower:
            return metrics_rows or []
        if "from posts" in sql_lower:
            return posts_rows or []
        return []
    db.query.side_effect = query_side_effect
    return db


# --- fetchClientMetrics ---

def test_fetchClientMetrics_returns_latest_followers():
    from execution.generateReport import fetchClientMetrics
    db = makeDb(metrics_rows=[
        {"metric_date": date(2026, 4, 9), "followers": 400, "engagement_rate": Decimal("0.02")},
        {"metric_date": date(2026, 5, 9), "followers": 540, "engagement_rate": Decimal("0.013")},
    ])
    result = fetchClientMetrics(db, "laika", date(2026, 4, 9), date(2026, 5, 9))
    assert result["followers"] == 540


def test_fetchClientMetrics_calculates_growth():
    from execution.generateReport import fetchClientMetrics
    db = makeDb(metrics_rows=[
        {"metric_date": date(2026, 4, 9), "followers": 400, "engagement_rate": Decimal("0.02")},
        {"metric_date": date(2026, 5, 9), "followers": 540, "engagement_rate": Decimal("0.013")},
    ])
    result = fetchClientMetrics(db, "laika", date(2026, 4, 9), date(2026, 5, 9))
    assert result["follower_growth"] == 140
    assert abs(result["follower_growth_pct"] - 35.0) < 0.1


def test_fetchClientMetrics_no_data_returns_none():
    from execution.generateReport import fetchClientMetrics
    db = makeDb(metrics_rows=[])
    result = fetchClientMetrics(db, "laika", date(2026, 4, 9), date(2026, 5, 9))
    assert result is None


def test_fetchClientMetrics_single_snapshot_zero_growth():
    from execution.generateReport import fetchClientMetrics
    db = makeDb(metrics_rows=[
        {"metric_date": date(2026, 5, 9), "followers": 540, "engagement_rate": Decimal("0.013")},
    ])
    result = fetchClientMetrics(db, "laika", date(2026, 4, 9), date(2026, 5, 9))
    assert result["followers"] == 540
    assert result["follower_growth"] == 0
    assert result["follower_growth_pct"] == 0.0


def test_fetchClientMetrics_avg_engagement():
    from execution.generateReport import fetchClientMetrics
    db = makeDb(metrics_rows=[
        {"metric_date": date(2026, 4, 9), "followers": 400, "engagement_rate": Decimal("0.02")},
        {"metric_date": date(2026, 5, 9), "followers": 540, "engagement_rate": Decimal("0.013")},
    ])
    result = fetchClientMetrics(db, "laika", date(2026, 4, 9), date(2026, 5, 9))
    assert abs(result["avg_engagement_rate"] - 0.0165) < 0.0001


# --- fetchTopPost ---

def test_fetchTopPost_returns_highest_engagement_post():
    from execution.generateReport import fetchTopPost
    db = makeDb(posts_rows=[
        {"metadata": {"like_count": 10, "comments_count": 2, "permalink": "https://ig.com/p/A"}, "published_at": datetime(2026, 5, 1, tzinfo=timezone.utc)},
        {"metadata": {"like_count": 87, "comments_count": 5, "permalink": "https://ig.com/p/B"}, "published_at": datetime(2026, 5, 3, tzinfo=timezone.utc)},
        {"metadata": {"like_count": 5,  "comments_count": 0, "permalink": "https://ig.com/p/C"}, "published_at": datetime(2026, 5, 5, tzinfo=timezone.utc)},
    ])
    result = fetchTopPost(db, "moacir", date(2026, 4, 9), date(2026, 5, 9))
    assert result["url"] == "https://ig.com/p/B"
    assert result["likes"] == 87
    assert result["comments"] == 5


def test_fetchTopPost_no_posts_returns_none():
    from execution.generateReport import fetchTopPost
    db = makeDb(posts_rows=[])
    result = fetchTopPost(db, "moacir", date(2026, 4, 9), date(2026, 5, 9))
    assert result is None


# --- buildReportRow ---

def test_buildReportRow_all_data():
    from execution.generateReport import buildReportRow
    row = buildReportRow(
        client="moacir",
        username="moacir.moper",
        period_start=date(2026, 4, 9),
        period_end=date(2026, 5, 9),
        metrics={"followers": 485, "follower_growth": 20, "follower_growth_pct": 4.3, "avg_engagement_rate": 0.082, "total_posts": 5},
        top_post={"url": "https://ig.com/p/X", "likes": 40, "comments": 3},
    )
    assert row["client"] == "moacir"
    assert row["username"] == "moacir.moper"
    assert row["followers"] == 485
    assert row["follower_growth"] == 20
    assert row["top_post_url"] == "https://ig.com/p/X"
    assert row["top_post_likes"] == 40


def test_buildReportRow_no_metrics_uses_na():
    from execution.generateReport import buildReportRow
    row = buildReportRow(
        client="namasa",
        username="namasa.mp",
        period_start=date(2026, 4, 9),
        period_end=date(2026, 5, 9),
        metrics=None,
        top_post=None,
    )
    assert row["followers"] == "N/A"
    assert row["top_post_url"] == "N/A"


# --- writeCsv ---

def test_writeCsv_creates_file_with_correct_columns(tmp_path):
    from execution.generateReport import writeCsv
    rows = [
        {"client": "moacir", "username": "moacir.moper", "period_start": "2026-04-09",
         "period_end": "2026-05-09", "followers": 485, "follower_growth": 20,
         "follower_growth_pct": "4.3%", "avg_engagement_rate": "8.20%", "total_posts": 5,
         "top_post_url": "https://ig.com/p/X", "top_post_likes": 40, "top_post_comments": 3},
    ]
    out = str(tmp_path / "report.csv")
    writeCsv(rows, out)
    with open(out) as f:
        lines = f.readlines()
    assert "client" in lines[0]
    assert "moacir" in lines[1]
