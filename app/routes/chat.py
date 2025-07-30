from fastapi import APIRouter, HTTPException, status, Path, Depends
from fastapi.responses import JSONResponse
from langchain.schema import HumanMessage, AIMessage
from app.schemas.chat import (
    ChatRequest, 
    ChatResponse, 
    SessionClearResponse, 
    MemoryStatsResponse
)
from app.llm import llm_service
from app.memory import memory_service
from app.auth import get_current_admin, get_current_admin_optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the chatbot",
    description="""
    Send a message to the conversational chatbot and receive a response.
    
    The chatbot uses ChatGroq for generating responses and maintains conversation 
    history using the provided session_id. Each session has its own memory that 
    persists for the configured TTL period.
    
    **Authentication Required**: You must be logged in to use this endpoint.
    
    **Session Management:**
    - Sessions are automatically created when first accessed
    - Conversation history is maintained within each session
    - Sessions expire after the configured TTL (default: 1 hour)
    - Use consistent session_id to maintain conversation context
    - Sessions are linked to your user account for privacy
    
    **Message Guidelines:**
    - Messages can be up to 4000 characters long
    - Supports any text-based conversation
    - The AI responds based on the full conversation history
    """,
    responses={
        200: {
            "description": "Successful response from the chatbot",
            "content": {
                "application/json": {
                    "examples": {
                        "greeting": {
                            "summary": "Simple greeting",
                            "value": {
                                "response": "Hello! I'm an AI assistant powered by ChatGroq. How can I help you today?",
                                "session_id": "user123_session",
                                "llm_provider": "chatgroq",
                                "model": "llama3-8b-8192",
                                "user_id": "550e8400-e29b-41d4-a716-446655440000"
                            }
                        },
                        "technical_question": {
                            "summary": "Technical question response",
                            "value": {
                                "response": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn and make predictions from data...",
                                "session_id": "tech_session_01",
                                "llm_provider": "chatgroq",
                                "model": "llama3-8b-8192",
                                "user_id": "550e8400-e29b-41d4-a716-446655440000"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Authentication required"
                    }
                }
            }
        },
        400: {
            "description": "Bad request - invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid request: message cannot be empty"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred while processing your request"
                    }
                }
            }
        }
    }
)
async def chat(
    request: ChatRequest, 
    admin: dict = Depends(get_current_admin)
) -> ChatResponse:
    """
    Handle chat conversation with session-based memory using ChatGroq.
    
    Args:
        request: ChatRequest containing session_id and message
        admin: Current authenticated admin user
        
    Returns:
        ChatResponse: Response from the chatbot
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        logger.info(f"Processing chat request for admin {admin['username']}, session: {request.session_id}")
        
        # Create admin-specific session ID to ensure privacy
        admin_session_id = f"admin_{admin['username']}_{request.session_id}"
        
        # Get or create memory for this session
        memory = memory_service.get_memory(admin_session_id)
        
        # Get chat history from memory
        chat_history = memory.chat_memory.messages
        
        # Add current user message to the conversation
        current_messages = chat_history + [HumanMessage(content=request.message)]
        
        # Generate response using ChatGroq
        response_content = await llm_service.generate_response(current_messages)
        
        # Get provider info for response
        provider_info = llm_service.get_provider_info()
        
        # Save the conversation to memory
        memory.chat_memory.add_user_message(request.message)
        memory.chat_memory.add_ai_message(response_content)
        
        logger.info(f"Successfully generated response for admin {admin['username']}, session: {request.session_id}")
        
        return ChatResponse(
            response=response_content,
            session_id=request.session_id,
            llm_provider=provider_info["provider"],
            model=provider_info["model"],
            user_id=admin['username']
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )


@router.delete(
    "/session/{session_id}",
    response_model=SessionClearResponse,
    status_code=status.HTTP_200_OK,
    tags=["memory"],
    summary="Clear session memory",
    description="""
    Clear the conversation memory for a specific session.
    
    This will permanently delete all conversation history for the given session
    that belongs to the authenticated user.
    
    **Authentication Required**: You must be logged in and can only clear your own sessions.
    
    **Use Cases:**
    - Reset conversation context
    - Clear sensitive information
    - Start fresh conversation
    - Memory management
    """,
    responses={
        200: {
            "description": "Session cleared successfully or session not found",
            "content": {
                "application/json": {
                    "examples": {
                        "cleared": {
                            "summary": "Session successfully cleared",
                            "value": {
                                "message": "Session user123_session cleared successfully"
                            }
                        },
                        "not_found": {
                            "summary": "Session not found",
                            "value": {
                                "message": "Session unknown_session not found"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Authentication required"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred while clearing the session"
                    }
                }
            }
        }
    }
)
async def clear_session(
    session_id: str = Path(
        ...,
        description="Session identifier to clear",
        examples=["user123_session", "session_abc123"],
        regex="^[a-zA-Z0-9_-]+$"
    ),
    admin: dict = Depends(get_current_admin)
) -> SessionClearResponse:
    """
    Clear memory for a specific session belonging to the authenticated admin.
    
    Args:
        session_id: Session identifier to clear
        admin: Current authenticated admin
        
    Returns:
        SessionClearResponse: Success message
    """
    try:
        # Create admin-specific session ID
        admin_session_id = f"admin_{admin['username']}_{session_id}"
        
        cleared = memory_service.clear_session(admin_session_id)
        if cleared:
            message = f"Session {session_id} cleared successfully"
        else:
            message = f"Session {session_id} not found"
            
        return SessionClearResponse(message=message)
    except Exception as e:
        logger.error(f"Error clearing session {session_id} for admin {admin['username']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while clearing the session"
        )


@router.get(
    "/stats",
    response_model=MemoryStatsResponse,
    status_code=status.HTTP_200_OK,
    tags=["memory"],
    summary="Get memory cache statistics",
    description="""
    Retrieve current statistics about the memory cache system.
    
    **Authentication Required**: Only superusers can access system statistics.
    
    This endpoint provides insights into:
    - Current number of active sessions
    - Maximum cache capacity
    - TTL configuration
    
    **Useful for:**
    - Monitoring system usage
    - Capacity planning
    - Performance analysis
    - Health monitoring
    """,
    responses={
        200: {
            "description": "Memory statistics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "memory_stats": {
                            "current_size": 42,
                            "max_size": 1000,
                            "ttl_seconds": 3600
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Authentication required"
                    }
                }
            }
        },
        403: {
            "description": "Insufficient permissions",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Superuser access required"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred while retrieving memory statistics"
                    }
                }
            }
        }
    }
)
async def get_memory_stats(
    admin: dict = Depends(get_current_admin)
) -> MemoryStatsResponse:
    """
    Get memory cache statistics (admin only).
    
    Args:
        admin: Current authenticated admin
    
    Returns:
        MemoryStatsResponse: Cache statistics
    """
    try:
        stats = memory_service.get_cache_stats()
        return MemoryStatsResponse(memory_stats=stats)
    except Exception as e:
        logger.error(f"Error getting memory stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving memory statistics"
        )