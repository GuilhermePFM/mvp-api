from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from model import Base, User, TransactionType, TransactionCategory
from sqlalchemy import ForeignKey

class Transaction(Base):
    __tablename__ = 'Transaction'

    id = Column("pk_transaction", Integer, primary_key=True)
    value = Column(Float)
    
    transaction_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now())
    
    

    user_id = Column(Integer, ForeignKey("User.pk_user"))
    transaction_type_id = Column(Integer, ForeignKey("TransactionType.pk_transaction_type"))
    transaction_category_id = Column(Integer, ForeignKey("TransactionCategory.pk_transaction_category"))
    
    user = relationship("User")
    transaction_type = relationship("TransactionType")
    transaction_category = relationship("TransactionCategory")

    def __init__(self, value:float, user:User, transaction_type:TransactionType, transaction_category:TransactionCategory, created_at:DateTime = None, transaction_date:DateTime = None):   
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
        self.user = user
        self.transaction_type = transaction_type
        self.category = transaction_category

        if created_at:
            self.created_at = created_at
        if transaction_date:
            self.transaction_date = transaction_date

        def __str__(self):
            return f"{self.value} - {self.transaction_date} - {self.user} - {self.transaction_type} - {self.category}"