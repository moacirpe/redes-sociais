# Relatório Mensal de Redes Sociais
## Moper Máquinas — 2026-04

**Status**: Aguardando primeira coleta de dados

---

Para gerar este relatório com dados reais:

```bash
# 1. Coletar dados de todas as plataformas
python clients/moper-maquinas/execution/fetchInstagramMetrics.py --save
python clients/moper-maquinas/execution/fetchYouTubeMetrics.py --save
python clients/moper-maquinas/execution/fetchTikTokMetrics.py --save

# 2. Gerar relatório consolidado
python clients/moper-maquinas/execution/generateMonthlyReport.py --month 2026-04
```

## Checklist de Credenciais Necessárias

- [ ] `MOPER_INSTAGRAM_TOKEN` no `.env`
- [ ] `MOPER_INSTAGRAM_ACCOUNT_ID` no `.env`
- [ ] `MOPER_YOUTUBE_API_KEY` no `.env`
- [ ] `MOPER_YOUTUBE_CHANNEL_ID` no `.env`
- [ ] `MOPER_TIKTOK_ACCESS_TOKEN` no `.env`
- [ ] `MOPER_TIKTOK_OPEN_ID` no `.env`
