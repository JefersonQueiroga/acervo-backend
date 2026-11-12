from sqlite3 import Connection

from fastapi import APIRouter, Depends, HTTPException

from database import get_db
from schemas import ProdutoCreate, ProdutoRead

router = APIRouter(prefix="/produtos", tags=["produtos"])


def buscar_produto(id: int, db: Connection) -> dict:
    linha = db.execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
    if linha is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return dict(linha)


@router.get("", response_model=list[ProdutoRead])
def listar_produtos(db: Connection = Depends(get_db)):
    linhas = db.execute("SELECT * FROM produtos").fetchall()
    return [dict(linha) for linha in linhas]


@router.get("/{id}", response_model=ProdutoRead)
def detalhar_produto(id: int, db: Connection = Depends(get_db)):
    return buscar_produto(id, db)


@router.post("", response_model=ProdutoRead, status_code=201)
def cadastrar_produto(produto: ProdutoCreate, db: Connection = Depends(get_db)):
    cursor = db.execute(
        "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
        (produto.nome, produto.preco, produto.quantidade),
    )
    db.commit()
    return buscar_produto(cursor.lastrowid, db)


@router.put("/{id}", response_model=ProdutoRead)
def editar_produto(id: int, produto: ProdutoCreate, db: Connection = Depends(get_db)):
    buscar_produto(id, db)  # 404 se não existe
    db.execute(
        "UPDATE produtos SET nome = ?, preco = ?, quantidade = ? WHERE id = ?",
        (produto.nome, produto.preco, produto.quantidade, id),
    )
    db.commit()
    return buscar_produto(id, db)


@router.delete("/{id}", status_code=204)
def excluir_produto(id: int, db: Connection = Depends(get_db)):
    buscar_produto(id, db)  # 404 se não existe
    db.execute("DELETE FROM produtos WHERE id = ?", (id,))
    db.commit()
