# Directive: TikTok — Moper Máquinas

## Objetivo
Monitorar alcance, viralização e engajamento no TikTok da Moper Máquinas. Identificar vídeos com maior potencial e padrões de conteúdo que performam bem no algoritmo.

## Credenciais Necessárias (.env)
```
MOPER_TIKTOK_ACCESS_TOKEN=
MOPER_TIKTOK_OPEN_ID=
```

## Métricas a Coletar

### Conta (diário)
- Seguidores totais
- Likes totais da conta
- Visualizações totais

### Por Vídeo
- Views, likes, comentários, compartilhamentos
- Tempo médio de visualização
- Taxa de conclusão (completion rate) — CRÍTICA no TikTok
- Plays (distintos de views — um user pode rever)
- Tráfego por fonte: FYP (For You Page), seguidores, busca, hashtag, sons
- Novos seguidores gerados pelo vídeo

### Análise de Algoritmo
- % de views vindas do FYP (> 70% = bom alcance orgânico)
- Completion rate > 80% = sinal forte para o algoritmo
- Shares / views ratio (indica valor percebido)

## Processo de Coleta

### Step 1: Coletar dados
```bash
python clients/moper-maquinas/execution/fetchTikTokMetrics.py --save
```

### Step 2: Análise de vídeos
```bash
python clients/moper-maquinas/execution/analyzeVideoPerformance.py --platform tiktok
```

Identifica:
- Top 5 vídeos por views (últimos 30 dias)
- Top 5 por completion rate
- Vídeos que geraram pico de seguidores
- Sons e hashtags usados nos top performers
- Duração média dos vídeos que completam bem

### Step 3: Análise de tendências (semanal)
- Hashtags com crescimento no nicho
- Sons em alta no segmento de máquinas/indústria
- Formatos virais adaptáveis para Moper

## Benchmarks TikTok

| Métrica | Valor Atual | Referência Setor |
|---------|-------------|-----------------|
| Seguidores | — | — |
| Views médias/vídeo | — | — |
| Completion rate médio | — | >50% |
| % FYP | — | >60% |
| Likes/views | — | >3% |
| Shares/views | — | >1% |

> Preencher após primeira coleta

## Anatomia de um Vídeo TikTok que Performa

### Primeiros 3 segundos (CRÍTICO)
- Hook visual ou verbal imediato
- Sem intro genérica ("olá, sejam bem vindos...")
- Texto na tela nos primeiros frames

### 4–30 segundos
- Conteúdo principal
- Ritmo rápido, cortes frequentes
- Legendas/textos na tela

### Últimos segundos
- CTA claro (curtir, comentar, seguir, visitar site)
- Loop: final que remete ao início → aumenta replays

## Edge Cases

### TikTok Business API vs. Creator API
- **Business API**: acesso a métricas de conta comercial
- **Creator API**: acesso a dados pessoais de creator
- Verificar qual tipo de conta a Moper usa antes de configurar

### Token expirado (HTTP 401)
Tokens TikTok expiram em 24h (access) e 30 dias (refresh).
**Fix**: Script renova automaticamente via refresh token se `MOPER_TIKTOK_REFRESH_TOKEN` estiver no .env

### Vídeo em processamento
Vídeos recém publicados podem não ter métricas por até 2h.
Script ignora vídeos com menos de 2h de publicação.

### API em sandbox (dados mockados)
Se `APP_ENV=development` no .env, a API TikTok retorna dados de sandbox.
Mudar para `production` após aprovação do app pela TikTok.

## Outputs
- `.tmp/moper/tiktok_<YYYYMMDD>.json` — dados brutos
- Métricas em `metrics` (PostgreSQL), `platform = 'tiktok'`, `client = 'moper'`
- Seção TikTok no relatório mensal

## Ferramentas
- `execution/fetchTikTokMetrics.py`
- `execution/analyzeVideoPerformance.py`

## Atualizar Este Directive Quando
- TikTok mudar política de API (comum!)
- Mudança na estratégia de conteúdo
- Benchmarks forem estabelecidos após coleta
- Conta for verificada / receber badge

---
**Última atualização**: 2026-04-06
**API**: TikTok Business API v2
**Atenção**: TikTok muda APIs frequentemente — verificar changelog antes de executar
**Status**: Aguardando MOPER_TIKTOK_ACCESS_TOKEN no .env
