import uuid
from typing import Optional
from fastapi_users import schemas
from pydantic import Field

class UserRead(schemas.BaseUser[uuid.UUID]):
    """Schema for reading user data."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    is_premium: bool = False
    total_messages: str = "0"

class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)

class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data."""
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    is_premium: Optional[bool] = None