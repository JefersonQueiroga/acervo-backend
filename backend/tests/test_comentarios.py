import database
from conftest import projeto_exemplo


def criar_projeto(cliente, headers):
    return cliente.post("/projetos", json=projeto_exemplo(), headers=headers).json()["id"]


def test_comentar_sem_token_da_401(cliente, ana):
    id = criar_projeto(cliente, ana)
    resposta = cliente.post(f"/projetos/{id}/comentarios", json={"texto": "Legal!"})
    assert resposta.status_code == 401


def test_comentar_com_token_da_201(cliente, ana, bruno):
    id = criar_projeto(cliente, ana)
    id_bruno = cliente.get("/auth/eu", headers=bruno).json()["id"]
    resposta = cliente.post(
        f"/projetos/{id}/comentarios", json={"texto": "Legal!"}, headers=bruno
    )
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["texto"] == "Legal!"
    assert dados["projeto_id"] == id
    assert dados["usuario_id"] == id_bruno
    assert len(dados["data"]) == 10  # AAAA-MM-DD


def test_comentario_vazio_da_422(cliente, ana):
    id = criar_projeto(cliente, ana)
    resposta = cliente.post(f"/projetos/{id}/comentarios", json={"texto": ""}, headers=ana)
    assert resposta.status_code == 422


def test_comentar_em_projeto_inexistente_da_404(cliente, ana):
    resposta = cliente.post("/projetos/9999/comentarios", json={"texto": "Oi"}, headers=ana)
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Projeto não encontrado"


def test_listar_do_mais_antigo_para_o_mais_novo(cliente, ana):
    id = criar_projeto(cliente, ana)
    for texto in ["primeiro", "segundo", "terceiro"]:
        cliente.post(f"/projetos/{id}/comentarios", json={"texto": texto}, headers=ana)
    resposta = cliente.get(f"/projetos/{id}/comentarios")  # público, sem token
    assert resposta.status_code == 200
    assert [c["texto"] for c in resposta.json()] == ["primeiro", "segundo", "terceiro"]


def test_listar_so_os_comentarios_do_projeto(cliente, ana):
    id_1 = criar_projeto(cliente, ana)
    id_2 = criar_projeto(cliente, ana)
    cliente.post(f"/projetos/{id_1}/comentarios", json={"texto": "no 1"}, headers=ana)
    cliente.post(f"/projetos/{id_2}/comentarios", json={"texto": "no 2"}, headers=ana)
    textos = [c["texto"] for c in cliente.get(f"/projetos/{id_1}/comentarios").json()]
    assert textos == ["no 1"]


def test_autor_apaga_o_proprio_comentario(cliente, ana):
    id = criar_projeto(cliente, ana)
    comentario = cliente.post(
        f"/projetos/{id}/comentarios", json={"texto": "Oi"}, headers=ana
    ).json()
    assert cliente.delete(f"/comentarios/{comentario['id']}", headers=ana).status_code == 204
    assert cliente.get(f"/projetos/{id}/comentarios").json() == []


def test_apagar_comentario_de_outro_da_403(cliente, ana, bruno):
    id = criar_projeto(cliente, ana)
    comentario = cliente.post(
        f"/projetos/{id}/comentarios", json={"texto": "Oi"}, headers=ana
    ).json()
    resposta = cliente.delete(f"/comentarios/{comentario['id']}", headers=bruno)
    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Você não é o autor deste comentário"


def test_apagar_comentario_inexistente_da_404(cliente, ana):
    assert cliente.delete("/comentarios/9999", headers=ana).status_code == 404


def test_excluir_projeto_apaga_os_comentarios(cliente, ana, bruno):
    id = criar_projeto(cliente, ana)
    cliente.post(f"/projetos/{id}/comentarios", json={"texto": "Oi"}, headers=bruno)
    cliente.post(f"/projetos/{id}/comentarios", json={"texto": "Olá"}, headers=ana)

    assert cliente.delete(f"/projetos/{id}", headers=ana).status_code == 204

    conexao = database.conectar()
    sobraram = conexao.execute(
        "SELECT * FROM comentarios WHERE projeto_id = ?", (id,)
    ).fetchall()
    conexao.close()
    assert sobraram == []
