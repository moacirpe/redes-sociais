# Handoff — Redes Sociais
_Atualizado em: 2026-08-10 (sessão 6)_

## ✅ SESSÃO 6 (10/ago) — BOT MOPER DE VOLTA AO AR + 2 DEFEITOS DE PRODUÇÃO CORRIGIDOS

Sessão conduzida com a **Melissa** (não o Moacir). Diagnóstico fechado com o CLI da Railway,
usando um `RAILWAY_API_TOKEN` de conta criado por ela.

**Causa raiz do apagão (definitiva, com a mensagem literal da plataforma):**
> `Your trial has expired. Please select a plan to continue using Railway.`

O trial da Railway venceu e a plataforma **removeu os deploys**. Nada foi apagado por engano.
Projeto `fearless-possibility` → serviço `web` → `web-production-476d9.up.railway.app` estava lá,
com todos os deploys em `REMOVED` e `canRedeploy: true`. Existe também um projeto **duplicado
`keen-vitality`** (mesmo repo, URL `...ce7131`, também derrubado) — vale apagar depois.

**Janela do apagão:** funcionou em 27/jul (teste do Moacir) → 404 em 06/ago. O bot ficou mudo
por ~2 semanas e **toda mensagem de cliente nesse período se perdeu** (não respondida, não
registrada).

**Resolvido:** plano pago assinado (Melissa) → `railway redeploy` → serviço `● Online`.

### 🔴 Dois defeitos que o "está no ar" escondia (achados no log, não no navegador)

1. **`DATABASE_URL` NUNCA EXISTIU NO RAILWAY.** O log de runtime mostrava
   `Erro ao conectar ao banco: connection to server on socket "/var/run/postgresql/..."`
   — ou seja, caía no socket local porque a variável não estava setada. **Consequência: a
   correção de memória de 27/jul (`b13928c`) jamais teve efeito em produção.** O bot rodou esse
   tempo todo sem banco → sem memória, repetindo perguntas, e `isTransferred()` sempre `False`.
   Isto também **explica de vez** o mistério da sessão 5 (`whatsapp_conversations` com 0 linhas):
   não era purga nem reset — **nunca houve gravação**.
   ⚠️ O HANDOFF anterior afirmava "`DATABASE_URL` no Railway ✅". **Era falso.** Lição: conferir
   variável no ambiente que roda, não no `.env` local.
   **Corrigido:** variável setada no serviço. Log agora mostra `Tabela whatsapp_conversations pronta`.

2. **Rodava no servidor de desenvolvimento do Flask, não no gunicorn.** O log trazia
   `WARNING: This is a development server`. O serviço tinha um **start command customizado**
   (`PYTHONPATH=. python execution/whatsappWebhook.py`) que **sobrepunha o `Procfile`**.
   Servidor de desenvolvimento = processo único: uma chamada lenta à API da Anthropic segura as
   outras mensagens, a Meta estoura timeout e reenvia (risco de resposta duplicada).
   **Corrigido:** start command trocado para
   `PYTHONPATH=. gunicorn execution.whatsappWebhook:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`.

### Verificações com evidência (10/ago)

| Check | Resultado |
|-------|-----------|
| App local (antes de mexer) | importa, conecta no Neon, `GET /` 200 → **provou que o código estava são; morreu a hospedagem** |
| `GET /` em produção | `200 {"laika":true,"moper":true}` |
| Verificação do webhook (como a Meta faz) | `200` devolvendo o challenge |
| Webhook com token errado | `403` (rejeita corretamente) |
| Token WhatsApp na Graph API | válido — `+55 11 92501-2098`, "Moper Máquinas IA", `quality_rating: GREEN` |
| Inscrição do app no webhook da WABA | **ativa** — a Meta não desinscreveu durante o apagão |
| Banco em produção | `Tabela whatsapp_conversations pronta` (sem erro) |

### ✅ TESTE REAL FEITO PELA MELISSA (10/ago) — bot vira `[5-T]`

Conversa completa lida no banco (`whatsapp_conversations`, **10 mensagens** — o contador que foi
**0 a vida inteira**). Prova de que a memória grava e é usada:

```
[user]      Boa tarde
[assistant] Boa tarde! ... Como posso ajudar?
[user]      Preciso empilhadeira elétrica 3 toneladas
[assistant] Empilhadeira Elétrica Moper® 3T ... a que altura vai elevar?
[user]      4,70 de altura
[assistant] 4,70 m atende ... o piso é galpão (liso), pátio ou outro?
[user]      Piso liso
[assistant] Piso liso é ideal ... de qual cidade/estado você está?
[user]      Itajaí
[system]    TRANSFERIDO_PARA_HUMANO
```

**Avançou nas 4 perguntas sem repetir nenhuma** e transferiu ao final. Também **acertou o
estoque**: anunciou a 3T como *"sob encomenda, ~90 dias"* (correto — estoque zero), sem repetir
a promessa falsa de "em estoque" que existia antes de 27/jul.

### 🔒 Segurança — token do GitHub ✅ RESOLVIDO (10/ago)

Pendência aberta desde 27/jul, fechada com evidência:

1. PAT saiu do `.git/config` (texto puro dentro do Google Drive) → **Keychain do macOS**.
   Remote agora é `https://github.com/moacirpe/redes-sociais.git`, sem token na URL.
2. **Token antigo revogado** pelo Moacir. Confirmado: `GET /user` com ele → **HTTP 401**.
3. **Token novo com privilégio mínimo:** scope **`public_repo`** (era `repo` — controle total de
   repositórios *privados*, sem data de expiração). Agora expira em **08/nov/2026**.
4. **Push real validado:** `cb9812e..2452a14`. Isto fecha a ressalva de que `git ls-remote` num
   repo público não provava escrita.

⚠️ **Renovar até 08/nov/2026** — quando vencer, `git push` passa a falhar com erro de
autenticação. Gerar outro em github.com/settings/tokens (classic, só `public_repo`) e regravar:
`git credential-osxkeychain erase` seguido de `store`.

ℹ️ Existe outro PAT na conta, **`Caixio Claude Code`** (projeto diferente), que **expirou em
06/ago/2026**. Não é risco, mas o Caixio vai precisar de um novo quando for mexido.

---

## 🚨 SESSÃO 5 (06/ago) — BOT MOPER ESTÁ FORA DO AR _(resolvido na sessão 6 — ver acima)_

O Marechal informou "não está no ar" enquanto conversávamos sobre melhorar o atendimento.
Diagnóstico feito com evidência, seguindo `superpowers:systematic-debugging` (Fase 1).

**Causa raiz alcançada: a aplicação não existe mais na Railway.**
- `GET https://web-production-476d9.up.railway.app/` → **HTTP 404** com header
  **`x-railway-fallback: true`** e corpo `{"message":"Application not found"}`. Idem em
  `/webhook/moper`. Isso é resposta de **plataforma**, não do Flask — app rodando e quebrado
  daria 502/erro do app. Nenhuma aplicação está servindo o domínio.
- **Consequência:** a Meta tenta entregar a mensagem do cliente no webhook, leva 404, e a
  mensagem morre. Não é bot lento nem prompt ruim — não há endpoint.

**O que foi verificado e está SÃO (para não caçar no lugar errado):**
- **Neon PostgreSQL:** conecta normalmente. Tabelas: `execution_logs, metrics, posts,
  social_accounts, whatsapp_conversations`.
- **Código:** último commit `44ff075` (27/jul). Nada mudou. **Caiu a hospedagem, não o software.**
- **`.env` local:** 99 chaves parseadas; `DATABASE_URL`, `ANTHROPIC_API_KEY`,
  `MOPER_WHATSAPP_TOKEN` e `MOPER_WHATSAPP_PHONE_NUMBER_ID` presentes e não vazios.

**Achado que NÃO foi possível concluir (registrar como aberto, não como fato):**
`whatsapp_conversations` está com **0 linhas**. A retenção é 30 dias e o último commit tem 10
dias, então `purgeExpired()` não explica. Mas **não dá para distinguir** entre (a) nada foi
processado desde 27/jul e (b) os registros do teste foram apagados com `resetConversation.py`.
**Não converter isso em "a memória nunca funcionou" sem evidência nova.**

**Bloqueio para fechar o diagnóstico:** só o painel da **railway.app** responde por que o app
sumiu — projeto apagado, trial/plano expirado, pagamento recusado ou serviço renomeado. Precisa
do Marechal. **Também não se sabe desde quando está fora** (o banco não dá timestamp).

**Decorrência de projeto:** o item que estava como "(Desejável) check de saúde pra avisar se o
bot cair" **deixou de ser desejável**. O bot morreu e o alarme foi alguém comentar por acaso.
Antes de mexer em qualidade de conversa, sincronizar estoque ou gravar RESUMO na planilha, o
atendimento precisa de **prova de vida automática**.

**🔴 SEGURANÇA — o token do GitHub em texto puro no `.git/config` foi exposto no terminal**
durante esta sessão (rodei `git remote -v` sem lembrar do aviso que já estava no ESTADO).
**Revogar em github.com/settings/tokens** e reconfigurar o remote sem token na URL (usar
`gh auth login` ou o credential helper do macOS). Isto já era pendência desde 27/jul.


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

### ⚠️ BOT EM MODO MANUTENÇÃO (ligado 10/ago ~17h, desligar em 11/ago)

Decisão do Moacir: editar o prompt sem atender cliente com versão pela metade. Ele pediu
"tirar do ar"; ofereci a alternativa e ele escolheu **modo manutenção** — melhor mandar o
cliente para uma pessoa do que deixá-lo no silêncio.

- **Chave:** `MOPER_MODO_MANUTENCAO=1` no Railway. Lida **a cada mensagem** (não no import),
  então liga/desliga sem tocar em código: `railway variables --set "MOPER_MODO_MANUTENCAO=0"`.
- **Comportamento:** responde mensagem curta + link `wa.me` do consultor. **Não chama a IA**
  (sem custo), **não grava histórico** e **não marca `transferred`** — ao desligar, o cliente
  volta a ser atendido do zero.
- **Código:** `modoManutencao()` / `buildManutencaoMessage()` em `whatsappResponder.py`,
  checado no passo 2 de `handleIncomingMessage` (depois do check de transferido). Commit `6429e84`.

### 🔴 Três defeitos achados na conversa real de 10/ago (não corrigidos)

O Moacir colou o transcript do teste. Achados olhando a conversa, não o código:

1. **O link do consultor está sendo escondido — é o que custa dinheiro.** A mensagem final
   junta recomendação + specs + prazo + pagamento + link, fica longa, e o WhatsApp corta com
   **"Ler mais"** — com o link **dentro da parte oculta**. O cliente que não expandir nunca vê
   o passo que fecha o lead. Origem: `whatsappResponder.py:354`
   (`texto = f"{recomendacao}\n\n{handoff}"`). **Correção acordada:** mandar o link em
   mensagem separada e curta, logo depois da recomendação.
2. **Mensagem duplicada.** Às 15:04:11 a mesma resposta saiu duas vezes. Hipótese mais
   provável: a Meta reentrega o webhook e **o bot não guarda quais message ids já processou**.
   ⚠️ **Não confirmado no código — não converter em fato sem evidência.**
3. **Tique do "Perfeito!".** Três "Perfeito!" seguidos e dois encerramentos emendados
   ("Excelente! Temos tudo que precisamos" + "Perfeito! Quem fecha negócio..."). Soa robô.

### ⏳ Reescrita do prompt — persona "Elô" (acordada, parcialmente redigida)

O Moacir batizou a IA de **Elô** e quer um **menu de abertura** (auto atendimento): o cliente
escolhe entre receber informações ou falar com um humano.

**Estrutura de 8 blocos acordada** (hoje o prompt é um bloco só de ~100 linhas em
`whatsappResponder.py:60`, difícil de editar sem bagunçar o resto):

| # | Bloco | Controla |
|---|-------|----------|
| 1 | Quem é a Elô | nome, identidade, que é automática |
| 2 | **Abertura** ✅ redigido | primeira mensagem + menu |
| 3 | Como ela conversa | tom, tamanho, ritmo |
| 4 | O que vendemos | portfólio + estoque — **isolar é o ponto**: é o que a Melissa atualiza, e foi o embolado atual que causou a promessa falsa de estoque em julho |
| 5 | Prazos e pagamento | 10 × 90 dias, entrada, parcelas |
| 6 | Qualificação | peso, altura, piso, cidade |
| 7 | Fechamento e transferência | inclui a correção do link separado |
| 8 | Limites | nunca inventa preço nem prazo |

**Bloco 2 (ABERTURA), texto aprovado:**

```
Oi! Aqui é a Elô, o atendimento virtual da Moper Máquinas 👋

Posso te ajudar de duas formas:

📋 *Informações sobre nossas máquinas* — empilhadeiras, paleteiras e carretas
👤 *Falar com um consultor* — te passo direto para a equipe

Se preferir, nosso site é mopermaquinas.com.br

*Como posso ajudar?*
```

Regras acordadas junto: apresentar-se **uma única vez**; **pular o menu** se o cliente já
chegar dizendo o que precisa; se escolher consultor, **uma pergunta só** antes de transferir;
assumir que é automática e **nunca fingir bastidor** ("vou consultar o estoque").

⚠️ **Trade-off que o Moacir aceitou de olhos abertos:** oferecer "falar com humano" na primeira
mensagem faz mais gente escolher isso, e o consultor passa a receber lead **cru**. A pergunta
única antes de transferir é o meio-termo.

### ⏳ Vigia de saúde — design aprovado, nada implementado

Quatro decisões fechadas com o Moacir (nesta ordem):

1. **Onde roda:** GitHub Actions — **fora da Railway de propósito**. Um vigia dentro da coisa
   que ele vigia teria morrido junto com o bot em julho.
2. **Como avisa:** template próprio na Meta (categoria UTILITY, com variável para o motivo).
   Ainda **não criado**. O único template aprovado hoje é o `hello_world` (texto fixo, sem
   variável). A Meta leva de minutos a ~24h para aprovar.
3. **O que testa:** site + banco + IA (os três motivos que já derrubaram o bot; um "o site
   responde?" teria pego só um deles).
4. **Ritmo:** de hora em hora, avisa **só na mudança de estado** (caiu / voltou), mais um
   heartbeat às segundas de manhã — silêncio não pode ser ambíguo.

**Arquitetura escolhida (e o porquê):** um endpoint `/health` **dentro do bot**, protegido por
token próprio e com resposta cacheada alguns minutos (senão qualquer um na internet gasta
crédito da Anthropic apertando). O vigia externo só lê o veredito. Assim **`DATABASE_URL` e
`ANTHROPIC_API_KEY` nunca saem da Railway** — o GitHub só guarda a chave de mandar WhatsApp.

**Estado guardado** num arquivo em branch separada do próprio repo (vira histórico de quedas
de brinde — hoje não se sabe nem o dia exato em que o bot morreu em julho). **Alerta vai para
o 67 99902-2233** (pessoal do Moacir; o (47) 99232-5747 é o comercial/Rodrigo).

## Estado atual

- **Pipeline Instagram:** moacir, moper, laika → Neon PostgreSQL ✅ (cron diário 8h)
- **Banco ativo:** Neon (cloud PostgreSQL) — `DATABASE_URL` no `.env` ✅ e **agora também no
  Railway** ✅ (setada em 10/ago; **antes disso faltava em produção** — ver sessão 6)
- **Hospedagem Railway:** plano **pago** desde 10/ago. O trial venceu e derrubou tudo por ~2
  semanas. ⚠️ Se o pagamento falhar, o bot cai de novo do mesmo jeito.
- **WhatsApp bot Moper:** ✅ **NO AR** como pré-atendimento (Meta API, Claude Haiku,
  `/webhook/moper`), servido por **gunicorn** (2 workers / 4 threads) desde 10/ago.
  Token permanente (System User) no Railway e no `.env` — revalidado na Graph API em 10/ago
  (`quality_rating: GREEN`). Número do bot: **+55 11 92501-2098** — ⚠️ **não é** o número dos
  leads, que é o **(47) 99232-5747** (humano, para onde o bot manda o cliente).
  ⏳ **Falta o teste real por WhatsApp** para confirmar que ele **lembra** do que já foi
  respondido — só agora isso é possível, porque só agora existe banco em produção.
- **Memória de conversa:** código corrigido em 27/07 (30 dias de retenção, `MAX_MESSAGES = 20`),
  mas **só passou a funcionar de fato em 10/ago**, quando `DATABASE_URL` chegou ao Railway.
- **WhatsApp bot Laika:** código pronto, Evolution API configurada — **aguardando escanear QR code** com celular (67) 99857-4771
- **Evolution API:** rodando em https://evo.huboperacional.com.br — instâncias `pai_espaco_laika` e `pai_moper_maquinas` criadas, status `connecting`
- **Catálogo Moper Paleteiras:** publicado no GitHub Pages ✅ → https://moacirpe.github.io/redes-sociais/paleteiras/
- **Meta Business Verification:** ✅ **APROVADA** (~13/06) — foi o que liberou a Meta API oficial do WhatsApp Moper
- **Publicação automática de posts:** ✅ funcionando — `generateCaptions.py` + `publishScheduled.py` + Cloudinary. Testado com post real no moper em 06/06/2026.
- **Credenciais vazias:** TikTok (todos), YouTube (todos), Instagram namasa

---

## Próximos passos (por prioridade)

1. ~~🧪 TESTE REAL DO BOT~~ ✅ **FEITO em 10/ago pela Melissa** — ver sessão 6. Bot `[5-T]`.
   ⚠️ O número de teste fica **`transferred`** e o bot para de responder nele. Para testar de
   novo: `python execution/resetConversation.py "<numero>"`.

1b. **🔔 CHECK DE SAÚDE DO BOT — agora é a prioridade real.** O bot ficou ~2 semanas mudo e o
   alarme foi alguém comentar por acaso. Já caiu por 3 motivos diferentes (crédito Anthropic em
   24/jun, trial da Railway em ~jul/ago, banco ausente o tempo todo). Um ping diário testando
   **webhook + banco + Anthropic** pegaria os três. ⚠️ Falta definir **por onde avisa** —
   `ALERT_EMAIL_*` não existe no `.env` e o `alertSystem.py` nunca teve canal configurado.
2. ~~🔴 SEGURANÇA — token do GitHub em texto puro~~ ✅ **RESOLVIDO em 10/ago** — ver sessão 6.
   Token revogado (401 confirmado), novo com scope mínimo `public_repo` no Keychain, push
   validado. **Só resta anotar na agenda: renovar até 08/nov/2026.**
   ⚠️ A pendência mais ampla **"Segredos no Drive" continua aberta** no `ESTADO.md` — o `.env`
   com 99 chaves (tokens do WhatsApp, Anthropic, banco) segue dentro do Google Drive.
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
| `DATABASE_URL` (Neon) | ✅ no `.env` **e no Railway** (só chegou ao Railway em 10/ago) |
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
| moper | WhatsApp Bot (pré-atendimento) | `[5-T]` ✅ | Testado fim-a-fim 10/ago: qualificou (3T→4,70m→piso→cidade) e transferiu, com memória gravando |
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
