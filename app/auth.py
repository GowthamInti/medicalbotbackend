import redis
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from fastapi import HTTPException, status, Depends, Header
from passlib.context import CryptContext
import os

# Redis connection for Upstash
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable is required for Upstash Redis")

# Initialize Redis client
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# Auth key configuration
AUTH_KEY_TTL_MINUTES = int(os.getenv("AUTH_KEY_TTL_MINUTES", "60"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis keys
ADMIN_CREDENTIALS_KEY = "admin:credentials"
USERS_KEY_PREFIX = "users"

class AuthenticationError(Exception):
    """Custom authentication error."""
    pass

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def generate_dynamic_auth_key(username: str, user_type: str = "user", ttl_minutes: int = AUTH_KEY_TTL_MINUTES) -> str:
    """
    Generate a secure, random authentication key for the user and store in Redis with a TTL.
    """
    auth_key = secrets.token_urlsafe(32)
    key_prefix = "admin:authkey" if user_type == "admin" else "user:authkey"
    redis_client.set(f"{key_prefix}:{username}", auth_key, ex=ttl_minutes * 60)
    return auth_key

def authenticate_with_dynamic_key(username: str, auth_key: str, user_type: str = "user") -> bool:
    """
    Authenticate user/admin using the dynamic auth key stored in Redis.
    """
    key_prefix = "admin:authkey" if user_type == "admin" else "user:authkey"
    stored_key = redis_client.get(f"{key_prefix}:{username}")
    return stored_key == auth_key

def init_default_admin():
    """Initialize default admin credentials if they don't exist."""
    try:
        existing = redis_client.hgetall(ADMIN_CREDENTIALS_KEY)
        if not existing:
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
            "last_login": ""
        }
        redis_client.hset(user_key, mapping=user_data)
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
        redis_client.srem(f"{USERS_KEY_PREFIX}:index", username)
        redis_client.delete(user_key)
        redis_client.delete(f"user:authkey:{username}")
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

def login_user(username: str, password: str) -> Optional[str]:
    """
    Authenticate user and return dynamic auth key if credentials are valid.
    """
    user = authenticate_user(username, password)
    if user:
        update_last_login(username)
        auth_key = generate_dynamic_auth_key(username, user_type="user")
        return auth_key
    return None

def login_admin(username: str, password: str) -> Optional[str]:
    """
    Authenticate admin and return dynamic auth key if credentials are valid.
    """
    if authenticate_admin(username, password):
        auth_key = generate_dynamic_auth_key(username, user_type="admin")
        return auth_key
    return None

async def get_current_admin(
    admin_username: str = Header(..., alias="X-Admin-Username"),
    auth_key: str = Header(..., alias="Authorization")
) -> dict:
    """
    Get current authenticated admin user using dynamic auth key in headers.
    """
    if authenticate_with_dynamic_key(admin_username, auth_key, user_type="admin"):
        admin_info = get_admin_info()
        return {
            "username": admin_username,
            "auth_method": "auth_key",
            "user_type": "admin",
            "admin_info": admin_info
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin authentication required",
        headers={"WWW-Authenticate": "AuthKey"},
    )

async def get_current_user(
    username: str = Header(..., alias="X-User-Username"),
    auth_key: str = Header(..., alias="Authorization")
) -> dict:
    """
    Get current authenticated user using dynamic auth key in headers.
    """
    if authenticate_with_dynamic_key(username, auth_key, user_type="user"):
        user_info = get_user(username)
        if user_info:
            return {
                "username": username, 
                "auth_method": "auth_key", 
                "user_type": "user",
                "user_info": user_info
            }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "AuthKey"},
    )

def check_redis_connection() -> bool:
    """Check if Redis connection is working."""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False
def get_user_sessions(username: str) -> list:
    """Get all active sessions for a specific user from Redis."""
    try:
        pattern = f"user:sessions:{username}:*"
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
