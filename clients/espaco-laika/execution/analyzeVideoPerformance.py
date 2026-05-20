#!/usr/bin/env python3
"""
Analyze Video Performance — Espaço Laika
Mesma lógica do script da Moper, com CLIENT = 'laika' e TMP_DIR = '.tmp/laika'.

Uso:
    python clients/espaco-laika/execution/analyzeVideoPerformance.py --platform all
"""

import os, sys, json, glob, logging, argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CLIENT  = "laika"
TMP_DIR = ".tmp/laika"


def loadLatestFile(platform: str) -> Optional[Dict]:
    files = sorted(glob.glob(os.path.join(TMP_DIR, f"{platform}_*.json")), reverse=True)
    if not files:
        logger.warning(f"Sem dados para {platform} em {TMP_DIR}/")
        return None
    logger.info(f"Carregando {files[0]}")
    with open(files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def analyzeInstagram(data: Dict) -> Dict:
    posts    = data.get("posts", [])
    profile  = data.get("profile", {})
    analysis = data.get("analysis", {})
    reels    = [p for p in posts if p.get("media_type") == "VIDEO"]

    def avg(lst, key):
        v = [p.get(key) or 0 for p in lst]
        return round(sum(v) / len(v), 2) if v else 0

    alerts = []
    eng = analysis.get("avg_engagement_rate", 0)
    if eng < 0.01:
        alerts.append("⚠️ Engajamento médio < 1% — rever formato e horário")
    if analysis.get("total_reels", 0) < 2:
        alerts.append("⚠️ Poucos Reels — algoritmo favorece Reels para alcance")
    if avg(posts, "saved") < 5:
        alerts.append("⚠️ Baixo número de saves — criar conteúdo de referência/guias")

    return {
        "platform":   "instagram",
        "followers":  profile.get("followers_count"),
        "content_mix": {"reels": len(reels), "others": len(posts) - len(reels)},
        "avg_engagement_rate": analysis.get("avg_engagement_rate"),
        "avg_saves":   avg(posts, "saved"),
        "avg_shares":  avg(posts, "shares_count"),
        "top_by_engagement": analysis.get("top_by_engagement", [])[:3],
        "top_by_saves":      analysis.get("top_by_saves", [])[:3],
        "top_by_shares":     analysis.get("top_by_shares", [])[:3],
        "top_reels":         analysis.get("top_reels_by_plays", [])[:3],
        "alerts": alerts,
    }


def analyzeYouTube(data: Dict) -> Dict:
    videos   = data.get("videos", [])
    channel  = data.get("channel", {})
    analysis = data.get("analysis", {})
    alerts   = []

    lowPerf = analysis.get("low_performance_count", 0)
    if lowPerf > 2:
        alerts.append(f"⚠️ {lowPerf} vídeos com curtidas < 2% das views — revisar thumbnails")
    if analysis.get("avg_engagement_rate", 0) < 0.02:
        alerts.append("⚠️ Engajamento médio baixo — inserir CTA de comentário nos vídeos")

    highPerf = [v for v in videos if v.get("views", 0) > analysis.get("avg_views", 0) * 1.5]
    if highPerf:
        alerts.append(f"🔥 {len(highPerf)} vídeo(s) acima da média — analisar padrão e replicar")

    return {
        "platform":    "youtube",
        "subscribers": channel.get("subscribers"),
        "avg_views":   analysis.get("avg_views"),
        "avg_engagement_rate": analysis.get("avg_engagement_rate"),
        "top_by_views":      analysis.get("top_by_views", [])[:3],
        "top_by_engagement": analysis.get("top_by_engagement", [])[:3],
        "alerts": alerts,
    }


def analyzeTikTok(data: Dict) -> Dict:
    videos   = data.get("videos", [])
    account  = data.get("account", {})
    analysis = data.get("analysis", {})
    alerts   = []

    cr = analysis.get("avg_completion_rate", 0)
    if cr < 0.4:
        alerts.append(f"⚠️ Completion rate médio de {cr:.0%} — melhorar hook dos 3 primeiros segundos")
    if analysis.get("fyp_videos_count", 0) == 0:
        alerts.append("⚠️ Sem vídeos com tráfego dominante do FYP — usar sons em tendência")

    goodComp = [v for v in videos if v.get("completion_rate", 0) > 0.6]
    if goodComp:
        alerts.append(f"✅ {len(goodComp)} vídeo(s) com completion > 60% — usar como modelo de formato")

    return {
        "platform":            "tiktok",
        "followers":           account.get("followers_count"),
        "avg_views":           analysis.get("avg_views"),
        "avg_completion_rate": analysis.get("avg_completion_rate"),
        "avg_engagement_rate": analysis.get("avg_engagement_rate"),
        "fyp_count":           analysis.get("fyp_videos_count"),
        "top_by_views":        analysis.get("top_by_views", [])[:3],
        "top_by_completion":   analysis.get("top_by_completion", [])[:3],
        "alerts": alerts,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", default="all",
                        choices=["all", "instagram", "youtube", "tiktok"])
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    platforms = ["instagram", "youtube", "tiktok"] if args.platform == "all" else [args.platform]
    analyses  = []

    for platform in platforms:
        data = loadLatestFile(platform)
        if not data:
            continue
        if platform == "instagram":
            analyses.append(analyzeInstagram(data))
        elif platform == "youtube":
            analyses.append(analyzeYouTube(data))
        elif platform == "tiktok":
            analyses.append(analyzeTikTok(data))

    if not analyses:
        print(json.dumps({"status": "error", "error": "Sem dados. Execute os scripts fetch primeiro."}))
        sys.exit(1)

    allAlerts = [f"[{a['platform'].upper()}] {alert}" for a in analyses for alert in a.get("alerts", [])]
    report = {
        "status":    "success",
        "client":    CLIENT,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "platforms": {a["platform"]: a for a in analyses},
        "executive_summary": {
            "platforms_analyzed": [a["platform"] for a in analyses],
            "total_alerts":       len(allAlerts),
            "all_alerts":         allAlerts,
        }
    }

    if args.save:
        os.makedirs(TMP_DIR, exist_ok=True)
        ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = f"{TMP_DIR}/analysis_{ts}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Salvo em {path}")

    print(json.dumps(report, indent=2, default=str))
    sys.exit(0)


if __name__ == "__main__":
    main()
