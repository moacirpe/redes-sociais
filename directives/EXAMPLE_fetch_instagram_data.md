# EXAMPLE Directive: Fetch Instagram Data

## Goal
Retrieve follower count, engagement metrics, and recent posts from all Instagram Business Accounts connected to the system. Data is validated, deduplicated, and stored for further processing.

## Inputs
- Instagram Business Account IDs (from database or .env)
- Instagram Access Tokens (from .env or secure vault)
- Time period: `last_7_days`, `last_30_days`, `last_90_days` (default: 30)

## Process

### Step 1: Load Configuration
Execute `../execution/fetchInstagramData.py` with parameters:
```bash
python execution/fetchInstagramData.py --period 30 --save-raw
```

**What it does:**
- Loads environment variables from `.env`
- Validates API tokens
- Initializes connection pool
- Prepares API request templates

### Step 2: Fetch Raw Data
The script makes authenticated API calls to Instagram Graph API:
- Get business account profile data
- Fetch recent posts (with captions, likes, comments)
- Get aggregated insights (impressions, reach, engagement rate)
- Handle pagination for large datasets

**API Limits to watch:**
- 200 calls/hour per token (Instagram standard)
- 50MB payload limit per request
- Rate limit error: HTTP 429 → Retry after 60 seconds

### Step 3: Validate & Transform
- Check required fields (id, followers, posts)
- Remove duplicates (by timestamp + post_id)
- Normalize date formats to ISO 8601
- Convert metrics to numeric types
- Handle null/missing values

### Step 4: Save Intermediate Output
Raw JSON saved to: `.tmp/scraped_data/instagram_<date>_<time>.json`

**Example output structure:**
```json
{
  "status": "success",
  "accounts": [
    {
      "account_id": "123456",
      "followers": 5000,
      "posts": [
        {
          "id": "abc123",
          "caption": "Hello world!",
          "likes": 150,
          "comments": 23,
          "timestamp": "2026-04-06T12:34:56Z"
        }
      ],
      "insights": {
        "impressions": 12500,
        "reach": 8900,
        "engagement_rate": 0.028
      }
    }
  ],
  "timestamp": "2026-04-06T12:35:00Z",
  "rows_processed": 45
}
```

## Outputs

1. **Raw JSON** (in `.tmp/scraped_data/`)
   - Complete response from API
   - Useful for debugging
   - Can be reprocessed if needed

2. **Processed CSV** (optional, in Google Sheets)
   - Normalized columns
   - Ready for analysis
   - Uploaded to `Sheet: "Instagram Raw Data"`

3. **Summary Statistics** (logged)
   - Number of accounts processed
   - Total posts fetched
   - Total followers across accounts
   - Processing time

## Edge Cases & Error Handling

### Case 1: Invalid API Token
**What happens:** API returns 401 Unauthorized
**How to handle:**
- Catch HTTP 401 error
- Log error with account ID
- Skip that account, continue with others
- Alert user to refresh token

**Script behavior:**
```python
if response.status_code == 401:
    logger.error(f"Invalid token for account {account_id}")
    failed_accounts.append(account_id)
    continue  # Move to next account
```

### Case 2: Rate Limit Hit
**What happens:** API returns 429 Too Many Requests
**How to handle:**
- Read `Retry-After` header (usually 60 seconds)
- Wait that duration
- Retry the request (max 3 attempts)
- If still failing, skip and continue

**Script behavior:**
```python
if response.status_code == 429:
    wait_time = int(response.headers.get("Retry-After", 60))
    logger.warning(f"Rate limited, waiting {wait_time}s")
    time.sleep(wait_time)
    retry_count += 1
```

### Case 3: Partial Data (API returns incomplete response)
**What happens:** Missing posts or incomplete metrics
**How to handle:**
- Log warning with account ID
- Continue processing with available data
- Flag record as "incomplete" in output
- Still save the data (some data > no data)

**Script behavior:**
```python
if len(posts) < expected_count:
    logger.warning(f"Got {len(posts)}/{expected_count} posts for {account_id}")
    account_data["_incomplete"] = True
```

### Case 4: Network Timeout
**What happens:** Connection times out after 30 seconds
**How to handle:**
- Retry up to 3 times with exponential backoff
- If all retries fail, mark account as failed
- Continue with next account
- Log full error details

**Script behavior:**
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        response = session.get(url, timeout=30)
        break  # Success
    except requests.Timeout:
        if attempt < max_retries - 1:
            wait = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait)
        else:
            logger.error(f"Failed after {max_retries} retries")
            raise
```

## Tools Used

- `execution/fetchInstagramData.py` - Main script
- `execution/utils.py` - Utilities (API calls, logging, file I/O)
- `.env` - API credentials and configuration

## Dependencies

```
requests>=2.28.0
psycopg2-binary>=2.9.0
python-dotenv>=0.20.0
```

## Performance Notes

- **Time estimate**: 5-15 minutes per 100 accounts (depends on API speed)
- **Resource usage**: ~50-100MB memory, minimal CPU
- **Bandwidth**: ~1-5MB per 100 accounts
- **Cost**: Free tier (Instagram Graph API)

## Success Criteria

✅ All required fields populated (id, followers, posts)
✅ No duplicate posts in output
✅ Timestamps in ISO 8601 format
✅ Numeric fields are actual numbers (not strings)
✅ Output saved to `.tmp/scraped_data/`
✅ Log file shows "Completed" message
✅ Exit code 0 returned

## When to Update This Directive

- ❌ Instagram API changes response format
- ❌ New fields available (add to collection)
- ❌ API rate limits change (update limits section)
- ❌ Timeout threshold needs adjustment
- ❌ New edge case discovered

---

**Last Updated**: 2026-04-06
**Status**: Template / Example
**Used By**: Orchestration Layer (Claude)
