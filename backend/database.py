import sqlite3

ARQUIVO_BANCO = "acervo.db"


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

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            resumo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            curso TEXT NOT NULL,
            ano INTEGER NOT NULL,
            autores TEXT NOT NULL,
            orientador TEXT NOT NULL,
            palavras_chave TEXT NOT NULL DEFAULT '',
            link_repositorio TEXT,
            link_demo TEXT,
            aberto_para_continuar INTEGER NOT NULL DEFAULT 0
        )
    """)

    conexao.commit()
    conexao.close()


def get_db():
    conexao = conectar()
    try:
        yield conexao
    finally:
        conexao.close()
