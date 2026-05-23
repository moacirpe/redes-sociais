#!/usr/bin/env python3
"""
Memória de conversa para o bot WhatsApp Moper.

Armazena histórico de mensagens por número de telefone no PostgreSQL.
Conversas inativas por mais de 30 dias são descartadas automaticamente.
"""

import logging
import os
from datetime import datetime, timedelta, timezone

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
EXPIRY_DAYS = 30
MAX_MESSAGES = 20  # máximo de mensagens retidas por conversa

_conn = None


def _getConnection():
    global _conn
    try:
        if _conn is None or _conn.closed:
            _conn = psycopg2.connect(DATABASE_URL)
        _conn.autocommit = False
        return _conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        _conn = None
        raise


def initDB():
    """Cria a tabela de histórico se não existir."""
    conn = _getConnection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS whatsapp_conversations (
                id SERIAL PRIMARY KEY,
                sender VARCHAR(30) NOT NULL,
                role VARCHAR(10) NOT NULL,
                content TEXT NOT NULL,
                transferred BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_wa_sender
                ON whatsapp_conversations(sender, created_at DESC);
        """)
        conn.commit()
    logger.info("Tabela whatsapp_conversations pronta")


def getHistory(sender: str) -> list[dict]:
    """Retorna o histórico de mensagens do sender nos últimos 30 dias."""
    try:
        conn = _getConnection()
        cutoff = datetime.now(timezone.utc) - timedelta(days=EXPIRY_DAYS)
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT role, content FROM whatsapp_conversations
                WHERE sender = %s AND created_at > %s
                ORDER BY created_at ASC
                LIMIT %s
            """, (sender, cutoff, MAX_MESSAGES))
            rows = cur.fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de {sender}: {e}")
        return []


def addMessage(sender: str, role: str, content: str):
    """Salva uma mensagem no histórico."""
    try:
        conn = _getConnection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO whatsapp_conversations (sender, role, content)
                VALUES (%s, %s, %s)
            """, (sender, role, content))
            conn.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar mensagem de {sender}: {e}")
        try:
            conn.rollback()
        except Exception:
            pass


def isTransferred(sender: str) -> bool:
    """Verifica se a conversa foi transferida para humano recentemente."""
    try:
        conn = _getConnection()
        cutoff = datetime.now(timezone.utc) - timedelta(days=EXPIRY_DAYS)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM whatsapp_conversations
                WHERE sender = %s AND transferred = TRUE AND created_at > %s
                LIMIT 1
            """, (sender, cutoff))
            return cur.fetchone() is not None
    except Exception as e:
        logger.error(f"Erro ao verificar transferência de {sender}: {e}")
        return False


def markTransferred(sender: str):
    """Marca a conversa como transferida para humano."""
    try:
        conn = _getConnection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO whatsapp_conversations (sender, role, content, transferred)
                VALUES (%s, 'system', 'TRANSFERIDO_PARA_HUMANO', TRUE)
            """, (sender,))
            conn.commit()
        logger.info(f"Conversa de {sender} marcada como transferida")
    except Exception as e:
        logger.error(f"Erro ao marcar transferência de {sender}: {e}")
        try:
            conn.rollback()
        except Exception:
            pass


def resetConversation(sender: str):
    """Limpa o histórico de um sender (reinicia a conversa)."""
    try:
        conn = _getConnection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM whatsapp_conversations WHERE sender = %s", (sender,)
            )
            conn.commit()
        logger.info(f"Histórico de {sender} limpo")
    except Exception as e:
        logger.error(f"Erro ao limpar histórico de {sender}: {e}")
        try:
            conn.rollback()
        except Exception:
            pass


def purgeExpired():
    """Remove mensagens com mais de 30 dias (limpeza periódica)."""
    try:
        conn = _getConnection()
        cutoff = datetime.now(timezone.utc) - timedelta(days=EXPIRY_DAYS)
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM whatsapp_conversations WHERE created_at < %s", (cutoff,)
            )
            deleted = cur.rowcount
            conn.commit()
        if deleted:
            logger.info(f"Purge: {deleted} mensagens antigas removidas")
    except Exception as e:
        logger.error(f"Erro no purge: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
