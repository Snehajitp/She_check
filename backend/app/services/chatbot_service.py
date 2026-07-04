"""
Women's health chatbot powered by Gemini.
Uses the new google-genai SDK (compatible with Python 3.14+).
Maintains per-session conversation history in MongoDB.
"""
import uuid
from datetime import datetime, timezone
from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.chatbot import ChatRequest, ChatResponse
from app.db.mongodb import get_chat_history_collection

SYSTEM_PROMPT = """You are She Check's compassionate women's health assistant.

Your role:
- Answer questions about women's health clearly and empathetically
- Topics: menstrual health, PCOS, endometriosis, fertility, pregnancy, menopause,
  breast health, mental health, nutrition, hormonal health, sexual health
- Suggest practical lifestyle recommendations when appropriate
- Always recommend consulting a doctor for diagnosis or treatment
- Never provide specific medication dosages or replace professional medical advice
- Be warm, non-judgmental, and inclusive

Always end responses that involve symptoms or concerns with a gentle reminder
to consult a healthcare professional."""


def _get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)


async def get_chat_response(payload: ChatRequest, user_id: str) -> ChatResponse:
    col = get_chat_history_collection()

    # Use a valid session_id — ignore "string" placeholder from Swagger
    session_id = payload.session_id
    if not session_id or session_id == "string":
        session_id = str(uuid.uuid4())

    session = await col.find_one({"session_id": session_id, "user_id": user_id})
    history = session["messages"] if session else []

    # Build genai history format (exclude last pair — that's the current turn)
    genai_history = [
        types.Content(
            role=msg["role"],
            parts=[types.Part(text=msg["content"])]
        )
        for msg in history
    ]

    client = _get_client()
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=genai_history + [
            types.Content(
                role="user",
                parts=[types.Part(text=payload.message)]
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=1024,
        ),
    )
    reply = response.text

    # Persist messages
    new_messages = [
        {"role": "user",  "content": payload.message, "timestamp": datetime.now(timezone.utc).isoformat()},
        {"role": "model", "content": reply,            "timestamp": datetime.now(timezone.utc).isoformat()},
    ]

    if session:
        await col.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": {"$each": new_messages}},
                "$set":  {"updated_at": datetime.now(timezone.utc)},
            },
        )
    else:
        await col.insert_one({
            "user_id":    user_id,
            "session_id": session_id,
            "messages":   new_messages,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })

    return ChatResponse(reply=reply, session_id=session_id)