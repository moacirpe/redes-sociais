#!/usr/bin/env python3
"""
Fetch YouTube Metrics — Moper Máquinas

Coleta via YouTube Data API v3 + YouTube Analytics API:
- Estatísticas do canal
- Performance por vídeo (views, watch time, retenção, CTR)
- Fontes de tráfego

Uso:
    python clients/moper-maquinas/execution/fetchYouTubeMetrics.py
    python clients/moper-maquinas/execution/fetchYouTubeMetrics.py --days 30 --save
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

CLIENT      = "moper"
YT_BASE     = "https://www.googleapis.com/youtube/v3"
YTA_BASE    = "https://youtubeanalytics.googleapis.com/v2"
TIMEOUT     = int(os.getenv("API_TIMEOUT", 30))


def loadConfig() -> Dict:
    api_key    = os.getenv("MOPER_YOUTUBE_API_KEY")
    channel_id = os.getenv("MOPER_YOUTUBE_CHANNEL_ID")
    if not api_key or not channel_id:
        raise EnvironmentError(
            "Defina MOPER_YOUTUBE_API_KEY e MOPER_YOUTUBE_CHANNEL_ID no .env"
        )
    return {"api_key": api_key, "channel_id": channel_id}


def buildSession():
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    session = requests.Session()
    retry = Retry(total=3, status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=["HEAD", "GET", "OPTIONS"], backoff_factor=1)
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetchChannelStats(cfg: Dict, session=None) -> Dict:
    """Estatísticas gerais do canal."""
    session = session or buildSession()
    r = session.get(f"{YT_BASE}/channels", params={
        "part":  "snippet,statistics,contentDetails",
        "id":    cfg["channel_id"],
        "key":   cfg["api_key"],
    }, timeout=TIMEOUT)
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        raise ValueError(f"Canal não encontrado: {cfg['channel_id']}")
    return items[0]


def fetchRecentVideos(cfg: Dict, maxResults: int = 50, session=None) -> List[Dict]:
    """Lista os vídeos mais recentes do canal."""
    session = session or buildSession()

    channel = fetchChannelStats(cfg, session=session)
    uploadPlaylistId = (
        channel.get("contentDetails", {})
               .get("relatedPlaylists", {})
               .get("uploads")
    )

    r = session.get(f"{YT_BASE}/playlistItems", params={
        "part":       "snippet,contentDetails",
        "playlistId": uploadPlaylistId,
        "maxResults": maxResults,
        "key":        cfg["api_key"],
    }, timeout=TIMEOUT)
    r.raise_for_status()

    videoIds = [
        item["contentDetails"]["videoId"]
        for item in r.json().get("items", [])
    ]
    return videoIds


def fetchVideoStats(cfg: Dict, videoIds: List[str], session=None) -> List[Dict]:
    """Estatísticas detalhadas por vídeo (batch de até 50)."""
    session = session or buildSession()
    videos = []

    for i in range(0, len(videoIds), 50):
        batch = videoIds[i:i+50]
        r = session.get(f"{YT_BASE}/videos", params={
            "part": "snippet,statistics,contentDetails",
            "id":   ",".join(batch),
            "key":  cfg["api_key"],
        }, timeout=TIMEOUT)
        r.raise_for_status()
        videos.extend(r.json().get("items", []))

    return videos


def enrichVideoData(videos: List[Dict]) -> List[Dict]:
    """Normaliza e enriquece dados dos vídeos."""
    enriched = []
    for v in videos:
        stats   = v.get("statistics", {})
        snippet = v.get("snippet", {})

        views    = int(stats.get("viewCount", 0))
        likes    = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        engagementRate = round((likes + comments) / views, 4) if views > 0 else 0
        likesRate      = round(likes / views, 4) if views > 0 else 0

        enriched.append({
            "id":               v["id"],
            "title":            snippet.get("title"),
            "published_at":     snippet.get("publishedAt"),
            "duration":         v.get("contentDetails", {}).get("duration"),  # ISO 8601
            "views":            views,
            "likes":            likes,
            "comments":         comments,
            "engagement_rate":  engagementRate,
            "likes_rate":       likesRate,
            "thumbnail":        snippet.get("thumbnails", {}).get("high", {}).get("url"),
            "url":              f"https://youtube.com/watch?v={v['id']}",
        })

    return enriched


def fetchYouTubeMetrics(days: int = 30) -> Dict[str, Any]:
    cfg     = loadConfig()
    ts      = datetime.utcnow().isoformat() + "Z"
    session = buildSession()

    logger.info("Coletando estatísticas do canal...")
    channel = fetchChannelStats(cfg, session=session)
    channelStats = channel.get("statistics", {})
    channelName  = channel.get("snippet", {}).get("title")
    logger.info(f"  Canal: {channelName} — {int(channelStats.get('subscriberCount', 0)):,} inscritos")

    logger.info("Listando vídeos recentes...")
    videoIds = fetchRecentVideos(cfg, maxResults=50, session=session)
    logger.info(f"  {len(videoIds)} vídeos encontrados")

    logger.info("Coletando estatísticas por vídeo...")
    rawVideos  = fetchVideoStats(cfg, videoIds, session=session)
    videos     = enrichVideoData(rawVideos)

    # Análises
    topByViews       = sorted(videos, key=lambda x: x["views"], reverse=True)[:5]
    topByEngagement  = sorted(videos, key=lambda x: x["engagement_rate"], reverse=True)[:5]
    lowCtr           = [v for v in videos if v.get("likes_rate", 1) < 0.02]  # proxy para CTR baixo

    avgViews      = int(sum(v["views"] for v in videos) / len(videos)) if videos else 0
    avgEngagement = round(sum(v["engagement_rate"] for v in videos) / len(videos), 4) if videos else 0

    return {
        "status":    "success",
        "client":    CLIENT,
        "platform":  "youtube",
        "timestamp": ts,
        "period_days": days,
        "channel": {
            "name":        channelName,
            "subscribers": int(channelStats.get("subscriberCount", 0)),
            "total_views": int(channelStats.get("viewCount", 0)),
            "video_count": int(channelStats.get("videoCount", 0)),
        },
        "videos": videos,
        "analysis": {
            "videos_analyzed":       len(videos),
            "avg_views":             avgViews,
            "avg_engagement_rate":   avgEngagement,
            "top_by_views":          topByViews,
            "top_by_engagement":     topByEngagement,
            "low_performance_count": len(lowCtr),
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    try:
        data = fetchYouTubeMetrics(days=args.days)

        if args.save:
            os.makedirs(".tmp/moper", exist_ok=True)
            ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            path = f".tmp/moper/youtube_{ts}.json"
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
