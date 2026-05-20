#!/usr/bin/env python3
"""
Analyze Video Performance — Moacir (Pessoal)

Uso:
    python clients/moacir/execution/analyzeVideoPerformance.py --platform all
    python clients/moacir/execution/analyzeVideoPerformance.py --platform tiktok --save
"""

import os, sys, json, glob, logging, argparse
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CLIENT  = "moacir"
TMP_DIR = f".tmp/{CLIENT}"


def loadLatest(platform: str) -> Optional[Dict]:
    files = sorted(glob.glob(os.path.join(TMP_DIR, f"{platform}_*.json")), reverse=True)
    if not files:
        logger.warning(f"Sem dados para {platform}. Execute fetch primeiro.")
        return None
    with open(files[0], encoding="utf-8") as f:
        return json.load(f)


def analyzeInstagram(data: Dict) -> Dict:
    posts = data.get("posts", [])
    a     = data.get("analysis", {})
    reels = [p for p in posts if p.get("media_type") == "VIDEO"]
    alerts = []
    if a.get("avg_engagement_rate", 0) < 0.01:
        alerts.append("⚠️ Engajamento < 1% — rever formato e horário")
    if len(reels) < 2:
        alerts.append("⚠️ Poucos Reels — algoritmo favorece Reels para alcance")
    return {
        "platform": "instagram",
        "followers": data.get("profile", {}).get("followers_count"),
        "avg_engagement_rate": a.get("avg_engagement_rate"),
        "total_posts": len(posts), "total_reels": len(reels),
        "top_by_engagement": a.get("top_by_engagement", [])[:3],
        "top_by_saves":      a.get("top_by_saves", [])[:3],
        "top_reels":         a.get("top_reels_by_plays", [])[:3],
        "alerts": alerts,
    }


def analyzeYouTube(data: Dict) -> Dict:
    a      = data.get("analysis", {})
    videos = data.get("videos", [])
    alerts = []
    if a.get("low_performance_count", 0) > 2:
        alerts.append(f"⚠️ {a['low_performance_count']} vídeos com curtidas < 2% — revisar thumbnails")
    highPerf = [v for v in videos if v.get("views", 0) > a.get("avg_views", 0) * 1.5]
    if highPerf:
        alerts.append(f"🔥 {len(highPerf)} vídeo(s) acima da média — analisar padrão")
    return {
        "platform":    "youtube",
        "subscribers": data.get("channel", {}).get("subscribers"),
        "avg_views":   a.get("avg_views"),
        "avg_engagement_rate": a.get("avg_engagement_rate"),
        "top_by_views":      a.get("top_by_views", [])[:3],
        "top_by_engagement": a.get("top_by_engagement", [])[:3],
        "alerts": alerts,
    }


def analyzeTikTok(data: Dict) -> Dict:
    a      = data.get("analysis", {})
    videos = data.get("videos", [])
    alerts = []
    cr = a.get("avg_completion_rate", 0)
    if cr < 0.4:
        alerts.append(f"⚠️ Completion rate {cr:.0%} — melhorar hook dos 3 primeiros segundos")
    if a.get("fyp_videos_count", 0) == 0:
        alerts.append("⚠️ Sem vídeos com FYP dominante — usar sons em tendência")
    goodComp = [v for v in videos if v.get("completion_rate", 0) > 0.6]
    if goodComp:
        alerts.append(f"✅ {len(goodComp)} vídeo(s) com completion > 60% — usar como modelo")
    return {
        "platform":            "tiktok",
        "followers":           data.get("account", {}).get("followers_count"),
        "avg_views":           a.get("avg_views"),
        "avg_completion_rate": a.get("avg_completion_rate"),
        "avg_engagement_rate": a.get("avg_engagement_rate"),
        "fyp_count":           a.get("fyp_videos_count"),
        "top_by_views":        a.get("top_by_views", [])[:3],
        "top_by_completion":   a.get("top_by_completion", [])[:3],
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

    for p in platforms:
        data = loadLatest(p)
        if not data:
            continue
        if p == "instagram":
            analyses.append(analyzeInstagram(data))
        elif p == "youtube":
            analyses.append(analyzeYouTube(data))
        elif p == "tiktok":
            analyses.append(analyzeTikTok(data))

    if not analyses:
        print(json.dumps({"status": "error", "error": "Sem dados. Execute os scripts fetch primeiro."}))
        sys.exit(1)

    allAlerts = [f"[{a['platform'].upper()}] {alert}" for a in analyses for alert in a.get("alerts", [])]
    report = {
        "status": "success", "client": CLIENT,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "platforms": {a["platform"]: a for a in analyses},
        "executive_summary": {
            "platforms_analyzed": [a["platform"] for a in analyses],
            "total_alerts": len(allAlerts),
            "all_alerts":   allAlerts,
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
