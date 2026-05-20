# YouTube API Setup - Passo a Passo
# Execute estes comandos no Google Cloud Console

## 1. Criar/Selecionar Projeto
# - Vá para https://console.cloud.google.com
# - Crie um novo projeto ou selecione um existente
# - Anote o nome do projeto

## 2. Ativar APIs
# - Vá para "APIs e Serviços" → "Biblioteca"
# - Procure e ative:
#   - YouTube Data API v3
#   - YouTube Analytics API

## 3. Criar Credenciais
# - Vá para "APIs e Serviços" → "Credenciais"
# - Clique "Criar credenciais" → "Chave de API"
# - Copie a chave gerada

## 4. Criar OAuth 2.0
# - Ainda em "Credenciais", clique "Criar credenciais" → "ID do cliente OAuth 2.0"
# - Tipo: "Aplicativo da Web"
# - Nome: "YouTube Social Monitor"
# - URIs de redirecionamento autorizados: http://localhost:8888/callback
# - Clique "Criar"
# - Baixe o arquivo JSON (client_secret_*.json)

## 5. Próximos passos
# - Renomeie o arquivo JSON baixado para: credentials/google_credentials.json
# - Adicione a API Key no .env: YOUTUBE_API_KEY=sua_chave_aqui
# - Execute: python3 execution/generateYouTubeToken.py