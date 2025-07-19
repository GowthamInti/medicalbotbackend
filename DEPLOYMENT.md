# 🚀 Deployment Guide

## Quick Start

The fastest way to get started with the ChatGroq & Llama Conversational Chatbot:

```bash
# 1. Start the services (Ollama is default)
./start.sh

# 2. The API will be available at http://localhost:8000
# 3. Swagger docs at http://localhost:8000/docs
```

## Deployment Options

### 1. Docker Compose with Ollama (Default)

This setup automatically runs Ollama locally with the llama3.2:1b model.

```bash
# Quick start
./start.sh

# Manual start
docker-compose --profile ollama up --build -d

# View logs
docker-compose logs -f

# Stop services
./stop.sh
```

**Features:**
- ✅ Automatic Ollama setup with llama3.2:1b model
- ✅ No internet dependency for inference
- ✅ Privacy-focused local processing
- ✅ ~1GB model download on first startup
- ✅ Persistent model storage

### 2. Docker Compose with ChatGroq

Use ChatGroq cloud API for inference.

```bash
# Set up .env file
echo "LLM_PROVIDER=chatgroq" >> .env
echo "GROQ_API_KEY=your_api_key" >> .env

# Start services (no Ollama profile needed)
docker-compose up chatbot --build -d
```

**Features:**
- ✅ Cloud-based inference
- ✅ No local model storage needed
- ✅ Faster startup time
- ✅ Access to multiple models
- ❗ Requires API key and internet connection

### 3. Hybrid Setup

Switch between providers at runtime.

```bash
# Start with Ollama
./start.sh

# Switch to ChatGroq via API
curl -X POST "http://localhost:8000/llm/switch" \
  -H "Content-Type: application/json" \
  -d '{"provider": "chatgroq"}'

# Or use specific provider per request
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "message": "Hello",
    "llm_provider": "ollama"
  }'
```

## Configuration

### Environment Variables

Create or modify `.env` file:

```bash
# Provider selection
LLM_PROVIDER=ollama  # or chatgroq

# Ollama settings
OLLAMA_MODEL_NAME=llama3.2:1b  # 1B parameter model (fast, efficient)
# OLLAMA_MODEL_NAME=llama3      # 8B parameter model (better quality)

# ChatGroq settings (if using ChatGroq)
GROQ_API_KEY=your_api_key_here

# Performance tuning
TEMPERATURE=0.7
MAX_TOKENS=1024
MEMORY_TTL_SECONDS=3600
```

### Model Options

| Model | Size | RAM Required | Quality | Speed |
|-------|------|--------------|---------|-------|
| `llama3.2:1b` | 1B | 2GB+ | Good | Very Fast |
| `llama3.2:3b` | 3B | 4GB+ | Better | Fast |
| `llama3` | 8B | 8GB+ | Best | Moderate |
| `llama3:70b` | 70B | 64GB+ | Excellent | Slow |

### GPU Support

For NVIDIA GPU acceleration, uncomment the GPU section in `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

## Production Deployment

### Production Setup

```bash
# Use production Docker Compose
ENVIRONMENT=production ./start.sh

# Or manually
docker-compose -f docker-compose.prod.yml --profile ollama up -d
```

**Production features:**
- Optimized health checks
- Better resource management
- Nginx reverse proxy option
- Extended model keep-alive
- Enhanced monitoring

### Scaling Considerations

1. **Memory Requirements:**
   - llama3.2:1b: 2GB RAM minimum
   - llama3: 8GB RAM minimum
   - Add 2GB for the API service

2. **Storage:**
   - Ollama models: 1-40GB depending on model
   - Use volumes for persistent storage

3. **Performance:**
   - GPU acceleration highly recommended
   - SSD storage for better model loading
   - Sufficient RAM to avoid swapping

### Monitoring

```bash
# Health checks
curl http://localhost:8000/health

# Provider status
curl http://localhost:8000/llm/health

# Memory usage
curl http://localhost:8000/chat/stats

# Container status
docker ps -a --filter "name=chatbot"
```

## Troubleshooting

### Common Issues

#### 1. Ollama Model Download Fails
```bash
# Check Ollama logs
docker logs -f chatbot-ollama

# Manually pull model
docker exec chatbot-ollama ollama pull llama3.2:1b
```

#### 2. Out of Memory
```bash
# Use smaller model
echo "OLLAMA_MODEL_NAME=llama3.2:1b" >> .env
./start.sh

# Check system resources
docker stats
```

#### 3. Slow Response Times
```bash
# Enable GPU (if available)
# Uncomment GPU section in docker-compose.yml

# Use faster model
echo "OLLAMA_MODEL_NAME=llama3.2:1b" >> .env

# Adjust performance settings
echo "TEMPERATURE=0.3" >> .env
echo "MAX_TOKENS=512" >> .env
```

#### 4. Service Won't Start
```bash
# Check all container status
docker ps -a --filter "name=chatbot"

# View detailed logs
docker-compose logs

# Reset and restart
./stop.sh --clean-volumes
./start.sh
```

### Performance Optimization

1. **Model Selection:**
   - Start with `llama3.2:1b` for testing
   - Upgrade to `llama3` for better quality
   - Use GPU acceleration when available

2. **Resource Allocation:**
   - Allocate sufficient RAM
   - Use SSD storage
   - Monitor CPU usage

3. **Network:**
   - Use Docker's internal networking
   - Consider reverse proxy for production
   - Implement rate limiting

## Security

### Production Security

1. **API Keys:**
   ```bash
   # Never commit API keys to version control
   echo ".env" >> .gitignore
   
   # Use environment-specific configurations
   cp .env.example .env.production
   ```

2. **Network Security:**
   ```bash
   # Limit external access
   # Modify docker-compose.yml ports section
   ports:
     - "127.0.0.1:8000:8000"  # Localhost only
   ```

3. **Container Security:**
   - Run containers as non-root user
   - Use official base images
   - Keep images updated

### Data Privacy

- **Ollama**: All processing happens locally
- **ChatGroq**: Data sent to external API
- **Sessions**: Stored in memory only (TTL-based)
- **Logs**: Review logging configuration for sensitive data

## Backup and Recovery

### Backup Ollama Models
```bash
# Backup Ollama data volume
docker run --rm -v chatbot_ollama_data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz -C /data .
```

### Restore Ollama Models
```bash
# Restore from backup
docker run --rm -v chatbot_ollama_data:/data -v $(pwd):/backup alpine tar xzf /backup/ollama-backup.tar.gz -C /data
```

### Configuration Backup
```bash
# Backup configuration
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup
```

## Support

For issues and support:
1. Check the troubleshooting section above
2. Review container logs: `docker-compose logs`
3. Test with the test suite: `python test_chat.py`
4. Check the API documentation: `http://localhost:8000/docs`