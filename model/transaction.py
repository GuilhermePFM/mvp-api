from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from model import Base, User, TransactionType, TransactionCategory


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column("pk_transaction", Integer, primary_key=True)
    value = Column(Float)
    
    transaction_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now())
    
    user = relationship("User") 
    transaction_type = relationship("TransactionType") 
    transaction_category = relationship("TransactionCategory") 
    
    def __init__(self, value:float, transaction_date:DateTime, user:User, transaction_type:TransactionType, transaction_category:TransactionCategory, created_at:DateTime = None):  
        """
        Creates a new Transaction
        
        Arguments:
            value: Value of the transaction
            transaction_date: Date of the transaction
            user: User that made the transaction
            transaction_type: Type of the transaction
            transaction_category: Category of the transaction
        """
        self.value = value
        self.transaction_date = transaction_date
        self.user = user
        self.transaction_type = transaction_type
        self.category = transaction_category

        if created_at:
            self.created_at = created_at