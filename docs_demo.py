#!/usr/bin/env python3
"""
Demo script showing how to interact with the ChatGroq Chatbot API
and explore its comprehensive Swagger documentation features.
"""

import asyncio
import httpx
import webbrowser
import time
from typing import List, Dict

BASE_URL = "http://localhost:8000"

def open_documentation():
    """Open the API documentation in browser."""
    print("🚀 Opening API Documentation...")
    print(f"Swagger UI: {BASE_URL}/docs")
    print(f"ReDoc: {BASE_URL}/redoc")
    print(f"OpenAPI JSON: {BASE_URL}/openapi.json")
    
    # Open in browser
    webbrowser.open(f"{BASE_URL}/docs")


async def demonstrate_api_features():
    """Demonstrate various API features with examples from Swagger docs."""
    
    print("\n📚 API Feature Demonstration")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # 1. Health Check
        print("\n1️⃣ Health Check")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"✅ Status: {response.status_code}")
            print(f"📋 Response: {response.json()}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
        
        # 2. API Information
        print("\n2️⃣ API Information")
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"✅ Status: {response.status_code}")
            print(f"📋 Response: {response.json()}")
        except Exception as e:
            print(f"❌ API info failed: {e}")
        
        # 3. Memory Statistics
        print("\n3️⃣ Memory Statistics")
        try:
            response = await client.get(f"{BASE_URL}/chat/stats")
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Memory Stats: {response.json()}")
        except Exception as e:
            print(f"❌ Memory stats failed: {e}")
        
        # 4. Chat Examples (from Swagger docs)
        print("\n4️⃣ Chat Examples")
        
        # Example conversations from the enhanced Swagger docs
        examples = [
            {
                "name": "Simple Greeting",
                "session_id": "demo_user_001",
                "message": "Hello! I'm testing the API documentation."
            },
            {
                "name": "Technical Question",
                "session_id": "demo_dev_session",
                "message": "Can you explain the difference between REST and GraphQL APIs?"
            },
            {
                "name": "Coding Help",
                "session_id": "demo_coding_session",
                "message": "Help me write a Python function to calculate fibonacci numbers"
            }
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"\n   📝 Example {i}: {example['name']}")
            try:
                response = await client.post(
                    f"{BASE_URL}/chat/",
                    json={
                        "session_id": example["session_id"],
                        "message": example["message"]
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   👤 User: {example['message']}")
                    print(f"   🤖 Bot: {data['response'][:150]}...")
                else:
                    print(f"   ❌ Error: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ Request failed: {e}")
            
            # Small delay between requests
            await asyncio.sleep(1)
        
        # 5. Session Management Demo
        print("\n5️⃣ Session Management")
        test_session = "demo_session_clear"
        
        # Create a session
        await client.post(
            f"{BASE_URL}/chat/",
            json={
                "session_id": test_session,
                "message": "Remember this test message"
            }
        )
        print(f"   📝 Created session: {test_session}")
        
        # Clear the session
        try:
            response = await client.delete(f"{BASE_URL}/chat/session/{test_session}")
            print(f"   🗑️ Clear result: {response.json()}")
        except Exception as e:
            print(f"   ❌ Clear failed: {e}")
        
        return True


def print_swagger_features():
    """Print information about the enhanced Swagger features."""
    
    print("\n🎯 Enhanced Swagger Documentation Features")
    print("=" * 50)
    
    features = [
        "📖 Comprehensive API descriptions with markdown formatting",
        "🔍 Multiple request/response examples for each endpoint",
        "🏷️ Organized endpoints with tags (chat, memory, health)",
        "✅ Detailed HTTP status code documentation",
        "🛡️ Security and authentication information",
        "📊 Schema validation with real-time feedback",
        "🎮 Interactive 'Try it out' functionality",
        "📋 Copy-paste ready cURL commands",
        "🔗 External documentation links",
        "💡 Performance and scaling guidelines"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print(f"\n🌐 Access the documentation at:")
    print(f"  • Swagger UI: {BASE_URL}/docs")
    print(f"  • ReDoc: {BASE_URL}/redoc")
    print(f"  • OpenAPI JSON: {BASE_URL}/openapi.json")


def print_api_testing_guide():
    """Print a guide for testing the API using Swagger UI."""
    
    print("\n🧪 API Testing Guide using Swagger UI")
    print("=" * 50)
    
    steps = [
        "1. Open http://localhost:8000/docs in your browser",
        "2. Explore the organized endpoint groups (chat, memory, health)",
        "3. Click on any endpoint to see detailed documentation",
        "4. Use 'Try it out' to test endpoints interactively",
        "5. Modify the example payloads to test different scenarios",
        "6. Check response codes and example responses",
        "7. Copy the generated cURL commands for external testing",
        "8. Monitor memory usage with /chat/stats endpoint",
        "9. Test session management with different session IDs",
        "10. Explore error responses by sending invalid data"
    ]
    
    for step in steps:
        print(f"  {step}")


async def main():
    """Main demo function."""
    
    print("🎉 ChatGroq Chatbot API - Swagger Documentation Demo")
    print("=" * 60)
    
    # Print feature overview
    print_swagger_features()
    
    # Print testing guide
    print_api_testing_guide()
    
    # Open documentation
    print("\n" + "=" * 60)
    choice = input("Would you like to open the Swagger documentation? (y/n): ").lower()
    if choice == 'y':
        open_documentation()
        time.sleep(2)  # Give browser time to open
    
    # Run API demonstration
    print("\n" + "=" * 60)
    choice = input("Would you like to run the API demonstration? (y/n): ").lower()
    if choice == 'y':
        success = await demonstrate_api_features()
        if success:
            print("\n✅ API demonstration completed successfully!")
            print("💡 Now try exploring the interactive Swagger UI at /docs")
        else:
            print("\n❌ Make sure the server is running: uvicorn app.main:app --reload")
    
    print("\n🎯 Next Steps:")
    print("  1. Explore the interactive Swagger UI at /docs")
    print("  2. Try different API endpoints and parameters")
    print("  3. Test various conversation scenarios")
    print("  4. Monitor system performance with /chat/stats")
    print("  5. Integrate the API into your applications")


if __name__ == "__main__":
    asyncio.run(main())