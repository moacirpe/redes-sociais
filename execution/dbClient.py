#!/usr/bin/env python3
"""
Database Client - Neon PostgreSQL

Connects directly to Neon (cloud PostgreSQL) via DATABASE_URL from .env.
No SSH tunnel or VPS needed.

Usage:
    from execution.dbClient import DbClient

    with DbClient() as db:
        db.execute("INSERT INTO logs (msg) VALUES (%s)", ("hello",))
        rows = db.query("SELECT * FROM metrics LIMIT 5")
"""

import os
import time
import logging
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_CONNECT_RETRIES = 3
_CONNECT_DELAY   = 2  # seconds between retries


class DbClient:
    """PostgreSQL client connecting via DATABASE_URL. No SSH tunnel needed."""

    def __init__(self):
        self._conn = None
        self._connect()

    def _connect(self):
        import psycopg2

        url = os.getenv("DATABASE_URL")
        if not url:
            raise EnvironmentError("Missing DATABASE_URL in .env")

        last_err = None
        for attempt in range(1, _CONNECT_RETRIES + 1):
            try:
                self._conn = psycopg2.connect(url)
                self._conn.autocommit = False
                logger.info("Neon PostgreSQL connection established")
                return
            except Exception as e:
                last_err = e
                if attempt < _CONNECT_RETRIES:
                    logger.warning(f"DB connect attempt {attempt} failed, retrying in {_CONNECT_DELAY}s: {e}")
                    time.sleep(_CONNECT_DELAY)
        raise EnvironmentError(f"Failed to connect to Neon after {_CONNECT_RETRIES} attempts: {last_err}")

    def query(self, sql: str, params: Tuple = None) -> List[Dict]:
        """Run SELECT and return list of dicts."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(sql, params)
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def execute(self, sql: str, params: Tuple = None) -> int:
        """Run INSERT/UPDATE/DELETE. Returns rows affected."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(sql, params)
            affected = cursor.rowcount
            self._conn.commit()
            return affected
        except Exception as e:
            self._conn.rollback()
            logger.error(f"DB error: {e}")
            raise
        finally:
            cursor.close()

    def executemany(self, sql: str, paramsList: List[Tuple]) -> int:
        """Bulk insert/update."""
        cursor = self._conn.cursor()
        try:
            cursor.executemany(sql, paramsList)
            affected = cursor.rowcount
            self._conn.commit()
            return affected
        except Exception as e:
            self._conn.rollback()
            logger.error(f"DB bulk error: {e}")
            raise
        finally:
            cursor.close()

    _ALLOWED_TABLES = {"social_accounts", "posts", "metrics", "execution_logs"}

    def upsert(self, table: str, conflictCols: List[str], data: Dict) -> int:
        """INSERT ... ON CONFLICT DO UPDATE. Returns rows affected."""
        if table not in self._ALLOWED_TABLES:
            raise ValueError(f"upsert: table '{table}' not in allowed list {self._ALLOWED_TABLES}")
        cols = list(data.keys())
        vals = list(data.values())
        placeholders = ", ".join(["%s"] * len(cols))
        colNames = ", ".join(cols)
        updateClause = ", ".join([f"{c} = EXCLUDED.{c}" for c in cols if c not in conflictCols])
        conflictClause = ", ".join(conflictCols)
        sql = (
            f"INSERT INTO {table} ({colNames}) VALUES ({placeholders}) "
            f"ON CONFLICT ({conflictClause}) DO UPDATE SET {updateClause}"
        )
        return self.execute(sql, tuple(vals))

    def listTables(self) -> List[str]:
        rows = self.query(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
        )
        return [r["table_name"] for r in rows]

    def ping(self) -> bool:
        try:
            self.query("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"DB ping failed: {e}")
            raise

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("DB connection closed")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
