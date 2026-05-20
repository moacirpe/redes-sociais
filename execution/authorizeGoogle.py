#!/usr/bin/env python3
"""
Autoriza acesso ao Google Sheets via OAuth2.
Abre o navegador, você autoriza, e o refresh_token é salvo no .env.

Uso:
    python execution/authorizeGoogle.py
"""

import os
import re
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

client_id     = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

if not client_id or not client_secret:
    raise EnvironmentError("Defina GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET no .env")

client_config = {
    "installed": {
        "client_id":     client_id,
        "client_secret": client_secret,
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
        "token_uri":     "https://oauth2.googleapis.com/token",
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

refresh_token = creds.refresh_token
print(f"\n✅ Autorizado com sucesso!")
print(f"Refresh token: {refresh_token}\n")

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
env_path = os.path.normpath(env_path)

with open(env_path, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r"^GOOGLE_REFRESH_TOKEN=.*$",
    f"GOOGLE_REFRESH_TOKEN={refresh_token}",
    content,
    flags=re.MULTILINE,
)

with open(env_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ GOOGLE_REFRESH_TOKEN salvo no .env automaticamente.")
