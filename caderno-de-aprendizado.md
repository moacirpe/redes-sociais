# Caderno de Aprendizado — Moacir

Este é o registro vivo do que estou aprendendo. O professor atualiza este arquivo
conforme avançamos — assim nada importante se perde e a revisão acontece na hora certa.

**Última atualização:** 2026-08-10

---

## Vocabulário de inglês técnico

| Termo | Tradução | Pronúncia | Aprendido em | Revisões | Status |
|---|---|---|---|---|---|
| workspace | espaço de trabalho / projeto | UÓRKs-peis | 2026-05-14 | 0 | novo |
| project | projeto | PRÓ-djekt | 2026-05-14 | 0 | novo |
| directory | pasta / diretório | di-RÉK-to-ri | 2026-05-14 | 0 | novo |
| token | ficha / chave de acesso | TÓU-kân | 2026-06-25 | 2 | revisado |
| scope | escopo (o que a chave pode fazer) | SKÔUP | 2026-08-10 | 0 | novo |
| revoke | revogar / cancelar um acesso | ri-VÔUK | 2026-08-10 | 0 | novo |
| board | quadro (o "mapa" no Miro) | BÓRD | 2026-06-25 | 0 | novo |
| host / hosting | hospedar / hospedagem | RÔUST / RÔUS-ting | 2026-06-25 | 0 | novo |
| deploy | publicar / colocar no ar | di-PLÓI | 2026-06-25 | 0 | novo |
| authentication | autenticação (provar quem é) | ó-then-ti-KÊI-chãn | 2026-06-25 | 0 | novo |
| role / permission | papel / permissão (nível de acesso) | RÔUL / per-MÍ-chãn | 2026-06-25 | 0 | novo |
| 2FA | autenticação em dois fatores | tchú-FÁK-tor | 2026-06-25 | 0 | novo |
| session | sessão (a conversa atual) | SÉ-chãn | 2026-06-27 | 0 | novo |
| context window | janela de contexto (memória da sessão) | CON-tékst UÍN-dou | 2026-06-27 | 0 | novo |
| handoff | passagem de bastão / transferência | RÉND-óf | 2026-06-27 | 0 | novo |

## Conceitos aprendidos

- **2026-05-14** — Claude Code tem "workspaces" (projetos) separados — cada pasta de trabalho é um ambiente independente.
- **2026-06-25** — O **token** é só a "chave de acesso". O trabalho (o board no Miro) fica salvo mesmo se o app/token for apagado. Desinstalar o app só corta o acesso de *edição* — não apaga o que já foi feito. Por isso, manter o app = poder editar depois sem retrabalho.
- **2026-06-25** — **Hospedar (host)** = colocar o sistema num computador ligado 24h na internet, com endereço fixo, pra você e o cliente acessarem pelo link. **Deploy** = a ação de publicar. Protótipo (página pronta) sobe fácil/grátis no Vercel ou Netlify; sistema real (com login + dados) usa algo como Supabase + Vercel.
- **2026-06-25** — **Login** é o "porteiro": cada um entra com email + senha (autenticação). Num sistema multi-empresa como o Caixio, o login também define o que cada um vê (analogia do "prédio de cofres": cliente vê só o cofre dele; o BPO vê os cofres dos seus clientes) — isso são as **permissões/roles**. **2FA** = segunda tranca (senha + código no celular). Não precisa programar do zero: o Supabase já traz login pronto.
- **2026-06-27** — Como funciona a memória da conversa: a **session** tem uma **context window** (memória de trabalho) limitada — analogia da **bancada/troca de turno**: o limite é de *espaço* (quanto a gente conversou), não de *tempo*. Quando enche, faz-se o **handoff** = escrever o estado em arquivos (no Caixio: `ESTADO.md`). O `/clear` esvazia a bancada e um ajudante automático lê o `ESTADO.md` e retoma de onde parou. **Não há prazo pra voltar** — os arquivos ficam salvos no Google Drive pra sempre; pode voltar em minutos, dias ou semanas que nada se perde.

- **2026-08-10** — **Login não é token.** São duas coisas diferentes e é fácil confundir: o **login** (entrar pelo Google no site) é *você, pessoa*, passando a digital na catraca — precisa de gente. O **token** é a *cópia da chave que trabalha no seu lugar*: é o que o computador usa pra mandar código pro GitHub sozinho, sem parar pra pedir seu login. Por isso a conta pode não ter senha nenhuma (entra pelo Google) e mesmo assim existir um token que precisa ser trocado. O **scope** do token diz o que ele pode fazer — o nosso era `repo`, a chave-mestra (lê e escreve em todos os repositórios).

## Problemas que resolvi

- **2026-05-14** — Atalho do Centro de Operação parou de funcionar. Causa: favorito do browser apontava para caminho antigo do Google Drive. Solução: abrir o `index.html` direto no Finder (dois cliques) e refavoritar com Cmd+D.
- **2026-06-25** — Primeiro **deploy** do protótipo Caixio no **Netlify Drop** (arrastar e soltar a pasta). Aprendizado: **sem conta**, o link é **temporário (dura 1h) e com senha**. Pra ter um link **permanente e sem senha** pra mandar pro cliente, é preciso **criar a conta grátis** do Netlify e republicar.

## Pontos para revisar

- **Login × token** — a diferença entre "eu entrando" e "a chave que trabalha por mim". Retomar
  daqui a algumas semanas: *"o que é um token, e por que ele é diferente de entrar pelo Google?"*

## Linha do tempo do progresso

- **2026-05-14** — Primeira aula! Começando a aprender a organizar o Claude Code.
- **2026-06-25** — Criou um app no Miro Developers e gerou um token de acesso para automação — montamos o mapa meta do projeto Caixio no Miro via API. Entendeu sozinho que, sem o token, não dá pra editar o board (raciocínio de chave de acesso). 🎯
- **2026-06-27** — Começou a elevação do app Caixio com 120 melhorias (5 de 14 lotes prontos) e entendeu o conceito de **context window / handoff / /clear** — sacou que o limite é de espaço, não de tempo, e que o trabalho fica salvo sem prazo pra voltar. 🎯
- **2026-08-10** — Fez a pergunta certa na hora certa: *"o GitHub não tem senha, entramos pelo Google — está correto?"*. Estava **certo**, e ao questionar em vez de sair criando senha, evitou mexer no que estava funcionando. Sinal de quem já pensa em segurança: separou "como eu entro" de "o que precisa ser trocado". 🎯
