# Directive: Instagram — Moacir (Pessoal)

## Objetivo
Monitorar crescimento de marca pessoal, engajamento e performance de conteúdo no Instagram do Moacir. Foco em identificar quais formatos e temas geram mais autoridade e seguidores.

## Credenciais (.env)
```
MOACIR_INSTAGRAM_TOKEN=
MOACIR_INSTAGRAM_ACCOUNT_ID=
```

## Métricas a Coletar

### Conta (diário)
- Seguidores totais e variação diária
- Alcance (contas únicas)
- Impressões totais
- Visitas ao perfil
- Cliques no link da bio

### Por Post
- Tipo: foto, carrossel, reels
- Likes, comentários, compartilhamentos, saves
- Alcance e impressões
- Taxa de engajamento: (likes + comentários + shares + saves) / alcance
- Para Reels: plays, plays únicos

### Análise de Marca Pessoal
- Posts sobre bastidores vs. conteúdo educativo vs. pessoal
- Qual tema gera mais saves (conteúdo de valor)
- Qual tema gera mais compartilhamentos (identificação)
- Quais comentários aparecem com mais frequência (sinal de audiência)

## Processo

### Step 1: Coleta diária
```bash
python clients/moacir/execution/fetchInstagramMetrics.py --save
```

### Step 2: Análise semanal
```bash
python clients/moacir/execution/analyzeVideoPerformance.py --platform instagram
```

Gera:
- Top 5 posts por engajamento
- Top 5 Reels por plays
- Top 5 por saves
- Horários de maior engajamento

## Edge Cases

### Token expirado (HTTP 401)
Tokens expiram em 60 dias.
**Fix**: Meta Business Suite → Configurações → Tokens → Atualizar

### Conta não-Business
**Fix**: Instagram → Configurações → Tipo de conta → Conta Profissional

### Rate limit (HTTP 429)
Retentativa automática até 3x. Se persistir, aguardar 1h.

## Outputs
- `.tmp/moacir/instagram_<YYYYMMDD>.json`
- Métricas em `metrics` PostgreSQL: `client = 'moacir'`, `platform = 'instagram'`
- Relatório mensal em `reports/<ano>-<mes>/`

## Atualizar Quando
- Benchmarks forem estabelecidos após primeira coleta
- Estratégia de conteúdo mudar
- API do Instagram mudar versão

---
**Última atualização**: 2026-04-06
**Status**: Aguardando credenciais no .env
