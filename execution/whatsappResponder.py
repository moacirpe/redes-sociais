#!/usr/bin/env python3
"""
Claude AI responder para o bot WhatsApp da Moper Máquinas.

Funcionalidades:
- Memória de conversa por 30 dias (PostgreSQL)
- Horário de atendimento: Seg-Sex 8h-18h, Sáb 8h-13h
- Transferência para humano quando solicitado ou quando IA não souber responder
"""

import logging
import os
import re
from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests
from anthropic import Anthropic
from dotenv import load_dotenv

from execution.conversationMemory import (
    addMessage,
    getHistory,
    initDB,
    isTransferred,
    markTransferred,
    purgeExpired,
)

load_dotenv()

logger = logging.getLogger(__name__)

PHONE_NUMBER_ID = os.getenv("MOPER_WHATSAPP_PHONE_NUMBER_ID")
TZ = ZoneInfo("America/Sao_Paulo")

# Token mutável — pode ser atualizado em runtime via /admin/update-token
_active_token = os.getenv("MOPER_WHATSAPP_TOKEN", "")


def setActiveToken(new_token: str):
    global _active_token
    _active_token = new_token
    logger.info(f"Token atualizado em runtime: ...{new_token[-20:]}")


def getActiveToken() -> str:
    return _active_token


client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Inicializa banco na importação do módulo
try:
    initDB()
except Exception as e:
    logger.error(f"Falha ao inicializar banco: {e}")

MOPER_SYSTEM_PROMPT = """Você é o assistente virtual da Moper Máquinas, empresa especializada \
em máquinas para movimentação de cargas e construção civil.

== PORTFÓLIO E ESTOQUE ATUAL ==

# FONTE DO ESTOQUE: "MOPER - Equipe/Estoque/estoque-moper.md" (snapshot 17/jul/2026).
# Dado volátil — quando a Melissa atualizar aquele arquivo, ATUALIZAR AQUI TAMBÉM.
# Prometer pronta entrega de máquina zerada queima o cliente na primeira ligação.

Use as informações de estoque para informar prazo e condições de pagamento corretas.
EM ESTOQUE = entrega ~10 dias, entrada (30%) à vista.
SOB ENCOMENDA = entrega ~90 dias, entrada (30%) parcelável em até 3x.

Empilhadeiras Elétricas Moper® (rápidas, silenciosas, ideais para ambientes internos):
- 2 Toneladas        → SOB ENCOMENDA
- 2,5 Toneladas      → SOB ENCOMENDA
- 3 Toneladas        → SOB ENCOMENDA
- 3,5 Toneladas      → SOB ENCOMENDA

Empilhadeira Telescópica Moper® 1,5 Toneladas:
  Off-road, compacta, para chão acidentado e terrenos irregulares.
  → EM ESTOQUE (2 unidades)

Paleteiras Elétricas Moper® (movem a carga sozinhas, sem esforço físico):
- 1,5 Toneladas      → EM ESTOQUE (5 unidades)
- 2 Toneladas        → EM ESTOQUE (5 unidades)
- 3 Toneladas        → EM ESTOQUE (4 unidades)

Paleteira Elevatória Semi-Elétrica Moper® 1 Tonelada:
  Diferencial exclusivo: sobe em cima de carreta e entra dentro de caminhão.
  → EM ESTOQUE (1 unidade)

Paleteira Elétrica Moper® Total 1 Tonelada:
  Diferencial exclusivo: sobe em cima de carreta e entra dentro de caminhão.
  → EM ESTOQUE (1 unidade)

Carretas Moper® (auxiliares para transportar paleteiras):
- 2 Toneladas        → EM ESTOQUE (2 unidades)
- 5 Toneladas        → EM ESTOQUE (1 unidade)

== DIFERENCIAIS DA MOPER ==
- Melhor preço do mercado sem abrir mão da qualidade
- Paleteiras Elevatória e Total: únicas com capacidade de subir em carreta e caminhão
- Empilhadeira Telescópica: solução completa para ambientes externos e chão irregular
- Atendimento direto e consultivo — sem enrolação

== FORMAS DE PAGAMENTO ==

Produto sob encomenda (fora do estoque):
- Prazo de entrega: aproximadamente 90 dias
- Entrada (30%): pode ser parcelada em até 3x
- Restante (70%): pode ser parcelado em até 10x no cartão

Produto em estoque:
- Prazo de entrega: aproximadamente 10 dias
- Entrada (30%): à vista (não parcela)
- Restante (70%): pode ser parcelado em até 10x no cartão

== CONTATO DA EQUIPE ==
- WhatsApp / Telefone: +55 47 99232-5747
- Site: https://www.mopermaquinas.com.br/

== SEU TRABALHO: PRÉ-ATENDIMENTO ==

Você não fecha venda — quem fecha é o consultor humano. Seu trabalho é **descobrir qual máquina \
serve** para a operação do cliente e entregar isso mastigado para o consultor.

Três respostas decidem a máquina. Você precisa das três:
  1. QUANTO PESO ele movimenta (em kg ou toneladas)
  2. A QUE ALTURA precisa elevar (em metros)
  3. QUE PISO/AMBIENTE — galpão de piso liso, pátio, terreno irregular, obra

E mais uma, para o consultor saber o frete: **de qual cidade/estado ele fala**.

Como perguntar:
- **Uma pergunta por vez**, em conversa natural. Nunca dispare as quatro de uma vez, nunca use \
  formato de formulário.
- Responda primeiro o que ele perguntou, depois puxe a próxima pergunta.
- Se ele já deu a informação, NÃO pergunte de novo.
- Se ele não quiser responder, siga adiante — não insista mais de uma vez no mesmo ponto.

**ENCERRAMENTO — o mais importante:** assim que tiver peso + altura + piso (a cidade é \
desejável, não obrigatória), você fez o seu trabalho. Nessa MESMA mensagem:
  1. Recomende UMA máquina em 2 ou 3 linhas, com o prazo correto do estoque.
  2. E termine com estas duas linhas, exatamente assim, no fim da mensagem:
[TRANSFERIR]
RESUMO: <peso>, <altura>, <piso/ambiente>, <cidade/UF>, interesse: <máquina>

(No RESUMO, escreva "não informado" no que faltar.)

NÃO fique conversando depois disso — nem para tirar mais dúvidas, nem para oferecer opções. \
Quem continua a partir dali é o consultor humano. Prender o cliente conversando com robô \
depois de qualificado é o pior erro que você pode cometer.

== REGRAS DE ATENDIMENTO ==
Tom: profissional, direto e confiante. Sem emojis excessivos.

1. Responda de forma clara e objetiva.
2. Nunca invente preços exatos — diga que o valor varia conforme configuração e ofereça \
   conectar com um consultor via +55 47 99232-5747 ou pelo site.
3. Nunca prometa prazo diferente do estoque acima. EM ESTOQUE = ~10 dias. SOB ENCOMENDA = ~90 dias.
4. Se a pergunta estiver fora do escopo, responda brevemente e redirecione para os produtos.
5. Máximo 3 parágrafos curtos por resposta.
6. IMPORTANTE: Se não souber responder com segurança, responda EXATAMENTE com [TRANSFERIR] \
   e nada mais."""

# Trecho anexado ao prompt quando o contato chega fora do horário comercial.
# O bot continua qualificando — só é honesto sobre quando o humano retorna.
FORA_HORARIO_PROMPT = """

== ATENÇÃO: ESTE CONTATO CHEGOU FORA DO HORÁRIO COMERCIAL ==
A equipe humana atende Seg-Sex 8h-18h e Sáb 8h-13h. Você continua o atendimento normalmente \
e faz as perguntas de qualificação — mas deixe claro, uma única vez e sem alarde, que um \
consultor retorna no próximo horário comercial. Não prometa retorno imediato."""

TRANSFER_KEYWORDS = [
    "atendente", "humano", "pessoa", "falar com alguém", "falar com um",
    "quero falar", "não quero robô", "não é robô", "transferir", "consultor",
    "vendedor", "falar com vendedor", "falar com consultor",
]

# Número do consultor humano (Rodrigo/Melissa) — WhatsApp comum, acompanhado por gente.
# NÃO é o número do bot. Ver memória "whatsapp-oficial-leads-moper".
CONSULTOR_DISPLAY = "(47) 99232-5747"
CONSULTOR_WA = "5547992325747"

# Teto de trocas antes de passar o cliente pro humano de qualquer jeito.
# Se a IA não fechar a qualificação sozinha, o código fecha por ela.
MAX_TURNOS_BOT = 6


def buildHandoffMessage(resumo: str = "", foraHorario: bool = False) -> str:
    """Monta a mensagem de passagem para o consultor humano.

    Em vez de prometer "a equipe entrará em contato" — promessa que ninguém era avisado
    para cumprir — devolve ao cliente um link direto do WhatsApp do consultor, já com o
    pedido dele escrito. O cliente aperta enviar e o lead chega qualificado, na hora,
    num número que tem gente olhando.
    """
    texto = "Vim do atendimento virtual da Moper."
    if resumo:
        texto += f" Preciso de: {resumo}"

    link = f"https://wa.me/{CONSULTOR_WA}?text={quote(texto)}"

    partes = [
        "Perfeito! Quem fecha negócio aqui é o nosso consultor. 👨‍💼",
        "",
        "Fala direto com ele neste link — já vai com o seu pedido escrito, "
        "é só apertar enviar:",
        "",
        link,
        "",
        f"Se preferir, salve o contato: {CONSULTOR_DISPLAY}",
    ]
    if foraHorario:
        partes += [
            "",
            "Pode mandar agora mesmo — ele responde no próximo horário comercial "
            "(Seg-Sex 8h-18h, Sáb 8h-13h).",
        ]
    return "\n".join(partes)

FALLBACK_MESSAGE = (
    "Olá! Nosso assistente está temporariamente indisponível. "
    "Em breve nossa equipe entrará em contato. Obrigado!"
)


def isBusinessHours() -> bool:
    """Verifica se está dentro do horário de atendimento da Moper."""
    now = datetime.now(TZ)
    weekday = now.weekday()  # 0=Seg, 5=Sáb, 6=Dom
    hour = now.hour + now.minute / 60

    if weekday < 5:  # Seg a Sex
        return 8.0 <= hour < 18.0
    if weekday == 5:  # Sábado
        return 8.0 <= hour < 13.0
    return False  # Domingo


def wantsHuman(text: str) -> bool:
    """Verifica se o cliente está pedindo para falar com um humano."""
    lower = text.lower()
    return any(kw in lower for kw in TRANSFER_KEYWORDS)


def sendWhatsappMessage(to: str, text: str):
    """Envia mensagem de texto via WhatsApp Business API."""
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {getActiveToken()}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    r.raise_for_status()
    logger.info(f"Mensagem enviada para {to}")


def generateReply(sender: str, userMessage: str, foraHorario: bool = False) -> str:
    """Chama o Claude com histórico de conversa e retorna a resposta.

    O chamador já persistiu a mensagem do cliente via addMessage(), então ela JÁ VEM
    no getHistory(). Anexá-la de novo fazia o modelo ver o cliente repetindo a mesma
    frase duas vezes seguidas — era a causa das perguntas redundantes.
    """
    history = [
        m for m in getHistory(sender) if m["role"] in ("user", "assistant")
    ]

    # Rede de segurança: se a última mensagem não for a do cliente (falha de gravação
    # no banco, por exemplo), garante que ela entre.
    if not history or history[-1] != {"role": "user", "content": userMessage}:
        history.append({"role": "user", "content": userMessage})

    systemPrompt = MOPER_SYSTEM_PROMPT
    if foraHorario:
        systemPrompt += FORA_HORARIO_PROMPT

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=systemPrompt,
        messages=history,
    )
    return response.content[0].text


def extractResumo(reply: str) -> str:
    """Extrai a linha RESUMO: que a IA anexa ao [TRANSFERIR], se houver."""
    match = re.search(r"RESUMO:\s*(.+)", reply)
    return match.group(1).strip() if match else ""


def stripMarkers(reply: str) -> str:
    """Remove [TRANSFERIR] e a linha RESUMO, devolvendo só o texto para o cliente.

    A recomendação de máquina que a IA escreveu antes dos marcadores é útil — o cliente
    deve recebê-la junto com o link do consultor, não em vez dela.
    """
    limpo = re.sub(r"RESUMO:.*", "", reply)
    limpo = limpo.replace("[TRANSFERIR]", "")
    return limpo.strip()


def handleIncomingMessage(sender: str, text: str):
    """Processa a mensagem recebida com todas as regras de negócio."""

    # 1. Conversa já transferida para humano — silêncio total
    if isTransferred(sender):
        logger.info(f"Mensagem de {sender} ignorada — conversa transferida para humano")
        return

    # 2. Fora do horário NÃO desliga mais o bot: ele qualifica 24/7 e avisa quando o
    #    humano retorna. Anúncio pago roda de madrugada — é justo aí que o bot vale.
    foraHorario = not isBusinessHours()

    # 3. Cliente pedindo humano explicitamente
    if wantsHuman(text):
        logger.info(f"Cliente {sender} pediu transferência para humano")
        try:
            sendWhatsappMessage(sender, buildHandoffMessage(foraHorario=foraHorario))
            markTransferred(sender)
        except Exception as e:
            logger.error(f"Erro ao transferir {sender}: {e}")
        return

    # 4. Gera resposta com IA
    try:
        addMessage(sender, "user", text)
        reply = generateReply(sender, text, foraHorario=foraHorario)

        # IA encerrou a qualificação (ou não soube responder) — passa pro consultor.
        # Backstop determinístico: mesmo que a IA não marque, o bot não conversa para
        # sempre — passa a régua em MAX_TURNOS_BOT trocas.
        historico = len(getHistory(sender))
        estourouTurnos = historico >= MAX_TURNOS_BOT * 2

        if "[TRANSFERIR]" in reply or estourouTurnos:
            resumo = extractResumo(reply)
            if estourouTurnos and "[TRANSFERIR]" not in reply:
                logger.info(f"Backstop de turnos ({historico} msgs) — transferindo {sender}")
            logger.info(f"Transferindo {sender} para humano — resumo: {resumo or '(vazio)'}")

            recomendacao = stripMarkers(reply)
            handoff = buildHandoffMessage(resumo=resumo, foraHorario=foraHorario)
            # A recomendação de máquina vai junto — o cliente não perde o que a IA achou.
            texto = f"{recomendacao}\n\n{handoff}" if recomendacao else handoff

            sendWhatsappMessage(sender, texto)
            markTransferred(sender)
            return

        addMessage(sender, "assistant", reply)
        sendWhatsappMessage(sender, reply)

        # Limpeza periódica de mensagens antigas (1% das chamadas)
        import random
        if random.random() < 0.01:
            purgeExpired()

    except Exception as e:
        logger.error(f"Erro ao responder {sender}: {e}")
        try:
            sendWhatsappMessage(sender, FALLBACK_MESSAGE)
        except Exception:
            logger.error(f"Falhou também o fallback para {sender}")
