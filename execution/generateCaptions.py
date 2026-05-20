#!/usr/bin/env python3
"""
Generate Instagram captions using Claude AI.

Reads client briefing + top posts from Neon, calls Claude API,
appends draft captions to queue/{client}/queue.csv.

Usage:
    python execution/generateCaptions.py --client moacir --count 5
    python execution/generateCaptions.py --client moper --count 3 --theme "promoção de maio"
"""

import csv
import json
import logging
import os
import re
import sys
import argparse
from datetime import datetime
from typing import List
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ACTIVE_CLIENTS = ["moacir", "moper", "laika", "namasa"]

CLIENT_BRIEFING_DIRS = {
    "moacir":  "clients/moacir",
    "moper":   "clients/moper-maquinas",
    "laika":   "clients/espaco-laika",
    "namasa":  "clients/namasa",
}

CSV_COLUMNS = [
    "id", "client", "platform", "scheduled_at", "caption",
    "media_filename", "status", "cloudinary_url", "ig_post_url",
    "generated_at", "published_at", "error",
]


def loadBriefing(client: str) -> str:
    briefing_path = os.path.join(CLIENT_BRIEFING_DIRS[client], "briefing.md")
    if not os.path.exists(briefing_path):
        raise FileNotFoundError(f"Briefing não encontrado: {briefing_path}")
    with open(briefing_path, encoding="utf-8") as f:
        return f.read()


def fetchTopPosts(db, client: str, limit: int = 10) -> list:
    return db.query(
        """SELECT content, metadata FROM posts
           WHERE client = %s AND metadata IS NOT NULL AND content != ''
           ORDER BY (
               COALESCE(CAST(metadata->>'like_count' AS INTEGER), 0) +
               COALESCE(CAST(metadata->>'comments_count' AS INTEGER), 0)
           ) DESC
           LIMIT %s""",
        (client, limit),
    )


def buildPrompt(briefing: str, top_posts: list, count: int, theme: str = "") -> str:
    lines = [
        f"- {p['content'][:200]} (likes: {(p['metadata'] or {}).get('like_count', 0)}, "
        f"comments: {(p['metadata'] or {}).get('comments_count', 0)})"
        for p in top_posts[:10] if p.get("content")
    ]
    posts_text = "\n".join(lines) or "Sem posts anteriores disponíveis."

    theme_section = f"\nTEMA DESTA SEMANA: {theme}" if theme else ""

    return f"""Você é um especialista em redes sociais. Gere {count} legendas para Instagram Reels.

BRIEFING DO CLIENTE:
{briefing}

TOP POSTS (inspire-se no estilo, não copie):
{posts_text}
{theme_section}

Retorne APENAS um JSON válido com esta estrutura (sem texto antes ou depois):
[{{"caption": "legenda completa com emojis e hashtags", "hashtags": "#tag1 #tag2"}}]

Gere exatamente {count} itens no array."""


def parseCaptionsResponse(response_text: str) -> list:
    """Extract JSON list from Claude response text."""
    def _parse(text: str) -> list:
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
        if match:
            return json.loads(match.group(1))
        raise ValueError(f"Não foi possível parsear JSON da resposta: {text[:300]}")

    result = _parse(response_text)
    if not isinstance(result, list):
        raise ValueError(f"Resposta esperada como lista JSON, recebeu: {type(result).__name__}")
    return [item for item in result if isinstance(item, dict) and item.get("caption", "").strip()]


def nextRowId(queue_path: str, client: str) -> str:
    """Generate next sequential ID like moacir-001."""
    if not os.path.exists(queue_path):
        return f"{client}-001"
    with open(queue_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return f"{client}-{len(rows) + 1:03d}"


def appendToQueue(queue_path: str, rows: list):
    """Append rows to CSV, creating with header if file doesn't exist."""
    file_exists = os.path.exists(queue_path)
    os.makedirs(os.path.dirname(queue_path) or ".", exist_ok=True)
    with open(queue_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Gerar legendas via Claude AI")
    parser.add_argument("--client", required=True, choices=ACTIVE_CLIENTS)
    parser.add_argument("--count",  type=int, default=5)
    parser.add_argument("--theme",  type=str, default="")
    args = parser.parse_args()

    if not 1 <= args.count <= 20:
        logger.error("--count deve ser entre 1 e 20")
        sys.exit(1)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY não encontrado no .env")
        sys.exit(1)

    briefing = loadBriefing(args.client)
    logger.info(f"Briefing carregado para {args.client}")

    from execution.dbClient import DbClient
    with DbClient() as db:
        top_posts = fetchTopPosts(db, args.client)
    logger.info(f"{len(top_posts)} top posts consultados")

    prompt = buildPrompt(briefing, top_posts, args.count, args.theme)

    import anthropic
    client_ai = anthropic.Anthropic(api_key=api_key)
    logger.info("Chamando Claude API...")
    message = client_ai.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    captions = parseCaptionsResponse(message.content[0].text)
    logger.info(f"{len(captions)} legendas geradas")

    queue_path = os.path.join("queue", args.client, "queue.csv")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    first_id = nextRowId(queue_path, args.client)
    start_n  = int(first_id.split("-")[-1])

    rows = []
    for i, cap in enumerate(captions):
        full_caption = cap.get("caption", "")
        hashtags = cap.get("hashtags", "")
        if hashtags and hashtags not in full_caption:
            full_caption = f"{full_caption}\n\n{hashtags}"
        rows.append({
            "id":             f"{args.client}-{(start_n + i):03d}",
            "client":         args.client,
            "platform":       "instagram",
            "scheduled_at":   "",
            "caption":        full_caption,
            "media_filename": "",
            "status":         "draft",
            "cloudinary_url": "",
            "ig_post_url":    "",
            "generated_at":   now,
            "published_at":   "",
            "error":          "",
        })

    appendToQueue(queue_path, rows)
    logger.info(f"✅ {len(rows)} rascunhos salvos em {queue_path}")

    try:
        from execution.sheetsClient import appendRows, getSheetId
        getSheetId(args.client)
        appendRows(args.client, rows)
        sheet_id = getSheetId(args.client)
        logger.info(f"✅ {len(rows)} rascunhos enviados para Google Sheets")
        print(f"\nAbra no Google Sheets para revisar e aprovar:")
        print(f"  https://docs.google.com/spreadsheets/d/{sheet_id}\n")
    except Exception as e:
        logger.warning(f"Google Sheets não disponível, usando CSV: {e}")
        print(f"\nAbra o arquivo no Google Sheets para revisar e aprovar:")
        print(f"  {os.path.abspath(queue_path)}\n")


if __name__ == "__main__":
    main()
