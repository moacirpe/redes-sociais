# Directive: Instagram — Moper Máquinas

## Objetivo
Monitorar engajamento, alcance e crescimento de seguidores no Instagram da Moper Máquinas. Identificar os conteúdos de maior performance e os horários ideais de postagem.

## Credenciais Necessárias (.env)
```
MOPER_INSTAGRAM_TOKEN=
MOPER_INSTAGRAM_ACCOUNT_ID=
```

## Métricas a Coletar

### Conta (diário)
- Seguidores totais
- Contas alcançadas
- Impressões totais
- Visitas ao perfil
- Cliques no link da bio

### Por Post
- Tipo: foto, carrossel, reels
- Likes, comentários, compartilhamentos, saves
- Alcance e impressões
- Taxa de engajamento = (likes + comentários + shares + saves) / alcance
- Para Reels: plays, retenção média

### Stories (quando disponível via API)
- Visualizações
- Respostas
- Saídas e avanços

## Processo de Coleta

### Step 1: Executar script de coleta
```bash
python clients/moper-maquinas/execution/fetchInstagramMetrics.py --save
```

### Step 2: Verificar dados
- `status: success` no output
- Campos `followers`, `posts`, `insights` presentes
- Arquivo salvo em `.tmp/moper/instagram_<data>.json`

### Step 3: Análise de Reels (semanal)
```bash
python clients/moper-maquinas/execution/analyzeVideoPerformance.py --platform instagram
```

Identifica:
- Top 5 Reels por views
- Top 5 por taxa de engajamento
- Horário de maior performance
- Duração média dos Reels que performam melhor

## Análise de Conteúdo por Tipo

| Tipo | Benchmark Engajamento | Alcance Esperado |
|------|----------------------|-----------------|
| Foto | — | — |
| Carrossel | — | — |
| Reels | — | — |
| Stories | — | — |

> Preencher após primeira coleta com dados reais

## Melhores Horários (a descobrir)
> Preencher com dados coletados

## Edge Cases

### Token expirado (HTTP 401)
Tokens do Instagram expiram em 60 dias.
**Fix**: Regenerar em Meta Business Suite → Settings → Tokens → Refresh

### Sem dados de insights (HTTP 400)
**Causa**: Conta pessoal em vez de Business
**Fix**: Confirmar que conta está configurada como Business no Instagram

### Rate limit (HTTP 429)
Script retenta automaticamente até 3x com backoff.
Se persistir: aguardar 1 hora e re-executar.

## Outputs
- `.tmp/moper/instagram_<YYYYMMDD>.json` — dados brutos
- Métricas gravadas na tabela `metrics` do PostgreSQL (coluna `platform = 'instagram'`, `client = 'moper'`)
- Incluído no relatório mensal em `reports/<ano>-<mes>/`

## Ferramentas
- `execution/fetchInstagramMetrics.py`
- `execution/analyzeVideoPerformance.py`

## Atualizar Este Directive Quando
- Taxa de engajamento médio mudar significativamente (> ±20%)
- Novos tipos de conteúdo forem criados (ex: Collab posts)
- API do Instagram mudar versão ou campos disponíveis
- Benchmarks forem estabelecidos após primeira coleta

---
**Última atualização**: 2026-04-06
**API**: Instagram Graph API v19.0
**Status**: Aguardando credenciais no .env
