from sqlalchemy.exc import IntegrityError

from model import Session, Transaction, User, TransactionType, TransactionCategory
from schemas import TransactionSchema, ErrorSchema, ListTransactionsSchema, show_transaction, DeleteTransactionSchema
from logger import logger
from schemas import *

from apis.users import *
from apis.transactions import *
from config import transaction_tag as transaction_tag

@app.post('/transaction', tags=[transaction_tag],
          responses={"200": TransactionSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_transaction(form: TransactionSchema):
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
        session = Session()
        session.add(transaction)
        session.commit()
        logger.debug(f"Adicionado transação: '{transaction}'")
        return show_transaction(transaction), 200

    except IntegrityError as e:
        error_msg = "Transaction already registred"
        logger.warning(f"Error adding transaction '{transaction}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        error_msg = "Not possible to add transaction"
        logger.warning(f"Error adding transaction '{transaction}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/transactions', tags=[transaction_tag],
         responses={"200": ListTransactionsSchema, "404": ErrorSchema})
def get_transactions():
    """Get all transactions in the database
    """
    logger.debug(f"Coletando produtos ")
    session = Session()
    transactions = session.query(Transaction).all()

    if not transactions:
        return {"transactions": []}, 200
    else:
        logger.debug(f"{len(transactions)} transactions found")
        return [show_transaction(transaction) for transaction in transactions], 200

@app.delete('/transaction', tags=[transaction_tag],
            responses={"200": DeleteTransactionSchema, "404": ErrorSchema})
def delete_transaction(query: SearchTransactionSchema) -> tuple[dict[str, str], int]:
    """Deletes a transaction given id

    Return a confirmation message
    """
    transaction = unquote(unquote(query.id))
    logger.debug(f"Deleting type {transaction}")
    session = Session()
    count = session.query(Transaction).filter(Transaction.id == id).delete()
    session.commit()

    if count > 0:
        logger.debug(f"Transaction #{transaction} deleted")
        return {"mesage": "Type removed successfully", "type": transaction}, 200
    else:
        error_msg = "Transaction not found"
        logger.warning(f"Error removing transaction '{transaction}', {error_msg}")
        return {"mesage": error_msg}, 404