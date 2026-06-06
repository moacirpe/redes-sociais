# Handoff — Redes Sociais
_Atualizado em: 2026-06-06_

## Estado atual

- **Pipeline Instagram:** moacir, moper, laika → Neon PostgreSQL ✅
- **Banco ativo:** Neon (cloud PostgreSQL) — `DATABASE_URL` configurado no Railway e no .env
- **WhatsApp bot Moper:** rodando no Railway.app — Claude Haiku, memória 30 dias, horário comercial, transferência para humano ✅
- **Catálogo Moper Paleteiras:** publicado no GitHub Pages ✅ → https://moacirpe.github.io/redes-sociais/paleteiras/
- **Repositório GitHub:** agora **público** (necessário para GitHub Pages gratuito)
- **Meta Business Verification:** múltiplas tentativas de rejeição por documento de identidade. Melissa submeteu novo documento em 05/06/2026 — aguardando resultado (até 48h)
- **Espaço Laika WhatsApp:** pendente — Moacir decide se migra o número (67) 99857-4771 para bot (decisão: dono do número perderia acesso pelo app, usaria Meta Business Suite)
- **Credenciais vazias no .env:** TikTok (todos), YouTube (todos), Instagram namasa

---

## Próximos passos (por prioridade)

1. ⏳ **Verificação Meta:** aguardar resultado (Melissa submeteu 05/06). Se aprovada → atualizar `MOPER_WHATSAPP_PHONE_NUMBER_ID` no Railway com o número real da Moper (47 99232-5747)
2. **Catálogo:** compartilhar link https://moacirpe.github.io/redes-sociais/paleteiras/ nas redes sociais da Moper ✅ (Melissa já tem o link)
3. **Espaço Laika WhatsApp:** Moacir precisa decidir sobre o número (67) 99857-4771
4. **Token WhatsApp:** renovar em ~60 dias via `./renovarToken.sh`
5. **Instagram Namasa:** preencher `NAMASA_INSTAGRAM_TOKEN` / `NAMASA_INSTAGRAM_ACCOUNT_ID` no .env
6. **TikTok/YouTube:** sem credenciais — preencher quando disponíveis
7. **Publicação automática de posts:** spec em `docs/superpowers/specs/2026-05-10-auto-publish-design.md`, implementação pendente

---

## Infraestrutura Railway (WhatsApp Bot)

- **URL:** https://web-production-476d9.up.railway.app
- **Variáveis obrigatórias no Railway:**
  - `MOPER_WHATSAPP_PHONE_NUMBER_ID`
  - `MOPER_WHATSAPP_TOKEN`
  - `MOPER_WHATSAPP_VERIFY_TOKEN`
  - `ANTHROPIC_API_KEY`
  - `DATABASE_URL` (Neon)
- **Deploy:** automático via push no GitHub (branch main)
- **Procfile:** `gunicorn execution.whatsappWebhook:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
- **Atenção:** imports do WhatsApp são fault-tolerant — app sobe mesmo se banco falhar

---

## Catálogo de Paleteiras

- **URL pública:** https://moacirpe.github.io/redes-sociais/paleteiras/
- **Fonte:** `docs/paleteiras/index.html` + `docs/paleteiras/img/`
- **Hospedagem:** GitHub Pages (branch main, pasta /docs)
- **8 produtos** com specs, condições de pagamento e botão WhatsApp para cada um
- **Para atualizar:** editar `docs/paleteiras/index.html` e fazer push — GitHub Pages atualiza automaticamente

---

## Catálogo de Verificação Meta (histórico)

| Data | Evento |
|------|--------|
| ~01/06 | Primeiro envio de documentos |
| 03/06 | Rejeição #1 — problema com documento de identidade |
| 04/06 | Melissa resubmitiu com RG |
| 05/06 | Rejeição #2 — mesmo problema. Nova submissão com documento diferente |
| 05/06+ | Aguardando resultado (até 48h) |

**Problemas identificados:**
- Documento de identidade rejeitado repetidamente (CNH com qualidade ruim)
- Número +556734162407 apareceu errado (deveria ser +554734162407 com DDD 47)
- Nome da empresa no Meta ("Moper Materiais de Construção LTDA") pode não bater com CNPJ ("ROMOA MATERIAIS PARA CONSTRUCAO LTDA") — potencial causa de rejeição futura

---

## Credenciais — status no .env

| Variável | Status |
|----------|--------|
| `DATABASE_URL` (Neon) | ✅ preenchido |
| `INSTAGRAM_CLIENT_NAME` | ✅ = `moacir` |
| `META_APP_ID` / `META_APP_SECRET` | ✅ preenchido |
| `INSTAGRAM_TOKEN` / `INSTAGRAM_BUSINESS_ACCOUNT_ID` | ✅ preenchido |
| `MOPER_INSTAGRAM_TOKEN` | ✅ preenchido |
| `MOPER_WHATSAPP_PHONE_NUMBER_ID` | ✅ número de teste (trocar após verificação Meta) |
| `MOPER_WHATSAPP_TOKEN` | ✅ preenchido (renovar em ~60 dias via `./renovarToken.sh`) |
| `LAIKA_INSTAGRAM_TOKEN` / `LAIKA_INSTAGRAM_ACCOUNT_ID` | ✅ preenchido (page token EAA) |
| `MOACIR_TIKTOK_*` | ❌ vazio |
| `MOACIR_YOUTUBE_*` | ❌ vazio |
| `NAMASA_INSTAGRAM_*` | ❌ vazio |
| `TIKTOK_CLIENT_KEY` / `_SECRET` | ❌ vazio |

---

## Status de Features

> Tags: `[0]` planejado · `[1-S]` diretiva/schema · `[2-E]` script · `[3-H]` creds prontas · `[4-C]` testado com dado real · `[5-T]` ✅ pipeline completo

| Frente | Feature | Status | Próxima etapa |
|--------|---------|--------|---------------|
| Infra | Neon PostgreSQL | `[5-T]` ✅ | Pronto |
| Auth | Meta/Instagram OAuth | `[3-H]` | Verificar expiração dos tokens (60 dias) |
| Auth | TikTok OAuth | `[1-S]` | Preencher TIKTOK_CLIENT_KEY/SECRET no .env |
| Auth | YouTube OAuth | `[1-S]` | Preencher YOUTUBE vars + seguir `YOUTUBE_SETUP.md` |
| moacir | Coleta Instagram | `[5-T]` ✅ | Pronto |
| moacir | Coleta TikTok | `[1-S]` | Preencher MOACIR_TIKTOK_* no .env |
| moacir | Coleta YouTube | `[1-S]` | Preencher MOACIR_YOUTUBE_* no .env |
| moacir | Relatório mensal | `[5-T]` ✅ | Pronto — `execution/generateReport.py` |
| moper-maquinas | Coleta Instagram | `[5-T]` ✅ | Pronto |
| moper-maquinas | WhatsApp Bot | `[4-C]` ✅ | Aguardando verificação Meta |
| moper-maquinas | Catálogo paleteiras | `[5-T]` ✅ | Publicado no GitHub Pages |
| espaco-laika | Coleta Instagram | `[5-T]` ✅ | Pronto |
| espaco-laika | WhatsApp Bot | `[0]` | Moacir decide sobre número (67) 99857-4771 |
| namasa | Coleta Instagram | `[1-S]` | Preencher NAMASA_INSTAGRAM_TOKEN/ACCOUNT_ID |
| Automação | Agendamento cron | `[5-T]` ✅ | Todo dia 8h — `execution/collectAll.sh` |
| Automação | Auto-publish posts | `[1-S]` | Spec pronta, implementação pendente |

---

## Arquivos de tracking

| Arquivo | Propósito |
|---------|-----------|
| `HANDOFF.md` | Este arquivo — estado atual do projeto |
| `docs/PLANO.md` | Lista completa de features com status |
| `CLAUDE.md` | Arquitetura, convenções, workflow, tabela de clientes |

---

## Infraestrutura

- **Python:** `.venv/` com psycopg2-binary, requests, python-dotenv, flask, gunicorn, anthropic
- **DB:** Neon PostgreSQL (cloud) via `DATABASE_URL`
- **Schema:** 5 tabelas — `social_accounts`, `posts`, `metrics`, `execution_logs`, `whatsapp_conversations`
- **Clientes:** moacir (`MOACIR_`), espaco-laika (`LAIKA_`), namasa (`NAMASA_`), moper-maquinas (`MOPER_`)
- **GitHub:** repositório público — https://github.com/moacirpe/redes-sociais
- **Auto-accept:** `.claude/settings.local.json` → `defaultMode: bypassPermissions`
