import time
from fastapi import APIRouter, HTTPException, status, Depends,Path
from pydantic import BaseModel, Field
from typing import Optional, List
from langchain.schema import HumanMessage
from app.auth import (
    authenticate_admin, 
    authenticate_user,
    login_admin,
    login_user,
    set_admin_credentials, 
    get_admin_info,
    check_redis_connection,
    create_user,
    get_user,
    get_all_users,
    update_user,
    delete_user,
    update_last_login,
    get_user_sessions,
    get_current_admin,
)
from app.llm import llm_service
import logging
from typing import Annotated

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Track application start time for uptime calculation
app_start_time = time.time()

# Pydantic Models

class LoginRequest(BaseModel):
    """Request model for admin login."""
    username: str = Field(..., description="Admin username")
    password: str = Field(..., description="Admin password")

class LoginResponse(BaseModel):
    """Response model for successful login."""
    access_token: str = Field(..., description="Dynamic auth key for admin")
    token_type: str = Field(..., description="Token type", examples=["auth_key"])
    expires_in: int = Field(..., description="Token expiration time in seconds")
    username: str = Field(..., description="Authenticated username")

class ChangeCredentialsRequest(BaseModel):
    """Request model for changing admin credentials."""
    new_username: str = Field(..., min_length=3, max_length=50, description="New admin username")
    new_password: str = Field(..., min_length=6, description="New admin password")

class AdminInfoResponse(BaseModel):
    """Response model for admin information."""
    username: str = Field(..., description="Current admin username")
    created_at: Optional[str] = Field(None, description="Account creation timestamp")
    last_updated: Optional[str] = Field(None, description="Last credentials update timestamp")

class SystemStatusResponse(BaseModel):
    """Response model for system status."""
    redis_connected: bool = Field(..., description="Redis connection status")
    chatgroq_healthy: bool = Field(..., description="ChatGroq service health")
    active_sessions_count: int = Field(..., description="Number of active sessions")
    uptime_seconds: int = Field(..., description="Application uptime in seconds")
    uptime_formatted: str = Field(..., description="Human-readable uptime")

class TestChatRequest(BaseModel):
    """Request model for testing ChatGroq connection."""
    message: str = Field(..., description="Test message to send to ChatGroq")

class TestChatResponse(BaseModel):
    """Response model for ChatGroq test."""
    success: bool = Field(..., description="Whether the test was successful")
    response: Optional[str] = Field(None, description="ChatGroq response (if successful)")
    error: Optional[str] = Field(None, description="Error message (if failed)")

# User Management Models

class CreateUserRequest(BaseModel):
    """Request model for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50, description="Username for the new user")
    password: str = Field(..., min_length=6, description="Password for the new user")
    email: str = Field(..., description="Email address for the new user")
    full_name: Optional[str] = Field(None, description="Full name of the user")

class UpdateUserRequest(BaseModel):
    """Request model for updating user information."""
    email: Optional[str] = Field(None, description="New email address")
    full_name: Optional[str] = Field(None, description="New full name")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    password: Optional[str] = Field(None, min_length=6, description="New password")

class UserResponse(BaseModel):
    """Response model for user information."""
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: str = Field(..., description="Full name")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: str = Field(..., description="User creation timestamp")
    last_updated: str = Field(..., description="Last update timestamp")
    last_login: Optional[str] = Field(None, description="Last login timestamp")

class UserListResponse(BaseModel):
    """Response model for list of users."""
    users: List[UserResponse] = Field(..., description="List of users")
    total_count: int = Field(..., description="Total number of users")

class UserSessionsResponse(BaseModel):
    """Response model for user sessions."""
    username: str = Field(..., description="Username")
    sessions: List[dict] = Field(..., description="Active sessions for the user")

class UserLoginRequest(BaseModel):
    """Request model for user login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class UserLoginResponse(BaseModel):
    """Response model for user login."""
    access_token: str = Field(..., description="Dynamic auth key for user")
    token_type: str = Field(..., description="Token type", examples=["auth_key"])
    expires_in: int = Field(..., description="Token expiration time in seconds")
    username: str = Field(..., description="Authenticated username")
    user_type: str = Field(..., description="User type", examples=["user"])
    user_info: UserResponse = Field(..., description="User information")

# Authentication Endpoints

@router.post(
    "/login", 
    response_model=LoginResponse,
    summary="Admin login",
    description="Authenticate admin user and receive dynamic auth key for API access"
)
async def login(request: LoginRequest):
    """
    Authenticate admin user and return dynamic auth key.
    Use the returned key in the Authorization header for authenticated endpoints.
    """
    try:
        auth_key = login_admin(request.username, request.password)
        if auth_key:
            logger.info(f"Admin user '{request.username}' logged in successfully")
            return LoginResponse(
                access_token=auth_key,
                token_type="auth_key",
                expires_in=60 * 60,  # 1 hour
                username=request.username
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "AuthKey"},
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )

@router.post(
    "/logout",
    summary="Admin logout",
    description="Logout admin user (no server-side invalidation for dynamic auth key)"
)
async def logout(admin: dict = Depends(get_current_admin)):
    """
    Logout admin user.
    This endpoint is mainly for logging purposes.
    """
    try:
        logger.info(f"Admin user '{admin['username']}' logged out")
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

# Admin Management Endpoints

@router.get(
    "/info",
    response_model=AdminInfoResponse,
    summary="Get admin information",
    description="Get current admin account information"
)
async def get_admin_info_endpoint(admin: dict = Depends(get_current_admin)):
    """Get current admin account information."""
    try:
        admin_info = get_admin_info()
        if not admin_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin information not found"
            )
        return AdminInfoResponse(**admin_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get admin info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin information"
        )

@router.post(
    "/change-credentials",
    summary="Change admin credentials",
    description="Update admin username and password"
)
async def change_credentials(
    request: ChangeCredentialsRequest,
    admin: dict = Depends(get_current_admin)
):
    """Change admin username and password."""
    try:
        if set_admin_credentials(request.new_username, request.new_password):
            logger.info(f"Admin credentials updated by '{admin['username']}'")
            return {
                "message": "Credentials updated successfully",
                "new_username": request.new_username
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update credentials"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change credentials error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating credentials"
        )

# System Status and Management

@router.get(
    "/status",
    response_model=SystemStatusResponse,
    summary="Get system status",
    description="Get overall system health and status information"
)
async def get_system_status(admin: dict = Depends(get_current_admin)):
    """Get system status and health information."""
    try:
        # Check Redis connection
        redis_connected = check_redis_connection()
        # Check ChatGroq health
        chatgroq_healthy = await llm_service.health_check()
        # Get active sessions (deprecated, set count to 0)
        active_sessions_count = 0
        # Calculate uptime
        uptime_seconds = int(time.time() - app_start_time)
        uptime_formatted = format_uptime(uptime_seconds)
        return SystemStatusResponse(
            redis_connected=redis_connected,
            chatgroq_healthy=chatgroq_healthy,
            active_sessions_count=active_sessions_count,
            uptime_seconds=uptime_seconds,
            uptime_formatted=uptime_formatted
        )
    except Exception as e:
        logger.error(f"Get system status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system status"
        )

@router.post(
    "/test-chat",
    response_model=TestChatResponse,
    summary="Test ChatGroq connection",
    description="Test ChatGroq API connection with a sample message"
)
async def test_chatgroq_connection(
    request: TestChatRequest,
    admin: dict = Depends(get_current_admin)
):
    """Test ChatGroq connection with a sample message."""
    try:
        test_messages = [HumanMessage(content=request.message)]
        response = await llm_service.generate_response(test_messages)
        logger.info(f"ChatGroq test successful for admin '{admin['username']}'")
        return TestChatResponse(
            success=True,
            response=response,
            error=None
        )
    except Exception as e:
        logger.error(f"ChatGroq test error: {e}")
        return TestChatResponse(
            success=False,
            response=None,
            error=str(e)
        )

# User Management Endpoints (Admin Only)

@router.post(
    "/users",
    response_model=UserResponse,
    summary="Create new user",
    description="Create a new user account (admin only)"
)
async def create_new_user(
    request: CreateUserRequest,
    admin: dict = Depends(get_current_admin)
):
    """Create a new user account."""
    try:
        existing_user = get_user(request.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User '{request.username}' already exists"
            )
        success = create_user(
            username=request.username,
            password=request.password,
            email=request.email,
            full_name=request.full_name
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        user_data = get_user(request.username)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created but could not retrieve data"
            )
        logger.info(f"Admin '{admin['username']}' created user '{request.username}'")
        return UserResponse(**user_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )

@router.get(
    "/users",
    response_model=UserListResponse,
    summary="Get all users",
    description="Get list of all users (admin only)"
)
async def get_all_users_endpoint(admin: dict = Depends(get_current_admin)):
    """Get list of all users."""
    try:
        users_data = get_all_users()
        users = [UserResponse(**user) for user in users_data]
        return UserListResponse(
            users=users,
            total_count=len(users)
        )
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get(
    "/users/{username}",
    response_model=UserResponse,
    summary="Get user by username",
    description="Get specific user information (admin only)"
)
async def get_user_endpoint(
    username: Annotated[str, Path(description="Username to retrieve")],
    admin: dict = Depends(get_current_admin)
):
    """Get specific user information."""
    try:
        user_data = get_user(username)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{username}' not found"
            )
        return UserResponse(**user_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )

@router.put(
    "/users/{username}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user information (admin only)"
)
async def update_user_endpoint(
    username: str,
    request: UpdateUserRequest,
    admin: dict = Depends(get_current_admin)
):
    """Update user information."""
    try:
        existing_user = get_user(username)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{username}' not found"
            )
        success = update_user(
            username=username,
            email=request.email,
            full_name=request.full_name,
            is_active=request.is_active,
            password=request.password
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
        user_data = get_user(username)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User updated but could not retrieve data"
            )
        logger.info(f"Admin '{admin['username']}' updated user '{username}'")
        return UserResponse(**user_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user"
        )

@router.delete(
    "/users/{username}",
    summary="Delete user",
    description="Delete a user account (admin only)"
)
async def delete_user_endpoint(
    username: str,
    admin: dict = Depends(get_current_admin)
):
    """Delete a user account."""
    try:
        existing_user = get_user(username)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{username}' not found"
            )
        success = delete_user(username)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
        logger.info(f"Admin '{admin['username']}' deleted user '{username}'")
        return {"message": f"User '{username}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the user"
        )

@router.get(
    "/users/{username}/sessions",
    response_model=UserSessionsResponse,
    summary="Get user sessions",
    description="Get active sessions for a specific user (admin only)"
)
async def get_user_sessions_endpoint(
    username: str,
    admin: dict = Depends(get_current_admin)
):
    """Get active sessions for a specific user."""
    try:
        existing_user = get_user(username)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{username}' not found"
            )
        sessions = get_user_sessions(username)
        return UserSessionsResponse(
            username=username,
            sessions=sessions
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user sessions"
        )

# User Login Endpoint (for regular users)

@router.post(
    "/user-login",
    response_model=UserLoginResponse,
    summary="User login",
    description="Authenticate regular user and receive dynamic auth key"
)
async def user_login(request: UserLoginRequest):
    """
    Authenticate regular user and return dynamic auth key.
    Use the returned key in the Authorization header for authenticated endpoints.
    """
    try:
        auth_key = login_user(request.username, request.password)
        if not auth_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "AuthKey"},
            )
        update_last_login(request.username)
        updated_user_data = get_user(request.username)
        logger.info(f"User '{request.username}' logged in successfully")
        return UserLoginResponse(
            access_token=auth_key,
            token_type="auth_key",
            expires_in=60 * 60,
            username=request.username,
            user_type="user",
            user_info=UserResponse(**updated_user_data)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )

# Utility Functions

def format_uptime(seconds: int) -> str:
    """Format uptime in a human-readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"
