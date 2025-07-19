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
            data = response.json()
            print(f"Response: {data}")
            
            # Validate response structure (should match HealthResponse schema)
            required_fields = ["status", "service", "version"]
            for field in required_fields:
                if field not in data:
                    print(f"⚠️ Missing field in health response: {field}")
                    return False
            
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


async def test_llm_provider_management():
    """Test LLM provider management endpoints."""
    async with httpx.AsyncClient() as client:
        print(f"\n--- LLM Provider Management ---")
        
        try:
            # Get current provider
            response = await client.get(f"{BASE_URL}/llm/provider")
            print(f"Current provider - Status: {response.status_code}")
            if response.status_code == 200:
                provider_info = response.json()
                print(f"Provider: {json.dumps(provider_info, indent=2)}")
            
            # Get available providers
            response = await client.get(f"{BASE_URL}/llm/providers")
            print(f"Available providers - Status: {response.status_code}")
            if response.status_code == 200:
                providers = response.json()
                print(f"Providers: {json.dumps(providers, indent=2)}")
            
            # Check LLM health
            response = await client.get(f"{BASE_URL}/llm/health")
            print(f"LLM health - Status: {response.status_code}")
            if response.status_code == 200:
                health = response.json()
                print(f"Health: {json.dumps(health, indent=2)}")
            
            return True
            
        except Exception as e:
            print(f"LLM provider management test failed: {e}")
            return False


async def test_provider_override():
    """Test per-request provider override."""
    async with httpx.AsyncClient() as client:
        print(f"\n--- Provider Override Test ---")
        
        session_id = "provider_override_test"
        
        try:
            # Test with default provider
            response = await client.post(
                f"{BASE_URL}/chat/",
                json={
                    "session_id": session_id,
                    "message": "What provider are you using?"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Default provider response:")
                print(f"  Provider: {data.get('llm_provider')}")
                print(f"  Model: {data.get('model')}")
                print(f"  Response: {data['response'][:100]}...")
            
            # Test with provider override (if available)
            providers_response = await client.get(f"{BASE_URL}/llm/providers")
            if providers_response.status_code == 200:
                available_providers = [p["name"] for p in providers_response.json()["providers"]]
                
                # Try to use a different provider if available
                for provider in ["ollama", "chatgroq"]:
                    if provider in available_providers:
                        try:
                            response = await client.post(
                                f"{BASE_URL}/chat/",
                                json={
                                    "session_id": f"{session_id}_{provider}",
                                    "message": "Test with override provider",
                                    "llm_provider": provider
                                },
                                timeout=30.0
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                print(f"\nOverride provider ({provider}) response:")
                                print(f"  Provider: {data.get('llm_provider')}")
                                print(f"  Model: {data.get('model')}")
                                print(f"  Response: {data['response'][:100]}...")
                            break
                        except Exception as e:
                            print(f"  Provider {provider} failed: {e}")
            
            return True
            
        except Exception as e:
            print(f"Provider override test failed: {e}")
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
        ("LLM Provider Management", test_llm_provider_management),
        ("Provider Override", test_provider_override),
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