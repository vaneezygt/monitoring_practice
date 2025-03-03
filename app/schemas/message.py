from pydantic import BaseModel
from datetime import datetime
from .user import User


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    created_at: datetime
    user_id: int
    user: User

    class Config:
        from_attributes = True
