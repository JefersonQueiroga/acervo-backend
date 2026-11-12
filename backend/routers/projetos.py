from sqlite3 import Connection

from fastapi import APIRouter, Depends, HTTPException

from database import get_db
from schemas import ProjetoCreate, ProjetoRead
from seguranca import get_usuario_atual

router = APIRouter(prefix="/projetos", tags=["projetos"])


def buscar_projeto(id: int, db: Connection) -> dict:
    linha = db.execute("SELECT * FROM projetos WHERE id = ?", (id,)).fetchone()
    if linha is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return dict(linha)


@router.get("", response_model=list[ProjetoRead])
def listar_projetos(
    tipo: str | None = None,
    curso: str | None = None,
    ano: int | None = None,
    busca: str | None = None,
    continuar: bool = False,
    db: Connection = Depends(get_db),
):
    linhas = db.execute("SELECT * FROM projetos ORDER BY ano DESC, id DESC").fetchall()
    projetos = [dict(linha) for linha in linhas]

    # Cada filtro só é aplicado se veio na URL
    if tipo:
        projetos = [p for p in projetos if p["tipo"] == tipo]
    if curso:
        projetos = [p for p in projetos if p["curso"] == curso]
    if ano:
        projetos = [p for p in projetos if p["ano"] == ano]
    if busca:
        texto = busca.lower()
        projetos = [
            p for p in projetos
            if texto in p["titulo"].lower()
            or texto in p["resumo"].lower()
            or texto in p["palavras_chave"].lower()
        ]
    if continuar:
        projetos = [p for p in projetos if p["aberto_para_continuar"]]

    return projetos


@router.get("/{id}", response_model=ProjetoRead)
def detalhar_projeto(id: int, db: Connection = Depends(get_db)):
    return buscar_projeto(id, db)


def conferir_dono(projeto: dict, usuario: dict):
    # RN07: só o dono edita ou exclui
    if projeto["usuario_id"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="Você não é o dono deste projeto")


@router.post("", response_model=ProjetoRead, status_code=201)
def cadastrar_projeto(
    projeto: ProjetoCreate,
    db: Connection = Depends(get_db),
    usuario: dict = Depends(get_usuario_atual),
):
    # RN09: o dono vem do token (usuario["id"]), nunca do corpo
    cursor = db.execute(
        """INSERT INTO projetos (titulo, resumo, tipo, curso, ano, autores, orientador,
               palavras_chave, link_repositorio, link_demo, aberto_para_continuar,
               usuario_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            projeto.titulo,
            projeto.resumo,
            projeto.tipo,
            projeto.curso,
            projeto.ano,
            projeto.autores,
            projeto.orientador,
            projeto.palavras_chave,
            projeto.link_repositorio,
            projeto.link_demo,
            projeto.aberto_para_continuar,
            usuario["id"],
        ),
    )
    db.commit()
    return buscar_projeto(cursor.lastrowid, db)


@router.put("/{id}", response_model=ProjetoRead)
def editar_projeto(
    id: int,
    projeto: ProjetoCreate,
    db: Connection = Depends(get_db),
    usuario: dict = Depends(get_usuario_atual),
):
    existente = buscar_projeto(id, db)  # 404 se não existe
    conferir_dono(existente, usuario)  # 403 se não é o dono
    db.execute(
        """UPDATE projetos SET titulo = ?, resumo = ?, tipo = ?, curso = ?, ano = ?,
               autores = ?, orientador = ?, palavras_chave = ?, link_repositorio = ?,
               link_demo = ?, aberto_para_continuar = ?
           WHERE id = ?""",
        (
            projeto.titulo,
            projeto.resumo,
            projeto.tipo,
            projeto.curso,
            projeto.ano,
            projeto.autores,
            projeto.orientador,
            projeto.palavras_chave,
            projeto.link_repositorio,
            projeto.link_demo,
            projeto.aberto_para_continuar,
            id,
        ),
    )
    db.commit()
    return buscar_projeto(id, db)


@router.delete("/{id}", status_code=204)
def excluir_projeto(
    id: int,
    db: Connection = Depends(get_db),
    usuario: dict = Depends(get_usuario_atual),
):
    existente = buscar_projeto(id, db)  # 404 se não existe
    conferir_dono(existente, usuario)  # 403 se não é o dono
    # RN10: apaga antes os comentários, senão o REFERENCES impede o DELETE
    db.execute("DELETE FROM comentarios WHERE projeto_id = ?", (id,))
    db.execute("DELETE FROM projetos WHERE id = ?", (id,))
    db.commit()
