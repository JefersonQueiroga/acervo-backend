import pytest
from fastapi.testclient import TestClient

import database
from main import app


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    # Cada teste usa um banco novo e vazio, numa pasta temporária
    monkeypatch.setattr(database, "ARQUIVO_BANCO", str(tmp_path / "teste.db"))
    database.criar_tabelas()
    return TestClient(app)


def entrar(cliente, email):
    """Cria a conta, faz o login e devolve o cabeçalho com o token."""
    cliente.post(
        "/auth/cadastro",
        json={"nome": "Teste", "email": email, "senha": "senha123", "curso": "ADS"},
    )
    resposta = cliente.post("/auth/login", json={"email": email, "senha": "senha123"})
    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def ana(cliente):
    return entrar(cliente, "ana@exemplo.com")


@pytest.fixture
def bruno(cliente):
    return entrar(cliente, "bruno@exemplo.com")


def projeto_exemplo(**mudancas):
    projeto = {
        "titulo": "Agenda da biblioteca",
        "resumo": "Reserva de salas de estudo.",
        "tipo": "PI",
        "curso": "Informática",
        "ano": 2024,
        "autores": "Ana e Bruno",
        "orientador": "Carlos",
        "palavras_chave": "biblioteca, reservas",
    }
    projeto.update(mudancas)
    return projeto
