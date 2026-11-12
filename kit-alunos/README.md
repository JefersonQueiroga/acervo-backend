# Kit inicial do backend

Este é o ponto de partida do backend do trabalho final. Copie a pasta `backend/` deste kit para o repositório do seu grupo. Ela já roda e já tem uma entidade de exemplo (`produtos`, a mesma da aula).

## 1. Como rodar

Abra o terminal **dentro da pasta `backend/`** e rode:

```bash
python -m venv venv
venv\Scripts\activate            # no Linux ou Mac: source venv/bin/activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

Abra http://127.0.0.1:8000/docs no navegador. As rotas de `produtos` devem aparecer.

O `.env` é opcional: sem ele o projeto roda com valores padrão. Para criar o seu, copie o `.env.example` para `.env` e troque o `SECRET_KEY`.

## 2. O que já vem pronto e o que vocês escrevem

| Já vem pronto (vocês usam, não precisam escrever) | Vocês escrevem (é o que vale nota) |
|---|---|
| `conectar()` e `get_db()` no `database.py` | Os `CREATE TABLE` das entidades do grupo |
| O `seguranca.py` inteiro: `gerar_hash`, `verificar_senha`, `criar_token` e `get_usuario_atual` | Os schemas `XCreate` e `XRead` |
| O `main.py`, com o CORS e o `include_router` | As rotas, com SQL e `?` |
| `requirements.txt`, `.env.example`, `.gitignore` e o comando de deploy | O 404, o `Depends(get_usuario_atual)` nas rotas certas e o 403 do dono |
| O exemplo completo de `produtos` | As rotas `/auth/cadastro` e `/auth/login` (feitas em sala) |

Os arquivos prontos são curtos. Vale a pena abrir e ler cada um.

## 3. Receita para criar uma entidade

Repita estes 5 passos para cada entidade do grupo. O exemplo usa `livros`.

**Passo 1.** No `database.py`, dentro do `criar_tabelas()`, escreva o `CREATE TABLE` no lugar marcado:

```python
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano INTEGER NOT NULL
        )
    """)
```

**Passo 2.** No `schemas.py`, crie o par de schemas. Os campos têm **os mesmos nomes** das colunas:

```python
class LivroCreate(BaseModel):
    titulo: str
    autor: str
    ano: int


class LivroRead(BaseModel):
    id: int
    titulo: str
    autor: str
    ano: int
```

**Passo 3.** Copie `routers/produtos.py` para `routers/livros.py` e troque:

- `produtos` por `livros` (no `prefix`, nas `tags` e no SQL);
- `Produto` por `Livro` (nos schemas e nos nomes das funções);
- as colunas do `INSERT` e do `UPDATE`, com um `?` para cada valor.

**Passo 4.** No `main.py`, ligue o router:

```python
from routers import livros, produtos

app.include_router(livros.router)
```

**Passo 5.** Pare o `uvicorn` (Ctrl+C), apague o `banco.db`, rode `python seed.py` e suba o `uvicorn` de novo. Teste as 5 rotas no `/docs`.

## 4. Filtro opcional em Python

Quer filtrar a listagem (por exemplo, `GET /livros?autor=Machado`)? Busque tudo com um SQL simples e filtre em Python, com um `if` e uma list comprehension:

```python
@router.get("", response_model=list[LivroRead])
def listar_livros(autor: str | None = None, db: Connection = Depends(get_db)):
    livros = [dict(linha) for linha in db.execute("SELECT * FROM livros").fetchall()]
    if autor:
        livros = [l for l in livros if l["autor"] == autor]
    return livros
```

Se `autor` não vier na URL, ele vale `None` e o `if` não faz nada.

## 5. Protegendo uma rota (a partir do Bloco 4)

**Antes** (qualquer pessoa cadastra):

```python
@router.post("", response_model=LivroRead, status_code=201)
def cadastrar_livro(livro: LivroCreate, db: Connection = Depends(get_db)):
    cursor = db.execute(
        "INSERT INTO livros (titulo, autor, ano) VALUES (?, ?, ?)",
        (livro.titulo, livro.autor, livro.ano),
    )
    ...
```

**Depois** (só quem está logado, e o dono vem do token):

```python
from seguranca import get_usuario_atual


@router.post("", response_model=LivroRead, status_code=201)
def cadastrar_livro(
    livro: LivroCreate,
    db: Connection = Depends(get_db),
    usuario: dict = Depends(get_usuario_atual),
):
    cursor = db.execute(
        "INSERT INTO livros (titulo, autor, ano, usuario_id) VALUES (?, ?, ?, ?)",
        (livro.titulo, livro.autor, livro.ano, usuario["id"]),
    )
    ...
```

Para editar ou excluir, confira se o usuário é o dono:

```python
    existente = buscar_livro(id, db)
    if existente["usuario_id"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="Você não é o dono deste livro")
```

Sem token, ou com token inválido, o `get_usuario_atual` já responde 401 sozinho.

## 6. Testando no `/docs` com login

1. Rode a rota `POST /auth/login` com o e-mail e a senha.
2. Copie o valor de `access_token` da resposta (sem as aspas).
3. Clique no botão **Authorize** (o cadeado), no alto da página.
4. Cole o token e clique em **Authorize**.

Agora as rotas protegidas funcionam. O token vale por 60 minutos.

## 7. Erros comuns

| Sintoma | Causa provável |
|---|---|
| Cadastrou, mas o dado sumiu | Faltou o `db.commit()` depois do `execute` |
| `parameters are of unsupported type` | Faltou a vírgula na tupla: escreva `(id,)`, e não `(id)` |
| `Incorrect number of bindings supplied` | O número de `?` é diferente do número de valores na tupla |
| `no such column` ou `table ... has no column named` | Você mudou um `CREATE TABLE` e não apagou o `banco.db`. Apague e rode o `seed.py` |
| `Could not import module "main"` | O `uvicorn` está rodando fora da pasta `backend/` |
| Não consegue apagar o `banco.db` no Windows | O `uvicorn` ainda está aberto. Pare com Ctrl+C antes |

## 8. Deploy no Render (Bloco 6)

No Render, crie um **Web Service** ligado ao repositório do grupo:

| Campo | Valor |
|---|---|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

Em **Environment**, crie as variáveis:

- `SECRET_KEY`: um texto longo e aleatório;
- `ORIGENS_CORS`: `http://localhost:5173,https://seu-front.vercel.app`.

**Atenção:** no plano gratuito, o Render apaga os arquivos do servidor a cada deploy ou reinício. O `banco.db` volta vazio.
