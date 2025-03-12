from sqlalchemy import Column, String, Integer
from model import Base
from sqlalchemy.orm import relationship

class TransactionCategory(Base):
    __tablename__ = 'TransactionCategory'

    id = Column("pk_transaction_category", Integer, primary_key=True)
    name = Column(String(140), unique=True)
    transaction = relationship("Transaction") 
    
    def __init__(self, name:str) -> None:  
        """
        Creates a new Category
        
        Arguments:
            name: Category of a transaction
        """
        self.name = name
    def __str__(self) -> str:
           return f'{self.name}'    