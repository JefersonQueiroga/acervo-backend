from sqlite3 import Connection

from fastapi import APIRouter, Depends, HTTPException

from database import get_db
from schemas import UsuarioCreate, UsuarioRead
from seguranca import gerar_hash

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/cadastro", response_model=UsuarioRead, status_code=201)
def cadastrar_usuario(usuario: UsuarioCreate, db: Connection = Depends(get_db)):
    # RN01: o e-mail é único
    existente = db.execute(
        "SELECT * FROM usuarios WHERE email = ?", (usuario.email,)
    ).fetchone()
    if existente is not None:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    # RN03: o banco guarda só o hash, nunca a senha
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha_hash, curso) VALUES (?, ?, ?, ?)",
        (usuario.nome, usuario.email, gerar_hash(usuario.senha), usuario.curso),
    )
    db.commit()

    # O response_model=UsuarioRead garante que o senha_hash não sai na resposta
    linha = db.execute("SELECT * FROM usuarios WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(linha)
