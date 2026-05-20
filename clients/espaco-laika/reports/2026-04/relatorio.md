# Relatório Mensal de Redes Sociais
## Espaço Laika — 2026-04

**Status**: Aguardando primeira coleta de dados

---

Para gerar este relatório com dados reais:

```bash
# 1. Coletar dados de todas as plataformas
python clients/espaco-laika/execution/fetchInstagramMetrics.py --save
python clients/espaco-laika/execution/fetchYouTubeMetrics.py --save
python clients/espaco-laika/execution/fetchTikTokMetrics.py --save

# 2. Gerar relatório consolidado
python clients/espaco-laika/execution/generateMonthlyReport.py --month 2026-04
```

## Checklist de Credenciais Necessárias

- [ ] `LAIKA_INSTAGRAM_TOKEN` no `.env`
- [ ] `LAIKA_INSTAGRAM_ACCOUNT_ID` no `.env`
- [ ] `LAIKA_YOUTUBE_API_KEY` no `.env`
- [ ] `LAIKA_YOUTUBE_CHANNEL_ID` no `.env`
- [ ] `LAIKA_TIKTOK_ACCESS_TOKEN` no `.env`
- [ ] `LAIKA_TIKTOK_OPEN_ID` no `.env`
