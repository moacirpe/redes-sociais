#!/usr/bin/env python3
"""
Reseta a conversa do bot WhatsApp com um número — apaga histórico e a marca de
"transferido para humano".

Para que serve:
- Testar o bot mais de uma vez com o mesmo celular. Depois que a conversa é passada
  para o consultor, o bot fica em silêncio com aquele número por 30 dias — sem resetar,
  o segundo teste parece que o bot quebrou.
- Recomeçar um atendimento do zero quando a conversa embolou.

Uso:
    python execution/resetConversation.py --listar
    python execution/resetConversation.py 5511925012098
    python execution/resetConversation.py "+55 11 92501-2098"
"""

import re
import sys

from execution.conversationMemory import _getConnection


def normalizar(numero: str) -> str:
    """Deixa só os dígitos — '+55 11 92501-2098' vira '5511925012098'."""
    return re.sub(r"\D", "", numero)


def listarConversas():
    """Mostra os números com conversa ativa, quantas mensagens e se foi transferido."""
    conn = _getConnection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT sender,
                   COUNT(*) AS mensagens,
                   BOOL_OR(transferred) AS transferido,
                   MAX(created_at) AS ultima
            FROM whatsapp_conversations
            GROUP BY sender
            ORDER BY ultima DESC
        """)
        linhas = cur.fetchall()

    if not linhas:
        print("Nenhuma conversa registrada.")
        return

    print(f"{'NÚMERO':<20} {'MSGS':>5}  {'TRANSFERIDO':<12} ÚLTIMA MENSAGEM")
    print("-" * 72)
    for sender, mensagens, transferido, ultima in linhas:
        marca = "SIM (mudo)" if transferido else "não"
        print(f"{sender:<20} {mensagens:>5}  {marca:<12} {ultima:%d/%m/%Y %H:%M}")


def resetar(numero: str) -> int:
    """Apaga todo o histórico do número. Devolve quantas linhas saíram."""
    sender = normalizar(numero)
    if not sender:
        print(f"Número inválido: {numero!r}")
        return 0

    conn = _getConnection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*), BOOL_OR(transferred) FROM whatsapp_conversations "
            "WHERE sender = %s",
            (sender,),
        )
        total, transferido = cur.fetchone()

        if not total:
            print(f"Nada a apagar — {sender} não tem conversa registrada.")
            return 0

        cur.execute("DELETE FROM whatsapp_conversations WHERE sender = %s", (sender,))
        apagadas = cur.rowcount
        conn.commit()

    print(f"✅ {sender}: {apagadas} mensagem(ns) apagada(s).")
    if transferido:
        print("   Marca de 'transferido' removida — o bot volta a responder esse número.")
    return apagadas


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--listar":
        listarConversas()
        return

    resetar(sys.argv[1])


if __name__ == "__main__":
    main()
