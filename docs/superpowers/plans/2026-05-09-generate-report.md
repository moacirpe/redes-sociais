# Monthly Report Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `execution/generateReport.py` that queries Neon PostgreSQL and prints a monthly social media report to console and/or CSV.

**Architecture:** Single script with pure functions for data querying, row building, console rendering, and CSV writing. All DB access via existing `DbClient`. No new dependencies beyond pytest for tests.

**Tech Stack:** Python 3.9, psycopg2-binary (via DbClient), stdlib `csv`/`argparse`/`datetime`, pytest for tests.

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `execution/generateReport.py` | Create | Full report script |
| `tests/__init__.py` | Create | Make tests a package |
| `tests/test_generateReport.py` | Create | Unit tests with mocked DB |
| `requirements.txt` | Modify | Add pytest |

---

### Task 1: Install pytest and create test infrastructure

**Files:**
- Modify: `requirements.txt`
- Create: `tests/__init__.py`

- [ ] **Step 1: Add pytest to requirements.txt**

Open `requirements.txt` and add at the end:
```
# Testing
pytest==8.2.0
```

- [ ] **Step 2: Install pytest**

```bash
.venv/bin/pip install pytest==8.2.0
```

Expected output: `Successfully installed pytest-8.2.0`

- [ ] **Step 3: Create tests package**

```bash
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt tests/__init__.py
git commit -m "chore: add pytest, create tests package"
```

---

### Task 2: Write failing tests for fetchClientMetrics and fetchTopPost

**Files:**
- Create: `tests/test_generateReport.py`

These two functions query the DB — they take a `DbClient` instance so we can pass a mock.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_generateReport.py`:

```python
import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock


# --- helpers ---

def makeDb(metrics_rows=None, posts_rows=None, accounts_rows=None):
    """Return a mock DbClient that returns given rows for each table."""
    db = MagicMock()
    def query_side_effect(sql, params=None):
        sql_lower = sql.lower()
        if "from metrics" in sql_lower:
            return metrics_rows or []
        if "from posts" in sql_lower:
            return posts_rows or []
        if "from social_accounts" in sql_lower:
            return accounts_rows or []
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
         "follower_growth_pct": 4.3, "avg_engagement_rate": "8.20%", "total_posts": 5,
         "top_post_url": "https://ig.com/p/X", "top_post_likes": 40, "top_post_comments": 3},
    ]
    out = str(tmp_path / "report.csv")
    writeCsv(rows, out)
    with open(out) as f:
        lines = f.readlines()
    assert "client" in lines[0]
    assert "moacir" in lines[1]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHONPATH=. .venv/bin/pytest tests/test_generateReport.py -v 2>&1 | tail -20
```

Expected: all tests FAIL with `ImportError: cannot import name 'fetchClientMetrics' from 'execution.generateReport'`

- [ ] **Step 3: Commit**

```bash
git add tests/test_generateReport.py
git commit -m "test: add failing tests for generateReport"
```

---

### Task 3: Implement fetchClientMetrics and fetchTopPost

**Files:**
- Create: `execution/generateReport.py` (partial — only these two functions + imports)

- [ ] **Step 1: Create execution/generateReport.py with the two query functions**

```python
#!/usr/bin/env python3
"""
Monthly Social Media Report

Queries Neon PostgreSQL and prints/exports a summary per client.

Usage:
    python execution/generateReport.py --period 30
    python execution/generateReport.py --period 30 --csv
    python execution/generateReport.py --period 30 --csv --output .tmp/exports/report_2026-05.csv
    python execution/generateReport.py --client moacir --period 30
"""

import os
import sys
import csv
import argparse
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ACTIVE_CLIENTS = ["moacir", "moper", "laika"]

CLIENT_USERNAMES = {
    "moacir": "moacir.moper",
    "moper":  "moper.maquinas",
    "laika":  "espacolaikadourados",
}

CSV_COLUMNS = [
    "client", "username", "period_start", "period_end",
    "followers", "follower_growth", "follower_growth_pct",
    "avg_engagement_rate", "total_posts",
    "top_post_url", "top_post_likes", "top_post_comments",
]


def fetchClientMetrics(db, client: str, since: date, until: date) -> Optional[Dict]:
    """Query metrics table for a client between since..until.

    Returns dict with followers, follower_growth, follower_growth_pct,
    avg_engagement_rate, total_posts — or None if no data.
    """
    rows = db.query(
        """SELECT metric_date, followers, engagement_rate
           FROM metrics
           WHERE client = %s AND metric_date BETWEEN %s AND %s
           ORDER BY metric_date ASC""",
        (client, since, until),
    )
    if not rows:
        return None

    latest = rows[-1]
    earliest = rows[0]

    followers = latest["followers"] or 0
    followers_start = earliest["followers"] or followers

    if len(rows) == 1:
        follower_growth = 0
        follower_growth_pct = 0.0
    else:
        follower_growth = followers - followers_start
        follower_growth_pct = round((follower_growth / followers_start) * 100, 2) if followers_start else 0.0

    rates = [float(r["engagement_rate"]) for r in rows if r["engagement_rate"] is not None]
    avg_engagement_rate = round(sum(rates) / len(rates), 4) if rates else 0.0

    post_count_rows = db.query(
        """SELECT COUNT(*) AS total
           FROM posts
           WHERE client = %s AND published_at BETWEEN %s AND %s""",
        (client, since, until),
    )
    total_posts = post_count_rows[0]["total"] if post_count_rows else 0

    return {
        "followers":           followers,
        "follower_growth":     follower_growth,
        "follower_growth_pct": follower_growth_pct,
        "avg_engagement_rate": avg_engagement_rate,
        "total_posts":         total_posts,
    }


def fetchTopPost(db, client: str, since: date, until: date) -> Optional[Dict]:
    """Return the post with highest like_count + comments_count in the period."""
    rows = db.query(
        """SELECT metadata, published_at
           FROM posts
           WHERE client = %s AND published_at BETWEEN %s AND %s""",
        (client, since, until),
    )
    if not rows:
        return None

    def score(row):
        m = row["metadata"] or {}
        return (m.get("like_count") or 0) + (m.get("comments_count") or 0)

    best = max(rows, key=score)
    m = best["metadata"] or {}
    return {
        "url":      m.get("permalink", "N/A"),
        "likes":    m.get("like_count", 0),
        "comments": m.get("comments_count", 0),
    }
```

- [ ] **Step 2: Run the metrics/top-post tests**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHONPATH=. .venv/bin/pytest tests/test_generateReport.py -k "fetchClientMetrics or fetchTopPost" -v 2>&1 | tail -20
```

Expected: all `fetchClientMetrics` and `fetchTopPost` tests PASS.

- [ ] **Step 3: Commit**

```bash
git add execution/generateReport.py
git commit -m "feat: add fetchClientMetrics and fetchTopPost"
```

---

### Task 4: Implement buildReportRow, printConsoleReport, writeCsv, loadClients, main

**Files:**
- Modify: `execution/generateReport.py` (append remaining functions)

- [ ] **Step 1: Append the remaining functions to execution/generateReport.py**

Add after `fetchTopPost`:

```python

def loadClients(client_filter: Optional[str]) -> List[str]:
    """Return list of clients to process."""
    if client_filter:
        if client_filter not in ACTIVE_CLIENTS:
            raise ValueError(f"Unknown client '{client_filter}'. Valid: {ACTIVE_CLIENTS}")
        return [client_filter]
    return ACTIVE_CLIENTS


def buildReportRow(
    client: str,
    username: str,
    period_start: date,
    period_end: date,
    metrics: Optional[Dict],
    top_post: Optional[Dict],
) -> Dict:
    """Normalize all client data into a flat CSV-ready dict."""
    if metrics is None:
        return {
            "client":              client,
            "username":            username,
            "period_start":        period_start.isoformat(),
            "period_end":          period_end.isoformat(),
            "followers":           "N/A",
            "follower_growth":     "N/A",
            "follower_growth_pct": "N/A",
            "avg_engagement_rate": "N/A",
            "total_posts":         "N/A",
            "top_post_url":        "N/A",
            "top_post_likes":      "N/A",
            "top_post_comments":   "N/A",
        }
    return {
        "client":              client,
        "username":            username,
        "period_start":        period_start.isoformat(),
        "period_end":          period_end.isoformat(),
        "followers":           metrics["followers"],
        "follower_growth":     metrics["follower_growth"],
        "follower_growth_pct": f"{metrics['follower_growth_pct']:.1f}%",
        "avg_engagement_rate": f"{metrics['avg_engagement_rate'] * 100:.2f}%",
        "total_posts":         metrics["total_posts"],
        "top_post_url":        top_post["url"] if top_post else "N/A",
        "top_post_likes":      top_post["likes"] if top_post else "N/A",
        "top_post_comments":   top_post["comments"] if top_post else "N/A",
    }


def printConsoleReport(rows: List[Dict], period_days: int, report_date: str):
    """Print formatted report to stdout."""
    print(f"\n{'='*60}")
    print(f"  Relatório Mensal — {report_date} (últimos {period_days} dias)")
    print(f"{'='*60}")
    for row in rows:
        username = row["username"]
        print(f"\nCliente: {row['client']} (@{username})")
        if row["followers"] == "N/A":
            print("  Sem dados no período.")
            continue
        growth = row["follower_growth"]
        growth_pct = row["follower_growth_pct"]
        growth_str = f"+{growth}" if isinstance(growth, int) and growth >= 0 else str(growth)
        print(f"  Seguidores:    {row['followers']:,}  ({growth_str}, {growth_pct})")
        print(f"  Engajamento:   {row['avg_engagement_rate']}  (média do período)")
        print(f"  Posts:         {row['total_posts']}")
        if row["top_post_url"] != "N/A":
            print(f"  Top post:      {row['top_post_url']} ({row['top_post_likes']} likes, {row['top_post_comments']} comentários)")
    print()


def writeCsv(rows: List[Dict], output_path: str):
    """Write rows to CSV file, creating parent dirs if needed."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"CSV salvo em: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Relatório mensal de redes sociais")
    parser.add_argument("--period", type=int, default=30, help="Dias do período (padrão: 30)")
    parser.add_argument("--csv",    action="store_true",   help="Exportar CSV")
    parser.add_argument("--output", type=str, default="",  help="Caminho do CSV")
    parser.add_argument("--client", type=str, default="",  help="Filtrar por cliente")
    args = parser.parse_args()

    clients = loadClients(args.client or None)
    period_end   = date.today()
    period_start = period_end - timedelta(days=args.period)
    report_date  = period_end.isoformat()

    output_path = args.output or f".tmp/exports/report_{period_end.strftime('%Y-%m')}.csv"

    try:
        from execution.dbClient import DbClient
        with DbClient() as db:
            rows = []
            for client in clients:
                username = CLIENT_USERNAMES.get(client, client)
                metrics  = fetchClientMetrics(db, client, period_start, period_end)
                top_post = fetchTopPost(db, client, period_start, period_end)
                row = buildReportRow(client, username, period_start, period_end, metrics, top_post)
                rows.append(row)

        printConsoleReport(rows, args.period, report_date)

        if args.csv:
            writeCsv(rows, output_path)

    except EnvironmentError as e:
        logger.error(f"Config error: {e}")
        logger.error("Verifique DATABASE_URL no .env")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run all tests**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHONPATH=. .venv/bin/pytest tests/test_generateReport.py -v 2>&1 | tail -25
```

Expected: all tests PASS.

- [ ] **Step 3: Commit**

```bash
git add execution/generateReport.py
git commit -m "feat: complete generateReport with console + CSV output"
```

---

### Task 5: Integration test against real Neon data

**Files:** None — run only.

- [ ] **Step 1: Run console report**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHONPATH=. .venv/bin/python execution/generateReport.py --period 30 2>&1 | grep -v NotOpenSSL | grep -v warnings
```

Expected: report printed for moacir, moper, laika. No errors. Clients with only one snapshot show 0% growth (normal — not a bug).

- [ ] **Step 2: Run with CSV export**

```bash
PYTHONPATH=. .venv/bin/python execution/generateReport.py --period 30 --csv 2>&1 | grep -v NotOpenSSL | grep -v warnings
cat .tmp/exports/report_2026-05.csv
```

Expected: CSV created with header + 3 rows (one per client).

- [ ] **Step 3: Update HANDOFF.md**

In `HANDOFF.md`, change:
```
| moacir | Relatório mensal | `[2-E]` | DB pronto — pode implementar |
```
to:
```
| moacir | Relatório mensal | `[5-T]` ✅ | Pronto — console + CSV |
```

- [ ] **Step 4: Commit**

```bash
git add HANDOFF.md
git commit -m "docs: mark monthly report as [5-T] complete"
```

---

## Self-Review Notes

- `fetchClientMetrics` queries `posts` for `total_posts` count — this is a second `db.query` call inside the function. The mock in tests uses `query_side_effect` that checks `"from posts"` vs `"from metrics"`. This is consistent.
- `buildReportRow` formats `avg_engagement_rate` as `"8.20%"` string — consistent with `printConsoleReport` which prints it directly.
- `follower_growth_pct` in `buildReportRow` is a formatted string like `"4.3%"`, but in `printConsoleReport` it's used as-is. Consistent.
- `writeCsv` uses `CSV_COLUMNS` fieldnames — all keys in `buildReportRow` output match exactly.
- `published_at` in the posts table is `timestamptz`. Passing a `date` object to `BETWEEN %s AND %s` works in PostgreSQL (it casts date to `timestamp 00:00:00`). The end-of-day edge case is acceptable for a monthly report.
