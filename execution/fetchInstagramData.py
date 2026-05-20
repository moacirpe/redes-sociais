#!/usr/bin/env python3
"""
Fetch Instagram Data

Retrieves follower count, engagement metrics, and recent posts
from Instagram Business Account via Graph API.

Reads credentials from .env. No copy-paste needed.

Usage:
    python execution/fetchInstagramData.py
    python execution/fetchInstagramData.py --period 7
    python execution/fetchInstagramData.py --save
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

# ============================================================================
# CONFIG
# ============================================================================

MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 30))


def getApiBase(token: str) -> str:
    """IGAA tokens use graph.instagram.com; EAA page tokens use graph.facebook.com."""
    if token.startswith("IGAA"):
        return "https://graph.instagram.com"
    return "https://graph.facebook.com/v19.0"

CLIENT_ENV_MAP = {
    "moacir": ("MOACIR_INSTAGRAM_TOKEN",  "MOACIR_INSTAGRAM_ACCOUNT_ID"),
    "moper":  ("MOPER_INSTAGRAM_TOKEN",   "MOPER_INSTAGRAM_ACCOUNT_ID"),
    "laika":  ("LAIKA_INSTAGRAM_TOKEN",   "LAIKA_INSTAGRAM_ACCOUNT_ID"),
    "namasa": ("NAMASA_INSTAGRAM_TOKEN",  "NAMASA_INSTAGRAM_ACCOUNT_ID"),
}


def loadConfig(client: str = "moacir") -> Dict:
    """Load and validate environment variables for the given client."""
    if client not in CLIENT_ENV_MAP:
        raise EnvironmentError(f"Unknown client '{client}'. Valid: {list(CLIENT_ENV_MAP)}")

    tokenVar, acctVar = CLIENT_ENV_MAP[client]
    token   = os.getenv(tokenVar)
    acct_id = os.getenv(acctVar)

    if not token or not acct_id:
        raise EnvironmentError(
            f"Missing: {tokenVar} and/or {acctVar} in .env for client '{client}'"
        )

    token = token.strip("'\"")
    return {
        "token":      token,
        "account_id": acct_id.strip("'\""),
        "api_base":   getApiBase(token),
        "client":     client,
        "timeout":    API_TIMEOUT,
    }


# ============================================================================
# API CALLS
# ============================================================================

def createSession():
    """HTTP session with retry logic."""
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    session = requests.Session()
    retry = Retry(
        total=MAX_RETRIES,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1,
        respect_retry_after_header=True
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetchAccountProfile(config: Dict, session=None) -> Dict:
    """Fetch account profile: followers, media count."""
    session = session or createSession()
    url = f"{config['api_base']}/{config['account_id']}"
    params = {
        "fields":       "id,name,username,followers_count,media_count,biography",
        "access_token": config["token"],
    }
    r = session.get(url, params=params, timeout=config["timeout"])
    r.raise_for_status()
    return r.json()


def fetchRecentPosts(config: Dict, limit: int = 25, session=None) -> List[Dict]:
    """Fetch recent posts with engagement metrics."""
    session = session or createSession()
    url = f"{config['api_base']}/{config['account_id']}/media"
    params = {
        "fields": (
            "id,caption,media_type,media_url,thumbnail_url,"
            "timestamp,like_count,comments_count,permalink"
        ),
        "limit":        limit,
        "access_token": config["token"],
    }
    r = session.get(url, params=params, timeout=config["timeout"])
    r.raise_for_status()
    data = r.json()
    return data.get("data", [])


def fetchAccountInsights(config: Dict, period: int = 30, session=None) -> Dict:
    """Fetch account-level insights: impressions, reach."""
    session = session or createSession()
    url = f"{config['api_base']}/{config['account_id']}/insights"

    since = int((datetime.utcnow() - timedelta(days=period)).timestamp())
    until = int(datetime.utcnow().timestamp())
    base_params = {"access_token": config["token"], "since": since, "until": until}

    # graph.facebook.com requires splitting time-series vs total_value metrics
    if "facebook.com" in config["api_base"]:
        result = {"data": []}
        r1 = session.get(url, params={**base_params, "metric": "reach,follower_count", "period": "day"}, timeout=config["timeout"])
        if r1.ok:
            result["data"].extend(r1.json().get("data", []))
        else:
            logger.warning(f"Insights r1 failed ({r1.status_code}): {r1.text[:200]}")
        r2 = session.get(url, params={**base_params, "metric": "profile_views,accounts_engaged,total_interactions", "metric_type": "total_value", "period": "days_28"}, timeout=config["timeout"])
        if r2.ok:
            result["data"].extend(r2.json().get("data", []))
        else:
            logger.warning(f"Insights r2 failed ({r2.status_code}): {r2.text[:200]}")
        return result

    params = {
        "metric":       "reach,profile_views,accounts_engaged,total_interactions,follower_count",
        "period":       "day",
        "since":        since,
        "until":        until,
        "access_token": config["token"],
    }
    r = session.get(url, params=params, timeout=config["timeout"])
    r.raise_for_status()
    return r.json()


# ============================================================================
# SAVE TO DATABASE
# ============================================================================

def saveToDb(data: Dict[str, Any]) -> Dict:
    """Persist fetched Instagram data to Neon PostgreSQL."""
    from execution.dbClient import DbClient

    client  = data.get("config", {}).get("client", os.getenv("INSTAGRAM_CLIENT_NAME", "unknown"))
    profile = data["profile"]
    posts   = data["posts"]
    acctId  = profile.get("id", os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID"))
    today   = datetime.utcnow().strftime("%Y-%m-%d")
    now     = datetime.utcnow()
    start   = now

    with DbClient() as db:
        # Upsert social_accounts
        db.upsert(
            "social_accounts",
            ["platform", "account_id"],
            {
                "platform":     "instagram",
                "account_id":   acctId,
                "username":     profile.get("username"),
                "display_name": profile.get("name"),
                "client":       client,
                "is_active":    True,
                "updated_at":   now,
            }
        )
        logger.info(f"  social_accounts: upserted @{profile.get('username')}")

        # Upsert metrics
        summary = data["summary"]
        db.upsert(
            "metrics",
            ["platform", "client", "metric_date"],
            {
                "platform":        "instagram",
                "client":          client,
                "account_id":      acctId,
                "metric_date":     today,
                "followers":       summary.get("followers"),
                "media_count":     summary.get("media_count"),
                "posts_fetched":   summary.get("posts_fetched"),
                "engagement_rate": summary.get("engagement_rate"),
                "raw_data":        json.dumps(data.get("insights", {})),
                "collected_at":    now,
            }
        )
        logger.info(f"  metrics: upserted {today} ({summary.get('followers')} followers)")

        # Upsert each post
        for post in posts:
            mediaUrls = [u for u in [post.get("media_url"), post.get("thumbnail_url")] if u]
            db.upsert(
                "posts",
                ["platform", "post_id"],
                {
                    "platform":     "instagram",
                    "post_id":      post.get("id"),
                    "client":       client,
                    "account_id":   acctId,
                    "content":      post.get("caption", ""),
                    "media_urls":   mediaUrls,
                    "status":       "published",
                    "published_at": post.get("timestamp"),
                    "metadata":     json.dumps({
                        "media_type":     post.get("media_type"),
                        "like_count":     post.get("like_count", 0),
                        "comments_count": post.get("comments_count", 0),
                        "permalink":      post.get("permalink"),
                    }),
                    "collected_at": now,
                }
            )
        logger.info(f"  posts: upserted {len(posts)} posts")

        # Insert execution log
        durationMs = int((datetime.utcnow() - start).total_seconds() * 1000)
        db.execute(
            """INSERT INTO execution_logs (script_name, status, message, details, duration_ms)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                "fetchInstagramData",
                "success",
                f"Collected {len(posts)} posts, 1 metrics snapshot for {client}",
                json.dumps({"client": client, "account_id": acctId, "metric_date": today}),
                durationMs,
            )
        )
        logger.info(f"  execution_logs: saved ({durationMs}ms)")

    return {"saved_to": "neon", "client": client, "date": today, "posts": len(posts)}


# ============================================================================
# MAIN
# ============================================================================

def fetchInstagramData(period: int = 30, client: str = "moacir") -> Dict[str, Any]:
    """Full Instagram data fetch: profile + posts + insights."""
    config = loadConfig(client)
    timestamp = datetime.utcnow().isoformat() + "Z"
    session = createSession()

    logger.info(f"Fetching Instagram data for account {config['account_id']}...")

    profile  = fetchAccountProfile(config, session=session)
    logger.info(f"  Profile: @{profile.get('username')} — {profile.get('followers_count', 0):,} followers")

    posts = fetchRecentPosts(config, session=session)
    logger.info(f"  Posts: {len(posts)} recent posts fetched")

    insights = fetchAccountInsights(config, period=period, session=session)
    logger.info(f"  Insights: {period}-day window fetched")

    # Compute engagement rate from recent posts
    totalEngagement = sum(
        (p.get("like_count") or 0) + (p.get("comments_count") or 0)
        for p in posts
    )
    followers = profile.get("followers_count") or 1
    engagementRate = round(totalEngagement / (len(posts) * followers), 4) if posts else 0

    result = {
        "status":    "success",
        "timestamp": timestamp,
        "period_days": period,
        "config":    {"client": client, "account_id": config["account_id"]},
        "profile":   profile,
        "posts":     posts,
        "insights":  insights,
        "summary": {
            "followers":       profile.get("followers_count"),
            "media_count":     profile.get("media_count"),
            "posts_fetched":   len(posts),
            "engagement_rate": engagementRate,
        }
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch Instagram Data")
    parser.add_argument("--client", default="moacir", choices=list(CLIENT_ENV_MAP), help="Client name")
    parser.add_argument("--period", type=int, default=30, help="Days of insights (7/30/90)")
    parser.add_argument("--save",   action="store_true", help="Save to Neon PostgreSQL")
    args = parser.parse_args()

    try:
        data = fetchInstagramData(period=args.period, client=args.client)

        if args.save:
            saved = saveToDb(data)
            logger.info(f"Saved to Neon: {saved}")
            data["saved"] = saved

        print(json.dumps(data, indent=2, default=str))
        sys.exit(0)

    except EnvironmentError as e:
        logger.error(f"Config error: {e}")
        print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
