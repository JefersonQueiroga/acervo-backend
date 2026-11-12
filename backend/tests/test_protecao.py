from datetime import datetime, timedelta, timezone

import jwt

import seguranca
from conftest import projeto_exemplo


def test_cadastrar_projeto_sem_token_da_401(cliente):
    resposta = cliente.post("/projetos", json=projeto_exemplo())
    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Não autenticado"


def test_usuario_id_vem_do_token_e_nao_do_corpo(cliente, ana, bruno):
    id_ana = cliente.get("/auth/eu", headers=ana).json()["id"]
    id_bruno = cliente.get("/auth/eu", headers=bruno).json()["id"]
    # A Ana tenta cadastrar um projeto em nome do Bruno
    resposta = cliente.post(
        "/projetos", json=projeto_exemplo(usuario_id=id_bruno), headers=ana
    )
    assert resposta.status_code == 201
    assert resposta.json()["usuario_id"] == id_ana


def test_outro_usuario_nao_edita_nem_exclui(cliente, ana, bruno):
    id = cliente.post("/projetos", json=projeto_exemplo(), headers=ana).json()["id"]

    editar = cliente.put(f"/projetos/{id}", json=projeto_exemplo(titulo="Hackeado"), headers=bruno)
    assert editar.status_code == 403
    assert editar.json()["detail"] == "Você não é o dono deste projeto"

    excluir = cliente.delete(f"/projetos/{id}", headers=bruno)
    assert excluir.status_code == 403

    # O projeto continua igual
    assert cliente.get(f"/projetos/{id}").json()["titulo"] == "Agenda da biblioteca"


def test_dono_edita_e_exclui(cliente, ana):
    id = cliente.post("/projetos", json=projeto_exemplo(), headers=ana).json()["id"]
    assert cliente.put(f"/projetos/{id}", json=projeto_exemplo(), headers=ana).status_code == 200
    assert cliente.delete(f"/projetos/{id}", headers=ana).status_code == 204


def test_editar_e_excluir_sem_token_da_401(cliente, ana):
    id = cliente.post("/projetos", json=projeto_exemplo(), headers=ana).json()["id"]
    assert cliente.put(f"/projetos/{id}", json=projeto_exemplo()).status_code == 401
    assert cliente.delete(f"/projetos/{id}").status_code == 401


def test_meus_projetos_traz_so_os_do_dono(cliente, ana, bruno):
    cliente.post("/projetos", json=projeto_exemplo(titulo="Da Ana 1"), headers=ana)
    cliente.post("/projetos", json=projeto_exemplo(titulo="Da Ana 2"), headers=ana)
    cliente.post("/projetos", json=projeto_exemplo(titulo="Do Bruno"), headers=bruno)
    titulos = {p["titulo"] for p in cliente.get("/meus-projetos", headers=ana).json()}
    assert titulos == {"Da Ana 1", "Da Ana 2"}


def test_meus_projetos_sem_token_da_401(cliente):
    assert cliente.get("/meus-projetos").status_code == 401


def test_token_adulterado_da_401(cliente, ana):
    token = ana["Authorization"].removeprefix("Bearer ")
    adulterado = {"Authorization": f"Bearer {token[:-4]}abcd"}
    assert cliente.get("/meus-projetos", headers=adulterado).status_code == 401


def test_token_expirado_da_401(cliente, ana):
    id_ana = cliente.get("/auth/eu", headers=ana).json()["id"]
    passado = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": str(id_ana), "exp": passado}, seguranca.SECRET_KEY, algorithm="HS256"
    )
    resposta = cliente.get("/meus-projetos", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401
