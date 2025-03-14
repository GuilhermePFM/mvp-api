from sqlalchemy import Column, String, Integer
from model import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'User'

    id = Column("pk_user", Integer, primary_key=True)
    first_name = Column(String(140), unique=False)
    last_name = Column(String(140), unique=False)
    email = Column(String(200), unique=True)
    
    transaction = relationship("Transaction",       
                               cascade="all, delete-orphan") 
    
    def __init__(self, first_name:str, last_name:str, email:str):  
        """
        Creates a new Category
        
        Arguments:
            name: Category of a transaction
        """
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
    
    def __str__(self):
           return f'{self.first_name} {self.last_name}'

