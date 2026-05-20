# Plano — Redes Sociais
_Atualizado em: 2026-04-21_

> **Adaptação de tags para este projeto (sem frontend):**
> `[0]` planejado · `[1-S]` diretiva/schema criados · `[2-E]` script existe ·
> `[3-H]` credenciais no .env (pronto para rodar) · `[4-C]` executado com dado real ·
> `[5-T]` pipeline completo testado nesta sessão (coleta → DB → relatório)

---

## Frente: Infraestrutura Core

- cancelado — SSH → VPS descartado, substituído por Neon
- `[5-T]` ✅ Banco Neon PostgreSQL — `DATABASE_URL` configurado, schema aplicado, pipeline testado
- `[5-T]` ✅ Schema do banco aplicado — `execution/setupDatabase.py` rodado, 4 tabelas criadas
- `[5-T]` ✅ Teste de conexões — `execution/testConnections.py` OK (Neon connected)
- `[2-E]` Backup manual — `execution/manualBackup.py` + arquivo `.tmp/manual_backup/moacir_manual_data.json` existe

---

## Frente: Autenticação / Tokens

- `[3-H]` Meta OAuth (Instagram + Facebook) — `execution/generateMetaToken.py` + tokens no .env
- `[3-H]` TikTok OAuth — `execution/generateTikTokToken.py` + tokens no .env
- `[3-H]` YouTube OAuth — `execution/generateYouTubeToken.py` + API keys no .env
- `[2-E]` Verificar elegibilidade TikTok — `execution/checkTikTokEligibility.py` (problema histórico com conta)

---

## Frente: Coleta de Dados (Global)

- `[5-T]` ✅ Fetch Instagram + save — `execution/fetchInstagramData.py --save` → dados no Neon confirmados
- `[2-E]` Fetch YouTube — não há script global, apenas por cliente
- `[2-E]` Monitor e Alertas — `execution/monitorAndAlert.py` + `alertSystem.py` + `performanceMonitor.py`

---

## Frente: Cliente — moacir

- `[5-T]` ✅ Coleta Instagram — `execution/fetchInstagramData.py --save` → dados salvos no Neon (2026-04-22)
- `[3-H]` Coleta TikTok — `clients/moacir/execution/fetchTikTokMetrics.py` + tokens no .env
- `[3-H]` Coleta YouTube — `clients/moacir/execution/fetchYouTubeMetrics.py` + API key no .env
- `[2-E]` Análise de vídeo — `clients/moacir/execution/analyzeVideoPerformance.py`
- `[2-E]` Relatório mensal — `clients/moacir/execution/generateMonthlyReport.py`
- `[1-S]` Plano de crescimento — `clients/moacir/directives/avaliacao_e_plano_crescimento.md`

---

## Frente: Cliente — espaco-laika

- `[3-H]` Coleta Instagram — `clients/espaco-laika/execution/fetchInstagramMetrics.py` + tokens no .env
- `[3-H]` Coleta TikTok — `clients/espaco-laika/execution/fetchTikTokMetrics.py` + tokens no .env
- `[3-H]` Coleta YouTube — `clients/espaco-laika/execution/fetchYouTubeMetrics.py` + API key no .env
- `[2-E]` Análise de vídeo — `clients/espaco-laika/execution/analyzeVideoPerformance.py`
- `[2-E]` Relatório mensal — `clients/espaco-laika/execution/generateMonthlyReport.py`
- `[1-S]` Website Espaço Laika — `clients/espaco-laika/website/index.html` (static site, melhorias planejadas)

---

## Frente: Cliente — namasa

- `[3-H]` Coleta Instagram — `clients/namasa/execution/fetchInstagramMetrics.py` + tokens no .env
- `[3-H]` Coleta TikTok — `clients/namasa/execution/fetchTikTokMetrics.py` + tokens no .env
- `[3-H]` Coleta YouTube — `clients/namasa/execution/fetchYouTubeMetrics.py` + API key no .env
- `[2-E]` Análise de vídeo — `clients/namasa/execution/analyzeVideoPerformance.py`
- `[2-E]` Relatório mensal — `clients/namasa/execution/generateMonthlyReport.py`

---

## Frente: Cliente — moper-maquinas

- `[3-H]` Coleta Instagram — `clients/moper-maquinas/execution/fetchInstagramMetrics.py` + tokens no .env
- `[3-H]` Coleta TikTok — `clients/moper-maquinas/execution/fetchTikTokMetrics.py` + tokens no .env
- `[3-H]` Coleta YouTube — `clients/moper-maquinas/execution/fetchYouTubeMetrics.py` + API key no .env
- `[2-E]` Análise de vídeo — `clients/moper-maquinas/execution/analyzeVideoPerformance.py`
- `[2-E]` Relatório mensal — `clients/moper-maquinas/execution/generateMonthlyReport.py`

---

## Frente: Automação e Agendamento

- `[0]` Agendamento via cron — monitorAndAlert.py preparado mas sem cron configurado
- `[0]` Publicação automática de posts — não iniciado
- `[0]` Dashboard unificado (todos os clientes) — não iniciado
- `[0]` Relatório automático enviado por e-mail — não iniciado
