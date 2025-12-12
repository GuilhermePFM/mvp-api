from sqlalchemy import Column, String, Integer, DateTime, Text, Enum
from datetime import datetime
from model import Base
import enum
import uuid


class JobStatus(enum.Enum):
    """Enum for batch job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BatchJob(Base):
    """Model for tracking async batch classification jobs"""
    __tablename__ = 'BatchJob'

    id = Column("pk_batch_job", String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Store transactions as JSON text
    transactions_input = Column(Text, nullable=False)
    transactions_output = Column(Text, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)

    def __init__(self, transactions_input: str, status: JobStatus = JobStatus.PENDING):
        """
        Creates a new BatchJob
        
        Arguments:
            transactions_input: JSON string of input transactions
            status: Initial job status (default: PENDING)
        """
        self.id = str(uuid.uuid4())
        self.transactions_input = transactions_input
        self.status = status
        self.retry_count = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def __repr__(self):
        return f'<BatchJob {self.id} - {self.status.value}>'

