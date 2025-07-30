#!/usr/bin/env python3
"""
Script to create a superuser for the ChatGroq Chatbot API.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth.database import create_db_and_tables, get_async_session
from app.auth.manager import get_user_manager
from app.auth.schemas import UserCreate
from app.auth.models import User

async def create_superuser():
    """Create a superuser."""
    await create_db_and_tables()
    
    email = input("Enter superuser email: ")
    password = input("Enter superuser password: ")
    first_name = input("Enter first name (optional): ") or None
    last_name = input("Enter last name (optional): ") or None
    
    user_create = UserCreate(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_superuser=True,
        is_verified=True
    )
    
    async for session in get_async_session():
        async for user_manager in get_user_manager(session):
            try:
                user = await user_manager.create(user_create)
                print(f"Superuser created successfully!")
                print(f"Email: {user.email}")
                print(f"ID: {user.id}")
                return user
            except Exception as e:
                print(f"Error creating superuser: {e}")
                return None

if __name__ == "__main__":
    asyncio.run(create_superuser())