#!/usr/bin/env python3
"""
Sistema Integrado de Monitoramento e Alertas — @moacir.moper

Executa monitoramento completo e envia alertas automaticamente.
Ideal para agendamento diário (cron job).
"""

import os
import sys
import json
from datetime import datetime

from performanceMonitor import PerformanceMonitor
from alertSystem import AlertSystem
from utils import setupLogging

logger = setupLogging()

def main():
    """Executa monitoramento completo com alertas."""
    print("🚀 Iniciando Sistema Integrado de Monitoramento")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. Executar monitoramento
        print("\n📊 Executando monitoramento de performance...")
        monitor = PerformanceMonitor()
        report = monitor.generateReport()
        monitor.saveReport(report)

        # 2. Exibir relatório no console
        monitor.printReport(report)

        alert_system = AlertSystem()

        # 3. Enviar alertas se necessário
        if report['alerts']['total'] > 0:
            print(f"\n🚨 Enviando {report['alerts']['total']} alertas...")
            alerts_sent = 0

            # Enviar alertas críticos primeiro
            for alert in report['alerts']['high'] + report['alerts']['medium']:
                if alert_system.sendAlert(alert):
                    alerts_sent += 1
                    print(f"✅ Alerta enviado: {alert['severity']} - {alert['platform']}")
                else:
                    print(f"❌ Falha no alerta: {alert['severity']} - {alert['platform']}")

            print(f"📤 {alerts_sent} alertas enviados com sucesso")

        # 4. Enviar relatório diário
        print("\n📧 Enviando relatório diário...")
        if alert_system.sendDailyReport(report):
            print("✅ Relatório diário enviado")
        else:
            print("❌ Falha no envio do relatório diário")

        # 5. Status final
        status = report['status']
        if status == 'CRITICAL':
            print("\n🚨 STATUS CRÍTICO: Ação imediata necessária!")
            sys.exit(2)
        elif status == 'WARNING':
            print("\n⚠️ STATUS DE ALERTA: Revisar processos")
            sys.exit(1)
        else:
            print("\n✅ STATUS BOM: Continuar estratégia atual")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Erro no sistema integrado: {e}")
        print(f"\n❌ ERRO SISTEMA: {e}")

        # Tentar enviar alerta de erro
        try:
            alert_system = AlertSystem()
            error_alert = {
                'severity': 'HIGH',
                'platform': 'sistema',
                'message': f'Erro no sistema de monitoramento: {str(e)}',
                'action': 'Verificar logs e reiniciar sistema'
            }
            alert_system.sendAlert(error_alert)
        except Exception:
            pass  # Não falhar se o alerta de erro também falhar

        sys.exit(3)

if __name__ == "__main__":
    main()