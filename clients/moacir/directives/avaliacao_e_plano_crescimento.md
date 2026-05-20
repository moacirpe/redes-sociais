# Directive: Avaliação e Plano de Crescimento — Moacir (@moacir.moper)

## Objetivo
Avaliar o estado atual das redes sociais do Moacir para criar um plano estratégico de crescimento, visando aumentar o engajamento e atingir 10.000 seguidores em 30 dias. Foco no perfil principal @moacir.moper.

## Contexto
- Perfil principal: @moacir.moper
- Alvo: 10.000 seguidores em 30 dias
- Foco: Aumento de engajamento e crescimento orgânico
- Plataformas: Instagram, TikTok, YouTube

## Credenciais Necessárias (.env)
```
MOACIR_INSTAGRAM_TOKEN=
MOACIR_INSTAGRAM_ACCOUNT_ID=
MOACIR_TIKTOK_ACCESS_TOKEN=
MOACIR_YOUTUBE_API_KEY=
MOACIR_YOUTUBE_CHANNEL_ID=
```

## Métricas Atuais a Avaliar

### Instagram
- Seguidores atuais
- Taxa de engajamento média
- Top posts por engajamento
- Frequência de postagem
- Horários de pico

### TikTok
- Seguidores atuais
- Views médias por vídeo
- Taxa de engajamento
- Vídeos virais vs. não virais
- Nicho de conteúdo

### YouTube
- Inscritos atuais
- Views totais e médias
- Tempo de watch médio
- CTR (Click-through rate)
- Canais similares

## Processo de Avaliação

### Step 1: Coleta de Dados Atuais
Coletar métricas das últimas 4 semanas de todas as plataformas.

```bash
# Instagram
python clients/moacir/execution/fetchInstagramMetrics.py --period 30d --save

# TikTok
python clients/moacir/execution/fetchTikTokMetrics.py --period 30d --save

# YouTube
python clients/moacir/execution/fetchYouTubeMetrics.py --period 30d --save
```

### Step 2: Análise de Performance
Analisar padrões de engajamento e crescimento.

```bash
python clients/moacir/execution/analyzeVideoPerformance.py --all-platforms --client moacir
```

Gera:
- Relatório de estado atual
- Análise SWOT das redes sociais
- Benchmarking com concorrentes similares

### Step 3: Plano de Crescimento 30 Dias
Com base na análise, criar plano estratégico.

**Objetivos por Plataforma:**
- Instagram: Foco em stories e reels diários
- TikTok: Conteúdo viral semanal
- YouTube: Vídeos longos semanais

**Estratégias:**
- Hashtags relevantes
- Colaborações
- Conteúdo de valor
- Engajamento com comunidade

## Plano de Execução 30 Dias

### Semana 1: Otimização e Consistência
- Postar diariamente em todas plataformas
- Otimizar perfis (bio, link, highlights)
- Identificar e replicar conteúdo de sucesso

### Semana 2: Aumento de Engajamento
- Responder todos comentários
- Criar conteúdo interativo (perguntas, polls)
- Usar trending hashtags

### Semana 3: Colaborações e Cross-Promotion
- Parcerias com influencers similares
- Cross-posting entre plataformas
- Giveaways e concursos

### Semana 4: Análise e Ajustes
- Monitorar crescimento diário
- Ajustar estratégia baseada em dados
- Foco em retenção de novos seguidores

## Métricas de Sucesso
- Seguidores: +10.000 (total alvo)
- Engajamento: +50% em todas plataformas
- Alcance orgânico: +100%
- Conversão perfil → seguidor: +30%

## Edge Cases

### Dados insuficientes
Se menos de 30 dias de histórico, focar em benchmarks da indústria.

### Plataforma sem conta
Pular plataforma e focar nas ativas.

### Rate limits
Usar retry automático e distribuir coletas ao longo do dia.

## Outputs
- Relatório de avaliação: `reports/<ano>-<mes>/avaliacao_redes_sociais.md`
- Plano de crescimento: `reports/<ano>-<mes>/plano_crescimento_30d.md`
- Dashboard de progresso: Atualização diária

## Atualizar Quando
- Após completar 30 dias
- Mudanças significativas no algoritmo das plataformas
- Novos objetivos estabelecidos

---
**Última atualização**: 2026-04-10
**Status**: Relatório gerado - Aguardando configuração de credenciais para coleta automática