from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from model import Base

class Transaction(Base):
    __tablename__ = 'Transaction'

    id = Column("pk_transaction", Integer, primary_key=True)
    value = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("User.pk_user"), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey("TransactionType.pk_transaction_type"), nullable=False)
    transaction_category_id = Column(Integer, ForeignKey("TransactionCategory.pk_transaction_category"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="transaction")
    transaction_type = relationship("TransactionType", back_populates="transaction")
    transaction_category = relationship("TransactionCategory", back_populates="transaction")

    def __init__(self, value: float, user_id: int, transaction_type_id: int, transaction_category_id: int, created_at: DateTime = None, transaction_date: DateTime = None, description: str = ""):   
        """
        Creates a new Transaction
        
        Arguments:
            value: Value of the transaction
            transaction_date: Date of the transaction
            user_id: ID of the user that made the transaction
            transaction_type_id: ID of the transaction type
            transaction_category_id: ID of the transaction category
        """
        self.value = value
        self.user_id = user_id
        self.transaction_type_id = transaction_type_id
        self.transaction_category_id = transaction_category_id
        self.description = description

        if created_at is not None:
            self.created_at = created_at
        else:
            self.created_at = datetime.now()
            
        if transaction_date is not None:
            self.transaction_date = transaction_date
        else:
            self.transaction_date = datetime.now()

    def __str__(self):
        return f"{self.value} - {self.transaction_date} - {self.user} - {self.transaction_type} - {self.transaction_category}"