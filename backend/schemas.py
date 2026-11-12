from typing import Literal

from pydantic import BaseModel, Field


# O que o cliente manda para cadastrar ou editar um projeto
class ProjetoCreate(BaseModel):
    titulo: str
    resumo: str
    tipo: Literal["TCC", "PI"]
    curso: Literal["Informática", "ADS"]
    ano: int = Field(ge=2000, le=2100)
    autores: str
    orientador: str
    palavras_chave: str = ""
    link_repositorio: str | None = None
    link_demo: str | None = None
    aberto_para_continuar: bool = False


# O que a API devolve (com o id)
class ProjetoRead(BaseModel):
    id: int
    titulo: str
    resumo: str
    tipo: str
    curso: str
    ano: int
    autores: str
    orientador: str
    palavras_chave: str
    link_repositorio: str | None
    link_demo: str | None
    aberto_para_continuar: bool  # no banco é 0 ou 1; o Pydantic converte
    usuario_id: int  # o dono do projeto (vem do token, nunca do corpo)


# O que o aluno manda para criar a conta
class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str = Field(min_length=6)
    curso: Literal["Informática", "ADS"]


# O que a API devolve: nunca a senha nem o hash
class UsuarioRead(BaseModel):
    id: int
    nome: str
    email: str
    curso: str


# Login em JSON
class LoginDados(BaseModel):
    email: str
    senha: str


# O que o login devolve
class Token(BaseModel):
    access_token: str
    token_type: str
