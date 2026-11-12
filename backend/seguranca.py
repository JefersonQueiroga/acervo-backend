import os
from datetime import datetime, timedelta, timezone
from sqlite3 import Connection

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave")
EXPIRA_MINUTOS = int(os.getenv("EXPIRA_MINUTOS", "60"))
ALGORITMO = "HS256"

# auto_error=False: quem responde 401 somos nós, com a nossa mensagem
esquema_bearer = HTTPBearer(auto_error=False)


def gerar_hash(senha: str) -> str:
    # o bcrypt só aceita até 72 bytes, por isso o [:72]
    return bcrypt.hashpw(senha.encode()[:72], bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode()[:72], senha_hash.encode())


def criar_token(usuario_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=EXPIRA_MINUTOS)
    dados = {"sub": str(usuario_id), "exp": expira}
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITMO)


def get_usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    db: Connection = Depends(get_db),
) -> dict:
    erro = HTTPException(status_code=401, detail="Não autenticado")
    if credenciais is None:
        raise erro
    try:
        dados = jwt.decode(credenciais.credentials, SECRET_KEY, algorithms=[ALGORITMO])
        usuario_id = int(dados["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise erro
    linha = db.execute(
        "SELECT id, nome, email, curso FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    if linha is None:
        raise erro
    return dict(linha)
