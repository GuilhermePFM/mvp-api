from urllib.parse import unquote
from sqlalchemy.exc import IntegrityError

from model import Session, Transaction
from schemas import TransactionSchema, ErrorSchema, ListTransactionsSchema, show_transaction, DeleteTransactionSchema
from logger import logger
from schemas import *
from config import transaction_tag as transaction_tag
from config import app


@app.post('/transaction', tags=[transaction_tag],
          responses={"200": TransactionSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_transaction(form: TransactionSchema):
    """
    Adds new transaction to database
    """
    try:
        #FIXME: category id is entering null. probably some error in the model
        transaction = Transaction(
                                    value=form.value,
                                    user_id=form.user_id,  
                                    transaction_type_id=form.transaction_type_id,  
                                    transaction_category_id=form.category_id,  
                                    transaction_date=form.transaction_date,
                                    description=form.description,
                                )
        logger.debug(f"Adicionando transação: '{transaction}'")
        with Session() as session:
            session.add(transaction)
            session.commit()
            logger.debug(f"Added transaction: '{transaction}'")

            # db.refresh(transaction)  # Refresh to get the ID
            return show_transaction(transaction), 200
    
    except IntegrityError as e:
        error_msg = "Transaction already registered"
        logger.warning(f"Error adding transaction '{form}', {error_msg}")
        return {"message": error_msg}, 409
    
    except Exception as e:
        error_msg = "Not possible to add transaction"
        logger.warning(f"Error adding transaction '{form}', {error_msg} - Exception {e}")
        return {"message": error_msg}, 400


@app.post('/transactions', tags=[transaction_tag],
          responses={"200": ListTransactionsSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_transactions_list(body: ListTransactionsSchema):
    """
    Adds new transaction to database
    """
    try:
        #FIXME: category id is entering null. probably some error in the model
        transactions = []
        with Session() as session:
            for transaction_row in body.transactions:
                transaction = Transaction(**transaction_row.model_dump())
                logger.debug(f"Adicionando transação: '{transaction_row}'")
                session.add(transaction)
                session.commit()
                logger.debug(f"Added transaction: '{transaction_row}'")
                transactions.append(transaction)

        # db.refresh(transaction)  # Refresh to get the ID
        return body.model_dump(), 200
    
    except IntegrityError as e:
        error_msg = "Transaction already registered"
        logger.warning(f"Error adding transaction '{body}', {error_msg}")
        return {"message": error_msg}, 409
    
    except Exception as e:
        error_msg = "Not possible to add transaction"
        logger.warning(f"Error adding transaction '{body}', {error_msg} - Exception {e}")
        return {"message": error_msg}, 400


@app.get('/transactions', tags=[transaction_tag],
         responses={"200": ListTransactionsSchema, "404": ErrorSchema})
def get_transactions():
    """Get all transactions in the database
    """
    logger.debug(f"Coletando produtos ")
    with Session() as session:
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
    transaction = query.id
    logger.debug(f"Deleting type {transaction}")
    with Session() as session:
        count = session.query(Transaction).filter(Transaction.id == id).delete()
        session.commit()

        if count > 0:
            logger.debug(f"Transaction #{transaction} deleted")
            return {"mesage": "Type removed successfully", "type": transaction}, 200
        else:
            error_msg = "Transaction not found"
            logger.warning(f"Error removing transaction '{transaction}', {error_msg}")
            return {"mesage": error_msg}, 404