#!/usr/bin/env python3
"""
WhatsApp Business API webhook server — Moper Máquinas.

Recebe mensagens dos clientes e envia para o respondedor com Claude AI.

Configuração no .env:
    MOPER_WHATSAPP_PHONE_NUMBER_ID=  (do painel Meta Developer)
    MOPER_WHATSAPP_TOKEN=            (token de acesso Meta)
    MOPER_WHATSAPP_VERIFY_TOKEN=     (string que você inventar, ex: moper_secret_2026)

Uso local (teste):
    PYTHONPATH=. python execution/whatsappWebhook.py

Produção (Railway sobe automaticamente via Procfile):
    web: PYTHONPATH=. python execution/whatsappWebhook.py
"""

import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from execution.whatsappResponder import handleIncomingMessage, setActiveToken

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("MOPER_WHATSAPP_VERIFY_TOKEN", "moper_secret_2026")


@app.route("/webhook", methods=["GET"])
def verifyWebhook():
    """Verificação do webhook — Meta envia um desafio e espera a resposta."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verificado com sucesso ✅")
        return challenge, 200

    logger.warning("Falha na verificação do webhook — token incorreto")
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def receiveMessage():
    """Recebe mensagens do WhatsApp e despacha para o respondedor."""
    data = request.get_json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]["value"]

        if "messages" not in changes:
            return jsonify({"status": "no_message"}), 200

        message = changes["messages"][0]
        sender = message["from"]
        msg_type = message.get("type", "")

        if msg_type != "text":
            logger.info(f"Mensagem ignorada (tipo: {msg_type}) de {sender}")
            return jsonify({"status": "ignored"}), 200

        text = message["text"]["body"]
        logger.info(f"Mensagem de {sender}: {text[:60]}...")

        handleIncomingMessage(sender, text)

    except (KeyError, IndexError) as e:
        logger.error(f"Erro ao processar payload: {e}")

    return jsonify({"status": "ok"}), 200


@app.route("/admin/update-token", methods=["POST"])
def updateToken():
    """Atualiza o token WhatsApp em runtime sem precisar reimplantar.

    Uso:
        curl -X POST https://<host>/admin/update-token \
             -H "Authorization: Bearer <VERIFY_TOKEN>" \
             -H "Content-Type: application/json" \
             -d '{"token": "NOVO_TOKEN_AQUI"}'
    """
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {VERIFY_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    new_token = (data or {}).get("token", "").strip()
    if not new_token:
        return jsonify({"error": "Campo 'token' ausente ou vazio"}), 400

    setActiveToken(new_token)
    return jsonify({"status": "ok", "token_suffix": f"...{new_token[-20:]}"}), 200


@app.route("/", methods=["GET"])
def healthCheck():
    """Verificação de saúde — Railway usa isso para saber se o servidor está de pé."""
    return jsonify({"status": "Moper WhatsApp Bot rodando ✅"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    token = os.getenv("MOPER_WHATSAPP_TOKEN", "")
    logger.info(f"Servidor WhatsApp Moper iniciando na porta {port}")
    logger.info(f"TOKEN carregado: ...{token[-20:] if token else 'VAZIO'}")
    app.run(host="0.0.0.0", port=port)
