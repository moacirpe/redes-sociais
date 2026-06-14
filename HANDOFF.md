# Handoff — Redes Sociais
_Atualizado em: 2026-06-06 (sessão 2)_

## Estado atual

- **Pipeline Instagram:** moacir, moper, laika → Neon PostgreSQL ✅ (cron diário 8h)
- **Banco ativo:** Neon (cloud PostgreSQL) — `DATABASE_URL` no Railway e no .env ✅
- **WhatsApp bot Moper:** REVERTIDO para **API oficial da Meta** (verificação da empresa aprovada em 13/06) — Claude Haiku, memória 30 dias, horário comercial. Código restaurado e validado (`/webhook/moper` GET+POST formato Meta). **Decisão:** usar NÚMERO NOVO dedicado à IA (não migrar o número atual da Moper, para preservar histórico no app). **Aguardando:** chip/número novo → cadastrar na Etapa 2 (Produção) do painel Meta → obter Phone Number ID, WABA ID e token permanente → preencher no .env/Railway + configurar webhook no painel Meta
- **WhatsApp bot Laika:** código pronto, Evolution API configurada — **aguardando escanear QR code** com celular (67) 99857-4771
- **Evolution API:** rodando em https://evo.huboperacional.com.br — instâncias `pai_espaco_laika` e `pai_moper_maquinas` criadas, status `connecting`
- **Catálogo Moper Paleteiras:** publicado no GitHub Pages ✅ → https://moacirpe.github.io/redes-sociais/paleteiras/
- **Meta Business Verification:** Melissa submeteu novo doc em 05/06 — aguardando resultado (até 48h)
- **Publicação automática de posts:** ✅ funcionando — `generateCaptions.py` + `publishScheduled.py` + Cloudinary. Testado com post real no moper em 06/06/2026.
- **Credenciais vazias:** TikTok (todos), YouTube (todos), Instagram namasa

---

## Próximos passos (por prioridade)

1. **Moper WhatsApp — cadastrar número novo na Meta (API oficial):**
   - Conseguir um chip/número NOVO (não ativo no WhatsApp) dedicado ao bot
   - Painel Meta → WhatsApp → Etapa 2 (Configuração da produção) → adicionar número → verificar via SMS/ligação
   - Me passar: **Phone Number ID**, **WABA ID** e **token permanente** (usuário do sistema)
   - Preencho `MOPER_WHATSAPP_PHONE_NUMBER_ID`, `MOPER_WHATSAPP_TOKEN`, `MOPER_WHATSAPP_VERIFY_TOKEN` no .env + Railway
   - Configuro o webhook no painel Meta apontando para `https://web-production-476d9.up.railway.app/webhook/moper` (verify token = `MOPER_WHATSAPP_VERIFY_TOKEN`)
   - ⚠️ Clientes precisam ser direcionados ao número NOVO (site/catálogo/Instagram) — o número antigo não chega no bot
2. **Laika WhatsApp — escanear QR code:**
   - Pegar celular (67) 99857-4771
   - WhatsApp → Menu → Aparelhos conectados → Conectar aparelho
   - Me chamar: "escanear QR code do Laika" → gero o QR na hora
   - Após scan: configuro webhook (`/webhook/laika`) no Evolution API + vars no Railway → bot ativo
3. **Railway — adicionar vars do Moper Evolution:** `EVOLUTION_API_KEY_MOPER`, `EVOLUTION_INSTANCIA_MOPER` (as da Laika já estão lá)
4. **Publicação Facebook** — adicionar suporte no `publishScheduled.py`. Credenciais já no .env (`FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_ACCESS_TOKEN`). Estimativa: 1-2h.
5. **Publicação TikTok** — requer aprovação de API no TikTok Developer Portal (processo burocrático, dias/semanas).
6. **Instagram Namasa:** preencher `NAMASA_INSTAGRAM_TOKEN` / `NAMASA_INSTAGRAM_ACCOUNT_ID`
7. **TikTok/YouTube:** sem credenciais — preencher quando disponíveis

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

## Infraestrutura Railway (WhatsApp Bots — Moper + Laika)

- **URL:** https://web-production-476d9.up.railway.app
- **Webhook Moper:** https://web-production-476d9.up.railway.app/webhook/moper
- **Webhook Laika:** https://web-production-476d9.up.railway.app/webhook/laika
- **Variáveis obrigatórias no Railway:**
  - Moper (Meta API): `MOPER_WHATSAPP_PHONE_NUMBER_ID`, `MOPER_WHATSAPP_TOKEN`, `MOPER_WHATSAPP_VERIFY_TOKEN`
  - Laika (Evolution): `EVOLUTION_API_URL`, `EVOLUTION_API_KEY_LAIKA`, `EVOLUTION_INSTANCIA_LAIKA`
  - `ANTHROPIC_API_KEY`, `DATABASE_URL`
- **Deploy:** automático via push no GitHub (branch main)
- **Procfile:** `gunicorn execution.whatsappWebhook:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
- **Nota:** Moper voltou para a Meta API oficial em 14/06/2026 (verificação aprovada). As vars `EVOLUTION_*_MOPER` e a instância `pai_moper_maquinas` não são mais usadas.

---

## Evolution API (WhatsApp Moper + Laika)

- **URL:** https://evo.huboperacional.com.br
- **Instância Laika:** `pai_espaco_laika` | Key: `B62C703C879E-425B-866F-FF29ACF7AEDF`
- **Instância Moper:** `pai_moper_maquinas` | Key: `6F0B0C0C89B0-4F30-85F4-7D9425C7ACF6`
- **Status:** ambas `connecting` — precisam escanear QR code
- **Webhooks a configurar após scan:**
  - Moper: `https://web-production-476d9.up.railway.app/webhook/moper`
  - Laika: `https://web-production-476d9.up.railway.app/webhook/laika`

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
| `EVOLUTION_API_URL` | ✅ https://evo.huboperacional.com.br |
| `EVOLUTION_API_KEY_MOPER` | ✅ |
| `EVOLUTION_INSTANCIA_MOPER` | ✅ pai_moper_maquinas |
| `EVOLUTION_API_KEY_LAIKA` | ✅ |
| `EVOLUTION_INSTANCIA_LAIKA` | ✅ pai_espaco_laika |
| `MOPER_WHATSAPP_PHONE_NUMBER_ID` / `_TOKEN` / `_VERIFY_TOKEN` (Meta) | ⏳ a preencher — número novo da IA |
| `EVOLUTION_*_MOPER` | ⚠️ obsoleto — Moper voltou para Meta API |
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
| moper | WhatsApp Bot | `[2-E]` | Cadastrar número novo na Meta (Etapa 2) → credenciais |
| moper | Catálogo paleteiras | `[5-T]` ✅ | — |
| laika | Instagram | `[5-T]` ✅ | — |
| laika | WhatsApp Bot | `[2-E]` | Escanear QR code |
| namasa | Instagram | `[1-S]` | Preencher token |
| Automação | Cron diário 8h | `[5-T]` ✅ | — |
| Automação | Publicação posts (IG+FB) | `[5-T]` ✅ | generateCaptions.py + publishScheduled.py |
| Automação | Auto-publish agendado | `[5-T]` ✅ | Testado com post real: https://www.instagram.com/reel/DZQKZajFTEE/ |

---

## Arquivos principais

| Arquivo | Propósito |
|---------|-----------|
| `HANDOFF.md` | Este arquivo |
| `docs/PLANO.md` | Lista detalhada de features |
| `CLAUDE.md` | Arquitetura, convenções, clientes |
| `execution/whatsappWebhook.py` | Flask — Moper (`/webhook/moper`, Meta API GET+POST) e Laika (`/webhook/laika`, Evolution) |
| `execution/whatsappResponder.py` | Bot Moper (Meta WhatsApp Business API) |
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
