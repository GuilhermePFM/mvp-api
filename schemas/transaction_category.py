from pydantic import BaseModel
from typing import List

from model.transaction_category import TransactionCategory

class TransactionCategorySchema(BaseModel):
    """ Schema for transaction category
    """
    name: str = 'Home'
    id: int = 1

def show_category(category:TransactionCategory):
     return {
            "transaction_category": category.name,
            "id": category.id,
     }

class ListTransactionCategoriesSchema(BaseModel):
    transaction_categories: List[TransactionCategorySchema]

class DeleteTransactionCategorySchema(BaseModel):
    category: int
    message:str
