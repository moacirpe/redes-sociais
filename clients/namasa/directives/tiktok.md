# Directive: TikTok — Namasa (Espiritualidade)

## Objetivo
Monitorar o alcance e ressonância de conteúdo espiritual breve no TikTok da Namasa. O TikTok serve como **porta de entrada** — conteúdo curto que toca, que faz a pessoa parar no scroll e refletir. A métrica mais importante é **completion rate**: quem assiste até o fim estava presente.

## Credenciais (.env)
```
NAMASA_TIKTOK_ACCESS_TOKEN=
NAMASA_TIKTOK_OPEN_ID=
NAMASA_TIKTOK_REFRESH_TOKEN=
```

## Métricas a Coletar

### Conta (diário)
- Seguidores e variação
- Likes totais
- Views totais

### Por Vídeo
- Views, likes, comentários, **compartilhamentos** ← importante para conteúdo espiritual
- **Completion rate** ← mais importante (quem ficou até o fim estava presente)
- Tempo médio assistido (segundos)
- Fonte de tráfego: FYP, seguindo, busca, hashtag
- Seguidores novos gerados

### Análise de Conteúdo
- Formatos com maior completion rate (fala direta ao câmera, natureza, silêncio com texto)
- Vídeos que geraram mais compartilhamentos (conteúdo que toca)
- Duração ideal para manter completion rate alto

## Processo

### Step 1: Coleta diária
```bash
python clients/namasa/execution/fetchTikTokMetrics.py --save
```

### Step 2: Análise
```bash
python clients/namasa/execution/analyzeVideoPerformance.py --platform tiktok
```

Identifica:
- Top 5 por **completion rate** (conteúdo que sustenta atenção)
- Top 5 por **compartilhamentos** (conteúdo que toca e é passado adiante)
- Duração média dos vídeos com completion > 60%
- Vídeos que geraram pico de novos seguidores (porta de entrada)

## Interpretação — Contexto Espiritual

| Sinal | Significado |
|-------|-------------|
| Completion rate > 70% | O conteúdo manteve a pessoa presente — formato a replicar |
| Alto compartilhamento | Conteúdo que a pessoa quis dar a alguém — muito valioso |
| Comentário com relato pessoal | Ressonância profunda — responder |
| Alto FYP, baixo compartilhamento | Alcance amplo mas superficial — aprofundar conteúdo |
| Baixo FYP, alto compartilhamento | Comunidade pequena mas comprometida — conteúdo de nicho valioso |

## Tipos de Conteúdo TikTok — Namasa
- Fala direta ao câmera (reflexão curta, 30–60s)
- Cenas de natureza com texto contemplativo
- Perguntas que convidam à reflexão interna
- Trechos de ensinamentos do YouTube (repurposing)
- Silêncio + frase + música suave

## Benchmarks

| Métrica | Atual | Meta Namasa |
|---------|-------|-------------|
| Seguidores | — | — |
| Completion rate médio | — | >55% |
| Compartilhamentos/views | — | >2% |
| % tráfego FYP | — | >50% |

> Preencher após primeira coleta

## Edge Cases

### Token expirado (access: 24h)
**Fix**: Script renova via `NAMASA_TIKTOK_REFRESH_TOKEN` automaticamente.
Se refresh expirar (30 dias): reconectar no TikTok Business Center.

### App em sandbox (dados fictícios)
**Fix**: Submeter app para revisão no TikTok Developer Portal.

### Sem dados de completion rate
Disponível apenas para contas Business verificadas.

## Outputs
- `.tmp/namasa/tiktok_<YYYYMMDD>.json`
- Métricas em `metrics`: `client = 'namasa'`, `platform = 'tiktok'`
- Seção TikTok no relatório mensal

---
**Última atualização**: 2026-04-06
**Contexto**: Completion rate e compartilhamentos são os sinais mais importantes — não views
**Status**: Aguardando credenciais no .env
