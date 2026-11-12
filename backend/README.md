# Acervo IF — backend

API em FastAPI do Acervo IF, o repositório de TCCs e Projetos Integradores do IFRN Campus Pau dos Ferros. Começou como uma cópia do [`kit-alunos/`](../kit-alunos/) e cresce uma etapa por vez. Os requisitos estão em [`docs/requisitos-backend.md`](../docs/requisitos-backend.md).

**Etapa atual: 3 (login e rotas protegidas).** Qualquer pessoa lista e lê os projetos. Para cadastrar é preciso estar logado, e só o dono edita ou exclui.

## Como rodar

Na pasta `backend/`:

```bash
python -m venv venv
venv\Scripts\activate            # no Linux ou Mac: source venv/bin/activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

Abra http://127.0.0.1:8000/docs. O `seed.py` apaga o `acervo.db` e cria:

| Usuário | Senha | Curso | Projetos |
|---|---|---|---|
| `ana@exemplo.com` | `senha123` | Informática | os 4 PIs de Informática |
| `bruno@exemplo.com` | `senha123` | ADS | os 4 TCCs de ADS |

São 8 projetos ao todo, 3 deles abertos para continuação.

Para rodar os testes, que usam um banco temporário e não mexem no `acervo.db`:

```bash
pytest
```

## Arquivos

| Arquivo | O que faz |
|---|---|
| `main.py` | Cria o app, liga o CORS, cria as tabelas e inclui os routers |
| `database.py` | `conectar()`, `criar_tabelas()` e `get_db()`. O banco é o `acervo.db` |
| `seguranca.py` | Hash de senha e JWT. Veio pronto do kit; a única mudança é que o `get_usuario_atual` devolve também o `curso` |
| `schemas.py` | `ProjetoCreate`, `ProjetoRead`, `UsuarioCreate`, `UsuarioRead`, `LoginDados` e `Token` |
| `routers/projetos.py` | As 5 rotas de projetos, os filtros e a checagem do dono |
| `routers/meus_projetos.py` | Os projetos do usuário logado |
| `routers/auth.py` | Cadastro, login e "quem sou eu" |
| `seed.py` | Recria o banco com os dados de exemplo |
| `tests/` | Testes com pytest |

## Rotas

| Método e rota | Acesso | Sucesso | O que faz |
|---|---|---|---|
| `GET /projetos` | público | 200 | Lista do ano mais novo para o mais antigo, com filtros opcionais |
| `GET /projetos/{id}` | público | 200 | Detalhe do projeto (404 se não existe) |
| `POST /projetos` | login | 201 | Cadastra um projeto. O dono é quem está logado |
| `PUT /projetos/{id}` | login + dono | 200 | Edita um projeto |
| `DELETE /projetos/{id}` | login + dono | 204 | Exclui um projeto |
| `GET /meus-projetos` | login | 200 | Só os projetos do usuário logado |
| `POST /auth/cadastro` | público | 201 | Cria a conta |
| `POST /auth/login` | público | 200 | Confere e-mail e senha e devolve o token |
| `GET /auth/eu` | login | 200 | Dados do usuário logado (o React vai usar no AuthContext) |

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

`tipo` aceita só `TCC` ou `PI`, `curso` só `Informática` ou `ADS`, e `ano` vai de 2000 a 2100. Fora disso, a resposta é 422. O corpo **não** tem `usuario_id`: se vier, é ignorado.

## Cadastro e login

`POST /auth/cadastro` recebe nome, e-mail, senha e curso e responde 201 com `id`, `nome`, `email` e `curso`. A resposta **nunca** traz a senha nem o hash.

```json
{
  "nome": "Ana Lívia",
  "email": "ana@exemplo.com",
  "senha": "senha123",
  "curso": "Informática"
}
```

`POST /auth/login` recebe e-mail e senha em JSON e devolve o token:

```json
{ "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```

### Testando no `/docs` com login

1. Rode `POST /auth/login` com `ana@exemplo.com` e `senha123`.
2. Copie o valor de `access_token`, sem as aspas.
3. Clique em **Authorize** (o cadeado), cole o token e confirme.

O token vale por 60 minutos.

## Regras de negócio

| Regra | O que acontece |
|---|---|
| RN01: o e-mail é único | E-mail repetido dá 409 `"E-mail já cadastrado"`. A rota faz um `SELECT` antes do `INSERT` |
| RN02: a senha tem no mínimo 6 caracteres | Senha curta dá 422 (quem responde é o Pydantic) |
| RN03: a senha é guardada só como hash | A rota grava `gerar_hash(senha)` na coluna `senha_hash`, que começa com `$2b$` |
| RN04: login errado não diz o que errou | E-mail que não existe e senha errada dão o mesmo 401 `"E-mail ou senha incorretos"` |
| RN05: o token expira | Depois de 60 minutos (`EXPIRA_MINUTOS`), dá 401 |
| RN06: rota protegida precisa de token | Sem token, ou com token inválido, dá 401 `"Não autenticado"` |
| RN07: só o dono edita ou exclui | Outro usuário recebe 403 `"Você não é o dono deste projeto"` |
| RN09: o dono vem do token | O `INSERT` grava `usuario["id"]`, nunca um valor do corpo |

## Mudou uma coluna?

Não há migrations. Pare o `uvicorn`, rode `python seed.py` (ele apaga o `acervo.db` e cria de novo) e suba o `uvicorn` outra vez.
