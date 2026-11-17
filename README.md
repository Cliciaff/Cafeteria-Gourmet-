# Cafeteria Gourmet

## 1. Apresentação

O Cafeteria Gourmet é um sistema de automação comercial desenvolvido como Projeto Integrador (PIT) do curso de Sistemas de Informação.

O sistema tem como objetivo automatizar a compra de produtos e a realização de pedidos de uma cafeteria gourmet ficticia.

## 2. Objetivo

Desenvolver uma aplicação web que permita organizar as operações básicas de autoatendimento da cafeteria, integrando uma interface de usuário, uma aplicação desenvolvida em Python e um banco de dados relacional MySQL.

## 3. Tecnologias utilizadas

- **Python:** linguagem de programação utilizada no desenvolvimento da aplicação.
- **Flask:** framework utilizado para criação das rotas e gerenciamento das requisições web.
- **MySQL:** sistema gerenciador de banco de dados utilizado para armazenamento das informações.
- **HTML:** estruturação das páginas.
- **CSS:** estilização da interface.
- **JavaScript:** implementação de interações na interface.
- **Visual Studio Code:** ambiente de desenvolvimento.

## 4. Funcionalidades

- Visualização do cardápio.
- Exibição de produtos disponíveis em estoque.
- Adição de produtos ao carrinho.
- Atualização da quantidade de itens no carrinho.
- Remoção de produtos do carrinho.
- Cálculo automático do subtotal e valor total.
- Seleção da forma de pagamento.
- Simulação de pagamento em dinheiro, PIX, cartão de débito, cartão de crédito e voucher.
- Cálculo de troco para pagamentos em dinheiro.
- Registro dos pedidos e respectivos itens no banco de dados.

## 5. Banco de dados

O projeto utiliza o MySQL para armazenar os dados da aplicação.

As principais tabelas são:

- **produtos:** armazena os dados dos produtos, preços e quantidades em estoque.
- **pedidos:** registra os pedidos realizados e suas informações de pagamento.
- **itens_pedido:** armazena os produtos e quantidades associados a cada pedido.

O arquivo `database.sql` contém a estrutura necessária para criação do banco de dados.

## 6. Instalação e execução

### Pré-requisitos

- Python 3 instalado.
- MySQL Server instalado e em execução.
- Git instalado (para clonar o repositório).

### Instalação

1. Clone o repositório:

   `git clone URL_DO_REPOSITORIO`

2. Entre na pasta do projeto:

   `cd cafeteria_gourmet`

3. Crie o ambiente virtual:

   `python -m venv venv`

4. Ative o ambiente virtual no Windows:

   `.\venv\Scripts\Activate.ps1`

5. Instale as dependências:

   `pip install -r requirements.txt`

6. Configure a variável de ambiente `DB_PASSWORD` com a senha do MySQL.

7. Configure a variável `FLASK_SECRET_KEY` com uma chave secreta para a aplicação.

8. Crie o banco de dados e as tabelas utilizando o arquivo `database.sql`.

9. Execute a aplicação:

   `python app.py`

10. Acesse no navegador:

   `http://127.0.0.1:5000`

## 7. Observação sobre pagamentos

As formas de pagamento disponíveis são utilizadas exclusivamente para fins de simulação acadêmica. O sistema não realiza transações financeiras reais nem possui integração com instituições bancárias ou operadoras de cartão.

## 8. Finalidade acadêmica

Projeto desenvolvido para fins acadêmicos, como parte das atividades do curso de Sistemas de Informação. 