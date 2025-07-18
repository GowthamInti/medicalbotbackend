---
title: {{title}}
emoji: {{emoji}}
colorFrom: {{colorFrom}}
colorTo: {{colorTo}}
sdk: {{sdk}}
sdk_version: "{{sdkVersion}}"
app_file: app.py
pinned: false
---

# ChatGroq Conversational Chatbot

A FastAPI-based conversational chatbot service using the ChatGroq API (OpenAI-compatible) for LLM inference. This repository is designed with a modular architecture that separates routing, language model logic, session memory, and request schema validation for clean extensibility and maintainability.

## Features

- **Modular Architecture**: Clean separation of concerns across different modules
- **Session-based Memory**: TTL-based in-memory caching for conversation history
- **Stateless & Scalable**: Designed for horizontal scaling with ephemeral memory
- **Schema Validation**: Automatic request/response validation using Pydantic
- **OpenAI-Compatible**: Easy to swap between ChatGroq and other OpenAI-compatible APIs
- **Production Ready**: Includes health checks, logging, and CORS support
- **Comprehensive Documentation**: Enhanced Swagger/OpenAPI docs with examples and detailed descriptions
- **Interactive API Testing**: Built-in Swagger UI for testing all endpoints

## Architecture Overview

```
app/
├── main.py              # FastAPI entry point
├── config.py            # Configuration management
├── llm.py              # LLM service (ChatGroq integration)
├── memory.py           # Session memory management
├── routes/
│   └── chat.py         # Chat endpoints
└── schemas/
    └── chat.py         # Pydantic models
```

### Module Details

- **`app/main.py`**: Entry point for the FastAPI app with router inclusion
- **`app/routes/chat.py`**: Chat endpoint handling with session management
- **`app/schemas/chat.py`**: Pydantic models for request/response validation
- **`app/llm.py`**: LangChain ChatOpenAI interface for ChatGroq API
- **`app/memory.py`**: TTL-based session memory using cachetools
- **`app/config.py`**: Centralized configuration from environment variables

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd chatgroq-chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your ChatGroq API key and other configurations
   ```

## Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your ChatGroq API key | Required |
| `GROQ_BASE_URL` | ChatGroq API base URL | `https://api.groq.com/openai/v1` |
| `MODEL_NAME` | LLM model to use | `llama3-8b-8192` |
| `TEMPERATURE` | LLM temperature setting | `0.7` |
| `MAX_TOKENS` | Maximum tokens per response | `1024` |
| `MEMORY_TTL_SECONDS` | Session memory TTL | `3600` (1 hour) |
| `MAX_CACHE_SIZE` | Maximum cached sessions | `1000` |

## Usage

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with comprehensive documentation:

- **Swagger UI**: `http://localhost:8000/docs` - Interactive API documentation
- **ReDoc**: `http://localhost:8000/redoc` - Alternative documentation view
- **OpenAPI JSON**: `http://localhost:8000/openapi.json` - Machine-readable API schema

### API Endpoints

#### POST `/chat/`
Send a message to the chatbot with session tracking.

**Request:**
```json
{
  "session_id": "user123_session",
  "message": "Hello, how are you today?"
}
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "session_id": "user123_session"
}
```

#### DELETE `/chat/session/{session_id}`
Clear memory for a specific session.

#### GET `/chat/stats`
Get memory cache statistics.

#### GET `/health`
Health check endpoint.

### Example Usage with cURL

```bash
# Send a chat message
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_1",
    "message": "What is artificial intelligence?"
  }'

# Clear a session
curl -X DELETE "http://localhost:8000/chat/session/test_session_1"

# Get memory statistics
curl "http://localhost:8000/chat/stats"
```

### Example Usage with Python

```python
import httpx

async def chat_example():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat/",
            json={
                "session_id": "python_session",
                "message": "Explain quantum computing in simple terms"
            }
        )
        print(response.json())
```

## API Documentation

The service includes comprehensive Swagger/OpenAPI documentation with:

### **Enhanced Swagger UI Features**
- **Interactive Testing**: Test all endpoints directly from the browser
- **Detailed Examples**: Multiple request/response examples for each endpoint
- **Schema Validation**: Real-time validation of request payloads
- **Response Codes**: Complete documentation of all possible response codes
- **Authentication Info**: Clear documentation of API security requirements

### **Documentation URLs**
- **Swagger UI**: `/docs` - Interactive API documentation and testing
- **ReDoc**: `/redoc` - Clean, alternative documentation view
- **OpenAPI JSON**: `/openapi.json` - Machine-readable API specification

### **Advanced Features**
- **Organized by Tags**: Endpoints grouped logically (chat, memory, health)
- **Rich Examples**: Real-world usage examples for different scenarios
- **Error Documentation**: Comprehensive error response examples
- **Performance Notes**: Guidelines for optimization and scaling

## Memory Management

The service uses TTL-based in-memory caching for session management:

- **Session Isolation**: Each session maintains its own conversation history
- **Automatic Expiry**: Sessions expire after the configured TTL period
- **Memory Limits**: Maximum number of concurrent sessions is configurable
- **Stateless Design**: No persistent storage, suitable for microservice architectures

## Extending the Service

### Switching to Different LLM Providers

To switch from ChatGroq to another provider (e.g., Ollama), modify only `app/llm.py`:

```python
# For Ollama
from langchain_community.llms import Ollama

class LLMService:
    def __init__(self):
        self.llm = Ollama(model="llama2")
```

### Adding New Endpoints

1. Create new route files in `app/routes/`
2. Define Pydantic models in `app/schemas/`
3. Include the router in `app/main.py`

### Custom Memory Backends

Extend `app/memory.py` to support persistent storage:

```python
class PersistentMemoryService(MemoryService):
    def __init__(self, redis_client):
        self.redis = redis_client
        # Implementation for Redis-based memory
```

## Production Deployment

### Environment Variables for Production

```bash
# Use a secure GROQ API key
GROQ_API_KEY=gsk_your_production_key

# Adjust memory settings based on expected load
MEMORY_TTL_SECONDS=7200
MAX_CACHE_SIZE=5000

# Model optimization
TEMPERATURE=0.5
MAX_TOKENS=512
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY .env .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Health Monitoring

The service includes health endpoints for monitoring:
- `/health`: Basic health check
- `/chat/stats`: Memory usage statistics

## License

[Your License Here]