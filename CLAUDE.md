# CLAUDE.md - Redes Sociais Project

## Project Purpose
**Social media management platform** - A system for managing, scheduling, analyzing, and automating social media content across multiple platforms.

## Architecture Overview: 3-Layer System

This project uses a **3-layer architecture** to separate concerns and maximize reliability through deterministic execution and intelligent orchestration.

### Layer 1: Directives (What to do)
- **Location**: `directives/` directory
- **Format**: Markdown SOPs (Standard Operating Procedures)
- **Content**: Goals, inputs, tools/scripts to use, outputs, edge cases
- **Purpose**: Natural language instructions that define HOW to accomplish tasks
- **Examples**: `directives/scrape_social_media.md`, `directives/schedule_post.md`, `directives/analytics_report.md`

### Layer 2: Orchestration (Decision making)
- **Who**: Claude (you) - the intelligent orchestrator
- **Responsibility**:
  - Read directives and understand intent
  - Call execution tools in the right order
  - Handle errors and exceptions
  - Ask for clarification when needed
  - Update directives with learnings
- **Principle**: You're the glue between intent and execution. Don't do the work yourself—route to execution scripts.

### Layer 3: Execution (Doing the work)
- **Location**: `execution/` directory
- **Language**: Python with deterministic logic
- **Content**: API calls, data processing, file operations, database interactions
- **Configuration**: Environment variables in `.env`
- **Principles**: Reliable, testable, fast, well-commented
- **Why**: 90% accuracy per step = 59% success over 5 steps. Pushing complexity into deterministic code fixes this.

---

## Coding Conventions

### Function Naming
- **camelCase** for all functions and methods
- **PascalCase** for classes
- **UPPER_SNAKE_CASE** for constants

**Examples:**
```python
# ✅ Correct
def fetchSocialMediaData(platform):
    pass

class InstagramAPI:
    pass

MAX_RETRIES = 3

# ❌ Wrong
def fetch_social_media_data(platform):
    pass

def FetchSocialMediaData(platform):
    pass
```

### File Organization

```
.
├── CLAUDE.md                 # This file
├── directives/               # SOPs in Markdown
│   ├── scrape_social_media.md
│   ├── schedule_post.md
│   ├── analytics_report.md
│   └── README.md
├── execution/                # Python scripts
│   ├── __init__.py
│   ├── fetchSocialMediaData.py
│   ├── schedulePost.py
│   ├── generateAnalytics.py
│   └── utils.py
├── .tmp/                     # Temporary files (never commit)
│   ├── scraped_data/
│   ├── exports/
│   └── processing/
├── .env                      # Environment variables (never commit)
├── .gitignore               # Git ignore rules
└── credentials.json         # OAuth (in .gitignore)
```

### Environment Variables (.env)
```
# Social Media APIs
INSTAGRAM_TOKEN=xxx
TWITTER_TOKEN=xxx
FACEBOOK_TOKEN=xxx

# VPS/Database
VPS_HOST=your-vps-host
VPS_USER=username
VPS_SSH_KEY=/path/to/key
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=redes_sociais
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# Google Cloud (if needed)
GOOGLE_SHEETS_KEY=xxx
GOOGLE_SLIDES_KEY=xxx
```

---

## Operating Principles

### 1. Check for Tools First
Before writing a script, check `execution/` directory per your directive.
- Only create new scripts if none exist
- Reuse existing utilities in `execution/utils.py`
- Name scripts clearly: `verb + Entity + Action.py` (e.g., `fetchTwitterAnalytics.py`)

### 2. Self-Anneal When Things Break
1. **Read** error message and stack trace
2. **Fix** the script (or ask user if it involves paid tokens/credits)
3. **Test** again locally
4. **Update** directive with learnings (API limits, timing, edge cases)
5. **Update** this CLAUDE.md with new patterns discovered

**Example**: Hit Twitter API rate limit → investigate API docs → find batch endpoint → rewrite script → test → update directive with rate-limit strategy → system is now stronger

### 3. Update Directives as You Learn
Directives are **living documents**. When you discover:
- API constraints or gotchas
- Better/faster approaches
- Common errors and solutions
- Timing expectations
- Edge cases

**Update the directive immediately.** This makes the next run smoother.

---

## Self-Annealing Loop (Error Management)

When something breaks:

```
1. Error Occurs
   ↓
2. Read Error & Stack Trace
   ↓
3. Fix Execution Script
   ↓
4. Test Script (until it works)
   ↓
5. Update Directive with New Flow
   ↓
6. Document in CLAUDE.md
   ↓
System is now stronger ✓
```

---

## Common Task Workflows

### Adding a New Feature
1. **Read** the relevant directive (or create one)
2. **Create** execution script in `execution/` following camelCase convention
3. **Write** utilities in `execution/utils.py` if reusable
4. **Test** the script with real data (or mock data)
5. **Update** directive with any discoveries
6. **Update** this CLAUDE.md if new patterns emerge

### Debugging Issues
1. **Check** the directive first—understand intended behavior
2. **Review** the execution script + error logs
3. **Test** the failing component in isolation
4. **Fix** the root cause (not symptoms)
5. **Re-test** full flow before declaring fixed
6. **Update** directive + CLAUDE.md with solution

### Database Operations
- All DB access goes through execution scripts
- Use environment variables for credentials (never hardcode)
- Keep connection pools open for performance
- Log all transactions (schema changes, data deletes, etc.)
- Backup before major operations

---

## VPS & SSH Integration

### Connection Setup (TODO - Fill In)
```
VPS Host: [TO BE FILLED]
SSH Port: [TO BE FILLED]
SSH User: [TO BE FILLED]
SSH Key Location: [TO BE FILLED]
```

### Connection Method
All SSH commands will use authenticated key-based SSH without requiring copy-paste:
- Store SSH key in `.env` as `VPS_SSH_KEY`
- Use `Paramiko` or `fabric` Python library for automation
- Direct PostgreSQL access via SSH tunnel when needed
- Results streamed directly to execution layer (minimal logging)

---

## Deliverables vs Intermediates

### Deliverables (User-Accessible)
- Google Sheets (analytics, data exports)
- Google Slides (reports, visualizations)
- Cloud storage files
- Live dashboards

### Intermediates (Temporary)
- All files in `.tmp/` can be deleted anytime
- Scraped raw data
- Processing logs
- Export staging files

**Principle**: Local files are ONLY for fast processing. Real deliverables live in cloud services.

---

## Important Infrastructure Notes

### Portainer + Docker SWARM
- Running on VPS (details in separate doc)
- Services available for deployment
- [TODO: Link or embed XYZ infrastructure file]

### PostgreSQL
- Location: [TO BE FILLED]
- Direct access via SSH tunnel [TO BE FILLED - credentials]
- Schema: [TO BE FILLED]

---

## Getting Started Checklist

- [ ] Fill in VPS credentials (host, user, key, port)
- [ ] Fill in PostgreSQL credentials and connection details
- [ ] Fill in social media API credentials
- [ ] Create first directive (e.g., `directives/setup.md`)
- [ ] Create initial execution script
- [ ] Test SSH tunnel to VPS
- [ ] Test PostgreSQL connection
- [ ] Document any new patterns discovered

---

## Quick Reference

**When you need to:**

| Task | Do This |
|------|---------|
| Create a new automation | Create directive in `directives/`, then execution script in `execution/` |
| Fix a bug | Read directive → fix execution script → test → update directive |
| Add a utility function | Add to `execution/utils.py` with camelCase naming |
| Store sensitive info | Add to `.env`, reference with `os.getenv()` |
| Run Python scripts | Use direct SSH/Paramiko integration (no copy-paste needed) |
| Debug API issues | Check directive for API details, use execution script traces |
| Update workflows | Modify directive, self-anneal with learnings |

---

## Contact & Support

For questions or issues:
- Check the relevant directive first
- Review CLAUDE.md for conventions
- Update CLAUDE.md + directive when you discover patterns
- Self-anneal: fix → test → document

---

## Context Guardian

Monitore o peso do contexto ao longo de cada sessão. Quando perceber que o histórico
está longo — muitos arquivos lidos, muitos tool calls encadeados, respostas acumuladas —
termine a tarefa atual e invoque o skill `context-guardian` sem esperar instrução do usuário.

Sinais de contexto pesado:
- Mais de 15–20 tool calls na sessão
- Arquivos grandes lidos (execution/, directives/, PLANO.md)
- Respostas longas encadeadas
- Sensação de que "já fiz muita coisa nesta sessão"

**Não espere chegar ao limite.** Agir cedo garante handoff limpo e docs atualizados.

---

**Last Updated**: 2026-06-06
**Architecture**: 3-Layer (Directives → Orchestration → Execution)
**Status**: 🟡 Em progresso — infra configurada, coletas pendentes de teste

---

## Tracking de Features

Ver `docs/PLANO.md` — atualizar imediatamente após cada etapa concluída.

Tags de progresso (adaptadas para projeto sem frontend):
- `[0]` Planejado, não iniciado
- `[1-S]` Diretiva criada OU schema definido em código
- `[2-E]` Script de execução existe
- `[3-H]` Credenciais configuradas no .env (pronto para rodar)
- `[4-C]` Executado com dado real da API (ao menos uma vez)
- `[5-T]` Pipeline completo testado nesta sessão (coleta → DB → relatório)

**Critério de "pronto" para qualquer feature:**
Pipeline testado nesta sessão: credenciais válidas → coleta retorna dados → dados salvos no DB → relatório gerado.
"Script existe" não conta. "Credenciais configuradas" não conta.

## Estado Atual do Projeto

Ver `HANDOFF.md` para estado detalhado e próximos passos.

**Resumo rápido:**
- Único pipeline confirmado: Instagram → moacir (backup manual existe)
- Todos os tokens configurados no `.env` mas não verificados nesta sessão
- Banco de dados: schema definido, aplicação no DB real não confirmada
- TikTok: histórico de problema com conta Business (ver `directives/troubleshoot_tiktok_account.md`)

## Clientes

| Cliente | .env prefix | Plataformas |
|---------|-------------|-------------|
| moacir | `MOACIR_` | Instagram, TikTok, YouTube |
| espaco-laika | `LAIKA_` | Instagram, TikTok, YouTube |
| namasa | `NAMASA_` | Instagram, TikTok, YouTube |
| moper-maquinas | `MOPER_` | Instagram, TikTok, YouTube |

## Workflow Obrigatório para Features Novas

1. `superpowers:brainstorming` — antes de qualquer código
2. `superpowers:writing-plans` — se a feature for multi-step
3. `superpowers:dispatching-parallel-agents` — coleta de múltiplos clientes em paralelo
4. `superpowers:systematic-debugging` — para qualquer erro de API ou conexão
5. `superpowers:verification-before-completion` — antes de marcar `[5-T]`

**Debug de conexão:** sempre rodar `execution/testConnections.py` primeiro.
**Novo cliente:** copiar estrutura de `clients/moacir/`, atualizar prefixo no `.env`.
