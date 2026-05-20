#!/usr/bin/env python3
"""
Auto-refresh Instagram IGAA tokens before expiry.

Checks IGAA tokens for all clients and refreshes them.
Each refresh extends the token for 60 more days.
Should run weekly via cron.

Usage:
    python execution/refreshTokens.py
    python execution/refreshTokens.py --check-only
"""

import argparse
import logging
import os
import re
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv, set_key

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

IGAA_CLIENTS = {
    "moacir": "MOACIR_INSTAGRAM_TOKEN",
    "moper":  "MOPER_INSTAGRAM_TOKEN",
    "laika":  "LAIKA_INSTAGRAM_TOKEN",
}


def refreshIgaaToken(token: str) -> str:
    """Refresh an IGAA token. Returns new token valid for 60 more days."""
    r = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def checkTokenValid(token: str) -> bool:
    """Return True if token responds without error."""
    try:
        r = requests.get(
            "https://graph.instagram.com/me",
            params={"fields": "id,username", "access_token": token},
            timeout=15,
        )
        return r.ok
    except Exception:
        return False


def updateEnvToken(env_var: str, new_token: str):
    """Update a token value in .env file."""
    with open(ENV_PATH, "r") as f:
        content = f.read()
    # Replace the value regardless of quotes
    pattern = rf"^({re.escape(env_var)}=).*$"
    replacement = f"{env_var}={new_token}"
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    with open(ENV_PATH, "w") as f:
        f.write(new_content)


def main():
    parser = argparse.ArgumentParser(description="Renovar tokens IGAA do Instagram")
    parser.add_argument("--check-only", action="store_true", help="Apenas verifica, não renova")
    args = parser.parse_args()

    logger.info(f"refreshTokens | {datetime.now().strftime('%Y-%m-%d %H:%M')} | check-only: {args.check_only}")

    refreshed = 0
    failed = 0
    skipped = 0

    for client, env_var in IGAA_CLIENTS.items():
        token = os.getenv(env_var, "").strip("'\"")

        if not token:
            logger.warning(f"  {client}: token vazio — pulando")
            skipped += 1
            continue

        if not token.startswith("IGAA"):
            logger.info(f"  {client}: token não é IGAA ({token[:10]}...) — pulando (usa Page Token)")
            skipped += 1
            continue

        valid = checkTokenValid(token)
        if not valid:
            logger.error(f"  {client}: token inválido ou expirado!")
            failed += 1
            continue

        if args.check_only:
            logger.info(f"  {client}: token válido ✅")
            continue

        try:
            new_token = refreshIgaaToken(token)
            updateEnvToken(env_var, new_token)
            logger.info(f"  {client}: token renovado ✅ (+60 dias)")
            refreshed += 1
        except Exception as e:
            logger.error(f"  {client}: falha ao renovar — {e}")
            failed += 1

    if not args.check_only:
        logger.info(f"Concluído: {refreshed} renovado(s), {skipped} pulado(s), {failed} falha(s)")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
