import redis
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Redis connection for Upstash
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable is required for Upstash Redis")

# Initialize Redis client
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# JWT and password configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer(auto_error=False)

# Redis keys
ADMIN_CREDENTIALS_KEY = "admin:credentials"
ACTIVE_SESSIONS_KEY = "admin:sessions"

class AuthenticationError(Exception):
    """Custom authentication error."""
    pass

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def init_default_admin():
    """Initialize default admin credentials if they don't exist."""
    try:
        existing = redis_client.hgetall(ADMIN_CREDENTIALS_KEY)
        if not existing:
            # Set default credentials
            default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
            default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
            
            hashed_password = hash_password(default_password)
            
            redis_client.hset(ADMIN_CREDENTIALS_KEY, mapping={
                "username": default_username,
                "password": hashed_password,
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            })
            
            print(f"✅ Default admin credentials initialized:")
            print(f"   Username: {default_username}")
            print(f"   Password: {default_password}")
            print(f"   ⚠️  Please change these credentials immediately!")
            
    except Exception as e:
        print(f"❌ Failed to initialize admin credentials: {e}")

def authenticate_admin(username: str, password: str) -> bool:
    """Authenticate admin user against Redis credentials."""
    try:
        credentials = redis_client.hgetall(ADMIN_CREDENTIALS_KEY)
        if not credentials:
            return False
            
        stored_username = credentials.get("username")
        stored_password = credentials.get("password")
        
        if stored_username != username:
            return False
            
        return verify_password(password, stored_password)
        
    except Exception as e:
        print(f"Authentication error: {e}")
        return False

def set_admin_credentials(username: str, password: str) -> bool:
    """Set new admin credentials in Redis."""
    try:
        hashed_password = hash_password(password)
        
        redis_client.hset(ADMIN_CREDENTIALS_KEY, mapping={
            "username": username,
            "password": hashed_password,
            "last_updated": datetime.utcnow().isoformat()
        })
        
        return True
        
    except Exception as e:
        print(f"Error setting credentials: {e}")
        return False

def get_admin_info() -> Optional[dict]:
    """Get admin user information (without password)."""
    try:
        credentials = redis_client.hgetall(ADMIN_CREDENTIALS_KEY)
        if credentials:
            return {
                "username": credentials.get("username"),
                "created_at": credentials.get("created_at"),
                "last_updated": credentials.get("last_updated")
            }
        return None
    except Exception as e:
        print(f"Error getting admin info: {e}")
        return None

def create_session(username: str) -> str:
    """Create a new session and store in Redis."""
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "username": username,
        "created_at": datetime.utcnow().isoformat(),
        "last_activity": datetime.utcnow().isoformat()
    }
    
    # Store session with expiration
    redis_client.hset(f"{ACTIVE_SESSIONS_KEY}:{session_id}", mapping=session_data)
    redis_client.expire(f"{ACTIVE_SESSIONS_KEY}:{session_id}", ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    return session_id

def verify_session(session_id: str) -> Optional[dict]:
    """Verify session exists and is valid."""
    try:
        session_data = redis_client.hgetall(f"{ACTIVE_SESSIONS_KEY}:{session_id}")
        if session_data:
            # Update last activity
            redis_client.hset(
                f"{ACTIVE_SESSIONS_KEY}:{session_id}", 
                "last_activity", 
                datetime.utcnow().isoformat()
            )
            return session_data
        return None
    except Exception as e:
        print(f"Session verification error: {e}")
        return None

def invalidate_session(session_id: str) -> bool:
    """Invalidate a session."""
    try:
        redis_client.delete(f"{ACTIVE_SESSIONS_KEY}:{session_id}")
        return True
    except Exception as e:
        print(f"Session invalidation error: {e}")
        return False

def get_active_sessions() -> list:
    """Get all active sessions."""
    try:
        pattern = f"{ACTIVE_SESSIONS_KEY}:*"
        session_keys = redis_client.keys(pattern)
        sessions = []
        
        for key in session_keys:
            session_data = redis_client.hgetall(key)
            if session_data:
                session_id = key.split(":")[-1]
                sessions.append({
                    "session_id": session_id,
                    **session_data
                })
        
        return sessions
    except Exception as e:
        print(f"Error getting active sessions: {e}")
        return []

async def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None, alias="admin_session")
) -> dict:
    """
    Get current authenticated admin user.
    Supports both JWT Bearer tokens and session cookies.
    """
    # Try JWT token first
    if credentials and credentials.credentials:
        token_data = verify_token(credentials.credentials)
        if token_data and token_data.get("sub") == "admin":
            return {"username": "admin", "auth_method": "jwt"}
    
    # Try session cookie
    if session_token:
        session_data = verify_session(session_token)
        if session_data:
            return {
                "username": session_data.get("username"),
                "auth_method": "session",
                "session_id": session_token
            }
    
    # No valid authentication found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_admin_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None, alias="admin_session")
) -> Optional[dict]:
    """
    Get current authenticated admin user (optional).
    Returns None if not authenticated instead of raising an exception.
    """
    try:
        return await get_current_admin(credentials, session_token)
    except HTTPException:
        return None

def check_redis_connection() -> bool:
    """Check if Redis connection is working."""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False
