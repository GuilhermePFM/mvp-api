from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from schemas.batch_classifier import BatchClassifierRowSchema


class BatchClassifyAsyncRequest(BaseModel):
    """Schema for async batch classification request"""
    transactions: List[BatchClassifierRowSchema]


class BatchClassifyAsyncResponse(BaseModel):
    """Schema for async batch classification response"""
    jobId: str


class BatchJobStatusResponse(BaseModel):
    """Schema for batch job status response"""
    status: str
    transactions: Optional[List[BatchClassifierRowSchema]] = None
    message: Optional[str] = None

