# API Audit — Redes Sociais
_Atualizado em: 2026-04-21_

> Este projeto não tem frontend, então não há dados mock vs reais na UI.
> O audit aqui cobre: quais scripts foram executados com dados reais vs apenas configurados vs não iniciados.

---

## Legenda

| Status | Significado |
|--------|-------------|
| ✅ real | Script rodou e retornou dados reais da API |
| ⚠️ pronto | Credenciais configuradas, script existe, mas não foi testado nesta sessão |
| ❌ não testado | Script existe mas sem credenciais ou com problema conhecido |
| 🔴 não iniciado | Funcionalidade planejada, sem script |

---

## Conexões de Infraestrutura

| Conexão | Status | Observação | Próximo passo |
|---------|--------|------------|---------------|
| SSH → VPS | ⚠️ pronto | Creds no .env, não testado nesta sessão | Rodar `testConnections.py` |
| PostgreSQL via SSH | ⚠️ pronto | Schema definido, não confirmado no DB real | Rodar `setupDatabase.py` |
| Docker Swarm (Portainer) | ⚠️ pronto | Creds no .env, não testado | Rodar `testConnections.py` |

---

## APIs de Plataformas

| Plataforma | Script | Status | Observação | Próximo passo |
|------------|--------|--------|------------|---------------|
| Meta/Instagram OAuth | `generateMetaToken.py` | ✅ real | Tokens gerados, salvos no .env | Verificar expiração (60 dias) |
| Instagram Graph API | `fetchInstagramData.py` | ✅ real | Backup de dados moacir existe | Confirmar outros clientes |
| TikTok OAuth | `generateTikTokToken.py` | ✅ real | Tokens no .env para todos os clientes | Verificar expiração |
| TikTok API | scripts por cliente | ⚠️ pronto | Tokens configurados, coleta não confirmada | Rodar `fetchTikTokMetrics.py` |
| YouTube Data API | `generateYouTubeToken.py` | ⚠️ pronto | API keys no .env, OAuth não confirmado | Seguir `YOUTUBE_SETUP.md` |
| YouTube Analytics | scripts por cliente | ⚠️ pronto | Depende do OAuth estar completo | Completar OAuth primeiro |
| Facebook Graph API | via Meta token | ⚠️ pronto | Mesmo token do Instagram | Testar isoladamente |

---

## Coleta por Cliente

| Cliente | Instagram | TikTok | YouTube | Relatório |
|---------|-----------|--------|---------|-----------|
| moacir | ✅ real | ⚠️ pronto | ⚠️ pronto | ❌ não testado |
| espaco-laika | ⚠️ pronto | ❌ não testado | ⚠️ pronto | ❌ não testado |
| namasa | ⚠️ pronto | ❌ não testado | ⚠️ pronto | ❌ não testado |
| moper-maquinas | ⚠️ pronto | ❌ não testado | ⚠️ pronto | ❌ não testado |

> TikTok marcado como "não testado" em clientes além de moacir porque houve problemas históricos com conta Business (ver `directives/troubleshoot_tiktok_account.md`)

---

## Prioridade para Avançar

1. **Rodar `testConnections.py`** — confirmar SSH + PostgreSQL funcionando (30 min)
2. **Rodar `setupDatabase.py`** — criar schema no DB real (10 min, depende do #1)
3. **Rodar `fetchInstagramData.py --save` para cada cliente** — confirmar tokens válidos (20 min)
4. **Completar YouTube OAuth** — seguir `YOUTUBE_SETUP.md` (30 min)
5. **Rodar `fetchTikTokMetrics.py` para cada cliente** — validar tokens TikTok (20 min)
6. **Rodar `generateMonthlyReport.py` para moacir** — primeiro relatório completo (depende de tudo acima)
