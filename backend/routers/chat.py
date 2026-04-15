# backend/routers/chat.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from agent.core import create_vgc_agent
from slowapi import Limiter
from slowapi.util import get_remote_address
from google.genai.errors import APIError
import traceback

router = APIRouter(tags=["AI Coach"])
limiter = Limiter(key_func=get_remote_address)

# Boot up a global instance of your stateful chat session
# This keeps the memory active while the server is running!
vgc_coach = create_vgc_agent()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
@limiter.limit("5/minute")
def chat_with_ai(request: Request, payload: ChatRequest):
    try:
        response = vgc_coach.send_message(payload.message)
        return {"response": response.text}
    except APIError as e:
        traceback.print_exc()
        error_code = e.code if hasattr(e, 'code') else 503
        
        if error_code == 429:
            bot_reply = "**System Alert:** We have hit our daily Gemini API quota limit! The free tier will reset tomorrow."
        elif error_code == 503:
            bot_reply = "**System Alert:** The AI is currently experiencing high demand. Please wait a moment and try again."
        else:
            bot_reply = "**System Alert:** The AI encountered an unexpected connection error."
        
        return {"response": bot_reply}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An internal server error occurred.")