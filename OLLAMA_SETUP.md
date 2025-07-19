# 🦙 Ollama Setup Guide for Local LLM Hosting

This guide will help you set up Ollama to run Llama models locally with the ChatGroq & Llama Conversational Chatbot API.

## 📋 Prerequisites

- **System Requirements**:
  - Minimum 8GB RAM (16GB+ recommended for larger models)
  - NVIDIA GPU with CUDA support (optional but recommended)
  - macOS, Linux, or Windows WSL2

## 🚀 Installation

### Option 1: Official Installer (Recommended)

#### macOS
```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Linux
```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
1. Download the installer from https://ollama.ai/download
2. Run the installer and follow the setup wizard

### Option 2: Docker Installation

```bash
# Pull Ollama Docker image
docker pull ollama/ollama

# Run Ollama in Docker
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### Option 3: Manual Installation

Check the official documentation at https://github.com/ollama/ollama for manual installation steps.

## 🔧 Configuration

### 1. Start Ollama Service

After installation, start the Ollama service:

```bash
# Start Ollama service (usually starts automatically)
ollama serve
```

The service will be available at `http://localhost:11434` by default.

### 2. Pull Llama Models

Download the models you want to use:

```bash
# Pull Llama 3 8B (recommended for most users)
ollama pull llama3

# Pull Llama 3 70B (requires more resources)
ollama pull llama3:70b

# Pull Llama 2 models
ollama pull llama2
ollama pull llama2:13b
ollama pull llama2:70b

# Pull other useful models
ollama pull codellama       # Code generation
ollama pull mistral         # Alternative model
ollama pull neural-chat     # Conversational model
```

### 3. Verify Installation

Test that Ollama is working:

```bash
# Check Ollama status
ollama list

# Test a simple chat
ollama run llama3 "Hello, how are you?"
```

## ⚙️ API Configuration

### Environment Variables

Update your `.env` file to use Ollama:

```bash
# Set LLM provider to Ollama
LLM_PROVIDER=ollama

# Ollama configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama3

# Other settings remain the same
TEMPERATURE=0.7
MAX_TOKENS=1024
```

### Model Selection

Available models and their characteristics:

| Model | Size | RAM Required | Description |
|-------|------|--------------|-------------|
| `llama3` | 8B | 8GB+ | Latest Llama 3 model, good performance |
| `llama3:70b` | 70B | 64GB+ | Larger model, better quality |
| `llama2` | 7B | 8GB+ | Previous generation, stable |
| `llama2:13b` | 13B | 16GB+ | Good balance of quality and speed |
| `codellama` | 7B | 8GB+ | Specialized for code generation |
| `mistral` | 7B | 8GB+ | Alternative to Llama models |

## 🧪 Testing Integration

### 1. Start the Chatbot API

```bash
# Make sure Ollama is running
ollama serve

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Ollama Provider

```bash
# Check current provider
curl http://localhost:8000/llm/provider

# Switch to Ollama
curl -X POST "http://localhost:8000/llm/switch" \
  -H "Content-Type: application/json" \
  -d '{"provider": "ollama"}'

# Test chat with Ollama
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_ollama",
    "message": "Hello! Please introduce yourself.",
    "llm_provider": "ollama"
  }'
```

### 3. Test Provider Switching

```bash
# Get available providers
curl http://localhost:8000/llm/providers

# Check Ollama health
curl http://localhost:8000/llm/health

# Switch between providers
curl -X POST "http://localhost:8000/llm/switch" \
  -H "Content-Type: application/json" \
  -d '{"provider": "chatgroq"}'
```

## 🔧 Advanced Configuration

### GPU Acceleration

If you have an NVIDIA GPU, Ollama will automatically use it. Verify GPU usage:

```bash
# Check GPU memory usage
nvidia-smi

# Ollama should show GPU usage when running models
```

### Custom Model Parameters

You can customize model parameters in the environment:

```bash
# Fine-tune model behavior
TEMPERATURE=0.3        # More focused responses
TEMPERATURE=0.9        # More creative responses

# Adjust token limits
MAX_TOKENS=2048        # Longer responses
MAX_TOKENS=512         # Shorter responses
```

### Model Management

```bash
# List downloaded models
ollama list

# Remove unused models to save space
ollama rm llama2

# Update models
ollama pull llama3    # Downloads latest version
```

## 🐳 Docker Compose Setup

For containerized deployment, update `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL_NAME=llama3
    depends_on:
      - ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Ollama Service Not Running
```bash
# Check if service is running
curl http://localhost:11434/api/tags

# Start service if not running
ollama serve
```

#### 2. Model Not Found
```bash
# Pull the required model
ollama pull llama3

# Verify model is available
ollama list
```

#### 3. Out of Memory
```bash
# Try a smaller model
ollama pull llama2    # Instead of llama3:70b

# Or adjust system resources
# Close other applications
# Increase swap space
```

#### 4. Slow Performance
- Use GPU acceleration if available
- Try smaller models for faster responses
- Adjust temperature and max_tokens
- Monitor system resources

### Performance Optimization

1. **Model Selection**: Use the smallest model that meets your quality requirements
2. **Hardware**: More RAM and GPU acceleration significantly improve performance
3. **Configuration**: Lower temperature values (0.1-0.3) for faster, more focused responses
4. **Batch Processing**: Process multiple requests together when possible

## 📊 Monitoring

### Resource Usage

Monitor Ollama performance:

```bash
# Check Ollama logs
ollama logs

# Monitor system resources
htop
nvidia-smi    # For GPU usage
```

### API Metrics

Use the chatbot's monitoring endpoints:

```bash
# Check LLM health
curl http://localhost:8000/llm/health

# Monitor memory usage
curl http://localhost:8000/chat/stats

# Overall health check
curl http://localhost:8000/health
```

## 🌟 Best Practices

1. **Start Small**: Begin with `llama3` or `llama2` models
2. **Monitor Resources**: Keep an eye on RAM and GPU usage
3. **Model Management**: Remove unused models to save disk space
4. **Provider Switching**: Use ChatGroq for high-throughput, Ollama for privacy
5. **Health Checks**: Regularly monitor provider health
6. **Backup Strategy**: Consider backing up model configurations

## 📚 Additional Resources

- [Ollama Official Documentation](https://github.com/ollama/ollama)
- [Llama Model Information](https://ai.meta.com/llama/)
- [LangChain Ollama Integration](https://python.langchain.com/docs/integrations/llms/ollama)
- [Model Performance Benchmarks](https://ollama.ai/library)

---

**Note**: Local model hosting requires significant computational resources. For production deployments with high traffic, consider using ChatGroq or combining both providers with automatic failover.