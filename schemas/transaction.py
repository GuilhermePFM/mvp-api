from sys import int_info
from pydantic import BaseModel
from typing import Optional, List

from datetime import datetime
from model.transaction import Transaction
from schemas.user import show_user
from schemas.transaction_type import show_type
from schemas.transaction_category import show_category

class TransactionSchema(BaseModel):
    """ Define como uma nova transação a ser inserida deve ser representado
    """
    value:float = 100.00
    description:str = "one time purchase"
    transaction_date:datetime = datetime.now()
    user_id:int
    transaction_type_id:int
    transaction_category_id:int

class ListTransactionsSchema(BaseModel):
    """ Define como uma listagem de transações será retornada.
    """
    transactions:List[TransactionSchema]


def show_transaction(transaction: Transaction):
    """ Retorna uma representação das transações seguindo o schema definido em TransactionSchema.
    """
    return {
        'value': transaction.value,
        'transaction_date':transaction.transaction_date,
        'created_at': transaction.created_at,
        'transaction_id': transaction.id,
        'description': transaction.description,
        'user_id': transaction.user_id,
        **show_user(transaction.user),
        **show_type(transaction.transaction_type),
        **show_category(transaction.transaction_category),
    }

class DeleteTransactionSchema(BaseModel):
    type: int
    message:str

class SearchTransactionSchema(BaseModel):
    id: int