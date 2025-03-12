from pydantic import BaseModel
from typing import Optional, List

from datetime import datetime
from model.transaction import Transaction


class TransactionSchema(BaseModel):
    """ Define como uma nova transação a ser inserida deve ser representado
    """
    value:float = 100.00
    transaction_date:datetime = "10/10/2025"
    user:str = "Guilherme Machado"
    transaction_type:str = "Compra"
    category:str = "Casa"


class ListTransactionsSchema(BaseModel):
    """ Define como uma listagem de transações será retornada.
    """
    produtos:List[TransactionSchema]


def show_transaction(transactions: List[Transaction]):
    """ Retorna uma representação das transações seguindo o schema definido em TransactionSchema.
    """
    result = []
    for transaction in transactions:
        result.append({
            'value': transaction.value,
            'transaction_date':transaction.transaction_date,
            'user':transaction.user,
            'transaction_type':transaction.transaction_type,
            'category':transaction.category,
        })

    return {"transactions": result}

class DeleteTransactionSchema(BaseModel):
    type: int
    message:str

class SearchTransactionSchema(BaseModel):
    id: int