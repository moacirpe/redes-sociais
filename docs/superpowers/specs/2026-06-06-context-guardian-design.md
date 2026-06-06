# Context Guardian — Design Spec
_Data: 2026-06-06_

## Objetivo

Sistema de gerenciamento de contexto que detecta quando a sessão está pesada, faz handoff automático dos docs, e retoma automaticamente após `/clear` — sem interrupção perceptível no fluxo de trabalho.

---

## Fluxo Completo

```
[Claude sente contexto pesado]
        ↓
[Termina tarefa atual]
        ↓
[Invoca skill: context-guardian]
        ↓
  ┌── Atualiza HANDOFF.md (estado atual da sessão)
  ├── Atualiza docs/PLANO.md (tags de progresso [0]→[5-T])
  └── Git commit: "docs: context-guardian handoff — YYYY-MM-DD"
        ↓
[Claude avisa: "Pronto. Digite /clear."]
        ↓
[Usuário digita /clear]  ← único passo manual
        ↓
[Hook SessionStart detecta source="clear"]
        ↓
[Injeta HANDOFF.md no contexto automaticamente]
        ↓
[Claude retoma ciente do estado]
```

---

## Componentes

### 1. Skill `context-guardian`

**Localização:** `~/.claude/skills/context-guardian`

**Responsabilidade:** guiar Claude pelo processo de handoff quando o contexto está pesado.

**Passos em ordem:**
1. Anunciar ao usuário que o contexto está pesado e o handoff está começando
2. Ler `HANDOFF.md` e `docs/PLANO.md` para entender estado atual
3. Reescrever `HANDOFF.md` com:
   - O que foi feito nesta sessão
   - Estado atual de cada pipeline/cliente
   - Próximos passos em ordem de prioridade
   - Data e hora do handoff
4. Atualizar tags `[0]`→`[5-T]` no `docs/PLANO.md` refletindo progresso real
5. `git add HANDOFF.md docs/PLANO.md` + commit com mensagem padronizada
6. Exibir: **"Handoff completo. Digite /clear para iniciar sessão limpa — vou retomar automaticamente."**

**O skill para aqui.** Não tenta fazer mais nada.

---

### 2. Hook `SessionStart`

**Localização:** entrada em `~/.claude/settings.json`

**Responsabilidade:** detectar quando a sessão veio de `/clear` e injetar o `HANDOFF.md` automaticamente.

**Script:**
```bash
#!/bin/bash
source=$(cat | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('source',''))" 2>/dev/null)

if [ "$source" = "clear" ]; then
  HANDOFF="/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS/HANDOFF.md"
  if [ -f "$HANDOFF" ]; then
    echo "=== RETOMADA AUTOMÁTICA ==="
    echo "Sessão iniciada após /clear. Estado do projeto:"
    echo ""
    cat "$HANDOFF"
    echo ""
    echo "Continue de onde parou com base no HANDOFF acima."
  fi
fi
```

**Comportamento:**
- `source = "startup"` ou `"resume"` → silencioso, não age
- `source = "clear"` → injeta HANDOFF.md antes de Claude processar qualquer coisa
- Se `HANDOFF.md` não existe → silencioso (não interfere em outros projetos)

---

### 3. Instrução no `CLAUDE.md`

Nova seção adicionada ao `CLAUDE.md` do projeto:

```markdown
## Context Guardian

Monitore o peso do contexto ao longo de cada sessão. Quando perceber que o histórico
está longo — muitos arquivos lidos, muitos tool calls encadeados, respostas acumuladas —
termine a tarefa atual e invoque o skill `context-guardian` sem esperar instrução do usuário.

Não espere chegar ao limite. Agir cedo garante handoff limpo.
```

---

## Decisões de Design

| Decisão | Motivo |
|---|---|
| `/clear` é manual | Claude Code não permite que skill ou hook emita `/clear` programaticamente |
| Skill em `~/.claude/skills/` | Disponível globalmente, não só neste projeto |
| Hook em `~/.claude/settings.json` | Global — mas verifica existência do HANDOFF.md antes de agir |
| Detecção por julgamento do Claude | Não há evento nativo "contexto em 60%" — instrução no CLAUDE.md é suficiente |
| Commit antes do /clear | Garante que os docs estejam salvos mesmo se algo der errado |

---

## O que NÃO está no escopo

- Threshold numérico exato (não há API para isso sem variável de ambiente)
- Compaction automática (Opção B/C descartadas — não dão fresh start)
- Resume de outros projetos (hook verifica caminho fixo do HANDOFF.md)

---

## Arquivos Criados/Modificados

| Arquivo | Ação |
|---|---|
| `~/.claude/skills/context-guardian` | Criar |
| `~/.claude/settings.json` | Modificar — adicionar hook SessionStart |
| `CLAUDE.md` | Modificar — adicionar seção Context Guardian |
