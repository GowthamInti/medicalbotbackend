from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.auth.database import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model with additional fields."""
    __tablename__ = "user"
    
    # Additional user fields
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Subscription/Usage tracking
    is_premium = Column(Boolean, default=False)
    total_messages = Column(String, default="0")
    
    def __repr__(self):
        return f"<User {self.email}>"