"""
Simple test script for the ChatGroq conversational chatbot.
Run this after starting the server to test basic functionality.
"""

import asyncio
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Test the health check endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"Health Check: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False


async def test_chat_conversation():
    """Test a multi-turn conversation."""
    session_id = "test_session_123"
    
    messages = [
        "Hello! What's your name?",
        "Can you explain what artificial intelligence is?",
        "What did I ask you about in my previous message?",
    ]
    
    async with httpx.AsyncClient() as client:
        print(f"\n--- Testing conversation for session: {session_id} ---")
        
        for i, message in enumerate(messages, 1):
            try:
                response = await client.post(
                    f"{BASE_URL}/chat/",
                    json={
                        "session_id": session_id,
                        "message": message
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"\nTurn {i}:")
                    print(f"User: {message}")
                    print(f"Bot: {data['response']}")
                else:
                    print(f"Error {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"Request failed: {e}")
                return False
        
        return True


async def test_memory_stats():
    """Test memory statistics endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/chat/stats")
            print(f"\n--- Memory Statistics ---")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                stats = response.json()
                print(f"Stats: {json.dumps(stats, indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"Memory stats failed: {e}")
            return False


async def test_session_clear():
    """Test session clearing functionality."""
    session_id = "test_clear_session"
    
    async with httpx.AsyncClient() as client:
        # First, create a session with a message
        await client.post(
            f"{BASE_URL}/chat/",
            json={
                "session_id": session_id,
                "message": "Remember this message"
            }
        )
        
        # Clear the session
        try:
            response = await client.delete(f"{BASE_URL}/chat/session/{session_id}")
            print(f"\n--- Session Clear Test ---")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Session clear failed: {e}")
            return False


async def test_error_handling():
    """Test error handling with invalid requests."""
    async with httpx.AsyncClient() as client:
        print(f"\n--- Error Handling Tests ---")
        
        # Test empty message
        try:
            response = await client.post(
                f"{BASE_URL}/chat/",
                json={
                    "session_id": "test_session",
                    "message": ""
                }
            )
            print(f"Empty message test - Status: {response.status_code}")
            
        except Exception as e:
            print(f"Empty message test failed: {e}")
        
        # Test missing session_id
        try:
            response = await client.post(
                f"{BASE_URL}/chat/",
                json={
                    "message": "Hello without session"
                }
            )
            print(f"Missing session_id test - Status: {response.status_code}")
            
        except Exception as e:
            print(f"Missing session_id test failed: {e}")


async def main():
    """Run all tests."""
    print("🚀 Starting ChatGroq Chatbot Tests")
    print("=" * 50)
    
    # Test health check first
    health_ok = await test_health_check()
    if not health_ok:
        print("❌ Health check failed. Make sure the server is running.")
        return
    
    # Run all tests
    tests = [
        ("Chat Conversation", test_chat_conversation),
        ("Memory Statistics", test_memory_stats),
        ("Session Clear", test_session_clear),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ {test_name}: FAILED ({e})")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")


if __name__ == "__main__":
    asyncio.run(main())