#!/usr/bin/env python3
"""
EXAMPLE: Template for execution scripts

This serves as a boilerplate for creating new execution scripts.
All scripts should follow this structure.

Naming: verbEntityAction.py
Example: fetchInstagramData.py
"""

import sys
import os
import json
from typing import Dict, Any

# Add execution directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils import logger, getEnv, validateEnv, ensureTmpDir, saveJsonFile, getTimestamp

# ============================================================================
# CONFIGURATION
# ============================================================================

def loadConfig() -> Dict[str, Any]:
    """Load and validate required environment variables."""
    required = [
        # Add required env vars here
        # Example: "INSTAGRAM_TOKEN"
    ]

    validateEnv(required)
    logger.info("Config validated successfully")

    return {
        # "instagram_token": getEnv("INSTAGRAM_TOKEN"),
        # "api_timeout": float(getEnv("API_TIMEOUT", "30")),
    }

# ============================================================================
# MAIN LOGIC
# ============================================================================

def fetchData(config: Dict) -> Dict[str, Any]:
    """
    Main function - replace with actual logic.

    Args:
        config: Configuration dict from loadConfig()

    Returns:
        Dict with results
    """
    try:
        logger.info("Starting data fetch...")

        # TODO: Implement actual work here
        # - Make API calls
        # - Process data
        # - Validate results

        result = {
            "status": "success",
            "timestamp": getTimestamp(),
            "data": [],
            "rowsProcessed": 0,
        }

        logger.info(f"Completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": getTimestamp(),
        }

# ============================================================================
# EXPORT & CLI
# ============================================================================

def main():
    """Entry point for CLI execution."""
    try:
        config = loadConfig()
        result = fetchData(config)

        # Save to .tmp/
        filename = f"example_output_{result['timestamp'].replace(':', '-')}.json"
        saveJsonFile(result, filename, subdir="exports")

        # Output to stdout (for orchestration layer)
        print(json.dumps(result, indent=2))

        # Exit with appropriate code
        exit_code = 0 if result.get("status") == "success" else 1
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "timestamp": getTimestamp()
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
