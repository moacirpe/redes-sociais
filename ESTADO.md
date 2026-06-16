# ESTADO — Redes Sociais
Status: 🟢 ativo
Atualizado em: 16/jun/2026

## 🔴 BLOQUEADO até amanhã (17/jun) — Moper WhatsApp
Diagnóstico feito hoje (via Graph API da Meta):
- O `.env` ainda aponta para o número de TESTE da Meta (+1 555-160-7776, NOT_VERIFIED) — **não** o número novo.
- O número novo NÃO aparece na WABA conectada (`MOPER_WHATSAPP_BUSINESS_ACCOUNT_ID` atual) → provavelmente foi cadastrado em outra conta/app.
- Token atual: válido, escopos certos, mas **expira em 21/jul/2026** (renovar antes).
- **Bloqueio:** SMS de verificação do número só libera amanhã (operadora/conta paga).

### Assim que o SMS chegar (amanhã), fazer nesta ordem:
1. No painel Meta (developers.facebook.com → App → WhatsApp → Configuração da API), pegar do número NOVO: **Phone Number ID** e **WABA ID**.
2. Trocar `MOPER_WHATSAPP_PHONE_NUMBER_ID` (e `..._BUSINESS_ACCOUNT_ID` se mudou) no `.env` E no Railway.
3. Verificar via Graph API que o número novo está VERIFIED.
4. Ligar o webhook no painel Meta: URL `https://web-production-476d9.up.railway.app/webhook/moper`, verify token = `MOPER_WHATSAPP_VERIFY_TOKEN`, assinar campo `messages`.
5. Teste real: mandar WhatsApp ao número novo → bot responde.

## Outras pendências
- Laika WhatsApp: escanear QR code com o celular (67) 99857-4771
- Railway: adicionar vars do Moper Evolution (`EVOLUTION_API_KEY_MOPER`, `EVOLUTION_INSTANCIA_MOPER`)
- Publicação no Facebook (1-2h) e TikTok (depende de aprovação de API)
- Credenciais pendentes: Instagram Namasa, TikTok, YouTube

## Próximos passos
- AMANHÃ (17/jun): seguir a lista "Assim que o SMS chegar" acima.

> Já funcionando: pipeline Instagram → Neon PostgreSQL (cron 8h), publicação automática de posts (Cloudinary), catálogo de paleteiras no GitHub Pages.
> Fonte detalhada: `REDES SOCIAIS/HANDOFF.md`.
