#!/usr/bin/env python3
"""
Fetch Instagram Metrics — Espaço Laika

Idêntico ao script da Moper, com credenciais LAIKA_*.
Foco adicional em saves e compartilhamentos (indicadores de comunidade).

Uso:
    python clients/espaco-laika/execution/fetchInstagramMetrics.py --save
"""

import os, sys, json, logging, argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CLIENT  = "laika"
TIMEOUT = int(os.getenv("API_TIMEOUT", 30))


def getApiBase(token: str) -> str:
    return "https://graph.instagram.com" if token.startswith("IGAA") else "https://graph.facebook.com/v19.0"


def loadConfig() -> Dict:
    token   = os.getenv("LAIKA_INSTAGRAM_TOKEN", "").strip("'\"")
    acct_id = os.getenv("LAIKA_INSTAGRAM_ACCOUNT_ID", "").strip("'\"")
    if not token or not acct_id:
        raise EnvironmentError("Defina LAIKA_INSTAGRAM_TOKEN e LAIKA_INSTAGRAM_ACCOUNT_ID no .env")
    return {"token": token, "account_id": acct_id, "api_base": getApiBase(token)}


def buildSession():
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1, respect_retry_after_header=True
    )))
    return s


def fetchProfile(cfg, session=None):
    session = session or buildSession()
    r = session.get(f"{cfg['api_base']}/{cfg['account_id']}", params={
        "fields": "id,name,username,followers_count,media_count,biography,website",
        "access_token": cfg["token"]}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def fetchPosts(cfg, limit=30, session=None):
    session = session or buildSession()
    r = session.get(f"{cfg['api_base']}/{cfg['account_id']}/media", params={
        "fields": ("id,caption,media_type,timestamp,permalink,"
                   "like_count,comments_count,shares_count,saved,"
                   "reach,impressions,plays,video_views"),
        "limit": limit, "access_token": cfg["token"]}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("data", [])


def fetchInsights(cfg, period=30, session=None):
    session = session or buildSession()
    since = int((datetime.utcnow() - timedelta(days=period)).timestamp())
    until = int(datetime.utcnow().timestamp())
    r = session.get(f"{cfg['api_base']}/{cfg['account_id']}/insights", params={
        "metric": "impressions,reach,profile_views,follower_count,accounts_engaged",
        "period": "day", "since": since, "until": until,
        "access_token": cfg["token"]}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def calcEngagementRate(post, followers):
    reach = post.get("reach") or followers or 1
    total = sum([
        post.get("like_count") or 0,
        post.get("comments_count") or 0,
        post.get("shares_count") or 0,
        post.get("saved") or 0,
    ])
    return round(total / reach, 4)


def fetchInstagramMetrics(period=30):
    cfg     = loadConfig()
    ts      = datetime.utcnow().isoformat() + "Z"
    session = buildSession()

    logger.info("Coletando perfil...")
    profile   = fetchProfile(cfg, session=session)
    followers = profile.get("followers_count", 0)
    logger.info(f"  @{profile.get('username')} — {followers:,} seguidores")

    logger.info("Coletando posts...")
    posts = fetchPosts(cfg, session=session)
    for p in posts:
        p["engagement_rate"] = calcEngagementRate(p, followers)
    logger.info(f"  {len(posts)} posts")

    logger.info("Coletando insights...")
    insights = fetchInsights(cfg, period, session=session)

    reels     = [p for p in posts if p.get("media_type") == "VIDEO"]
    topEng    = sorted(posts, key=lambda x: x["engagement_rate"], reverse=True)[:5]
    topSaves  = sorted(posts, key=lambda x: x.get("saved") or 0, reverse=True)[:5]
    topShares = sorted(posts, key=lambda x: x.get("shares_count") or 0, reverse=True)[:5]
    topReels  = sorted(reels, key=lambda x: x.get("plays") or 0, reverse=True)[:5]
    avgEng    = round(sum(p["engagement_rate"] for p in posts) / len(posts), 4) if posts else 0

    return {
        "status": "success", "client": CLIENT, "platform": "instagram",
        "timestamp": ts, "period_days": period,
        "profile": profile, "posts": posts, "insights": insights,
        "analysis": {
            "total_posts": len(posts), "total_reels": len(reels),
            "avg_engagement_rate": avgEng,
            "top_by_engagement": topEng,
            "top_by_saves":      topSaves,
            "top_by_shares":     topShares,
            "top_reels_by_plays": topReels,
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", type=int, default=30)
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    try:
        data = fetchInstagramMetrics(period=args.period)
        if args.save:
            os.makedirs(".tmp/laika", exist_ok=True)
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            path = f".tmp/laika/instagram_{ts}.json"
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
