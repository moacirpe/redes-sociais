#!/usr/bin/env python3
"""
Publish scheduled Instagram posts from queue CSV.

Reads queue/{client}/queue.csv, uploads media to Cloudinary,
publishes via Instagram Graph API, updates CSV with result.

Usage:
    python execution/publishScheduled.py
    python execution/publishScheduled.py --client moacir
    python execution/publishScheduled.py --dry-run
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ACTIVE_CLIENTS  = ["moacir", "moper", "laika", "namasa"]
POLLING_INTERVAL = 10   # seconds between status checks
POLLING_TIMEOUT  = 300  # 5 minutes max wait for video processing

from execution.generateCaptions import CSV_COLUMNS
from execution.fetchInstagramData import loadConfig


def detectMediaType(filename: str) -> str:
    """Return REELS for video files, IMAGE for photos."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".mp4", ".mov"):
        return "REELS"
    return "IMAGE"


def isDue(row: Dict) -> bool:
    """Return True if row is approved and scheduled_at <= now."""
    if row.get("status") != "approved":
        return False
    scheduled_str = row.get("scheduled_at", "").strip()
    if not scheduled_str:
        return False
    try:
        return datetime.strptime(scheduled_str, "%Y-%m-%d %H:%M") <= datetime.now()
    except ValueError:
        logger.warning(f"scheduled_at inválido: {scheduled_str}")
        return False


def readQueue(queue_path: str) -> List[Dict]:
    """Read all rows from queue CSV. Returns empty list if file missing."""
    if not os.path.exists(queue_path):
        return []
    with open(queue_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def writeQueue(queue_path: str, rows: List[Dict]):
    """Overwrite queue CSV with given rows."""
    with open(queue_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def configureCloudinary():
    """Configure Cloudinary from .env. Raises EnvironmentError if missing."""
    import cloudinary
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key    = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    if not all([cloud_name, api_key, api_secret]):
        raise EnvironmentError(
            "Credenciais Cloudinary ausentes. Configure CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET no .env"
        )
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)


def uploadToCloudinary(media_path: str) -> str:
    """Upload file to Cloudinary and return secure public URL."""
    import cloudinary.uploader
    result = cloudinary.uploader.upload(
        media_path,
        resource_type="auto",
        folder="redes-sociais",
    )
    return result["secure_url"]


def createMediaContainer(config: Dict, caption: str, media_url: str, media_type: str) -> str:
    """Create Instagram media container. Returns creation_id."""
    url    = f"{config['api_base']}/{config['account_id']}/media"
    params = {"access_token": config["token"]}
    data   = {"caption": caption}
    if media_type == "REELS":
        data.update({"media_type": "REELS", "video_url": media_url, "share_to_feed": "true"})
    else:
        data.update({"image_url": media_url})
    r = requests.post(url, params=params, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["id"]


def waitForContainer(config: Dict, creation_id: str) -> bool:
    """Poll until container status is FINISHED. Raises on error or timeout."""
    url      = f"{config['api_base']}/{creation_id}"
    params   = {"fields": "status_code", "access_token": config["token"]}
    deadline = time.time() + POLLING_TIMEOUT
    while time.time() < deadline:
        r = requests.get(url, params=params, timeout=30)
        if r.ok:
            status = r.json().get("status_code", "")
            if status == "FINISHED":
                return True
            if status == "ERROR":
                raise RuntimeError(f"Container processing failed: {r.json()}")
        else:
            logger.warning(f"Status poll failed ({r.status_code}): {r.text[:200]}")
        time.sleep(POLLING_INTERVAL)
    raise TimeoutError(f"Video processing timeout after {POLLING_TIMEOUT}s")


def publishContainer(config: Dict, creation_id: str) -> str:
    """Publish the container. Returns IG media ID."""
    url = f"{config['api_base']}/{config['account_id']}/media_publish"
    r   = requests.post(
        url,
        params={"access_token": config["token"]},
        data={"creation_id": creation_id},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["id"]


def getPostUrl(config: Dict, media_id: str) -> str:
    """Fetch permalink for a published post."""
    url = f"{config['api_base']}/{media_id}"
    r   = requests.get(url, params={"fields": "permalink", "access_token": config["token"]}, timeout=30)
    if not r.ok:
        logger.warning(f"getPostUrl failed ({r.status_code}): {r.text[:200]}")
        return ""
    return r.json().get("permalink", "")


def publishPost(config: Dict, row: Dict, media_path: str, dry_run: bool) -> Dict:
    """Execute full publish flow for one row. Returns updated row dict."""
    if dry_run:
        logger.info(
            f"  [DRY-RUN] {row['client']} | {row['scheduled_at']} | "
            f"{row['caption'][:60]}... | {row['media_filename']}"
        )
        return row

    updated = dict(row)
    try:
        logger.info(f"  Uploading {row['media_filename']} to Cloudinary...")
        cloudinary_url         = uploadToCloudinary(media_path)
        updated["cloudinary_url"] = cloudinary_url

        media_type  = detectMediaType(row["media_filename"])
        creation_id = createMediaContainer(config, row["caption"], cloudinary_url, media_type)
        logger.info(f"  Container criado: {creation_id}")

        if media_type == "REELS":
            logger.info("  Aguardando processamento do vídeo...")
            waitForContainer(config, creation_id)
        else:
            time.sleep(4)

        media_id = publishContainer(config, creation_id)
        ig_url   = getPostUrl(config, media_id)

        updated["status"]       = "published"
        updated["ig_post_url"]  = ig_url
        updated["published_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        updated["error"]        = ""
        logger.info(f"  ✅ Publicado: {ig_url}")

    except Exception as e:
        updated["status"] = "failed"
        updated["error"]  = str(e)[:500]
        logger.error(f"  ❌ Falha: {e}")

    return updated


def logToNeon(client: str, published: int, failed: int, duration_ms: int):
    try:
        from execution.dbClient import DbClient
        with DbClient() as db:
            db.execute(
                """INSERT INTO execution_logs (script_name, status, message, details, duration_ms)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    "publishScheduled",
                    "success" if failed == 0 else "partial",
                    f"Published {published}, failed {failed} for {client}",
                    json.dumps({"client": client, "published": published, "failed": failed}),
                    duration_ms,
                ),
            )
    except Exception as e:
        logger.warning(f"Neon log failed (non-fatal): {e}")


def loadRowsFromSheets(client: str):
    """Try to load rows from Google Sheets. Returns (rows, use_sheets) tuple."""
    try:
        from execution.sheetsClient import readRows, getSheetId
        getSheetId(client)
        rows = readRows(client)
        return rows, True
    except Exception as e:
        logger.debug(f"Google Sheets indisponível para {client}: {e}")
        return None, False


def saveRowsToSheets(client: str, rows: List[Dict]):
    try:
        from execution.sheetsClient import writeAllRows
        writeAllRows(client, rows)
    except Exception as e:
        logger.warning(f"Falha ao salvar no Sheets: {e}")


def processClient(client: str, dry_run: bool):
    """Process all due posts for one client."""
    queue_path  = os.path.join("queue", client, "queue.csv")
    sheet_rows, use_sheets = loadRowsFromSheets(client)
    rows = sheet_rows if use_sheets else readQueue(queue_path)
    due  = [(i, row) for i, row in enumerate(rows) if isDue(row)]

    if not due:
        logger.info(f"  {client}: nenhum post agendado para publicar")
        return

    logger.info(f"  {client}: {len(due)} post(s) para publicar")

    try:
        config = loadConfig(client)
    except EnvironmentError as e:
        logger.error(f"  {client}: config error — {e}")
        return

    published = 0
    failed    = 0
    start     = datetime.utcnow()

    for idx, row in due:
        if not row.get("media_filename", "").strip():
            logger.error(f"  media_filename vazio para post {row.get('id')} — pulando")
            rows[idx]["status"] = "failed"
            rows[idx]["error"]  = "media_filename vazio"
            failed += 1
            if use_sheets:
                saveRowsToSheets(client, rows)
            else:
                writeQueue(queue_path, rows)
            continue

        media_path = os.path.join("queue", client, "media", row["media_filename"])
        if not os.path.exists(media_path) and not dry_run:
            logger.error(f"  Mídia não encontrada: {media_path}")
            rows[idx]["status"] = "failed"
            rows[idx]["error"]  = f"Arquivo não encontrado: {media_path}"
            failed += 1
            if use_sheets:
                saveRowsToSheets(client, rows)
            else:
                writeQueue(queue_path, rows)
            continue

        rows[idx] = publishPost(config, row, media_path, dry_run)
        if not dry_run:
            if rows[idx]["status"] == "published":
                published += 1
            elif rows[idx]["status"] == "failed":
                failed += 1
            if use_sheets:
                saveRowsToSheets(client, rows)
            else:
                writeQueue(queue_path, rows)

    if not dry_run:
        duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
        logToNeon(client, published, failed, duration_ms)
        logger.info(f"  {client}: {published} publicado(s), {failed} falha(s)")


def main():
    parser = argparse.ArgumentParser(description="Publicar posts agendados")
    parser.add_argument("--client",  type=str, default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dry_run:
        try:
            configureCloudinary()
        except EnvironmentError as e:
            logger.error(str(e))
            sys.exit(1)

    if args.client and args.client not in ACTIVE_CLIENTS:
        logger.error(f"Cliente inválido '{args.client}'. Válidos: {ACTIVE_CLIENTS}")
        sys.exit(1)

    clients = [args.client] if args.client else ACTIVE_CLIENTS
    logger.info(f"publishScheduled | clientes: {clients} | dry-run: {args.dry_run}")

    for client in clients:
        logger.info(f"Processando: {client}")
        processClient(client, args.dry_run)

    logger.info("Concluído.")


if __name__ == "__main__":
    main()
