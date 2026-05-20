# Directive: Gerar Tokens TikTok

## Objetivo
Gerar e configurar tokens de API do TikTok para todos os clientes do projeto, permitindo coleta automática de métricas e dados.

## Entradas
- Credenciais do TikTok Developer Portal (Client Key e Client Secret)
- Contas TikTok de cada cliente autorizadas

## Processo

### 1. Preparação no TikTok Developer Portal
```
Acesse: https://developers.tiktok.com
→ Create App
→ App for Business
→ Adicionar produtos:
  - TikTok Business API
  - Research API (opcional)
→ App Settings:
  - Copiar Client Key e Client Secret
  - Adicionar Redirect URI: http://localhost:8888/callback
```

### 2. Configuração Local
```bash
# Adicionar no .env:
TIKTOK_CLIENT_KEY=seu_client_key_aqui
TIKTOK_CLIENT_SECRET=seu_client_secret_aqui
```

### 3. Execução do Script
```bash
python execution/generateTikTokToken.py
```

### 4. Autorização por Cliente
Para cada cliente:
- Script abre navegador automaticamente
- Fazer login na conta TikTok do cliente
- Autorizar permissões solicitadas
- Tokens salvos automaticamente no .env

## Tokens Gerados

### Por Cliente:
- `{CLIENTE}_TIKTOK_ACCESS_TOKEN` - Token de acesso (1 hora)
- `{CLIENTE}_TIKTOK_OPEN_ID` - ID único do usuário
- `{CLIENTE}_TIKTOK_REFRESH_TOKEN` - Token para renovação (30 dias)

### Mapeamento Automático:
```
moacir.moper        → MOACIR_*
namasa.mp           → NAMASA_*
moper.maquinas      → MOPER_*
espacolaikadourados → LAIKA_*
```

## Permissões Solicitadas
- `user.info.basic` - Informações básicas do usuário
- `video.list` - Listar vídeos publicados
- `video.upload` - Upload de vídeos (futuro)
- `research.data.basic` - Dados básicos de pesquisa
- `research.data.targeting` - Dados de targeting

## Renovação Automática
- Access tokens expiram em 1 hora
- Refresh tokens válidos por 30 dias
- Sistema renova automaticamente via `refresh_token`

## Teste de Conexão
```bash
python execution/testConnections.py
```

## Troubleshooting

### Erro: "Invalid client"
- Verificar Client Key e Client Secret no .env
- Confirmar app está aprovado no TikTok Developer

### Erro: "Redirect URI mismatch"
- Adicionar `http://localhost:8888/callback` nas configurações do app

### Erro: "Scope not authorized"
- Solicitar revisão do app no TikTok Developer Portal
- Aguardar aprovação (pode levar dias)

### Conta não mapeada
- Verificar username exato no TikTok
- Adicionar manualmente no código se necessário

## Outputs
- Tokens salvos no `.env`
- Confirmação de contas mapeadas
- Logs de sucesso/erro

## Próximos Passos
1. Executar `testConnections.py` para validar
2. Configurar scripts de coleta de dados
3. Implementar renovação automática
4. Adicionar monitoramento de expiração