# Design — Publicação Automática de Posts
_Data: 2026-05-10_

## Objetivo

Sistema de publicação automática de posts no Instagram: Claude gera legendas com base em briefing fixo + top posts do cliente, usuário aprova via Google Sheets (Drive), cron publica no horário agendado.

---

## Fluxo completo

```
[1] generateCaptions.py          [2] Google Sheets (queue.csv no Drive)
    --client moacir         →        usuário edita legenda, define
    --count 5                        scheduled_at, media_filename,
                                     muda status draft → approved
                                              ↓
[3] publishScheduled.py          [4] Instagram Graph API
    (cron diário 8h)         →        upload Cloudinary → URL pública
                                      POST media container
                                      polling até FINISHED
                                      POST media_publish
                                      salva ig_post_url no CSV
```

---

## Componentes

| Arquivo | Ação | Responsabilidade |
|---------|------|-----------------|
| `clients/{client}/briefing.md` | Criar (1 por cliente) | Tom, temas, hashtags, CTA do cliente |
| `queue/{client}/queue.csv` | Criar/gerenciar | Fila de posts — editado no Google Sheets |
| `queue/{client}/media/` | Pasta gerenciada pelo usuário | Vídeos e fotos prontos para publicar |
| `execution/generateCaptions.py` | Criar | Gera legendas via Claude API, escreve no CSV |
| `execution/publishScheduled.py` | Criar | Publica posts aprovados via Instagram + Cloudinary |
| `execution/collectAll.sh` | Modificar | Adicionar chamada ao publishScheduled.py |

---

## Queue CSV — estrutura

Caminho: `queue/{client}/queue.csv`

| Coluna | Tipo | Preenchido por | Descrição |
|--------|------|----------------|-----------|
| `id` | string | Sistema | Ex: `moacir-001` |
| `client` | string | Sistema | `moacir`, `moper`, `laika` |
| `platform` | string | Sistema | `instagram` |
| `scheduled_at` | datetime | Usuário | `2026-05-11 08:00` |
| `caption` | text | Claude (usuário edita) | Legenda do post |
| `media_filename` | string | Usuário | `video_11mai.mp4` |
| `status` | string | Usuário/Sistema | `draft` → `approved` → `published` → `failed` |
| `cloudinary_url` | string | Sistema | URL pública após upload |
| `ig_post_url` | string | Sistema | URL do post publicado |
| `generated_at` | datetime | Sistema | Timestamp da geração |
| `published_at` | datetime | Sistema | Timestamp da publicação |
| `error` | string | Sistema | Mensagem de erro (se status=failed) |

---

## Briefing por cliente

Formato Markdown, um arquivo por cliente:

```markdown
# Briefing — {cliente} (@{username})
Tom: [descrição do tom de voz]
Temas: [temas principais]
Hashtags fixas: #tag1 #tag2
CTA padrão: [chamada para ação]
Evitar: [o que não usar]
```

Exemplo para moacir (`clients/moacir/briefing.md`):
```markdown
# Briefing — moacir (@moacir.moper)
Tom: pessoal, autêntico, motivacional
Temas: empreendedorismo, máquinas, bastidores da empresa
Hashtags fixas: #moper #maquinas #empreendedor
CTA padrão: Manda mensagem!
Evitar: linguagem muito formal, jargão técnico excessivo
```

---

## generateCaptions.py

**Interface:**
```bash
python execution/generateCaptions.py --client moacir --count 5
python execution/generateCaptions.py --client moper --count 3 --theme "promoção de maio"
```

**Flags:**
- `--client STR` — cliente (obrigatório)
- `--count INT` — número de legendas a gerar (padrão: 5)
- `--theme STR` — tema/pauta opcional para guiar a geração

**Lógica interna:**
1. Lê `clients/{client}/briefing.md`
2. Consulta Neon: top 10 posts por engajamento (`like_count + comments_count`) do cliente
3. Monta prompt com briefing + exemplos de posts + instrução de geração
4. Chama `anthropic.messages.create()` com `claude-sonnet-4-6`
5. Parseia resposta JSON com lista de legendas
6. Append no `queue/{client}/queue.csv` com `status=draft` — se o arquivo não existir, cria com cabeçalho. O `id` é gerado como `{client}-{N}` onde N é o próximo número sequencial baseado nas linhas existentes.
7. Imprime no console o número de rascunhos gerados

**Prompt structure:**
```
Você é um especialista em redes sociais. Gere {count} legendas para Instagram Reels.

BRIEFING DO CLIENTE:
{conteúdo do briefing.md}

TOP POSTS (inspire-se no estilo, não copie):
{posts com maior engajamento — caption + likes/comments}

{se --theme fornecido: TEMA DESTA SEMANA: {theme}}

Retorne JSON: [{"caption": "...", "hashtags": "..."}, ...]
```

---

## publishScheduled.py

**Interface:**
```bash
python execution/publishScheduled.py                    # todos os clientes
python execution/publishScheduled.py --client moacir   # cliente específico
python execution/publishScheduled.py --dry-run         # simula sem publicar
```

**Lógica interna:**
1. Para cada cliente ativo, lê `queue/{client}/queue.csv`
2. Filtra linhas: `status=approved` E `scheduled_at <= now`
3. Para cada post aprovado:
   a. Valida que `media_filename` existe em `queue/{client}/media/`
   b. Upload para Cloudinary → salva `cloudinary_url` no CSV
   c. `POST /{ig-id}/media` com `video_url` + `caption` → `creation_id`
   d. Polling: `GET /{ig-id}/{creation_id}?fields=status_code` até `FINISHED` (timeout: 5min)
   e. `POST /{ig-id}/media_publish` → salva `ig_post_url`
   f. Atualiza CSV: `status=published`, `published_at=now`
4. Em caso de erro: `status=failed`, salva mensagem em `error`
5. Loga tudo em `execution_logs` no Neon

**Detecção do tipo de mídia:**
- `.mp4`, `.mov` → `media_type=REELS`, `share_to_feed=true`
- `.jpg`, `.jpeg`, `.png` → `media_type=IMAGE`

**Token e base URL por cliente:** reutiliza `CLIENT_ENV_MAP` e `getApiBase()` de `fetchInstagramData.py`. Laika usa token EAA com `graph.facebook.com/v19.0`; moacir e moper usam token IGAA com `graph.instagram.com`.

**`--dry-run`:** imprime no console quais posts seriam publicados (client, scheduled_at, caption truncada, media_filename) sem fazer upload nem chamada à API.

---

## Credenciais necessárias no .env

```
# Cloudinary
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Anthropic (para generateCaptions.py)
ANTHROPIC_API_KEY=
```

**Onde obter:**
- Cloudinary: cloudinary.com → free tier → painel → API Keys
- Anthropic: console.anthropic.com → API Keys

---

## Alteração no collectAll.sh

Adicionar após as coletas de dados:

```bash
PYTHONPATH="$PROJECT_DIR" "$PYTHON" execution/publishScheduled.py >> "$LOG_FILE" 2>&1
echo "publish: exit $?" >> "$LOG_FILE"
```

---

## Tratamento de erros

| Situação | Comportamento |
|----------|--------------|
| Arquivo de mídia não encontrado | `status=failed`, erro no CSV, continua próximo post |
| Cloudinary upload falha | `status=failed`, erro no CSV, sem chamada à Instagram API |
| Instagram API erro | `status=failed`, erro no CSV, Cloudinary URL mantida para retentar |
| Timeout no polling de vídeo | `status=failed`, erro "video processing timeout" |
| `scheduled_at` no futuro | Post ignorado (não é erro) |

---

## Clientes suportados

| Cliente | Queue path | Briefing |
|---------|-----------|---------|
| moacir | `queue/moacir/` | `clients/moacir/briefing.md` |
| moper | `queue/moper/` | `clients/moper/briefing.md` |
| laika | `queue/laika/` | `clients/laika/briefing.md` |

---

## Critério de "pronto"

`[5-T]`: `generateCaptions.py` gera rascunhos no CSV → usuário aprova → `publishScheduled.py` publica com sucesso no Instagram de um cliente real, `ig_post_url` salvo no CSV e post visível na conta.
