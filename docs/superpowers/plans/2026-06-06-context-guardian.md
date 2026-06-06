# Context Guardian — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar um sistema de 3 componentes que detecta contexto pesado, faz handoff dos docs automaticamente, e retoma após `/clear` sem intervenção manual além de digitar `/clear`.

**Architecture:** Skill markdown guia o handoff → hook shell script injeta HANDOFF.md quando `source=clear` → instrução no CLAUDE.md ativa o monitoramento. Nenhuma dependência externa, tudo local.

**Tech Stack:** Bash, Python 3 (parse JSON do stdin), Claude Code hooks (SessionStart), Claude Code skills (SKILL.md)

---

## Mapa de Arquivos

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `~/.claude/skills/context-guardian/SKILL.md` | Criar | Instruções do skill para Claude executar o handoff |
| `~/.claude/hooks/context-guardian-resume.sh` | Criar | Script que injeta HANDOFF.md após /clear |
| `~/.claude/settings.json` | Modificar | Registrar o hook SessionStart |
| `CLAUDE.md` | Modificar | Instrução para Claude monitorar e invocar o skill |

---

## Task 1: Criar o script do hook

**Files:**
- Create: `~/.claude/hooks/context-guardian-resume.sh`

- [ ] **Step 1: Criar o diretório de hooks**

```bash
mkdir -p ~/.claude/hooks
```

- [ ] **Step 2: Criar o script**

Criar o arquivo `~/.claude/hooks/context-guardian-resume.sh` com o seguinte conteúdo:

```bash
#!/bin/bash
# Lê o JSON do stdin passado pelo Claude Code no evento SessionStart
source_val=$(cat | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('source', ''))
except:
    print('')
" 2>/dev/null)

# Só age quando a sessão veio de /clear
if [ "$source_val" = "clear" ]; then
  HANDOFF="/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS/HANDOFF.md"
  if [ -f "$HANDOFF" ]; then
    echo "=== RETOMADA AUTOMÁTICA ==="
    echo "Sessão iniciada após /clear. Leia o estado do projeto abaixo e retome de onde parou:"
    echo ""
    cat "$HANDOFF"
    echo ""
    echo "---"
    echo "Acima está o HANDOFF.md atualizado. Continue o trabalho a partir dos próximos passos listados."
  fi
fi
```

- [ ] **Step 3: Tornar o script executável**

```bash
chmod +x ~/.claude/hooks/context-guardian-resume.sh
```

- [ ] **Step 4: Testar o script manualmente com source=clear**

```bash
echo '{"source":"clear"}' | bash ~/.claude/hooks/context-guardian-resume.sh
```

Resultado esperado: imprime o conteúdo do HANDOFF.md precedido de `=== RETOMADA AUTOMÁTICA ===`

- [ ] **Step 5: Testar com source=startup (deve ser silencioso)**

```bash
echo '{"source":"startup"}' | bash ~/.claude/hooks/context-guardian-resume.sh
```

Resultado esperado: nenhuma saída (silencioso)

- [ ] **Step 6: Commit**

```bash
git -C ~/.claude add hooks/context-guardian-resume.sh 2>/dev/null || true
# Não há git no ~/.claude — só confirmar que o arquivo existe
ls -la ~/.claude/hooks/context-guardian-resume.sh
```

---

## Task 2: Registrar o hook no settings.json

**Files:**
- Modify: `~/.claude/settings.json`

Estado atual do `settings.json`:
```json
{
  "enableAllProjectMcpServers": true,
  "enabledPlugins": { ... },
  "extraKnownMarketplaces": { ... },
  "permissions": {
    "allow": ["Bash(git commit -m ' *)"]
  },
  "effortLevel": "medium"
}
```

- [ ] **Step 1: Adicionar a seção `hooks` ao settings.json**

Adicionar dentro do objeto raiz (antes do `}`  final):

```json
"hooks": {
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "bash /Users/moacirpereira/.claude/hooks/context-guardian-resume.sh"
        }
      ]
    }
  ]
}
```

O `settings.json` completo ficará assim:

```json
{
  "enableAllProjectMcpServers": true,
  "enabledPlugins": {
    "superpowers@superpowers-dev": true,
    "ui-ux-pro-max@ui-ux-pro-max-skill": true
  },
  "extraKnownMarketplaces": {
    "superpowers-dev": {
      "source": {
        "source": "git",
        "url": "https://github.com/obra/superpowers.git"
      }
    },
    "ui-ux-pro-max-skill": {
      "source": {
        "source": "git",
        "url": "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git"
      }
    }
  },
  "permissions": {
    "allow": [
      "Bash(git commit -m ' *)"
    ]
  },
  "effortLevel": "medium",
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash /Users/moacirpereira/.claude/hooks/context-guardian-resume.sh"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Validar o JSON**

```bash
python3 -c "import json; json.load(open('/Users/moacirpereira/.claude/settings.json')); print('JSON válido')"
```

Resultado esperado: `JSON válido`

---

## Task 3: Criar o skill `context-guardian`

**Files:**
- Create: `~/.claude/skills/context-guardian/SKILL.md`

- [ ] **Step 1: Criar o diretório do skill**

```bash
mkdir -p ~/.claude/skills/context-guardian
```

- [ ] **Step 2: Criar o arquivo SKILL.md**

Criar `~/.claude/skills/context-guardian/SKILL.md` com o seguinte conteúdo:

```markdown
---
name: context-guardian
description: >
  Handoff de contexto — atualiza HANDOFF.md e docs/PLANO.md, commita, e instrui
  o usuário a digitar /clear para retomada automática. Invocar quando o contexto
  estiver pesado (histórico longo, muitos arquivos lidos, muitos tool calls).
---

# Context Guardian

Você foi invocado porque o contexto da sessão está ficando pesado. Execute os
passos abaixo em ordem, sem pular nenhum.

## Passo 1 — Anunciar

Diga ao usuário:

> "Contexto pesado detectado. Iniciando handoff automático — vou atualizar os docs
> e preparar uma retomada limpa. Isso leva cerca de 1 minuto."

## Passo 2 — Ler o estado atual

Leia os arquivos:
- `HANDOFF.md` (estado atual do projeto)
- `docs/PLANO.md` (features e tags de progresso)

## Passo 3 — Reescrever o HANDOFF.md

Reescreva o `HANDOFF.md` **completamente** com:

1. **Cabeçalho:** `# Handoff — Redes Sociais` + `_Atualizado em: YYYY-MM-DD (sessão N)_`
2. **Estado atual:** bullet points com o que está funcionando (✅), pendente (⏳), ou quebrado (❌)
3. **O que foi feito nesta sessão:** lista do que foi concluído agora
4. **Próximos passos:** em ordem de prioridade, numerados
5. **Seções de infraestrutura** que existiam antes — manter e atualizar conforme necessário

Seja específico e concreto. O Claude que vai ler este arquivo não tem memória desta sessão.

## Passo 4 — Atualizar docs/PLANO.md

Percorra as features listadas no `docs/PLANO.md` e atualize as tags:
- `[0]` Planejado, não iniciado
- `[1-S]` Diretiva criada OU schema definido
- `[2-E]` Script de execução existe
- `[3-H]` Credenciais configuradas no .env
- `[4-C]` Executado com dado real da API ao menos uma vez
- `[5-T]` Pipeline completo testado nesta sessão

Só atualize tags que mudaram nesta sessão. Não invente progresso.

## Passo 5 — Commit

Execute:

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
git add HANDOFF.md docs/PLANO.md
git commit -m "docs: context-guardian handoff — $(date +%Y-%m-%d)"
```

## Passo 6 — Encerrar

Diga ao usuário:

> "Handoff completo. HANDOFF.md e PLANO.md atualizados e commitados.
>
> **Digite /clear para iniciar sessão limpa — vou retomar automaticamente.**"

Não execute mais nada. Aguarde o usuário digitar /clear.
```

- [ ] **Step 3: Verificar que o skill aparece na lista**

No Claude Code, verificar que o skill `context-guardian` aparece no sistema de skills disponíveis. Pode ser confirmado vendo que o arquivo existe:

```bash
ls -la ~/.claude/skills/context-guardian/SKILL.md
```

Resultado esperado: arquivo listado com permissões normais.

---

## Task 4: Atualizar o CLAUDE.md do projeto

**Files:**
- Modify: `CLAUDE.md` (raiz do projeto Redes Sociais)

- [ ] **Step 1: Adicionar seção Context Guardian ao CLAUDE.md**

Adicionar antes da última linha do arquivo (antes de `**Last Updated**`):

```markdown
## Context Guardian

Monitore o peso do contexto ao longo de cada sessão. Quando perceber que o histórico
está longo — muitos arquivos lidos, muitos tool calls encadeados, respostas acumuladas —
termine a tarefa atual e invoque o skill `context-guardian` sem esperar instrução do usuário.

Sinais de contexto pesado:
- Mais de 15–20 tool calls na sessão
- Arquivos grandes lidos (execução, directives, PLANO.md)
- Respostas longas encadeadas
- Sensação de que "já fiz muita coisa nesta sessão"

**Não espere chegar ao limite.** Agir cedo garante handoff limpo e docs atualizados.
```

- [ ] **Step 2: Atualizar a data no CLAUDE.md**

Atualizar a linha `**Last Updated**` para a data atual:

```markdown
**Last Updated**: 2026-06-06
```

- [ ] **Step 3: Commit**

```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
git add CLAUDE.md
git commit -m "feat: add context-guardian monitoring instruction to CLAUDE.md"
```

---

## Task 5: Teste de fumaça (smoke test)

- [ ] **Step 1: Verificar todos os arquivos criados**

```bash
ls -la ~/.claude/hooks/context-guardian-resume.sh
ls -la ~/.claude/skills/context-guardian/SKILL.md
python3 -c "import json; d=json.load(open('/Users/moacirpereira/.claude/settings.json')); print('hooks' in d and 'SessionStart' in d['hooks'])"
```

Resultado esperado:
```
-rwxr-xr-x  ... context-guardian-resume.sh
-rw-r--r--  ... SKILL.md
True
```

- [ ] **Step 2: Simular o hook com source=clear**

```bash
echo '{"source":"clear","sessionId":"test-123"}' | bash ~/.claude/hooks/context-guardian-resume.sh
```

Resultado esperado: conteúdo do HANDOFF.md impresso com o cabeçalho `=== RETOMADA AUTOMÁTICA ===`

- [ ] **Step 3: Verificar que o hook é silencioso em sessões normais**

```bash
echo '{"source":"startup","sessionId":"test-456"}' | bash ~/.claude/hooks/context-guardian-resume.sh
echo "Exit code: $?"
```

Resultado esperado: nenhuma saída, exit code 0

- [ ] **Step 4: Teste real (opcional mas recomendado)**

1. Invocar o skill `context-guardian` manualmente via `Skill` tool
2. Verificar que Claude segue os passos e commita os docs
3. Digitar `/clear`
4. Verificar que na nova sessão o HANDOFF.md é injetado automaticamente

---

## Notas de Implementação

- O hook usa `python3` para parse do JSON — disponível no macOS por padrão
- O caminho do HANDOFF.md está hardcoded no script. Se o projeto mudar de localização, atualizar `~/.claude/hooks/context-guardian-resume.sh`
- O hook é global (`~/.claude/settings.json`) mas silencioso em projetos sem HANDOFF.md
- O `/clear` continua sendo o único passo manual — limitação do Claude Code, não contornável via skill/hook
