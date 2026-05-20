#!/usr/bin/env python3
"""
Generate Monthly Report — Moper Máquinas

Consolida dados do mês de todas as plataformas e gera
relatório em Markdown para a pasta reports/.

Uso:
    python clients/moper-maquinas/execution/generateMonthlyReport.py
    python clients/moper-maquinas/execution/generateMonthlyReport.py --month 2026-04
"""

import os
import sys
import json
import glob
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CLIENT      = "moper"
CLIENT_NAME = "Moper Máquinas"
TMP_DIR     = ".tmp/moper"
REPORTS_DIR = "clients/moper-maquinas/reports"


def loadFilesForMonth(platform: str, month: str) -> List[Dict]:
    """Carrega todos os arquivos JSON de uma plataforma no mês."""
    pattern = os.path.join(TMP_DIR, f"{platform}_{month.replace('-', '')}*.json")
    files   = sorted(glob.glob(pattern))
    data    = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            data.append(json.load(fh))
    return data


def loadLatestFile(platform: str) -> Optional[Dict]:
    """Carrega o arquivo mais recente de uma plataforma."""
    pattern = os.path.join(TMP_DIR, f"{platform}_*.json")
    files   = sorted(glob.glob(pattern), reverse=True)
    if not files:
        return None
    with open(files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def formatNumber(n) -> str:
    """Formata número com separadores."""
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return str(n) if n is not None else "—"


def formatPct(n) -> str:
    """Formata como porcentagem."""
    try:
        return f"{float(n) * 100:.1f}%"
    except Exception:
        return "—"


def buildInstagramSection(data: Optional[Dict]) -> str:
    if not data:
        return "## 📸 Instagram\n\n> Dados não disponíveis. Execute `fetchInstagramMetrics.py --save` primeiro.\n\n"

    profile  = data.get("profile", {})
    analysis = data.get("analysis", {})
    posts    = data.get("posts", [])
    reels    = [p for p in posts if p.get("media_type") == "VIDEO"]

    topPosts = analysis.get("top_by_engagement", [])[:3]
    topReels = analysis.get("top_reels_by_plays", [])[:3]

    lines = [
        "## 📸 Instagram\n",
        "### Visão Geral",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Seguidores | {formatNumber(profile.get('followers_count'))} |",
        f"| Posts no período | {len(posts)} |",
        f"| Reels no período | {len(reels)} |",
        f"| Engajamento médio | {formatPct(analysis.get('avg_engagement_rate'))} |",
        "",
        "### Top 3 Posts por Engajamento",
    ]

    for i, p in enumerate(topPosts, 1):
        caption = (p.get("caption") or "Sem legenda")[:60]
        lines.append(
            f"{i}. **{caption}...** — {formatPct(p.get('engagement_rate'))} engajamento "
            f"| {formatNumber(p.get('like_count'))} likes | {formatNumber(p.get('comments_count'))} comentários"
        )

    lines += ["", "### Top 3 Reels por Views"]
    for i, r in enumerate(topReels, 1):
        caption = (r.get("caption") or "Sem legenda")[:60]
        lines.append(
            f"{i}. **{caption}...** — {formatNumber(r.get('plays'))} plays"
        )

    lines += [""]
    return "\n".join(lines) + "\n"


def buildYouTubeSection(data: Optional[Dict]) -> str:
    if not data:
        return "## 🎬 YouTube\n\n> Dados não disponíveis. Execute `fetchYouTubeMetrics.py --save` primeiro.\n\n"

    channel  = data.get("channel", {})
    analysis = data.get("analysis", {})
    topViews = analysis.get("top_by_views", [])[:3]
    topEng   = analysis.get("top_by_engagement", [])[:3]

    lines = [
        "## 🎬 YouTube\n",
        "### Visão Geral do Canal",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Inscritos | {formatNumber(channel.get('subscribers'))} |",
        f"| Views totais | {formatNumber(channel.get('total_views'))} |",
        f"| Vídeos analisados | {analysis.get('videos_analyzed', '—')} |",
        f"| Views médias/vídeo | {formatNumber(analysis.get('avg_views'))} |",
        f"| Engajamento médio | {formatPct(analysis.get('avg_engagement_rate'))} |",
        "",
        "### Top 3 Vídeos por Views",
    ]

    for i, v in enumerate(topViews, 1):
        lines.append(
            f"{i}. [{v.get('title', 'Sem título')}]({v.get('url', '#')}) "
            f"— {formatNumber(v.get('views'))} views | {formatPct(v.get('engagement_rate'))} engajamento"
        )

    lines += ["", "### Top 3 por Engajamento"]
    for i, v in enumerate(topEng, 1):
        lines.append(
            f"{i}. [{v.get('title', 'Sem título')}]({v.get('url', '#')}) "
            f"— {formatPct(v.get('engagement_rate'))} | {formatNumber(v.get('views'))} views"
        )

    lines += [""]
    return "\n".join(lines) + "\n"


def buildTikTokSection(data: Optional[Dict]) -> str:
    if not data:
        return "## 🎵 TikTok\n\n> Dados não disponíveis. Execute `fetchTikTokMetrics.py --save` primeiro.\n\n"

    account  = data.get("account", {})
    analysis = data.get("analysis", {})
    topViews = analysis.get("top_by_views", [])[:3]
    topComp  = analysis.get("top_by_completion", [])[:3]

    lines = [
        "## 🎵 TikTok\n",
        "### Visão Geral da Conta",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Seguidores | {formatNumber(account.get('followers_count'))} |",
        f"| Vídeos analisados | {analysis.get('videos_analyzed', '—')} |",
        f"| Views médias/vídeo | {formatNumber(analysis.get('avg_views'))} |",
        f"| Completion rate médio | {formatPct(analysis.get('avg_completion_rate'))} |",
        f"| Engajamento médio | {formatPct(analysis.get('avg_engagement_rate'))} |",
        f"| Vídeos com tráfego FYP dominante | {analysis.get('fyp_videos_count', '—')} |",
        "",
        "### Top 3 Vídeos por Views",
    ]

    for i, v in enumerate(topViews, 1):
        lines.append(
            f"{i}. [{v.get('id', 'Video')}]({v.get('url', '#')}) "
            f"— {formatNumber(v.get('views'))} views | completion: {formatPct(v.get('completion_rate'))}"
        )

    lines += ["", "### Top 3 por Completion Rate"]
    for i, v in enumerate(topComp, 1):
        lines.append(
            f"{i}. [{v.get('id', 'Video')}]({v.get('url', '#')}) "
            f"— {formatPct(v.get('completion_rate'))} completion | {formatNumber(v.get('views'))} views"
        )

    lines += [""]
    return "\n".join(lines) + "\n"


def buildRecommendations(igData, ytData, ttData) -> str:
    recs = ["## 💡 Recomendações do Mês\n"]
    n    = 1

    # Instagram
    if igData:
        analysis = igData.get("analysis", {})
        eng = analysis.get("avg_engagement_rate", 0)
        if eng < 0.02:
            recs.append(f"{n}. **Instagram**: Engajamento médio de {formatPct(eng)} — testar formatos interativos (enquetes, perguntas nas stories, carrosséis com valor)")
            n += 1
        if analysis.get("total_reels", 0) < 4:
            recs.append(f"{n}. **Instagram**: Aumentar frequência de Reels — são priorizados pelo algoritmo para crescimento de alcance")
            n += 1

    # YouTube
    if ytData:
        analysis = ytData.get("analysis", {})
        if analysis.get("low_performance_count", 0) > 2:
            recs.append(f"{n}. **YouTube**: {analysis['low_performance_count']} vídeos com baixo CTR — revisar thumbnails e títulos para aumentar cliques")
            n += 1

    # TikTok
    if ttData:
        analysis = ttData.get("analysis", {})
        cr = analysis.get("avg_completion_rate", 0)
        if cr < 0.5:
            recs.append(f"{n}. **TikTok**: Completion rate médio de {formatPct(cr)} — reforçar hook nos primeiros 3 segundos e reduzir intro")
            n += 1
        if analysis.get("fyp_videos_count", 0) == 0:
            recs.append(f"{n}. **TikTok**: Nenhum vídeo com alcance dominante do FYP — usar sons em tendência e hashtags de nicho")
            n += 1

    if n == 1:
        recs.append("✅ Performance geral dentro do esperado. Manter estratégia atual e acompanhar benchmarks.")

    return "\n".join(recs) + "\n"


def generateReport(month: str) -> str:
    igData = loadLatestFile("instagram")
    ytData = loadLatestFile("youtube")
    ttData = loadLatestFile("tiktok")

    header = f"""# Relatório Mensal de Redes Sociais
## {CLIENT_NAME} — {month}

**Gerado em**: {datetime.utcnow().strftime("%d/%m/%Y às %H:%M UTC")}
**Plataformas**: Instagram · YouTube · TikTok

---

"""

    report = (
        header
        + buildInstagramSection(igData)
        + "---\n\n"
        + buildYouTubeSection(ytData)
        + "---\n\n"
        + buildTikTokSection(ttData)
        + "---\n\n"
        + buildRecommendations(igData, ytData, ttData)
        + "\n---\n\n*Relatório gerado automaticamente pelo sistema de monitoramento.*\n"
    )

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", default=datetime.utcnow().strftime("%Y-%m"),
                        help="Mês no formato YYYY-MM (padrão: mês atual)")
    args = parser.parse_args()

    report = generateReport(args.month)

    # Salvar em reports/
    reportDir  = os.path.join(REPORTS_DIR, args.month)
    os.makedirs(reportDir, exist_ok=True)
    reportPath = os.path.join(reportDir, "relatorio.md")

    with open(reportPath, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Relatório salvo em {reportPath}")
    print(json.dumps({
        "status":  "success",
        "path":    reportPath,
        "month":   args.month,
        "client":  CLIENT_NAME,
    }, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
