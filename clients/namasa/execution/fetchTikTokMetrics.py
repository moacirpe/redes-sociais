#!/usr/bin/env python3
"""
Fetch TikTok Metrics — Namasa

Uso:
    python clients/namasa/execution/fetchTikTokMetrics.py --save
"""

import os, sys, json, logging, argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CLIENT  = "namasa"
TT_BASE = "https://business-api.tiktok.com/open_api/v1.3"
TIMEOUT = int(os.getenv("API_TIMEOUT", 30))


def loadConfig():
    token = os.getenv("NAMASA_TIKTOK_ACCESS_TOKEN")
    if not token:
        raise EnvironmentError("Defina NAMASA_TIKTOK_ACCESS_TOKEN no .env")
    return {"token": token, "open_id": os.getenv("NAMASA_TIKTOK_OPEN_ID")}


def buildSession(token):
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    s = requests.Session()
    s.headers.update({"Access-Token": token, "Content-Type": "application/json"})
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, status_forcelist=[429, 500, 502, 503, 504], backoff_factor=1)))
    return s


def fetchAccount(cfg):
    r = buildSession(cfg["token"]).get(f"{TT_BASE}/business/get/", params={
        "business_id": cfg.get("open_id"),
        "fields": json.dumps(["username","display_name","followers_count","likes_count","video_count"])
    }, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise ValueError(f"TikTok API erro: {data.get('message')}")
    return data.get("data", {})


def fetchVideos(cfg, days=30):
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.utcnow().strftime("%Y-%m-%d")
    r = buildSession(cfg["token"]).post(f"{TT_BASE}/video/list/", json={
        "business_id": cfg.get("open_id"),
        "filters": {"create_time_start": since, "create_time_end": until},
        "fields": ["item_id","create_time","share_url","video_views","likes",
                   "comments","shares","average_time_watched","full_video_watched_rate",
                   "reach","traffic_source_types"],
        "max_count": 50,
    }, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise ValueError(f"TikTok API erro: {data.get('message')}")
    return data.get("data", {}).get("videos", [])


def enrichVideos(videos):
    result = []
    for v in videos:
        views    = v.get("video_views") or 0
        likes    = v.get("likes") or 0
        comments = v.get("comments") or 0
        shares   = v.get("shares") or 0
        result.append({
            "id":              v.get("item_id"),
            "created_at":      v.get("create_time"),
            "url":             v.get("share_url"),
            "views":           views, "likes": likes,
            "comments":        comments, "shares": shares,
            "engagement_rate": round((likes + comments + shares) / views, 4) if views > 0 else 0,
            "shares_rate":     round(shares / views, 4) if views > 0 else 0,
            "completion_rate": round(v.get("full_video_watched_rate") or 0, 4),
            "avg_watch_sec":   round(v.get("average_time_watched") or 0, 1),
            "reach":           v.get("reach"),
            "traffic_sources": v.get("traffic_source_types", {}),
        })
    return result


def fetchTikTokMetrics(days=30):
    cfg     = loadConfig()
    ts      = datetime.utcnow().isoformat() + "Z"
    account = fetchAccount(cfg)
    logger.info(f"@{account.get('username')} — {account.get('followers_count', 0):,} seguidores")

    videos   = enrichVideos(fetchVideos(cfg, days=days))
    logger.info(f"{len(videos)} vídeos coletados")

    topViews = sorted(videos, key=lambda x: x["views"], reverse=True)[:5]
    topComp  = sorted(videos, key=lambda x: x["completion_rate"], reverse=True)[:5]
    avgComp  = round(sum(v["completion_rate"] for v in videos) / len(videos), 4) if videos else 0
    avgEng   = round(sum(v["engagement_rate"] for v in videos) / len(videos), 4) if videos else 0
    avgViews = int(sum(v["views"] for v in videos) / len(videos)) if videos else 0
    fypCount = len([v for v in videos if v.get("traffic_sources", {}).get("FOR_YOU_PAGE", 0) > 0.7])

    return {
        "status": "success", "client": CLIENT, "platform": "tiktok",
        "timestamp": ts, "period_days": days,
        "account": account, "videos": videos,
        "analysis": {
            "videos_analyzed":     len(videos),
            "avg_views":           avgViews,
            "avg_completion_rate": avgComp,
            "avg_engagement_rate": avgEng,
            "fyp_videos_count":    fypCount,
            "top_by_views":        topViews,
            "top_by_completion":   topComp,
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
            os.makedirs(f".tmp/{CLIENT}", exist_ok=True)
            ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            path = f".tmp/{CLIENT}/tiktok_{ts}.json"
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
