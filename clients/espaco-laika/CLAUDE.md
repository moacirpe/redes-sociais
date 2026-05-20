# CLAUDE.md — Espaço Laika

## Perfil do Cliente
**Empresa**: Espaço Laika
**Segmento**: [Descrever segmento — pet shop, espaço cultural, coworking, etc.]
**Tom de voz**: Descontraído, criativo, próximo à comunidade

## Plataformas Monitoradas
| Plataforma | Foco | Frequência de coleta |
|------------|------|----------------------|
| Instagram  | Engajamento, reels, comunidade | Diário |
| YouTube    | Vídeos longos, vlogs | Semanal |
| TikTok     | Viralização, trends | Diário |

## KPIs Prioritários
- **Engajamento**: likes + comentários + compartilhamentos / alcance
- **Retenção de vídeo**: % do vídeo assistido (YouTube/TikTok)
- **Crescimento de comunidade**: seguidores + saves + compartilhamentos
- **Conteúdo de melhor performance**: top 5 posts por mês

## Estrutura de Arquivos
```
clients/espaco-laika/
├── CLAUDE.md              ← este arquivo
├── directives/            ← estratégias por plataforma
│   ├── instagram.md
│   ├── youtube.md
│   └── tiktok.md
├── execution/             ← scripts Python
│   ├── fetchInstagramMetrics.py
│   ├── fetchYouTubeMetrics.py
│   ├── fetchTikTokMetrics.py
│   ├── analyzeVideoPerformance.py
│   └── generateMonthlyReport.py
└── reports/               ← relatórios mensais
    └── 2026-04/
```

## Operação
- Leia sempre o directive da plataforma antes de executar coleta
- Salve dados brutos em `.tmp/laika/`
- Relatórios finais vão em `reports/<ano>-<mes>/`
- Atualize benchmarks no directive após cada coleta

## Benchmarks Atuais
> Preencher após primeira coleta

| Métrica | Instagram | YouTube | TikTok |
|---------|-----------|---------|--------|
| Seguidores | — | — | — |
| Taxa de engajamento | — | — | — |
| Alcance médio/post | — | — | — |
| Views médias/vídeo | — | — | — |

**Última atualização**: 2026-04-06
