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

A FastAPI-based conversational chatbot service powered by ChatGroq's high-performance cloud API. This repository is designed with a modular architecture that separates routing, language model logic, session memory, and request schema validation for clean extensibility and maintainability.

## Features

- **ChatGroq Integration**: High-performance cloud inference with multiple model options
- **Modular Architecture**: Clean separation of concerns across different modules
- **Session-based Memory**: TTL-based in-memory caching for conversation history
- **Stateless & Scalable**: Designed for horizontal scaling with ephemeral memory
- **Schema Validation**: Automatic request/response validation using Pydantic
- **OpenAI-Compatible**: Easy integration with ChatGroq API
- **Production Ready**: Includes health checks, logging, and CORS support
- **Comprehensive Documentation**: Enhanced Swagger/OpenAPI docs with examples and detailed descriptions
- **Interactive API Testing**: Built-in Swagger UI for testing all endpoints

## Architecture Overview

```
app/
├── main.py              # FastAPI entry point
├── config.py            # Configuration management
├── llm.py              # ChatGroq LLM service
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
- **`app/routes/llm.py`**: LLM provider management and information endpoints
- **`app/schemas/chat.py`**: Pydantic models for request/response validation
- **`app/llm.py`**: ChatGroq LLM service integration
- **`app/memory.py`**: TTL-based session memory management
- **`app/config.py`**: Centralized configuration management

## Quick Start

### Prerequisites

- Python 3.11+
- ChatGroq API key
- Docker & Docker Compose (optional)

### Environment Setup

**For ChatGroq (cloud hosting):**

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional customization
LLM_PROVIDER=chatgroq
GROQ_MODEL_NAME=llama3-8b-8192
TEMPERATURE=0.7
MAX_TOKENS=1024
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | ChatGroq API key (required) | None |
| `LLM_PROVIDER` | LLM provider (always chatgroq) | `chatgroq` |
| `GROQ_BASE_URL` | ChatGroq API base URL | `https://api.groq.com/openai/v1` |
| `GROQ_MODEL_NAME` | ChatGroq model name | `llama3-8b-8192` |
| `TEMPERATURE` | LLM temperature (0.0-2.0) | `0.7` |
| `MAX_TOKENS` | Maximum response tokens | `1024` |
| `MEMORY_TTL_SECONDS` | Session memory TTL | `3600` (1 hour) |
| `MAX_CACHE_SIZE` | Maximum cached sessions | `1000` |

## Installation & Deployment

### Docker Deployment (Recommended)

```bash
# Quick start with ChatGroq
docker-compose up --build -d

# Production deployment
ENVIRONMENT=production docker-compose -f docker-compose.prod.yml up -d
```

### Local Development

```bash
# 1. Clone and install dependencies
git clone <repository-url>
cd chatgroq-chatbot
pip install -r requirements.txt

# 2. Set environment variables
export GROQ_API_KEY="your_api_key_here"

# 3. Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Access the API
# - API Documentation: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
```

### Production Features

The deployment includes:
- **Production-ready configuration** with optimized settings
- **Health checks** for monitoring and load balancers
- **Comprehensive logging** for debugging and monitoring
- **CORS support** for web applications
- **Persistent session memory** with TTL management

## API Usage

### Basic Chat Conversation

```bash
# Send a message
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "message": "Hello! How are you today?"
  }'

# Response
{
  "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "session_id": "user123",
  "llm_provider": "chatgroq",
  "model": "llama3-8b-8192"
}
```

### Get Provider Information

```bash
curl -X GET "http://localhost:8000/llm/provider"

# Response
{
  "current_provider": {
    "provider": "chatgroq",
    "model": "llama3-8b-8192",
    "base_url": "https://api.groq.com/openai/v1",
    "temperature": 0.7,
    "max_tokens": 1024,
    "type": "cloud",
    "description": "ChatGroq cloud-based LLM inference"
  }
}
```

### Session Management

```bash
# Clear session memory
curl -X DELETE "http://localhost:8000/chat/session/user123"

# Get memory statistics
curl -X GET "http://localhost:8000/chat/stats"
```

### Health Check

```bash
curl -X GET "http://localhost:8000/health"

# Response
{
  "status": "healthy",
  "service": "chatbot-api",
  "version": "1.0.0",
  "llm_provider": "chatgroq",
  "llm_healthy": true
}
```

## Monitoring & Logs

```bash
# View application logs
docker logs -f chatbot-api

# Monitor health
watch curl -s http://localhost:8000/health
```

## Testing

Test the API endpoints:

```bash
python test_chat.py
```

This will run comprehensive tests including:
- Basic chat functionality
- Session management
- Memory statistics
- Health checks
- Provider information

## API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create an issue in this repository
- Check the API documentation at `/docs`
- Review the health check endpoint at `/health`

## Changelog

### v1.0.0
- ChatGroq integration with high-performance cloud inference
- Session-based conversation memory with TTL
- Production-ready FastAPI service
- Comprehensive API documentation
- Docker deployment support
- Health monitoring and logging