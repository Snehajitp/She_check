from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.deps import get_current_user
from app.db.mongodb import get_db
from app.services.gemini_service import get_health_response
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/chat", tags=["chatbot"])


@router.post("/", response_model=ChatResponse)
async def chat(body: ChatRequest, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["user_id"]

    # Get existing session or create a new one
    if body.session_id:
        session = await db.chat_sessions.find_one(
            {"_id": ObjectId(body.session_id), "user_id": user_id}
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = {
            "user_id": user_id,
            "title": body.message[:50],
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.chat_sessions.insert_one(session)
        session["_id"] = result.inserted_id

    history = session.get("messages", [])
    reply = await get_health_response(body.message, history)

    # Persist both turns to MongoDB
    now = datetime.utcnow()
    new_msgs = [
        {"role": "user",  "content": body.message, "timestamp": now},
        {"role": "model", "content": reply,         "timestamp": now},
    ]
    await db.chat_sessions.update_one(
        {"_id": session["_id"]},
        {
            "$push": {"messages": {"$each": new_msgs}},
            "$set":  {"updated_at": now},
        },
    )

    return ChatResponse(session_id=str(session["_id"]), reply=reply)


@router.get("/sessions")
async def list_sessions(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = (
        db.chat_sessions
        .find({"user_id": current_user["user_id"]}, {"messages": 0})
        .sort("updated_at", -1)
        .limit(20)
    )
    sessions = []
    async for s in cursor:
        s["_id"] = str(s["_id"])
        sessions.append(s)
    return sessions


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    session = await db.chat_sessions.find_one(
        {"_id": ObjectId(session_id), "user_id": current_user["user_id"]}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session["_id"] = str(session["_id"])
    return session
