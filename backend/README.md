# Acervo IF — backend

API em FastAPI do Acervo IF, o repositório de TCCs e Projetos Integradores do IFRN Campus Pau dos Ferros. Começou como uma cópia do [`kit-alunos/`](../kit-alunos/) e cresce uma etapa por vez. Os requisitos estão em [`docs/requisitos-backend.md`](../docs/requisitos-backend.md).

**Etapa atual: 2 (cadastro com senha).** Já dá para criar conta, mas ainda não tem login: todas as rotas de projetos continuam públicas.

## Como rodar

Na pasta `backend/`:

```bash
python -m venv venv
venv\Scripts\activate            # no Linux ou Mac: source venv/bin/activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

Abra http://127.0.0.1:8000/docs. O `seed.py` apaga o `acervo.db` e cria 8 projetos de exemplo, 3 deles abertos para continuação.

Para rodar os testes, que usam um banco temporário e não mexem no `acervo.db`:

```bash
pytest
```

## Arquivos

| Arquivo | O que faz |
|---|---|
| `main.py` | Cria o app, liga o CORS, cria as tabelas e inclui os routers |
| `database.py` | `conectar()`, `criar_tabelas()` e `get_db()`. O banco é o `acervo.db` |
| `seguranca.py` | Hash de senha e JWT. Veio pronto do kit. Por enquanto só o `gerar_hash` é usado |
| `schemas.py` | `ProjetoCreate` e `ProjetoRead`, `UsuarioCreate` e `UsuarioRead` |
| `routers/projetos.py` | As 5 rotas de projetos e os filtros |
| `routers/auth.py` | O cadastro de usuário |
| `seed.py` | Recria o banco com os dados de exemplo |
| `tests/` | Testes com pytest |

## Rotas

| Método e rota | Sucesso | O que faz |
|---|---|---|
| `GET /projetos` | 200 | Lista do ano mais novo para o mais antigo, com filtros opcionais |
| `GET /projetos/{id}` | 200 | Detalhe do projeto (404 se não existe) |
| `POST /projetos` | 201 | Cadastra um projeto |
| `PUT /projetos/{id}` | 200 | Edita um projeto (404 se não existe) |
| `DELETE /projetos/{id}` | 204 | Exclui um projeto (404 se não existe) |

### Filtros do `GET /projetos`

Todos são opcionais e podem ser combinados. O SQL é sempre o mesmo (`SELECT * FROM projetos ORDER BY ano DESC, id DESC`), e os filtros são feitos em Python, com `if` e list comprehension.

| Filtro | Exemplo | O que traz |
|---|---|---|
| `tipo` | `?tipo=PI` | Só TCC ou só PI |
| `curso` | `?curso=ADS` | Só um curso (`Informática` ou `ADS`) |
| `ano` | `?ano=2024` | Só um ano |
| `busca` | `?busca=biblioteca` | O texto aparece no título, no resumo ou nas palavras-chave, sem diferenciar maiúsculas |
| `continuar` | `?continuar=true` | Só os projetos abertos para continuação |

### Exemplo de corpo para o `POST` e o `PUT`

```json
{
  "titulo": "BiblioAgenda",
  "resumo": "Reserva das salas de estudo da biblioteca.",
  "tipo": "PI",
  "curso": "Informática",
  "ano": 2024,
  "autores": "Ana, Bruno e Carla",
  "orientador": "Marcos",
  "palavras_chave": "biblioteca, reservas",
  "link_repositorio": "https://github.com/exemplo/biblioagenda",
  "link_demo": null,
  "aberto_para_continuar": true
}
```

`tipo` aceita só `TCC` ou `PI`, `curso` só `Informática` ou `ADS`, e `ano` vai de 2000 a 2100. Fora disso, a resposta é 422.

## Cadastro de usuário

`POST /auth/cadastro` cria a conta e responde 201 com `id`, `nome`, `email` e `curso`. A resposta **nunca** traz a senha nem o hash.

```json
{
  "nome": "Ana Lívia",
  "email": "ana@exemplo.com",
  "senha": "senha123",
  "curso": "Informática"
}
```

| Regra | O que acontece |
|---|---|
| RN01: o e-mail é único | E-mail repetido dá 409 `"E-mail já cadastrado"` |
| RN02: a senha tem no mínimo 6 caracteres | Senha curta dá 422 (quem responde é o Pydantic) |
| RN03: a senha é guardada só como hash | A rota grava `gerar_hash(senha)` na coluna `senha_hash`, que começa com `$2b$` |

O 409 é feito com um `SELECT` antes do `INSERT`: se já existe um usuário com aquele e-mail, a rota levanta o `HTTPException`.

## Mudou uma coluna?

Não há migrations. Pare o `uvicorn`, rode `python seed.py` (ele apaga o `acervo.db` e cria de novo) e suba o `uvicorn` outra vez.
