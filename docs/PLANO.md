# Plano — Redes Sociais
_Atualizado em: 2026-06-06 (sessão 2)_

> **Tags:** `[0]` planejado · `[1-S]` diretiva/schema · `[2-E]` script existe ·
> `[3-H]` credenciais no .env · `[4-C]` testado com dado real · `[5-T]` ✅ pipeline completo

---

## Infraestrutura Core

- `[5-T]` ✅ Neon PostgreSQL — `DATABASE_URL` configurado, schema aplicado, pipeline testado
- `[5-T]` ✅ Schema do banco — 5 tabelas: `social_accounts`, `posts`, `metrics`, `execution_logs`, `whatsapp_conversations`
- `[5-T]` ✅ Cron diário 8h — `execution/collectAll.sh` coleta todos os clientes
- `[5-T]` ✅ GitHub Pages — catálogo de paleteiras publicado em https://moacirpe.github.io/redes-sociais/paleteiras/
- `[2-E]` Evolution API — rodando em https://evo.huboperacional.com.br (instâncias Moper e Laika criadas)

---

## Autenticação / Tokens

- `[5-T]` ✅ Meta OAuth Instagram — tokens moacir, moper, laika no .env
- `[1-S]` Meta OAuth Instagram namasa — script existe, token vazio
- `[1-S]` TikTok OAuth — script existe, todos os tokens vazios
- `[1-S]` YouTube OAuth — script existe, todos os tokens vazios

---

## Cliente — moacir

- `[5-T]` ✅ Coleta Instagram — `execution/fetchInstagramData.py --save`
- `[5-T]` ✅ Relatório mensal — `execution/generateReport.py`
- `[1-S]` Coleta TikTok — script existe, credenciais vazias
- `[1-S]` Coleta YouTube — script existe, credenciais vazias

---

## Cliente — moper-maquinas

- `[5-T]` ✅ Coleta Instagram — pipeline ativo
- `[5-T]` ✅ Catálogo paleteiras — GitHub Pages publicado
- `[2-E]` WhatsApp Bot — migrado da Meta API para Evolution (`execution/whatsappResponder.py`), instância `pai_moper_maquinas`. **Falta: escanear QR code com celular dedicado da Moper**
- `[1-S]` Coleta TikTok — credenciais vazias
- `[1-S]` Coleta YouTube — credenciais vazias

---

## Cliente — espaco-laika

- `[5-T]` ✅ Coleta Instagram — pipeline ativo
- `[2-E]` WhatsApp Bot — `execution/whatsappResponderLaika.py` pronto, Evolution API configurada. **Falta: escanear QR code com celular (67) 99857-4771**
- `[1-S]` Coleta TikTok — credenciais vazias
- `[1-S]` Coleta YouTube — credenciais vazias

---

## Cliente — namasa

- `[1-S]` Coleta Instagram — script existe, token vazio
- `[1-S]` Coleta TikTok — credenciais vazias
- `[1-S]` Coleta YouTube — credenciais vazias

---

## Automação e Publicação

- `[5-T]` ✅ Cron diário — coleta automática todos os dias às 8h
- `[5-T]` ✅ **Publicação automática Instagram** — `generateCaptions.py` + `publishScheduled.py` + Cloudinary. Testado com post real em 06/06/2026.
  - Suporte a: imagem (IMAGE) e vídeo (REELS)
  - Clientes: moacir, moper, laika
  - Fila: `queue/{cliente}/queue.csv` — editar status para `approved` para publicar
- `[0]` Publicação Facebook — credenciais prontas, falta implementar no publishScheduled.py
- `[0]` Publicação TikTok — requer aprovação de API pelo TikTok (processo burocrático)
- `[0]` Dashboard unificado — não iniciado
- `[0]` Relatório automático por e-mail — não iniciado
