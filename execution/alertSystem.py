#!/usr/bin/env python3
"""
Sistema de Alertas — @moacir.moper

Envia notificações automáticas sobre problemas detectados.
Integra com WhatsApp, email e outras plataformas.
"""

import os
import json
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List

from utils import setupLogging, getEnv

logger = setupLogging()

class AlertSystem:
    """Sistema de alertas multi-canal."""

    def __init__(self):
        self.config = self.loadConfig()

    def loadConfig(self) -> Dict:
        """Carrega configuração de alertas."""
        return {
            'email': {
                'enabled': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': getEnv('ALERT_EMAIL_FROM', ''),
                'sender_password': getEnv('ALERT_EMAIL_PASSWORD', ''),
                'recipients': [r.strip() for r in getEnv('ALERT_EMAIL_TO', 'moacirper@icloud.com').split(',')],
            },
            'whatsapp': {
                'enabled': False,  # Desabilitado por enquanto
                'api_url': 'https://api.whatsapp.com/send',
                'api_key': getEnv('WHATSAPP_API_KEY', ''),
                'recipients': ['+5511999999999']
            },
            'telegram': {
                'enabled': False,  # Desabilitado por enquanto
                'bot_token': getEnv('TELEGRAM_BOT_TOKEN', ''),
                'chat_ids': ['123456789']
            }
        }

    def sendEmailAlert(self, subject: str, message: str, severity: str) -> bool:
        """Envia alerta por email."""
        if not self.config['email']['enabled']:
            return False

        try:
            # Configurar email
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['sender_email']
            msg['To'] = ', '.join(self.config['email']['recipients'])
            msg['Subject'] = f"🚨 [{severity}] {subject}"

            # Corpo do email
            body = f"""
            Alerta Automático - Sistema de Monitoramento @moacir.moper

            {message}

            ---
            Sistema de Alertas Automáticos
            Data: {datetime.now().isoformat()}
            """

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port']) as server:
                server.starttls()
                server.login(self.config['email']['sender_email'], self.config['email']['sender_password'])
                server.sendmail(self.config['email']['sender_email'], self.config['email']['recipients'], msg.as_string())

            logger.info(f"Email enviado para {self.config['email']['recipients']}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False

    def sendWhatsAppAlert(self, message: str, severity: str) -> bool:
        """Envia alerta por WhatsApp."""
        if not self.config['whatsapp']['enabled']:
            return False

        try:
            emoji = {'HIGH': '🚨', 'MEDIUM': '⚠️', 'LOW': 'ℹ️'}.get(severity, '📢')

            for recipient in self.config['whatsapp']['recipients']:
                payload = {
                    'phone': recipient,
                    'message': f"{emoji} ALERTA {severity}\n\n{message}",
                    'api_key': self.config['whatsapp']['api_key']
                }

                response = requests.post(self.config['whatsapp']['api_url'], json=payload, timeout=15)
                response.raise_for_status()

            logger.info(f"WhatsApp enviado para {self.config['whatsapp']['recipients']}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")
            return False

    def sendTelegramAlert(self, message: str, severity: str) -> bool:
        """Envia alerta por Telegram."""
        if not self.config['telegram']['enabled']:
            return False

        try:
            emoji = {'HIGH': '🚨', 'MEDIUM': '⚠️', 'LOW': 'ℹ️'}.get(severity, '📢')

            for chat_id in self.config['telegram']['chat_ids']:
                url = f"https://api.telegram.org/bot{self.config['telegram']['bot_token']}/sendMessage"
                payload = {
                    'chat_id': chat_id,
                    'text': f"{emoji} *ALERTA {severity}*\n\n{message}",
                    'parse_mode': 'Markdown'
                }

                response = requests.post(url, json=payload, timeout=15)
                response.raise_for_status()

            logger.info(f"Telegram enviado para {self.config['telegram']['chat_ids']}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar Telegram: {e}")
            return False

    def sendAlert(self, alert: Dict) -> bool:
        """Envia alerta por todos os canais configurados."""
        severity = alert.get('severity', 'MEDIUM')
        platform = alert.get('platform', 'geral')
        message = alert.get('message', 'Alerta sem mensagem')
        action = alert.get('action', 'Verificar sistema')

        # Formatar mensagem completa
        full_message = f"""🚨 ALERTA AUTOMÁTICO

📊 Plataforma: {platform.upper()}
⚠️ Severidade: {severity}
📝 Problema: {message}
💡 Ação Recomendada: {action}

---
Sistema de Monitoramento @moacir.moper
Data: automática"""

        subject = f"Alerta {severity}: {platform} - @moacir.moper"

        # Enviar por todos os canais
        results = []
        results.append(self.sendEmailAlert(subject, full_message, severity))
        results.append(self.sendWhatsAppAlert(full_message, severity))
        results.append(self.sendTelegramAlert(full_message, severity))

        # Retorna True se pelo menos um canal funcionou
        return any(results)

    def sendDailyReport(self, report: Dict) -> bool:
        """Envia relatório diário consolidado."""
        status = report.get('status', 'UNKNOWN')
        alerts_total = report.get('alerts', {}).get('total', 0)

        emoji = {'CRITICAL': '🚨', 'WARNING': '⚠️', 'GOOD': '✅'}.get(status, '📊')

        message = f"""{emoji} RELATÓRIO DIÁRIO - @moacir.moper

📊 Status Geral: {status}
🚨 Alertas: {alerts_total}

👥 Métricas Atuais:
• Instagram: {report.get('metrics', {}).get('instagram', {}).get('followers', 0):,} seguidores
• TikTok: {report.get('metrics', {}).get('tiktok', {}).get('followers', 0):,} seguidores
• YouTube: {report.get('metrics', {}).get('youtube', {}).get('subscribers', 0):,} inscritos
• TOTAL: {report.get('metrics', {}).get('overall', {}).get('total_followers', 0):,} seguidores

💡 Recomendações:
{chr(10).join('• ' + rec for rec in report.get('recommendations', []))}

---
Relatório automático gerado pelo sistema de monitoramento."""

        subject = f"📊 Relatório Diário: {status} - @moacir.moper"

        # Enviar relatório por email (WhatsApp/Telegram podem ser muito longos)
        return self.sendEmailAlert(subject, message, status)

def main():
    """Testa sistema de alertas."""
    alert_system = AlertSystem()

    # Teste com alerta de exemplo
    test_alert = {
        'severity': 'MEDIUM',
        'platform': 'instagram',
        'message': 'Engajamento abaixo do esperado (1.8% vs 2.0% mínimo)',
        'action': 'Aumentar interação nos próximos posts, testar stories interativos'
    }

    print("🧪 Testando sistema de alertas...")

    # Por enquanto, apenas email está habilitado
    if alert_system.config['email']['enabled']:
        print("📧 Testando email...")
        success = alert_system.sendAlert(test_alert)
        if success:
            print("✅ Email enviado com sucesso!")
        else:
            print("❌ Falha no envio do email")
    else:
        print("📧 Email desabilitado (configurar ALERT_EMAIL_FROM e ALERT_EMAIL_PASSWORD)")

    print("\n💡 Para habilitar WhatsApp/Telegram:")
    print("   - Configure WHATSAPP_API_KEY no .env")
    print("   - Configure TELEGRAM_BOT_TOKEN no .env")

if __name__ == "__main__":
    main()