# Design: Migração PostgreSQL → MongoDB (MLabs)

_Data: 2026-04-21_

## Objetivo

Substituir PostgreSQL+VPS por MongoDB Atlas (MLabs) como banco de dados do projeto. Elimina dependência de VPS e SSH tunnel. Resultado esperado: `fetchInstagramData.py --save` salva dados reais no MLabs.

---

## Contexto

O projeto coleta métricas de redes sociais para 4 clientes (moacir, espaco-laika, namasa, moper-maquinas). O pipeline de coleta do Instagram já funciona (`[4-C]`), mas os dados não eram persistidos porque o banco (PostgreSQL via SSH no VPS) nunca foi configurado. Com MLabs, a conexão é direta via URI — sem VPS, sem tunnel.

---

## Arquitetura

### Antes
```
fetchInstagramData.py → dbClient.py (psycopg2) → SSH Tunnel → VPS → PostgreSQL
```

### Depois
```
fetchInstagramData.py → dbClient.py (pymongo) → MongoDB Atlas (MLabs)
```

---

## Arquivos Afetados

| Arquivo | Ação |
|---------|------|
| `execution/dbClient.py` | Reescrita completa — psycopg2 → pymongo |
| `execution/setupDatabase.py` | Reescrita — CREATE TABLE → criar coleções + índices |
| `execution/fetchInstagramData.py` | Implementar `--save` que persiste no banco |
| `execution/testConnections.py` | Atualizar teste de DB para MongoDB |
| `.env` | Adicionar `MONGODB_URI`, remover vars VPS/Postgres |
| `requirements.txt` | Remover psycopg2, sshtunnel — adicionar pymongo |

---

## Schema — Coleções MongoDB

### `social_accounts`
```json
{
  "platform": "instagram",
  "account_id": "17841400000",
  "username": "moacir.moper",
  "client": "moacir",
  "access_token": "...",
  "is_active": true,
  "updated_at": "2026-04-21T00:00:00Z"
}
```
Índice único: `(platform, account_id)`

### `metrics`
```json
{
  "platform": "instagram",
  "client": "moacir",
  "account_id": "17841400000",
  "metric_date": "2026-04-21",
  "followers": 461,
  "reach": 1200,
  "likes": 89,
  "comments": 12,
  "engagement_rate": 0.0432,
  "raw_data": {},
  "collected_at": "2026-04-21T00:00:00Z"
}
```
Índice único: `(platform, client, metric_date)` — evita duplicatas na coleta diária

### `posts`
```json
{
  "platform": "instagram",
  "client": "moacir",
  "account_id": "17841400000",
  "post_id": "17854360000",
  "content": "...",
  "media_urls": [],
  "status": "published",
  "published_at": "2026-04-20T00:00:00Z",
  "metadata": {},
  "collected_at": "2026-04-21T00:00:00Z"
}
```
Índice único: `(platform, post_id)`

### `execution_logs`
```json
{
  "script_name": "fetchInstagramData",
  "status": "success",
  "message": "Collected 25 posts, 1 metrics snapshot",
  "details": {},
  "duration_ms": 1240,
  "created_at": "2026-04-21T00:00:00Z"
}
```
Índice: `created_at` (para limpeza periódica)

---

## Variáveis de Ambiente

### Remover do `.env`
```
VPS_HOST, VPS_PORT, VPS_USER, VPS_SSH_KEY
POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
```

### Adicionar ao `.env`
```
MONGODB_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/redes_sociais
```

---

## Interface do DbClient (pymongo)

```python
class DbClient:
    def __init__(self)          # conecta via MONGODB_URI
    def getCollection(name)     # retorna coleção
    def upsert(collection, filter, doc)  # insert ou update
    def insertOne(collection, doc)
    def find(collection, filter, limit)
    def close()
    def __enter__ / __exit__    # context manager
```

---

## Critério de Sucesso

Pipeline completo testado nesta sessão:
1. `python execution/setupDatabase.py` — cria coleções e índices no MLabs
2. `python execution/testConnections.py` — conexão MongoDB OK
3. `python execution/fetchInstagramData.py --save` — dados do @moacir.moper salvos no MLabs
4. Verificação manual no painel MLabs — documentos visíveis na coleção `metrics`

---

## Fora do Escopo

- Migração de dados históricos (não há dados para migrar)
- Outros clientes (laika, namasa, moper) — tokens ainda vazios, ficam para depois
- Agendamento cron — próxima fase, após DB funcionando
- TikTok e YouTube — credenciais ainda vazias
