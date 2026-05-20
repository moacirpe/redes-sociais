"""
Execution Layer - Deterministic Python Scripts

These scripts handle all the actual work:
- API calls
- Data processing
- File operations
- Database interactions

Naming Convention: verbEntityAction.py (camelCase)
Example: fetchInstagramData.py, schedulePost.py, generateAnalyticsReport.py

All scripts should:
1. Load config from .env via utils.py
2. Use logging from utils.py
3. Return structured JSON output
4. Handle errors gracefully
5. Exit with status code (0 = success, 1 = failure)
"""
