# Directive: YouTube — Espaço Laika

## Objetivo
Monitorar performance de vídeos no YouTube do Espaço Laika. Foco em watch time, retenção e crescimento orgânico via SEO do YouTube.

## Credenciais Necessárias (.env)
```
LAIKA_YOUTUBE_API_KEY=
LAIKA_YOUTUBE_CHANNEL_ID=
```

## Métricas a Coletar

### Canal (semanal)
- Inscritos e variação no período
- Views totais e watch time (horas)
- RPM (se monetizado)
- Impressões e CTR global do canal

### Por Vídeo
- Views, likes, comentários, compartilhamentos
- Watch time total e médio por viewer
- % de retenção da audiência (curva)
- CTR do thumbnail
- Fontes de tráfego: busca, sugerido, FYP, externo
- Novos inscritos gerados pelo vídeo

### SEO do Vídeo
- Posição nas buscas para palavras-chave principais
- Tags e descrição otimizadas
- Performance de cards e telas finais

## Processo de Coleta

### Step 1: Coletar dados semanalmente
```bash
python clients/espaco-laika/execution/fetchYouTubeMetrics.py --save
```

### Step 2: Análise de vídeos
```bash
python clients/espaco-laika/execution/analyzeVideoPerformance.py --platform youtube
```

Gera:
- Ranking de vídeos por performance composta (views + retenção + CTR)
- Alerta para vídeos com CTR < 2% (thumbnail precisa ser revisada)
- Alerta para retenção < 30% (intro ou conteúdo fraco)
- Vídeos com crescimento acelerado (últimos 7 dias)

### Step 3: Análise de retenção por segmento (mensal)
Para cada vídeo com > 500 views:
- Identificar momento exato de maior queda de audiência
- Identificar picos de replay
- Recomendar ajuste no formato/duração/ritmo

## Benchmarks

| Métrica | Valor Atual | Referência Setor |
|---------|-------------|-----------------|
| Inscritos | — | — |
| Views/mês | — | — |
| Watch time/mês (h) | — | — |
| CTR médio | — | 4–10% |
| Retenção média | — | >40% |
| Inscritos/vídeo | — | — |

> Preencher após primeira coleta

## Tipos de Conteúdo Monitorados
- Vlogs / dia a dia do espaço
- Conteúdo temático do segmento
- YouTube Shorts
- Lives arquivadas

## Edge Cases

### Quota esgotada (403 quotaExceeded)
YouTube API: 10.000 unidades/dia grátis.
**Fix**: Script verifica quota antes de executar. Rodar 1x/dia preferentemente à meia-noite.
**Solução definitiva**: Solicitar aumento de quota em console.cloud.google.com

### Vídeo com < 100 views
YouTube não expõe dados de retenção para vídeos com poucos views.
Script registra vídeo mas pula análise de retenção.

### Canal sem Analytics API
**Fix**: Ativar YouTube Analytics API no Google Cloud Console + oauth2.

## Outputs
- `.tmp/laika/youtube_<YYYYMMDD>.json`
- `.tmp/laika/youtube_retention_<video_id>.json`
- Métricas em `metrics`: `client = 'laika'`, `platform = 'youtube'`
- Seção YouTube no relatório mensal

## Ferramentas
- `execution/fetchYouTubeMetrics.py`
- `execution/analyzeVideoPerformance.py`

---
**Última atualização**: 2026-04-06
**API**: YouTube Data API v3 + YouTube Analytics API
**Status**: Aguardando LAIKA_YOUTUBE_API_KEY no .env
