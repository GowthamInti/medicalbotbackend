import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ChatGroq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3-8b-8192")

# LLM Configuration
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

# Memory Configuration
MEMORY_TTL_SECONDS = int(os.getenv("MEMORY_TTL_SECONDS", "3600"))  # 1 hour default
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "1000"))  # Max number of sessions

# FastAPI Configuration
API_TITLE = "ChatGroq Conversational Chatbot"
API_DESCRIPTION = """
## ChatGroq Conversational Chatbot API

A production-ready FastAPI service that provides conversational AI capabilities using the ChatGroq API.

### Features

* **Session-based Conversations**: Maintain conversation history across multiple interactions
* **TTL Memory Management**: Automatic session expiration with configurable time-to-live
* **Scalable Architecture**: Stateless design suitable for horizontal scaling
* **OpenAI Compatible**: Easy integration with ChatGroq and other OpenAI-compatible APIs
* **Production Ready**: Health checks, logging, error handling, and monitoring

### Authentication

This API requires a valid ChatGroq API key configured on the server side.

### Rate Limiting

Please be mindful of API rate limits. The service includes built-in retry mechanisms for transient failures.

### Session Management

Sessions automatically expire after the configured TTL period (default: 1 hour).
You can manually clear sessions using the DELETE endpoint.
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
        "name": "chat",
        "description": "Conversational endpoints for chatbot interactions",
        "externalDocs": {
            "description": "ChatGroq API Documentation",
            "url": "https://console.groq.com/docs/quickstart"
        }
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