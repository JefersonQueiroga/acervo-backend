from sqlite3 import Connection

from fastapi import APIRouter, Depends

from database import get_db
from schemas import ProjetoRead
from seguranca import get_usuario_atual

router = APIRouter(prefix="/meus-projetos", tags=["projetos"])


@router.get("", response_model=list[ProjetoRead])
def listar_meus_projetos(
    db: Connection = Depends(get_db),
    usuario: dict = Depends(get_usuario_atual),
):
    linhas = db.execute(
        "SELECT * FROM projetos WHERE usuario_id = ?", (usuario["id"],)
    ).fetchall()
    return [dict(linha) for linha in linhas]
