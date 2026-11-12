import database


def usuario_exemplo(**mudancas):
    usuario = {
        "nome": "Ana Lívia",
        "email": "ana@exemplo.com",
        "senha": "senha123",
        "curso": "Informática",
    }
    usuario.update(mudancas)
    return usuario


def test_cadastro_da_201_sem_senha_na_resposta(cliente):
    resposta = cliente.post("/auth/cadastro", json=usuario_exemplo())
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["id"] > 0
    assert dados["email"] == "ana@exemplo.com"
    assert dados["curso"] == "Informática"
    assert "senha" not in dados
    assert "senha_hash" not in dados


def test_banco_guarda_so_o_hash(cliente):
    cliente.post("/auth/cadastro", json=usuario_exemplo())
    conexao = database.conectar()
    linha = conexao.execute(
        "SELECT * FROM usuarios WHERE email = ?", ("ana@exemplo.com",)
    ).fetchone()
    conexao.close()
    assert linha["senha_hash"].startswith("$2b$")
    assert linha["senha_hash"] != "senha123"


def test_email_repetido_da_409(cliente):
    cliente.post("/auth/cadastro", json=usuario_exemplo())
    resposta = cliente.post("/auth/cadastro", json=usuario_exemplo(nome="Outra Ana"))
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "E-mail já cadastrado"


def test_senha_curta_da_422(cliente):
    resposta = cliente.post("/auth/cadastro", json=usuario_exemplo(senha="abc"))
    assert resposta.status_code == 422


def test_curso_invalido_da_422(cliente):
    resposta = cliente.post("/auth/cadastro", json=usuario_exemplo(curso="Medicina"))
    assert resposta.status_code == 422


def test_login_certo_da_token(cliente):
    cliente.post("/auth/cadastro", json=usuario_exemplo())
    resposta = cliente.post(
        "/auth/login", json={"email": "ana@exemplo.com", "senha": "senha123"}
    )
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["access_token"]
    assert dados["token_type"] == "bearer"


def test_login_errado_da_a_mesma_mensagem(cliente):
    cliente.post("/auth/cadastro", json=usuario_exemplo())
    senha_errada = cliente.post(
        "/auth/login", json={"email": "ana@exemplo.com", "senha": "errada123"}
    )
    email_inexistente = cliente.post(
        "/auth/login", json={"email": "ninguem@exemplo.com", "senha": "senha123"}
    )
    assert senha_errada.status_code == 401
    assert email_inexistente.status_code == 401
    assert senha_errada.json()["detail"] == "E-mail ou senha incorretos"
    assert email_inexistente.json()["detail"] == senha_errada.json()["detail"]


def test_eu_devolve_o_usuario_logado(cliente, ana):
    resposta = cliente.get("/auth/eu", headers=ana)
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["email"] == "ana@exemplo.com"
    assert "curso" in dados
    assert "senha_hash" not in dados


def test_eu_sem_token_da_401(cliente):
    resposta = cliente.get("/auth/eu")
    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Não autenticado"
