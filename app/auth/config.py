from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTAuthentication,
    CookieTransport,
)
from app.auth.manager import get_user_manager
from app.auth.models import User
import os

SECRET = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# Bearer token transport (for API access)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# JWT authentication backend
jwt_authentication = JWTAuthentication(
    secret=SECRET,
    lifetime_seconds=3600,  # 1 hour
    tokenUrl="auth/jwt/login",
)

# Cookie transport (for web interface)
cookie_transport = CookieTransport(cookie_max_age=3600)

# Authentication backends
jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=lambda: jwt_authentication,
)

cookie_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=lambda: jwt_authentication,
)

# FastAPI Users instance
import uuid
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [jwt_backend, cookie_backend])

# Dependencies
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)