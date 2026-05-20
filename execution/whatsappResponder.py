#!/usr/bin/env python3
"""
Claude AI responder para o bot WhatsApp da Moper Máquinas.

Recebe a mensagem do cliente, consulta o Claude com contexto da Moper,
e envia a resposta de volta via WhatsApp Business API.
"""

import logging
import os

import requests
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PHONE_NUMBER_ID = os.getenv("MOPER_WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_TOKEN  = os.getenv("MOPER_WHATSAPP_TOKEN")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MOPER_SYSTEM_PROMPT = """Você é o assistente virtual da Moper Máquinas, empresa de Dourados/MS \
especializada em máquinas para movimentação de cargas e construção civil.

Produtos e serviços:
- Empilhadeiras elétricas e a combustão (capacidade 1,5t a 5t)
- Paleteiras manuais e elétricas
- Mini escavadeiras e equipamentos de terraplanagem
- Venda e locação de equipamentos

Tom de resposta: profissional, direto, confiante. Sem emojis excessivos.

Regras:
1. Responda a dúvida do cliente de forma clara e objetiva.
2. Nunca invente preços, prazos ou especificações — diga que varia conforme o modelo e ofereça \
   conectar com um consultor.
3. Se a pergunta for totalmente fora do escopo (máquinas/equipamentos/locação), responda \
   brevemente e redirecione para o assunto da empresa.
4. Máximo 3 parágrafos curtos por resposta.
5. Sempre termine oferecendo mais ajuda ou sugerindo falar com a equipe para detalhes técnicos.
"""

FALLBACK_MESSAGE = (
    "Olá! Nosso assistente está temporariamente indisponível. "
    "Em breve nossa equipe entrará em contato. Obrigado!"
)


def sendWhatsappMessage(to: str, text: str):
    """Envia mensagem de texto via WhatsApp Business API."""
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    r.raise_for_status()
    logger.info(f"Resposta enviada para {to}")


def generateReply(userMessage: str) -> str:
    """Chama o Claude e retorna a resposta gerada."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=MOPER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": userMessage}],
    )
    return response.content[0].text


def handleIncomingMessage(sender: str, text: str):
    """Processa a mensagem recebida: gera resposta e envia de volta."""
    try:
        reply = generateReply(text)
        sendWhatsappMessage(sender, reply)
    except Exception as e:
        logger.error(f"Erro ao responder {sender}: {e}")
        try:
            sendWhatsappMessage(sender, FALLBACK_MESSAGE)
        except Exception:
            logger.error(f"Falhou também o fallback para {sender}")
