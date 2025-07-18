from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: str = Field(
        ..., 
        description="Unique identifier for the chat session. Used to maintain conversation history.",
        min_length=1,
        max_length=100,
        pattern="^[a-zA-Z0-9_-]+$",
        examples=["user123_session", "session_abc123", "chat_2024_01"]
    )
    message: str = Field(
        ..., 
        description="User message to send to the chatbot",
        min_length=1,
        max_length=4000,
        examples=[
            "Hello, how are you today?",
            "Can you explain quantum computing?",
            "What's the weather like?",
            "Help me write a Python function"
        ]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "user123_session",
                "message": "Hello! Can you help me understand machine learning?"
            }
        }
    }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(
        ..., 
        description="Chatbot's response to the user message",
        examples=[
            "Hello! I'm doing well, thank you for asking. How can I help you today?",
            "Machine learning is a subset of artificial intelligence...",
            "I'd be happy to help you with that Python function!"
        ]
    )
    session_id: str = Field(
        ..., 
        description="Session identifier for tracking conversation",
        examples=["user123_session", "session_abc123"]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "response": "Hello! I'm an AI assistant powered by ChatGroq. I'm doing well and ready to help you with any questions or tasks you have. How can I assist you today?",
                "session_id": "user123_session"
            }
        }
    }


class SessionClearResponse(BaseModel):
    """Response model for session clear endpoint."""
    message: str = Field(
        ...,
        description="Status message indicating the result of the session clear operation",
        examples=[
            "Session user123_session cleared successfully",
            "Session user123_session not found"
        ]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Session user123_session cleared successfully"
            }
        }
    }


class MemoryStats(BaseModel):
    """Model for memory cache statistics."""
    current_size: int = Field(
        ...,
        description="Current number of active sessions in memory",
        ge=0,
        examples=[42, 150, 0]
    )
    max_size: int = Field(
        ...,
        description="Maximum number of sessions that can be stored in memory",
        gt=0,
        examples=[1000, 5000]
    )
    ttl_seconds: int = Field(
        ...,
        description="Time-to-live for sessions in seconds",
        gt=0,
        examples=[3600, 7200]
    )


class MemoryStatsResponse(BaseModel):
    """Response model for memory statistics endpoint."""
    memory_stats: MemoryStats = Field(
        ...,
        description="Current memory cache statistics"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "memory_stats": {
                    "current_size": 42,
                    "max_size": 1000,
                    "ttl_seconds": 3600
                }
            }
        }
    }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(
        ...,
        description="Health status of the service",
        examples=["healthy", "unhealthy"]
    )
    service: str = Field(
        ...,
        description="Service name",
        examples=["chatbot-api"]
    )
    version: str = Field(
        ...,
        description="API version",
        examples=["1.0.0"]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "service": "chatbot-api",
                "version": "1.0.0"
            }
        }
    }


class APIInfoResponse(BaseModel):
    """Response model for root endpoint."""
    message: str = Field(
        ...,
        description="Welcome message",
        examples=["ChatGroq Conversational Chatbot API"]
    )
    version: str = Field(
        ...,
        description="API version",
        examples=["1.0.0"]
    )
    docs: str = Field(
        ...,
        description="Link to API documentation",
        examples=["/docs"]
    )
    health: str = Field(
        ...,
        description="Link to health check endpoint",
        examples=["/health"]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "ChatGroq Conversational Chatbot API",
                "version": "1.0.0",
                "docs": "/docs",
                "health": "/health"
            }
        }
    }