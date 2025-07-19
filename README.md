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

A FastAPI-based conversational chatbot service supporting multiple LLM providers including ChatGroq API and local Ollama hosting. This repository is designed with a modular architecture that separates routing, language model logic, session memory, and request schema validation for clean extensibility and maintainability.

## Features

- **Multi-Provider Support**: Switch between ChatGroq (cloud) and Ollama (local) at runtime
- **Modular Architecture**: Clean separation of concerns across different modules
- **Session-based Memory**: TTL-based in-memory caching for conversation history
- **Stateless & Scalable**: Designed for horizontal scaling with ephemeral memory
- **Schema Validation**: Automatic request/response validation using Pydantic
- **OpenAI-Compatible**: Easy integration with multiple LLM providers
- **Local Model Support**: Run Llama models locally using Ollama for privacy and control
- **Runtime Provider Switching**: Change LLM providers without restarting the service
- **Production Ready**: Includes health checks, logging, and CORS support
- **Comprehensive Documentation**: Enhanced Swagger/OpenAPI docs with examples and detailed descriptions
- **Interactive API Testing**: Built-in Swagger UI for testing all endpoints

## Architecture Overview

```
app/
├── main.py              # FastAPI entry point
├── config.py            # Configuration management
├── llm.py              # Multi-provider LLM service (ChatGroq & Ollama)
├── memory.py           # Session memory management
├── routes/
│   ├── chat.py         # Chat endpoints
│   └── llm.py          # LLM provider management endpoints
└── schemas/
    └── chat.py         # Pydantic models
```

### Module Details

- **`app/main.py`**: Entry point for the FastAPI app with router inclusion
- **`app/routes/chat.py`**: Chat endpoint handling with session management
- **`app/routes/llm.py`**: LLM provider management and switching endpoints
- **`app/schemas/chat.py`**: Pydantic models for request/response validation
- **`app/llm.py`**: Multi-provider LLM service supporting ChatGroq and Ollama
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
   # Edit .env with your configuration
   ```

4. **Configure LLM Provider**:
   
   **For Ollama (default - local hosting):**
   ```bash
   # Default configuration in .env
   LLM_PROVIDER=ollama
   OLLAMA_MODEL_NAME=llama3.2:1b
   
   # Ollama will be automatically started with Docker Compose
   ```
   
   **For ChatGroq (cloud API):**
   ```bash
   # Set your ChatGroq API key in .env
   GROQ_API_KEY=your_api_key_here
   LLM_PROVIDER=chatgroq
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

### LLM Provider Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Active LLM provider (`ollama` or `chatgroq`) | `ollama` |
| `GROQ_MODEL_NAME` | ChatGroq model name | `llama3-8b-8192` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL_NAME` | Ollama model name | `llama3.2:1b` |

## Usage

### Running the Server

#### Option 1: Docker Compose (Recommended)

```bash
# Quick start with default Ollama setup
./start.sh

# Or manually with docker-compose
docker-compose --profile ollama up --build -d
```

#### Option 2: Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with comprehensive documentation:

- **Swagger UI**: `http://localhost:8000/docs` - Interactive API documentation
- **ReDoc**: `http://localhost:8000/redoc` - Alternative documentation view
- **OpenAPI JSON**: `http://localhost:8000/openapi.json` - Machine-readable API schema

### Docker Deployment

#### Quick Start Scripts
```bash
# Automatic startup (detects provider from .env)
./start.sh

# Stop all services
./stop.sh

# Stop with volume cleanup (removes Ollama models)
./stop.sh --clean-volumes
```

#### Manual Docker Compose Commands
```bash
# Start with Ollama (default setup)
docker-compose --profile ollama up --build -d

# Start with ChatGroq only (no Ollama)
docker-compose up chatbot --build -d

# Production deployment
ENVIRONMENT=production docker-compose -f docker-compose.prod.yml --profile ollama up -d
```

#### Monitoring & Troubleshooting
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker logs -f chatbot-ollama
docker logs -f chatbot-api

# Check container status
docker ps -a --filter "name=chatbot"

# Monitor Ollama model download progress
docker logs -f chatbot-ollama-setup
```

#### Service Configuration

The Docker setup automatically:
- **Starts Ollama** when `LLM_PROVIDER=ollama` is configured
- **Downloads llama3.2:1b model** (1GB) on first startup
- **Configures networking** between services
- **Handles health checks** and service dependencies
- **Provides persistent storage** for Ollama models

### API Endpoints

#### Chat Endpoints

##### POST `/chat/`
Send a message to the chatbot with session tracking.

**Request:**
```json
{
  "session_id": "user123_session",
  "message": "Hello, how are you today?",
  "llm_provider": "ollama"
}
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "session_id": "user123_session",
  "llm_provider": "ollama",
  "model": "llama3"
}
```

##### DELETE `/chat/session/{session_id}`
Clear memory for a specific session.

##### GET `/chat/stats`
Get memory cache statistics.

#### LLM Provider Management

##### GET `/llm/provider`
Get current LLM provider information.

##### GET `/llm/providers`
List all available LLM providers.

##### POST `/llm/switch`
Switch LLM provider at runtime.

**Request:**
```json
{
  "provider": "ollama"
}
```

##### GET `/llm/health`
Check current LLM provider health.

#### System Endpoints

##### GET `/health`
Health check endpoint with LLM status.

##### GET `/`
API information and current provider.

### Example Usage with cURL

```bash
# Send a chat message (uses default provider)
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_1",
    "message": "What is artificial intelligence?"
  }'

# Send a message with specific provider
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_1",
    "message": "Explain quantum computing",
    "llm_provider": "ollama"
  }'

# Switch global LLM provider
curl -X POST "http://localhost:8000/llm/switch" \
  -H "Content-Type: application/json" \
  -d '{"provider": "ollama"}'

# Get current provider info
curl "http://localhost:8000/llm/provider"

# Check LLM health
curl "http://localhost:8000/llm/health"

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