import os

from database import ARQUIVO_BANCO, conectar, criar_tabelas

# Começa do zero: apaga o banco antigo e cria as tabelas de novo
if os.path.exists(ARQUIVO_BANCO):
    os.remove(ARQUIVO_BANCO)
criar_tabelas()

produtos = [
    ("Coxinha", 4.50, 30),
    ("Suco de laranja", 3.00, 20),
    ("Bolo de chocolate", 5.00, 12),
]

conexao = conectar()
for produto in produtos:
    conexao.execute(
        "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)", produto
    )
conexao.commit()
conexao.close()

print(f"Banco {ARQUIVO_BANCO} criado com {len(produtos)} produtos.")
