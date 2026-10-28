"""Conexão com o SQLite e criação das tabelas."""
import sqlite3
from pathlib import Path

CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "crm.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS clientes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT NOT NULL,
    telefone  TEXT DEFAULT '',
    email     TEXT DEFAULT '',
    criado_em TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS atendimentos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    data       TEXT NOT NULL,
    canal      TEXT NOT NULL CHECK (canal IN ('telefone','whatsapp','email','presencial')),
    assunto    TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'aberto'
               CHECK (status IN ('aberto','em_negociacao','fechado'))
);

CREATE TABLE IF NOT EXISTS negociacoes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    descricao  TEXT NOT NULL,
    valor      REAL NOT NULL CHECK (valor > 0),
    etapa      TEXT NOT NULL DEFAULT 'proposta'
               CHECK (etapa IN ('proposta','negociacao','fechamento')),
    resultado  TEXT NOT NULL DEFAULT 'em_andamento'
               CHECK (resultado IN ('em_andamento','ganha','perdida')),
    criado_em  TEXT NOT NULL,
    fechado_em TEXT
);
"""


def conectar(caminho=CAMINHO_PADRAO):
    """Abre a conexão (use ':memory:' nos testes) e garante que as tabelas existem."""
    conn = sqlite3.connect(str(caminho))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn
