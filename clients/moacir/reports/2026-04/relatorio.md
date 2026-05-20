# Relatório Mensal — Moacir Pereira — 2026-04

**Status**: Aguardando primeira coleta de dados

```bash
python clients/moacir/execution/fetchInstagramMetrics.py --save
python clients/moacir/execution/fetchYouTubeMetrics.py --save
python clients/moacir/execution/fetchTikTokMetrics.py --save
python clients/moacir/execution/generateMonthlyReport.py --month 2026-04
```

## Credenciais necessárias no .env
- [ ] `MOACIR_INSTAGRAM_TOKEN`
- [ ] `MOACIR_INSTAGRAM_ACCOUNT_ID`
- [ ] `MOACIR_YOUTUBE_API_KEY`
- [ ] `MOACIR_YOUTUBE_CHANNEL_ID`
- [ ] `MOACIR_TIKTOK_ACCESS_TOKEN`
- [ ] `MOACIR_TIKTOK_OPEN_ID`
