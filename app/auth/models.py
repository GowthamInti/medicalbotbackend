from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String, Boolean, DateTime, Text, Index
from sqlalchemy.sql import func
from app.auth.database import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model optimized for Upstash PostgreSQL."""
    __tablename__ = "users"
    
    # Additional user fields
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Timestamps with timezone support
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Subscription/Usage tracking
    is_premium = Column(Boolean, default=False, nullable=False)
    total_messages = Column(String(20), default="0", nullable=False)  # Using String to avoid integer overflow
    
    # Add database indexes for better performance on Upstash
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_is_active', 'is_active'),
        Index('idx_users_is_premium', 'is_premium'),
        Index('idx_users_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.email
    
    def increment_message_count(self) -> None:
        """Increment the user's message count."""
        try:
            current_count = int(self.total_messages)
            self.total_messages = str(current_count + 1)
        except (ValueError, TypeError):
            self.total_messages = "1"