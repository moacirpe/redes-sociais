# CLAUDE.md — Moper Máquinas

## Perfil do Cliente
**Empresa**: Moper Máquinas
**Segmento**: Máquinas e equipamentos
**Tom de voz**: Técnico, confiável, próximo ao cliente

## Plataformas Monitoradas
| Plataforma | Foco | Frequência de coleta |
|------------|------|----------------------|
| Instagram  | Engajamento, reels, stories | Diário |
| YouTube    | Vídeos técnicos, tutoriais | Semanal |
| TikTok     | Alcance, vídeos virais | Diário |

## KPIs Prioritários
- **Engajamento**: likes + comentários + compartilhamentos / alcance
- **Retenção de vídeo**: % do vídeo assistido (YouTube/TikTok)
- **Crescimento**: seguidores mês a mês
- **Melhor horário**: horários com maior engajamento

## Estrutura de Arquivos
```
clients/moper-maquinas/
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
- Salve dados brutos em `.tmp/moper/`
- Relatórios finais vão em `reports/<ano>-<mes>/`
- Atualize métricas de referência (benchmarks) no directive após cada coleta

## Benchmarks Atuais
> Preencher após primeira coleta

| Métrica | Instagram | YouTube | TikTok |
|---------|-----------|---------|--------|
| Seguidores | — | — | — |
| Taxa de engajamento | — | — | — |
| Alcance médio/post | — | — | — |
| Views médias/vídeo | — | — | — |

**Última atualização**: 2026-04-06
