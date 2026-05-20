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
    """Query metrics table for a client in the period.

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

    latest   = rows[-1]
    earliest = rows[0]

    followers       = latest["followers"] or 0
    followers_start = earliest["followers"] if earliest["followers"] is not None else followers

    if len(rows) == 1:
        follower_growth     = 0
        follower_growth_pct = 0.0
    else:
        follower_growth     = followers - followers_start
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
        m = row["metadata"]
        if isinstance(m, str):
            import json as _json
            try:
                m = _json.loads(m)
            except Exception:
                m = {}
        m = m or {}
        return (m.get("like_count") or 0) + (m.get("comments_count") or 0)

    best = max(rows, key=score)
    m = best["metadata"]
    if isinstance(m, str):
        import json as _json
        try:
            m = _json.loads(m)
        except Exception:
            m = {}
    m = m or {}
    return {
        "url":      m.get("permalink", "N/A"),
        "likes":    m.get("like_count", 0),
        "comments": m.get("comments_count", 0),
    }


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
        "top_post_url":        top_post["url"]      if top_post else "N/A",
        "top_post_likes":      top_post["likes"]    if top_post else "N/A",
        "top_post_comments":   top_post["comments"] if top_post else "N/A",
    }


def printConsoleReport(rows: List[Dict], period_days: int, report_date: str):
    """Print formatted report to stdout."""
    print(f"\n{'='*60}")
    print(f"  Relatório Mensal — {report_date} (últimos {period_days} dias)")
    print(f"{'='*60}")
    for row in rows:
        print(f"\nCliente: {row['client']} (@{row['username']})")
        if row["followers"] == "N/A":
            print("  Sem dados no período.")
            continue
        growth = row["follower_growth"]
        growth_str = f"+{growth}" if isinstance(growth, int) and growth >= 0 else str(growth)
        print(f"  Seguidores:    {row['followers']:,}  ({growth_str}, {row['follower_growth_pct']})")
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

    try:
        clients = loadClients(args.client or None)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    period_end   = date.today()
    period_start = period_end - timedelta(days=args.period)
    report_date  = period_end.isoformat()
    output_path  = args.output or f".tmp/exports/report_{period_end.strftime('%Y-%m')}.csv"

    try:
        from execution.dbClient import DbClient
        with DbClient() as db:
            rows = []
            for client in clients:
                username = CLIENT_USERNAMES.get(client, client)
                metrics  = fetchClientMetrics(db, client, period_start, period_end)
                top_post = fetchTopPost(db, client, period_start, period_end)
                rows.append(buildReportRow(client, username, period_start, period_end, metrics, top_post))

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
