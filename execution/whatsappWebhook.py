#!/usr/bin/env python3
"""
Webhook server dos bots WhatsApp — Moper Máquinas e Espaço Laika.

Ambos os bots usam Evolution API (não-oficial, via QR code). Cada cliente tem
sua própria instância no Evolution e uma rota dedicada aqui.

Rotas:
    POST /webhook/moper  → bot Moper Máquinas (instância pai_moper_maquinas)
    POST /webhook/laika  → bot Espaço Laika   (instância pai_espaco_laika)

Uso local (teste):
    PYTHONPATH=. python execution/whatsappWebhook.py

Produção (Railway sobe automaticamente via Procfile):
    web: gunicorn execution.whatsappWebhook:app ...
"""

import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

try:
    from execution.whatsappResponder import handleIncomingMessage as handleMoperMessage
    MOPER_ENABLED = True
    logger.info("WhatsApp responder Moper carregado ✅")
except Exception as e:
    logger.error(f"WhatsApp responder Moper indisponível: {e}")
    MOPER_ENABLED = False
    def handleMoperMessage(sender, text): pass

try:
    from execution.whatsappResponderLaika import handleIncomingMessage as handleLaikaMessage
    LAIKA_ENABLED = True
    logger.info("WhatsApp responder Laika carregado ✅")
except Exception as e:
    logger.error(f"WhatsApp responder Laika indisponível: {e}")
    LAIKA_ENABLED = False
    def handleLaikaMessage(sender, text): pass

app = Flask(__name__)


def parseEvolutionMessage(data: dict):
    """Extrai (sender, text) de um payload Evolution API.

    Retorna (None, None) quando o payload não é uma mensagem de texto de cliente
    (evento diferente de messages.upsert, mensagem do próprio bot, ou sem texto).
    """
    event = data.get("event", "")
    if event != "messages.upsert":
        return None, None

    msg_data = data.get("data", {})
    key = msg_data.get("key", {})

    # Ignora mensagens enviadas pelo próprio bot
    if key.get("fromMe", False):
        return None, None

    # Extrai remetente — formato: "5567912345678@s.whatsapp.net"
    remote_jid = key.get("remoteJid", "")
    sender = remote_jid.replace("@s.whatsapp.net", "").replace("@c.us", "")

    # Extrai texto — Evolution API pode enviar em campos diferentes
    message = msg_data.get("message", {})
    text = (
        message.get("conversation")
        or message.get("extendedTextMessage", {}).get("text")
        or ""
    ).strip()

    if not sender or not text:
        return None, None

    return sender, text


@app.route("/webhook/moper", methods=["POST"])
def receiveMoperMessage():
    """Recebe mensagens da Moper Máquinas via Evolution API."""
    data = request.get_json()

    try:
        sender, text = parseEvolutionMessage(data or {})
        if not sender:
            return jsonify({"status": "ignored"}), 200

        logger.info(f"[Moper] Mensagem de {sender}: {text[:60]}...")
        handleMoperMessage(sender, text)

    except (KeyError, IndexError, AttributeError) as e:
        logger.error(f"Erro ao processar payload Moper: {e}")

    return jsonify({"status": "ok"}), 200


@app.route("/webhook/laika", methods=["POST"])
def receiveLaikaMessage():
    """Recebe mensagens do Espaço Laika via Evolution API."""
    data = request.get_json()

    try:
        sender, text = parseEvolutionMessage(data or {})
        if not sender:
            return jsonify({"status": "ignored"}), 200

        logger.info(f"[Laika] Mensagem de {sender}: {text[:60]}...")
        handleLaikaMessage(sender, text)

    except (KeyError, IndexError, AttributeError) as e:
        logger.error(f"Erro ao processar payload Laika: {e}")

    return jsonify({"status": "ok"}), 200


@app.route("/paleteiras")
def catalogoPaleteiras():
    """Página de catálogo de paleteiras auto elevatórias Moper."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    return send_from_directory(static_dir, "paleteiras.html")


@app.route("/paleteiras/img/<path:filename>")
def imagensPaleteiras(filename):
    """Serve imagens do catálogo de paleteiras."""
    img_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "img")
    return send_from_directory(img_dir, filename)


@app.route("/", methods=["GET"])
def healthCheck():
    """Verificação de saúde — Railway usa isso para saber se o servidor está de pé."""
    return jsonify({
        "status": "WhatsApp Bots rodando ✅",
        "moper": MOPER_ENABLED,
        "laika": LAIKA_ENABLED,
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Servidor WhatsApp (Moper + Laika via Evolution) iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port)
