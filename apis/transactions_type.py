from model.transaction_type import TransactionType
from schemas import ErrorSchema, show_type, TransactionTypeSchema, ListTransactionTypesSchema, DeleteTransactionTypeSchema
from config import app
from config import transaction_type_tag as tag 
from model import Session, User
from logger import logger
from sqlalchemy.exc import IntegrityError
from urllib.parse import unquote


@app.post('/transaction_type', tags=[tag],
          responses={"200": TransactionTypeSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_transaction_type(form: TransactionTypeSchema):
    """
    Add a new transaction type"""
    ttype = TransactionType(
        type=form.type,
       )
    logger.debug(f"Adding transaction type: '{ttype}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(ttype)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Transaction type successfully added: '{ttype}'")
        return show_type(ttype), 200

    except IntegrityError as e:
        error_msg = "Transaction type already exists"
        logger.warning(f"Error adding transaction type '{ttype}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Could not add transaction type"
        logger.warning(f"Error adding transaction type '{ttype}', {error_msg}")
        return {"mesage": error_msg}, 400

@app.get('/transaction_types', tags=[tag],
          responses={"200": ListTransactionTypesSchema, "409": ErrorSchema, "400": ErrorSchema})
def get_all_transaction_types():
    """
    Get all transaction types in the database"""
    logger.debug(f"Listing all transaction types")
   
    session = Session()
    ttypes = session.query(TransactionType).all()

    if not ttypes:
        return {"users": []}, 200
    else:
        logger.debug(f"{len(ttypes)} types found")
        return [show_type(ttype) for ttype in ttypes], 200

@app.delete('/transaction_type', tags=[tag],
            responses={"200": DeleteTransactionTypeSchema, "404": ErrorSchema})
def delete_type(query: TransactionTypeSchema) -> tuple[dict[str, str], int]:
    """Deletes a type given name

    Return a confirmation message
    """
    ttype = unquote(unquote(query.type))
    logger.debug(f"Deleting type {ttype}")
    session = Session()
    count = session.query(TransactionType).filter(TransactionType.type == ttype).delete()
    session.commit()

    if count > 0:
        logger.debug(f"Type #{ttype} deleted")
        return {"mesage": "Type removed successfully", "type": ttype}, 200
    else:
        error_msg = "Type not found"
        logger.warning(f"Error removing type '{ttype}', {error_msg}")
        return {"mesage": error_msg}, 404