import time
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langchain.schema import HumanMessage
from app.auth import (
    authenticate_admin, 
    create_access_token, 
    set_admin_credentials, 
    get_admin_info,
    create_session,
    invalidate_session,
    get_active_sessions,
    get_current_admin,
    get_current_admin_optional,
    check_redis_connection
)
from app.llm import llm_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

# Track application start time for uptime calculation
app_start_time = time.time()

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangeCredentialsRequest(BaseModel):
    new_username: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.get("/login", response_class=HTMLResponse, summary="Admin login page")
async def login_page(request: Request, error: str = None, success: str = None):
    """Display the admin login page."""
    # Check if there are any credentials set
    admin_info = get_admin_info()
    show_default_creds = admin_info is None
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
        "success": success,
        "show_default_creds": show_default_creds
    })

@router.post("/login", response_class=HTMLResponse, summary="Process admin login")
async def login_process(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    """Process admin login form submission."""
    try:
        if authenticate_admin(username, password):
            # Create session
            session_id = create_session(username)
            
            # Set session cookie
            response = RedirectResponse(url="/admin/dashboard", status_code=302)
            response.set_cookie(
                key="admin_session",
                value=session_id,
                max_age=3600,  # 1 hour
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax"
            )
            
            logger.info(f"Admin user '{username}' logged in successfully")
            return response
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Invalid username or password",
                "username": username
            })
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "An error occurred during login. Please try again.",
            "username": username
        })

@router.post("/logout", summary="Admin logout")
async def logout(request: Request, admin: dict = Depends(get_current_admin)):
    """Logout admin user and invalidate session."""
    try:
        # Invalidate session if using session auth
        if admin.get("auth_method") == "session" and admin.get("session_id"):
            invalidate_session(admin["session_id"])
        
        # Clear cookie and redirect
        response = RedirectResponse(url="/admin/login?success=Logged out successfully", status_code=302)
        response.delete_cookie(key="admin_session")
        
        logger.info(f"Admin user '{admin['username']}' logged out")
        return response
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return RedirectResponse(url="/admin/login?error=Logout failed", status_code=302)

@router.get("/dashboard", response_class=HTMLResponse, summary="Admin dashboard")
async def dashboard(
    request: Request, 
    admin: dict = Depends(get_current_admin),
    success: str = None,
    error: str = None
):
    """Display the admin dashboard."""
    try:
        # Get system information
        admin_info = get_admin_info()
        active_sessions = get_active_sessions()
        redis_status = "✅" if check_redis_connection() else "❌"
        uptime = format_uptime(time.time() - app_start_time)
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "admin": admin,
            "admin_info": admin_info,
            "active_sessions": active_sessions,
            "redis_status": redis_status,
            "uptime": uptime,
            "success": success,
            "error": error
        })
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "admin": admin,
            "error": f"Error loading dashboard: {str(e)}"
        })

@router.post("/change-credentials", summary="Change admin credentials")
async def change_credentials(
    request: Request,
    admin: dict = Depends(get_current_admin),
    new_username: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Change admin username and password."""
    try:
        # Validate passwords match
        if new_password != confirm_password:
            return RedirectResponse(
                url="/admin/dashboard?error=Passwords do not match",
                status_code=302
            )
        
        # Validate password length
        if len(new_password) < 6:
            return RedirectResponse(
                url="/admin/dashboard?error=Password must be at least 6 characters long",
                status_code=302
            )
        
        # Update credentials
        if set_admin_credentials(new_username, new_password):
            logger.info(f"Admin credentials updated by '{admin['username']}'")
            return RedirectResponse(
                url="/admin/dashboard?success=Credentials updated successfully",
                status_code=302
            )
        else:
            return RedirectResponse(
                url="/admin/dashboard?error=Failed to update credentials",
                status_code=302
            )
            
    except Exception as e:
        logger.error(f"Change credentials error: {e}")
        return RedirectResponse(
            url="/admin/dashboard?error=An error occurred while updating credentials",
            status_code=302
        )

@router.post("/test-chat", summary="Test ChatGroq connection")
async def test_chat(
    request: Request,
    admin: dict = Depends(get_current_admin),
    test_message: str = Form(...)
):
    """Test ChatGroq connection with a test message."""
    try:
        # Create test message
        test_messages = [HumanMessage(content=test_message)]
        
        # Test ChatGroq response
        response = await llm_service.generate_response(test_messages)
        
        # Redirect with success
        return RedirectResponse(
            url=f"/admin/dashboard?success=ChatGroq test successful: {response[:50]}...",
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"ChatGroq test error: {e}")
        return RedirectResponse(
            url=f"/admin/dashboard?error=ChatGroq test failed: {str(e)}",
            status_code=302
        )

# API Endpoints for programmatic access

@router.post("/api-login", response_model=TokenResponse, summary="API login for JWT token")
async def api_login(request: LoginRequest):
    """
    Login via API to get JWT token for programmatic access.
    
    This endpoint allows you to get a JWT token that can be used with the chat API.
    """
    try:
        if authenticate_admin(request.username, request.password):
            access_token = create_access_token(
                data={"sub": "admin", "username": request.username}
            )
            
            logger.info(f"API token generated for admin user '{request.username}'")
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )

@router.post("/api-change-credentials", summary="Change credentials via API")
async def api_change_credentials(
    request: ChangeCredentialsRequest,
    admin: dict = Depends(get_current_admin)
):
    """Change admin credentials via API."""
    try:
        # Validate password length
        if len(request.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Update credentials
        if set_admin_credentials(request.new_username, request.new_password):
            logger.info(f"Admin credentials updated via API by '{admin['username']}'")
            return {"message": "Credentials updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update credentials"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API change credentials error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating credentials"
        )

@router.get("/api-info", summary="Get admin information via API")
async def api_info(admin: dict = Depends(get_current_admin)):
    """Get current admin information via API."""
    try:
        admin_info = get_admin_info()
        active_sessions = get_active_sessions()
        
        return {
            "admin": admin_info,
            "active_sessions_count": len(active_sessions),
            "redis_connected": check_redis_connection(),
            "uptime_seconds": int(time.time() - app_start_time)
        }
        
    except Exception as e:
        logger.error(f"API info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin information"
        )

@router.get("/api-sessions", summary="Get active sessions via API")
async def api_sessions(admin: dict = Depends(get_current_admin)):
    """Get all active sessions via API."""
    try:
        sessions = get_active_sessions()
        return {"active_sessions": sessions}
        
    except Exception as e:
        logger.error(f"API sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active sessions"
        )

# Helper functions

def format_uptime(seconds: float) -> str:
    """Format uptime in a human-readable format."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    else:
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        return f"{days}d {hours}h"

# Redirect root admin URL to login
@router.get("/", response_class=RedirectResponse, summary="Redirect to admin login")
async def admin_root():
    """Redirect admin root to login page."""
    return RedirectResponse(url="/admin/login")