# backend/routers/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agent.core import create_vgc_agent

router = APIRouter(tags=["AI Coach"])

# Boot up a global instance of your stateful chat session
# This keeps the memory active while the server is running!
vgc_coach = create_vgc_agent()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat_with_ai(request: ChatRequest):
    try:
        response = vgc_coach.send_message(request.message)
        return {"response": response.text}
    except Exception as e:
        # Convert the error to a lowercase string so we can inspect it
        error_msg = str(e).lower()
        
        # Check if the error is complaining about rate limits or quotas
        if "429" in error_msg or "exhausted" in error_msg or "quota" in error_msg:
            return {"response": "⚠️ **System Alert:** We have hit our daily Gemini API quota limit! The free tier will reset tomorrow."}
        
        # If it's a completely different error (like a database crash), throw the normal 500
        raise HTTPException(status_code=500, detail=str(e))