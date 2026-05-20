# Directive: YouTube — Moper Máquinas

## Objetivo
Monitorar performance de vídeos técnicos e tutoriais no YouTube da Moper Máquinas. Foco em retenção de audiência, watch time e crescimento de canal.

## Credenciais Necessárias (.env)
```
MOPER_YOUTUBE_API_KEY=
MOPER_YOUTUBE_CHANNEL_ID=
```

## Métricas a Coletar

### Canal (semanal)
- Inscritos totais
- Total de views
- Watch time acumulado (horas)
- Receita estimada (se canal monetizado)

### Por Vídeo (últimos 50 ou por período)
- Views, likes, comentários, compartilhamentos
- Watch time médio e % de retenção
- CTR (click-through rate do thumbnail)
- Impressões vs. views
- Tráfego por fonte (busca, sugerido, externo, direto)
- Cards e telas finais (cliques)

### Análise de Retenção (crítico)
- Curva de retenção por vídeo
- Ponto de maior queda (onde os usuários saem)
- Segmentos com rewatch (spike na curva = conteúdo interessante)

## Processo de Coleta

### Step 1: Coletar dados do canal e vídeos
```bash
python clients/moper-maquinas/execution/fetchYouTubeMetrics.py --save
```

### Step 2: Análise de performance de vídeos
```bash
python clients/moper-maquinas/execution/analyzeVideoPerformance.py --platform youtube
```

Identifica:
- Top 5 vídeos por views (últimos 30 dias)
- Top 5 por watch time
- Top 5 por taxa de retenção
- Vídeos com CTR abaixo de 2% (thumbnail fraca)
- Vídeos com queda brusca nos primeiros 30 segundos (intro ruim)

### Step 3: Recomendações mensais
Baseado nos dados, gerar:
1. Quais formatos performam melhor (curto vs. longo)
2. Horário ideal de publicação
3. Títulos e thumbnails que geram mais CTR
4. Tópicos com maior watch time

## Benchmarks do Canal

| Métrica | Valor Atual | Meta |
|---------|-------------|------|
| Inscritos | — | — |
| Views/mês | — | — |
| Watch time/mês (h) | — | — |
| CTR médio | — | >4% |
| Retenção média | — | >40% |
| Likes/views ratio | — | >3% |

> Preencher após primeira coleta

## Classificação de Vídeos por Performance

### 🔥 Alto desempenho
- Views > média do canal × 1.5
- Retenção > 50%
- CTR > 6%

### ✅ Bom desempenho
- Views próximas à média
- Retenção 35–50%
- CTR 3–6%

### ⚠️ Baixo desempenho
- Views < média do canal × 0.5
- Retenção < 35%
- CTR < 2%

## Tipos de Vídeo Monitorados
- Tutoriais de uso de máquinas
- Reviews de equipamentos
- Cases de cliente
- Dicas rápidas (Shorts)

## Edge Cases

### Quota da API esgotada
YouTube Data API tem 10.000 unidades/dia.
**Estimativa por operação**: list vídeos = ~1 unit/vídeo; analytics = ~100 units/query
**Fix**: Rodar coleta uma vez por dia, no horário de menor uso (madrugada)
**Script já verifica quota restante antes de executar**

### Canal sem YouTube Analytics API habilitado
**Requisito**: Canal deve estar conectado ao Google Search Console e ter Analytics API ativado
**Fix**: Ativar em console.cloud.google.com → APIs → YouTube Analytics API

### Vídeo privado ou removido
Script ignora automaticamente, registra no log.

## Outputs
- `.tmp/moper/youtube_<YYYYMMDD>.json` — dados brutos de vídeos
- `.tmp/moper/youtube_retention_<video_id>.json` — curva de retenção por vídeo
- Métricas gravadas em `metrics` (PostgreSQL), `platform = 'youtube'`, `client = 'moper'`
- Seção YouTube incluída no relatório mensal

## Ferramentas
- `execution/fetchYouTubeMetrics.py`
- `execution/analyzeVideoPerformance.py`

## Atualizar Este Directive Quando
- Canal atingir marco de inscritos (ex: 1k, 10k)
- Mudar estratégia de conteúdo (mais Shorts, mais tutoriais)
- API do YouTube mudar versão
- Benchmarks forem estabelecidos

---
**Última atualização**: 2026-04-06
**API**: YouTube Data API v3 + YouTube Analytics API
**Quota padrão**: 10.000 unidades/dia
**Status**: Aguardando MOPER_YOUTUBE_API_KEY e MOPER_YOUTUBE_CHANNEL_ID no .env
