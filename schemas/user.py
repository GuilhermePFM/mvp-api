from pickletools import int4
from pydantic import BaseModel
from typing import Optional, List, Any

from datetime import datetime
from model.transaction import Transaction


class UserSchema(BaseModel):
    """ Schema for users
    """
    first_name: str = 'John'
    last_name: str = 'Smith'
    email: str = 'john.smith@gmail.com'

def show_user(user) -> dict[str, Any]:
     return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "id": user.id
     }

class SearchUserSchema(BaseModel):
    email: str = 'john.smith@gmail.com'

class ListUserSchema(BaseModel):
    users: List[UserSchema]


class DeleteUserSchema(BaseModel):
    id: int
    message:str


