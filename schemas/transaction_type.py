from pydantic import BaseModel
from typing import List

from model.transaction_type import TransactionType

class TransactionTypeSchema(BaseModel):
    """ Schema for transaction types
    """
    type: str = 'Income'
    id: int = 1

def show_type(ttype:TransactionType):
     return {
            "transaction_type": ttype.type,
            "id": ttype.id,
     }

class ListTransactionTypesSchema(BaseModel):
    transaction_types: List[TransactionTypeSchema]

class DeleteTransactionTypeSchema(BaseModel):
    type: int
    message:str
