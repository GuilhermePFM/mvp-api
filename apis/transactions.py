from sqlalchemy.exc import IntegrityError

from model import Session, Transaction, User, TransactionType, TransactionCategory
from schemas import TransactionSchema, ErrorSchema, ListTransactionsSchema, show_transaction
from logger import logger
from schemas import *

from apis.users import *
from apis.transactions import *
from config import transaction_tag as transaction_tag

@app.post('/transaction', tags=[transaction_tag],
          responses={"200": TransactionSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_produto(form: TransactionSchema):
    """Adds new transaction to database
    """
    transaction = Transaction(
        value=form.value,
        transaction_date=form.transaction_date,
        user=form.user,
        transaction_type=form.transaction_type,
        category=form.category,
        )
    logger.debug(f"Adicionando transação: '{transaction}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(transaction)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado transação: '{transaction}'")
        return show_transaction(transaction), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Produto de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar produto '{transaction}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar produto '{transaction}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/produtos', tags=[transaction_tag],
         responses={"200": ListTransactionsSchema, "404": ErrorSchema})
def get_produtos():
    """Faz a busca por todos os Produto cadastrados

    Retorna uma representação da listagem de produtos.
    """
    logger.debug(f"Coletando produtos ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    produtos = session.query(Transaction).all()

    if not produtos:
        # se não há produtos cadastrados
        return {"produtos": []}, 200
    else:
        logger.debug(f"%d rodutos econtrados" % len(produtos))
        # retorna a representação de produto
        print(produtos)
        return show_transaction(produtos), 200


# @app.get('/produto', tags=[transaction_tag],
#          responses={"200": TransactionSchema, "404": ErrorSchema})
# def get_produto(query: ProdutoBuscaSchema):
#     """Faz a busca por um Produto a partir do id do produto

#     Retorna uma representação dos produtos e comentários associados.
#     """
#     produto_nome = query.nome
#     logger.debug(f"Coletando dados sobre produto #{produto_nome}")
#     # criando conexão com a base
#     session = Session()
#     # fazendo a busca
#     produto = session.query(Produto).filter(Produto.nome == produto_nome).first()

#     if not produto:
#         # se o produto não foi encontrado
#         error_msg = "Produto não encontrado na base :/"
#         logger.warning(f"Erro ao buscar produto '{produto_nome}', {error_msg}")
#         return {"mesage": error_msg}, 404
#     else:
#         logger.debug(f"Produto econtrado: '{produto.nome}'")
#         # retorna a representação de produto
#         return apresenta_produto(produto), 200


# @app.delete('/produto', tags=[transaction_tag],
#             responses={"200": ProdutoDelSchema, "404": ErrorSchema})
# def del_produto(query: ProdutoBuscaSchema):
#     """Deleta um Produto a partir do nome de produto informado

#     Retorna uma mensagem de confirmação da remoção.
#     """
#     produto_nome = unquote(unquote(query.nome))
#     print(produto_nome)
#     logger.debug(f"Deletando dados sobre produto #{produto_nome}")
#     # criando conexão com a base
#     session = Session()
#     # fazendo a remoção
#     count = session.query(Produto).filter(Produto.nome == produto_nome).delete()
#     session.commit()

#     if count:
#         # retorna a representação da mensagem de confirmação
#         logger.debug(f"Deletado produto #{produto_nome}")
#         return {"mesage": "Produto removido", "id": produto_nome}
#     else:
#         # se o produto não foi encontrado
#         error_msg = "Produto não encontrado na base :/"
#         logger.warning(f"Erro ao deletar produto #'{produto_nome}', {error_msg}")
#         return {"mesage": error_msg}, 404