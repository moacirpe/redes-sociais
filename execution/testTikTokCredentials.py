#!/usr/bin/env python3
"""
Teste de Credenciais TikTok

Verifica se as credenciais do TikTok Developer Portal estão corretas
antes de executar o script principal de geração de tokens.

Uso:
    python execution/testTikTokCredentials.py
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def testCredentials():
    print("\n" + "="*50)
    print("   Teste de Credenciais TikTok")
    print("="*50 + "\n")

    clientKey = os.getenv("TIKTOK_CLIENT_KEY", "")
    clientSecret = os.getenv("TIKTOK_CLIENT_SECRET", "")

    if not clientKey or not clientSecret:
        print("❌ Credenciais não encontradas no .env")
        print("\nAdicione no .env:")
        print("TIKTOK_CLIENT_KEY=seu_client_key")
        print("TIKTOK_CLIENT_SECRET=seu_client_secret")
        return False

    print(f"✅ Client Key: {clientKey[:10]}...")
    print(f"✅ Client Secret: {clientSecret[:10]}...")

    # Testar conexão básica com a API
    try:
        # Endpoint de teste (verificar se as credenciais são válidas)
        testUrl = "https://open-api.tiktok.com/oauth/client_token/"
        data = {
            "client_key": clientKey,
            "client_secret": clientSecret,
            "grant_type": "client_credentials"
        }

        print("\n🔍 Testando conexão com TikTok API...")
        response = requests.post(testUrl, data=data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result.get("message") == "success":
                print("✅ Credenciais válidas!")
                print("✅ Conexão com TikTok API: OK")
                return True
            else:
                print(f"❌ Erro na resposta: {result}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def showNextSteps():
    print("\n" + "="*50)
    print("   PRÓXIMOS PASSOS")
    print("="*50)
    print("\nSe as credenciais estiverem OK:")
    print("1. Execute: python execution/generateTikTokToken.py")
    print("2. Siga as instruções no navegador")
    print("3. Autorize cada conta TikTok dos clientes")
    print("4. Tokens serão salvos automaticamente no .env")

    print("\nSe houver problemas:")
    print("• Verifique se o app está aprovado no TikTok Developer")
    print("• Confirme se o Redirect URI está correto")
    print("• Aguarde aprovação se necessário")

if __name__ == "__main__":
    success = testCredentials()
    showNextSteps()

    if success:
        print("\n🎉 Pronto para gerar tokens!")
        sys.exit(0)
    else:
        print("\n❌ Corrija as credenciais antes de continuar.")
        sys.exit(1)