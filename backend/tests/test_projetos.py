from conftest import projeto_exemplo


def test_cadastrar_projeto_valido(cliente, ana):
    resposta = cliente.post("/projetos", json=projeto_exemplo(), headers=ana)
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["id"] > 0
    assert dados["titulo"] == "Agenda da biblioteca"
    assert dados["aberto_para_continuar"] is False


def test_cadastrar_tipo_invalido_da_422(cliente, ana):
    resposta = cliente.post("/projetos", json=projeto_exemplo(tipo="Monografia"), headers=ana)
    assert resposta.status_code == 422


def test_cadastrar_ano_fora_da_faixa_da_422(cliente, ana):
    resposta = cliente.post("/projetos", json=projeto_exemplo(ano=1999), headers=ana)
    assert resposta.status_code == 422


def test_detalhar_projeto_inexistente_da_404(cliente):
    resposta = cliente.get("/projetos/9999")
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Projeto não encontrado"


def test_listar_ordena_do_mais_novo_para_o_mais_antigo(cliente, ana):
    cliente.post("/projetos", json=projeto_exemplo(titulo="Antigo", ano=2022), headers=ana)
    cliente.post("/projetos", json=projeto_exemplo(titulo="Novo", ano=2025), headers=ana)
    titulos = [p["titulo"] for p in cliente.get("/projetos").json()]
    assert titulos == ["Novo", "Antigo"]


def test_filtro_tipo(cliente, ana):
    cliente.post("/projetos", json=projeto_exemplo(tipo="PI"), headers=ana)
    cliente.post("/projetos", json=projeto_exemplo(tipo="TCC", curso="ADS"), headers=ana)
    projetos = cliente.get("/projetos?tipo=PI").json()
    assert len(projetos) == 1
    assert all(p["tipo"] == "PI" for p in projetos)


def test_filtro_curso_e_ano(cliente, ana):
    cliente.post("/projetos", json=projeto_exemplo(curso="ADS", ano=2023), headers=ana)
    cliente.post("/projetos", json=projeto_exemplo(curso="ADS", ano=2024), headers=ana)
    cliente.post("/projetos", json=projeto_exemplo(curso="Informática", ano=2023), headers=ana)
    projetos = cliente.get("/projetos?curso=ADS&ano=2023").json()
    assert len(projetos) == 1
    assert projetos[0]["curso"] == "ADS" and projetos[0]["ano"] == 2023


def test_filtro_continuar(cliente, ana):
    cliente.post("/projetos", json=projeto_exemplo(aberto_para_continuar=True), headers=ana)
    cliente.post("/projetos", json=projeto_exemplo(aberto_para_continuar=False), headers=ana)
    projetos = cliente.get("/projetos?continuar=true").json()
    assert len(projetos) == 1
    assert projetos[0]["aberto_para_continuar"] is True


def test_busca_ignora_maiusculas(cliente, ana):
    cliente.post("/projetos", json=projeto_exemplo(titulo="Agenda da Biblioteca"), headers=ana)
    cliente.post("/projetos", json=projeto_exemplo(titulo="Caronas", resumo="Transporte.", palavras_chave="mobilidade"), headers=ana)
    projetos = cliente.get("/projetos?busca=BIBLIOTECA").json()
    assert len(projetos) == 1
    assert projetos[0]["titulo"] == "Agenda da Biblioteca"


def test_busca_tambem_olha_resumo_e_palavras_chave(cliente, ana):
    cliente.post("/projetos", json=projeto_exemplo(titulo="A", resumo="Usa Arduino.", palavras_chave=""), headers=ana)
    cliente.post("/projetos", json=projeto_exemplo(titulo="B", resumo="Nada.", palavras_chave="arduino, sensores"), headers=ana)
    cliente.post("/projetos", json=projeto_exemplo(titulo="C", resumo="Nada.", palavras_chave="web"), headers=ana)
    titulos = {p["titulo"] for p in cliente.get("/projetos?busca=arduino").json()}
    assert titulos == {"A", "B"}


def test_editar_muda_os_campos(cliente, ana):
    id = cliente.post("/projetos", json=projeto_exemplo(), headers=ana).json()["id"]
    resposta = cliente.put(
        f"/projetos/{id}",
        json=projeto_exemplo(titulo="Título novo", aberto_para_continuar=True),
        headers=ana,
    )
    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Título novo"
    assert cliente.get(f"/projetos/{id}").json()["aberto_para_continuar"] is True


def test_editar_projeto_inexistente_da_404(cliente, ana):
    resposta = cliente.put("/projetos/9999", json=projeto_exemplo(), headers=ana)
    assert resposta.status_code == 404


def test_excluir_da_204_e_depois_404(cliente, ana):
    id = cliente.post("/projetos", json=projeto_exemplo(), headers=ana).json()["id"]
    assert cliente.delete(f"/projetos/{id}", headers=ana).status_code == 204
    assert cliente.get(f"/projetos/{id}").status_code == 404
