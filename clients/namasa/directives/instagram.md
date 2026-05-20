# Directive: Instagram — Namasa (Espiritualidade)

## Objetivo
Monitorar a ressonância do conteúdo espiritual da Namasa no Instagram. O foco não é volume — é **profundidade de conexão**: saves, compartilhamentos e comentários genuínos são os sinais mais importantes.

## Credenciais (.env)
```
NAMASA_INSTAGRAM_TOKEN=
NAMASA_INSTAGRAM_ACCOUNT_ID=
```

## Métricas a Coletar

### Conta (diário)
- Seguidores totais e variação
- Alcance (contas únicas)
- Visitas ao perfil
- Cliques no link da bio

### Por Post
- Tipo: foto, carrossel, reels
- **Saves** ← métrica principal para conteúdo espiritual
- **Compartilhamentos** ← conteúdo que a pessoa quer passar adiante
- Likes e comentários
- Alcance e impressões
- Taxa de engajamento: (likes + comentários + shares + saves) / alcance
- Para Reels: plays, tempo médio assistido

### Análise por Tipo de Conteúdo
Identificar qual formato ressoa mais:
- Frases / citações (foto ou carrossel)
- Reflexões escritas (carrossel longo)
- Meditações guiadas em vídeo (Reels)
- Conteúdo de natureza / silêncio / contemplação

## Processo

### Step 1: Coleta diária
```bash
python clients/namasa/execution/fetchInstagramMetrics.py --save
```

### Step 2: Análise semanal
```bash
python clients/namasa/execution/analyzeVideoPerformance.py --platform instagram
```

Gera:
- Top 5 posts por **saves** (conteúdo de maior valor percebido)
- Top 5 posts por **compartilhamentos** (conteúdo que toca e é passado adiante)
- Top 5 posts por engajamento total
- Top Reels por plays e tempo assistido
- Análise de tipo de conteúdo (qual formato gera mais saves)

## Interpretação dos Dados — Contexto Espiritual

| Métrica | O que significa no contexto da Namasa |
|---------|--------------------------------------|
| Alto save | Conteúdo de valor duradouro — a pessoa quer revisitar |
| Alto compartilhamento | Conteúdo que toca, que a pessoa quer oferecer a alguém |
| Comentário longo | Conexão genuína — mais valioso que 10 likes |
| Alto alcance, baixo save | Conteúdo atraente mas superficial — recalibrar profundidade |
| Baixo alcance, alto save | Conteúdo de nicho mas altamente relevante — continuar |

## Edge Cases

### Token expirado (HTTP 401)
**Fix**: Meta Business Suite → Tokens → Atualizar (válido 60 dias)

### Conta não configurada como Business
**Fix**: Instagram → Configurações → Tipo de conta → Conta Profissional

### Rate limit (HTTP 429)
Retentativa automática até 3x. Se persistir, aguardar 1h.

## Outputs
- `.tmp/namasa/instagram_<YYYYMMDD>.json`
- Métricas em `metrics` PostgreSQL: `client = 'namasa'`, `platform = 'instagram'`
- Seção Instagram no relatório mensal

## Atualizar Quando
- Benchmarks de saves/shares forem estabelecidos
- Novo formato de conteúdo for adicionado
- Estratégia de publicação mudar

---
**Última atualização**: 2026-04-06
**Contexto**: Marca espiritual — priorizar saves e compartilhamentos sobre volume
**Status**: Aguardando credenciais no .env
