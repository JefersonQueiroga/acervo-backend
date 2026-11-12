import sqlite3

ARQUIVO_BANCO = "banco.db"


def conectar():
    conexao = sqlite3.connect(ARQUIVO_BANCO, check_same_thread=False)
    conexao.row_factory = sqlite3.Row  # cada linha funciona como um dicionário
    conexao.execute("PRAGMA foreign_keys = ON")  # o SQLite passa a respeitar o REFERENCES
    return conexao


def criar_tabelas():
    conexao = conectar()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL
        )
    """)

    # Tabela de exemplo (a mesma da aula). Pode apagar quando não precisar mais.
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL
        )
    """)

    # ==========================================================
    # COLOQUE AQUI OS CREATE TABLE DO SEU GRUPO
    # ==========================================================

    conexao.commit()
    conexao.close()


def get_db():
    conexao = conectar()
    try:
        yield conexao
    finally:
        conexao.close()
