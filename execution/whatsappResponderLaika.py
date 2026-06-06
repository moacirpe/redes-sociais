#!/usr/bin/env python3
"""
Respondedor WhatsApp do Espaço Laika via Evolution API.

Diferente da Moper (que usa Meta API oficial), o Laika usa Evolution API
(não-oficial, via QR code) para manter o celular funcionando normalmente
e permitir que o humano assuma conversas pelo WhatsApp comum.

Configuração no .env:
    EVOLUTION_API_URL=http://<VPS_IP>:8080
    EVOLUTION_API_KEY=<chave_definida_no_docker_stack>
    LAIKA_EVOLUTION_INSTANCE=laika
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

EVOLUTION_URL = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_KEY = os.getenv("EVOLUTION_API_KEY", "")
INSTANCE = os.getenv("LAIKA_EVOLUTION_INSTANCE", "laika")
TZ = ZoneInfo("America/Sao_Paulo")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

try:
    initDB()
except Exception as e:
    logger.error(f"Falha ao inicializar banco: {e}")

# ---------------------------------------------------------------------------
# System prompt — preencher com dados reais do Espaço Laika
# ---------------------------------------------------------------------------

LAIKA_SYSTEM_PROMPT = """Você é o assistente virtual do Espaço Laika, espaço para eventos \
localizado em Dourados/MS.

== SOBRE O ESPAÇO ==
Endereço: Rua Takeo Takemoto, 50 – Altos do Indaiá – Dourados/MS
Proprietário: Moacir Pereira

[TODO: preencher capacidade, estrutura, diferenciais]

== TIPOS DE EVENTO ATENDIDOS ==
Casamentos, aniversários, formaturas, confraternizações e outros eventos sociais.

== VALORES E CONDIÇÕES ==
[TODO: preencher tabela de preços e pacotes de locação]

== DISPONIBILIDADE ==
[TODO: listar datas já reservadas ou bloquear via atualização deste prompt]

== FLUXO DE ATENDIMENTO ==
Seu objetivo é coletar as seguintes informações do cliente, uma de cada vez, \
de forma natural e acolhedora:
1. Data desejada para o evento
2. Tipo de evento (casamento, aniversário, formatura, etc.)
3. Número aproximado de convidados
4. Nome completo do cliente e melhor telefone para contato

Depois de coletar os 4 dados, confirme as informações, informe se a data \
está disponível (conforme as datas bloqueadas acima) e diga que nossa equipe \
entrará em contato em breve para fechar os detalhes.

== REGRAS DE ATENDIMENTO ==
Tom: caloroso, acolhedor e profissional. Pode usar emojis com moderação.

1. Colete as informações uma por vez — não bombardeie o cliente com várias perguntas.
2. Nunca confirme valores exatos sem consultar a equipe — diga que depende do \
   pacote e que a equipe vai detalhar.
3. Máximo 3 parágrafos curtos por resposta.
4. Se não souber responder com segurança, responda EXATAMENTE com [TRANSFERIR] e nada mais."""

# ---------------------------------------------------------------------------
# Mensagens fixas
# ---------------------------------------------------------------------------

TRANSFER_KEYWORDS = [
    "atendente", "humano", "pessoa", "falar com alguém", "falar com um",
    "quero falar", "não quero robô", "transferir", "dono", "moacir",
    "falar com o responsável",
]

MSG_FORA_HORARIO = (
    "Olá! Obrigado por entrar em contato com o Espaço Laika. 🌿\n\n"
    "Nosso horário de atendimento é:\n"
    "• Segunda a Sexta: 8h às 18h\n"
    "• Sábado: 8h às 13h\n\n"
    "Deixe sua mensagem que retornamos assim que possível!"
)

MSG_TRANSFERENCIA = (
    "Entendido! Vou passar seu contato para nossa equipe. 😊\n\n"
    "Em breve o Espaço Laika entrará em contato com você. "
    "Obrigado pela preferência!"
)

FALLBACK_MESSAGE = (
    "Olá! Nosso assistente está temporariamente indisponível. "
    "Em breve nossa equipe entrará em contato. Obrigado!"
)


# ---------------------------------------------------------------------------
# Funções de integração com Evolution API
# ---------------------------------------------------------------------------

def sendWhatsappMessage(to: str, text: str):
    """Envia mensagem via Evolution API."""
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    payload = {"number": to, "text": text}
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    r.raise_for_status()
    logger.info(f"Mensagem enviada para {to}")


# ---------------------------------------------------------------------------
# Lógica de negócio
# ---------------------------------------------------------------------------

def isBusinessHours() -> bool:
    now = datetime.now(TZ)
    weekday = now.weekday()
    hour = now.hour + now.minute / 60
    if weekday < 5:
        return 8.0 <= hour < 18.0
    if weekday == 5:
        return 8.0 <= hour < 13.0
    return False


def wantsHuman(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in TRANSFER_KEYWORDS)


def generateReply(sender: str, userMessage: str) -> str:
    # Prefixo "laika_" no sender para separar memória do Moper no mesmo banco
    history = getHistory(f"laika_{sender}")
    history.append({"role": "user", "content": userMessage})
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=LAIKA_SYSTEM_PROMPT,
        messages=history,
    )
    return response.content[0].text


def handleIncomingMessage(sender: str, text: str):
    """Processa mensagem recebida do cliente do Espaço Laika."""
    laika_sender = f"laika_{sender}"

    if isTransferred(laika_sender):
        logger.info(f"Mensagem de {sender} ignorada — conversa transferida")
        return

    if not isBusinessHours():
        logger.info(f"Fora do horário — respondendo {sender}")
        try:
            sendWhatsappMessage(sender, MSG_FORA_HORARIO)
        except Exception as e:
            logger.error(f"Erro ao enviar msg fora de horário para {sender}: {e}")
        return

    if wantsHuman(text):
        logger.info(f"Cliente {sender} pediu transferência")
        try:
            sendWhatsappMessage(sender, MSG_TRANSFERENCIA)
            markTransferred(laika_sender)
        except Exception as e:
            logger.error(f"Erro ao transferir {sender}: {e}")
        return

    try:
        addMessage(laika_sender, "user", text)
        reply = generateReply(sender, text)

        if "[TRANSFERIR]" in reply:
            logger.info(f"IA transferindo {sender}")
            sendWhatsappMessage(sender, MSG_TRANSFERENCIA)
            markTransferred(laika_sender)
            return

        addMessage(laika_sender, "assistant", reply)
        sendWhatsappMessage(sender, reply)

        import random
        if random.random() < 0.01:
            purgeExpired()

    except Exception as e:
        logger.error(f"Erro ao responder {sender}: {e}")
        try:
            sendWhatsappMessage(sender, FALLBACK_MESSAGE)
        except Exception:
            logger.error(f"Fallback também falhou para {sender}")
