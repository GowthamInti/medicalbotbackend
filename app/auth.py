import redis
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict
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
USERS_KEY_PREFIX = "users"
ACTIVE_SESSIONS_KEY = "admin:sessions"
USER_SESSIONS_KEY = "user:sessions"

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

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate regular user against Redis credentials."""
    try:
        user_key = f"{USERS_KEY_PREFIX}:{username}"
        user_data = redis_client.hgetall(user_key)
        
        if not user_data:
            return None
            
        stored_password = user_data.get("password")
        is_active = user_data.get("is_active", "true").lower() == "true"
        
        if not is_active:
            return None
            
        if verify_password(password, stored_password):
            return {
                "username": username,
                "email": user_data.get("email"),
                "full_name": user_data.get("full_name"),
                "is_active": is_active,
                "created_at": user_data.get("created_at"),
                "last_login": user_data.get("last_login")
            }
        
        return None
        
    except Exception as e:
        print(f"User authentication error: {e}")
        return None

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

def create_user(username: str, password: str, email: str, full_name: str = None) -> bool:
    """Create a new user in Redis."""
    try:
        user_key = f"{USERS_KEY_PREFIX}:{username}"
        
        # Check if user already exists
        if redis_client.exists(user_key):
            return False
        
        hashed_password = hash_password(password)
        
        user_data = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "full_name": full_name or username,
            "is_active": "true",
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "last_login": None
        }
        
        redis_client.hset(user_key, mapping=user_data)
        
        # Add to users index
        redis_client.sadd(f"{USERS_KEY_PREFIX}:index", username)
        
        return True
        
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def get_user(username: str) -> Optional[dict]:
    """Get user information by username."""
    try:
        user_key = f"{USERS_KEY_PREFIX}:{username}"
        user_data = redis_client.hgetall(user_key)
        
        if not user_data:
            return None
        
        # Remove password from response
        user_data.pop("password", None)
        user_data["is_active"] = user_data.get("is_active", "true").lower() == "true"
        
        return user_data
        
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_all_users() -> List[dict]:
    """Get all users (without passwords)."""
    try:
        usernames = redis_client.smembers(f"{USERS_KEY_PREFIX}:index")
        users = []
        
        for username in usernames:
            user_data = get_user(username)
            if user_data:
                users.append(user_data)
        
        return users
        
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []

def update_user(username: str, email: str = None, full_name: str = None, 
                is_active: bool = None, password: str = None) -> bool:
    """Update user information."""
    try:
        user_key = f"{USERS_KEY_PREFIX}:{username}"
        
        if not redis_client.exists(user_key):
            return False
        
        update_data = {"last_updated": datetime.utcnow().isoformat()}
        
        if email is not None:
            update_data["email"] = email
        if full_name is not None:
            update_data["full_name"] = full_name
        if is_active is not None:
            update_data["is_active"] = "true" if is_active else "false"
        if password is not None:
            update_data["password"] = hash_password(password)
        
        redis_client.hset(user_key, mapping=update_data)
        return True
        
    except Exception as e:
        print(f"Error updating user: {e}")
        return False

def delete_user(username: str) -> bool:
    """Delete a user."""
    try:
        user_key = f"{USERS_KEY_PREFIX}:{username}"
        
        if not redis_client.exists(user_key):
            return False
        
        # Remove from index
        redis_client.srem(f"{USERS_KEY_PREFIX}:index", username)
        
        # Delete user data
        redis_client.delete(user_key)
        
        # Clear user sessions
        pattern = f"{USER_SESSIONS_KEY}:{username}:*"
        session_keys = redis_client.keys(pattern)
        if session_keys:
            redis_client.delete(*session_keys)
        
        return True
        
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def update_last_login(username: str) -> None:
    """Update user's last login timestamp."""
    try:
        user_key = f"{USERS_KEY_PREFIX}:{username}"
        if redis_client.exists(user_key):
            redis_client.hset(user_key, "last_login", datetime.utcnow().isoformat())
    except Exception as e:
        print(f"Error updating last login: {e}")

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

def create_session(username: str, user_type: str = "admin") -> str:
    """Create a new session and store in Redis."""
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "username": username,
        "user_type": user_type,
        "created_at": datetime.utcnow().isoformat(),
        "last_activity": datetime.utcnow().isoformat()
    }
    
    # Store session with expiration
    if user_type == "admin":
        session_key = f"{ACTIVE_SESSIONS_KEY}:{session_id}"
    else:
        session_key = f"{USER_SESSIONS_KEY}:{username}:{session_id}"
    
    redis_client.hset(session_key, mapping=session_data)
    redis_client.expire(session_key, ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    return session_id

def verify_session(session_id: str, user_type: str = "admin") -> Optional[dict]:
    """Verify session exists and is valid."""
    try:
        if user_type == "admin":
            session_key = f"{ACTIVE_SESSIONS_KEY}:{session_id}"
        else:
            # For user sessions, we need to find the session across all users
            pattern = f"{USER_SESSIONS_KEY}:*:{session_id}"
            keys = redis_client.keys(pattern)
            if not keys:
                return None
            session_key = keys[0]
        
        session_data = redis_client.hgetall(session_key)
        if session_data:
            # Update last activity
            redis_client.hset(session_key, "last_activity", datetime.utcnow().isoformat())
            return session_data
        return None
    except Exception as e:
        print(f"Session verification error: {e}")
        return None

def invalidate_session(session_id: str, user_type: str = "admin") -> bool:
    """Invalidate a session."""
    try:
        if user_type == "admin":
            session_key = f"{ACTIVE_SESSIONS_KEY}:{session_id}"
            redis_client.delete(session_key)
        else:
            # For user sessions, find and delete the session
            pattern = f"{USER_SESSIONS_KEY}:*:{session_id}"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"Session invalidation error: {e}")
        return False

def get_active_sessions() -> list:
    """Get all active admin sessions."""
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

def get_user_sessions(username: str) -> list:
    """Get all active sessions for a specific user."""
    try:
        pattern = f"{USER_SESSIONS_KEY}:{username}:*"
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
        print(f"Error getting user sessions: {e}")
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
            return {"username": "admin", "auth_method": "jwt", "user_type": "admin"}
    
    # Try session cookie
    if session_token:
        session_data = verify_session(session_token, "admin")
        if session_data:
            return {
                "username": session_data.get("username"),
                "auth_method": "session",
                "session_id": session_token,
                "user_type": "admin"
            }
    
    # No valid authentication found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None, alias="user_session")
) -> dict:
    """
    Get current authenticated user (admin or regular user).
    Supports both JWT Bearer tokens and session cookies.
    """
    # Try JWT token first
    if credentials and credentials.credentials:
        token_data = verify_token(credentials.credentials)
        if token_data:
            username = token_data.get("username")
            user_type = token_data.get("user_type", "user")
            
            if user_type == "admin" or username:
                return {
                    "username": username, 
                    "auth_method": "jwt", 
                    "user_type": user_type
                }
    
    # Try session cookie
    if session_token:
        # Try admin session first
        session_data = verify_session(session_token, "admin")
        if session_data and session_data.get("user_type") == "admin":
            return {
                "username": session_data.get("username"),
                "auth_method": "session",
                "session_id": session_token,
                "user_type": "admin"
            }
        
        # Try user session
        session_data = verify_session(session_token, "user")
        if session_data:
            return {
                "username": session_data.get("username"),
                "auth_method": "session",
                "session_id": session_token,
                "user_type": "user"
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
