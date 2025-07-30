from fastapi import APIRouter
from app.auth.config import fastapi_users, jwt_backend, cookie_backend
from app.auth.schemas import UserRead, UserCreate, UserUpdate

router = APIRouter()

# Include authentication routes
router.include_router(
    fastapi_users.get_auth_router(jwt_backend), 
    prefix="/jwt", 
    tags=["auth"]
)

router.include_router(
    fastapi_users.get_auth_router(cookie_backend), 
    prefix="/cookie", 
    tags=["auth"]
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)