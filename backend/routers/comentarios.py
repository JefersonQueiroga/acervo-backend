from sqlite3 import Connection

from fastapi import APIRouter, Depends, HTTPException

from database import get_db
from routers.projetos import buscar_projeto
from schemas import ComentarioCreate, ComentarioRead
from seguranca import get_usuario_atual

# Sem prefix: as rotas começam ora com /projetos, ora com /comentarios
router = APIRouter(tags=["comentarios"])


def buscar_comentario(id: int, db: Connection) -> dict:
    linha = db.execute("SELECT * FROM comentarios WHERE id = ?", (id,)).fetchone()
    if linha is None:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    return dict(linha)


@router.get("/projetos/{id}/comentarios", response_model=list[ComentarioRead])
def listar_comentarios(id: int, db: Connection = Depends(get_db)):
    buscar_projeto(id, db)  # 404 se o projeto não existe
    linhas = db.execute(
        "SELECT * FROM comentarios WHERE projeto_id = ? ORDER BY id", (id,)
    ).fetchall()
    return [dict(linha) for linha in linhas]


@router.post("/projetos/{id}/comentarios", response_model=ComentarioRead, status_code=201)
def comentar(
    id: int,
    comentario: ComentarioCreate,
    db: Connection = Depends(get_db),
    usuario: dict = Depends(get_usuario_atual),
):
    buscar_projeto(id, db)  # RN11: 404 se o projeto não existe
    # RN09: o autor vem do token; a data o banco preenche sozinho
    cursor = db.execute(
        "INSERT INTO comentarios (texto, projeto_id, usuario_id) VALUES (?, ?, ?)",
        (comentario.texto, id, usuario["id"]),
    )
    db.commit()
    return buscar_comentario(cursor.lastrowid, db)


@router.delete("/comentarios/{id}", status_code=204)
def apagar_comentario(
    id: int,
    db: Connection = Depends(get_db),
    usuario: dict = Depends(get_usuario_atual),
):
    existente = buscar_comentario(id, db)  # 404 se não existe
    # RN08: só o autor apaga
    if existente["usuario_id"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="Você não é o autor deste comentário")
    db.execute("DELETE FROM comentarios WHERE id = ?", (id,))
    db.commit()
