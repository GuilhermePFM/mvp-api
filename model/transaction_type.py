from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from model import Base, User, TransactionType, TransactionCategory


class TransactionType(Base):
    __tablename__ = 'TransactionType'

    id = Column("pk_transaction_type", Integer, primary_key=True)
    type = Column(String(140), unique=True)
    
    def __init__(self, type:str):  
        """
        Creates a new Transaction type
        
        Arguments:
            type: Type of a transaction
        """
        self.type = type