from fastapi import APIRouter, HTTPException, status, Depends, Header, Body, Path, File, UploadFile, Form
from app.schemas.chat import ChatResponse, SessionClearResponse, MemoryStatsResponse
from app.auth import get_current_user  # Validates token in Authorization header
from app.extractors import extract_text_from_files
from typing import List, Optional
from app.llm import llm_service
from app.memory import memory_service

from app.prompt_template import *  # Import the ultrasound prompt template
import logging


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to chatbot",
    description="Send a message to the chatbot. Requires authentication (Authorization header)."
)
async def chat(
    session_id: str = Form(...),
    message: str = Form(...),
    files: List[UploadFile] = File(None),
    task_name: Optional[str] = Form(None),
    user: dict = Depends(get_current_user)
):
    """
    Handle a chat message.
    Authenticated via Authorization header.
    Uses session_id from body.
    Optionally: session_id can be the token itself if you want, but recommended to keep separate.
    """
    try:
        # Use both session_id and user context for LangChain
        user_id = user["username"]

        memory = memory_service.get_memory(session_id)

        if task_name == "ultrasound":
            user_message = f"{ultrasound}\n\nPatient data:\n{message}"
        else:
            user_message = message


        if files:
            extracted_texts = await extract_text_from_files(files)
            for text in extracted_texts:
                if text: user_message += f"\n\n[content interpreted from attached documents]:\n{text}"
        
        messages = [
            {"role": "user", "content": user_message}
        ]
        # Optional: populate memory manually if needed
        memory.chat_memory.add_user_message(messages)

        # Or pass it to your LLM service directly
        response_text = await llm_service.generate_response(
            input_message=messages,
            memory=memory)

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            llm_provider="chatgroq",
            model="llama3-8b-8192",
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Chat error for user {user.get('username')}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the chat request"
        )

@router.delete(
    "/sessions/{session_id}",
    response_model=SessionClearResponse,
    status_code=status.HTTP_200_OK,
    summary="Clear conversation session",
    description="Clear memory for a specific session belonging to the authenticated user."
)
async def clear_session(
    session_id: str = Path(..., description="Session identifier to clear"),
    user: dict = Depends(get_current_user)
):
    """
    Clear session context for authenticated user.
    """
    try:
        user_session_id = f"{user['user_type']}_{user['username']}_{session_id}"
        cleared = memory_service.clear_session(user_session_id)
        if cleared:
            message = f"Session {session_id} cleared successfully"
        else:
            message = f"Session {session_id} not found"
        return SessionClearResponse(message=message)
    except Exception as e:
        logger.error(f"Error clearing session {session_id} for {user['username']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while clearing the session"
        )

@router.get(
    "/memory/stats",
    response_model=MemoryStatsResponse,
    status_code=status.HTTP_200_OK,
    tags=["memory"],
    summary="Get memory cache statistics",
    description="Retrieve current statistics about the memory cache system. Requires authentication."
)
async def get_memory_stats(user: dict = Depends(get_current_user)):
    """
    Get stats about memory/session cache. Only authenticated users can access.
    """
    try:
        stats = memory_service.get_stats()
        return MemoryStatsResponse(memory_stats=stats)
    except Exception as e:
        logger.error(f"Error getting memory stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get memory stats"
        )
