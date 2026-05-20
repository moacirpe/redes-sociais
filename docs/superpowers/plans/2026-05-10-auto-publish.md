# Auto-Publish Posts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `execution/generateCaptions.py` (Claude API → draft captions → queue CSV) and `execution/publishScheduled.py` (reads CSV → Cloudinary upload → Instagram publish).

**Architecture:** Two independent scripts sharing a `queue/{client}/queue.csv` file. `generateCaptions.py` appends drafts; `publishScheduled.py` reads approved rows and publishes. Both reuse `loadConfig()` and `getApiBase()` from `fetchInstagramData.py`. No new DB tables needed — `execution_logs` tracks publish events.

**Tech Stack:** Python 3.9, `anthropic` SDK, `cloudinary` SDK, `requests`, `csv` (stdlib), existing `DbClient` + `fetchInstagramData.loadConfig`.

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `clients/moacir/briefing.md` | Create | Briefing fixo do cliente moacir |
| `clients/moper-maquinas/briefing.md` | Create | Briefing fixo do cliente moper |
| `clients/espaco-laika/briefing.md` | Create | Briefing fixo do cliente laika |
| `queue/moacir/media/.gitkeep` | Create | Pasta de mídia moacir |
| `queue/moper/media/.gitkeep` | Create | Pasta de mídia moper |
| `queue/laika/media/.gitkeep` | Create | Pasta de mídia laika |
| `execution/generateCaptions.py` | Create | Gera legendas via Claude API, escreve no CSV |
| `execution/publishScheduled.py` | Create | Publica posts aprovados via Cloudinary + Instagram |
| `tests/test_generateCaptions.py` | Create | Testes unitários de generateCaptions |
| `tests/test_publishScheduled.py` | Create | Testes unitários de publishScheduled |
| `execution/collectAll.sh` | Modify | Adicionar chamada ao publishScheduled.py |
| `requirements.txt` | Modify | Adicionar anthropic e cloudinary |
| `.env` | Modify | Adicionar CLOUDINARY_* e ANTHROPIC_API_KEY |

---

### Task 1: Install dependencies and create directory structure

**Files:**
- Modify: `requirements.txt`
- Modify: `.env`
- Create: `clients/moacir/briefing.md`, `clients/moper-maquinas/briefing.md`, `clients/espaco-laika/briefing.md`
- Create: `queue/moacir/media/`, `queue/moper/media/`, `queue/laika/media/`

- [ ] **Step 1: Add dependencies to requirements.txt**

Append to `requirements.txt`:
```
# AI & Media
anthropic==0.25.0
cloudinary==1.40.0
```

- [ ] **Step 2: Install them**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
.venv/bin/pip install anthropic==0.25.0 cloudinary==1.40.0 -q
```

Expected: `Successfully installed anthropic-0.25.0 cloudinary-1.40.0` (and dependencies)

- [ ] **Step 3: Add credentials to .env**

Open `.env` and add after the `# SECURITY` section:
```
# ============================================================================
# AI & MEDIA HOSTING
# ============================================================================
ANTHROPIC_API_KEY=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

- [ ] **Step 4: Create briefing files**

Create `clients/moacir/briefing.md`:
```markdown
# Briefing — moacir (@moacir.moper)
Tom: pessoal, autêntico, motivacional
Temas: empreendedorismo, máquinas, bastidores da empresa, vida de empresário
Hashtags fixas: #moper #maquinas #empreendedor
CTA padrão: Manda mensagem!
Evitar: linguagem muito formal, jargão técnico excessivo
```

Create `clients/moper-maquinas/briefing.md`:
```markdown
# Briefing — moper-maquinas (@moper.maquinas)
Tom: profissional, confiante, focado em resultados
Temas: máquinas pesadas, produtividade, obras, soluções para construtoras
Hashtags fixas: #mopermaquinas #maquinaspesadas #construcao
CTA padrão: Entre em contato!
Evitar: linguagem informal demais, emojis excessivos
```

Create `clients/espaco-laika/briefing.md`:
```markdown
# Briefing — espaco-laika (@espacolaikadourados)
Tom: acolhedor, festivo, emotivo
Temas: festas, eventos, celebrações, momentos especiais, espaço para alugar
Hashtags fixas: #espacolaika #festas #dourados
CTA padrão: Reserve seu espaço! (67) 99857-4771
Evitar: linguagem fria ou muito corporativa
```

- [ ] **Step 5: Create queue directories**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
mkdir -p queue/moacir/media queue/moper/media queue/laika/media
touch queue/moacir/media/.gitkeep queue/moper/media/.gitkeep queue/laika/media/.gitkeep
```

- [ ] **Step 6: Verify structure**

```bash
ls queue/
# Expected: laika  moacir  moper
ls queue/moacir/
# Expected: media
```

---

### Task 2: Write failing tests for generateCaptions helpers

**Files:**
- Create: `tests/test_generateCaptions.py`

- [ ] **Step 1: Create the test file**

Create `tests/test_generateCaptions.py`:

```python
import csv
import json
import os
import pytest
from unittest.mock import MagicMock, patch


# --- parseCaptionsResponse ---

def test_parseCaptionsResponse_plain_json():
    from execution.generateCaptions import parseCaptionsResponse
    raw = '[{"caption": "Teste!", "hashtags": "#teste"}]'
    result = parseCaptionsResponse(raw)
    assert len(result) == 1
    assert result[0]["caption"] == "Teste!"


def test_parseCaptionsResponse_markdown_block():
    from execution.generateCaptions import parseCaptionsResponse
    raw = '```json\n[{"caption": "Teste!", "hashtags": "#teste"}]\n```'
    result = parseCaptionsResponse(raw)
    assert result[0]["caption"] == "Teste!"


def test_parseCaptionsResponse_invalid_raises():
    from execution.generateCaptions import parseCaptionsResponse
    with pytest.raises(ValueError):
        parseCaptionsResponse("não é json nenhum")


# --- nextRowId ---

def test_nextRowId_no_file_returns_001(tmp_path):
    from execution.generateCaptions import nextRowId
    path = str(tmp_path / "queue.csv")
    assert nextRowId(path, "moacir") == "moacir-001"


def test_nextRowId_existing_rows_increments(tmp_path):
    from execution.generateCaptions import nextRowId, CSV_COLUMNS
    path = str(tmp_path / "queue.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerow({col: "" for col in CSV_COLUMNS})
        writer.writerow({col: "" for col in CSV_COLUMNS})
    assert nextRowId(path, "moacir") == "moacir-003"


# --- appendToQueue ---

def test_appendToQueue_creates_file_with_header(tmp_path):
    from execution.generateCaptions import appendToQueue, CSV_COLUMNS
    path = str(tmp_path / "queue.csv")
    rows = [{"id": "moacir-001", "client": "moacir", "platform": "instagram",
             "caption": "Olá!", "status": "draft",
             **{col: "" for col in CSV_COLUMNS if col not in ["id","client","platform","caption","status"]}}]
    appendToQueue(path, rows)
    with open(path) as f:
        lines = f.readlines()
    assert "id" in lines[0]
    assert "moacir-001" in lines[1]


def test_appendToQueue_appends_to_existing(tmp_path):
    from execution.generateCaptions import appendToQueue, CSV_COLUMNS
    path = str(tmp_path / "queue.csv")
    row = {col: "x" for col in CSV_COLUMNS}
    row["id"] = "moacir-001"
    appendToQueue(path, [row])
    row2 = {col: "y" for col in CSV_COLUMNS}
    row2["id"] = "moacir-002"
    appendToQueue(path, [row2])
    with open(path) as f:
        lines = f.readlines()
    assert len(lines) == 3  # header + 2 rows


# --- buildPrompt ---

def test_buildPrompt_contains_briefing():
    from execution.generateCaptions import buildPrompt
    result = buildPrompt("Tom: alegre", [], 3)
    assert "Tom: alegre" in result
    assert "3" in result


def test_buildPrompt_includes_theme_when_given():
    from execution.generateCaptions import buildPrompt
    result = buildPrompt("Tom: alegre", [], 2, theme="promoção de maio")
    assert "promoção de maio" in result


def test_buildPrompt_no_theme_when_empty():
    from execution.generateCaptions import buildPrompt
    result = buildPrompt("Tom: alegre", [], 2, theme="")
    assert "TEMA DESTA SEMANA" not in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHONPATH=. .venv/bin/pytest tests/test_generateCaptions.py -v 2>&1 | tail -15
```

Expected: all FAIL with `ModuleNotFoundError: No module named 'execution.generateCaptions'`

---

### Task 3: Implement generateCaptions.py

**Files:**
- Create: `execution/generateCaptions.py`

- [ ] **Step 1: Create execution/generateCaptions.py**

```python
#!/usr/bin/env python3
"""
Generate Instagram captions using Claude AI.

Reads client briefing + top posts from Neon, calls Claude API,
appends draft captions to queue/{client}/queue.csv.

Usage:
    python execution/generateCaptions.py --client moacir --count 5
    python execution/generateCaptions.py --client moper --count 3 --theme "promoção de maio"
"""

import csv
import json
import logging
import os
import re
import sys
import argparse
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ACTIVE_CLIENTS = ["moacir", "moper", "laika"]

CLIENT_BRIEFING_DIRS = {
    "moacir": "clients/moacir",
    "moper":  "clients/moper-maquinas",
    "laika":  "clients/espaco-laika",
}

CSV_COLUMNS = [
    "id", "client", "platform", "scheduled_at", "caption",
    "media_filename", "status", "cloudinary_url", "ig_post_url",
    "generated_at", "published_at", "error",
]


def loadBriefing(client: str) -> str:
    briefing_dir = CLIENT_BRIEFING_DIRS[client]
    briefing_path = os.path.join(briefing_dir, "briefing.md")
    if not os.path.exists(briefing_path):
        raise FileNotFoundError(f"Briefing não encontrado: {briefing_path}")
    with open(briefing_path, encoding="utf-8") as f:
        return f.read()


def fetchTopPosts(db, client: str, limit: int = 10) -> list:
    rows = db.query(
        """SELECT content, metadata FROM posts
           WHERE client = %s AND metadata IS NOT NULL AND content != ''
           ORDER BY (
               COALESCE(CAST(metadata->>'like_count' AS INTEGER), 0) +
               COALESCE(CAST(metadata->>'comments_count' AS INTEGER), 0)
           ) DESC
           LIMIT %s""",
        (client, limit),
    )
    return rows


def buildPrompt(briefing: str, top_posts: list, count: int, theme: str = "") -> str:
    posts_text = "\n".join([
        f"- {p['content'][:200]} (likes: {(p['metadata'] or {}).get('like_count', 0)}, "
        f"comments: {(p['metadata'] or {}).get('comments_count', 0)})"
        for p in top_posts if p.get("content")
    ]) or "Sem posts anteriores disponíveis."

    theme_section = f"\nTEMA DESTA SEMANA: {theme}" if theme else ""

    return f"""Você é um especialista em redes sociais. Gere {count} legendas para Instagram Reels.

BRIEFING DO CLIENTE:
{briefing}

TOP POSTS (inspire-se no estilo, não copie):
{posts_text}
{theme_section}

Retorne APENAS um JSON válido com esta estrutura (sem texto antes ou depois):
[{{"caption": "legenda completa com emojis e hashtags", "hashtags": "#tag1 #tag2"}}]

Gere exatamente {count} itens no array."""


def parseCaptionsResponse(response_text: str) -> list:
    """Extract JSON list from Claude response text."""
    try:
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", response_text)
    if match:
        return json.loads(match.group(1))
    raise ValueError(f"Não foi possível parsear JSON da resposta: {response_text[:300]}")


def nextRowId(queue_path: str, client: str) -> str:
    """Generate next sequential ID like moacir-001."""
    if not os.path.exists(queue_path):
        return f"{client}-001"
    with open(queue_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    n = len(rows) + 1
    return f"{client}-{n:03d}"


def appendToQueue(queue_path: str, rows: list):
    """Append rows to CSV, creating with header if file doesn't exist."""
    file_exists = os.path.exists(queue_path)
    os.makedirs(os.path.dirname(queue_path), exist_ok=True)
    with open(queue_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Gerar legendas via Claude AI")
    parser.add_argument("--client", required=True, choices=ACTIVE_CLIENTS)
    parser.add_argument("--count",  type=int, default=5)
    parser.add_argument("--theme",  type=str, default="")
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY não encontrado no .env")
        sys.exit(1)

    briefing = loadBriefing(args.client)
    logger.info(f"Briefing carregado para {args.client}")

    from execution.dbClient import DbClient
    with DbClient() as db:
        top_posts = fetchTopPosts(db, args.client)
    logger.info(f"{len(top_posts)} top posts consultados")

    prompt = buildPrompt(briefing, top_posts, args.count, args.theme)

    import anthropic
    client_ai = anthropic.Anthropic(api_key=api_key)
    logger.info("Chamando Claude API...")
    message = client_ai.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    response_text = message.content[0].text
    captions = parseCaptionsResponse(response_text)
    logger.info(f"{len(captions)} legendas geradas")

    queue_path = os.path.join("queue", args.client, "queue.csv")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for i, cap in enumerate(captions):
        row_id = nextRowId(queue_path, args.client) if i == 0 else None
        if i > 0:
            # recalculate after appending
            pass
        full_caption = cap.get("caption", "")
        hashtags = cap.get("hashtags", "")
        if hashtags and hashtags not in full_caption:
            full_caption = f"{full_caption}\n\n{hashtags}"
        rows.append({
            "id":             f"{args.client}-{(len(rows) + 1 + (int(row_id.split('-')[1]) - 1)):03d}" if row_id else "",
            "client":         args.client,
            "platform":       "instagram",
            "scheduled_at":   "",
            "caption":        full_caption,
            "media_filename": "",
            "status":         "draft",
            "cloudinary_url": "",
            "ig_post_url":    "",
            "generated_at":   now,
            "published_at":   "",
            "error":          "",
        })

    # Fix IDs sequentially
    base_n = 0
    if os.path.exists(queue_path):
        with open(queue_path, newline="", encoding="utf-8") as f:
            base_n = len(list(csv.DictReader(f)))
    for i, row in enumerate(rows):
        row["id"] = f"{args.client}-{(base_n + i + 1):03d}"

    appendToQueue(queue_path, rows)
    logger.info(f"✅ {len(rows)} rascunhos salvos em {queue_path}")
    print(f"\nAbra o arquivo no Google Sheets para revisar e aprovar:")
    print(f"  {os.path.abspath(queue_path)}\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run generateCaptions tests**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHONPATH=. .venv/bin/pytest tests/test_generateCaptions.py -v 2>&1 | tail -15
```

Expected: all 9 tests PASS.

---

### Task 4: Write failing tests for publishScheduled helpers

**Files:**
- Create: `tests/test_publishScheduled.py`

- [ ] **Step 1: Create the test file**

Create `tests/test_publishScheduled.py`:

```python
import csv
import os
import pytest
from datetime import datetime, timedelta


# --- detectMediaType ---

def test_detectMediaType_mp4_returns_reels():
    from execution.publishScheduled import detectMediaType
    assert detectMediaType("video.mp4") == "REELS"


def test_detectMediaType_mov_returns_reels():
    from execution.publishScheduled import detectMediaType
    assert detectMediaType("clip.MOV") == "REELS"


def test_detectMediaType_jpg_returns_image():
    from execution.publishScheduled import detectMediaType
    assert detectMediaType("foto.jpg") == "IMAGE"


def test_detectMediaType_png_returns_image():
    from execution.publishScheduled import detectMediaType
    assert detectMediaType("banner.PNG") == "IMAGE"


# --- isDue ---

def test_isDue_approved_past_time_returns_true():
    from execution.publishScheduled import isDue
    past = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    row = {"status": "approved", "scheduled_at": past}
    assert isDue(row) is True


def test_isDue_approved_future_time_returns_false():
    from execution.publishScheduled import isDue
    future = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
    row = {"status": "approved", "scheduled_at": future}
    assert isDue(row) is False


def test_isDue_draft_returns_false():
    from execution.publishScheduled import isDue
    past = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    row = {"status": "draft", "scheduled_at": past}
    assert isDue(row) is False


def test_isDue_empty_scheduled_at_returns_false():
    from execution.publishScheduled import isDue
    row = {"status": "approved", "scheduled_at": ""}
    assert isDue(row) is False


# --- readQueue / writeQueue ---

def test_readQueue_returns_empty_for_missing_file(tmp_path):
    from execution.publishScheduled import readQueue
    path = str(tmp_path / "missing.csv")
    assert readQueue(path) == []


def test_readQueue_returns_rows(tmp_path):
    from execution.publishScheduled import readQueue
    from execution.generateCaptions import CSV_COLUMNS
    path = str(tmp_path / "queue.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerow({col: "x" if col == "id" else "" for col in CSV_COLUMNS})
    rows = readQueue(path)
    assert len(rows) == 1
    assert rows[0]["id"] == "x"


def test_writeQueue_overwrites_file(tmp_path):
    from execution.publishScheduled import writeQueue
    from execution.generateCaptions import CSV_COLUMNS
    path = str(tmp_path / "queue.csv")
    rows = [{col: "v" for col in CSV_COLUMNS}]
    writeQueue(path, rows)
    with open(path) as f:
        content = f.read()
    assert content.count("v,") > 0
```

- [ ] **Step 2: Run to verify they fail**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHONPATH=. .venv/bin/pytest tests/test_publishScheduled.py -v 2>&1 | tail -15
```

Expected: all FAIL with `ModuleNotFoundError: No module named 'execution.publishScheduled'`

---

### Task 5: Implement publishScheduled.py

**Files:**
- Create: `execution/publishScheduled.py`

- [ ] **Step 1: Create execution/publishScheduled.py**

```python
#!/usr/bin/env python3
"""
Publish scheduled Instagram posts from queue CSV.

Reads queue/{client}/queue.csv, uploads media to Cloudinary,
publishes via Instagram Graph API, updates CSV with result.

Usage:
    python execution/publishScheduled.py
    python execution/publishScheduled.py --client moacir
    python execution/publishScheduled.py --dry-run
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import cloudinary
import cloudinary.uploader
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ACTIVE_CLIENTS = ["moacir", "moper", "laika"]

CSV_COLUMNS = [
    "id", "client", "platform", "scheduled_at", "caption",
    "media_filename", "status", "cloudinary_url", "ig_post_url",
    "generated_at", "published_at", "error",
]

POLLING_INTERVAL = 10   # seconds between status checks
POLLING_TIMEOUT  = 300  # 5 minutes max wait for video processing


def detectMediaType(filename: str) -> str:
    """Return REELS for video files, IMAGE for photos."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".mp4", ".mov"):
        return "REELS"
    return "IMAGE"


def isDue(row: Dict) -> bool:
    """Return True if row is approved and scheduled_at <= now."""
    if row.get("status") != "approved":
        return False
    scheduled_str = row.get("scheduled_at", "")
    if not scheduled_str:
        return False
    try:
        scheduled = datetime.strptime(scheduled_str.strip(), "%Y-%m-%d %H:%M")
        return scheduled <= datetime.now()
    except ValueError:
        logger.warning(f"scheduled_at inválido: {scheduled_str}")
        return False


def readQueue(queue_path: str) -> List[Dict]:
    """Read all rows from queue CSV. Returns empty list if file missing."""
    if not os.path.exists(queue_path):
        return []
    with open(queue_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def writeQueue(queue_path: str, rows: List[Dict]):
    """Overwrite queue CSV with given rows."""
    with open(queue_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def configureCloudinary():
    """Configure Cloudinary from .env. Raises if credentials missing."""
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key    = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    if not all([cloud_name, api_key, api_secret]):
        raise EnvironmentError(
            "Cloudinary credentials missing. Set CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET in .env"
        )
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)


def uploadToCloudinary(media_path: str) -> str:
    """Upload file to Cloudinary and return secure public URL."""
    result = cloudinary.uploader.upload(
        media_path,
        resource_type="auto",
        folder="redes-sociais",
    )
    return result["secure_url"]


def createMediaContainer(config: Dict, caption: str, media_url: str, media_type: str) -> str:
    """Create Instagram media container. Returns creation_id."""
    url = f"{config['api_base']}/{config['account_id']}/media"
    params = {"access_token": config["token"]}
    data = {"caption": caption}
    if media_type == "REELS":
        data.update({"media_type": "REELS", "video_url": media_url, "share_to_feed": "true"})
    else:
        data.update({"image_url": media_url})
    r = requests.post(url, params=params, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["id"]


def waitForContainer(config: Dict, creation_id: str) -> bool:
    """Poll until container status is FINISHED. Raises on error or timeout."""
    url = f"{config['api_base']}/{creation_id}"
    params = {"fields": "status_code", "access_token": config["token"]}
    deadline = time.time() + POLLING_TIMEOUT
    while time.time() < deadline:
        r = requests.get(url, params=params, timeout=30)
        if r.ok:
            status = r.json().get("status_code", "")
            if status == "FINISHED":
                return True
            if status == "ERROR":
                raise RuntimeError(f"Container processing failed: {r.json()}")
        time.sleep(POLLING_INTERVAL)
    raise TimeoutError(f"Video processing timeout after {POLLING_TIMEOUT}s")


def publishContainer(config: Dict, creation_id: str) -> str:
    """Publish the container. Returns IG media ID."""
    url = f"{config['api_base']}/{config['account_id']}/media_publish"
    r = requests.post(
        url,
        params={"access_token": config["token"]},
        data={"creation_id": creation_id},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["id"]


def getPostUrl(config: Dict, media_id: str) -> str:
    """Fetch permalink for a published post."""
    url = f"{config['api_base']}/{media_id}"
    r = requests.get(url, params={"fields": "permalink", "access_token": config["token"]}, timeout=30)
    if r.ok:
        return r.json().get("permalink", "")
    return ""


def publishPost(config: Dict, row: Dict, media_path: str, dry_run: bool) -> Dict:
    """Execute full publish flow for one row. Returns updated row dict."""
    if dry_run:
        logger.info(
            f"  [DRY-RUN] {row['client']} | {row['scheduled_at']} | "
            f"{row['caption'][:60]}... | {row['media_filename']}"
        )
        return row

    updated = dict(row)
    try:
        # Upload media
        logger.info(f"  Uploading {row['media_filename']} to Cloudinary...")
        cloudinary_url = uploadToCloudinary(media_path)
        updated["cloudinary_url"] = cloudinary_url
        logger.info(f"  Cloudinary URL: {cloudinary_url[:60]}...")

        # Create container
        from execution.fetchInstagramData import loadConfig
        media_type   = detectMediaType(row["media_filename"])
        creation_id  = createMediaContainer(config, row["caption"], cloudinary_url, media_type)
        logger.info(f"  Container criado: {creation_id}")

        # Wait for processing (Reels need time)
        if media_type == "REELS":
            logger.info(f"  Aguardando processamento do vídeo...")
            waitForContainer(config, creation_id)

        # Publish
        media_id = publishContainer(config, creation_id)
        ig_url   = getPostUrl(config, media_id)

        updated["status"]       = "published"
        updated["ig_post_url"]  = ig_url
        updated["published_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        updated["error"]        = ""
        logger.info(f"  ✅ Publicado: {ig_url}")

    except Exception as e:
        updated["status"] = "failed"
        updated["error"]  = str(e)[:500]
        logger.error(f"  ❌ Falha: {e}")

    return updated


def logToNeon(client: str, published: int, failed: int, duration_ms: int):
    """Insert execution log into Neon."""
    try:
        from execution.dbClient import DbClient
        with DbClient() as db:
            db.execute(
                """INSERT INTO execution_logs (script_name, status, message, details, duration_ms)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    "publishScheduled",
                    "success" if failed == 0 else "partial",
                    f"Published {published}, failed {failed} for {client}",
                    json.dumps({"client": client, "published": published, "failed": failed}),
                    duration_ms,
                ),
            )
    except Exception as e:
        logger.warning(f"Neon log failed (non-fatal): {e}")


def processClient(client: str, dry_run: bool):
    """Process all due posts for one client."""
    from execution.fetchInstagramData import loadConfig
    queue_path = os.path.join("queue", client, "queue.csv")
    rows = readQueue(queue_path)

    due_rows = [(i, row) for i, row in enumerate(rows) if isDue(row)]
    if not due_rows:
        logger.info(f"  {client}: nenhum post agendado para publicar")
        return

    logger.info(f"  {client}: {len(due_rows)} post(s) para publicar")

    try:
        config = loadConfig(client)
    except EnvironmentError as e:
        logger.error(f"  {client}: config error — {e}")
        return

    published = 0
    failed    = 0
    start     = datetime.utcnow()

    for idx, row in due_rows:
        media_path = os.path.join("queue", client, "media", row["media_filename"])
        if not os.path.exists(media_path) and not dry_run:
            logger.error(f"  Mídia não encontrada: {media_path}")
            rows[idx]["status"] = "failed"
            rows[idx]["error"]  = f"Arquivo não encontrado: {media_path}"
            failed += 1
            continue

        rows[idx] = publishPost(config, row, media_path, dry_run)
        if not dry_run:
            if rows[idx]["status"] == "published":
                published += 1
            elif rows[idx]["status"] == "failed":
                failed += 1
            writeQueue(queue_path, rows)  # write after each post (safe)

    if not dry_run:
        duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
        logToNeon(client, published, failed, duration_ms)
        logger.info(f"  {client}: {published} publicado(s), {failed} falha(s)")


def main():
    parser = argparse.ArgumentParser(description="Publicar posts agendados")
    parser.add_argument("--client",  type=str, default="", help="Filtrar por cliente")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem publicar")
    args = parser.parse_args()

    if not args.dry_run:
        try:
            configureCloudinary()
        except EnvironmentError as e:
            logger.error(str(e))
            sys.exit(1)

    clients = [args.client] if args.client else ACTIVE_CLIENTS
    logger.info(f"publishScheduled | clientes: {clients} | dry-run: {args.dry_run}")

    for client in clients:
        logger.info(f"Processando: {client}")
        processClient(client, args.dry_run)

    logger.info("Concluído.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run publishScheduled tests**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHONPATH=. .venv/bin/pytest tests/test_publishScheduled.py -v 2>&1 | tail -15
```

Expected: all 11 tests PASS.

- [ ] **Step 3: Run all tests together**

```bash
PYTHONPATH=. .venv/bin/pytest tests/ -v 2>&1 | tail -20
```

Expected: 30 tests PASS (10 generateReport + 9 generateCaptions + 11 publishScheduled).

---

### Task 6: Update collectAll.sh and verify credentials

**Files:**
- Modify: `execution/collectAll.sh`

- [ ] **Step 1: Add publishScheduled.py to collectAll.sh**

Open `execution/collectAll.sh`. After the last `echo "laika: exit $?" >> "$LOG_FILE"` line and before the closing `echo`, add:

```bash
PYTHONPATH="$PROJECT_DIR" "$PYTHON" execution/publishScheduled.py >> "$LOG_FILE" 2>&1
echo "publish: exit $?" >> "$LOG_FILE"
```

The final file should look like:
```bash
#!/bin/bash
# Coleta diária de métricas — todos os clientes configurados
# Executado via crontab. Logs em .tmp/logs/

PROJECT_DIR="/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHON="$PROJECT_DIR/.venv/bin/python"
LOG_DIR="$PROJECT_DIR/.tmp/logs"
LOG_FILE="$LOG_DIR/collect_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') — Coleta iniciada ===" >> "$LOG_FILE"

cd "$PROJECT_DIR"

PYTHONPATH="$PROJECT_DIR" "$PYTHON" execution/fetchInstagramData.py --client moacir --period 7 --save >> "$LOG_FILE" 2>&1
echo "moacir: exit $?" >> "$LOG_FILE"

PYTHONPATH="$PROJECT_DIR" "$PYTHON" execution/fetchInstagramData.py --client moper --period 7 --save >> "$LOG_FILE" 2>&1
echo "moper: exit $?" >> "$LOG_FILE"

PYTHONPATH="$PROJECT_DIR" "$PYTHON" execution/fetchInstagramData.py --client laika --period 7 --save >> "$LOG_FILE" 2>&1
echo "laika: exit $?" >> "$LOG_FILE"

PYTHONPATH="$PROJECT_DIR" "$PYTHON" execution/publishScheduled.py >> "$LOG_FILE" 2>&1
echo "publish: exit $?" >> "$LOG_FILE"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') — Coleta concluída ===" >> "$LOG_FILE"
```

- [ ] **Step 2: Test dry-run (before adding real credentials)**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHONPATH=. .venv/bin/python execution/publishScheduled.py --dry-run 2>&1 | grep -v NotOpenSSL | grep -v warnings
```

Expected output:
```
INFO publishScheduled | clientes: ['moacir', 'moper', 'laika'] | dry-run: True
INFO Processando: moacir
INFO   moacir: nenhum post agendado para publicar
INFO Processando: moper
INFO   moper: nenhum post agendado para publicar
INFO Processando: laika
INFO   laika: nenhum post agendado para publicar
INFO Concluído.
```

- [ ] **Step 3: Add Cloudinary and Anthropic credentials to .env**

1. Cloudinary: acesse cloudinary.com → crie conta free → painel → API Keys → copie Cloud Name, API Key, API Secret
2. Anthropic: acesse console.anthropic.com → API Keys → crie chave → copie

Abra `.env` e preencha:
```
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret
ANTHROPIC_API_KEY=sk-ant-...
```

---

### Task 7: End-to-end integration test

**Files:** None — run only.

- [ ] **Step 1: Generate captions for moacir**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHONPATH=. .venv/bin/python execution/generateCaptions.py --client moacir --count 3 2>&1 | grep -v NotOpenSSL | grep -v warnings
```

Expected:
```
INFO Briefing carregado para moacir
INFO 10 top posts consultados
INFO Chamando Claude API...
INFO 3 legendas geradas
INFO ✅ 3 rascunhos salvos em queue/moacir/queue.csv

Abra o arquivo no Google Sheets para revisar e aprovar:
  /Users/.../queue/moacir/queue.csv
```

- [ ] **Step 2: Verify CSV content**

```bash
cat queue/moacir/queue.csv
```

Expected: header + 3 rows com `status=draft`, captions preenchidas, `scheduled_at` e `media_filename` vazios.

- [ ] **Step 3: Simulate approval (test publish flow)**

Edit `queue/moacir/queue.csv` manually (or via the script below) to simulate one approved post:

```bash
PYTHONPATH=. .venv/bin/python3 -c "
import csv
from execution.generateCaptions import CSV_COLUMNS
from datetime import datetime, timedelta

path = 'queue/moacir/queue.csv'
with open(path, newline='') as f:
    rows = list(csv.DictReader(f))

# Approve first row with past scheduled_at and a media filename
rows[0]['status'] = 'approved'
rows[0]['scheduled_at'] = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M')
rows[0]['media_filename'] = 'test_video.mp4'

with open(path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
print('Row approved for testing')
"
```

- [ ] **Step 4: Run dry-run to confirm it detects the post**

```bash
PYTHONPATH=. .venv/bin/python execution/publishScheduled.py --client moacir --dry-run 2>&1 | grep -v NotOpenSSL | grep -v warnings
```

Expected:
```
INFO publishScheduled | clientes: ['moacir'] | dry-run: True
INFO Processando: moacir
INFO   moacir: 1 post(s) para publicar
INFO   [DRY-RUN] moacir | 2026-05-10 ... | <caption>... | test_video.mp4
INFO Concluído.
```

- [ ] **Step 5: Real publish (when ready)**

Place a real video file at `queue/moacir/media/test_video.mp4` (any short `.mp4`), ensure `.env` has Cloudinary + Anthropic credentials, then:

```bash
PYTHONPATH=. .venv/bin/python execution/publishScheduled.py --client moacir 2>&1 | grep -v NotOpenSSL | grep -v warnings
```

Expected:
```
INFO Processando: moacir
INFO   moacir: 1 post(s) para publicar
INFO   Uploading test_video.mp4 to Cloudinary...
INFO   Cloudinary URL: https://res.cloudinary.com/...
INFO   Container criado: 12345678
INFO   Aguardando processamento do vídeo...
INFO   ✅ Publicado: https://www.instagram.com/reel/...
INFO   moacir: 1 publicado(s), 0 falha(s)
```

- [ ] **Step 6: Update HANDOFF.md**

In `HANDOFF.md`, add to the features table:
```
| Automação | Publicação automática | `[5-T]` ✅ | generateCaptions.py + publishScheduled.py |
```

---

## Self-Review

**Spec coverage:**
- ✅ generateCaptions.py — briefing + top posts + Claude API + CSV append
- ✅ publishScheduled.py — Cloudinary + Instagram 2-step publish + polling + error handling
- ✅ Queue CSV structure — all 12 columns defined and used
- ✅ Briefing files — 3 clients created in Task 1
- ✅ detectMediaType — REELS vs IMAGE
- ✅ dry-run flag — implemented, tested
- ✅ Error handling — all 5 error cases from spec handled (media missing, Cloudinary fail, API error, timeout, future scheduled_at)
- ✅ collectAll.sh update — Task 6 Step 1
- ✅ .env credentials — Task 1 Step 3 and Task 6 Step 3

**Type consistency:**
- `CSV_COLUMNS` defined in `generateCaptions.py`, imported in `test_publishScheduled.py` from there — consistent
- `loadConfig()` imported from `fetchInstagramData` in `publishScheduled.py` — consistent with existing pattern
- `isDue()` expects `"%Y-%m-%d %H:%M"` format — matches what the spec says users enter (`2026-05-11 08:00`) — consistent
- `detectMediaType()` called in `publishPost()` and tested in isolation — consistent

**Placeholder scan:** No TBD, TODO, or vague steps. All code blocks are complete.
