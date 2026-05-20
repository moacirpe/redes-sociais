#!/usr/bin/env python3
"""
Fetch YouTube Metrics — Namasa

Uso:
    python clients/namasa/execution/fetchYouTubeMetrics.py --save
"""

import os, sys, json, logging, argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CLIENT  = "namasa"
YT_BASE = "https://www.googleapis.com/youtube/v3"
TIMEOUT = int(os.getenv("API_TIMEOUT", 30))


def loadConfig():
    key = os.getenv("NAMASA_YOUTUBE_API_KEY")
    ch  = os.getenv("NAMASA_YOUTUBE_CHANNEL_ID")
    if not key or not ch:
        raise EnvironmentError("Defina NAMASA_YOUTUBE_API_KEY e NAMASA_YOUTUBE_CHANNEL_ID no .env")
    return {"api_key": key, "channel_id": ch}


def buildSession():
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, status_forcelist=[429, 500, 502, 503, 504], backoff_factor=1)))
    return s


def fetchChannel(cfg):
    r = buildSession().get(f"{YT_BASE}/channels", params={
        "part": "snippet,statistics,contentDetails",
        "id": cfg["channel_id"], "key": cfg["api_key"]}, timeout=TIMEOUT)
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        raise ValueError(f"Canal não encontrado: {cfg['channel_id']}")
    return items[0]


def fetchVideoIds(cfg, channel, maxResults=50):
    uploadId = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    r = buildSession().get(f"{YT_BASE}/playlistItems", params={
        "part": "contentDetails", "playlistId": uploadId,
        "maxResults": maxResults, "key": cfg["api_key"]}, timeout=TIMEOUT)
    r.raise_for_status()
    return [i["contentDetails"]["videoId"] for i in r.json().get("items", [])]


def fetchVideoStats(cfg, videoIds):
    session = buildSession()
    videos  = []
    for i in range(0, len(videoIds), 50):
        batch = videoIds[i:i+50]
        r = session.get(f"{YT_BASE}/videos", params={
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch), "key": cfg["api_key"]}, timeout=TIMEOUT)
        r.raise_for_status()
        videos.extend(r.json().get("items", []))
    return videos


def enrichVideos(videos):
    enriched = []
    for v in videos:
        stats    = v.get("statistics", {})
        views    = int(stats.get("viewCount", 0))
        likes    = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        enriched.append({
            "id":             v["id"],
            "title":          v["snippet"].get("title"),
            "published_at":   v["snippet"].get("publishedAt"),
            "duration":       v.get("contentDetails", {}).get("duration"),
            "views":          views,
            "likes":          likes,
            "comments":       comments,
            "engagement_rate":round((likes + comments) / views, 4) if views > 0 else 0,
            "likes_rate":     round(likes / views, 4) if views > 0 else 0,
            "url":            f"https://youtube.com/watch?v={v['id']}",
        })
    return enriched


def fetchYouTubeMetrics(days=30):
    cfg     = loadConfig()
    ts      = datetime.utcnow().isoformat() + "Z"
    channel = fetchChannel(cfg)
    stats   = channel.get("statistics", {})
    name    = channel["snippet"]["title"]
    logger.info(f"{name} — {int(stats.get('subscriberCount', 0)):,} inscritos")

    videoIds = fetchVideoIds(cfg, channel)
    videos   = enrichVideos(fetchVideoStats(cfg, videoIds))
    logger.info(f"{len(videos)} vídeos coletados")

    topViews = sorted(videos, key=lambda x: x["views"], reverse=True)[:5]
    topEng   = sorted(videos, key=lambda x: x["engagement_rate"], reverse=True)[:5]
    avgViews = int(sum(v["views"] for v in videos) / len(videos)) if videos else 0
    avgEng   = round(sum(v["engagement_rate"] for v in videos) / len(videos), 4) if videos else 0
    lowCtr   = len([v for v in videos if v["likes_rate"] < 0.02])

    return {
        "status": "success", "client": CLIENT, "platform": "youtube",
        "timestamp": ts, "period_days": days,
        "channel": {
            "name": name,
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
        },
        "videos": videos,
        "analysis": {
            "videos_analyzed":       len(videos),
            "avg_views":             avgViews,
            "avg_engagement_rate":   avgEng,
            "low_performance_count": lowCtr,
            "top_by_views":          topViews,
            "top_by_engagement":     topEng,
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
            os.makedirs(f".tmp/{CLIENT}", exist_ok=True)
            ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            path = f".tmp/{CLIENT}/youtube_{ts}.json"
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
        logger.error(str(e), exc_info=True)
        print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
