from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from model import Base


class TransactionType(Base):
    __tablename__ = 'TransactionType'

    id = Column("pk_transaction_type", Integer, primary_key=True)
    type = Column(String(140), unique=True)
    transaction = relationship("Transaction") 
    
    def __init__(self, type:str):  
        """
        Creates a new Transaction type
        
        Arguments:
            type: Type of a transaction
        """
        self.type = type
    def __str__(self):
        return f'{self.type}'