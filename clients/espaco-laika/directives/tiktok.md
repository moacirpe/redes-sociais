# Directive: TikTok — Espaço Laika

## Objetivo
Monitorar viralização, completion rate e crescimento de audiência no TikTok do Espaço Laika. Identificar conteúdo que ressoa com a comunidade e padrões de formato que o algoritmo favorece.

## Credenciais Necessárias (.env)
```
LAIKA_TIKTOK_ACCESS_TOKEN=
LAIKA_TIKTOK_OPEN_ID=
LAIKA_TIKTOK_REFRESH_TOKEN=
```

## Métricas a Coletar

### Conta (diário)
- Seguidores totais e variação
- Likes totais da conta
- Vídeos publicados no período
- Visualizações totais

### Por Vídeo
- Views, plays únicos, likes, comentários, compartilhamentos
- Tempo médio de visualização (segundos)
- **Completion rate** = % que assistiu até o final (métrica mais importante)
- Fonte de tráfego: FYP, seguindo, busca, hashtag, som, perfil
- Novos seguidores gerados pelo vídeo
- Taxa de curtidas por 100 views

### Sons e Hashtags
- Sons usados em cada vídeo
- Posição de tendência do som no momento da postagem
- Hashtags com melhor alcance por vídeo

## Processo de Coleta

### Step 1: Coletar dados diariamente
```bash
python clients/espaco-laika/execution/fetchTikTokMetrics.py --save
```

### Step 2: Análise de performance
```bash
python clients/espaco-laika/execution/analyzeVideoPerformance.py --platform tiktok
```

Identifica:
- Top 5 por views
- Top 5 por completion rate
- Vídeos que trouxeram pico de seguidores
- Padrão de duração dos melhores vídeos
- Sons em alta usados em vídeos de sucesso

### Step 3: Análise de tendências (semanal)
- Auditar FYP do nicho manualmente
- Registrar sons em alta relevantes para Espaço Laika
- Identificar formatos virais para adaptar

## Sinais de Qualidade do Algoritmo TikTok

| Sinal | Peso | Meta Espaço Laika |
|-------|------|-------------------|
| Completion rate | ⭐⭐⭐⭐⭐ | >60% |
| Shares | ⭐⭐⭐⭐ | >1% das views |
| Comments | ⭐⭐⭐ | >0.5% das views |
| Likes | ⭐⭐ | >5% das views |
| Replays | ⭐⭐ | — |
| Follows from video | ⭐ | — |

## Anatomia do Vídeo Ideal — Espaço Laika

### Hook (0–3s): capturar atenção
- Cena impactante ou pergunta direta
- Texto grande na tela

### Desenvolvimento (4–25s): entregar valor
- Conteúdo relevante, bem editado
- Ritmo dinâmico com cortes rápidos
- Músicas em tendência ou som original

### Fechamento (últimos 3s): ação
- CTA claro: "segue pra mais", "comenta aqui", "compartilha com..."
- Loop sutil para incentivar replay

## Edge Cases

### Token expirado (access token: 24h)
**Fix**: Script renova automaticamente via `LAIKA_TIKTOK_REFRESH_TOKEN` (válido 30 dias).
Se refresh também expirar: reconectar conta no TikTok Business Center.

### API retorna dados de sandbox
**Causa**: App TikTok ainda em modo sandbox (não aprovado)
**Fix**: Submeter app para revisão no TikTok Developer Portal.
Dados de sandbox são fictícios — não usar para relatórios.

### Vídeo removido ou privado
Script ignora automaticamente e registra no log de execução.

### Sem dados de completion rate
Disponível apenas para contas Business verificadas com volume mínimo.
**Fix**: Verificar status da conta no TikTok Business Center.

## Outputs
- `.tmp/laika/tiktok_<YYYYMMDD>.json`
- Métricas em `metrics`: `client = 'laika'`, `platform = 'tiktok'`
- Seção TikTok no relatório mensal

## Ferramentas
- `execution/fetchTikTokMetrics.py`
- `execution/analyzeVideoPerformance.py`

---
**Última atualização**: 2026-04-06
**API**: TikTok Business API v2
**Atenção**: TikTok altera APIs com frequência. Verificar changelog antes de executar.
**Status**: Aguardando LAIKA_TIKTOK_ACCESS_TOKEN no .env
