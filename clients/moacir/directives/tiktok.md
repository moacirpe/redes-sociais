# Directive: TikTok — Moacir (Pessoal)

## Objetivo
Monitorar crescimento e performance de vídeos no TikTok pessoal do Moacir. Foco em completion rate, tráfego FYP e conteúdo que gera novos seguidores.

## Credenciais (.env)
```
MOACIR_TIKTOK_ACCESS_TOKEN=
MOACIR_TIKTOK_OPEN_ID=
MOACIR_TIKTOK_REFRESH_TOKEN=
```

## Métricas a Coletar

### Conta (diário)
- Seguidores e variação
- Likes totais
- Views totais do período

### Por Vídeo
- Views, likes, comentários, compartilhamentos
- Completion rate (% que assistiu até o final) — mais importante
- Tempo médio assistido (segundos)
- Fonte de tráfego: FYP, seguindo, busca, hashtag
- Seguidores novos gerados pelo vídeo

## Processo

### Step 1: Coleta diária
```bash
python clients/moacir/execution/fetchTikTokMetrics.py --save
```

### Step 2: Análise
```bash
python clients/moacir/execution/analyzeVideoPerformance.py --platform tiktok
```

## Sinais de Qualidade — TikTok

| Sinal | Meta |
|-------|------|
| Completion rate | >60% |
| % tráfego FYP | >60% |
| Shares/views | >1% |
| Likes/views | >5% |

## Edge Cases

### Token expirado (access: 24h)
**Fix**: Script renova automaticamente via `MOACIR_TIKTOK_REFRESH_TOKEN`.
Se refresh expirar (30 dias): reconectar no TikTok Business Center.

### Sem dados de completion rate
Disponível apenas para contas Business verificadas.

## Outputs
- `.tmp/moacir/tiktok_<YYYYMMDD>.json`
- Métricas em `metrics`: `client = 'moacir'`, `platform = 'tiktok'`

---
**Última atualização**: 2026-04-06
**Status**: Aguardando credenciais no .env
