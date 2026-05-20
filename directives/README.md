# Directives & Standard Operating Procedures

This directory contains Markdown files that define **HOW to accomplish tasks**.

## Directory Structure

Each directive should:
- **Have a clear goal** at the top
- **List required inputs** (data, API keys, etc.)
- **Define steps** (order matters)
- **Specify outputs** (what gets created/returned)
- **Document edge cases** (what can go wrong)
- **List execution tools** to use (scripts in `../execution/`)

## Current Directives

- `README.md` (this file)

## Creating a New Directive

1. **Title**: Descriptive, verb-noun format (e.g., `fetch_instagram_data.md`)
2. **Structure**:
   ```markdown
   # Fetch Instagram Data

   ## Goal
   Retrieve follower count, engagement metrics, and recent posts from Instagram Business Account

   ## Inputs
   - Instagram Business Account ID (from .env)
   - Instagram Access Token (from .env)
   - Time period (last 7/30/90 days)

   ## Process
   1. Execute `../execution/fetchInstagramData.py` with parameters
   2. Validate data integrity
   3. Transform to standard format
   4. Export to `.tmp/instagram_data_<date>.json`

   ## Outputs
   - Raw JSON data (in .tmp/)
   - Processed CSV (in Sheets or local)
   - Summary statistics

   ## Edge Cases
   - API rate limits: Retry after 60 seconds
   - Missing data: Log warning, continue with available data
   - Invalid token: Raise error, stop execution

   ## Tools Used
   - `execution/fetchInstagramData.py`
   - `execution/utils.py` (data validation)
   ```

3. **Link execution scripts** - reference them from `../execution/`
4. **Document API constraints** - rate limits, timeouts, response limits
5. **Include error handling** - what to do when APIs fail

## When to Update a Directive

- ✅ API changes behavior or limits
- ✅ New edge case discovered during execution
- ✅ Better/faster approach found
- ✅ Tools/scripts added or removed
- ✅ Timing estimates change

## Never Remove a Directive

Keep dated history. If a directive is obsolete:
- Add `[DEPRECATED]` to filename: `[DEPRECATED] fetch_instagram_data.md`
- Add deprecation notice at top
- Link to replacement directive if exists

---

**Remember**: Directives are instructions for Claude (the orchestrator). They guide decision-making but don't execute code. Execution happens in `../execution/` layer.
