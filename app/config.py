import os
from dotenv import load_dotenv
from enum import Enum

# Load environment variables from .env file
load_dotenv()

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    CHATGROQ = "chatgroq"

# LLM Provider Selection - ChatGroq only
LLM_PROVIDER = os.getenv("LLM_PROVIDER", LLMProvider.CHATGROQ.value).lower()

# ChatGroq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192")

# Backward compatibility - falls back to GROQ_MODEL_NAME if MODEL_NAME is used
MODEL_NAME = os.getenv("MODEL_NAME", GROQ_MODEL_NAME)

# LLM Configuration
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

# Memory Configuration
MEMORY_TTL_SECONDS = int(os.getenv("MEMORY_TTL_SECONDS", "3600"))  # 1 hour default
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "1000"))  # Max number of sessions

# Authentication Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./chatbot.db")

# FastAPI Configuration
API_TITLE = "ChatGroq Conversational Chatbot API"
API_DESCRIPTION = """
## ChatGroq Conversational Chatbot API with Redis Authentication

A production-ready FastAPI service that provides conversational AI capabilities using ChatGroq with Redis-based admin authentication:

### Features

* **ChatGroq Integration**: High-performance cloud inference with multiple model options
* **Redis Authentication**: Simple admin authentication using Upstash Redis
* **Session-based Conversations**: Maintain conversation history across multiple interactions
* **Admin API**: Comprehensive admin endpoints for credential management and system monitoring
* **TTL Memory Management**: Automatic session expiration with configurable time-to-live
* **Scalable Architecture**: Stateless design suitable for horizontal scaling
* **OpenAI Compatible**: Easy integration with ChatGroq and other OpenAI-compatible APIs
* **Production Ready**: Health checks, logging, error handling, and monitoring

### Authentication

The API uses Redis-based authentication with the following endpoints:

#### Admin Endpoints
- `POST /admin/login` - Login and receive JWT token
- `GET /admin/info` - Get admin account information
- `POST /admin/change-credentials` - Update admin credentials
- `GET /admin/status` - System health and status
- `GET /admin/sessions` - Active admin sessions
- `POST /admin/test-chat` - Test ChatGroq connection

#### Chat Endpoints (Require Authentication)
- `POST /chat/` - Send message to chatbot
- `DELETE /chat/sessions/{session_id}` - Clear conversation session
- `GET /chat/memory/stats` - Memory cache statistics

### LLM Provider

#### ChatGroq (Cloud)
- High-performance cloud inference
- Multiple model options (Llama, Mixtral, etc.)
- No local setup required
- API key authentication

### Redis Configuration

Admin credentials are stored in Upstash Redis using configurable key-value pairs. Default credentials can be set via environment variables.

### Rate Limiting

Please be mindful of API rate limits for ChatGroq cloud services.

### Session Management

Conversations are session-based with configurable memory TTL (Time-To-Live). Each admin's sessions are isolated and maintain conversation history until expiration.

### Usage

1. **Admin Login**: Authenticate via `/admin/login` to receive JWT token
2. **Set Authorization**: Use `Authorization: Bearer <token>` header for chat endpoints
3. **Start Chatting**: Send messages to `/chat/` with session ID
4. **Manage System**: Use admin endpoints to monitor and configure the system
"""

API_VERSION = "1.0.0"
API_CONTACT = {
    "name": "API Support",
    "url": "https://github.com/your-repo/chatgroq-chatbot",
    "email": "support@example.com"
}
API_LICENSE = {
    "name": "MIT",
    "url": "https://opensource.org/licenses/MIT"
}

# Swagger UI Configuration
SWAGGER_UI_PARAMETERS = {
    "deepLinking": True,
    "displayRequestDuration": True,
    "docExpansion": "list",
    "operationsSorter": "method",
    "showExtensions": True,
    "showCommonExtensions": True,
    "tryItOutEnabled": True
}

# API Tags for endpoint organization
API_TAGS_METADATA = [
    {
        "name": "admin",
        "description": "Admin authentication and system management endpoints"
    },
    {
        "name": "chat",
        "description": "Conversational endpoints for chatbot interactions using ChatGroq (requires authentication)",
        "externalDocs": {
            "description": "ChatGroq API Documentation",
            "url": "https://console.groq.com/docs/quickstart"
        }
    },
    {
        "name": "llm",
        "description": "LLM provider management and information endpoints"
    },
    {
        "name": "health",
        "description": "Health check and system status endpoints"
    },
    {
        "name": "memory",
        "description": "Session memory management and statistics"
    }
]