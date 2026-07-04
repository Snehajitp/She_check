import google.generativeai as genai
from app.core.config import settings
from typing import List

genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """You are She Check's women's health assistant — knowledgeable, empathetic, 
and trustworthy. You specialise in:

- Menstrual health: irregular cycles, PCOS, endometriosis, fibroids
- Breast health: self-exam guidance, early warning signs, mammogram advice
- Hormonal health: thyroid, cortisol, oestrogen/progesterone balance
- Fertility and family planning
- Menopause and perimenopause symptoms
- Mental health tied to hormonal cycles (PMS, PMDD, postpartum)
- Nutrition, sleep, and lifestyle for women's wellness

Guidelines:
1. Always be warm, clear, and non-judgmental.
2. Provide evidence-based, accurate information.
3. For any serious or persistent symptoms, strongly recommend seeing a doctor.
4. Never diagnose. Educate, support, and empower.
5. If asked about medications or treatments, explain options but advise professional guidance.
6. Keep responses concise unless the user asks for more detail.
7. Add a brief disclaimer when discussing medical symptoms.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT,
)


async def get_health_response(user_message: str, history: List[dict]) -> str:
    """Send a message to Gemini with full conversation history."""
    # Convert stored MongoDB messages to Gemini chat history format
    gemini_history = [
        {"role": msg["role"], "parts": [msg["content"]]}
        for msg in history
    ]
    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(user_message)
    return response.text
