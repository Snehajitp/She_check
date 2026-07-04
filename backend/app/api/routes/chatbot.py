from fastapi import APIRouter, Depends
from app.schemas.chatbot import ChatRequest, ChatResponse
from app.core.security import get_current_user
from app.services.chatbot_service import get_chat_response

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    return await get_chat_response(payload, current_user["user_id"])


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    from app.db.mongodb import get_chat_history_collection
    col = get_chat_history_collection()
    session = await col.find_one({"session_id": session_id, "user_id": current_user["user_id"]})
    if session:
        session["_id"] = str(session["_id"])
    return session or {"messages": []}
