#!/usr/bin/env python3
"""
Monitor de Performance — @moacir.moper

Monitora métricas críticas e alerta sobre problemas potenciais.
Executar diariamente para detectar issues precocemente.
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from utils import (
    setupLogging,
    calculateEngagementRate,
    createGrowthProjection,
    getTimestamp
)

logger = setupLogging()

CLIENT = "moacir"
REPORTS_DIR = f"clients/{CLIENT}/reports"
DASHBOARD_FILE = f"{REPORTS_DIR}/dashboard_monitoramento.json"

class PerformanceMonitor:
    """Monitor de performance com alertas automáticos."""

    def __init__(self):
        self.alerts = []
        self.metrics = {}
        self.risks = []

    def loadCurrentData(self) -> Dict:
        """Carrega dados atuais das plataformas."""
        # Simulação - em produção, carrega dados reais
        return {
            'instagram': {
                'followers': 2500,
                'engagement_rate': 2.1,
                'posts_today': 1,
                'comments_unanswered': 5
            },
            'tiktok': {
                'followers': 1200,
                'engagement_rate': 3.8,
                'videos_today': 1,
                'duets_pending': 2
            },
            'youtube': {
                'subscribers': 800,
                'avg_views': 150,
                'ctr': 1.2,  # Click-through rate
                'videos_today': 0,
                'comments_unanswered': 3
            },
            'overall': {
                'total_followers': 4500,
                'target_followers': 10000,
                'days_elapsed': 0,
                'target_completion_days': 30
            }
        }

    def checkEngagementRates(self, data: Dict) -> None:
        """Verifica se engagement rates estão dentro do esperado."""
        thresholds = {
            'instagram': 2.0,  # mínimo 2%
            'tiktok': 3.0,     # mínimo 3%
            'youtube': 1.0     # mínimo 1% (CTR)
        }

        for platform, threshold in thresholds.items():
            # YouTube usa CTR como proxy de engajamento
            metric_key = 'engagement_rate' if platform != 'youtube' else 'ctr'
            current = data[platform].get(metric_key, 0)

            if current < threshold:
                severity = 'HIGH' if current < threshold * 0.7 else 'MEDIUM'
                metric_name = 'engajamento' if platform != 'youtube' else 'CTR'
                self.alerts.append({
                    'type': 'ENGAGEMENT_LOW',
                    'platform': platform,
                    'severity': severity,
                    'message': f'{metric_name.capitalize()} {platform} em {current:.1f}% (mínimo: {threshold:.1f}%)',
                    'action': 'Aumentar interação, testar novos formatos, verificar horários'
                })

    def checkPostingFrequency(self, data: Dict) -> None:
        """Verifica frequência de postagem."""
        targets = {
            'instagram': {'min': 0.8, 'max': 1.5},  # 3-4 posts/semana
            'tiktok': {'min': 0.5, 'max': 1.0},     # 4-5 vídeos/semana
            'youtube': {'min': 0.1, 'max': 0.2}     # 1 vídeo/semana
        }

        for platform, target in targets.items():
            today_posts = data[platform].get(f'posts_today', 0) or data[platform].get(f'videos_today', 0)
            if today_posts < target['min']:
                self.alerts.append({
                    'type': 'POSTING_LOW',
                    'platform': platform,
                    'severity': 'MEDIUM',
                    'message': f'Frequência baixa em {platform}: {today_posts} posts hoje',
                    'action': 'Agendar posts, preparar conteúdo antecipado'
                })
            elif today_posts > target['max']:
                self.alerts.append({
                    'type': 'POSTING_HIGH',
                    'platform': platform,
                    'severity': 'LOW',
                    'message': f'Frequência alta em {platform}: {today_posts} posts hoje',
                    'action': 'Verificar qualidade vs quantidade, espaçar posts'
                })

    def checkGrowthTrajectory(self, data: Dict) -> None:
        """Verifica se crescimento está no caminho certo."""
        current = data['overall']['total_followers']
        target = data['overall']['target_followers']
        days_elapsed = data['overall']['days_elapsed']
        total_days = data['overall']['target_completion_days']

        if days_elapsed == 0:
            return  # Primeiro dia, sem dados históricos

        # Calcular progresso esperado vs real
        expected_progress = (days_elapsed / total_days) * target
        actual_progress = current

        growth_rate = (actual_progress / expected_progress) if expected_progress > 0 else 1.0

        if growth_rate < 0.8:  # Atrasado
            self.alerts.append({
                'type': 'GROWTH_BEHIND',
                'severity': 'HIGH',
                'message': f'Crescimento atrasado: {actual_progress}/{expected_progress:.0f} seguidores esperados',
                'action': 'Aumentar frequência, investir em anúncios, melhorar engajamento'
            })
        elif growth_rate > 1.2:  # À frente
            self.alerts.append({
                'type': 'GROWTH_AHEAD',
                'severity': 'LOW',
                'message': f'Crescimento acima do esperado: {actual_progress}/{expected_progress:.0f}',
                'action': 'Manter estratégia, documentar sucesso'
            })

    def checkUnansweredInteractions(self, data: Dict) -> None:
        """Verifica comentários e interações não respondidas."""
        for platform in ['instagram', 'tiktok', 'youtube']:
            unanswered = data[platform].get('comments_unanswered', 0)
            if unanswered > 10:
                self.alerts.append({
                    'type': 'UNANSWERED_INTERACTIONS',
                    'platform': platform,
                    'severity': 'HIGH',
                    'message': f'{unanswered} interações não respondidas em {platform}',
                    'action': 'Responder urgentemente, configurar lembretes automáticos'
                })
            elif unanswered > 5:
                self.alerts.append({
                    'type': 'UNANSWERED_INTERACTIONS',
                    'platform': platform,
                    'severity': 'MEDIUM',
                    'message': f'{unanswered} interações não respondidas em {platform}',
                    'action': 'Responder hoje, melhorar sistema de notificações'
                })

    def checkContentQuality(self, data: Dict) -> None:
        """Verifica qualidade do conteúdo baseado em métricas."""
        # Verificar se há sinais de shadowban (baixa visibilidade)
        for platform in ['instagram', 'tiktok']:
            reach_rate = data[platform].get('reach_rate', 1.0)  # alcance / seguidores
            if reach_rate < 0.3:  # Menos de 30% do alcance esperado
                self.alerts.append({
                    'type': 'CONTENT_QUALITY',
                    'platform': platform,
                    'severity': 'HIGH',
                    'message': f'Alcance baixo em {platform}: {reach_rate:.1%} (possível shadowban)',
                    'action': 'Pausar posts 24h, verificar regras da comunidade, variar conteúdo'
                })

    def generateReport(self) -> Dict:
        """Gera relatório completo de monitoramento."""
        self.alerts = []
        data = self.loadCurrentData()

        # Executar todas as verificações
        self.checkEngagementRates(data)
        self.checkPostingFrequency(data)
        self.checkGrowthTrajectory(data)
        self.checkUnansweredInteractions(data)
        self.checkContentQuality(data)

        # Classificar alertas por severidade
        high_alerts = [a for a in self.alerts if a['severity'] == 'HIGH']
        medium_alerts = [a for a in self.alerts if a['severity'] == 'MEDIUM']
        low_alerts = [a for a in self.alerts if a['severity'] == 'LOW']

        report = {
            'timestamp': getTimestamp(),
            'client': CLIENT,
            'status': 'CRITICAL' if high_alerts else 'WARNING' if medium_alerts else 'GOOD',
            'metrics': data,
            'alerts': {
                'high': high_alerts,
                'medium': medium_alerts,
                'low': low_alerts,
                'total': len(self.alerts)
            },
            'recommendations': self.generateRecommendations(high_alerts, medium_alerts),
            'next_check': (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"
        }

        return report

    def generateRecommendations(self, high_alerts: List, medium_alerts: List) -> List[str]:
        """Gera recomendações baseadas nos alertas."""
        recommendations = []

        if high_alerts:
            recommendations.append("🚨 PRIORIDADE: Resolver alertas críticos imediatamente")
            recommendations.append("📞 Agendar reunião de emergência para ajustar estratégia")

        if medium_alerts:
            recommendations.append("⚠️ MÉDIO: Revisar processos e otimizar performance")
            recommendations.append("📊 Aumentar monitoramento para 2x/dia")

        if not high_alerts and not medium_alerts:
            recommendations.append("✅ SISTEMA: Performance dentro do esperado")
            recommendations.append("📈 Continuar estratégia atual com ajustes finos")

        # Recomendações específicas
        alert_types = [a['type'] for a in high_alerts + medium_alerts]

        if 'ENGAGEMENT_LOW' in alert_types:
            recommendations.append("💬 ENGAGEMENT: Aumentar interação, fazer mais perguntas, usar polls")

        if 'POSTING_LOW' in alert_types:
            recommendations.append("📝 FREQUÊNCIA: Preparar mais conteúdo, usar agendamento automático")

        if 'GROWTH_BEHIND' in alert_types:
            recommendations.append("📈 CRESCIMENTO: Considerar anúncios pagos, parcerias, giveaways")

        if 'UNANSWERED_INTERACTIONS' in alert_types:
            recommendations.append("💬 INTERAÇÕES: Configurar notificações push, delegar respostas")

        return recommendations

    def saveReport(self, report: Dict) -> None:
        """Salva relatório em arquivo."""
        os.makedirs(os.path.dirname(DASHBOARD_FILE), exist_ok=True)

        with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Relatório salvo em {DASHBOARD_FILE}")

    def printReport(self, report: Dict) -> None:
        """Imprime relatório formatado."""
        print(f"\n📊 MONITOR DE PERFORMANCE — {CLIENT.upper()}")
        print(f"📅 {report['timestamp']}")
        print(f"📊 Status: {report['status']}")

        print(f"\n👥 MÉTRICAS ATUAIS:")
        metrics = report['metrics']
        print(f"  Instagram: {metrics['instagram']['followers']:,} seguidores ({metrics['instagram']['engagement_rate']:.1f}% engajamento)")
        print(f"  TikTok: {metrics['tiktok']['followers']:,} seguidores ({metrics['tiktok']['engagement_rate']:.1f}% engajamento)")
        print(f"  YouTube: {metrics['youtube']['subscribers']:,} inscritos")
        print(f"  TOTAL: {metrics['overall']['total_followers']:,} seguidores")

        alerts = report['alerts']
        if alerts['total'] > 0:
            print(f"\n🚨 ALERTAS ({alerts['total']}):")
            for alert in alerts['high']:
                print(f"  🔴 HIGH: {alert['message']}")
            for alert in alerts['medium']:
                print(f"  🟡 MEDIUM: {alert['message']}")
            for alert in alerts['low']:
                print(f"  🟢 LOW: {alert['message']}")

        print(f"\n💡 RECOMENDAÇÕES:")
        for rec in report['recommendations']:
            print(f"  • {rec}")

        print(f"\n⏰ Próxima verificação: {report['next_check']}")

def main():
    """Executa monitoramento completo."""
    monitor = PerformanceMonitor()
    report = monitor.generateReport()
    monitor.saveReport(report)
    monitor.printReport(report)

    # Exit code baseado na severidade
    if report['status'] == 'CRITICAL':
        sys.exit(2)  # Crítico
    elif report['status'] == 'WARNING':
        sys.exit(1)  # Aviso
    else:
        sys.exit(0)  # OK

if __name__ == "__main__":
    main()