# Directive: YouTube — Namasa (Espiritualidade)

## Objetivo
Monitorar a performance de conteúdo espiritual longo no YouTube da Namasa. O YouTube é o espaço de **aprofundamento** — meditações guiadas, ensinamentos, conversas contemplativas. A métrica mais importante aqui é **watch time e retenção**: pessoas que ficam até o fim estão realmente presentes.

## Credenciais (.env)
```
NAMASA_YOUTUBE_API_KEY=
NAMASA_YOUTUBE_CHANNEL_ID=
```

## Métricas a Coletar

### Canal (semanal)
- Inscritos e variação
- Watch time total (horas) — indica tempo de presença genuína
- Views totais
- CTR do thumbnail

### Por Vídeo
- Views, likes, comentários
- **Watch time médio** e **% de retenção** ← mais importantes
- CTR do thumbnail
- Fontes de tráfego: busca, sugerido, externo, direto
- Novos inscritos gerados pelo vídeo

### Análise de Retenção (crítica)
- Curva de retenção por vídeo
- Onde as pessoas saem (sinal de onde o conteúdo perde atenção)
- Picos de replay (momentos de maior ressonância)

## Processo

### Step 1: Coleta semanal
```bash
python clients/namasa/execution/fetchYouTubeMetrics.py --save
```

### Step 2: Análise
```bash
python clients/namasa/execution/analyzeVideoPerformance.py --platform youtube
```

Identifica:
- Vídeos com **retenção > 50%** (conteúdo que sustenta presença)
- Vídeos com **watch time alto** mesmo com views baixas (audiência pequena mas presente)
- Vídeos com queda abrupta nos primeiros 2 minutos (intro perdendo atenção)
- Formatos que mantêm a audiência: meditação guiada vs. ensinamento vs. conversa

## Tipos de Conteúdo Monitorados
- Meditações guiadas (10–30 min)
- Ensinamentos / reflexões faladas (5–20 min)
- Conversas / entrevistas contemplativas (20–60 min)
- Conteúdo curto (YouTube Shorts — reflexões de 60s)

## Interpretação — Contexto Espiritual

| Sinal | Significado |
|-------|-------------|
| Retenção > 60% em meditação | Conteúdo que sustenta presença — continuar esse formato |
| Watch time alto, views baixas | Audiência pequena mas comprometida — valiosa |
| Queda nos primeiros 2 min | Intro muito longa ou não ressoa — encurtar entrada |
| Muitos inscritos de 1 vídeo | Conteúdo de porta de entrada — replicar o tema |
| Comentários com relatos | Alta ressonância — responder pessoalmente |

## Benchmarks

| Métrica | Atual | Meta Namasa |
|---------|-------|-------------|
| Inscritos | — | — |
| Watch time médio | — | >50% do vídeo |
| Retenção média | — | >45% |
| Comentários com relatos | — | >30% dos comentários |

> Preencher após primeira coleta

## Edge Cases

### Quota esgotada (403 quotaExceeded)
YouTube API: 10.000 unidades/dia. Executar 1x/dia.

### Vídeo com < 100 views
YouTube não disponibiliza curva de retenção. Script pula análise de retenção.

### Canal sem Analytics API habilitado
**Fix**: console.cloud.google.com → APIs → YouTube Analytics API → Ativar

## Outputs
- `.tmp/namasa/youtube_<YYYYMMDD>.json`
- Métricas em `metrics`: `client = 'namasa'`, `platform = 'youtube'`
- Seção YouTube no relatório mensal

---
**Última atualização**: 2026-04-06
**Contexto**: Watch time e retenção são os sinais mais importantes — não views
**Status**: Aguardando credenciais no .env
