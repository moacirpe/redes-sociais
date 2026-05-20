# Design — Relatório Mensal de Redes Sociais
_Data: 2026-05-09_

## Objetivo

Script `execution/generateReport.py` que consulta o Neon PostgreSQL e gera um relatório mensal com crescimento de seguidores, taxa de engajamento e top posts por cliente.

---

## Dados de entrada

Fonte: Neon PostgreSQL via `DbClient`.

| Tabela | O que usa |
|--------|-----------|
| `metrics` | `followers`, `engagement_rate`, `metric_date`, `client` |
| `posts` | `content`, `metadata` (like_count, comments_count, permalink), `published_at`, `client` |
| `social_accounts` | `username`, `display_name`, `client` |

Clientes ativos: `moacir`, `moper`, `laika`. Namasa omitida (sem dados).

---

## Métricas calculadas

Para cada cliente no período:

| Campo | Como calcular |
|-------|--------------|
| `followers` | snapshot mais recente em `metrics` |
| `follower_growth` | `followers_recente - followers_inicio_periodo` |
| `follower_growth_pct` | `(growth / followers_inicio) * 100` |
| `avg_engagement_rate` | média de `engagement_rate` no período |
| `total_posts` | count de posts com `published_at` no período |
| `top_post_url` | post com maior `like_count + comments_count` |
| `top_post_likes` | likes do top post |
| `top_post_comments` | comentários do top post |

---

## Interface do script

```bash
# Console (padrão)
python execution/generateReport.py --period 30

# CSV para Google Sheets
python execution/generateReport.py --period 30 --csv

# CSV com caminho customizado
python execution/generateReport.py --period 30 --csv --output .tmp/exports/report_2026-05.csv

# Cliente específico
python execution/generateReport.py --client moacir --period 30
```

Flags:
- `--period INT` — dias do período (padrão: 30)
- `--csv` — gera CSV além do console
- `--output PATH` — caminho do CSV (padrão: `.tmp/exports/report_YYYY-MM.csv`)
- `--client STR` — filtra por cliente (padrão: todos)

---

## Saída console

```
=== Relatório Mensal — 2026-05-09 (últimos 30 dias) ===

Cliente: moacir (@moacir.moper)
  Seguidores:    1.234  (+45, +3.8%)
  Engajamento:   2.14%  (média do período)
  Posts:         12
  Top post:      https://www.instagram.com/p/... (87 likes, 5 comentários)

Cliente: moper (@moper.maquinas)
  ...
```

---

## Saída CSV

Colunas:
```
client, username, period_start, period_end, followers, follower_growth,
follower_growth_pct, avg_engagement_rate, total_posts,
top_post_url, top_post_likes, top_post_comments
```

Uma linha por cliente. Salvo em `.tmp/exports/report_YYYY-MM.csv`.

---

## Arquitetura interna

```
generateReport.py
├── loadClients(client_filter)         → lista clientes a processar
├── fetchClientMetrics(db, client, since, until) → Dict com métricas agregadas
├── fetchTopPost(db, client, since, until)       → Dict com dados do top post
├── buildReportRow(client_data)        → Dict normalizado por cliente
├── printConsoleReport(rows)           → formata para terminal
├── writeCsv(rows, output_path)        → escreve CSV
└── main()                             → orquestra tudo via argparse
```

Sem dependências novas — usa `DbClient` existente e biblioteca padrão (`csv`, `argparse`).

---

## Tratamento de erros

- Cliente sem dados no período: inclui linha com `N/A`, não aborta os demais
- Conexão Neon falha: erro claro com instrução de verificar `DATABASE_URL`
- Diretório de output não existe: criado automaticamente

---

## Critério de "pronto"

`[5-T]`: script roda sem erro, gera CSV com dados reais dos 3 clientes ativos (moacir, moper, laika), colunas corretas.
