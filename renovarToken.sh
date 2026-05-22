#!/bin/bash
# renovarToken.sh — Renova o token WhatsApp da Moper em 1 comando
#
# USO:
#   ./renovarToken.sh SEU_TOKEN_NOVO_AQUI
#
# Onde pegar o token:
#   1. Acesse developers.facebook.com → seu app → Etapa 1. Experimente
#   2. Clique em "Gerar token"
#   3. Cole o token como argumento deste script
#
# O script vai:
#   1. Converter o token de ~24h para um token de 60 dias
#   2. Atualizar o bot Moper imediatamente (sem precisar acessar Railway)
#   3. Salvar o token longo no .env

set -e

APP_ID="3452397504935912"
APP_SECRET="88ed9669a4b7a7ce157c3b4f514555d2"
BOT_URL="https://web-production-476d9.up.railway.app"
VERIFY_TOKEN="moper_secret_2026"
ENV_FILE="$(dirname "$0")/.env"

SHORT_TOKEN="$1"

if [ -z "$SHORT_TOKEN" ]; then
  echo ""
  echo "USO: ./renovarToken.sh SEU_TOKEN_NOVO_AQUI"
  echo ""
  echo "Onde pegar o token:"
  echo "  1. Acesse developers.facebook.com"
  echo "  2. Seu app → Etapa 1. Experimente → Gerar token"
  echo "  3. Cole aqui como argumento"
  echo ""
  exit 1
fi

echo ""
echo "=== Renovando token Moper WhatsApp ==="
echo ""

# Etapa 1: Converter para token de 60 dias
echo "1/3 Convertendo para token de 60 dias..."
RESPONSE=$(curl -s "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=${APP_ID}&client_secret=${APP_SECRET}&fb_exchange_token=${SHORT_TOKEN}")
LONG_TOKEN=$(echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null)

if [ -z "$LONG_TOKEN" ]; then
  echo "ERRO: Não foi possível converter o token."
  echo "Resposta da Meta: $RESPONSE"
  exit 1
fi

echo "   Token de 60 dias gerado: ...${LONG_TOKEN: -20}"

# Etapa 2: Atualizar o bot imediatamente
echo "2/3 Atualizando o bot Moper..."
UPDATE_RESPONSE=$(curl -s -X POST "${BOT_URL}/admin/update-token" \
  -H "Authorization: Bearer ${VERIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"${LONG_TOKEN}\"}")

STATUS=$(echo "$UPDATE_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status','erro'))" 2>/dev/null)

if [ "$STATUS" != "ok" ]; then
  echo "AVISO: Bot não respondeu como esperado."
  echo "Resposta: $UPDATE_RESPONSE"
else
  echo "   Bot atualizado com sucesso!"
fi

# Etapa 3: Salvar no .env
echo "3/3 Salvando no .env..."
if [ -f "$ENV_FILE" ]; then
  # Atualiza a linha MOPER_WHATSAPP_TOKEN no .env
  python3 -c "
import re, sys
with open('${ENV_FILE}', 'r') as f:
    content = f.read()
new_content = re.sub(
    r'^MOPER_WHATSAPP_TOKEN=.*$',
    'MOPER_WHATSAPP_TOKEN=${LONG_TOKEN}',
    content,
    flags=re.MULTILINE
)
with open('${ENV_FILE}', 'w') as f:
    f.write(new_content)
print('   .env atualizado')
"
fi

echo ""
echo "=== PRONTO! ==="
echo ""
echo "Bot Moper está funcionando com token válido por 60 dias."
echo "Token: ...${LONG_TOKEN: -20}"
echo ""
echo "LEMBRETE: Daqui a 60 dias, rode este script novamente com um novo token."
echo "(Apenas 30 segundos de trabalho)"
echo ""
