# Upstash PostgreSQL Setup Guide

This guide will help you set up the ChatGroq Chatbot with Upstash's serverless PostgreSQL database for authentication and user management.

## 🚀 Why Upstash PostgreSQL?

- **Serverless**: Auto-scaling, pay-per-request pricing
- **Global**: Low-latency access from anywhere
- **Production-Ready**: Built for scale with automatic backups
- **PostgreSQL Compatible**: Full SQL support with familiar syntax
- **No Connection Limits**: Perfect for serverless applications

## 📋 Prerequisites

1. **Upstash Account**: Sign up at [console.upstash.com](https://console.upstash.com/)
2. **ChatGroq API Key**: Get from [console.groq.com](https://console.groq.com/)
3. **Docker** (optional, for containerized deployment)

## 🔧 Step 1: Create Upstash PostgreSQL Database

### 1.1 Create Database

1. Go to [Upstash Console](https://console.upstash.com/)
2. Click **"Create Database"**
3. Choose **PostgreSQL**
4. Select your preferred region (choose closest to your deployment)
5. Name your database (e.g., `chatgroq-chatbot`)
6. Click **"Create"**

### 1.2 Get Connection Details

After creation, you'll see your database dashboard with:
- **Database URL** (this is what you need)
- **Host, Port, Database Name, Username, Password** (individual components)

Copy the **Database URL** - it looks like:
```
postgresql://username:password@region-database.upstash.io:5432/dbname?sslmode=require
```

## 🔧 Step 2: Configure Environment Variables

### 2.1 Create Environment File

Copy the example environment file:
```bash
cp .env.example .env
```

### 2.2 Set Required Variables

Edit `.env` and set:

```bash
# ChatGroq Configuration (Required)
GROQ_API_KEY=your_groq_api_key_here

# Upstash PostgreSQL Database (Required)
DATABASE_URL=postgresql://username:password@region-database.upstash.io:5432/dbname?sslmode=require

# Authentication Secret (Required for production)
SECRET_KEY=your-super-secret-key-min-32-characters-long

# Optional: Customize other settings
GROQ_MODEL_NAME=llama3-8b-8192
TEMPERATURE=0.7
MAX_TOKENS=1024
MEMORY_TTL_SECONDS=3600
MAX_CACHE_SIZE=1000
```

### 2.3 Generate Secure Secret Key

Generate a secure secret key:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

## 🔧 Step 3: Database Migration

### 3.1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3.2 Run Database Migration

The application will automatically create tables on startup, but you can also run migrations manually:

```bash
# Run migrations
alembic upgrade head

# Or let the app create tables automatically on first startup
```

## 🚀 Step 4: Deployment Options

### Option A: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your_groq_api_key"
export DATABASE_URL="your_upstash_database_url"
export SECRET_KEY="your_secret_key"

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Application will be available at http://localhost:8000
```

### Option B: Docker Deployment

```bash
# Create .env file with your variables
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=your_upstash_database_url
SECRET_KEY=your_secret_key
EOF

# Build and run with Docker Compose
docker-compose up --build -d

# Application will be available at http://localhost:8000
```

### Option C: Production Deployment

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up --build -d
```

## 👤 Step 5: Create Admin User

### 5.1 Using the Script

```bash
# Run the superuser creation script
python scripts/create_superuser.py

# Follow the prompts to create an admin user
```

### 5.2 Manual Registration

You can also create users via the API:

```bash
# Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "secure_password",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

## 🔐 Step 6: Authentication Flow

### 6.1 Login and Get Token

```bash
# Login to get JWT token
curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=secure_password"

# Response includes access_token
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### 6.2 Use Token for Chat

```bash
# Chat with authentication
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "session_id": "my_session",
    "message": "Hello, how are you?"
  }'
```

## 📊 Step 7: Available Endpoints

### Authentication Endpoints

```
POST /auth/register              # User registration
POST /auth/jwt/login             # JWT login
POST /auth/jwt/logout            # JWT logout
GET  /auth/users/me              # Get current user
PATCH /auth/users/me             # Update user profile
POST /auth/forgot-password       # Password reset request
POST /auth/reset-password        # Password reset confirmation
```

### Chat Endpoints (Require Authentication)

```
POST /chat/                      # Send message
DELETE /chat/session/{id}        # Clear session
GET  /chat/stats                 # Memory stats (admin only)
```

### System Endpoints

```
GET  /                          # API info
GET  /health                    # Health check
GET  /llm/provider              # LLM provider info
GET  /docs                      # API documentation
```

## 🛠️ Step 8: Monitoring and Maintenance

### 8.1 Database Monitoring

Monitor your Upstash database via the [Upstash Console](https://console.upstash.com/):
- Connection counts
- Query performance
- Storage usage
- Backup status

### 8.2 Application Logs

```bash
# View application logs
docker logs -f chatbot-api

# Monitor health
watch curl -s http://localhost:8000/health
```

### 8.3 User Management

```bash
# Get user statistics (admin only)
curl -X GET "http://localhost:8000/chat/stats" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Get current user info
curl -X GET "http://localhost:8000/auth/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Step 9: Advanced Configuration

### 9.1 Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GROQ_API_KEY` | ChatGroq API key | None | ✅ |
| `DATABASE_URL` | Upstash PostgreSQL URL | None | ✅ |
| `SECRET_KEY` | JWT signing secret | None | ✅ |
| `GROQ_MODEL_NAME` | ChatGroq model | `llama3-8b-8192` | ❌ |
| `TEMPERATURE` | LLM temperature | `0.7` | ❌ |
| `MAX_TOKENS` | Max response tokens | `1024` | ❌ |
| `MEMORY_TTL_SECONDS` | Session TTL | `3600` | ❌ |
| `MAX_CACHE_SIZE` | Max cached sessions | `1000` | ❌ |

### 9.2 Database Performance Tuning

For high-traffic applications, consider:

1. **Connection Pooling**: Upstash handles this automatically
2. **Query Optimization**: Use the provided indexes
3. **Monitoring**: Watch query performance in Upstash Console
4. **Scaling**: Upstash auto-scales based on usage

### 9.3 Security Best Practices

1. **Environment Variables**: Never commit secrets to version control
2. **HTTPS**: Always use HTTPS in production
3. **Secret Rotation**: Regularly rotate your SECRET_KEY
4. **Database Access**: Restrict database access to your application only

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Failed
```
Error: Database connection failed
```
**Solution**: Check your DATABASE_URL format and network connectivity

#### Authentication Required
```
Error: Authentication required
```
**Solution**: Include Authorization header with valid JWT token

#### Migration Errors
```
Error: Table already exists
```
**Solution**: The app handles table creation automatically, no manual migration needed

### Getting Help

1. **Check Logs**: Look at application logs for detailed error messages
2. **Upstash Console**: Monitor database health and connections
3. **API Documentation**: Visit `/docs` for interactive API testing
4. **Health Check**: Check `/health` endpoint for system status

## 🎯 Next Steps

1. **Customize**: Modify user models or add new fields as needed
2. **Scale**: Upstash automatically scales with your usage
3. **Monitor**: Set up alerts in Upstash Console
4. **Integrate**: Connect with your frontend application
5. **Extend**: Add more authentication methods or user features

## 📚 Additional Resources

- [Upstash PostgreSQL Documentation](https://docs.upstash.com/postgresql)
- [ChatGroq API Documentation](https://console.groq.com/docs)
- [FastAPI Users Documentation](https://fastapi-users.github.io/fastapi-users/)
- [Alembic Migration Documentation](https://alembic.sqlalchemy.org/)

---

Your ChatGroq chatbot with Upstash PostgreSQL authentication is now ready for production use! 🚀