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

# ChatGroq Conversational Chatbot API

A FastAPI-based conversational chatbot service powered by ChatGroq's high-performance cloud API with Redis-based admin authentication. This repository is designed with a modular architecture that separates routing, language model logic, session memory, authentication, and request schema validation for clean extensibility and maintainability.

## Features

- **ChatGroq Integration**: High-performance cloud inference with multiple model options
- **Redis Authentication**: Simple admin authentication using Upstash Redis
- **JWT Token Security**: Standard Bearer token authentication for API access
- **Session-based Memory**: TTL-based in-memory caching for conversation history
- **Admin Management**: Comprehensive admin endpoints for credential and system management
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
├── auth.py              # Redis-based authentication
├── llm.py              # ChatGroq LLM service
├── memory.py           # Session memory management
├── routes/
│   ├── admin.py        # Admin authentication and management
│   ├── chat.py         # Chat endpoints (requires auth)
│   └── llm.py          # LLM provider management endpoints
└── schemas/
    └── chat.py         # Pydantic models
```

### Module Details

- **`app/main.py`**: Entry point for the FastAPI app with router inclusion
- **`app/auth.py`**: Redis-based authentication system with JWT tokens
- **`app/routes/admin.py`**: Admin authentication and system management endpoints
- **`app/routes/chat.py`**: Chat endpoint handling with admin authentication
- **`app/routes/llm.py`**: LLM provider management and information endpoints
- **`app/schemas/chat.py`**: Pydantic models for request/response validation
- **`app/llm.py`**: ChatGroq LLM service integration
- **`app/memory.py`**: TTL-based session memory management
- **`app/config.py`**: Centralized configuration management

## Quick Start

### Prerequisites

- Python 3.11+
- ChatGroq API key
- Upstash Redis database (see [REDIS_SETUP.md](REDIS_SETUP.md))
- Docker & Docker Compose (optional)

### Environment Setup

**Required Configuration:**

```bash
# ChatGroq API (Required)
GROQ_API_KEY=your_groq_api_key_here

# Upstash Redis (Required)
REDIS_URL=rediss://default:password@proud-firefly-12345.upstash.io:6380

# Authentication Secret (Required)
SECRET_KEY=your-super-secret-key-min-32-characters-long

# Default Admin Credentials (Optional)
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123

# Optional customization
LLM_PROVIDER=chatgroq
GROQ_MODEL_NAME=llama3-8b-8192
TEMPERATURE=0.7
MAX_TOKENS=1024
```

> 📖 **Detailed Setup Guide**: See [REDIS_SETUP.md](REDIS_SETUP.md) for complete instructions on setting up Upstash Redis database.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | ChatGroq API key (required) | None |
| `REDIS_URL` | Upstash Redis connection URL (required) | None |
| `SECRET_KEY` | JWT secret key (required) | None |
| `DEFAULT_ADMIN_USERNAME` | Initial admin username | `admin` |
| `DEFAULT_ADMIN_PASSWORD` | Initial admin password | `admin123` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `60` |
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
# Quick start with ChatGroq and Redis
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
export REDIS_URL="rediss://default:password@host:port"
export SECRET_KEY="your-secure-secret-key"

# 3. Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Access the API
# - API Documentation: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
# - Admin Login: Use POST /admin/login
```

### Production Features

The deployment includes:
- **Redis-based authentication** with configurable credentials
- **JWT token security** with configurable expiration
- **Production-ready configuration** with optimized settings
- **Health checks** for monitoring and load balancers
- **Comprehensive logging** for debugging and monitoring
- **CORS support** for web applications
- **Persistent session memory** with TTL management

## API Usage

### 1. Admin Authentication

#### Login and Get Token

```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin", "password":"admin123"}'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "username": "admin"
}
```

#### Change Admin Credentials

```bash
curl -X POST "http://localhost:8000/admin/change-credentials" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_username":"newadmin", "new_password":"newsecurepass"}'
```

### 2. Chat Conversations (Requires Authentication)

```bash
# Send a message (requires Bearer token)
curl -X POST "http://localhost:8000/chat/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "chat123",
    "message": "Hello! How are you today?"
  }'

# Response
{
  "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "session_id": "chat123",
  "llm_provider": "chatgroq",
  "model": "llama3-8b-8192",
  "user_id": "admin"
}
```

### 3. System Management

#### Get System Status

```bash
curl -X GET "http://localhost:8000/admin/status" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response
{
  "redis_connected": true,
  "chatgroq_healthy": true,
  "active_sessions_count": 2,
  "uptime_seconds": 3600,
  "uptime_formatted": "1h 0m"
}
```

#### Test ChatGroq Connection

```bash
curl -X POST "http://localhost:8000/admin/test-chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'
```

### 4. Session Management

```bash
# Clear session memory
curl -X DELETE "http://localhost:8000/chat/sessions/chat123" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get memory statistics (admin only)
curl -X GET "http://localhost:8000/chat/memory/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Provider Information

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

### 6. Health Check

```bash
curl -X GET "http://localhost:8000/health"

# Response
{
  "status": "healthy",
  "service": "chatbot-api",
  "version": "1.0.0",
  "llm_provider": "chatgroq",
  "llm_healthy": true,
  "redis_healthy": true
}
```

## Available Endpoints

### Admin Endpoints
- `POST /admin/login` - Login and receive JWT token
- `POST /admin/logout` - Logout (session cleanup)
- `GET /admin/info` - Get admin account information
- `POST /admin/change-credentials` - Update admin credentials
- `GET /admin/status` - System health and status
- `GET /admin/sessions` - Active admin sessions
- `POST /admin/test-chat` - Test ChatGroq connection

### Chat Endpoints (Require Authentication)
- `POST /chat/` - Send message to chatbot
- `DELETE /chat/sessions/{session_id}` - Clear conversation session
- `GET /chat/memory/stats` - Memory cache statistics

### LLM Endpoints
- `GET /llm/provider` - Get current LLM provider information
- `GET /llm/providers` - Get available LLM providers
- `GET /llm/health` - Check LLM provider health

### System Endpoints
- `GET /health` - API health check
- `GET /info` - API information
- `GET /docs` - Swagger documentation
- `GET /redoc` - ReDoc documentation

## Authentication Flow

1. **Initial Setup**: Default admin credentials are created on first startup
2. **Login**: Use `/admin/login` to get a JWT token
3. **API Access**: Include `Authorization: Bearer <token>` header in requests
4. **Token Expiry**: Tokens expire after 1 hour (configurable)
5. **Credential Management**: Change username/password via `/admin/change-credentials`

## Monitoring & Logs

```bash
# View application logs
docker logs -f chatbot-api

# Monitor health
watch curl -s http://localhost:8000/health

# Check Redis connection
curl -s http://localhost:8000/admin/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Security Features

- **JWT Authentication**: Industry-standard token-based authentication
- **Password Hashing**: bcrypt with secure salt rounds
- **Redis Storage**: Credentials securely stored in Upstash Redis
- **Session Isolation**: Each admin's conversations are completely isolated
- **Configurable Secrets**: Environment-based secret management
- **HTTPS Ready**: SSL/TLS support for production deployment

## API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

The Swagger UI includes authentication support - use the "Authorize" button to set your Bearer token for testing authenticated endpoints.

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**: 
   - Check your `REDIS_URL` format
   - Verify Upstash Redis is accessible
   - Check network connectivity

2. **Authentication Failed**:
   - Verify admin credentials
   - Check if default credentials were created
   - Try resetting credentials in Redis

3. **ChatGroq Errors**:
   - Verify `GROQ_API_KEY` is correct
   - Check API quota and rate limits
   - Test connection via `/admin/test-chat`

### Resetting Admin Credentials

If you lose access:
1. Delete the `admin:credentials` key from Redis
2. Restart the API (it will recreate default credentials)
3. Login with default credentials and set new ones

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
- Consult [REDIS_SETUP.md](REDIS_SETUP.md) for setup help

## Changelog

### v2.0.0
- **Breaking**: Migrated from PostgreSQL to Redis-based authentication
- **New**: Pure API-only design (no frontend dependencies)
- **New**: JWT token authentication with configurable expiration
- **New**: Comprehensive admin management endpoints
- **New**: Redis-based credential storage with Upstash integration
- **Enhanced**: System monitoring and health checks
- **Enhanced**: Session isolation per admin user

### v1.0.0
- ChatGroq integration with high-performance cloud inference
- Session-based conversation memory with TTL
- Production-ready FastAPI service
- Comprehensive API documentation
- Docker deployment support
- Health monitoring and logging