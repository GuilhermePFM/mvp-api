from pydantic import BaseModel
from typing import Optional, List

from datetime import datetime
from model.transaction import Transaction


class TransactionSchema(BaseModel):
    """ Define como uma nova transação a ser inserida deve ser representado
    """
    value:float = 100.00
    transaction_date:datetime = None
    user_email:str = "john.smith@gmail.com"
    transaction_type:str = "Expense"
    category:str = "House"


class ListTransactionsSchema(BaseModel):
    """ Define como uma listagem de transações será retornada.
    """
    produtos:List[TransactionSchema]


def show_transaction(transaction: Transaction):
    """ Retorna uma representação das transações seguindo o schema definido em TransactionSchema.
    """
    return {
        'value': transaction.value,
        'transaction_date':transaction.transaction_date,
        'user_id':transaction.user_id,
        'transaction_type_id':transaction.transaction_type_id,
        'transaction_category_id':transaction.transaction_category_id,
        'created_at': transaction.created_at,
        'id': transaction.id
    }

class DeleteTransactionSchema(BaseModel):
    type: int
    message:str

class SearchTransactionSchema(BaseModel):
    id: int