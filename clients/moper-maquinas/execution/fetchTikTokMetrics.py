#!/usr/bin/env python3
"""
Fetch TikTok Metrics — Moper Máquinas

Coleta via TikTok Business API v2:
- Dados da conta (seguidores, likes)
- Performance por vídeo (views, completion rate, fontes de tráfego)

Uso:
    python clients/moper-maquinas/execution/fetchTikTokMetrics.py
    python clients/moper-maquinas/execution/fetchTikTokMetrics.py --save
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CLIENT   = "moper"
TT_BASE  = "https://business-api.tiktok.com/open_api/v1.3"
TIMEOUT  = int(os.getenv("API_TIMEOUT", 30))


def loadConfig() -> Dict:
    token   = os.getenv("MOPER_TIKTOK_ACCESS_TOKEN")
    open_id = os.getenv("MOPER_TIKTOK_OPEN_ID")
    if not token:
        raise EnvironmentError("Defina MOPER_TIKTOK_ACCESS_TOKEN no .env")
    return {"token": token, "open_id": open_id}


def buildSession(token: str):
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    session = requests.Session()
    session.headers.update({"Access-Token": token, "Content-Type": "application/json"})
    retry = Retry(total=3, status_forcelist=[429, 500, 502, 503, 504], backoff_factor=1)
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetchAccountInfo(cfg: Dict) -> Dict:
    """Dados básicos da conta."""
    session = buildSession(cfg["token"])
    r = session.get(f"{TT_BASE}/business/get/", params={
        "business_id": cfg.get("open_id"),
        "fields": json.dumps(["username", "display_name", "profile_image",
                               "followers_count", "likes_count", "video_count"]),
    }, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise ValueError(f"TikTok API erro: {data.get('message')}")
    return data.get("data", {})


def fetchVideoList(cfg: Dict, days: int = 30) -> List[Dict]:
    """Lista vídeos publicados no período."""
    session = buildSession(cfg["token"])
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.utcnow().strftime("%Y-%m-%d")

    r = session.post(f"{TT_BASE}/video/list/", json={
        "business_id": cfg.get("open_id"),
        "filters": {
            "create_time_start": since,
            "create_time_end":   until,
        },
        "fields": [
            "item_id", "create_time", "share_url", "cover_image_url",
            "video_views", "likes", "comments", "shares",
            "average_time_watched", "full_video_watched_rate",
            "total_time_watched", "reach",
            "traffic_source_types",
        ],
        "max_count": 50,
    }, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise ValueError(f"TikTok API erro: {data.get('message')}")
    return data.get("data", {}).get("videos", [])


def enrichVideos(videos: List[Dict]) -> List[Dict]:
    """Normaliza e calcula métricas derivadas."""
    enriched = []
    for v in videos:
        views    = v.get("video_views") or 0
        likes    = v.get("likes") or 0
        comments = v.get("comments") or 0
        shares   = v.get("shares") or 0

        completionRate = v.get("full_video_watched_rate") or 0
        avgWatch       = v.get("average_time_watched") or 0
        engagementRate = round((likes + comments + shares) / views, 4) if views > 0 else 0
        sharesRate     = round(shares / views, 4) if views > 0 else 0

        enriched.append({
            "id":              v.get("item_id"),
            "created_at":      v.get("create_time"),
            "url":             v.get("share_url"),
            "views":           views,
            "likes":           likes,
            "comments":        comments,
            "shares":          shares,
            "engagement_rate": engagementRate,
            "shares_rate":     sharesRate,
            "completion_rate": round(completionRate, 4),
            "avg_watch_sec":   round(avgWatch, 1),
            "reach":           v.get("reach"),
            "traffic_sources": v.get("traffic_source_types", {}),
        })

    return enriched


def fetchTikTokMetrics(days: int = 30) -> Dict[str, Any]:
    cfg = loadConfig()
    ts  = datetime.utcnow().isoformat() + "Z"

    logger.info("Coletando dados da conta TikTok...")
    account = fetchAccountInfo(cfg)
    logger.info(f"  @{account.get('username')} — {account.get('followers_count', 0):,} seguidores")

    logger.info(f"Coletando vídeos dos últimos {days} dias...")
    rawVideos = fetchVideoList(cfg, days=days)
    videos    = enrichVideos(rawVideos)
    logger.info(f"  {len(videos)} vídeos coletados")

    # Análises
    topByViews      = sorted(videos, key=lambda x: x["views"], reverse=True)[:5]
    topByCompletion = sorted(videos, key=lambda x: x["completion_rate"], reverse=True)[:5]
    topByShares     = sorted(videos, key=lambda x: x["shares"], reverse=True)[:5]

    avgCompletion   = round(sum(v["completion_rate"] for v in videos) / len(videos), 4) if videos else 0
    avgEngagement   = round(sum(v["engagement_rate"] for v in videos) / len(videos), 4) if videos else 0
    avgViews        = int(sum(v["views"] for v in videos) / len(videos)) if videos else 0

    # FYP ratio — vídeos onde > 70% vieram do FYP
    fypVideos = [
        v for v in videos
        if v.get("traffic_sources", {}).get("FOR_YOU_PAGE", 0) > 0.7
    ]

    return {
        "status":    "success",
        "client":    CLIENT,
        "platform":  "tiktok",
        "timestamp": ts,
        "period_days": days,
        "account":   account,
        "videos":    videos,
        "analysis": {
            "videos_analyzed":     len(videos),
            "avg_views":           avgViews,
            "avg_completion_rate": avgCompletion,
            "avg_engagement_rate": avgEngagement,
            "fyp_videos_count":    len(fypVideos),
            "top_by_views":        topByViews,
            "top_by_completion":   topByCompletion,
            "top_by_shares":       topByShares,
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    try:
        data = fetchTikTokMetrics(days=args.days)

        if args.save:
            os.makedirs(".tmp/moper", exist_ok=True)
            ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            path = f".tmp/moper/tiktok_{ts}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Salvo em {path}")

        print(json.dumps(data, indent=2, default=str))
        sys.exit(0)

    except EnvironmentError as e:
        logger.error(str(e))
        print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Falha: {e}", exc_info=True)
        print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
