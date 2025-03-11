from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from model import Base, User, TransactionType, TransactionCategory


class User(Base):
    __tablename__ = 'User'

    id = Column("pk_user", Integer, primary_key=True)
    first_name = Column(String(140), unique=False)
    last_name = Column(String(140), unique=False)
    email = Column(String(200), unique=True)
    
    def __init__(self, first_name:str, last_name:str, email:str):  
        """
        Creates a new Category
        
        Arguments:
            name: Category of a transaction
        """
        self.first_name = first_name
        self.last_name = last_name
        self.email = email