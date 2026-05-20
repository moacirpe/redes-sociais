# Handoff — Redes Sociais
_Atualizado em: 2026-05-09_

## Estado atual

- **Pipeline completo funcionando:** Instagram moacir, moper, laika → Neon PostgreSQL ✅
- **Banco ativo:** Neon (cloud PostgreSQL, sem VPS, sem SSH) — `DATABASE_URL` configurado
- **Laika:** page token EAA salvo, fetchInstagramData adaptado para graph.facebook.com ✅
- **Credenciais vazias no .env:** TikTok (todos), YouTube (todos), Instagram namasa
- **VPS descartado:** substituído por Neon — sem necessidade de SSH tunnel
- **Auto-accept configurado:** `.claude/settings.local.json` tem `defaultMode: bypassPermissions`

**Próximos passos:**
1. Preencher tokens do Instagram namasa (requer acesso à conta que gerencia a página do Facebook Namasa)
2. Desenvolver relatório mensal (`execution/generateReport.py`)

---

## Pipeline confirmado nesta sessão

```bash
python execution/setupDatabase.py   # ✅ tabelas criadas no Neon
python execution/testConnections.py # ✅ Neon PostgreSQL: connected OK
python execution/fetchInstagramData.py --period 7 --save  # ✅ dados salvos
```

Dados salvos no Neon:
- `social_accounts`: @moacir.moper upserted
- `metrics`: snapshot de 2026-04-22 (followers, engagement_rate)
- `posts`: 10 posts recentes upserted
- `execution_logs`: log do run salvo

---

## Credenciais — o que está preenchido no .env

| Variável | Status |
|----------|--------|
| `DATABASE_URL` (Neon) | ✅ preenchido |
| `INSTAGRAM_CLIENT_NAME` | ✅ = `moacir` |
| `META_APP_ID` / `META_APP_SECRET` | ✅ preenchido |
| `INSTAGRAM_TOKEN` / `INSTAGRAM_BUSINESS_ACCOUNT_ID` | ✅ preenchido |
| `MOPER_INSTAGRAM_TOKEN` | ✅ preenchido (sem ACCOUNT_ID) |
| `MOACIR_TIKTOK_*` | ❌ vazio |
| `MOACIR_YOUTUBE_*` | ❌ vazio |
| `LAIKA_INSTAGRAM_TOKEN` / `LAIKA_INSTAGRAM_ACCOUNT_ID` | ✅ preenchido (page token EAA) |
| `NAMASA_INSTAGRAM_*` | ❌ vazio |
| `TIKTOK_CLIENT_KEY` / `_SECRET` | ❌ vazio |
| `VPS_*` / `POSTGRES_*` | ❌ removidos — substituídos por Neon |

---

## Status de Features

> Fonte da verdade: `docs/PLANO.md`
> Tags: `[0]` planejado · `[1-S]` diretiva/schema · `[2-E]` script · `[3-H]` creds prontas · `[4-C]` testado com dado real · `[5-T]` ✅ pipeline completo

| Frente | Feature | Status | Próxima etapa |
|--------|---------|--------|---------------|
| Infra | Neon PostgreSQL | `[5-T]` ✅ | Pronto — sem ação necessária |
| Infra | SSH → VPS | cancelado | Substituído por Neon |
| Auth | Meta/Instagram OAuth | `[3-H]` | Verificar expiração dos tokens (60 dias) |
| Auth | TikTok OAuth | `[1-S]` | Preencher TIKTOK_CLIENT_KEY/SECRET no .env |
| Auth | YouTube OAuth | `[1-S]` | Preencher YOUTUBE vars + seguir `YOUTUBE_SETUP.md` |
| moacir | Coleta Instagram | `[5-T]` ✅ | Agendar via cron |
| moacir | Coleta TikTok | `[1-S]` | Preencher MOACIR_TIKTOK_* no .env |
| moacir | Coleta YouTube | `[1-S]` | Preencher MOACIR_YOUTUBE_* no .env |
| moacir | Relatório mensal | `[5-T]` ✅ | Pronto — console + CSV (`execution/generateReport.py`) |
| moper-maquinas | Coleta Instagram | `[5-T]` ✅ | Pronto |
| espaco-laika | Coleta Instagram | `[5-T]` ✅ | Pronto — page token EAA, graph.facebook.com |
| namasa | Coleta Instagram | `[1-S]` | Preencher NAMASA_INSTAGRAM_TOKEN/ACCOUNT_ID |
| Automação | Agendamento cron | `[5-T]` ✅ | Todo dia 8h — `execution/collectAll.sh` |

---

## Arquivos de tracking

| Arquivo | Propósito |
|---------|-----------|
| `HANDOFF.md` | Este arquivo — estado atual do projeto |
| `docs/PLANO.md` | Lista completa de features com status |
| `docs/api-audit.md` | Quais APIs foram testadas vs prontas vs não iniciadas |
| `CLAUDE.md` | Arquitetura, convenções, workflow, tabela de clientes |

---

## Infraestrutura

- **Python:** `.venv/` com psycopg2-binary, requests, python-dotenv
- **DB:** Neon PostgreSQL (cloud) via `DATABASE_URL` — sem SSH, sem VPS
- **Schema:** 4 tabelas — `social_accounts`, `posts`, `metrics`, `execution_logs`
- **Clientes:** moacir (`MOACIR_`), espaco-laika (`LAIKA_`), namasa (`NAMASA_`), moper-maquinas (`MOPER_`)
- **Auto-accept:** `.claude/settings.local.json` → `defaultMode: bypassPermissions`
