# Upstash Redis Setup for ChatGroq Chatbot API

This guide shows you how to set up Upstash Redis for admin authentication with the ChatGroq Chatbot API.

## Prerequisites

- Upstash account (free tier available)
- ChatGroq API key

## 1. Create Upstash Redis Database

1. Go to [Upstash Console](https://console.upstash.com/)
2. Sign up or log in to your account
3. Click "Create Database"
4. Choose your region (closer to your deployment for better performance)
5. Select "Redis" as the database type
6. Give your database a name (e.g., "chatgroq-auth")
7. Click "Create"

## 2. Get Redis Connection URL

After creating the database:

1. Go to your database dashboard
2. Copy the "UPSTASH_REDIS_REST_URL" or "Redis URL"
3. The URL format should be: `rediss://default:password@host:port`

## 3. Environment Configuration

Create a `.env` file in your project root with the following variables:

```bash
# ChatGroq Configuration (Required)
GROQ_API_KEY=your_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL_NAME=llama3-8b-8192

# LLM Configuration
LLM_PROVIDER=chatgroq
TEMPERATURE=0.7
MAX_TOKENS=1024

# Memory Configuration
MEMORY_TTL_SECONDS=3600
MAX_CACHE_SIZE=1000

# Authentication Configuration (Required)
SECRET_KEY=your-secret-key-change-in-production-to-a-secure-random-string

# Upstash Redis (Required)
REDIS_URL=rediss://default:your_password@proud-firefly-12345.upstash.io:6380

# Default Admin Credentials (Optional - will be auto-generated if not set)
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123

# Session Configuration (Optional)
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Start the API

```bash
uvicorn app.main:app --reload
```

## 6. Default Admin Credentials

On first startup, if no admin credentials exist in Redis, the API will automatically create default credentials:

- **Username**: `admin` (or value from `DEFAULT_ADMIN_USERNAME`)
- **Password**: `admin123` (or value from `DEFAULT_ADMIN_PASSWORD`)

**⚠️ Important**: Change these credentials immediately after first login!

## 7. API Usage

### Login and Get Token

```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin", "password":"admin123"}'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "username": "admin"
}
```

### Use Token for Chat

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test", "message":"Hello!"}'
```

### Change Admin Credentials

```bash
curl -X POST "http://localhost:8000/admin/change-credentials" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{"new_username":"newadmin", "new_password":"newsecurepassword"}'
```

### Get System Status

```bash
curl -X GET "http://localhost:8000/admin/status" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## 8. Available Endpoints

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

### System Endpoints
- `GET /health` - API health check
- `GET /info` - API information
- `GET /docs` - Swagger documentation
- `GET /redoc` - ReDoc documentation

## 9. Redis Data Structure

The API stores the following data in Redis:

```
admin:credentials -> {
  username: "admin",
  password: "hashed_password",
  created_at: "2024-01-01T00:00:00",
  last_updated: "2024-01-01T00:00:00"
}

admin:sessions:{session_id} -> {
  username: "admin",
  created_at: "2024-01-01T00:00:00",
  last_activity: "2024-01-01T00:00:00"
}
```

## 10. Production Deployment

### Environment Variables

Set these environment variables in your production deployment:

1. **REDIS_URL**: Your Upstash Redis connection URL
2. **SECRET_KEY**: A secure random string (min 32 characters)
3. **GROQ_API_KEY**: Your ChatGroq API key
4. **DEFAULT_ADMIN_USERNAME**: Initial admin username
5. **DEFAULT_ADMIN_PASSWORD**: Initial admin password (change after first login)

### Security Notes

1. Always use HTTPS in production
2. Change default admin credentials immediately
3. Use a strong SECRET_KEY (generate with `openssl rand -hex 32`)
4. Monitor Redis access logs
5. Set appropriate CORS policies
6. Consider rate limiting for production use

### Docker Deployment

You can use the included Docker Compose setup:

```bash
docker-compose up -d
```

Make sure to set your environment variables in the compose file or use a `.env` file.

## 11. Troubleshooting

### Connection Issues

1. **Redis Connection Failed**: Check your REDIS_URL format and network access
2. **Authentication Failed**: Verify your admin credentials
3. **ChatGroq Errors**: Check your GROQ_API_KEY and quota

### Checking Redis Connection

```bash
curl -X GET "http://localhost:8000/admin/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This will show Redis connection status along with other system health metrics.

### Resetting Admin Credentials

If you lose access, you can reset credentials by:

1. Deleting the `admin:credentials` key from Redis
2. Restarting the API (it will recreate default credentials)
3. Or manually setting credentials in Redis

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the health check endpoint at `/health`
- Check application logs for detailed error messages