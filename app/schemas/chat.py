from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: str = Field(..., description="Unique identifier for the chat session", min_length=1)
    message: str = Field(..., description="User message to send to the chatbot", min_length=1)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "user123_session",
                "message": "Hello, how are you today?"
            }
        }
    }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Chatbot's response to the user message")
    session_id: str = Field(..., description="Session identifier for tracking conversation")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
                "session_id": "user123_session"
            }
        }
    }