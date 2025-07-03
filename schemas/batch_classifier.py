from pickletools import int4
from pydantic import BaseModel, Json, ValidationError
from typing import Optional, List, Any
from datetime import datetime
from model.transaction import Transaction
from datetime import datetime, date
from typing import Optional


class BatchClassifierRowSchema(BaseModel):
    """ Schema for running classification model on transactions
    """
    date:datetime
    description:str
    value:float 
    user:Optional[str]
    classification:Optional[str]


class BatchClassifierListSchema(BaseModel):
    """ Schema for running classification model on transactions
    """
    transactions:List[BatchClassifierRowSchema]