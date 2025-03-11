from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from model import Base, User, TransactionType, TransactionCategory


class TransactionCategory(Base):
    __tablename__ = 'TransactionCategory'

    id = Column("pk_transaction_category", Integer, primary_key=True)
    name = Column(String(140), unique=True)
    
    def __init__(self, name:str):  
        """
        Creates a new Category
        
        Arguments:
            name: Category of a transaction
        """
        self.name = name