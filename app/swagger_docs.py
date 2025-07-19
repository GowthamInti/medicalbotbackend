"""
Advanced Swagger/OpenAPI documentation customization for the ChatGroq Chatbot API.
This module contains additional documentation, examples, and custom schemas.
"""

from typing import Dict, Any

# Custom OpenAPI schema additions
CUSTOM_OPENAPI_SCHEMA: Dict[str, Any] = {
    "info": {
        "x-logo": {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
            "altText": "ChatGroq Chatbot API"
        }
    },
    "servers": [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production server"
        }
    ]
}

# Additional examples for different use cases
CHAT_EXAMPLES = {
    "simple_greeting": {
        "summary": "Simple greeting",
        "description": "A basic hello message to start a conversation",
        "value": {
            "session_id": "user_001",
            "message": "Hello!"
        }
    },
    "technical_question": {
        "summary": "Technical question",
        "description": "Asking about a technical topic",
        "value": {
            "session_id": "dev_session_123",
            "message": "Can you explain the difference between REST and GraphQL APIs?"
        }
    },
    "coding_help": {
        "summary": "Coding assistance",
        "description": "Requesting help with programming",
        "value": {
            "session_id": "coding_session",
            "message": "Help me write a Python function to calculate fibonacci numbers"
        }
    },
    "follow_up": {
        "summary": "Follow-up question",
        "description": "Continuing a previous conversation",
        "value": {
            "session_id": "user_001",
            "message": "Can you explain that in more detail?"
        }
    },
    "creative_writing": {
        "summary": "Creative writing request",
        "description": "Asking for creative content",
        "value": {
            "session_id": "creative_session",
            "message": "Write a short story about a robot learning to paint"
        }
    }
}

# Response examples for different scenarios
CHAT_RESPONSE_EXAMPLES = {
    "greeting_response": {
        "summary": "Greeting response",
        "description": "AI response to a greeting",
        "value": {
            "response": "Hello! I'm an AI assistant powered by ChatGroq. I'm here to help you with questions, provide information, assist with coding, creative writing, and much more. What would you like to talk about today?",
            "session_id": "user_001"
        }
    },
    "technical_response": {
        "summary": "Technical explanation",
        "description": "Detailed technical response",
        "value": {
            "response": "REST and GraphQL are both API architectural styles, but they differ significantly:\n\n**REST (Representational State Transfer):**\n- Uses standard HTTP methods (GET, POST, PUT, DELETE)\n- Resource-based URLs\n- Multiple endpoints for different resources\n- Over-fetching/under-fetching can be common\n\n**GraphQL:**\n- Single endpoint\n- Query language for APIs\n- Client specifies exactly what data is needed\n- Strongly typed schema\n- Better for complex data requirements\n\nWould you like me to elaborate on any specific aspect?",
            "session_id": "dev_session_123"
        }
    },
    "code_response": {
        "summary": "Code assistance",
        "description": "Programming help with code examples",
        "value": {
            "response": "Here's a Python function to calculate Fibonacci numbers:\n\n```python\ndef fibonacci(n):\n    \"\"\"Calculate the nth Fibonacci number.\"\"\"\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\n# More efficient iterative version:\ndef fibonacci_iterative(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n```\n\nThe iterative version is more efficient for larger numbers. Would you like me to explain how it works?",
            "session_id": "coding_session"
        }
    }
}

# Error response examples
ERROR_EXAMPLES = {
    "validation_error": {
        "summary": "Validation error",
        "description": "Request validation failed",
        "value": {
            "detail": [
                {
                    "loc": ["body", "message"],
                    "msg": "ensure this value has at least 1 characters",
                    "type": "value_error.any_str.min_length",
                    "ctx": {"limit_value": 1}
                }
            ]
        }
    },
    "empty_message": {
        "summary": "Empty message error",
        "description": "Message field cannot be empty",
        "value": {
            "detail": "Invalid request: message cannot be empty"
        }
    },
    "invalid_session_id": {
        "summary": "Invalid session ID",
        "description": "Session ID contains invalid characters",
        "value": {
            "detail": "Invalid request: session_id must contain only alphanumeric characters, underscores, and hyphens"
        }
    },
    "service_error": {
        "summary": "Service unavailable",
        "description": "Internal service error",
        "value": {
            "detail": "An error occurred while processing your request"
        }
    }
}

# Memory statistics examples
MEMORY_STATS_EXAMPLES = {
    "low_usage": {
        "summary": "Low memory usage",
        "description": "System with low session count",
        "value": {
            "memory_stats": {
                "current_size": 15,
                "max_size": 1000,
                "ttl_seconds": 3600
            }
        }
    },
    "high_usage": {
        "summary": "High memory usage",
        "description": "System approaching capacity",
        "value": {
            "memory_stats": {
                "current_size": 850,
                "max_size": 1000,
                "ttl_seconds": 3600
            }
        }
    },
    "empty_cache": {
        "summary": "Empty cache",
        "description": "No active sessions",
        "value": {
            "memory_stats": {
                "current_size": 0,
                "max_size": 1000,
                "ttl_seconds": 3600
            }
        }
    }
}

# Security considerations for documentation
SECURITY_NOTES = """
## Security Considerations

### API Key Management
- ChatGroq API keys are managed server-side
- No client-side API key exposure
- Keys should be rotated regularly

### Session Security
- Session IDs should not contain sensitive information
- Sessions automatically expire after TTL
- No persistent storage of conversation data

### Rate Limiting
- Implement rate limiting in production
- Monitor API usage patterns
- Set appropriate timeouts

### Data Privacy
- Conversations are ephemeral (TTL-based)
- No permanent storage of user messages
- Consider data retention policies
"""

# Performance notes
PERFORMANCE_NOTES = """
## Performance Considerations

### Memory Management
- TTL-based session expiration prevents memory leaks
- Configurable cache size limits
- Monitor memory usage with `/chat/stats`

### Scaling
- Stateless design enables horizontal scaling
- Consider Redis for persistent sessions in multi-instance deployments
- Load balance across multiple instances

### Optimization
- Adjust TTL based on usage patterns
- Monitor response times
- Consider caching frequently asked questions
"""