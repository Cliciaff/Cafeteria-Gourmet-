
import os
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import mysql.connector
from mysql.connector import Error
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

app = Flask(__name__)

# Chave de segurança da sessão
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "chave-local-cafeteria-gourmet-2026"
)

# Configuração do banco de dados
def conectar_banco():
    senha = os.getenv("DB_PASSWORD")

    if not senha:
        raise RuntimeError(
            "A variável de ambiente DB_PASSWORD não foi configurada."
        )

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=senha,
        database=os.getenv("DB_NAME", "cafeteria_gourmet")
    )


# Função para converter valores monetários
def converter_decimal(valor):
    return Decimal(str(valor)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


# Função para obter os itens do carrinho

def obter_itens_carrinho():
    carrinho = session.get("carrinho", {})

    # Descarta dados antigos ou incompatíveis da sessão
    if not isinstance(carrinho, dict) or any(
        not isinstance(item, dict)
        for item in carrinho.values()
    ):
        session.pop("carrinho", None)
        return []

    return list(carrinho.values())


# --------------------------------------------------
# PÁGINA INICIAL
# --------------------------------------------------

@app.route("/")
def inicio():
    return render_template("inicio.html")


# --------------------------------------------------
# CARDÁPIO
# --------------------------------------------------

@app.route("/cardapio")
def cardapio():
    conexao = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        pesquisa = request.args.get(
            "q",
            request.args.get("busca", "")
        ).strip()

        sql = """
            SELECT
                id,
                nome,
                descricao,
                preco,
                quantidade_estoque,
                unidade_medida
            FROM produtos
            WHERE quantidade_estoque > 0
        """

        parametros = []

        if pesquisa:
            sql += " AND nome LIKE %s"
            parametros.append(f"%{pesquisa}%")

        sql += " ORDER BY nome"

        cursor.execute(sql, parametros)
        produtos = cursor.fetchall()

        cursor.close()

        return render_template(
            "cardapio.html",
            produtos=produtos,
            pesquisa=pesquisa
        )

    except (Error, RuntimeError) as erro:
        print(f"Erro ao consultar o banco de dados: {erro}")

        return render_template(
            "cardapio.html",
            produtos=[],
            pesquisa="",
            erro="Não foi possível consultar os produtos."
        )

    finally:
        if conexao and conexao.is_connected():
            conexao.close()


# --------------------------------------------------
# ADICIONAR PRODUTO AO CARRINHO
# --------------------------------------------------

@app.route("/adicionar/<int:produto_id>", methods=["POST"])
def adicionar(produto_id):
    conexao = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                nome,
                descricao,
                preco,
                quantidade_estoque,
                unidade_medida
            FROM produtos
            WHERE id = %s
            """,
            (produto_id,)
        )

        produto = cursor.fetchone()

        if not produto:
            flash("Produto não encontrado.")
            return redirect(url_for("cardapio"))

        if produto["quantidade_estoque"] <= 0:
            flash("Produto sem estoque disponível.")
            return redirect(url_for("cardapio"))

        carrinho = session.get("carrinho", {})
        
        chave = str(produto_id)

        if chave in carrinho and not isinstance(carrinho[chave], dict):
            carrinho.pop(chave)

        quantidade_atual = (
            int(carrinho[chave]["quantidade"])
            if chave in carrinho else 0
        )

        if quantidade_atual + 1 > produto["quantidade_estoque"]:
            flash("Quantidade superior ao estoque disponível.")
            return redirect(url_for("cardapio"))

        carrinho[chave] = {
            "id": produto["id"],
            "nome": produto["nome"],
            "descricao": produto["descricao"],
            "preco": str(produto["preco"]),
            "quantidade": quantidade_atual + 1,
            "estoque": produto["quantidade_estoque"],
            "unidade_medida": produto["unidade_medida"]
        }

        session["carrinho"] = carrinho
        session.modified = True

        cursor.close()

        flash("Produto adicionado ao carrinho!")

        return redirect(url_for("cardapio"))

    except (Error, RuntimeError) as erro:
        print(f"Erro ao adicionar produto: {erro}")
        flash("Não foi possível adicionar o produto.")

        return redirect(url_for("cardapio"))

    finally:
        if conexao and conexao.is_connected():
            conexao.close()

# --------------------------------------------------
# VISUALIZAR CARRINHO
# --------------------------------------------------


# --------------------------------------------------
# CÁLCULO DO TOTAL DO CARRINHO
# --------------------------------------------------

def calcular_total_carrinho():
    total = Decimal("0.00")

    for item in obter_itens_carrinho():
        preco = Decimal(str(item["preco"]))
        quantidade = int(item["quantidade"])
        total += preco * quantidade

    return converter_decimal(total)

# --------------------------------------------------
# VISUALIZAR CARRINHO
# --------------------------------------------------

@app.route("/carrinho")
def carrinho():
    itens = obter_itens_carrinho()
    total = calcular_total_carrinho()

    return render_template(
        "carrinho.html",
        carrinho=itens,
        itens=itens,
        total=total
    )

# --------------------------------------------------
# ATUALIZAR QUANTIDADES DO CARRINHO
# --------------------------------------------------

@app.route("/atualizar_carrinho", methods=["POST"])
def atualizar_carrinho():
    conexao = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        carrinho = session.get("carrinho", {})

        for chave, item in list(carrinho.items()):

            quantidade_informada = request.form.get(
                f"quantidade_{chave}",
                request.form.get("quantidade")
            )

            if quantidade_informada is None:
                continue

            try:
                quantidade = int(quantidade_informada)
            except ValueError:
                continue

            if quantidade <= 0:
                carrinho.pop(chave)
                continue

            cursor.execute(
                """
                SELECT quantidade_estoque
                FROM produtos
                WHERE id = %s
                """,
                (int(chave),)
            )

            produto = cursor.fetchone()

            if not produto:
                carrinho.pop(chave)
                continue

            if quantidade > produto["quantidade_estoque"]:
                quantidade = produto["quantidade_estoque"]

            if quantidade <= 0:
                carrinho.pop(chave)
                continue

            item["quantidade"] = quantidade
            item["estoque"] = produto["quantidade_estoque"]

        session["carrinho"] = carrinho
        session.modified = True

        cursor.close()

        flash("Carrinho atualizado!")

    except (Error, RuntimeError) as erro:
        print(f"Erro ao atualizar carrinho: {erro}")
        flash("Não foi possível atualizar o carrinho.")

    finally:
        if conexao and conexao.is_connected():
            conexao.close()

    return redirect(url_for("carrinho"))


# --------------------------------------------------
# REMOVER PRODUTO DO CARRINHO
# --------------------------------------------------

@app.route("/remover/<int:produto_id>", methods=["POST"])
def remover(produto_id):
    carrinho = session.get("carrinho", {})

    carrinho.pop(str(produto_id), None)

    session["carrinho"] = carrinho
    session.modified = True

    flash("Produto removido do carrinho.")

    return redirect(url_for("carrinho"))


# --------------------------------------------------
# CADASTRO DE PRODUTOS
# --------------------------------------------------

@app.route("/admin", methods=["GET", "POST"])
def admin():
    conexao = None

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        preco_informado = request.form.get("preco", "")
        estoque_informado = request.form.get(
            "quantidade_estoque",
            ""
        )
        unidade = request.form.get(
            "unidade_medida",
            "UN"
        ).strip().upper()

        try:
            preco = converter_decimal(preco_informado)
            estoque = int(estoque_informado)

            if not nome:
                raise ValueError("Informe o nome do produto.")

            if preco <= 0:
                raise ValueError("O preço deve ser maior que zero.")

            if estoque < 0:
                raise ValueError("O estoque não pode ser negativo.")

            if len(unidade) > 10 or not unidade:
                raise ValueError("Unidade de medida inválida.")

            conexao = conectar_banco()
            cursor = conexao.cursor()

            cursor.execute(
                """
                INSERT INTO produtos
                (nome, descricao, preco, quantidade_estoque, unidade_medida)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nome, descricao, preco, estoque, unidade)
            )

            conexao.commit()
            cursor.close()

            flash("Produto cadastrado com sucesso!")

        except (ValueError, InvalidOperation, Error, RuntimeError) as erro:
            if conexao:
                conexao.rollback()

            print(f"Erro ao cadastrar produto: {erro}")
            flash(str(erro))

        finally:
            if conexao and conexao.is_connected():
                conexao.close()

        return redirect(url_for("admin"))

    produtos = []
    conexao = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                nome,
                descricao,
                preco,
                quantidade_estoque,
                unidade_medida
            FROM produtos
            ORDER BY nome
            """
        )

        produtos = cursor.fetchall()
        cursor.close()

    except (Error, RuntimeError) as erro:
        print(f"Erro ao listar produtos: {erro}")
        flash("Não foi possível carregar os produtos.")

    finally:
        if conexao and conexao.is_connected():
            conexao.close()

    return render_template(
        "cadastro.html",
        produtos=produtos
    )


# --------------------------------------------------
# PAGAMENTO
# --------------------------------------------------

@app.route("/pagamento", methods=["GET", "POST"])
def pagamento():

    itens = obter_itens_carrinho()

    if not itens:
        flash("Seu carrinho está vazio.")
        return redirect(url_for("cardapio"))

    total = calcular_total_carrinho()

    if request.method == "GET":
        return render_template(
            "pagamento.html",
            itens=itens,
            total=total
        )

    forma_pagamento = request.form.get(
        "forma_pagamento",
        ""
    ).strip().upper()

    formas_permitidas = [
        "PIX",
        "DINHEIRO",
        "DEBITO",
        "CREDITO",
        "VOUCHER"
    ]

    if forma_pagamento not in formas_permitidas:
        flash("Selecione uma forma de pagamento válida.")
        return redirect(url_for("pagamento"))

    if forma_pagamento == "DINHEIRO":

        try:
            valor_recebido = converter_decimal(
                request.form.get("valor_recebido", "0")
            )

        except (InvalidOperation, ValueError):
            flash("Informe um valor recebido válido.")
            return redirect(url_for("pagamento"))

        if valor_recebido < total:
            flash("O valor recebido é inferior ao total do pedido.")
            return redirect(url_for("pagamento"))

        troco = converter_decimal(valor_recebido - total)

    else:
        valor_recebido = total
        troco = Decimal("0.00")

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        conexao.start_transaction()

        cursor = conexao.cursor(dictionary=True)

        # Conferir novamente o estoque antes de registrar o pedido
        itens_confirmados = []

        for item in itens:

            cursor.execute(
                """
                SELECT
                    id,
                    nome,
                    preco,
                    quantidade_estoque
                FROM produtos
                WHERE id = %s
                FOR UPDATE
                """,
                (item["id"],)
            )

            produto = cursor.fetchone()

            if not produto:
                raise ValueError(
                    f"O produto {item['nome']} não foi encontrado."
                )

            quantidade = int(item["quantidade"])

            if produto["quantidade_estoque"] < quantidade:
                raise ValueError(
                    f"Estoque insuficiente para {produto['nome']}."
                )

            preco = converter_decimal(produto["preco"])
            subtotal = converter_decimal(preco * quantidade)

            itens_confirmados.append({
                "id": produto["id"],
                "nome": produto["nome"],
                "quantidade": quantidade,
                "preco": preco,
                "subtotal": subtotal
            })

        # Recalcular o total usando os preços atuais do banco
        total = converter_decimal(
            sum(
                (item["subtotal"] for item in itens_confirmados),
                Decimal("0.00")
            )
        )

        if forma_pagamento == "DINHEIRO":
            if valor_recebido < total:
                raise ValueError(
                    "O valor recebido não cobre o total atualizado."
                )

            troco = converter_decimal(valor_recebido - total)

        else:
            valor_recebido = total
            troco = Decimal("0.00")

        # Registrar o pedido
        cursor.execute(
            """
            INSERT INTO pedidos
            (
                forma_pagamento,
                total,
                valor_recebido,
                troco,
                status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                forma_pagamento,
                total,
                valor_recebido,
                troco,
                "PAGO"
            )
        )

        pedido_id = cursor.lastrowid

        # Registrar os produtos e baixar o estoque
        for item in itens_confirmados:

            cursor.execute(
                """
                INSERT INTO itens_pedido
                (
                    pedido_id,
                    produto_id,
                    nome_produto,
                    quantidade,
                    preco_unitario,
                    subtotal
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    pedido_id,
                    item["id"],
                    item["nome"],
                    item["quantidade"],
                    item["preco"],
                    item["subtotal"]
                )
            )

            cursor.execute(
                """
                UPDATE produtos
                SET quantidade_estoque = quantidade_estoque - %s
                WHERE id = %s
                  AND quantidade_estoque >= %s
                """,
                (
                    item["quantidade"],
                    item["id"],
                    item["quantidade"]
                )
            )

            if cursor.rowcount != 1:
                raise ValueError(
                    f"Não foi possível atualizar o estoque de {item['nome']}."
                )

        # Confirmar todas as operações
        conexao.commit()

        # Limpar carrinho somente após a confirmação
        session.pop("carrinho", None)

        return render_template(
            "pedido_confirmado.html",
            pedido_id=pedido_id,
            total=total,
            forma_pagamento=forma_pagamento,
            troco=troco
        )

    except (Error, ValueError, RuntimeError) as erro:

        if conexao:
            conexao.rollback()

        print(f"Erro ao processar pagamento: {erro}")

        flash(str(erro))

        return redirect(url_for("pagamento"))

    finally:
        if cursor:
            cursor.close()

        if conexao and conexao.is_connected():
            conexao.close()


# --------------------------------------------------
# EXECUÇÃO DA APLICAÇÃO
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )