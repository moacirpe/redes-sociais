# ESTADO — Redes Sociais
Status: 🟡 bot restaurado e funcionando, **em manutenção deliberada até 11/ago**
Atualizado em: 10/ago/2026 (sessão 6)

> Detalhe técnico completo em `HANDOFF.md`. Este arquivo é só o resumo.

## ⚠️ LEIA ANTES DE DIAGNOSTICAR QUALQUER COISA

**O bot Moper está em MODO MANUTENÇÃO de propósito.** Se você mandar mensagem para o
**+55 11 92501-2098** e receber *"nosso atendimento virtual está passando por uma melhoria"*,
**isso não é bug** — é a chave `MOPER_MODO_MANUTENCAO=1` no Railway, ligada por decisão do
Moacir em 10/ago para editar o prompt sem atender cliente com versão pela metade.

**Para desligar** (primeira coisa a fazer ao retomar, depois que o prompt estiver pronto):
```
railway variables --set "MOPER_MODO_MANUTENCAO=0"   # projeto fearless-possibility, serviço web
```
Em manutenção o bot **não chama a IA e não grava histórico** — encaminha todo mundo para o
consultor **(47) 99232-5747**. Ninguém fica no silêncio.

## ✅ Resolvido na sessão 6 (10/ago)

- **Apagão do bot — causa raiz:** `Your trial has expired` — o trial da Railway venceu e a
  plataforma **removeu os deploys**. Plano pago assinado pela Melissa; serviço religado.
  Ficou fora ~2 semanas (funcionou em 27/jul, 404 em 06/ago).
- **🔴 `DATABASE_URL` nunca existiu no Railway.** O bot rodava **sem banco** — a correção de
  memória de 27/jul jamais teve efeito em produção. Explica de vez `whatsapp_conversations`
  com 0 linhas: **nunca houve gravação**, não foi purga nem reset. Corrigido.
- **Servidor de desenvolvimento em produção.** Um start command customizado sobrepunha o
  `Procfile`. Trocado para gunicorn (2 workers / 4 threads).
- **Bot testado fim-a-fim pela Melissa** → `[5-T]`. Qualificou 3T → 4,70m → piso → cidade
  **sem repetir pergunta** e transferiu. 10 mensagens no banco (era 0 desde sempre).
- **🔒 Token do GitHub — pendência de 27/jul fechada.** Revogado (confirmado HTTP 401), novo
  com scope mínimo `public_repo` (era `repo`, sem expiração) no Keychain do macOS, push real
  validado. **Renovar até 08/nov/2026.**

## Pendências (o que falta)

- ⏳ **Reescrita do prompt — persona "Elô"** (em andamento, decidido com o Moacir):
  estrutura de 8 blocos acordada, bloco **ABERTURA já redigido** (menu: informações ×
  falar com consultor). Ver `HANDOFF.md` para o texto pronto.
- ❌ **3 defeitos achados na conversa real de 10/ago:**
  1. 🔴 **Link do consultor escondido** — `whatsappResponder.py:354` junta recomendação +
     link numa mensagem só; o WhatsApp corta com "Ler mais" e **o link fica na parte oculta**.
     Custa lead. Corrigir mandando o link em mensagem separada.
  2. 🟡 **Mensagem duplicada** — mesma resposta enviada 2× no mesmo segundo. Hipótese (a
     confirmar, **não afirmar sem evidência**): falta dedupe por id de mensagem da Meta.
  3. 🟡 **Tique do "Perfeito!"** — repetido 3× seguidas; dois encerramentos emendados.
- ⏳ **Vigia de saúde — design aprovado, nada escrito.** GitHub Actions (fora da Railway, para
  sobreviver a uma queda dela) + endpoint `/health` protegido dentro do bot (mantém as chaves
  do banco e da IA na Railway) + template WhatsApp a criar na Meta. Alerta para o
  **67 99902-2233**, de hora em hora, **só na mudança de estado**, heartbeat às segundas.
- ❌ **`GOOGLE_REFRESH_TOKEN` morto** (`invalid_grant`) — o lead qualificado **não entra sozinho
  na planilha "Leads Moper"**; a Melissa ainda digita à mão. Destravar com `authorizeGoogle.py`.
- ⏳ **Laika WhatsApp** — código pronto, falta escanear QR code com o (67) 99857-4771.
- ⏳ **Faxina:** projeto duplicado `keen-vitality` na Railway (mesmo repo, também derrubado).
- 🔒 **Segredos no Drive — segue aberto.** O `.env` com 99 chaves (WhatsApp, Anthropic, banco)
  continua dentro do Google Drive. O token do GitHub era **um** deles; os outros não foram
  tratados.

## Próximos passos

1. **Terminar o prompt da Elô** (blocos 1 e 3–8), aplicar, testar.
2. **Corrigir o link escondido** (`whatsappResponder.py:354`) — é o defeito que custa dinheiro.
3. **Desligar o modo manutenção** (`MOPER_MODO_MANUTENCAO=0`) e testar de ponta a ponta.
   ⚠️ O número do Moacir (**556799022233**) está marcado `transferred` — o bot fica mudo com
   ele até rodar `python execution/resetConversation.py "+55 67 99902-2233"`.
4. **Investigar a mensagem duplicada** com evidência antes de concluir a causa.
5. **Construir o vigia de saúde** — o bot já caiu por 3 motivos diferentes e nas 3 vezes o
   alarme foi alguém reparar por acaso.

## 🔒 Segredos no Google Drive — decisão do Moacir pendente (17/jul)

Continua valendo. Ver `HANDOFF.md`. O token do GitHub foi resolvido em 10/ago; o `.env`, não.

## Infraestrutura (referência rápida)

- **Railway:** projeto `fearless-possibility` → serviço `web` → `web-production-476d9.up.railway.app`.
  Plano **pago** desde 10/ago. ⚠️ Se o pagamento falhar, cai igual a julho.
- **Banco:** Neon PostgreSQL via `DATABASE_URL` (no `.env` **e** no Railway desde 10/ago).
- **Bot:** +55 11 92501-2098 (não é o número dos leads — o humano é o **(47) 99232-5747**).
