"""
Execution Layer - Utilities Module

Shared utility functions for all execution scripts.
Handles: database, API calls, data validation, logging, error handling.

Naming Convention: camelCase for all functions
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import psycopg2
from psycopg2.pool import SimpleConnectionPool
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setupLogging(logLevel: str = None) -> logging.Logger:
    """Initialize logging configuration."""
    logLevel = logLevel or os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, logLevel),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setupLogging()

# ============================================================================
# DATABASE CONNECTIONS
# ============================================================================

_dbPool = None

def getDbConnection():
    """Get PostgreSQL connection from pool."""
    global _dbPool

    if _dbPool is None:
        _dbPool = SimpleConnectionPool(
            minconn=int(os.getenv("POSTGRES_POOL_MIN", 2)),
            maxconn=int(os.getenv("POSTGRES_POOL_MAX", 10)),
            host=os.getenv("POSTGRES_HOST"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )

    return _dbPool.getconn()

def releaseDbConnection(conn):
    """Release connection back to pool."""
    if _dbPool:
        _dbPool.putconn(conn)

def closeDbPool():
    """Close all database connections."""
    global _dbPool
    if _dbPool:
        _dbPool.closeall()
        _dbPool = None

def executeDbQuery(query: str, params: tuple = None) -> List[Dict]:
    """Execute SELECT query and return results as list of dicts."""
    conn = getDbConnection()
    try:
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            colnames = [desc[0] for desc in cursor.description]
            return [dict(zip(colnames, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()
    finally:
        releaseDbConnection(conn)

def executeDbUpdate(query: str, params: tuple = None) -> int:
    """Execute INSERT/UPDATE/DELETE query. Returns affected rows."""
    conn = getDbConnection()
    try:
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            affected = cursor.rowcount
            conn.commit()
            return affected
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    finally:
        releaseDbConnection(conn)

# ============================================================================
# HTTP REQUESTS WITH RETRIES
# ============================================================================

def createSession(retries: int = 3, timeout: float = 30) -> requests.Session:
    """Create requests session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def makeApiCall(url: str, method: str = "GET", headers: Dict = None,
                data: Dict = None, timeout: float = 30) -> Dict:
    """Make HTTP request with error handling."""
    try:
        session = createSession()
        response = session.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        raise

# ============================================================================
# FILE OPERATIONS
# ============================================================================

def ensureTmpDir(subdir: str = "") -> str:
    """Ensure .tmp directory exists. Returns path."""
    basePath = ".tmp"
    fullPath = os.path.join(basePath, subdir) if subdir else basePath
    os.makedirs(fullPath, exist_ok=True)
    return fullPath

def saveJsonFile(data: Dict, filename: str, subdir: str = "") -> str:
    """Save data to JSON file in .tmp/. Returns filepath."""
    tmpPath = ensureTmpDir(subdir)
    filepath = os.path.join(tmpPath, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved JSON to {filepath}")
    return filepath

def loadJsonFile(filepath: str) -> Dict:
    """Load JSON file. Returns dict."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# ============================================================================
# DATA VALIDATION
# ============================================================================

def validateRequired(data: Dict, fields: List[str]) -> bool:
    """Check if required fields exist, are not None, and not empty string."""
    for field in fields:
        if field not in data or data[field] is None or data[field] == "":
            logger.error(f"Missing required field: {field}")
            return False
    return True

def validateDataTypes(data: Dict, schema: Dict[str, type]) -> bool:
    """Validate data types match schema."""
    for field, expectedType in schema.items():
        if field in data and not isinstance(data[field], expectedType):
            logger.error(f"Invalid type for {field}: expected {expectedType}, got {type(data[field])}")
            return False
    return True

# ============================================================================
# ENVIRONMENT
# ============================================================================

def getEnv(key: str, default: str = None) -> str:
    """Get environment variable with fallback. Raises if missing and no default."""
    value = os.getenv(key)
    if value is None:
        if default is None:
            raise ValueError(f"Missing environment variable: {key}")
        return default
    return value

def validateEnv(requiredKeys: List[str]) -> bool:
    """Check if all required env vars are set and non-empty."""
    missing = [k for k in requiredKeys if not os.getenv(k)]
    if missing:
        logger.error(f"Missing env vars: {missing}")
        return False
    return True

# ============================================================================
# TIMESTAMPING & NAMING
# ============================================================================

def getTimestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"

def getFilenamestamp() -> str:
    """Get timestamp for filenames (sortable, compact)."""
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def generateFilename(prefix: str, extension: str = "json") -> str:
    """Generate timestamped filename."""
    return f"{prefix}_{getFilenamestamp()}.{extension}"

# ============================================================================
# SOCIAL MEDIA STRATEGY UTILITIES
# ============================================================================

def calculateEngagementRate(likes: int, comments: int, shares: int, reach: int) -> float:
    """Calculate engagement rate percentage."""
    if reach == 0:
        return 0.0
    engagement = likes + comments + shares
    return round((engagement / reach) * 100, 2)

def optimizePostingSchedule(engagementData: List[Dict]) -> Dict[str, List[int]]:
    """Analyze engagement data to find optimal posting hours."""
    hourlyEngagement = {}
    for post in engagementData:
        hour = post.get('hour', 0)
        engagement = post.get('engagement', 0)
        if hour not in hourlyEngagement:
            hourlyEngagement[hour] = []
        hourlyEngagement[hour].append(engagement)

    # Calculate average engagement per hour
    avgEngagement = {}
    for hour, engagements in hourlyEngagement.items():
        avgEngagement[hour] = sum(engagements) / len(engagements)

    # Find top 3 hours
    topHours = sorted(avgEngagement.items(), key=lambda x: x[1], reverse=True)[:3]
    return {
        'optimal_hours': [hour for hour, _ in topHours],
        'avg_engagement_by_hour': avgEngagement
    }

def generateHashtagStrategy(niche: str, platform: str) -> Dict[str, List[str]]:
    """Generate hashtag strategy based on niche and platform."""
    baseHashtags = {
        'empreendedorismo_tech': ['#Empreendedorismo', '#Tecnologia', '#Startup', '#Inovacao'],
        'interior': ['#Interior', '#InteriorSP', '#CidadePequena', '#VidaNoInterior']
    }

    platformMultipliers = {
        'instagram': 1.0,
        'tiktok': 1.2,  # TikTok favors more hashtags
        'youtube': 0.8  # YouTube favors fewer, more specific
    }

    nicheTags = baseHashtags.get(niche, [])
    multiplier = platformMultipliers.get(platform, 1.0)

    return {
        'primary': nicheTags[:2],  # Always use these
        'secondary': nicheTags[2:int(4 * multiplier)],  # Use based on platform
        'trending': [],  # To be filled with current trending tags
        'max_recommended': int(8 * multiplier)
    }

def analyzeContentPerformance(posts: List[Dict]) -> Dict[str, Any]:
    """Analyze content performance patterns."""
    if not posts:
        return {'error': 'No posts to analyze'}

    # Group by content type
    typePerformance = {}
    for post in posts:
        contentType = post.get('type', 'unknown')
        engagement = post.get('engagement_rate', 0)

        if contentType not in typePerformance:
            typePerformance[contentType] = []
        typePerformance[contentType].append(engagement)

    # Calculate averages
    avgByType = {}
    for contentType, rates in typePerformance.items():
        avgByType[contentType] = round(sum(rates) / len(rates), 2)

    # Find best performing type
    bestType = max(avgByType.items(), key=lambda x: x[1]) if avgByType else ('unknown', 0)

    return {
        'best_content_type': bestType[0],
        'avg_engagement_by_type': avgByType,
        'total_posts_analyzed': len(posts),
        'recommendation': f"Focus on {bestType[0]} content for better engagement"
    }

def createGrowthProjection(currentFollowers: int, targetFollowers: int,
                          days: int, growthRate: float = None) -> Dict[str, Any]:
    """Create growth projection with milestones."""
    if growthRate is None:
        if currentFollowers == 0:
            raise ValueError("currentFollowers must be > 0 to compute growthRate")
        totalGrowth = targetFollowers - currentFollowers
        growthRate = (totalGrowth / currentFollowers) / days * 100

    projection = []
    current = currentFollowers

    for day in range(1, days + 1):
        current += current * (growthRate / 100)
        projection.append({
            'day': day,
            'projected_followers': int(current),
            'daily_growth': int(current * (growthRate / 100))
        })

    return {
        'current_followers': currentFollowers,
        'target_followers': targetFollowers,
        'required_daily_growth_rate': round(growthRate, 2),
        'projection': projection,
        'feasibility': 'realistic' if growthRate <= 5 else 'challenging' if growthRate <= 10 else 'ambitious'
    }

def generateContentCalendar(theme: str, days: int = 7) -> List[Dict[str, Any]]:
    """Generate content calendar for a theme."""
    themes = {
        'bastidores_jornada': [
            'Rotina diária de um empreendedor',
            'Desafios da semana',
            'Pequenas vitórias conquistadas',
            'Lições aprendidas com erros',
            'Planos para o futuro',
            'Ferramentas que uso diariamente',
            'Como mantenho a motivação'
        ],
        'tecnologias_que_uso': [
            'Apps de produtividade favoritos',
            'Ferramentas para gestão de projetos',
            'Softwares de análise de dados',
            'Plataformas de marketing digital',
            'Gadgets essenciais para trabalho',
            'Soluções cloud que recomendo',
            'Automação que salva meu tempo'
        ]
    }

    contentIdeas = themes.get(theme, [])
    calendar = []

    for i in range(min(days, len(contentIdeas))):
        calendar.append({
            'day': i + 1,
            'theme': theme,
            'content_idea': contentIdeas[i],
            'platforms': ['instagram', 'tiktok', 'youtube'],
            'hashtags': generateHashtagStrategy('empreendedorismo_tech', 'instagram'),
            'status': 'planned'
        })

    return calendar

# ============================================================================
# CLEANUP
# ============================================================================

def cleanupOnExit():
    """Close all resources on script exit."""
    closeDbPool()

import atexit
atexit.register(cleanupOnExit)
