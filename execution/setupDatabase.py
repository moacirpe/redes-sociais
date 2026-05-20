#!/usr/bin/env python3
"""
Database Setup - Create Initial Schema on Neon

Creates all PostgreSQL tables needed for the social media platform.
Safe to run multiple times (uses IF NOT EXISTS).

Usage:
    python execution/setupDatabase.py
"""

import sys
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS social_accounts (
        id              SERIAL PRIMARY KEY,
        platform        VARCHAR(50) NOT NULL,
        account_id      VARCHAR(255) NOT NULL,
        username        VARCHAR(255),
        display_name    VARCHAR(255),
        client          VARCHAR(100),
        access_token    TEXT,
        is_active       BOOLEAN DEFAULT TRUE,
        metadata        JSONB DEFAULT '{}',
        created_at      TIMESTAMPTZ DEFAULT NOW(),
        updated_at      TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE(platform, account_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS posts (
        id              SERIAL PRIMARY KEY,
        platform        VARCHAR(50) NOT NULL,
        post_id         VARCHAR(255),
        client          VARCHAR(100),
        account_id      VARCHAR(255),
        content         TEXT,
        media_urls      TEXT[],
        status          VARCHAR(50) DEFAULT 'published',
        published_at    TIMESTAMPTZ,
        metadata        JSONB DEFAULT '{}',
        collected_at    TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE(platform, post_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS metrics (
        id              SERIAL PRIMARY KEY,
        platform        VARCHAR(50) NOT NULL,
        client          VARCHAR(100) NOT NULL,
        account_id      VARCHAR(255),
        metric_date     DATE NOT NULL,
        followers       INTEGER,
        media_count     INTEGER,
        posts_fetched   INTEGER,
        engagement_rate NUMERIC(8, 6),
        raw_data        JSONB DEFAULT '{}',
        collected_at    TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE(platform, client, metric_date)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS execution_logs (
        id              SERIAL PRIMARY KEY,
        script_name     VARCHAR(255),
        status          VARCHAR(50),
        message         TEXT,
        details         JSONB DEFAULT '{}',
        duration_ms     INTEGER,
        created_at      TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics(metric_date)",
    "CREATE INDEX IF NOT EXISTS idx_metrics_client ON metrics(client)",
    "CREATE INDEX IF NOT EXISTS idx_posts_client ON posts(client)",
    "CREATE INDEX IF NOT EXISTS idx_logs_created ON execution_logs(created_at)",
]


def setupDatabase():
    from execution.dbClient import DbClient

    with DbClient() as db:
        logger.info("Running schema migrations on Neon...")
        for i, stmt in enumerate(SCHEMA, 1):
            sql = stmt.strip()
            preview = sql.split("\n")[0][:80]
            try:
                db.execute(sql)
                logger.info(f"  [{i}/{len(SCHEMA)}] OK: {preview}")
            except Exception as e:
                logger.error(f"  [{i}/{len(SCHEMA)}] FAIL: {preview}")
                logger.error(f"  Error: {e}")
                raise

        tables = db.listTables()
        logger.info(f"\nSchema ready. Tables: {tables}")
        return tables


def main():
    try:
        tables = setupDatabase()
        print(json.dumps({"status": "ok", "tables": tables}, indent=2))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
