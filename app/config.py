import os
from dotenv import load_dotenv
from enum import Enum

# Load environment variables from .env file
load_dotenv()

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    CHATGROQ = "chatgroq"
    OLLAMA = "ollama"

# LLM Provider Selection
LLM_PROVIDER = os.getenv("LLM_PROVIDER", LLMProvider.CHATGROQ.value).lower()

# ChatGroq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192")

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")

# Backward compatibility - falls back to GROQ_MODEL_NAME if MODEL_NAME is used
MODEL_NAME = os.getenv("MODEL_NAME", GROQ_MODEL_NAME)

# LLM Configuration
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

# Memory Configuration
MEMORY_TTL_SECONDS = int(os.getenv("MEMORY_TTL_SECONDS", "3600"))  # 1 hour default
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "1000"))  # Max number of sessions

# FastAPI Configuration
API_TITLE = "ChatGroq & Llama Conversational Chatbot"
API_DESCRIPTION = """
## ChatGroq & Llama Conversational Chatbot API

A production-ready FastAPI service that provides conversational AI capabilities using multiple LLM providers:
- **ChatGroq API** for cloud-based inference
- **Ollama** for local Llama model hosting

### Features

* **Multi-Provider Support**: Switch between ChatGroq and local Llama models at runtime
* **Session-based Conversations**: Maintain conversation history across multiple interactions
* **TTL Memory Management**: Automatic session expiration with configurable time-to-live
* **Scalable Architecture**: Stateless design suitable for horizontal scaling
* **OpenAI Compatible**: Easy integration with ChatGroq and other OpenAI-compatible APIs
* **Local Model Support**: Run Llama models locally using Ollama for privacy and control
* **Production Ready**: Health checks, logging, error handling, and monitoring

### LLM Providers

#### ChatGroq (Cloud)
- High-performance cloud inference
- Multiple model options (Llama, Mixtral, etc.)
- No local setup required
- API key authentication

#### Ollama (Local)
- Local Llama model hosting
- Privacy and data control
- No internet dependency
- GPU acceleration support

### Provider Selection

Configure the LLM provider using the `LLM_PROVIDER` environment variable:
- `chatgroq` - Use ChatGroq cloud API (default)
- `ollama` - Use local Ollama server

### Authentication

- **ChatGroq**: Requires a valid API key configured server-side
- **Ollama**: No authentication required for local deployment

### Rate Limiting

Please be mindful of API rate limits for cloud providers. Local Ollama deployments have no rate limits but depend on hardware capabilities.

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
        "description": "Conversational endpoints for chatbot interactions with multiple LLM providers",
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