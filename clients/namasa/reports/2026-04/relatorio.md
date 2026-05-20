# Relatório Mensal — Namasa — 2026-04

**Status**: Aguardando primeira coleta de dados

```bash
python clients/namasa/execution/fetchInstagramMetrics.py --save
python clients/namasa/execution/fetchYouTubeMetrics.py --save
python clients/namasa/execution/fetchTikTokMetrics.py --save
python clients/namasa/execution/generateMonthlyReport.py --month 2026-04
```

## Credenciais necessárias no .env
- [ ] `NAMASA_INSTAGRAM_TOKEN`
- [ ] `NAMASA_INSTAGRAM_ACCOUNT_ID`
- [ ] `NAMASA_YOUTUBE_API_KEY`
- [ ] `NAMASA_YOUTUBE_CHANNEL_ID`
- [ ] `NAMASA_TIKTOK_ACCESS_TOKEN`
- [ ] `NAMASA_TIKTOK_OPEN_ID`
