# Directive: YouTube — Moacir (Pessoal)

## Objetivo
Monitorar performance de vídeos do canal pessoal do Moacir no YouTube. Foco em watch time, retenção e crescimento de inscritos.

## Credenciais (.env)
```
MOACIR_YOUTUBE_API_KEY=
MOACIR_YOUTUBE_CHANNEL_ID=
```

## Métricas a Coletar

### Canal (semanal)
- Inscritos e variação
- Views totais e watch time (horas)
- Impressões e CTR global

### Por Vídeo
- Views, likes, comentários, compartilhamentos
- Watch time médio e % de retenção
- CTR do thumbnail
- Fontes de tráfego: busca, sugerido, externo, direto
- Novos inscritos gerados pelo vídeo

## Processo

### Step 1: Coletar dados
```bash
python clients/moacir/execution/fetchYouTubeMetrics.py --save
```

### Step 2: Análise
```bash
python clients/moacir/execution/analyzeVideoPerformance.py --platform youtube
```

## Benchmarks

| Métrica | Atual | Meta |
|---------|-------|------|
| Inscritos | — | — |
| Views/mês | — | — |
| CTR médio | — | >4% |
| Retenção média | — | >40% |

> Preencher após primeira coleta

## Edge Cases

### Quota API esgotada (403 quotaExceeded)
YouTube API: 10.000 unidades/dia.
**Fix**: Executar coleta 1x/dia, preferencialmente à meia-noite.

### Vídeo com < 100 views
YouTube não expõe dados de retenção.
Script ignora retenção para esses vídeos.

## Outputs
- `.tmp/moacir/youtube_<YYYYMMDD>.json`
- Métricas em `metrics`: `client = 'moacir'`, `platform = 'youtube'`

---
**Última atualização**: 2026-04-06
**Status**: Aguardando credenciais no .env
