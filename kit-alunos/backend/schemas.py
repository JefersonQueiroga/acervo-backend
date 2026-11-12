from pydantic import BaseModel


# O que o cliente manda para cadastrar ou editar
class ProdutoCreate(BaseModel):
    nome: str
    preco: float
    quantidade: int


# O que a API devolve (com o id)
class ProdutoRead(BaseModel):
    id: int
    nome: str
    preco: float
    quantidade: int


# Coloque aqui os schemas do seu grupo (XCreate e XRead)
