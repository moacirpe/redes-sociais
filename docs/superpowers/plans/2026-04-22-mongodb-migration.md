# MongoDB Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Substituir PostgreSQL+VPS por MongoDB Atlas (MLabs) e fazer `fetchInstagramData.py --save` persistir dados reais no banco.

**Architecture:** `dbClient.py` é reescrito com `pymongo` conectando via `MONGODB_URI` direto ao MLabs. `fetchInstagramData.py` ganha uma função `saveToMongo()` que upsert métricas, posts e logs. Sem SSH, sem VPS, sem tunnel.

**Tech Stack:** Python 3, pymongo 4.x, MongoDB Atlas (MLabs), python-dotenv

---

## Mapa de Arquivos

| Arquivo | Ação |
|---------|------|
| `requirements.txt` | Remove psycopg2, paramiko, fabric, sshtunnel — adiciona pymongo |
| `execution/dbClient.py` | Reescrita completa com pymongo |
| `execution/setupDatabase.py` | Reescrita — cria coleções + índices no Mongo |
| `execution/testConnections.py` | Remove testSsh/testDocker/testPostgres — adiciona testMongo |
| `execution/fetchInstagramData.py` | Adiciona `saveToMongo()` e integra ao `--save` |
| `.env` | Adiciona `MONGODB_URI` e `INSTAGRAM_CLIENT_NAME` |

---

## Task 1: Atualizar dependências e .env

**Files:**
- Modify: `requirements.txt`
- Modify: `.env`

- [ ] **Step 1: Atualizar requirements.txt**

Substituir o conteúdo de `requirements.txt` por:

```
# Core
python-dotenv==1.0.0

# Database
pymongo==4.6.3

# HTTP & APIs
requests==2.31.0
urllib3==2.0.7

# Data Processing
pandas==2.0.3

# Utilities
pytz==2023.3

# Optional: Google Services
google-auth==2.23.0
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.2.0
google-api-python-client==2.100.0
```

- [ ] **Step 2: Instalar pymongo**

```bash
pip install pymongo==4.6.3
```

Saída esperada: `Successfully installed pymongo-4.6.3`

- [ ] **Step 3: Adicionar variáveis ao .env**

Adicionar no final do `.env`:

```
# MongoDB Atlas (MLabs)
MONGODB_URI=mongodb+srv://USUARIO:SENHA@CLUSTER.mongodb.net/redes_sociais

# Cliente padrão para coleta Instagram moacir
INSTAGRAM_CLIENT_NAME=moacir
```

> Substituir `USUARIO`, `SENHA` e `CLUSTER` pelos valores reais do painel MLabs.

- [ ] **Step 4: Verificar import pymongo**

```bash
python -c "import pymongo; print(pymongo.version)"
```

Saída esperada: `4.6.3`

---

## Task 2: Reescrever dbClient.py com pymongo

**Files:**
- Modify: `execution/dbClient.py`

- [ ] **Step 1: Reescrever execution/dbClient.py**

```python
#!/usr/bin/env python3
"""
Database Client - MongoDB Atlas via pymongo

Connects to MongoDB Atlas (MLabs) using MONGODB_URI from .env.
No SSH tunnel or VPS needed.

Usage:
    from execution.dbClient import DbClient

    with DbClient() as db:
        db.upsert("metrics", {"platform": "instagram", "client": "moacir", "metric_date": "2026-04-22"}, doc)
"""

import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DbClient:
    """MongoDB Atlas client. Reads MONGODB_URI from .env."""

    def __init__(self):
        self._client = None
        self._db = None
        self._connect()

    def _connect(self):
        from pymongo import MongoClient
        from pymongo.server_api import ServerApi

        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise EnvironmentError("Missing MONGODB_URI in .env")

        self._client = MongoClient(uri, server_api=ServerApi("1"))
        dbName = uri.split("/")[-1].split("?")[0] or "redes_sociais"
        self._db = self._client[dbName]
        logger.info(f"MongoDB connected: {dbName}")

    def getCollection(self, name: str):
        return self._db[name]

    def upsert(self, collection: str, filter: Dict, doc: Dict) -> str:
        """Insert or update a document. Returns 'inserted' or 'updated'."""
        from pymongo import ReturnDocument
        doc["updated_at"] = datetime.utcnow()
        result = self._db[collection].find_one_and_replace(
            filter, {**filter, **doc},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return "ok"

    def insertOne(self, collection: str, doc: Dict) -> str:
        """Insert a single document. Returns inserted_id as string."""
        doc["created_at"] = datetime.utcnow()
        result = self._db[collection].insert_one(doc)
        return str(result.inserted_id)

    def find(self, collection: str, filter: Dict = None, limit: int = 100) -> List[Dict]:
        """Find documents matching filter."""
        cursor = self._db[collection].find(filter or {}, limit=limit)
        return [{**doc, "_id": str(doc["_id"])} for doc in cursor]

    def listCollections(self) -> List[str]:
        return self._db.list_collection_names()

    def ping(self) -> bool:
        self._client.admin.command("ping")
        return True

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            logger.info("MongoDB connection closed")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

- [ ] **Step 2: Verificar import**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS" && python -c "from execution.dbClient import DbClient; print('OK')"
```

Saída esperada: `OK`

---

## Task 3: Reescrever setupDatabase.py para MongoDB

**Files:**
- Modify: `execution/setupDatabase.py`

- [ ] **Step 1: Reescrever execution/setupDatabase.py**

```python
#!/usr/bin/env python3
"""
Database Setup - Create Collections and Indexes

Creates MongoDB collections and indexes for the social media platform.
Safe to run multiple times (indexes use background creation).

Usage:
    python execution/setupDatabase.py
"""

import sys
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

INDEXES = {
    "social_accounts": [
        {"keys": [("platform", 1), ("account_id", 1)], "unique": True},
    ],
    "metrics": [
        {"keys": [("platform", 1), ("client", 1), ("metric_date", 1)], "unique": True},
        {"keys": [("collected_at", -1)], "unique": False},
    ],
    "posts": [
        {"keys": [("platform", 1), ("post_id", 1)], "unique": True},
        {"keys": [("client", 1), ("published_at", -1)], "unique": False},
    ],
    "execution_logs": [
        {"keys": [("created_at", -1)], "unique": False},
    ],
}


def setupDatabase():
    from execution.dbClient import DbClient
    from pymongo import ASCENDING, DESCENDING

    dirMap = {1: ASCENDING, -1: DESCENDING}

    with DbClient() as db:
        logger.info("Setting up MongoDB collections and indexes...")

        for collection, indexes in INDEXES.items():
            col = db.getCollection(collection)
            for idx in indexes:
                keys = [(k, dirMap[v]) for k, v in idx["keys"]]
                col.create_index(keys, unique=idx["unique"], background=True)
                logger.info(f"  [{collection}] index {[k for k,_ in idx['keys']]} unique={idx['unique']} OK")

        collections = db.listCollections()
        logger.info(f"\nSetup complete. Collections: {collections}")
        return collections


def main():
    try:
        collections = setupDatabase()
        print(json.dumps({"status": "ok", "collections": collections}, indent=2))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar setupDatabase.py**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS" && python execution/setupDatabase.py
```

Saída esperada:
```json
{
  "status": "ok",
  "collections": ["social_accounts", "metrics", "posts", "execution_logs"]
}
```

Se houver erro de autenticação: verificar `MONGODB_URI` no `.env`.

---

## Task 4: Atualizar testConnections.py para MongoDB

**Files:**
- Modify: `execution/testConnections.py`

- [ ] **Step 1: Reescrever execution/testConnections.py**

```python
#!/usr/bin/env python3
"""
Connection Test Suite

Tests all infrastructure connections:
- Environment variables
- MongoDB Atlas

Run this to verify .env is correctly configured.

Usage:
    python execution/testConnections.py
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PASS = "✅"
FAIL = "❌"
SKIP = "⏭️ "

results = {}


def testEnv():
    """Check which .env vars are filled in."""
    label = "Environment"
    allVars = {
        "MongoDB": ["MONGODB_URI"],
        "Instagram (moacir)": ["INSTAGRAM_TOKEN", "INSTAGRAM_BUSINESS_ACCOUNT_ID", "INSTAGRAM_CLIENT_NAME"],
        "Instagram (moper)": ["MOPER_INSTAGRAM_TOKEN"],
        "TikTok": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"],
        "YouTube": ["MOACIR_YOUTUBE_CLIENT_ID"],
    }

    summary = {}
    for group, keys in allVars.items():
        filled = [k for k in keys if os.getenv(k)]
        missing = [k for k in keys if not os.getenv(k)]
        summary[group] = {"filled": filled, "missing": missing}

    allFilled  = [k for g in allVars.values() for k in g if os.getenv(k)]
    allMissing = [k for g in allVars.values() for k in g if not os.getenv(k)]

    logger.info(f"{PASS} {label}: {len(allFilled)} vars set, {len(allMissing)} missing")
    for group, s in summary.items():
        status = PASS if not s["missing"] else "⚠️ "
        logger.info(f"  {status} {group}: {len(s['filled'])}/{len(s['filled']) + len(s['missing'])} vars set")
        if s["missing"]:
            logger.info(f"     Missing: {s['missing']}")

    results[label] = {"status": "ok", "summary": summary}


def testMongo():
    """Test MongoDB Atlas connection."""
    label = "MongoDB Atlas"
    try:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            logger.warning(f"{SKIP} {label}: MONGODB_URI not set in .env")
            results[label] = {"status": "skipped", "reason": "MONGODB_URI not set"}
            return

        from execution.dbClient import DbClient
        with DbClient() as db:
            db.ping()
            collections = db.listCollections()
            logger.info(f"{PASS} {label}: connected OK")
            logger.info(f"  Collections: {collections if collections else '(empty — run setupDatabase.py)'}")
            results[label] = {"status": "ok", "collections": collections}

    except EnvironmentError as e:
        logger.warning(f"{SKIP} {label}: {e}")
        results[label] = {"status": "skipped", "reason": str(e)}
    except Exception as e:
        logger.error(f"{FAIL} {label}: {e}")
        results[label] = {"status": "fail", "error": str(e)}


def main():
    print("\n" + "=" * 60)
    print("   REDES SOCIAIS — Connection Test Suite")
    print("=" * 60 + "\n")

    testEnv()
    print()
    testMongo()

    print("\n" + "=" * 60)
    print("   RESULTS SUMMARY")
    print("=" * 60)

    for label, res in results.items():
        icon = {"ok": PASS, "skipped": SKIP, "fail": FAIL}.get(res["status"], "?")
        print(f"  {icon} {label}: {res['status'].upper()}")

    failed = [k for k, v in results.items() if v["status"] == "fail"]
    if failed:
        print(f"\n{FAIL} Some connections failed: {failed}")
        sys.exit(1)
    else:
        print(f"\n{PASS} All configured connections OK!")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar testConnections.py**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS" && python execution/testConnections.py
```

Saída esperada:
```
✅ MongoDB Atlas: connected OK
  Collections: ['social_accounts', 'metrics', 'posts', 'execution_logs']
✅ All configured connections OK!
```

---

## Task 5: Implementar --save no fetchInstagramData.py

**Files:**
- Modify: `execution/fetchInstagramData.py`

- [ ] **Step 1: Adicionar função saveToMongo() e integrar ao --save**

Substituir a seção `# MAIN` inteira (linha 132 em diante) por:

```python
# ============================================================================
# SAVE TO MONGODB
# ============================================================================

def saveToMongo(data: Dict[str, Any]) -> Dict:
    """Persist fetched Instagram data to MongoDB Atlas."""
    from execution.dbClient import DbClient

    client = os.getenv("INSTAGRAM_CLIENT_NAME", "unknown")
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
            {"platform": "instagram", "account_id": acctId},
            {
                "username":     profile.get("username"),
                "display_name": profile.get("name"),
                "client":       client,
                "is_active":    True,
            }
        )
        logger.info(f"  social_accounts: upserted @{profile.get('username')}")

        # Upsert metrics (one document per day per client)
        summary = data["summary"]
        db.upsert(
            "metrics",
            {"platform": "instagram", "client": client, "metric_date": today},
            {
                "account_id":      acctId,
                "followers":       summary.get("followers"),
                "media_count":     summary.get("media_count"),
                "posts_fetched":   summary.get("posts_fetched"),
                "engagement_rate": summary.get("engagement_rate"),
                "raw_data":        data.get("insights", {}),
                "collected_at":    now,
            }
        )
        logger.info(f"  metrics: upserted {today} snapshot ({summary.get('followers')} followers)")

        # Upsert each post
        for post in posts:
            db.upsert(
                "posts",
                {"platform": "instagram", "post_id": post.get("id")},
                {
                    "client":       client,
                    "account_id":   acctId,
                    "content":      post.get("caption", ""),
                    "media_urls":   [u for u in [post.get("media_url"), post.get("thumbnail_url")] if u],
                    "status":       "published",
                    "published_at": post.get("timestamp"),
                    "metadata": {
                        "media_type":     post.get("media_type"),
                        "like_count":     post.get("like_count", 0),
                        "comments_count": post.get("comments_count", 0),
                        "permalink":      post.get("permalink"),
                    },
                    "collected_at": now,
                }
            )
        logger.info(f"  posts: upserted {len(posts)} posts")

        # Insert execution log
        durationMs = int((datetime.utcnow() - start).total_seconds() * 1000)
        db.insertOne(
            "execution_logs",
            {
                "script_name": "fetchInstagramData",
                "status":      "success",
                "message":     f"Collected {len(posts)} posts, 1 metrics snapshot for {client}",
                "details":     {"client": client, "account_id": acctId, "metric_date": today},
                "duration_ms": durationMs,
            }
        )
        logger.info(f"  execution_logs: saved ({durationMs}ms)")

    return {
        "saved_to": "mongodb",
        "client":   client,
        "date":     today,
        "posts":    len(posts),
    }


# ============================================================================
# MAIN
# ============================================================================

def fetchInstagramData(period: int = 30) -> Dict[str, Any]:
    """Full Instagram data fetch: profile + posts + insights."""
    config = loadConfig()
    timestamp = datetime.utcnow().isoformat() + "Z"

    logger.info(f"Fetching Instagram data for account {config['account_id']}...")

    profile  = fetchAccountProfile(config)
    logger.info(f"  Profile: @{profile.get('username')} — {profile.get('followers_count', 0):,} followers")

    posts = fetchRecentPosts(config)
    logger.info(f"  Posts: {len(posts)} recent posts fetched")

    insights = fetchAccountInsights(config, period=period)
    logger.info(f"  Insights: {period}-day window fetched")

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
    parser.add_argument("--period", type=int, default=30, help="Days of insights (7/30/90)")
    parser.add_argument("--save",   action="store_true", help="Save to MongoDB Atlas")
    args = parser.parse_args()

    try:
        data = fetchInstagramData(period=args.period)

        if args.save:
            saved = saveToMongo(data)
            logger.info(f"Saved to MongoDB: {saved}")
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
```

- [ ] **Step 2: Rodar coleta sem --save para confirmar que não quebrou**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS" && python execution/fetchInstagramData.py --period 7 2>&1 | head -20
```

Saída esperada: JSON com `"status": "success"` e dados de perfil.

- [ ] **Step 3: Rodar coleta com --save (pipeline completo)**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS" && python execution/fetchInstagramData.py --period 7 --save
```

Saída esperada no log:
```
INFO social_accounts: upserted @moacir.moper
INFO metrics: upserted 2026-04-22 snapshot (461 followers)
INFO posts: upserted 25 posts
INFO execution_logs: saved (XXXms)
```

E no JSON final: `"saved": {"saved_to": "mongodb", "client": "moacir", ...}`

- [ ] **Step 4: Verificar no painel MLabs**

Abrir o painel do MongoDB Atlas → Database → Collections → `metrics`.
Deve existir um documento com `metric_date: "2026-04-22"` e `client: "moacir"`.

---

## Task 6: Atualizar HANDOFF.md e PLANO.md

**Files:**
- Modify: `HANDOFF.md`
- Modify: `docs/PLANO.md`

- [ ] **Step 1: Atualizar status no HANDOFF.md**

Na tabela de features, alterar:
- `moacir | Coleta Instagram` → `[5-T]` ✅ pipeline completo
- `Infra | PostgreSQL via SSH` → remover ou marcar como `cancelado — substituído por MongoDB Atlas`

Atualizar a seção "Credenciais" para refletir que `MONGODB_URI` está preenchido.

- [ ] **Step 2: Atualizar docs/PLANO.md**

Marcar `[5-T]` para "Coleta Instagram moacir" e adicionar linha para MongoDB Atlas como `[5-T]`.

---

## Critério de Sucesso Final

Todos os itens abaixo devem passar antes de marcar como completo:

```bash
# 1. Setup do banco
python execution/setupDatabase.py
# → status: ok, collections listadas

# 2. Teste de conexão
python execution/testConnections.py
# → ✅ MongoDB Atlas: connected OK

# 3. Pipeline completo
python execution/fetchInstagramData.py --period 7 --save
# → JSON com "saved": {"saved_to": "mongodb", ...}
# → documentos visíveis no painel MLabs
```
