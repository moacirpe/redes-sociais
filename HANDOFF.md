# Handoff — Redes Sociais
_Atualizado em: 2026-06-06_

## Estado atual

- **Pipeline Instagram:** moacir, moper, laika → Neon PostgreSQL ✅ (cron diário 8h)
- **Banco ativo:** Neon (cloud PostgreSQL) — `DATABASE_URL` no Railway e no .env ✅
- **WhatsApp bot Moper:** Railway.app — Claude Haiku, memória 30 dias, horário comercial ✅ (número de teste — aguardando verificação Meta para trocar pelo real 47 99232-5747)
- **WhatsApp bot Laika:** código pronto, Evolution API configurada — **aguardando escanear QR code** com celular (67) 99857-4771
- **Evolution API:** rodando em https://evo.huboperacional.com.br — instância `pai_espaco_laika` criada, status `connecting`
- **Catálogo Moper Paleteiras:** publicado no GitHub Pages ✅ → https://moacirpe.github.io/redes-sociais/paleteiras/
- **Meta Business Verification:** Melissa submeteu novo doc em 05/06 — aguardando resultado (até 48h)
- **Publicação automática de posts:** próxima frente a implementar (Instagram + Facebook)
- **Credenciais vazias:** TikTok (todos), YouTube (todos), Instagram namasa

---

## Próximos passos (por prioridade)

1. ⏳ **Verificação Meta:** aguardar resultado. Se aprovada → trocar `MOPER_WHATSAPP_PHONE_NUMBER_ID` no Railway pelo número real (47 99232-5747)
2. **Laika WhatsApp — escanear QR code:**
   - Pegar celular (67) 99857-4771
   - WhatsApp → Menu → Aparelhos conectados → Conectar aparelho
   - Me chamar: "escanear QR code do Laika" → gero o QR na hora
   - Após scan: configuro webhook no Evolution API + vars no Railway → bot ativo
3. **Publicação automática:** implementar postagem no Instagram e Facebook via API (próxima sessão — ver seção abaixo)
4. **Token WhatsApp Moper:** renovar em ~60 dias via `./renovarToken.sh`
5. **Instagram Namasa:** preencher `NAMASA_INSTAGRAM_TOKEN` / `NAMASA_INSTAGRAM_ACCOUNT_ID`
6. **TikTok/YouTube:** sem credenciais — preencher quando disponíveis

---

## Publicação automática — o que vem a seguir

A próxima grande frente é publicar posts no Instagram e Facebook das empresas diretamente via API.

**O que precisaremos:**
- Script `execution/publishPost.py` que recebe imagem + legenda + cliente e publica
- Agendamento via cron ou execução manual por comando
- Suporte a: imagem única, carrossel, stories (futuramente)
- Clientes: moacir, moper-maquinas, espaco-laika, namasa

**Tokens necessários (já temos para 3 dos 4 clientes):**
- moacir ✅, moper ✅, laika ✅, namasa ❌

---

## Infraestrutura Railway (WhatsApp Bot Moper)

- **URL:** https://web-production-476d9.up.railway.app
- **Webhook Laika:** https://web-production-476d9.up.railway.app/webhook/laika
- **Variáveis obrigatórias no Railway:**
  - `MOPER_WHATSAPP_PHONE_NUMBER_ID`, `MOPER_WHATSAPP_TOKEN`, `MOPER_WHATSAPP_VERIFY_TOKEN`
  - `EVOLUTION_API_URL`, `EVOLUTION_API_KEY_LAIKA`, `EVOLUTION_INSTANCIA_LAIKA`
  - `ANTHROPIC_API_KEY`, `DATABASE_URL`
- **Deploy:** automático via push no GitHub (branch main)
- **Procfile:** `gunicorn execution.whatsappWebhook:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`

---

## Evolution API (WhatsApp Laika)

- **URL:** https://evo.huboperacional.com.br
- **Instância Laika:** `pai_espaco_laika` | Key: `B62C703C879E-425B-866F-FF29ACF7AEDF`
- **Instância Moper:** `pai_moper_maquinas` | Key: `6F0B0C0C89B0-4F30-85F4-7D9425C7ACF6`
- **Status Laika:** `connecting` — precisa escanear QR code
- **Webhook a configurar após scan:** `https://web-production-476d9.up.railway.app/webhook/laika`

---

## Catálogo de Paleteiras

- **URL pública:** https://moacirpe.github.io/redes-sociais/paleteiras/
- **Fonte:** `docs/paleteiras/index.html` + `docs/paleteiras/img/`
- **Para atualizar:** editar o HTML e fazer push — GitHub Pages atualiza automaticamente

---

## Histórico Meta Business Verification

| Data | Evento |
|------|--------|
| ~01/06 | Primeiro envio |
| 03/06 | Rejeição #1 — documento de identidade |
| 04/06 | Melissa resubmitiu com RG |
| 05/06 | Rejeição #2. Nova submissão com documento diferente |
| 05/06+ | Aguardando (até 48h) |

**Atenção:** nome da empresa no Meta ("Moper Materiais de Construção LTDA") pode não bater com CNPJ ("ROMOA MATERIAIS PARA CONSTRUCAO LTDA") — possível causa de rejeição futura.

---

## Credenciais — status no .env

| Variável | Status |
|----------|--------|
| `DATABASE_URL` (Neon) | ✅ |
| `META_APP_ID` / `META_APP_SECRET` | ✅ |
| `INSTAGRAM_TOKEN` / `INSTAGRAM_BUSINESS_ACCOUNT_ID` (moacir) | ✅ |
| `MOPER_INSTAGRAM_TOKEN` / `MOPER_INSTAGRAM_ACCOUNT_ID` | ✅ |
| `LAIKA_INSTAGRAM_TOKEN` / `LAIKA_INSTAGRAM_ACCOUNT_ID` | ✅ |
| `MOPER_WHATSAPP_PHONE_NUMBER_ID` | ✅ (teste — trocar após verificação Meta) |
| `MOPER_WHATSAPP_TOKEN` | ✅ (renovar em ~60 dias) |
| `EVOLUTION_API_URL` | ✅ https://evo.huboperacional.com.br |
| `EVOLUTION_API_KEY_LAIKA` | ✅ |
| `EVOLUTION_INSTANCIA_LAIKA` | ✅ pai_espaco_laika |
| `NAMASA_INSTAGRAM_*` | ❌ vazio |
| `MOACIR_TIKTOK_*` | ❌ vazio |
| `MOACIR_YOUTUBE_*` | ❌ vazio |

---

## Status de Features

> Tags: `[0]` planejado · `[1-S]` diretiva/schema · `[2-E]` script · `[3-H]` creds prontas · `[4-C]` testado com dado real · `[5-T]` ✅ pipeline completo

| Cliente | Feature | Status | Próxima etapa |
|---------|---------|--------|---------------|
| Infra | Neon PostgreSQL | `[5-T]` ✅ | — |
| moacir | Instagram | `[5-T]` ✅ | — |
| moacir | TikTok | `[1-S]` | Preencher credenciais |
| moacir | YouTube | `[1-S]` | Preencher credenciais |
| moacir | Relatório mensal | `[5-T]` ✅ | — |
| moper | Instagram | `[5-T]` ✅ | — |
| moper | WhatsApp Bot | `[4-C]` | Aguardar verificação Meta |
| moper | Catálogo paleteiras | `[5-T]` ✅ | — |
| laika | Instagram | `[5-T]` ✅ | — |
| laika | WhatsApp Bot | `[2-E]` | Escanear QR code |
| namasa | Instagram | `[1-S]` | Preencher token |
| Automação | Cron diário 8h | `[5-T]` ✅ | — |
| Automação | Publicação posts (IG+FB) | `[0]` | Próxima sessão |
| Automação | Auto-publish agendado | `[1-S]` | Spec em `docs/superpowers/specs/` |

---

## Arquivos principais

| Arquivo | Propósito |
|---------|-----------|
| `HANDOFF.md` | Este arquivo |
| `docs/PLANO.md` | Lista detalhada de features |
| `CLAUDE.md` | Arquitetura, convenções, clientes |
| `execution/whatsappWebhook.py` | Flask — rotas Moper (`/webhook`) e Laika (`/webhook/laika`) |
| `execution/whatsappResponder.py` | Bot Moper (Meta API) |
| `execution/whatsappResponderLaika.py` | Bot Laika (Evolution API) |
| `execution/collectAll.sh` | Cron — coleta todos os clientes |
| `infra/evolution-api.yml` | Docker Stack Evolution API (referência) |

---

## Infraestrutura

- **Python:** `.venv/` com psycopg2-binary, requests, python-dotenv, flask, gunicorn, anthropic
- **DB:** Neon PostgreSQL (cloud) via `DATABASE_URL`
- **Schema:** 5 tabelas — `social_accounts`, `posts`, `metrics`, `execution_logs`, `whatsapp_conversations`
- **GitHub:** público — https://github.com/moacirpe/redes-sociais
- **Auto-accept:** `.claude/settings.local.json` → `defaultMode: bypassPermissions`
