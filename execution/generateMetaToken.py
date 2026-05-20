#!/usr/bin/env python3
"""
Gerador de Token OAuth — Meta (Instagram + Facebook)

Abre o navegador automaticamente no fluxo de autorização do Meta.
Captura o token, busca os Account IDs e salva tudo no .env.

Uso:
    python execution/generateMetaToken.py

Pré-requisito:
    Você precisa de um App criado no Meta for Developers:
    1. Acesse https://developers.facebook.com
    2. "Meus Apps" → "Criar App" → Tipo: Business
    3. Adicione o produto "Instagram Graph API"
    4. Em Configurações → Básico: copie o APP_ID e APP_SECRET
    5. Cole aqui embaixo ou defina no .env:
       META_APP_ID=...
       META_APP_SECRET=...
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
# CONFIGURAÇÃO — preencher após criar App no Meta for Developers
# ============================================================================

APP_ID     = os.getenv("META_APP_ID", "")
APP_SECRET = os.getenv("META_APP_SECRET", "")

REDIRECT_URI  = "http://localhost:8888/callback"
SCOPES        = [
    "instagram_basic",
    "instagram_manage_insights",
    "instagram_content_publish",
    "pages_read_engagement",
    "pages_show_list",
    "business_management",
]

ENV_FILE = ".env"

# ============================================================================
# SERVIDOR LOCAL — captura o callback do Meta
# ============================================================================

captured_code  = None
captured_error = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code, captured_error

        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            captured_code = params["code"][0]
            self._respond("✅ Autorização recebida! Pode fechar esta janela e voltar ao terminal.")
        elif "error" in params:
            captured_error = params.get("error_description", ["Erro desconhecido"])[0]
            self._respond(f"❌ Erro: {captured_error}")
        else:
            self._respond("⚠️ Resposta inesperada.")

    def _respond(self, message: str):
        html = f"""
        <html><body style="font-family:sans-serif;text-align:center;padding:60px">
        <h2>{message}</h2>
        <p>Retorne ao terminal para continuar.</p>
        </body></html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, *args):
        pass  # silenciar logs do servidor


def startServer():
    server = HTTPServer(("localhost", 8888), CallbackHandler)
    while captured_code is None and captured_error is None:
        server.handle_request()


# ============================================================================
# FLUXO OAUTH
# ============================================================================

def buildAuthUrl() -> str:
    params = urllib.parse.urlencode({
        "client_id":     APP_ID,
        "redirect_uri":  REDIRECT_URI,
        "scope":         ",".join(SCOPES),
        "response_type": "code",
    })
    return f"https://www.facebook.com/v19.0/dialog/oauth?{params}"


def exchangeCodeForToken(code: str) -> dict:
    import requests
    r = requests.get("https://graph.facebook.com/v19.0/oauth/access_token", params={
        "client_id":     APP_ID,
        "redirect_uri":  REDIRECT_URI,
        "client_secret": APP_SECRET,
        "code":          code,
    }, timeout=30)
    r.raise_for_status()
    return r.json()


def getLongLivedToken(shortToken: str) -> dict:
    """Troca token de curta duração (1h) por longa duração (60 dias)."""
    import requests
    r = requests.get("https://graph.facebook.com/v19.0/oauth/access_token", params={
        "grant_type":        "fb_exchange_token",
        "client_id":         APP_ID,
        "client_secret":     APP_SECRET,
        "fb_exchange_token": shortToken,
    }, timeout=30)
    r.raise_for_status()
    return r.json()


def fetchInstagramAccounts(token: str) -> list:
    """Lista todas as contas Instagram Business conectadas."""
    import requests

    # Buscar páginas do Facebook
    r = requests.get("https://graph.facebook.com/v19.0/me/accounts", params={
        "access_token": token,
        "fields": "id,name,instagram_business_account",
    })
    r.raise_for_status()
    pages = r.json().get("data", [])

    accounts = []
    for page in pages:
        ig = page.get("instagram_business_account")
        if ig:
            # Buscar detalhes da conta Instagram
            ig_id = ig["id"]
            r2 = requests.get(f"https://graph.facebook.com/v19.0/{ig_id}", params={
                "fields": "id,username,name,followers_count",
                "access_token": token,
            }, timeout=30)
            if r2.ok:
                data = r2.json()
                accounts.append({
                    "page_name":    page.get("name"),
                    "page_id":      page.get("id"),
                    "ig_id":        data.get("id"),
                    "ig_username":  data.get("username"),
                    "ig_followers": data.get("followers_count"),
                })

    return accounts


def saveToEnv(key: str, value: str):
    """Salva ou atualiza variável no .env."""
    set_key(ENV_FILE, key, value)
    print(f"  ✅ {key} salvo no .env")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("   Gerador de Token Meta — Instagram / Facebook")
    print("="*60 + "\n")

    # Verificar APP_ID e APP_SECRET
    if not APP_ID or not APP_SECRET:
        print("❌ META_APP_ID e META_APP_SECRET não encontrados no .env")
        print()
        print("Passos para criar o App no Meta:")
        print("  1. Acesse https://developers.facebook.com")
        print("  2. 'Meus Apps' → 'Criar App' → Tipo: Business")
        print("  3. Adicione o produto 'Instagram Graph API'")
        print("  4. Configurações → Básico → copie App ID e App Secret")
        print("  5. Adicione no .env:")
        print("     META_APP_ID=seu_app_id")
        print("     META_APP_SECRET=seu_app_secret")
        print()
        print("  ⚠️  Em Configurações → Básico → URIs de redirecionamento OAuth válidos")
        print("     adicione: http://localhost:8888/callback")
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
    timeout = 300
    elapsed = 0
    while captured_code is None and captured_error is None and elapsed < timeout:
        time.sleep(1)
        elapsed += 1

    if captured_error:
        print(f"\n❌ Erro na autorização: {captured_error}")
        sys.exit(1)

    if captured_code is None:
        print(f"\n❌ Timeout — autorização não recebida em {timeout // 60} minutos.")
        sys.exit(1)

    print("\n✅ Código de autorização recebido!")

    # Trocar código por token
    print("\n🔄 Trocando código por token de acesso...")
    tokenData = exchangeCodeForToken(captured_code)
    shortToken = tokenData.get("access_token")

    if not shortToken:
        print(f"❌ Falha ao obter token: {tokenData}")
        sys.exit(1)

    # Converter para token de longa duração
    print("🔄 Convertendo para token de longa duração (60 dias)...")
    longTokenData = getLongLivedToken(shortToken)
    longToken = longTokenData.get("access_token")

    if not longToken:
        print("⚠️  Não foi possível obter token longo. Usando token curto.")
        longToken = shortToken

    expiresIn = longTokenData.get("expires_in", 0)
    print(f"✅ Token válido por {expiresIn // 86400} dias")

    # Buscar contas Instagram conectadas
    print("\n🔍 Buscando contas Instagram Business conectadas...")
    accounts = fetchInstagramAccounts(longToken)

    if not accounts:
        print("⚠️  Nenhuma conta Instagram Business encontrada.")
        print("   Verifique se as contas estão conectadas a uma Página do Facebook.")
    else:
        print(f"\n📱 {len(accounts)} conta(s) encontrada(s):\n")
        for i, acc in enumerate(accounts, 1):
            print(f"  {i}. @{acc['ig_username']} — {acc['ig_followers']:,} seguidores (ID: {acc['ig_id']})")

    # Perguntar qual conta mapear
    print("\n" + "="*60)
    print("Salvando tokens no .env...")
    print("="*60)

    # Salvar token principal para Meta/Facebook e Instagram genéricos
    saveToEnv("META_LONG_LIVED_TOKEN", longToken)
    saveToEnv("FACEBOOK_ACCESS_TOKEN", longToken)
    saveToEnv("INSTAGRAM_TOKEN", longToken)

    # Salvar um identificador genérico de conta Instagram Business
    if accounts:
        saveToEnv("INSTAGRAM_BUSINESS_ACCOUNT_ID", accounts[0]["ig_id"])
        saveToEnv("FACEBOOK_PAGE_ID", accounts[0]["page_id"])

    # Mapear contas automaticamente por username
    knownAccounts = {
        "moper.maquinas":      ("MOPER_INSTAGRAM_TOKEN", "MOPER_INSTAGRAM_ACCOUNT_ID"),
        "namasa.mp":           ("NAMASA_INSTAGRAM_TOKEN", "NAMASA_INSTAGRAM_ACCOUNT_ID"),
        "moacir.moper":        ("MOACIR_INSTAGRAM_TOKEN", "MOACIR_INSTAGRAM_ACCOUNT_ID"),
        "moper.revest":        ("MOPER_INSTAGRAM_USER_PESSOAL_TOKEN", "MOPER_INSTAGRAM_USER_PESSOAL_ID"),
        "espacolaikadourados": ("LAIKA_INSTAGRAM_TOKEN", "LAIKA_INSTAGRAM_ACCOUNT_ID"),
    }

    matched = 0
    for acc in accounts:
        username = acc.get("ig_username", "").lower()
        if username in knownAccounts:
            tokenKey, idKey = knownAccounts[username]
            saveToEnv(tokenKey, longToken)
            saveToEnv(idKey, acc["ig_id"])
            print(f"  → @{username} mapeado como {tokenKey}")
            matched += 1

    if matched == 0:
        print("\n⚠️  Nenhuma conta foi mapeada automaticamente.")
        print("   Salve manualmente no .env:")
        print(f"   TOKEN = {longToken[:30]}...")
        for acc in accounts:
            print(f"   @{acc['ig_username']} → ID: {acc['ig_id']}")

    print(f"\n✅ Concluído! {matched} conta(s) configurada(s) no .env")
    print("\nPróximo passo: testar a conexão com")
    print("  python execution/testConnections.py\n")


if __name__ == "__main__":
    main()
