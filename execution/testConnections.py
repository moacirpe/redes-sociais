#!/usr/bin/env python3
"""
Connection Test Suite

Tests all infrastructure connections:
- Environment variables
- Neon PostgreSQL

Usage:
    python execution/testConnections.py
"""

import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PASS = "✅"
FAIL = "❌"
SKIP = "⏭️ "

results = {}


def testEnv():
    label = "Environment"
    allVars = {
        "Neon PostgreSQL":     ["DATABASE_URL"],
        "Instagram (moacir)":  ["MOACIR_INSTAGRAM_TOKEN", "MOACIR_INSTAGRAM_ACCOUNT_ID"],
        "Instagram (moper)":   ["MOPER_INSTAGRAM_TOKEN",  "MOPER_INSTAGRAM_ACCOUNT_ID"],
        "Instagram (laika)":   ["LAIKA_INSTAGRAM_TOKEN",  "LAIKA_INSTAGRAM_ACCOUNT_ID"],
        "Cloudinary":          ["CLOUDINARY_CLOUD_NAME",  "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"],
        "Claude AI":           ["ANTHROPIC_API_KEY"],
        "Meta App":            ["META_APP_ID", "META_APP_SECRET"],
    }

    summary = {}
    for group, keys in allVars.items():
        filled = [k for k in keys if os.getenv(k)]
        missing = [k for k in keys if not os.getenv(k)]
        summary[group] = {"filled": filled, "missing": missing}

    allFilled  = [k for g in allVars.values() for k in g if os.getenv(k)]
    allMissing = [k for g in allVars.values() for k in g if not os.getenv(k)]

    logger.info(f"{PASS} {label}: {len(allFilled)} vars set, {len(allMissing)} missing")
    for group, s in summary.items():
        status = PASS if not s["missing"] else "⚠️ "
        logger.info(f"  {status} {group}: {len(s['filled'])}/{len(s['filled']) + len(s['missing'])} vars set")
        if s["missing"]:
            logger.info(f"     Missing: {s['missing']}")

    results[label] = {"status": "ok", "summary": summary}


def testNeon():
    label = "Neon PostgreSQL"
    try:
        url = os.getenv("DATABASE_URL")
        if not url:
            logger.warning(f"{SKIP} {label}: DATABASE_URL not set in .env")
            results[label] = {"status": "skipped", "reason": "DATABASE_URL not set"}
            return

        from execution.dbClient import DbClient
        with DbClient() as db:
            db.ping()
            tables = db.listTables()
            logger.info(f"{PASS} {label}: connected OK")
            logger.info(f"  Tables: {tables if tables else '(empty — run setupDatabase.py)'}")
            results[label] = {"status": "ok", "tables": tables}

    except EnvironmentError as e:
        logger.warning(f"{SKIP} {label}: {e}")
        results[label] = {"status": "skipped", "reason": str(e)}
    except Exception as e:
        logger.error(f"{FAIL} {label}: {e}")
        results[label] = {"status": "fail", "error": str(e)}


def main():
    print("\n" + "=" * 60)
    print("   REDES SOCIAIS — Connection Test Suite")
    print("=" * 60 + "\n")

    testEnv()
    print()
    testNeon()

    print("\n" + "=" * 60)
    print("   RESULTS SUMMARY")
    print("=" * 60)

    for label, res in results.items():
        icon = {"ok": PASS, "skipped": SKIP, "fail": FAIL}.get(res["status"], "?")
        print(f"  {icon} {label}: {res['status'].upper()}")

    failed = [k for k, v in results.items() if v["status"] == "fail"]
    if failed:
        print(f"\n{FAIL} Some connections failed: {failed}")
        sys.exit(1)
    else:
        print(f"\n{PASS} All configured connections OK!")
        sys.exit(0)


if __name__ == "__main__":
    main()
