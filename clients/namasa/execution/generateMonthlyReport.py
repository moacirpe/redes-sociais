#!/usr/bin/env python3
"""
Generate Monthly Report — Namasa

Uso:
    python clients/namasa/execution/generateMonthlyReport.py
    python clients/namasa/execution/generateMonthlyReport.py --month 2026-04
"""

import os, sys, json, glob, logging, argparse
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CLIENT      = "namasa"
CLIENT_NAME = "Namasa"
TMP_DIR     = f".tmp/{CLIENT}"
REPORTS_DIR = f"clients/{CLIENT}/reports"


def loadLatest(platform: str) -> Optional[Dict]:
    files = sorted(glob.glob(os.path.join(TMP_DIR, f"{platform}_*.json")), reverse=True)
    if not files:
        return None
    with open(files[0], encoding="utf-8") as f:
        return json.load(f)


def fmt(n) -> str:
    try: return f"{int(n):,}".replace(",", ".")
    except: return str(n) if n is not None else "—"

def pct(n) -> str:
    try: return f"{float(n) * 100:.1f}%"
    except: return "—"


def igSection(data: Optional[Dict]) -> str:
    if not data:
        return "## 📸 Instagram\n\n> Sem dados. Execute `fetchInstagramMetrics.py --save`.\n\n"
    p     = data.get("profile", {})
    a     = data.get("analysis", {})
    posts = data.get("posts", [])
    reels = [x for x in posts if x.get("media_type") == "VIDEO"]
    lines = [
        "## 📸 Instagram\n",
        "| Métrica | Valor |", "|---------|-------|",
        f"| Seguidores | {fmt(p.get('followers_count'))} |",
        f"| Posts no período | {len(posts)} |",
        f"| Reels | {len(reels)} |",
        f"| Engajamento médio | {pct(a.get('avg_engagement_rate'))} |",
        "", "### Top 3 por Engajamento",
    ]
    for i, post in enumerate(a.get("top_by_engagement", [])[:3], 1):
        lines.append(f"{i}. **{(post.get('caption') or '—')[:60]}** — {pct(post.get('engagement_rate'))}")
    lines += ["", "### Top 3 Reels por Plays"]
    for i, r in enumerate(a.get("top_reels_by_plays", [])[:3], 1):
        lines.append(f"{i}. **{(r.get('caption') or '—')[:60]}** — {fmt(r.get('plays'))} plays")
    return "\n".join(lines) + "\n\n"


def ytSection(data: Optional[Dict]) -> str:
    if not data:
        return "## 🎬 YouTube\n\n> Sem dados. Execute `fetchYouTubeMetrics.py --save`.\n\n"
    ch = data.get("channel", {})
    a  = data.get("analysis", {})
    lines = [
        "## 🎬 YouTube\n",
        "| Métrica | Valor |", "|---------|-------|",
        f"| Inscritos | {fmt(ch.get('subscribers'))} |",
        f"| Views médias/vídeo | {fmt(a.get('avg_views'))} |",
        f"| Engajamento médio | {pct(a.get('avg_engagement_rate'))} |",
        "", "### Top 3 por Views",
    ]
    for i, v in enumerate(a.get("top_by_views", [])[:3], 1):
        lines.append(f"{i}. [{v.get('title','—')}]({v.get('url','#')}) — {fmt(v.get('views'))} views")
    return "\n".join(lines) + "\n\n"


def ttSection(data: Optional[Dict]) -> str:
    if not data:
        return "## 🎵 TikTok\n\n> Sem dados. Execute `fetchTikTokMetrics.py --save`.\n\n"
    acc = data.get("account", {})
    a   = data.get("analysis", {})
    lines = [
        "## 🎵 TikTok\n",
        "| Métrica | Valor |", "|---------|-------|",
        f"| Seguidores | {fmt(acc.get('followers_count'))} |",
        f"| Views médias/vídeo | {fmt(a.get('avg_views'))} |",
        f"| Completion rate médio | {pct(a.get('avg_completion_rate'))} |",
        f"| Engajamento médio | {pct(a.get('avg_engagement_rate'))} |",
        "", "### Top 3 por Views",
    ]
    for i, v in enumerate(a.get("top_by_views", [])[:3], 1):
        lines.append(f"{i}. [{v.get('id','Video')}]({v.get('url','#')}) — {fmt(v.get('views'))} views | completion: {pct(v.get('completion_rate'))}")
    return "\n".join(lines) + "\n\n"


def recsSection(igData, ytData, ttData) -> str:
    recs = ["## 💡 Recomendações do Mês\n"]
    n = 1

    if igData:
        posts = igData.get("posts", [])
        a     = igData.get("analysis", {})
        avgSaves = sum(p.get("saved") or 0 for p in posts) / len(posts) if posts else 0
        avgShares= sum(p.get("shares_count") or 0 for p in posts) / len(posts) if posts else 0
        if avgSaves < 5:
            recs.append(f"{n}. **Instagram**: Saves médios baixos ({avgSaves:.1f}/post) — criar conteúdo mais denso e reflexivo que as pessoas queiram guardar (reflexões escritas, carrosséis com ensinamentos)")
            n += 1
        if avgShares < 3:
            recs.append(f"{n}. **Instagram**: Compartilhamentos baixos — criar conteúdo que toque a ponto de a pessoa querer oferecer a alguém (frases, reflexões universais)")
            n += 1
        if a.get("total_reels", 0) < 2:
            recs.append(f"{n}. **Instagram**: Poucos Reels — considerar reflexões faladas em vídeo curto para ampliar alcance orgânico")
            n += 1

    if ytData:
        a = ytData.get("analysis", {})
        if a.get("avg_engagement_rate", 0) < 0.01:
            recs.append(f"{n}. **YouTube**: Engajamento baixo — inserir convite à reflexão no final dos vídeos (não CTA comercial, mas uma pergunta para os comentários)")
            n += 1

    if ttData:
        a  = ttData.get("analysis", {})
        cr = a.get("avg_completion_rate", 0)
        if cr < 0.5:
            recs.append(f"{n}. **TikTok**: Completion rate de {pct(cr)} — os primeiros segundos não estão sustentando a presença; começar com silêncio ou uma frase impactante em vez de introdução")
            n += 1
        if a.get("avg_engagement_rate", 0) < 0.02:
            recs.append(f"{n}. **TikTok**: Compartilhamentos baixos — criar conteúdo que a pessoa sinta vontade de mandar para alguém específico")
            n += 1

    if n == 1:
        recs.append("✅ Boa ressonância no período. Manter profundidade e autenticidade do conteúdo.")

    recs.append("\n> *Recomendações orientadas à profundidade de conexão, não a volume ou viralidade.*")
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
