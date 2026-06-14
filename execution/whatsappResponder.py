#!/usr/bin/env python3
"""
Claude AI responder para o bot WhatsApp da Moper Máquinas.

Funcionalidades:
- Memória de conversa por 30 dias (PostgreSQL)
- Horário de atendimento: Seg-Sex 8h-18h, Sáb 8h-13h
- Transferência para humano quando solicitado ou quando IA não souber responder
"""

import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from anthropic import Anthropic
from dotenv import load_dotenv

from execution.conversationMemory import (
    addMessage,
    getHistory,
    initDB,
    isTransferred,
    markTransferred,
    purgeExpired,
)

load_dotenv()

logger = logging.getLogger(__name__)

PHONE_NUMBER_ID = os.getenv("MOPER_WHATSAPP_PHONE_NUMBER_ID")
TZ = ZoneInfo("America/Sao_Paulo")

# Token mutável — pode ser atualizado em runtime via /admin/update-token
_active_token = os.getenv("MOPER_WHATSAPP_TOKEN", "")


def setActiveToken(new_token: str):
    global _active_token
    _active_token = new_token
    logger.info(f"Token atualizado em runtime: ...{new_token[-20:]}")


def getActiveToken() -> str:
    return _active_token


client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Inicializa banco na importação do módulo
try:
    initDB()
except Exception as e:
    logger.error(f"Falha ao inicializar banco: {e}")

MOPER_SYSTEM_PROMPT = """Você é o assistente virtual da Moper Máquinas, empresa especializada \
em máquinas para movimentação de cargas e construção civil.

== PORTFÓLIO E ESTOQUE ATUAL ==

Use as informações de estoque para informar prazo e condições de pagamento corretas.
EM ESTOQUE = entrega ~10 dias, entrada (30%) à vista.
SOB ENCOMENDA = entrega ~90 dias, entrada (30%) parcelável em até 3x.

Empilhadeiras Elétricas Moper® (rápidas, silenciosas, ideais para ambientes internos):
- 2 Toneladas        → SOB ENCOMENDA
- 2,5 Toneladas      → SOB ENCOMENDA
- 3 Toneladas        → EM ESTOQUE (1 unidade)
- 3,5 Toneladas      → SOB ENCOMENDA

Empilhadeira Telescópica Moper® 1,5 Toneladas:
  Off-road, compacta, para chão acidentado e terrenos irregulares.
  → EM ESTOQUE (2 unidades)

Paleteiras Elétricas Moper® (movem a carga sozinhas, sem esforço físico):
- 1,5 Toneladas      → EM ESTOQUE (5 unidades)
- 2 Toneladas        → EM ESTOQUE (5 unidades)
- 3 Toneladas        → EM ESTOQUE (4 unidades)

Paleteira Elevatória Semi-Elétrica Moper® 1 Tonelada:
  Diferencial exclusivo: sobe em cima de carreta e entra dentro de caminhão.
  → SOB ENCOMENDA

Paleteira Elétrica Moper® Total 1 Tonelada:
  Diferencial exclusivo: sobe em cima de carreta e entra dentro de caminhão.
  → EM ESTOQUE (1 unidade)

Carretas Moper® (auxiliares para transportar paleteiras):
- 2 Toneladas        → EM ESTOQUE (2 unidades)
- 5 Toneladas        → EM ESTOQUE (1 unidade)

== DIFERENCIAIS DA MOPER ==
- Melhor preço do mercado sem abrir mão da qualidade
- Paleteiras Elevatória e Total: únicas com capacidade de subir em carreta e caminhão
- Empilhadeira Telescópica: solução completa para ambientes externos e chão irregular
- Atendimento direto e consultivo — sem enrolação

== FORMAS DE PAGAMENTO ==

Produto sob encomenda (fora do estoque):
- Prazo de entrega: aproximadamente 90 dias
- Entrada (30%): pode ser parcelada em até 3x
- Restante (70%): pode ser parcelado em até 10x no cartão

Produto em estoque:
- Prazo de entrega: aproximadamente 10 dias
- Entrada (30%): à vista (não parcela)
- Restante (70%): pode ser parcelado em até 10x no cartão

== CONTATO DA EQUIPE ==
- WhatsApp / Telefone: +55 47 99232-5747
- Site: https://www.mopermaquinas.com.br/

== REGRAS DE ATENDIMENTO ==
Tom: profissional, direto e confiante. Sem emojis excessivos.

1. Responda de forma clara e objetiva.
2. Nunca invente preços exatos — diga que o valor varia conforme configuração e ofereça \
   conectar com um consultor via +55 47 99232-5747 ou pelo site.
3. Se a pergunta estiver fora do escopo, responda brevemente e redirecione para os produtos.
4. Máximo 3 parágrafos curtos por resposta.
5. Ao final, sempre ofereça mais ajuda ou sugira falar com a equipe para fechar negócio.
6. IMPORTANTE: Se não souber responder com segurança, responda EXATAMENTE com [TRANSFERIR] \
   e nada mais."""

TRANSFER_KEYWORDS = [
    "atendente", "humano", "pessoa", "falar com alguém", "falar com um",
    "quero falar", "não quero robô", "não é robô", "transferir", "consultor",
    "vendedor", "falar com vendedor", "falar com consultor",
]

MSG_FORA_HORARIO = (
    "Olá! Obrigado por entrar em contato com a Moper Máquinas. 😊\n\n"
    "Nosso horário de atendimento é:\n"
    "• Segunda a Sexta: 8h às 18h\n"
    "• Sábado: 8h às 13h\n\n"
    "Em breve nossa equipe retornará seu contato. "
    "Se preferir, envie sua dúvida que respondemos assim que possível!"
)

MSG_TRANSFERENCIA = (
    "Entendido! Vou transferir você para um de nossos consultores. 👨‍💼\n\n"
    "Em breve a equipe da Moper Máquinas entrará em contato. "
    "Se preferir, ligue diretamente para nós!"
)

FALLBACK_MESSAGE = (
    "Olá! Nosso assistente está temporariamente indisponível. "
    "Em breve nossa equipe entrará em contato. Obrigado!"
)


def isBusinessHours() -> bool:
    """Verifica se está dentro do horário de atendimento da Moper."""
    now = datetime.now(TZ)
    weekday = now.weekday()  # 0=Seg, 5=Sáb, 6=Dom
    hour = now.hour + now.minute / 60

    if weekday < 5:  # Seg a Sex
        return 8.0 <= hour < 18.0
    if weekday == 5:  # Sábado
        return 8.0 <= hour < 13.0
    return False  # Domingo


def wantsHuman(text: str) -> bool:
    """Verifica se o cliente está pedindo para falar com um humano."""
    lower = text.lower()
    return any(kw in lower for kw in TRANSFER_KEYWORDS)


def sendWhatsappMessage(to: str, text: str):
    """Envia mensagem de texto via WhatsApp Business API."""
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {getActiveToken()}",
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
    logger.info(f"Mensagem enviada para {to}")


def generateReply(sender: str, userMessage: str) -> str:
    """Chama o Claude com histórico de conversa e retorna a resposta."""
    history = getHistory(sender)
    history.append({"role": "user", "content": userMessage})

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=MOPER_SYSTEM_PROMPT,
        messages=history,
    )
    return response.content[0].text


def handleIncomingMessage(sender: str, text: str):
    """Processa a mensagem recebida com todas as regras de negócio."""

    # 1. Conversa já transferida para humano — silêncio total
    if isTransferred(sender):
        logger.info(f"Mensagem de {sender} ignorada — conversa transferida para humano")
        return

    # 2. Fora do horário de atendimento
    if not isBusinessHours():
        logger.info(f"Fora do horário — respondendo {sender} com mensagem de fechado")
        try:
            sendWhatsappMessage(sender, MSG_FORA_HORARIO)
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem fora de horário para {sender}: {e}")
        return

    # 3. Cliente pedindo humano explicitamente
    if wantsHuman(text):
        logger.info(f"Cliente {sender} pediu transferência para humano")
        try:
            sendWhatsappMessage(sender, MSG_TRANSFERENCIA)
            markTransferred(sender)
        except Exception as e:
            logger.error(f"Erro ao transferir {sender}: {e}")
        return

    # 4. Gera resposta com IA
    try:
        addMessage(sender, "user", text)
        reply = generateReply(sender, text)

        # IA sinalizou que não sabe responder
        if "[TRANSFERIR]" in reply:
            logger.info(f"IA não soube responder para {sender} — transferindo")
            sendWhatsappMessage(sender, MSG_TRANSFERENCIA)
            markTransferred(sender)
            return

        addMessage(sender, "assistant", reply)
        sendWhatsappMessage(sender, reply)

        # Limpeza periódica de mensagens antigas (1% das chamadas)
        import random
        if random.random() < 0.01:
            purgeExpired()

    except Exception as e:
        logger.error(f"Erro ao responder {sender}: {e}")
        try:
            sendWhatsappMessage(sender, FALLBACK_MESSAGE)
        except Exception:
            logger.error(f"Falhou também o fallback para {sender}")
