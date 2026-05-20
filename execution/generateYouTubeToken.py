#!/usr/bin/env python3
"""
Gerador de Token OAuth — YouTube (Google)

Abre o navegador no fluxo de autorização do Google.
Salva o API Key e Channel ID no .env automaticamente.

Uso:
    python execution/generateYouTubeToken.py

Pré-requisito:
    1. Acesse https://console.cloud.google.com com moacirper@gmail.com
    2. Crie um projeto (ex: "Moper Social Monitor")
    3. APIs e Serviços → Biblioteca → Ative:
       - YouTube Data API v3
       - YouTube Analytics API
    4. APIs e Serviços → Credenciais → Criar credencial:
       - API Key → copie e cole em YOUTUBE_API_KEY no .env
       - OAuth 2.0 → Tipo: Aplicativo da Web
       - URI de redirecionamento autorizado: http://localhost:8888/callback
       - Baixe o JSON e salve como credentials/google_credentials.json
"""

import os
import sys
import json
import webbrowser
import threading
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv, set_key

load_dotenv()

CREDENTIALS_FILE = "credentials/google_credentials.json"
TOKEN_FILE        = "credentials/google_token.json"
ENV_FILE          = ".env"
REDIRECT_URI      = "http://localhost:8888/callback"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

GENERIC_YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

captured_code  = None
captured_error = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code, captured_error
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in params:
            captured_code = params["code"][0]
            self._respond("✅ Autorização recebida! Pode fechar esta aba.")
        elif "error" in params:
            captured_error = params.get("error", ["Erro"])[0]
            self._respond(f"❌ Erro: {captured_error}")
        else:
            self._respond("⚠️ Resposta inesperada.")

    def _respond(self, msg):
        html = f"<html><body style='font-family:sans-serif;text-align:center;padding:60px'><h2>{msg}</h2></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, *args):
        pass


def startServer():
    HTTPServer(("localhost", 8888), CallbackHandler).handle_request()


def loadCredentials() -> dict:
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Arquivo não encontrado: {CREDENTIALS_FILE}")
        print("\nPara obter este arquivo:")
        print("  1. console.cloud.google.com → Credenciais")
        print("  2. Criar credencial → OAuth 2.0 → Aplicativo da Web")
        print("  3. URI redirecionamento: http://localhost:8888/callback")
        print("  4. Baixar JSON → salvar como credentials/google_credentials.json")
        sys.exit(1)

    with open(CREDENTIALS_FILE) as f:
        data = json.load(f)

    # Suporte a formato "web" ou "installed"
    return data.get("web") or data.get("installed") or {}


def buildAuthUrl(creds: dict) -> str:
    params = urllib.parse.urlencode({
        "client_id":     creds["client_id"],
        "redirect_uri":  REDIRECT_URI,
        "response_type": "code",
        "scope":         " ".join(SCOPES),
        "access_type":   "offline",
        "prompt":        "consent",
    })
    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"


def propagateYoutubeApiKeyToClients(apiKey: str):
    """Populate per-client YouTube API key env vars from a generic key."""
    client_keys = [
        "MOACIR_YOUTUBE_API_KEY",
        "NAMASA_YOUTUBE_API_KEY",
        "MOPER_YOUTUBE_API_KEY",
        "LAIKA_YOUTUBE_API_KEY",
    ]
    for key in client_keys:
        if not os.getenv(key):
            saveToEnv(key, apiKey)


def exchangeCode(code: str, creds: dict) -> dict:
    import requests
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "code":          code,
        "client_id":     creds["client_id"],
        "client_secret": creds["client_secret"],
        "redirect_uri":  REDIRECT_URI,
        "grant_type":    "authorization_code",
    })
    r.raise_for_status()
    return r.json()


def fetchChannels(accessToken: str) -> list:
    import requests
    r = requests.get("https://www.googleapis.com/youtube/v3/channels", params={
        "part":        "snippet,statistics",
        "mine":        "true",
        "access_token": accessToken,
    })
    r.raise_for_status()
    return r.json().get("items", [])


def saveToEnv(key: str, value: str):
    set_key(ENV_FILE, key, value)
    print(f"  ✅ {key} salvo no .env")


def main():
    print("\n" + "="*60)
    print("   Gerador de Token YouTube — Google OAuth")
    print("="*60 + "\n")

    creds = loadCredentials()
    if not creds.get("client_id"):
        print("❌ Credenciais inválidas no arquivo JSON.")
        sys.exit(1)

    # Servidor local
    threading.Thread(target=startServer, daemon=True).start()

    # Abrir navegador
    authUrl = buildAuthUrl(creds)
    print("🌐 Abrindo navegador para autorização Google...")
    webbrowser.open(authUrl)

    # Aguardar callback
    print("⏳ Aguardando autorização no navegador (2 min)...")
    elapsed = 0
    while captured_code is None and captured_error is None and elapsed < 120:
        time.sleep(1)
        elapsed += 1

    if captured_error:
        print(f"❌ Erro: {captured_error}")
        sys.exit(1)
    if captured_code is None:
        print("❌ Timeout.")
        sys.exit(1)

    print("✅ Código recebido!")

    # Trocar por token
    print("🔄 Obtendo tokens...")
    tokenData = exchangeCode(captured_code, creds)

    # Salvar token em arquivo
    os.makedirs("credentials", exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokenData, f, indent=2)
    print(f"✅ Token salvo em {TOKEN_FILE}")

    # Usar chave API genérica para preencher variáveis de cada cliente
    if GENERIC_YOUTUBE_API_KEY:
        propagateYoutubeApiKeyToClients(GENERIC_YOUTUBE_API_KEY)
    else:
        print("⚠️  YOUTUBE_API_KEY não encontrado no .env. Se você tiver uma API Key, adicione YOUTUBE_API_KEY=... e rode novamente para preencher os clientes.")

    # Buscar canais
    accessToken = tokenData.get("access_token")
    print("\n🔍 Buscando canais YouTube...")
    channels = fetchChannels(accessToken)

    knownChannels = {
        "namasa":  ("NAMASA_YOUTUBE_CHANNEL_ID",),
        "namasa_mp": ("NAMASA_YOUTUBE_CHANNEL_ID",),
        "moper":   ("MOPER_YOUTUBE_CHANNEL_ID",),
        "moacir":  ("MOACIR_YOUTUBE_CHANNEL_ID",),
    }

    print(f"\n📺 {len(channels)} canal(is) encontrado(s):\n")
    for ch in channels:
        snippet = ch.get("snippet", {})
        stats   = ch.get("statistics", {})
        chId    = ch["id"]
        chName  = snippet.get("title", "")
        subs    = int(stats.get("subscriberCount", 0))
        print(f"  • {chName} — {subs:,} inscritos (ID: {chId})")

        # Tentar mapear automaticamente
        for keyword, keys in knownChannels.items():
            if keyword.lower() in chName.lower():
                for k in keys:
                    saveToEnv(k, chId)
                break

    # Salvar refresh token no .env para renovação automática
    if tokenData.get("refresh_token"):
        saveToEnv("GOOGLE_REFRESH_TOKEN", tokenData["refresh_token"])

    if GENERIC_YOUTUBE_API_KEY:
        print("\n✅ YOUTUBE_API_KEY aplicado a clientes faltantes.")
    else:
        print("\n⚠️  Nenhuma YOUTUBE_API_KEY foi propagada para clientes; defina YOUTUBE_API_KEY no .env se precisar de fetchers de métricas baseados em API Key.")

    print(f"\n✅ Configuração YouTube concluída!")
    print("   Próximo passo: python execution/testConnections.py\n")


if __name__ == "__main__":
    main()
