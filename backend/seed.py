import os

from database import ARQUIVO_BANCO, conectar, criar_tabelas

# Começa do zero: apaga o banco antigo e cria as tabelas de novo
if os.path.exists(ARQUIVO_BANCO):
    os.remove(ARQUIVO_BANCO)
criar_tabelas()

# Todos os nomes são fictícios.
# Ordem das colunas: titulo, resumo, tipo, curso, ano, autores, orientador,
# palavras_chave, link_repositorio, link_demo, aberto_para_continuar
projetos = [
    (
        "BiblioAgenda: agendamento de salas de estudo da biblioteca",
        "Sistema web para reservar as salas de estudo em grupo da biblioteca do campus, com controle de horários e aviso por e-mail.",
        "PI", "Informática", 2023,
        "Ana Lívia Rocha, Bruno Henrique Dantas e Carla Nunes",
        "Marcos Vinícius Fernandes",
        "biblioteca, agendamento, reservas",
        "https://github.com/exemplo/biblioagenda", None, 1,
    ),
    (
        "Carona IF: caronas solidárias para o campus",
        "Aplicativo que conecta alunos e servidores que fazem o mesmo trajeto entre as cidades da região e o campus Pau dos Ferros.",
        "TCC", "ADS", 2024,
        "Diego Alencar Souza",
        "Patrícia Lima Carvalho",
        "caronas, mobilidade, transporte",
        "https://github.com/exemplo/carona-if", "https://carona-if.exemplo.com", 1,
    ),
    (
        "Estoque Fácil: controle de estoque para mercearias de bairro",
        "Sistema simples de entrada e saída de mercadorias, pensado para pequenos comércios do interior que ainda usam caderno.",
        "PI", "Informática", 2022,
        "Elisa Gomes, Fábio Medeiros e Gabriel Freitas",
        "Marcos Vinícius Fernandes",
        "estoque, comércio local, vendas",
        "https://github.com/exemplo/estoque-facil", None, 0,
    ),
    (
        "Feira Viva: vitrine on-line para a feira livre de Pau dos Ferros",
        "Site onde os feirantes divulgam os produtos e os preços da semana, e os clientes fazem pedidos para retirar no sábado.",
        "TCC", "ADS", 2025,
        "Helena Maia Bezerra",
        "Ricardo Augusto Queiroz",
        "feira, agricultura familiar, pedidos",
        "https://github.com/exemplo/feira-viva", "https://feiraviva.exemplo.com", 0,
    ),
    (
        "Merenda em Dia: cardápio e avaliação da merenda escolar",
        "Aplicação para divulgar o cardápio da semana e coletar a avaliação dos alunos sobre as refeições do refeitório.",
        "PI", "Informática", 2024,
        "Igor Lucena, Júlia Torres e Kauã Pinheiro",
        "Patrícia Lima Carvalho",
        "merenda, refeitório, avaliação",
        None, None, 1,
    ),
    (
        "AquaSertão: monitoramento do nível de cisternas com Arduino",
        "Protótipo com sensor ultrassônico e Arduino que mede o nível de água de cisternas na zona rural e mostra os dados num painel web.",
        "TCC", "ADS", 2023,
        "Larissa Fontes de Oliveira",
        "Ricardo Augusto Queiroz",
        "cisternas, arduino, internet das coisas, seca",
        "https://github.com/exemplo/aquasertao", None, 0,
    ),
    (
        "Achados IF: achados e perdidos do campus",
        "Mural on-line para registrar objetos perdidos e encontrados no campus, com foto, local e contato de quem achou.",
        "PI", "Informática", 2025,
        "Mateus Rebouças e Natália Sales",
        "Marcos Vinícius Fernandes",
        "achados e perdidos, campus, mural",
        "https://github.com/exemplo/achados-if", "https://achados-if.exemplo.com", 0,
    ),
    (
        "Horta Escolar Digital: registro de plantio e colheita",
        "Sistema para os projetos de horta das escolas municipais registrarem o que foi plantado, a irrigação e a colheita de cada canteiro.",
        "TCC", "ADS", 2022,
        "Otávio Cavalcante Lima",
        "Patrícia Lima Carvalho",
        "horta, escolas, agricultura",
        None, None, 0,
    ),
]

conexao = conectar()
for projeto in projetos:
    conexao.execute(
        """INSERT INTO projetos (titulo, resumo, tipo, curso, ano, autores, orientador,
               palavras_chave, link_repositorio, link_demo, aberto_para_continuar)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        projeto,
    )
conexao.commit()
conexao.close()

print(f"Banco {ARQUIVO_BANCO} criado com {len(projetos)} projetos.")
