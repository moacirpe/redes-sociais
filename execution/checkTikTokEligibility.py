#!/usr/bin/env python3
"""
Verificador de Elegibilidade TikTok

Verifica se uma conta TikTok existe e é elegível para o Developer Portal.

Uso:
    python execution/checkTikTokEligibility.py @username
    python execution/checkTikTokEligibility.py --all  # verificar todas as contas
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Contas a verificar
ACCOUNTS = {
    "moacir": "@moacir.moper",
    "namasa": "@namasa.mp",
    "moper": "@moper.maquinas",
    "laika": "@espacolaikadourados"
}

def checkAccountExists(username):
    """Verifica se a conta existe no TikTok."""
    try:
        # Remove @ se existir
        clean_username = username.lstrip('@')

        # Tentar acessar perfil público
        url = f"https://www.tiktok.com/@{clean_username}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            # Verificar se não é página de erro
            if "user not found" in response.text.lower() or "não encontrado" in response.text.lower():
                return False, "Conta não encontrada"

            # Verificar se é conta Business (pode ter indicadores)
            if "business" in response.text.lower() or "empresa" in response.text.lower():
                return True, "Conta existe (possivelmente Business)"

            return True, "Conta existe (verificar se é Business)"

        elif response.status_code == 404:
            return False, "Conta não encontrada (404)"

        else:
            return False, f"Erro HTTP {response.status_code}"

    except requests.exceptions.RequestException as e:
        return False, f"Erro de conexão: {e}"

def checkBusinessEligibility(username):
    """Verifica elegibilidade para conta Business."""
    exists, message = checkAccountExists(username)

    if not exists:
        return False, message

    # Para contas brasileiras, verificar requisitos específicos
    print(f"   Conta {username}: {message}")

    # Requisitos para TikTok Business API no Brasil:
    # - Conta Business verificada
    # - Pelo menos 30 dias de idade
    # - Sem violações de termos
    # - País suportado (Brasil tem restrições)

    print("   ✅ Requisitos para Brasil:")
    print("     - Conta Business: VERIFICAR MANUALMENTE")
    print("     - Idade da conta: 30+ dias")
    print("     - Sem violações: VERIFICAR MANUALMENTE")
    print("     - País suportado: Brasil (com restrições)")

    return True, "Conta elegível (verificar manualmente)"

def checkAllAccounts():
    """Verifica todas as contas do projeto."""
    print("\n" + "="*60)
    print("   Verificação de Elegibilidade TikTok")
    print("="*60 + "\n")

    results = {}

    for client, username in ACCOUNTS.items():
        print(f"🔍 Verificando {client.upper()}: {username}")
        eligible, message = checkBusinessEligibility(username)
        results[client] = {"eligible": eligible, "message": message, "username": username}

        if eligible:
            print("   ✅ POSSIVELMENTE ELEGÍVEL")
        else:
            print("   ❌ NÃO ELEGÍVEL")



        print(f"   📝 {message}\n")

    return results

def showSolutions():
    """Mostra soluções para problemas comuns."""
    print("\n" + "="*60)
    print("   SOLUÇÕES PARA PROBLEMAS COMUNS")
    print("="*60)

    print("\n🔧 SE CONTA NÃO EXISTE:")
    print("   1. Verificar se o username está correto")
    print("   2. Tentar sem o @")
    print("   3. Verificar se a conta foi deletada/suspensa")

    print("\n🔧 SE CONTA NÃO É BUSINESS:")
    print("   1. Abrir app TikTok")
    print("   2. Ir em Perfil → Configurações → Conta")
    print("   3. Selecionar 'Alternar para conta Business'")
    print("   4. Preencher dados da empresa")
    print("   5. Aguardar aprovação (2-7 dias)")

    print("\n🔧 PARA CONTAS BRASILEIRAS:")
    print("   1. Conta deve ter pelo menos 30 dias")
    print("   2. Email e telefone verificados")
    print("   3. Sem violações de termos de serviço")
    print("   4. Categorizar como 'Empresa/Local' no Business")

    print("\n🔧 SE TUDO FALHAR:")
    print("   1. Criar nova conta Business")
    print("   2. Aguardar 30 dias")
    print("   3. Verificar completamente")
    print("   4. Contatar suporte: business@tiktok.com")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            results = checkAllAccounts()
        else:
            username = sys.argv[1]
            print(f"\n🔍 Verificando conta: {username}")
            eligible, message = checkBusinessEligibility(username)
            print(f"Resultado: {'✅ ELEGÍVEL' if eligible else '❌ NÃO ELEGÍVEL'}")
            print(f"Mensagem: {message}")
    else:
        print("Uso:")
        print("  python execution/checkTikTokEligibility.py @username")
        print("  python execution/checkTikTokEligibility.py --all")
        sys.exit(1)

    showSolutions()

if __name__ == "__main__":
    main()