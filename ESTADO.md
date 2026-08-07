# ESTADO — Redes Sociais
Status: 🔴 BOT MOPER FORA DO AR
Atualizado em: 07/ago/2026

## 🚨 BOT MOPER CAIU — APP SUMIU DA RAILWAY (diagnosticado 06/ago/2026)

**O Marechal informou "não está no ar". Diagnosticado com evidência, não por dedução.**

**Evidência 1 — o app não existe mais na Railway:**
```
GET https://web-production-476d9.up.railway.app/
HTTP/2 404 · x-railway-fallback: true
{"status":"error","code":404,"message":"Application not found"}
```
Mesma resposta em `/webhook/moper`. O header `x-railway-fallback: true` é resposta da
**plataforma**, não do Flask. App rodando e quebrado daria 502 "Application failed to respond"
ou erro do próprio app. Isto é a Railway dizendo que **nenhuma aplicação serve esse domínio**.
⇒ Cliente manda mensagem → Meta tenta entregar no webhook → recebe 404 → **a mensagem morre**.

**Evidência 2 — banco vivo e vazio:** Neon conecta normal; `whatsapp_conversations` existe com o
schema certo (`id, sender, role, content, transferred, created_at`) e tem **0 linhas**. A
retenção é 30 dias e o último commit é de 27/jul (10 dias), então o `purgeExpired` **não**
explica. ⚠️ **Não dá para distinguir daqui** entre "nada foi processado" e "os registros do teste
foram limpos com `resetConversation.py`" — **não chutar**. O que se pode afirmar: não existe
registro de nenhuma conversa de cliente.

**Evidência 3 — o código não mudou:** último commit `44ff075` (27/jul). **Caiu a hospedagem, não
o software.** Não há bug para caçar; há serviço para restaurar.

**❓ O QUE FALTA PARA FECHAR O DIAGNÓSTICO (precisa do Marechal):** abrir **railway.app** e ver
o que houve — projeto apagado? trial/plano expirado? pagamento recusado? serviço renomeado (o
domínio mudaria)? Sem o painel não dá para saber, e **daqui eu não tenho acesso**.

**⚠️ NÃO SE SABE DESDE QUANDO ESTÁ FORA.** O banco não dá timestamp (0 linhas). Só o painel da
Railway responde. **Impacto comercial a apurar:** onde o número do bot (**+55 11 92501-2098**)
está publicado? Os 31 leads do anúncio de 30/jul–4/ago entraram pelo link `wa.me` do **(47)
99232-5747** (humano), então **não dependiam do bot** — mas quem procurou o número do bot caiu no
vazio e ninguém soube.

**🎯 A LIÇÃO QUE JÁ ESTAVA ESCRITA AQUI.** O item "(Desejável) check de saúde pra avisar se o bot
cair — hoje o alarme é 'alguém reparar'" (linha da seção 1) **se cumpriu literalmente**: o bot
morreu e o alarme foi o Marechal comentar por acaso, dias depois. **O check de saúde sai de
"desejável" para pré-requisito.** Qualquer trabalho de melhoria do atendimento começa por saber
que ele está vivo — antes de qualidade de conversa, estoque sincronizado ou RESUMO na planilha.

## 🎯 TAREFAS ABERTAS (17/jul/2026)

### 1. Bot de WhatsApp Moper — 🚀 PRÉ-ATENDIMENTO REESCRITO E DEPLOYADO (27/jul)
Diagnóstico de 27/jul mostrou que o bot **não estava desligado — estava ligado com 4 buracos**.
Corrigidos e no ar (commit `3b98c69`, push pro `main` → Railway redeploya sozinho). Testado
localmente com **chamada real na API — 13 checagens, todas passando**.
- [x] **Transferência silenciosa CORRIGIDA (era o pior).** O bot prometia "em breve a equipe
      entrará em contato", marcava `transferred` no Postgres e **ninguém era avisado** —
      verificado no código: nenhum alerta/e-mail/notificação existia. Agora devolve um **link
      `wa.me` do consultor (47) 99232-5747 com o pedido do cliente já escrito**; ele aperta
      enviar e o lead chega qualificado num número com gente olhando. Sem credencial nova.
- [x] **Bot atende 24/7.** A trava `isBusinessHours()` cortava **antes** da IA — fora do horário
      só saía mensagem de "fechado", inclusive se o cliente respondesse contando o que precisava.
      Anúncio pago roda de madrugada. Agora qualifica sempre e avisa uma vez quando o humano volta.
- [x] **Pré-atendimento real:** pergunta **peso, altura e piso** (as 3 que decidem a máquina) +
      cidade, uma por vez, e encerra com `RESUMO:` estruturado. **Backstop determinístico:**
      `MAX_TURNOS_BOT = 6` — o código transfere mesmo se a IA enrolar.
- [x] **Drift de estoque corrigido.** O prompt anunciava **Empilhadeira 3T "EM ESTOQUE, ~10 dias"
      com estoque real ZERO** (promessa falsa na máquina de maior procura) e **Paleteira
      Elevatória 1T como "SOB ENCOMENDA" tendo 1 unidade em Itajaí**. Fonte anotada no prompt.
- [x] **Crédito Anthropic OK** — confirmado por chamada real em 27/jul (não por dedução).
- [x] **1º teste real feito pelo Marechal (27/jul): o bot respondeu e qualificou** ✅ — mas veio
      **repetindo perguntas**. Diagnóstico achou **2 bugs**, corrigidos e deployados (commit
      `b13928c`):
      - 🔴 **A MEMÓRIA NUNCA FUNCIONOU.** `_getConnection()` fazia `_conn.autocommit = False` em
        toda chamada; no psycopg2 isso chama `set_session`, proibido com transação aberta — e o
        `getHistory` faz SELECT sem fechar a transação. Erro real capturado: *"set_session cannot
        be used inside a transaction"*. Como o `addMessage` engolia a exceção, a falha era muda: a
        tabela `whatsapp_conversations` estava com **0 linhas desde sempre**. Cada mensagem era
        conversa nova → por isso repetia. **Efeito colateral:** `isTransferred` sempre `False`, ou
        seja, a transferência pra humano também nunca segurava.
      - **Mensagem do cliente entrava duplicada** no histórico enviado ao modelo (gravava e
        anexava de novo) — o modelo via o cliente repetindo a frase.
      - Verificado depois do fix: 3 mensagens gravadas e lidas, transferência persistindo, várias
        chamadas seguidas sem erro.
- [x] **Ferramenta nova: `execution/resetConversation.py`** — `--listar` mostra quem tem conversa e
      **quem está mudo por transferência**; passando o número, apaga o histórico e libera o bot.
      Necessário porque agora a memória funciona: depois de transferido, o bot fica mudo 30 dias
      com aquele número. ⚠️ Mexe no banco de **produção** (Neon), não há banco de teste.
- [ ] ⏳ **FALTA O ✅ FINAL: repetir o teste no WhatsApp** (+55 11 92501-2098) depois deste redeploy
      — agora ele deve **lembrar** do que já foi respondido e não repetir pergunta. Só aí é "pronto".
- [ ] 🔴 **`GOOGLE_REFRESH_TOKEN` MORTO** (`invalid_grant`, testado 27/jul) — por isso o lead
      **não entra sozinho na "Leads Moper"**; a Melissa ainda digita. Destravar rodando
      `authorizeGoogle.py` (fluxo OAuth no navegador). Depois disso dá pra o bot gravar a linha
      via `sheetsClient.appendRows` (o `GOOGLE_SHEET_ID_MOPER` aponta pra planilha antiga — vai
      precisar de uma var nova pra "Leads Moper" `1TVA80EJ…`).
- [ ] **Refinar (pendente):** bot enviar **foto + ficha técnica** das pastas de mídia (Melissa).
- [ ] (Desejável) **check de saúde** pra avisar se o bot cair — hoje o alarme é "alguém reparar".

### 2. 🔒 Segredos no Google Drive — decisão do Moacir pendente (17/jul)
🔴 **AGRAVADO (27/jul): o `.git/config` deste projeto guarda um TOKEN DO GITHUB em texto puro**
dentro da URL do remote (`https://ghp_***@github.com/moacirpe/redes-sociais.git`). Como o `.git`
mora no Drive, quem tem acesso à pasta tem **acesso de escrita ao repositório**. **Revogar** em
github.com/settings/tokens e reconfigurar o remote (usar `gh auth` ou credential helper do macOS,
não token na URL).

Os segredos vivos estão nesta pasta, que fica no **Drive**: `.env` (99 vars), `credentials/logins.env`,
`e-mail/Dados Importantes Moper.pdf`. O `.gitignore` protege do git, **mas não do Drive**.
- [ ] **Moacir responder:** essa pasta (ou a `Claude Code` inteira) está compartilhada com Julia/Melissa?
- [ ] Se **sim** → tirar os segredos do Drive (mover pra local fora do Drive; produção já vive no Railway).
- [ ] Se **não** → sem exposição; higiene opcional.
- _Feito em 17/jul: removidos 3 `.env.bak` antigos (segredo velho duplicado) → Lixo. `.env` de produção intacto._

## ✅ Moper WhatsApp — RESOLVIDO (26/jun): bot voltou a responder
- ✅ **RESOLVIDO 26/jun (fechado):** crédito Anthropic recarregado → bot respondendo. Verificado em dobro: (1) teste real no WhatsApp pela Melissa = respondeu normal; (2) re-diagnóstico técnico 26/jun 09:37 = Anthropic OK (sem erro de crédito), número CONNECTED/GREEN/VERIFIED, webhook HTTP 200. ✅ **RECARGA AUTOMÁTICA ATIVADA (26/jun)** na conta Anthropic "moacir's I…" → crédito não seca mais sozinho; bot não cai mais por falta de saldo. Sem pendências.
- ✅ Produção (Railway): **número REAL da Moper**, já testado e atendendo (confirmado pela Melissa). Token permanente; webhook OK (24/jun).
- 🔵 **HISTÓRICO — CAUSA (24/jun; RE-CONFIRMADA 25/jun — resolvida 26/jun).** Crédito da API Anthropic zerado. Bot cai no fallback *"temporariamente indisponível"* (confirmado por print de conversa real da Melissa: sáb 20/jun respondia normal; qua 24/jun já caía no fallback). Diagnóstico com evidência (não dedução):
  - Testei a `ANTHROPIC_API_KEY` do `.env` com o **mesmo modelo do bot** (claude-haiku-4-5) → a API retornou: **"Your credit balance is too low to access the Anthropic API."**
  - Banco **Neon testado = OK** (conectou e leu `whatsapp_conversations`). Token Meta válido. Logo: bot usa Anthropic p/ gerar resposta → sem crédito → exceção → fallback. Nada no número/código mudou; o crédito acabou com o uso. (É a mesma conta Anthropic com "crédito baixo".)
  - **Correção:** adicionar crédito na conta **Anthropic — Plans & Billing** (platform.claude.com/settings/billing). **Não precisa redeploy** — volta a responder assim que recarregar.
  - **Verificar pós-recarga:** rodar de novo o teste da chave (deve dar OK) + mandar msg de teste no horário comercial (Seg-Sex 8-18h, Sáb 8-13h). Conferir que a `ANTHROPIC_API_KEY` do Railway é a mesma do `.env`.
  - **⏳ DECISÃO PENDENTE (25/jun):** Melissa vai aguardar o **Moacir** e o **filho dele** decidirem se recarregam ou não. Conta Anthropic é **"moacir's I…"** (e-mail diferente do Claude chat) — saldo **−US$ 0,59**, cartão Visa ····6564 já cadastrado, recarga automática DESATIVADA. Recarregar em platform.claude.com → Plans & Billing. Custo é miúdo: ~US$ 0,0025/resposta (gasto até agora foi só de 2 pessoas testando). Recomendado ativar **recarga automática** + limite mensal. Tabela de conversas no Neon vem vazia (bot faz `purgeExpired`), então uso histórico só pelo Painel da Anthropic.
- ✅ `.env` LOCAL **sincronizado com produção em 25/jun** (era nº de teste; backup em `.env.bak-20260625`). Produção: Phone Number ID `1101382049734245`, WABA `1018454904096569`. Número real verificado direto na Meta (25/jun): **+55 11 92501-2098 — CONNECTED, quality GREEN, VERIFIED/APPROVED**; webhook app "MOPER MÁQUINAS - REDE DE FOTO" inscrito. **Não houve desconexão — o único problema é o crédito da Anthropic.**
- 🔜 Próximo nível (Melissa em andamento): bot enviar **foto + ficha técnica** a partir das pastas de mídia.

## Outras pendências
- Laika WhatsApp: escanear QR code com o celular (67) 99857-4771
- Publicação no Facebook (1-2h) e TikTok (depende de aprovação de API)
- Credenciais pendentes: Instagram Namasa, TikTok, YouTube

## Próximos passos
- ✅ WhatsApp Moper: concluído (token permanente sincronizado Railway + `.env`, 22/jun).
- **Laika WhatsApp (BLOQUEADO):** instância `pai_espaco_laika` retorna 404 (não existe); chave por-instância dá 401 em fetchInstances. Precisa **recriar a instância** — exige a **chave global do Evolution** (`AUTHENTICATION_API_KEY`).
  - **Diagnóstico 24/jun (confirmado):** essa chave NÃO está em arquivo nenhum — o `infra/evolution-api.yml` usa `${EVOLUTION_API_KEY}`, então ela vive no **ambiente do container Evolution (Portainer/VPS)**.
  - **Pra destravar:** pegar a `EVOLUTION_API_KEY` no **Portainer** (container Evolution → Environment variables) → com ela: recriar instância `pai_espaco_laika` → gerar QR → escanear com **(67) 99857-4771** → configurar webhook `/webhook/laika`.

> Já funcionando: pipeline Instagram → Neon PostgreSQL (cron 8h), publicação automática de posts (Cloudinary), catálogo de paleteiras no GitHub Pages.
> Fonte detalhada: `REDES SOCIAIS/HANDOFF.md`.
