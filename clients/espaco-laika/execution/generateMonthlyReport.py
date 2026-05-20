#!/usr/bin/env python3
"""
Generate Monthly Report — Espaço Laika
Gera relatório Markdown em clients/espaco-laika/reports/<YYYY-MM>/relatorio.md

Uso:
    python clients/espaco-laika/execution/generateMonthlyReport.py
    python clients/espaco-laika/execution/generateMonthlyReport.py --month 2026-04
"""

import os, sys, json, glob, logging, argparse
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CLIENT      = "laika"
CLIENT_NAME = "Espaço Laika"
TMP_DIR     = ".tmp/laika"
REPORTS_DIR = "clients/espaco-laika/reports"


def loadLatest(platform: str) -> Optional[Dict]:
    files = sorted(glob.glob(os.path.join(TMP_DIR, f"{platform}_*.json")), reverse=True)
    if not files:
        return None
    with open(files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def fmt(n) -> str:
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return str(n) if n is not None else "—"

def pct(n) -> str:
    try:
        return f"{float(n) * 100:.1f}%"
    except Exception:
        return "—"


def igSection(data: Optional[Dict]) -> str:
    if not data:
        return "## 📸 Instagram\n\n> Sem dados. Execute `fetchInstagramMetrics.py --save`.\n\n"
    p = data.get("profile", {})
    a = data.get("analysis", {})
    posts = data.get("posts", [])
    reels = [x for x in posts if x.get("media_type") == "VIDEO"]

    top3Eng   = a.get("top_by_engagement", [])[:3]
    top3Saves = a.get("top_by_saves", [])[:3]
    top3Reels = a.get("top_reels_by_plays", [])[:3]

    lines = [
        "## 📸 Instagram\n",
        "| Métrica | Valor |",
        "|---------|-------|",
        f"| Seguidores | {fmt(p.get('followers_count'))} |",
        f"| Posts no período | {len(posts)} |",
        f"| Reels | {len(reels)} |",
        f"| Engajamento médio | {pct(a.get('avg_engagement_rate'))} |",
        "",
        "### Top 3 por Engajamento",
    ]
    for i, post in enumerate(top3Eng, 1):
        caption = (post.get("caption") or "—")[:60]
        lines.append(f"{i}. **{caption}** — {pct(post.get('engagement_rate'))}")

    lines += ["", "### Top 3 por Saves"]
    for i, post in enumerate(top3Saves, 1):
        caption = (post.get("caption") or "—")[:60]
        lines.append(f"{i}. **{caption}** — {fmt(post.get('saved'))} saves")

    lines += ["", "### Top 3 Reels por Views"]
    for i, r in enumerate(top3Reels, 1):
        caption = (r.get("caption") or "—")[:60]
        lines.append(f"{i}. **{caption}** — {fmt(r.get('plays'))} plays")

    return "\n".join(lines) + "\n\n"


def ytSection(data: Optional[Dict]) -> str:
    if not data:
        return "## 🎬 YouTube\n\n> Sem dados. Execute `fetchYouTubeMetrics.py --save`.\n\n"
    ch = data.get("channel", {})
    a  = data.get("analysis", {})
    top = a.get("top_by_views", [])[:3]

    lines = [
        "## 🎬 YouTube\n",
        "| Métrica | Valor |",
        "|---------|-------|",
        f"| Inscritos | {fmt(ch.get('subscribers'))} |",
        f"| Vídeos analisados | {a.get('videos_analyzed', '—')} |",
        f"| Views médias/vídeo | {fmt(a.get('avg_views'))} |",
        f"| Engajamento médio | {pct(a.get('avg_engagement_rate'))} |",
        "",
        "### Top 3 por Views",
    ]
    for i, v in enumerate(top, 1):
        lines.append(f"{i}. [{v.get('title','—')}]({v.get('url','#')}) — {fmt(v.get('views'))} views")

    return "\n".join(lines) + "\n\n"


def ttSection(data: Optional[Dict]) -> str:
    if not data:
        return "## 🎵 TikTok\n\n> Sem dados. Execute `fetchTikTokMetrics.py --save`.\n\n"
    acc = data.get("account", {})
    a   = data.get("analysis", {})
    top = a.get("top_by_views", [])[:3]
    topComp = a.get("top_by_completion", [])[:3]

    lines = [
        "## 🎵 TikTok\n",
        "| Métrica | Valor |",
        "|---------|-------|",
        f"| Seguidores | {fmt(acc.get('followers_count'))} |",
        f"| Vídeos analisados | {a.get('videos_analyzed', '—')} |",
        f"| Views médias/vídeo | {fmt(a.get('avg_views'))} |",
        f"| Completion rate médio | {pct(a.get('avg_completion_rate'))} |",
        f"| Engajamento médio | {pct(a.get('avg_engagement_rate'))} |",
        f"| Vídeos com FYP dominante | {a.get('fyp_videos_count', '—')} |",
        "",
        "### Top 3 por Views",
    ]
    for i, v in enumerate(top, 1):
        lines.append(f"{i}. [{v.get('id','Video')}]({v.get('url','#')}) — {fmt(v.get('views'))} views | completion: {pct(v.get('completion_rate'))}")

    lines += ["", "### Top 3 por Completion Rate"]
    for i, v in enumerate(topComp, 1):
        lines.append(f"{i}. [{v.get('id','Video')}]({v.get('url','#')}) — {pct(v.get('completion_rate'))} | {fmt(v.get('views'))} views")

    return "\n".join(lines) + "\n\n"


def recsSection(igData, ytData, ttData) -> str:
    recs = ["## 💡 Recomendações do Mês\n"]
    n = 1

    if igData:
        a = igData.get("analysis", {})
        eng = a.get("avg_engagement_rate", 0)
        if eng < 0.02:
            recs.append(f"{n}. **Instagram**: Engajamento de {pct(eng)} — criar conteúdo interativo e de valor (guias, checklists) para aumentar saves")
            n += 1
        if a.get("total_reels", 0) < 4:
            recs.append(f"{n}. **Instagram**: Aumentar frequência de Reels — priorizado pelo algoritmo para novos seguidores")
            n += 1

    if ytData:
        a = ytData.get("analysis", {})
        if a.get("low_performance_count", 0) > 2:
            recs.append(f"{n}. **YouTube**: Revisar thumbnails dos vídeos com baixo CTR — testar estilo diferente de título/imagem")
            n += 1

    if ttData:
        a = ttData.get("analysis", {})
        if a.get("avg_completion_rate", 0) < 0.5:
            recs.append(f"{n}. **TikTok**: Melhorar hook inicial — os primeiros 3 segundos determinam completion rate")
            n += 1

    if n == 1:
        recs.append("✅ Performance dentro dos benchmarks. Manter estratégia e monitorar tendências do nicho.")

    return "\n".join(recs) + "\n"


def generateReport(month: str) -> str:
    igData = loadLatest("instagram")
    ytData = loadLatest("youtube")
    ttData = loadLatest("tiktok")

    header = f"""# Relatório Mensal de Redes Sociais
## {CLIENT_NAME} — {month}

**Gerado em**: {datetime.utcnow().strftime("%d/%m/%Y às %H:%M UTC")}
**Plataformas**: Instagram · YouTube · TikTok

---

"""
    return (
        header
        + igSection(igData) + "---\n\n"
        + ytSection(ytData) + "---\n\n"
        + ttSection(ttData) + "---\n\n"
        + recsSection(igData, ytData, ttData)
        + "\n---\n\n*Gerado automaticamente pelo sistema de monitoramento.*\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", default=datetime.utcnow().strftime("%Y-%m"))
    args = parser.parse_args()

    report    = generateReport(args.month)
    reportDir = os.path.join(REPORTS_DIR, args.month)
    os.makedirs(reportDir, exist_ok=True)
    path = os.path.join(reportDir, "relatorio.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Relatório salvo em {path}")
    print(json.dumps({"status": "success", "path": path, "month": args.month, "client": CLIENT_NAME}))
    sys.exit(0)


if __name__ == "__main__":
    main()
