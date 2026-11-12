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
