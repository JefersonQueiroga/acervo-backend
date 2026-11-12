import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import criar_tabelas
from routers import auth, comentarios, meus_projetos, projetos

load_dotenv()

app = FastAPI(title="Acervo IF")

# Endereços do front-end que podem chamar a API (separados por vírgula no .env)
origens = os.getenv("ORIGENS_CORS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origem.strip() for origem in origens],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

criar_tabelas()

app.include_router(auth.router)
app.include_router(projetos.router)
app.include_router(meus_projetos.router)
app.include_router(comentarios.router)
