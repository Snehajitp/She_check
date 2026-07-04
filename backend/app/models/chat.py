from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "model"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatSessionDocument(BaseModel):
    user_id: str
    session_id: str
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
