#!/usr/bin/env python3
"""
Analyze Video Performance — Moper Máquinas

Carrega dados coletados de .tmp/moper/ e gera análise consolidada
de performance de vídeos por plataforma.

Uso:
    python clients/moper-maquinas/execution/analyzeVideoPerformance.py --platform all
    python clients/moper-maquinas/execution/analyzeVideoPerformance.py --platform youtube
    python clients/moper-maquinas/execution/analyzeVideoPerformance.py --platform instagram
    python clients/moper-maquinas/execution/analyzeVideoPerformance.py --platform tiktok
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

CLIENT   = "moper"
TMP_DIR  = ".tmp/moper"


def loadLatestFile(platform: str) -> Optional[Dict]:
    """Carrega o arquivo JSON mais recente de uma plataforma."""
    pattern = os.path.join(TMP_DIR, f"{platform}_*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    if not files:
        logger.warning(f"Nenhum dado encontrado para {platform} em {TMP_DIR}/")
        return None
    path = files[0]
    logger.info(f"Carregando {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================================
# ANÁLISE POR PLATAFORMA
# ============================================================================

def analyzeInstagram(data: Dict) -> Dict:
    posts    = data.get("posts", [])
    profile  = data.get("profile", {})
    analysis = data.get("analysis", {})

    reels    = [p for p in posts if p.get("media_type") == "VIDEO"]
    carousels= [p for p in posts if p.get("media_type") == "CAROUSEL_ALBUM"]
    photos   = [p for p in posts if p.get("media_type") == "IMAGE"]

    def avgMetric(lst, key):
        vals = [p.get(key) or 0 for p in lst]
        return round(sum(vals) / len(vals), 2) if vals else 0

    return {
        "platform": "instagram",
        "followers": profile.get("followers_count"),
        "content_mix": {
            "reels":     len(reels),
            "carousels": len(carousels),
            "photos":    len(photos),
        },
        "avg_engagement_rate": analysis.get("avg_engagement_rate"),
        "avg_likes":     avgMetric(posts, "like_count"),
        "avg_comments":  avgMetric(posts, "comments_count"),
        "avg_saves":     avgMetric(posts, "saved"),
        "avg_reels_plays": avgMetric(reels, "plays"),
        "top_posts": analysis.get("top_by_engagement", [])[:3],
        "top_reels":  analysis.get("top_reels_by_plays", [])[:3],
        "alerts": _instagramAlerts(posts, analysis),
    }


def _instagramAlerts(posts: List, analysis: Dict) -> List[str]:
    alerts = []
    eng = analysis.get("avg_engagement_rate", 0)
    if eng < 0.01:
        alerts.append("⚠️ Engajamento médio abaixo de 1% — revisar formato e horário de postagem")
    if analysis.get("total_reels", 0) < 2:
        alerts.append("⚠️ Poucos Reels no período — algoritmo prioriza Reels para alcance")
    return alerts


def analyzeYouTube(data: Dict) -> Dict:
    videos   = data.get("videos", [])
    channel  = data.get("channel", {})
    analysis = data.get("analysis", {})

    lowRetention = [v for v in videos if v.get("likes_rate", 1) < 0.02]
    highPerf     = [v for v in videos if v.get("views", 0) > analysis.get("avg_views", 0) * 1.5]

    return {
        "platform":    "youtube",
        "subscribers": channel.get("subscribers"),
        "total_views": channel.get("total_views"),
        "video_count": channel.get("video_count"),
        "period_stats": {
            "videos_analyzed":    analysis.get("videos_analyzed"),
            "avg_views":          analysis.get("avg_views"),
            "avg_engagement_rate":analysis.get("avg_engagement_rate"),
        },
        "top_by_views":      analysis.get("top_by_views", [])[:3],
        "top_by_engagement": analysis.get("top_by_engagement", [])[:3],
        "alerts": _youtubeAlerts(videos, analysis, lowRetention, highPerf),
    }


def _youtubeAlerts(videos, analysis, lowRetention, highPerf) -> List[str]:
    alerts = []
    if lowRetention:
        alerts.append(f"⚠️ {len(lowRetention)} vídeo(s) com curtidas < 2% das views — avaliar thumbnails")
    if analysis.get("avg_engagement_rate", 0) < 0.02:
        alerts.append("⚠️ Engajamento médio baixo — estimular comentários no CTA")
    if highPerf:
        alerts.append(f"🔥 {len(highPerf)} vídeo(s) com performance acima da média — analisar padrão")
    return alerts


def analyzeTikTok(data: Dict) -> Dict:
    videos   = data.get("videos", [])
    account  = data.get("account", {})
    analysis = data.get("analysis", {})

    goodCompletion = [v for v in videos if v.get("completion_rate", 0) > 0.6]
    fypDominant    = [
        v for v in videos
        if v.get("traffic_sources", {}).get("FOR_YOU_PAGE", 0) > 0.7
    ]

    return {
        "platform":   "tiktok",
        "followers":  account.get("followers_count"),
        "period_stats": {
            "videos_analyzed":     analysis.get("videos_analyzed"),
            "avg_views":           analysis.get("avg_views"),
            "avg_completion_rate": analysis.get("avg_completion_rate"),
            "avg_engagement_rate": analysis.get("avg_engagement_rate"),
            "fyp_videos_count":    analysis.get("fyp_videos_count"),
        },
        "top_by_views":      analysis.get("top_by_views", [])[:3],
        "top_by_completion": analysis.get("top_by_completion", [])[:3],
        "good_completion_count": len(goodCompletion),
        "fyp_dominant_count":    len(fypDominant),
        "alerts": _tiktokAlerts(analysis, goodCompletion),
    }


def _tiktokAlerts(analysis: Dict, goodCompletion: List) -> List[str]:
    alerts = []
    cr = analysis.get("avg_completion_rate", 0)
    if cr < 0.4:
        alerts.append("⚠️ Completion rate médio abaixo de 40% — melhorar hook dos primeiros 3 segundos")
    if analysis.get("fyp_videos_count", 0) == 0:
        alerts.append("⚠️ Nenhum vídeo com tráfego dominante do FYP — revisar uso de sons em tendência e hashtags")
    if goodCompletion:
        alerts.append(f"✅ {len(goodCompletion)} vídeo(s) com completion > 60% — usar como referência de formato")
    return alerts


# ============================================================================
# ANÁLISE CONSOLIDADA
# ============================================================================

def buildConsolidatedReport(analyses: List[Dict]) -> Dict:
    """Combina análises de todas as plataformas em um resumo executivo."""
    alerts_all = []
    for a in analyses:
        for alert in a.get("alerts", []):
            alerts_all.append(f"[{a['platform'].upper()}] {alert}")

    return {
        "client":    CLIENT,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "platforms": {a["platform"]: a for a in analyses},
        "executive_summary": {
            "platforms_analyzed": [a["platform"] for a in analyses],
            "total_alerts":       len(alerts_all),
            "all_alerts":         alerts_all,
        }
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", default="all",
                        choices=["all", "instagram", "youtube", "tiktok"])
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    analyses = []

    platforms = (
        ["instagram", "youtube", "tiktok"]
        if args.platform == "all"
        else [args.platform]
    )

    for platform in platforms:
        data = loadLatestFile(platform)
        if data is None:
            logger.warning(f"Pulando {platform} — sem dados. Execute fetch primeiro.")
            continue

        if platform == "instagram":
            analyses.append(analyzeInstagram(data))
        elif platform == "youtube":
            analyses.append(analyzeYouTube(data))
        elif platform == "tiktok":
            analyses.append(analyzeTikTok(data))

    if not analyses:
        print(json.dumps({"status": "error", "error": "Nenhum dado disponível. Execute os scripts fetch primeiro."}))
        sys.exit(1)

    report = buildConsolidatedReport(analyses)
    report["status"] = "success"

    if args.save:
        os.makedirs(TMP_DIR, exist_ok=True)
        ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = f"{TMP_DIR}/analysis_{ts}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Análise salva em {path}")

    print(json.dumps(report, indent=2, default=str))
    sys.exit(0)


if __name__ == "__main__":
    main()
