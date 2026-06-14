#!/usr/bin/env python3
"""
Webhook server dos bots WhatsApp — Moper Máquinas e Espaço Laika.

Cada cliente usa uma plataforma diferente:
    - Moper → WhatsApp Business API oficial (Meta / graph.facebook.com), número novo
              dedicado à IA. Webhook precisa de verificação GET (hub.challenge) e
              recebe mensagens em POST no formato Meta.
    - Laika → Evolution API (não-oficial, via QR code). Webhook recebe mensagens em
              POST no formato Evolution.

Rotas:
    GET  /webhook/moper  → verificação do webhook Meta (hub.challenge)
    POST /webhook/moper  → mensagens da Moper Máquinas (formato Meta)
    POST /webhook/laika  → mensagens do Espaço Laika   (formato Evolution)

Configuração no .env (Moper):
    MOPER_WHATSAPP_PHONE_NUMBER_ID=  (do painel Meta Developer — Etapa 2 Produção)
    MOPER_WHATSAPP_TOKEN=            (token de acesso permanente Meta)
    MOPER_WHATSAPP_VERIFY_TOKEN=     (string que você inventar, ex: moper_secret_2026)

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
    from execution.whatsappResponder import setActiveToken
    MOPER_ENABLED = True
    logger.info("WhatsApp responder Moper carregado ✅")
except Exception as e:
    logger.error(f"WhatsApp responder Moper indisponível: {e}")
    MOPER_ENABLED = False
    def handleMoperMessage(sender, text): pass
    def setActiveToken(token): pass

try:
    from execution.whatsappResponderLaika import handleIncomingMessage as handleLaikaMessage
    LAIKA_ENABLED = True
    logger.info("WhatsApp responder Laika carregado ✅")
except Exception as e:
    logger.error(f"WhatsApp responder Laika indisponível: {e}")
    LAIKA_ENABLED = False
    def handleLaikaMessage(sender, text): pass

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("MOPER_WHATSAPP_VERIFY_TOKEN", "moper_secret_2026")


# ─────────────────────────── Moper — Meta API ───────────────────────────

@app.route("/webhook/moper", methods=["GET"])
def verifyMoperWebhook():
    """Verificação do webhook Meta — a Meta envia um desafio e espera a resposta."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook Moper (Meta) verificado com sucesso ✅")
        return challenge, 200

    logger.warning("Falha na verificação do webhook Moper — token incorreto")
    return "Forbidden", 403


@app.route("/webhook/moper", methods=["POST"])
def receiveMoperMessage():
    """Recebe mensagens da Moper Máquinas via WhatsApp Business API (Meta)."""
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
            logger.info(f"[Moper] Mensagem ignorada (tipo: {msg_type}) de {sender}")
            return jsonify({"status": "ignored"}), 200

        text = message["text"]["body"]
        logger.info(f"[Moper] Mensagem de {sender}: {text[:60]}...")
        handleMoperMessage(sender, text)

    except (KeyError, IndexError) as e:
        logger.error(f"Erro ao processar payload Moper: {e}")

    return jsonify({"status": "ok"}), 200


@app.route("/admin/update-token", methods=["POST"])
def updateToken():
    """Atualiza o token WhatsApp Meta (Moper) em runtime sem reimplantar.

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


# ─────────────────────────── Laika — Evolution API ───────────────────────────

@app.route("/webhook/laika", methods=["POST"])
def receiveLaikaMessage():
    """Recebe mensagens do Espaço Laika via Evolution API."""
    data = request.get_json() or {}

    try:
        event = data.get("event", "")
        if event != "messages.upsert":
            return jsonify({"status": "ignored"}), 200

        msg_data = data.get("data", {})
        key = msg_data.get("key", {})

        # Ignora mensagens enviadas pelo próprio bot
        if key.get("fromMe", False):
            return jsonify({"status": "from_me"}), 200

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
            return jsonify({"status": "no_text"}), 200

        logger.info(f"[Laika] Mensagem de {sender}: {text[:60]}...")
        handleLaikaMessage(sender, text)

    except (KeyError, IndexError, AttributeError) as e:
        logger.error(f"Erro ao processar payload Laika: {e}")

    return jsonify({"status": "ok"}), 200


# ─────────────────────────── Catálogo / health ───────────────────────────

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
    logger.info(f"Servidor WhatsApp (Moper via Meta + Laika via Evolution) iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port)
