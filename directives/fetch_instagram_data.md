# Directive: Fetch Instagram Data

## Goal
Retrieve profile metrics, recent posts, and account insights from Instagram Business Account. Store raw data locally and optionally persist to PostgreSQL.

## Inputs
- `INSTAGRAM_TOKEN` — Instagram Graph API access token (from `.env`)
- `INSTAGRAM_BUSINESS_ACCOUNT_ID` — Business Account ID (from `.env`)
- `period` — Days of insights to retrieve: 7, 30, or 90 (default: 30)

## Process

### Step 1: Run Data Fetch
```bash
python execution/fetchInstagramData.py --period 30 --save
```

**What it fetches:**
- Profile: followers, media count, biography
- Recent posts: caption, media type, likes, comments, permalink
- Insights: impressions, reach, profile views, follower growth

### Step 2: Validate Output
Check returned JSON for:
- `status: success`
- `summary.followers` is a number
- `posts` array is not empty
- `insights` data is present

### Step 3: Save to Database (optional)
If PostgreSQL is configured:
```python
from execution.dbClient import DbClient
from execution.fetchInstagramData import fetchInstagramData

data = fetchInstagramData(period=30)

with DbClient() as db:
    # Upsert account metrics
    db.execute("""
        INSERT INTO metrics (account_id, platform, metric_date, followers, impressions, reach)
        VALUES (%s, 'instagram', %s, %s, %s, %s)
        ON CONFLICT (account_id, metric_date, platform) DO UPDATE
        SET followers = EXCLUDED.followers,
            impressions = EXCLUDED.impressions,
            reach = EXCLUDED.reach
    """, (account_db_id, today, data["summary"]["followers"], ...))
```

## Outputs
- Raw JSON in `.tmp/scraped_data/instagram_<timestamp>.json`
- Metrics stored in `metrics` PostgreSQL table (if Step 3 done)

## API Limits
- Instagram Graph API: 200 calls/hour per token
- Rate limit response: HTTP 429 with `Retry-After` header
- Script auto-retries up to 3 times with backoff

## Edge Cases

### Invalid Token (HTTP 401)
**Error**: `{"error": {"code": 190, "message": "Invalid OAuth access token"}}`
**Fix**: Regenerate token at Meta Business Suite → Tokens → Refresh

### Token Expired (HTTP 400)
**Error**: `OAuthException code 463`
**Fix**: Long-lived tokens expire after 60 days. Use token refresh flow.

### Account Not Business (HTTP 400)
**Error**: `Requires business account`
**Fix**: Convert Instagram account to Business in app settings → Use Facebook Page connection

### Rate Limited (HTTP 429)
**Fix**: Script respects `Retry-After` automatically. If persistent, reduce period or wait 1 hour.

### No Posts Returned
**Cause**: Account has no posts or `media_count` is 0
**Fix**: Verify account ID is correct. Check account has posts on Instagram app.

## Tools Used
- `execution/fetchInstagramData.py`

## Success Criteria
- ✅ `status: success` in output
- ✅ `summary.followers` is present and > 0
- ✅ `posts` array has entries
- ✅ File saved to `.tmp/scraped_data/`

---
**Last Updated**: 2026-04-06
**API Version**: Instagram Graph API v19.0
**Status**: Ready — requires INSTAGRAM_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID in .env
