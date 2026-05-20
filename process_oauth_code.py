#!/usr/bin/env python3
"""
Processar Código OAuth do Meta Manualmente

Uso:
    python3 process_oauth_code.py "SEU_CODIGO_AQUI"
"""

import sys
import requests
from dotenv import set_key

# Credenciais do app
APP_ID = '2159359204835308'
APP_SECRET = '98d06a519c32cf17e7b6d98af738ca0b'
REDIRECT_URI = 'http://localhost:8888/callback'

def process_oauth_code(code):
    try:
        print('🔄 Trocando código por token...')

        # Trocar código por token curto
        token_url = 'https://graph.facebook.com/v19.0/oauth/access_token'
        params = {
            'client_id': APP_ID,
            'redirect_uri': REDIRECT_URI,
            'client_secret': APP_SECRET,
            'code': code
        }

        response = requests.get(token_url, params=params)
        response.raise_for_status()
        token_data = response.json()

        short_token = token_data.get('access_token')
        if not short_token:
            print(f'❌ Erro nos dados do token: {token_data}')
            return False

        print(f'✅ Token curto obtido: {short_token[:20]}...')

        # Converter para token longo
        long_token_url = 'https://graph.facebook.com/v19.0/oauth/access_token'
        long_params = {
            'grant_type': 'fb_exchange_token',
            'client_id': APP_ID,
            'client_secret': APP_SECRET,
            'fb_exchange_token': short_token
        }

        long_response = requests.get(long_token_url, params=long_params)
        long_response.raise_for_status()
        long_token_data = long_response.json()

        long_token = long_token_data.get('access_token')
        if not long_token:
            print(f'⚠️ Token longo não obtido, usando token curto: {long_token_data}')
            long_token = short_token

        expires_in = long_token_data.get('expires_in', 0)
        print(f'✅ Token longo obtido (válido por {expires_in // 86400} dias)')

        # Salvar no .env
        set_key('.env', 'META_LONG_LIVED_TOKEN', long_token)
        set_key('.env', 'FACEBOOK_ACCESS_TOKEN', long_token)
        set_key('.env', 'INSTAGRAM_TOKEN', long_token)

        print('✅ Tokens salvos no .env!')
        return True

    except Exception as e:
        print(f'❌ Erro: {e}')
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Uso: python3 process_oauth_code.py "SEU_CODIGO_AQUI"')
        sys.exit(1)

    code = sys.argv[1]
    if process_oauth_code(code):
        print('\n🎉 Sucesso! Agora execute:')
        print('python3 execution/testConnections.py')
    else:
        print('\n❌ Falhou. Verifique o código e tente novamente.')