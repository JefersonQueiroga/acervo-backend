# Acervo IF

Repositório on-line de TCCs e Projetos Integradores dos alunos do IFRN Campus Pau dos Ferros. É o trabalho final de exemplo da disciplina Programação para Internet (3º ano, 2026), feito junto com a turma.

## Como rodar no Windows

Siga os passos na ordem. Se der erro, procure a mensagem na tabela [Deu erro?](#deu-erro), no fim desta seção.

### 1. Abrir o terminal na pasta `backend`

**Jeito mais fácil:** no Explorador de Arquivos, entre na pasta `backend` do projeto, clique na barra de endereço, apague o que está lá, digite `powershell` e aperte Enter. O PowerShell abre já dentro da pasta.

**No VS Code:** abra a pasta `backend` (Arquivo → Abrir Pasta) e depois o terminal (Terminal → Novo Terminal, ou Ctrl+').

Confira se está no lugar certo:

```powershell
dir
```

Precisam aparecer o `main.py`, o `seed.py` e o `requirements.txt`. Se não aparecerem, você está na pasta errada.

Confira também o Python, que já vem instalado nos computadores:

```powershell
python --version
```

Deve aparecer `Python 3.11` ou mais novo. Se o comando abrir a Microsoft Store ou der erro, use `py` no lugar de `python` em todos os comandos (por exemplo, `py --version` e `py -m venv venv`).

### 2. Criar o ambiente virtual (só na primeira vez)

```powershell
python -m venv venv
```

Isso cria a pasta `venv`, onde ficam as bibliotecas deste projeto. Ela não vai para o Git.

### 3. Ativar o ambiente virtual

```powershell
venv\Scripts\activate
```

Deu certo quando aparece `(venv)` no começo da linha:

```
(venv) PS C:\...\backend>
```


O `-Scope Process` vale só para esta janela do PowerShell. Quando você fechar a janela, tudo volta ao normal. Por isso o comando precisa ser repetido toda vez que você abrir um terminal novo.

> **Usando o VS Code?** Aperte Ctrl+Shift+P, digite "Python: Select Interpreter" e escolha o que tem `venv` no caminho. A partir daí, todo terminal novo do VS Code já abre com o `(venv)` ativado.

### 4. Instalar as bibliotecas (só na primeira vez)

Com o `(venv)` aparecendo:

```powershell
python -m pip install -r requirements.txt
```

Demora um pouco. No fim, aparece `Successfully installed fastapi-... uvicorn-...`.

> Use `python -m pip` em vez de só `pip`. Assim as bibliotecas vão para o `venv`, e não para outro Python do computador.

### 5. Criar o banco com os dados de exemplo

```powershell
python seed.py
```

Deve aparecer `Banco acervo.db criado com 2 usuários, 8 projetos e 3 comentários.`

Rode isso de novo sempre que quiser **voltar o banco ao começo**. Atenção: o seed apaga tudo o que foi cadastrado.

### 6. Subir a API

```powershell
uvicorn main:app --reload
```

Quando aparecer `Application startup complete.`, abra no navegador:

**http://127.0.0.1:8000/docs**

O terminal fica "preso" enquanto a API está no ar. Isso é normal. Com o `--reload`, a API reinicia sozinha quando você salva um arquivo `.py`.

Para **parar**, clique no terminal e aperte **Ctrl+C**.

### 7. Testar com login no `/docs`

O seed cria dois usuários, os dois com a senha `senha123`:

| E-mail | Curso |
|---|---|
| `ana@exemplo.com` | Informática |
| `bruno@exemplo.com` | ADS |

1. Abra `POST /auth/login`, clique em **Try it out** e mande `{"email": "ana@exemplo.com", "senha": "senha123"}`.
2. Copie o valor de `access_token`, sem as aspas.
3. Clique em **Authorize** (o cadeado), cole o token e confirme.

Agora as rotas com cadeado funcionam.

### Nas próximas vezes

Os passos 2 e 4 são feitos só uma vez. Da segunda vez em diante, abra o terminal na pasta `backend` e rode:

```powershell
venv\Scripts\activate
uvicorn main:app --reload
```

(Antes do `activate`, se precisar: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.)

### Rodando sem ativar o `venv`

Se a ativação não funcionar de jeito nenhum, dá para chamar o Python do `venv` direto, sem o `activate`:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe seed.py
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

### Rodando os testes

Com o `(venv)` ativado:

```powershell
python -m pytest
```

Os testes usam um banco temporário e não mexem no seu `acervo.db`. O resultado esperado é algo como `41 passed`.

### Deu erro?

| Mensagem ou sintoma | O que fazer |
|---|---|
| `python` abre a Microsoft Store | Use `py` no lugar de `python` em todos os comandos |
| `'python' não é reconhecido como nome de cmdlet` | Tente `py`. Se também não funcionar, chame o professor |
| `a execução de scripts foi desabilitada neste sistema` | Rode `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` e ative de novo (passo 3) |
| `'pip' não é reconhecido` | Use `python -m pip` em vez de `pip` |
| `'uvicorn' não é reconhecido` | O `venv` não está ativado (falta o `(venv)` no começo da linha) ou as bibliotecas não foram instaladas. Refaça os passos 3 e 4 |
| `No module named 'fastapi'` | Mesma causa do anterior: ative o `venv` e instale as bibliotecas |
| `CERTIFICATE_VERIFY_FAILED` ou `SSLError` no `pip install` | Acontece em algumas redes com proxy, como a do campus. Rode: `python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt` |
| `Could not import module "main"` | O terminal não está na pasta `backend`. Volte ao passo 1 e confira com `dir` |
| `[WinError 10048]` ou "endereço já em uso" | Já tem uma API rodando na porta 8000, talvez em outro terminal. Feche a outra ou use `uvicorn main:app --reload --port 8001` e abra http://127.0.0.1:8001/docs |
| `[WinError 32]` ao rodar o `seed.py` | O `uvicorn` está usando o `acervo.db`. Pare a API com Ctrl+C, rode o seed e suba de novo |
| `no such column` ou `has no column named` | O banco é de uma versão antiga do código. Pare a API, rode `python seed.py` e suba de novo |
| Letras com acento aparecem estranhas no terminal (`usu�rios`) | É só a exibição do terminal; os dados estão certos. Pode ignorar |
| O `/docs` não abre no navegador | Confira se o terminal mostra `Application startup complete.` e se o endereço é `http://127.0.0.1:8000/docs`, com `http` e não `https` |

## O que tem aqui

| Pasta | O que é |
|---|---|
| [`kit-alunos/`](kit-alunos/) | O esqueleto que cada grupo copia para começar o backend do trabalho final (etapa 0) |
| [`backend/`](backend/) | A API do Acervo IF, que começa como uma cópia do kit e cresce etapa por etapa. O [README dele](backend/README.md) explica as rotas e as regras |
| [`docs/requisitos-backend.md`](docs/requisitos-backend.md) | Os requisitos completos e o cronograma das etapas |

## Etapas

Cada etapa concluída tem um commit e uma tag (`etapa-0`, `etapa-1`, ...). Para ver o código como estava numa etapa:

```bash
git checkout etapa-1
```

| Etapa | Situação |
|---|---|
| 0. Kit dos alunos | pronta |
| 1. CRUD de projetos | pronta |
| 2. Cadastro com senha | pronta |
| 3. Login e rotas protegidas | pronta |
| 4. Comentários | pronta |
| 5. Deploy | — |
