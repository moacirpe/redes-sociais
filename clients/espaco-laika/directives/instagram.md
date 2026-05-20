# Directive: Instagram — Espaço Laika

## Objetivo
Monitorar engajamento, crescimento de comunidade e performance de conteúdo criativo no Instagram do Espaço Laika. Foco em Reels, saves e compartilhamentos como indicadores de conteúdo com alto valor percebido.

## Credenciais Necessárias (.env)
```
LAIKA_INSTAGRAM_TOKEN=
LAIKA_INSTAGRAM_ACCOUNT_ID=
```

## Métricas a Coletar

### Conta (diário)
- Seguidores totais e variação diária
- Alcance (contas únicas alcançadas)
- Impressões totais
- Visitas ao perfil
- Cliques no link da bio
- Contas com engajamento

### Por Post
- Tipo: foto, carrossel, reels, collab
- Likes, comentários, compartilhamentos, **saves** (saves = indicador de valor)
- Alcance e impressões
- Taxa de engajamento completa: (likes + comentários + shares + saves) / alcance
- Para Reels: plays, plays únicos, retenção

### Stories
- Visualizações por frame
- Respostas e reações
- Cliques em links e stickers
- Saídas (% que abandona = story perdendo atenção)

## Processo de Coleta

### Step 1: Coletar dados
```bash
python clients/espaco-laika/execution/fetchInstagramMetrics.py --save
```

### Step 2: Análise semanal de Reels
```bash
python clients/espaco-laika/execution/analyzeVideoPerformance.py --platform instagram
```

Identifica:
- Top 5 Reels por plays
- Top 5 posts por saves (conteúdo de referência para o público)
- Top 5 posts por compartilhamentos (conteúdo viral)
- Horários de maior engajamento
- Hashtags que geraram mais alcance

## Estratégia de Conteúdo — Referência

### Conteúdo que gera Saves (repositório)
- Dicas práticas relacionadas ao segmento
- Checklists visuais
- "Guia de..."
- Infográficos

### Conteúdo que gera Compartilhamentos
- Humor relacionado ao nicho
- Conteúdo emocional / identificação
- Novidades e tendências

### Conteúdo que gera Comentários
- Perguntas abertas
- Polêmicas saudáveis do nicho
- Enquetes na legenda

## Benchmarks

| Métrica | Valor Atual | Meta |
|---------|-------------|------|
| Seguidores | — | — |
| Engajamento médio | — | >3% |
| Alcance médio/post | — | — |
| Saves médios/post | — | — |
| Plays médios/Reels | — | — |

> Preencher após primeira coleta

## Melhores Horários (a descobrir)
> Preencher com dados de insights de audiência

## Edge Cases

### Token expirado (HTTP 401)
**Fix**: Meta Business Suite → Configurações → Tokens → Atualizar
Tokens de longa duração válidos por 60 dias.

### Conta não classificada como Business
**Fix**: Instagram → Configurações → Tipo de conta → Conta profissional

### Rate limit (HTTP 429)
Retentativa automática até 3x. Se persistir, aguardar 1h.

## Outputs
- `.tmp/laika/instagram_<YYYYMMDD>.json`
- Métricas em `metrics` (PostgreSQL): `client = 'laika'`, `platform = 'instagram'`
- Incluído no relatório mensal em `reports/<ano>-<mes>/`

## Ferramentas
- `execution/fetchInstagramMetrics.py`
- `execution/analyzeVideoPerformance.py`

---
**Última atualização**: 2026-04-06
**API**: Instagram Graph API v19.0
**Status**: Aguardando credenciais no .env
