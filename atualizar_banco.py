
import os
import mysql.connector

senha = os.getenv("DB_PASSWORD")

if not senha:
    raise RuntimeError(
        "A variável de ambiente DB_PASSWORD não foi configurada."
    )

conexao = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password=senha,
    database="cafeteria_gourmet"
)

cursor = conexao.cursor()

print("Banco conectado:", conexao.database)

cursor.execute("SHOW COLUMNS FROM produtos")
colunas = cursor.fetchall()

print("\nColunas atuais da tabela produtos:")
for coluna in colunas:
    print(coluna[0])

if not any(coluna[0] == "unidade_medida" for coluna in colunas)
    cursor.execute("""
        ALTER TABLE produtos
        ADD COLUMN unidade_medida VARCHAR(10) NOT NULL DEFAULT 'UN'
    """)
    conexao.commit()
    print("\nColuna criada com sucesso!")
else:
    print("\nA coluna unidade_medida já existe!")

cursor.close()
conexao.close()
