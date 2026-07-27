# Handoff — Redes Sociais
_Atualizado em: 2026-07-27 (sessão 4)_

## O que foi feito nesta sessão (27/07) — bot Moper virou PRÉ-ATENDIMENTO

Pedido do Moacir: "ativar a IA do pré-atendimento". O diagnóstico mostrou que **o bot não estava
desligado — estava ligado com buracos**, alguns invisíveis porque falhavam em silêncio.
Dois deploys: `3b98c69` (pré-atendimento) e `b13928c` (memória).

**Corrigido e no ar:**
1. **Transferência silenciosa (o pior).** O bot dizia "em breve a equipe entrará em contato",
   marcava `transferred` e **ninguém era avisado** — confirmado no código: não existia alerta,
   e-mail nem notificação. Agora devolve um **link `wa.me` do consultor (47) 99232-5747 com o
   pedido do cliente já escrito** (`buildHandoffMessage`). O cliente aperta enviar e o lead chega
   qualificado num número com gente olhando. Não depende de credencial nova.
2. **Bot atende 24/7.** `isBusinessHours()` cortava **antes** da IA; fora do horário só saía
   mensagem de "fechado", mesmo se o cliente respondesse contando o que precisava. Anúncio pago
   roda de madrugada. Agora qualifica sempre e avisa uma vez quando o humano retorna
   (`FORA_HORARIO_PROMPT`).
3. **Pré-atendimento real:** pergunta **peso, altura, piso** (as 3 que decidem a máquina) +
   cidade, uma por vez, e encerra com `[TRANSFERIR]` + `RESUMO:` estruturado. Backstop
   determinístico `MAX_TURNOS_BOT = 6` — o código transfere mesmo se a IA enrolar.
   `stripMarkers()` faz a recomendação de máquina chegar junto com o link.
4. **Drift de estoque.** O prompt anunciava **Empilhadeira 3T "EM ESTOQUE, ~10 dias" com estoque
   real ZERO** (promessa falsa na máquina de maior procura) e **Paleteira Elevatória 1T como
   "SOB ENCOMENDA" tendo 1 unidade em Itajaí**. Corrigido, com a fonte
   (`MOPER - Equipe/Estoque/estoque-moper.md`) anotada dentro do prompt.
5. 🔴 **A MEMÓRIA DE CONVERSA NUNCA FUNCIONOU** — achado no 1º teste real do Moacir, que relatou
   o bot repetindo perguntas. `_getConnection()` executava `_conn.autocommit = False` a **cada
   chamada**; no psycopg2 isso invoca `set_session`, proibido com transação aberta — e
   `getHistory()` faz SELECT sem fechar a transação. Erro real capturado:
   *"set_session cannot be used inside a transaction"*. Como `addMessage()` engolia a exceção,
   a falha era muda: `whatsapp_conversations` estava com **0 linhas desde sempre**, o bot rodava
   **sem memória** (cada mensagem = conversa nova) e `isTransferred()` sempre voltava `False`
   (a transferência também nunca segurava). Corrigido: autocommit só na criação, rollback de
   transação pendente e checagem de conexão viva (Neon derruba ociosa).
6. **Mensagem do cliente entrava duplicada** no histórico enviado ao modelo — `addMessage()` já
   gravava e `generateReply()` anexava de novo. O modelo via o cliente repetindo a frase.
7. **Novo:** `execution/resetConversation.py` — `--listar` mostra conversas e quem está mudo por
   transferência; passando o número, apaga o histórico e libera o bot. ⚠️ Mexe no banco de
   **produção** (não há banco de teste).

**Verificações feitas com evidência (não por dedução):** 13 checagens automatizadas incluindo
chamada real na API Anthropic (crédito **OK**); round-trip de memória gravando/lendo 3 mensagens;
`ANTHROPIC_API_KEY` respondendo; teste real no WhatsApp pelo Moacir (bot respondeu e qualificou).

**Achados que NÃO foram corrigidos (ver Próximos passos):** `GOOGLE_REFRESH_TOKEN` morto
(`invalid_grant`) e **token do GitHub em texto puro no `.git/config`**, dentro do Google Drive.

## Estado atual

- **Pipeline Instagram:** moacir, moper, laika → Neon PostgreSQL ✅ (cron diário 8h)
- **Banco ativo:** Neon (cloud PostgreSQL) — `DATABASE_URL` no Railway e no .env ✅
- **WhatsApp bot Moper:** ✅ **FUNCIONANDO como pré-atendimento** (Meta API, Claude Haiku,
  `/webhook/moper`). Token permanente (System User) no Railway e no `.env`, verificado 22/06.
  Número do bot: **+55 11 92501-2098** — ⚠️ **não é** o número dos leads, que é o
  **(47) 99232-5747** (humano, para onde o bot manda o cliente).
  ⏳ **Falta repetir o teste real** depois do deploy `b13928c` para confirmar que agora ele
  **lembra** do que já foi respondido.
- **Memória de conversa:** ✅ corrigida em 27/07 — 30 dias de retenção, `MAX_MESSAGES = 20`.
- **WhatsApp bot Laika:** código pronto, Evolution API configurada — **aguardando escanear QR code** com celular (67) 99857-4771
- **Evolution API:** rodando em https://evo.huboperacional.com.br — instâncias `pai_espaco_laika` e `pai_moper_maquinas` criadas, status `connecting`
- **Catálogo Moper Paleteiras:** publicado no GitHub Pages ✅ → https://moacirpe.github.io/redes-sociais/paleteiras/
- **Meta Business Verification:** ✅ **APROVADA** (~13/06) — foi o que liberou a Meta API oficial do WhatsApp Moper
- **Publicação automática de posts:** ✅ funcionando — `generateCaptions.py` + `publishScheduled.py` + Cloudinary. Testado com post real no moper em 06/06/2026.
- **Credenciais vazias:** TikTok (todos), YouTube (todos), Instagram namasa

---

## Próximos passos (por prioridade)

1. **🧪 REPETIR O TESTE REAL DO BOT** (+55 11 92501-2098), depois do deploy `b13928c`. Mandar em
   mensagens separadas: "preciso de uma empilhadeira" → "2 toneladas" → "3 metros" → "galpão de
   piso liso, sou de Itajaí". **Sinal de sucesso:** ele avança nas perguntas em vez de repetir, e
   termina recomendando a máquina + link do (47). Se não responder, é a transferência do teste
   anterior segurando → rodar `resetConversation.py "+55 11 92501-2098"`. **Só depois disso o bot
   vira ✅ "pronto".**
2. **🔴 SEGURANÇA — token do GitHub em texto puro.** O `.git/config` guarda o PAT dentro da URL do
   remote (`https://ghp_***@github.com/moacirpe/redes-sociais.git`) e o `.git` mora **dentro do
   Google Drive** — quem acessa a pasta tem escrita no repo. **Revogar** em
   github.com/settings/tokens e reconfigurar o remote (credential helper do macOS ou `gh auth`,
   nunca token na URL). Ver também a pendência "Segredos no Drive" no `ESTADO.md`.
3. **🔴 `GOOGLE_REFRESH_TOKEN` MORTO** (`invalid_grant`, testado 27/07) — o `sheetsClient` não
   escreve, então **o lead qualificado pelo bot não entra sozinho na planilha "Leads Moper"**
   (a Melissa ainda digita à mão). Destravar rodando `authorizeGoogle.py` (OAuth no navegador).
   Depois: criar var nova apontando para a planilha **"Leads Moper"** (`1TVA80EJXwOBsh0Omqnd
   EX6uwxE3-6oJBhuzBD2syL74`, dona = comercial@mopermaquinas.com.br) — o `GOOGLE_SHEET_ID_MOPER`
   atual aponta para a planilha antiga de fila de posts.
4. **Bot enviar foto + ficha técnica** das pastas de mídia (o "próximo nível" iniciado pela
   Melissa, ainda pendente).
5. **Check de saúde do bot** — hoje o alarme é "alguém reparar"; ele já caiu por crédito (24/jun)
   e rodou meses sem memória sem ninguém notar. Um ping diário que testa Anthropic + banco +
   webhook evitaria os dois casos.
6. **Laika WhatsApp — escanear QR code:**
   - Pegar celular (67) 99857-4771
   - WhatsApp → Menu → Aparelhos conectados → Conectar aparelho
   - Me chamar: "escanear QR code do Laika" → gero o QR na hora
   - Após scan: configuro webhook (`/webhook/laika`) no Evolution API + vars no Railway → bot ativo
3. ~~Railway — vars do Moper Evolution~~ — **obsoleto:** Moper usa Meta API; as vars/instância Evolution do Moper não são mais usadas.
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
| `MOPER_WHATSAPP_PHONE_NUMBER_ID` / `_BUSINESS_ACCOUNT_ID` / `_VERIFY_TOKEN` (Meta) | ✅ preenchidas |
| `MOPER_WHATSAPP_TOKEN` (Meta) | ✅ token permanente (System User) no Railway e no .env — verificado 22/06 |
| `EVOLUTION_*_MOPER` | ⚠️ obsoleto — Moper voltou para Meta API |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | ✅ preenchidas |
| `GOOGLE_REFRESH_TOKEN` | ❌ **MORTO** — `invalid_grant` (testado 27/07). Rodar `authorizeGoogle.py` |
| `GOOGLE_SHEET_ID_MOPER` | ⚠️ aponta pra planilha antiga de posts, não pra "Leads Moper" |
| `ALERT_EMAIL_FROM` / `ALERT_EMAIL_TO` / `ALERT_EMAIL_PASSWORD` | ❌ **não existem** no `.env` — o `alertSystem.py` nunca teve canal de e-mail configurado |
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
| moper | WhatsApp Bot (pré-atendimento) | `[4-C]` | Repetir teste real pós-`b13928c` → vira `[5-T]` |
| moper | Bot grava lead na planilha | `[2-E]` | ❌ bloqueado: `GOOGLE_REFRESH_TOKEN` morto → `authorizeGoogle.py` |
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
