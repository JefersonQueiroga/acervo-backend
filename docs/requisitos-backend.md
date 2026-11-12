# Acervo IF — requisitos do backend

Documento de requisitos da API do **Acervo IF**, o trabalho final de exemplo do professor na disciplina Programação para Internet (IFRN Campus Pau dos Ferros, 3º ano, 2026). Também descreve o **kit inicial** que os grupos de alunos copiam para começar o próprio backend. As regras de código e de trabalho estão no `CLAUDE.md` da raiz.

Princípio geral: os alunos **estão aprendendo FastAPI**. Tudo o que é infraestrutura (conexão, segurança, CORS, deploy) vem pronto; o esforço deles fica nas tabelas, nos schemas, nas rotas e nas regras de acesso.

## 1. O problema

Todo ano os alunos produzem TCCs e Projetos Integradores, e no ano seguinte esses trabalhos somem: ficam no Drive do orientador, num e-mail ou num GitHub que ninguém encontra. Cada aluno faz o seu próprio TCC ou PI, então são dezenas de trabalhos por ano. O resultado:

- quem está começando não sabe o que já foi feito e repete temas;
- bons projetos morrem, porque ninguém sabe que eles podiam ser continuados;
- o aluno não tem onde mostrar o próprio trabalho.

## 2. A solução

Uma API REST em FastAPI que guarda os projetos (título, resumo, autores, orientador, links do código e do sistema) e permite buscar, filtrar, cadastrar e comentar. O front-end em React vai consumir esta API mais tarde.

**Funcionalidade extra: "Procura-se continuação".** Os autores marcam o projeto como aberto para continuar, e a listagem tem um filtro só para esses projetos.

## 3. Quem usa

| Ator | Pode |
|---|---|
| Visitante (sem login) | Listar, buscar e filtrar projetos; ver o detalhe e os comentários; criar conta; fazer login |
| Aluno logado | Tudo o que o visitante faz, mais: cadastrar projetos, ver "meus projetos" e comentar |
| Dono do projeto | Editar e excluir **os próprios** projetos |
| Autor do comentário | Apagar **os próprios** comentários |

Não existe administrador nem perfis.

## 4. Etapa 0: kit inicial dos alunos (`kit-alunos/`)

O esqueleto que cada grupo copia para a pasta `backend/` do repositório do trabalho final. Ele precisa **rodar logo depois de copiado**, com uma entidade de exemplo funcionando.

### 4.1 Arquivos

```
kit-alunos/
├── README.md
└── backend/
    ├── main.py
    ├── database.py
    ├── seguranca.py
    ├── schemas.py
    ├── routers/
    │   ├── __init__.py
    │   └── produtos.py
    ├── seed.py
    ├── requirements.txt
    ├── .env.example
    └── .gitignore
```

### 4.2 O que cada arquivo faz

**`database.py`** (pronto, o grupo só acrescenta as tabelas)

- `conectar()`: abre `banco.db`, com `check_same_thread=False`, `row_factory = sqlite3.Row` e `PRAGMA foreign_keys = ON`.
- `criar_tabelas()`: cria a tabela `usuarios`, a tabela de exemplo `produtos` e tem um comentário bem visível `# COLOQUE AQUI OS CREATE TABLE DO SEU GRUPO`.
- `get_db()`: `yield` dentro de `try/finally`.
- Tabela `usuarios`, igual para todos os grupos:

  ```sql
  CREATE TABLE IF NOT EXISTS usuarios (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nome TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      senha_hash TEXT NOT NULL
  );
  ```

**`seguranca.py`** (pronto, o grupo não edita; cerca de 40 linhas)

- `SECRET_KEY` e `EXPIRA_MINUTOS` vêm do `.env`, com valores padrão (`"troque-esta-chave"` e 60) para rodar sem `.env`.
- `gerar_hash(senha) -> str`: usa o `bcrypt`.
- `verificar_senha(senha, senha_hash) -> bool`
- `criar_token(usuario_id) -> str`: JWT HS256 com payload `{"sub": str(usuario_id), "exp": ...}`. O `sub` precisa ser texto no PyJWT.
- `get_usuario_atual(...) -> dict`: dependência para usar com `Depends`.
  - Lê o token com `HTTPBearer(auto_error=False)`. Assim o botão **Authorize** do `/docs` aceita colar o token.
  - Decodifica o token e busca o usuário no banco.
  - Devolve `{"id", "nome", "email"}`, **sem** `senha_hash`.
  - Sem token, com token inválido, com token expirado ou com usuário que não existe mais: 401 `"Não autenticado"`.

**`main.py`** (pronto)

- `load_dotenv()`, `app = FastAPI(title=...)` e `criar_tabelas()`.
- CORS com as origens lidas de `ORIGENS_CORS` no `.env`, separadas por vírgula. O padrão é `http://localhost:5173`. No deploy, basta acrescentar a URL da Vercel na variável, sem mexer no código.
- `app.include_router(produtos.router)` e um comentário mostrando onde incluir os routers do grupo.

**`schemas.py` e `routers/produtos.py`** (exemplo para copiar)

- É a mesma API da cantina da aula "Revisão de FastAPI": `ProdutoCreate` e `ProdutoRead`, e as 5 rotas públicas (listar, buscar com 404, cadastrar com 201, editar e excluir com 204).
- O código fica **idêntico** ao dos slides, para o aluno reconhecer.

**`seed.py`**: apaga o `banco.db`, recria as tabelas e insere 3 produtos.

**`requirements.txt`**: `fastapi`, `uvicorn`, `bcrypt`, `pyjwt` e `python-dotenv`, nas versões testadas.

**`.env.example`**: `SECRET_KEY`, `EXPIRA_MINUTOS` e `ORIGENS_CORS`. **`.gitignore`**: `venv/`, `.env`, `*.db` e `__pycache__/`.

### 4.3 `kit-alunos/README.md`, escrito para os alunos

Linguagem simples, frases curtas, com exemplos de código. Seções:

1. **Como rodar:** venv, `pip install -r requirements.txt`, `python seed.py`, `uvicorn main:app --reload` e abrir o `/docs`.
2. **O que já vem pronto e o que vocês escrevem:** a tabela do `CLAUDE.md`, em versão para o aluno.
3. **Receita para criar uma entidade** (repetir para cada uma das 3 entidades da trilha):
   1. escrever o `CREATE TABLE` no `criar_tabelas()`;
   2. criar `XCreate` e `XRead` no `schemas.py`, com os mesmos nomes das colunas;
   3. copiar `routers/produtos.py` para `routers/x.py` e trocar nomes, colunas e SQL;
   4. ligar o router com `app.include_router(x.router)` no `main.py`;
   5. apagar o `banco.db`, rodar de novo e testar as 5 rotas no `/docs`.
4. **Filtro opcional em Python:** o exemplo com `if` e list comprehension do `CLAUDE.md`.
5. **Protegendo uma rota (a partir do Bloco 4):** acrescentar `usuario: dict = Depends(get_usuario_atual)` nos parâmetros, gravar `usuario["id"]` no INSERT e fazer a checagem do dono com 403. Um exemplo curto, antes e depois.
6. **Testando no `/docs` com login:** fazer o login, copiar o `access_token`, clicar em Authorize e colar.
7. **Erros comuns:** commit esquecido; `(id)` sem vírgula; número de `?` diferente do número de valores; coluna nova sem apagar o `banco.db`; `uvicorn` rodando fora da pasta.
8. **Deploy no Render (Bloco 6):** Root Directory `backend`, Build Command `pip install -r requirements.txt`, Start Command `uvicorn main:app --host 0.0.0.0 --port $PORT` e as variáveis `SECRET_KEY` e `ORIGENS_CORS`. Avisar que, no plano gratuito, o banco volta vazio a cada deploy ou reinício.

As rotas `/auth/cadastro` e `/auth/login` **não** vêm no kit: são escritas em sala nos Blocos 3 e 4, usando as funções do `seguranca.py`. O código do Acervo (etapas 2 e 3) serve de modelo depois.

### 4.4 Como verificar a etapa 0

Sem deixar testes dentro do kit, rode um script temporário fora dele que confira:

- as 5 rotas de produtos (201, 200, 404, 422, 204);
- `gerar_hash` e `verificar_senha`;
- uma rota protegida de teste com `get_usuario_atual`: 401 sem token, 401 com token adulterado e 200 com token válido;
- o CORS para `http://localhost:5173`.

Depois apague o script e o `banco.db`.

## 5. O Acervo IF: modelo de dados

Três tabelas, todas com relacionamentos 1:N. Os autores do projeto ficam como texto ("Ana, Bruno e Carla"), para evitar uma relação N:N.

```sql
-- usuarios: a mesma do kit, mais a coluna curso
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    curso TEXT NOT NULL
);

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
    aberto_para_continuar INTEGER NOT NULL DEFAULT 0,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS comentarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    texto TEXT NOT NULL,
    data TEXT NOT NULL DEFAULT (date('now')),
    projeto_id INTEGER NOT NULL REFERENCES projetos(id),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id)
);
```

Observações:

- O banco do Acervo se chama `acervo.db`.
- Na etapa 1, `projetos` ainda **não tem** `usuario_id`. A coluna entra na etapa 3 (apagar o banco e rodar o seed de novo).
- `aberto_para_continuar` é 0 ou 1 no SQLite e `bool` no schema; o Pydantic converte.
- O `get_usuario_atual` do Acervo devolve também o `curso`. É o único ajuste no `seguranca.py` copiado do kit.

## 6. Schemas

| Schema | Campos | Observação |
|---|---|---|
| `ProjetoCreate` | `titulo: str`, `resumo: str`, `tipo: Literal["TCC", "PI"]`, `curso: Literal["Informática", "ADS"]`, `ano: int` (2000 a 2100), `autores: str`, `orientador: str`, `palavras_chave: str = ""`, `link_repositorio: str \| None = None`, `link_demo: str \| None = None`, `aberto_para_continuar: bool = False` | Não tem `id` nem `usuario_id` |
| `ProjetoRead` | `id` + os campos acima + `usuario_id` | `usuario_id` só a partir da etapa 3 |
| `UsuarioCreate` | `nome: str`, `email: str`, `senha: str` (mínimo 6 caracteres), `curso: Literal["Informática", "ADS"]` | |
| `UsuarioRead` | `id`, `nome`, `email`, `curso` | **Nunca** devolve senha nem hash |
| `LoginDados` | `email: str`, `senha: str` | Login em JSON |
| `Token` | `access_token: str`, `token_type: str` | `token_type` = `"bearer"` |
| `ComentarioCreate` | `texto: str` (mínimo 1 caractere) | |
| `ComentarioRead` | `id`, `texto`, `data`, `projeto_id`, `usuario_id` | O nome do autor é extra (seção 10) |

## 7. Rotas

| Método e rota | Acesso | Sucesso | O que faz | Etapa |
|---|---|---|---|---|
| `GET /projetos` | público | 200 | Lista, com filtros opcionais (veja abaixo) | 1 |
| `GET /projetos/{id}` | público | 200 | Detalhe (404 se não existe) | 1 |
| `POST /projetos` | público na etapa 1, **login** a partir da 3 | 201 | Cadastra | 1 / 3 |
| `PUT /projetos/{id}` | público na etapa 1, **login + dono** a partir da 3 | 200 | Edita | 1 / 3 |
| `DELETE /projetos/{id}` | público na etapa 1, **login + dono** a partir da 3 | 204 | Exclui o projeto e os comentários dele | 1 / 3 |
| `POST /auth/cadastro` | público | 201 | Cria a conta, com a senha em hash | 2 |
| `POST /auth/login` | público | 200 | Confere e-mail e senha e devolve o token | 3 |
| `GET /auth/eu` | login | 200 | Dados do usuário logado (o React usa no AuthContext) | 3 |
| `GET /meus-projetos` | login | 200 | `SELECT * FROM projetos WHERE usuario_id = ?` | 3 |
| `GET /projetos/{id}/comentarios` | público | 200 | Comentários do projeto, do mais antigo para o mais novo | 4 |
| `POST /projetos/{id}/comentarios` | login | 201 | Comenta (404 se o projeto não existe) | 4 |
| `DELETE /comentarios/{id}` | login + autor | 204 | Apaga o próprio comentário | 4 |

**Filtros do `GET /projetos`, todos em Python:**

1. Faça `SELECT * FROM projetos ORDER BY ano DESC, id DESC` e transforme as linhas em uma lista de dicionários.
2. Aplique cada filtro com um `if` e uma list comprehension:
   - `tipo`, `curso` e `ano`: igualdade;
   - `busca`: o texto, em minúsculas, aparece em `titulo`, `resumo` ou `palavras_chave`, também em minúsculas;
   - `continuar=true`: só os projetos com `aberto_para_continuar` verdadeiro.

## 8. Regras de negócio

| Regra | Descrição | Resposta |
|---|---|---|
| RN01 | O e-mail é único | 409 `"E-mail já cadastrado"` |
| RN02 | A senha tem no mínimo 6 caracteres | 422 (Pydantic) |
| RN03 | A senha é guardada só como hash (`gerar_hash`) | — |
| RN04 | Login errado dá a mesma mensagem para e-mail inexistente e para senha errada | 401 `"E-mail ou senha incorretos"` |
| RN05 | O token expira em 60 minutos (`EXPIRA_MINUTOS`) | 401 depois de expirar |
| RN06 | Rota protegida sem token ou com token inválido | 401 `"Não autenticado"` |
| RN07 | Só o dono edita ou exclui o projeto | 403 `"Você não é o dono deste projeto"` |
| RN08 | Só o autor apaga o comentário | 403 `"Você não é o autor deste comentário"` |
| RN09 | O `usuario_id` do projeto e do comentário vem **do token** (`usuario["id"]`), nunca do corpo | — |
| RN10 | Excluir um projeto apaga antes os comentários dele (`DELETE FROM comentarios WHERE projeto_id = ?`) | 204 |
| RN11 | Comentar em projeto que não existe | 404 `"Projeto não encontrado"` |

## 9. Etapas (acompanham o cronograma do 4º bimestre)

| Etapa | Quando | O que entra | Pronto quando |
|---|---|---|---|
| 0. Kit dos alunos | Agora | Tudo da seção 4 | O kit roda logo depois de copiado e passa na verificação da seção 4.4 |
| 1. CRUD de projetos | Agora, antes do Bloco 3 | Copiar o kit para `backend/`, trocar `banco.db` por `acervo.db`, remover o exemplo de produtos, criar a tabela `projetos` (sem `usuario_id`), o CRUD aberto, os filtros em Python, o seed com 8 projetos e o README | As 5 rotas funcionam no `/docs` e os testes da etapa 1 passam |
| 2. Cadastro com senha | Bloco 3 (12 e 13/11) | Coluna `curso` em `usuarios`, `POST /auth/cadastro` usando `gerar_hash`, RN01 a RN03 | O banco guarda só o hash, e o e-mail repetido dá 409 |
| 3. Login e rotas protegidas | Bloco 4 (19 a 27/11) | `POST /auth/login` com `verificar_senha` e `criar_token`, `GET /auth/eu`, `usuario_id` em `projetos`, `Depends(get_usuario_atual)` em POST/PUT/DELETE, RN04 a RN07 e RN09, `GET /meus-projetos`, seed com 2 usuários | Sem token dá 401, com token de outro usuário dá 403 e o dono consegue tudo |
| 4. Comentários | Até o Bloco 5 (28/11) | Tabela `comentarios`, as 3 rotas, RN08, RN10 e RN11 | Comentar, listar e apagar funcionam com as regras |
| 5. Deploy | Bloco 6 (03 e 04/12) | Instruções de deploy no Render no README, `ORIGENS_CORS` com a URL da Vercel e a decisão sobre o banco (seção 12) | A API responde no Render e o `/docs` abre |

A Entrega 2 dos alunos é em 09/12, e as apresentações vão de 10 a 18/12. O Acervo deve estar pronto e no ar antes disso.

## 10. Extras (opcionais, se sobrar tempo)

- `nome_usuario` no `ComentarioRead`, com `JOIN` entre `comentarios` e `usuarios`.
- Paginação (`pagina` e `por_pagina`) no `GET /projetos`.
- "Entrar com GitHub" (OAuth), só como demonstração do Bloco 6.

## 11. Dados de exemplo e testes do Acervo

**`seed.py`:** apaga o `acervo.db`, recria as tabelas e insere os dados de exemplo.

- **Etapa 1:** 8 projetos fictícios com títulos plausíveis para estudantes de informática do interior do RN (agendamento da biblioteca, caronas para o campus, estoque de uma mercearia…). Devem misturar TCC e PI, os dois cursos e anos de 2022 a 2025, e **3** deles devem estar abertos para continuação.
- **A partir da etapa 3:** 2 usuários de teste (`ana@exemplo.com` e `bruno@exemplo.com`, senha `senha123`), cada um dono de parte dos projetos.
- **A partir da etapa 4:** 2 ou 3 comentários.
- Todos os nomes de pessoas são fictícios.

**Testes (`backend/tests/`, pytest, com banco temporário):**

**Etapa 1**

- `POST /projetos` válido dá 201 com `id`; com `tipo: "Monografia"` dá 422.
- `GET /projetos/9999` dá 404.
- `?tipo=PI` traz só PIs; `?continuar=true` traz só os abertos; `?busca=BIBLIOTECA` acha sem diferenciar maiúsculas.
- `PUT` muda os campos; `DELETE` dá 204 e depois o `GET` dá 404.

**Etapa 2**

- O cadastro dá 201 e a resposta não tem `senha` nem `senha_hash`.
- No banco, `senha_hash` começa com `$2b$`.
- Um e-mail repetido dá 409, e uma senha de 3 caracteres dá 422.

**Etapa 3**

- O login certo dá 200 com `access_token`; a senha errada e o e-mail inexistente dão 401 com a mesma mensagem.
- `POST /projetos` sem token dá 401; com token dá 201, e o `usuario_id` é o do token mesmo que o corpo mande outro.
- `PUT` e `DELETE` com o token de outro usuário dão 403; com o do dono, 200 e 204.
- `GET /meus-projetos` traz só os projetos do dono; um token adulterado dá 401.

**Etapa 4**

- Comentar sem token dá 401; com token dá 201.
- Comentar no projeto 9999 dá 404; apagar o comentário de outro usuário dá 403.
- Excluir o projeto apaga os comentários dele.

## 12. Fora do escopo e decisões em aberto

**Fora do escopo:** refresh token, perfis/administrador, upload de arquivos, ORM e migrations, `async`, Docker.

**Decisões em aberto (o professor decide):**

1. **SQLite no Render.** No plano gratuito, os arquivos do servidor são apagados a cada deploy ou reinício, então o banco volta vazio. Opções:
   - (a) rodar o seed na inicialização quando o banco estiver vazio, que é o suficiente para a apresentação;
   - (b) usar um disco persistente do Render, que é pago;
   - (c) trocar para PostgreSQL mantendo SQL puro (`psycopg`, com `%s` no lugar de `?`).

   Sugestão: (a), e o mesmo para os grupos.
2. **Login em JSON com `HTTPBearer`**, em vez do formulário do `OAuth2PasswordBearer`. É mais simples para o React e para o `/docs`. Se a aula do Bloco 4 usar o `OAuth2PasswordBearer`, alinhar aqui e no kit.
3. **`passlib[bcrypt]`, citado na ementa**, não funciona com o bcrypt 5.x. O kit e o Acervo usam a biblioteca `bcrypt` direto. Vale usar a mesma coisa nos slides do Bloco 3.
