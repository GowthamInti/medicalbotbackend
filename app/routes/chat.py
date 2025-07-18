from fastapi import APIRouter, HTTPException, status
from langchain.schema import HumanMessage, AIMessage
from app.schemas.chat import ChatRequest, ChatResponse
from app.llm import llm_service
from app.memory import memory_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Handle chat conversation with session-based memory.
    
    Args:
        request: ChatRequest containing session_id and message
        
    Returns:
        ChatResponse: Response from the chatbot
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        logger.info(f"Processing chat request for session: {request.session_id}")
        
        # Get or create memory for this session
        memory = memory_service.get_memory(request.session_id)
        
        # Get chat history from memory
        chat_history = memory.chat_memory.messages
        
        # Add current user message to the conversation
        current_messages = chat_history + [HumanMessage(content=request.message)]
        
        # Generate response using LLM
        response_content = await llm_service.generate_response(current_messages)
        
        # Save the conversation to memory
        memory.chat_memory.add_user_message(request.message)
        memory.chat_memory.add_ai_message(response_content)
        
        logger.info(f"Successfully generated response for session: {request.session_id}")
        
        return ChatResponse(
            response=response_content,
            session_id=request.session_id
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


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear memory for a specific session.
    
    Args:
        session_id: Session identifier to clear
        
    Returns:
        dict: Success message
    """
    try:
        cleared = memory_service.clear_session(session_id)
        if cleared:
            return {"message": f"Session {session_id} cleared successfully"}
        else:
            return {"message": f"Session {session_id} not found"}
    except Exception as e:
        logger.error(f"Error clearing session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while clearing the session"
        )


@router.get("/stats")
async def get_memory_stats():
    """
    Get memory cache statistics.
    
    Returns:
        dict: Cache statistics
    """
    try:
        stats = memory_service.get_cache_stats()
        return {"memory_stats": stats}
    except Exception as e:
        logger.error(f"Error getting memory stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving memory statistics"
        )