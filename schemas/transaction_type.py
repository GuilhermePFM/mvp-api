from pydantic import BaseModel
from typing import List

from model.transaction_type import TransactionType

class TransactionTypeSchema(BaseModel):
    """ Schema for transaction types
    """
    type: str = 'Income'

def show_type(ttype:TransactionType):
     return {
            "transaction_type": ttype.type,
     }

class ListTransactionTypesSchema(BaseModel):
    transaction_types: List[TransactionTypeSchema]