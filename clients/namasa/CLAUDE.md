# CLAUDE.md — Namasa

## Perfil do Cliente
**Marca**: Namasa
**Segmento**: Espiritualidade
**Tom de voz**: Sereno, acolhedor, profundo, sem jargões religiosos dogmáticos
**Público**: Pessoas em busca de autoconhecimento, espiritualidade, bem-estar interior

## Contexto de Conteúdo
A Namasa não é uma marca comercial — é uma marca espiritual.
O objetivo das redes sociais **não é vender**, é **conectar, inspirar e acolher**.

Métricas de sucesso aqui têm um peso diferente:
- **Saves** > likes → conteúdo que as pessoas guardam para revisitar (reflexões, frases, ensinamentos)
- **Compartilhamentos** → conteúdo que toca e que a pessoa quer passar adiante
- **Comentários** → conexão genuína, não volume
- **Alcance orgânico** → crescimento natural por ressonância, não por viralização forçada

## Plataformas Monitoradas
| Plataforma | Foco | Frequência |
|------------|------|------------|
| Instagram  | Reflexões, frases, Reels contemplativos | Diário |
| YouTube    | Conteúdo longo: meditações, ensinamentos, conversas | Semanal |
| TikTok     | Alcance orgânico com conteúdo breve e reflexivo | Diário |

## KPIs Prioritários (ordem de importância)
1. **Saves por post** — conteúdo que as pessoas querem guardar
2. **Compartilhamentos** — conteúdo que inspira a pessoa a compartilhar com alguém
3. **Engajamento qualitativo** — comentários com reflexão, não apenas emojis
4. **Watch time** (YouTube) — pessoas que ficam até o fim de meditações/ensinamentos
5. **Completion rate** (TikTok) — vídeos assistidos até o fim
6. **Crescimento orgânico de seguidores** — sem ads, crescimento por ressonância

## Credenciais (.env)
```
NAMASA_INSTAGRAM_TOKEN=
NAMASA_INSTAGRAM_ACCOUNT_ID=
NAMASA_YOUTUBE_API_KEY=
NAMASA_YOUTUBE_CHANNEL_ID=
NAMASA_TIKTOK_ACCESS_TOKEN=
NAMASA_TIKTOK_OPEN_ID=
NAMASA_TIKTOK_REFRESH_TOKEN=
```

## Estrutura
```
clients/namasa/
├── CLAUDE.md
├── directives/
│   ├── instagram.md
│   ├── youtube.md
│   └── tiktok.md
├── execution/
│   ├── fetchInstagramMetrics.py
│   ├── fetchYouTubeMetrics.py
│   ├── fetchTikTokMetrics.py
│   ├── analyzeVideoPerformance.py
│   └── generateMonthlyReport.py
└── reports/
    └── 2026-04/
```

## Benchmarks Atuais
> Preencher após primeira coleta

| Métrica | Instagram | YouTube | TikTok |
|---------|-----------|---------|--------|
| Seguidores | — | — | — |
| Saves médios/post | — | — | — |
| Compartilhamentos médios | — | — | — |
| Engajamento médio | — | — | — |
| Watch time médio (YT) | — | — | — |
| Completion rate médio (TT) | — | — | — |

## Nota Importante para Análise
Ao gerar relatórios ou análises para a Namasa, **não usar linguagem de marketing agressivo**.
Recomendações devem ser orientadas a **profundidade e autenticidade**, não a volume ou viralidade.
Ex: "aumentar saves criando conteúdo de reflexão mais denso" — não "postar mais para crescer rápido".

**Última atualização**: 2026-04-06
