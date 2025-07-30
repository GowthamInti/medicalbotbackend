from pydantic import BaseModel, Field
from typing import Optional, List


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
    llm_provider: str = Field(
        ...,
        description="LLM provider used to generate this response",
        examples=["chatgroq"]
    )
    model: str = Field(
        ...,
        description="Specific model used for this response",
        examples=["llama3-8b-8192"]
    )
    user_id: str = Field(
        ...,
        description="ID of the authenticated user",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "response": "Hello! I'm an AI assistant powered by ChatGroq. I'm doing well and ready to help you with any questions or tasks you have. How can I assist you today?",
                "session_id": "user123_session",
                "llm_provider": "chatgroq",
                "model": "llama3-8b-8192",
                "user_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    }


class LLMProviderInfo(BaseModel):
    """Model for LLM provider information."""
    provider: str = Field(..., description="Provider name", examples=["chatgroq"])
    model: str = Field(..., description="Model name", examples=["llama3-8b-8192"])
    base_url: str = Field(..., description="Base URL for the provider", examples=["https://api.groq.com/openai/v1"])
    temperature: float = Field(..., description="Temperature setting", examples=[0.7])
    max_tokens: int = Field(..., description="Maximum tokens", examples=[1024])
    type: str = Field(..., description="Provider type", examples=["cloud"])
    description: str = Field(..., description="Provider description")


class LLMProviderResponse(BaseModel):
    """Response model for current LLM provider information."""
    current_provider: LLMProviderInfo = Field(..., description="Current LLM provider information")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "current_provider": {
                    "provider": "chatgroq",
                    "model": "llama3-8b-8192",
                    "base_url": "https://api.groq.com/openai/v1",
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "type": "cloud",
                    "description": "ChatGroq cloud-based LLM inference"
                }
            }
        }
    }


class AvailableProvider(BaseModel):
    """Model for available LLM provider."""
    name: str = Field(..., description="Provider identifier")
    display_name: str = Field(..., description="Human-readable provider name")
    type: str = Field(..., description="Provider type (cloud)")
    description: str = Field(..., description="Provider description")
    requires_api_key: bool = Field(..., description="Whether this provider requires an API key")
    models: List[str] = Field(..., description="Available models for this provider")


class AvailableProvidersResponse(BaseModel):
    """Response model for available LLM providers."""
    providers: List[AvailableProvider] = Field(..., description="List of available LLM providers")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "providers": [
                    {
                        "name": "chatgroq",
                        "display_name": "ChatGroq",
                        "type": "cloud",
                        "description": "ChatGroq cloud-based LLM inference",
                        "requires_api_key": True,
                        "models": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
                    }
                ]
            }
        }
    }


class LLMHealthResponse(BaseModel):
    """Response model for LLM provider health check."""
    provider: str = Field(..., description="Provider name")
    healthy: bool = Field(..., description="Whether the provider is healthy")
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "provider": "chatgroq",
                    "healthy": True
                },
                {
                    "provider": "chatgroq",
                    "healthy": False,
                    "error": "Connection timeout to ChatGroq API"
                }
            ]
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
    llm_provider: str = Field(
        ...,
        description="Current LLM provider",
        examples=["chatgroq"]
    )
    llm_healthy: bool = Field(
        ...,
        description="Whether the LLM provider is healthy"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "service": "chatbot-api",
                "version": "1.0.0",
                "llm_provider": "chatgroq",
                "llm_healthy": True
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
    current_llm_provider: str = Field(
        ...,
        description="Current LLM provider",
        examples=["chatgroq"]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "ChatGroq Conversational Chatbot API",
                "version": "1.0.0",
                "docs": "/docs",
                "health": "/health",
                "current_llm_provider": "chatgroq"
            }
        }
    }