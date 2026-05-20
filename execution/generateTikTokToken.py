#!/usr/bin/env python3
"""
Gerador de Token OAuth — TikTok

Abre o navegador automaticamente no fluxo de autorização do TikTok.
Captura o token, busca os Account IDs e salva tudo no .env.

Uso:
    python execution/generateTikTokToken.py

Pré-requisito:
    Você precisa de um App criado no TikTok Developer Portal:
    1. Acesse https://developers.tiktok.com
    2. "Create App" → Tipo: App for Business
    3. Adicione os produtos necessários (TikTok Business API)
    4. Em App Settings: copie o Client Key e Client Secret
    5. Cole aqui embaixo ou defina no .env:
       TIKTOK_CLIENT_KEY=...
       TIKTOK_CLIENT_SECRET=...
"""

import os
import sys
import json
import time
import webbrowser
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv, set_key

load_dotenv()

# ============================================================================
# CONFIGURAÇÃO — preencher após criar App no TikTok Developer Portal
# ============================================================================

CLIENT_KEY     = os.getenv("TIKTOK_CLIENT_KEY", "")
CLIENT_SECRET  = os.getenv("TIKTOK_CLIENT_SECRET", "")

REDIRECT_URI  = "http://localhost:8888/callback"
SCOPES        = [
    "user.info.basic",
    "video.list",
    "video.upload",
    "research.data.basic",
    "research.data.targeting",
]

ENV_FILE = ".env"
captured_code = None
captured_error = None


# ============================================================================
# SERVIDOR LOCAL PARA CALLBACK
# ============================================================================

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code, captured_error

        # Parse da URL
        url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(url.query)

        # Verificar se é erro
        if "error" in query:
            captured_error = query["error"][0]
            self.showMessage("❌ Erro na Autorização", f"Erro: {captured_error}")
            return

        # Capturar código de autorização
        if "code" in query:
            captured_code = query["code"][0]
            self.showMessage("✅ Autorização Aprovada!", "Retorne ao terminal para continuar.")
            return

        # Página padrão
        self.showMessage("Aguardando Autorização", "Complete a autorização no TikTok.")

    def showMessage(self, title, message):
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #FF0050, #00F2EA);
                    color: white;
                    text-align: center;
                    padding: 50px;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    margin: 0 0 20px 0;
                    font-size: 2.5em;
                    font-weight: 700;
                }}
                p {{
                    font-size: 1.2em;
                    margin: 0;
                    opacity: 0.9;
                }}
                .spinner {{
                    border: 4px solid rgba(255, 255, 255, 0.3);
                    border-top: 4px solid white;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 20px auto;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                <p>{message}</p>
                {"<div class='spinner'></div>" if "Aguardando" in title else ""}
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass  # Silenciar logs do servidor


def startServer():
    server = HTTPServer(("localhost", 8888), CallbackHandler)
    server.handle_request()  # Aguarda apenas 1 requisição


# ============================================================================
# FLUXO OAUTH
# ============================================================================

def buildAuthUrl() -> str:
    """Constrói URL de autorização do TikTok."""
    params = {
        "client_key":    CLIENT_KEY,
        "scope":         ",".join(SCOPES),
        "response_type": "code",
        "redirect_uri":  REDIRECT_URI,
        "state":         "tiktok_oauth_" + str(int(time.time())),
    }
    return f"https://www.tiktok.com/auth/authorize/?{urllib.parse.urlencode(params)}"


def exchangeCodeForToken(code: str) -> dict:
    """Troca código de autorização por tokens de acesso."""
    import requests

    data = {
        "client_key":    CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code":          code,
        "grant_type":    "authorization_code",
        "redirect_uri":  REDIRECT_URI,
    }

    r = requests.post("https://open-api.tiktok.com/oauth/access_token/", data=data)
    r.raise_for_status()
    return r.json()


def fetchUserInfo(accessToken: str) -> dict:
    """Busca informações do usuário autenticado."""
    import requests

    headers = {"Authorization": f"Bearer {accessToken}"}
    r = requests.get("https://open-api.tiktok.com/user/info/", headers=headers)
    r.raise_for_status()
    return r.json()


def saveToEnv(key: str, value: str):
    """Salva ou atualiza variável no .env."""
    set_key(ENV_FILE, key, value)
    print(f"  ✅ {key} salvo no .env")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("   Gerador de Token TikTok — TikTok OAuth")
    print("="*60 + "\n")

    # Verificar CLIENT_KEY e CLIENT_SECRET
    if not CLIENT_KEY or not CLIENT_SECRET:
        print("❌ TIKTOK_CLIENT_KEY e TIKTOK_CLIENT_SECRET não encontrados no .env")
        print()
        print("Passos para criar o App no TikTok Developer Portal:")
        print("  1. Acesse https://developers.tiktok.com")
        print("  2. 'Create App' → Tipo: App for Business")
        print("  3. Adicione os produtos necessários:")
        print("     - TikTok Business API")
        print("     - Research API (opcional)")
        print("  4. Em App Settings → copie Client Key e Client Secret")
        print("  5. Adicione no .env:")
        print("     TIKTOK_CLIENT_KEY=seu_client_key")
        print("     TIKTOK_CLIENT_SECRET=seu_client_secret")
        print()
        print("  ⚠️  Em App Settings → Redirect URIs")
        print("     adicione: http://localhost:8888/callback")
        print()
        sys.exit(1)

    # Iniciar servidor em background
    print("🔌 Iniciando servidor local na porta 8888...")
    serverThread = threading.Thread(target=startServer, daemon=True)
    serverThread.start()

    # Abrir navegador
    authUrl = buildAuthUrl()
    print("🌐 Abrindo navegador para autorização...")
    print(f"   URL: {authUrl[:80]}...")
    webbrowser.open(authUrl)

    # Aguardar callback
    print("\n⏳ Aguardando você autorizar no navegador...")
    timeout = 120
    elapsed = 0
    while captured_code is None and captured_error is None and elapsed < timeout:
        time.sleep(1)
        elapsed += 1

    if captured_error:
        print(f"\n❌ Erro na autorização: {captured_error}")
        sys.exit(1)

    if captured_code is None:
        print("\n❌ Timeout — autorização não recebida em 2 minutos.")
        sys.exit(1)

    print("\n✅ Código de autorização recebido!")

    # Trocar código por tokens
    print("\n🔄 Trocando código por tokens de acesso...")
    tokenData = exchangeCodeForToken(captured_code)

    if tokenData.get("message") != "success":
        print(f"❌ Falha ao obter tokens: {tokenData}")
        sys.exit(1)

    accessToken = tokenData.get("data", {}).get("access_token")
    refreshToken = tokenData.get("data", {}).get("refresh_token")
    openId = tokenData.get("data", {}).get("open_id")

    if not accessToken:
        print("❌ Token de acesso não encontrado na resposta.")
        sys.exit(1)

    print("✅ Tokens obtidos com sucesso!")

    # Buscar informações do usuário
    print("\n🔍 Buscando informações da conta TikTok...")
    try:
        userData = fetchUserInfo(accessToken)
        if userData.get("message") == "success":
            userInfo = userData.get("data", {}).get("user", {})
            username = userInfo.get("username", "desconhecido")
            displayName = userInfo.get("display_name", "Desconhecido")
            print(f"   Conta: @{username} ({displayName})")
        else:
            print("   ⚠️  Não foi possível buscar informações da conta")
            username = "desconhecido"
    except Exception as e:
        print(f"   ⚠️  Erro ao buscar informações: {e}")
        username = "desconhecido"

    # Salvar tokens no .env
    print("\n" + "="*60)
    print("Salvando tokens no .env...")
    print("="*60)

    # Mapear contas automaticamente por username
    knownAccounts = {
        "moacir.moper":        ("MOACIR_TIKTOK_ACCESS_TOKEN", "MOACIR_TIKTOK_OPEN_ID", "MOACIR_TIKTOK_REFRESH_TOKEN"),
        "namasa.mp":           ("NAMASA_TIKTOK_ACCESS_TOKEN", "NAMASA_TIKTOK_OPEN_ID", "NAMASA_TIKTOK_REFRESH_TOKEN"),
        "moper.maquinas":      ("MOPER_TIKTOK_ACCESS_TOKEN", "MOPER_TIKTOK_OPEN_ID", "MOPER_TIKTOK_REFRESH_TOKEN"),
        "espacolaikadourados": ("LAIKA_TIKTOK_ACCESS_TOKEN", "LAIKA_TIKTOK_OPEN_ID", "LAIKA_TIKTOK_REFRESH_TOKEN"),
    }

    matched = False
    for accountUsername, keys in knownAccounts.items():
        if accountUsername == username:
            accessKey, openIdKey, refreshKey = keys
            saveToEnv(accessKey, accessToken)
            saveToEnv(openIdKey, openId or "")
            if refreshToken:
                saveToEnv(refreshKey, refreshToken)
            print(f"  → @{username} mapeado como {accessKey}")
            matched = True
            break

    if not matched:
        print("\n⚠️  Conta não mapeada automaticamente.")
        print("   Salve manualmente no .env:")
        print(f"   ACCESS_TOKEN = {accessToken[:30]}...")
        print(f"   OPEN_ID = {openId or 'não disponível'}")
        if refreshToken:
            print(f"   REFRESH_TOKEN = {refreshToken[:30]}...")

        # Perguntar se quer salvar mesmo assim
        saveAnyway = input("\nSalvar tokens genéricos no .env? (s/n): ").lower().strip()
        if saveAnyway == 's':
            saveToEnv("TIKTOK_ACCESS_TOKEN", accessToken)
            saveToEnv("TIKTOK_OPEN_ID", openId or "")
            if refreshToken:
                saveToEnv("TIKTOK_REFRESH_TOKEN", refreshToken)
            print("  ✅ Tokens salvos como genéricos")

    print(f"\n✅ Configuração TikTok concluída!")
    print("   Próximo passo: python execution/testConnections.py\n")


if __name__ == "__main__":
    main()