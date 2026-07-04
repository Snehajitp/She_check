from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    disclaimer: str = (
        "This chatbot provides general health information only. "
        "Always consult a qualified medical professional for personal health advice."
    )
