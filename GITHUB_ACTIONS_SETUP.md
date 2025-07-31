# GitHub Actions Setup Guide

This guide explains how to set up GitHub Actions workflows for building, testing, and deploying the ChatGroq Chatbot API with Docker and environment variables.

## Prerequisites

- GitHub repository with the chatbot code
- Upstash Redis database
- ChatGroq API key
- Target deployment server (optional)

## 1. Required GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add the following secrets:

### Required Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `GROQ_API_KEY` | ChatGroq API key | `gsk_...` |
| `REDIS_URL` | Upstash Redis connection URL | `rediss://default:password@host:port` |
| `SECRET_KEY` | JWT secret key (32+ characters) | `your-super-secure-secret-key-32-chars` |

### Optional Secrets (with defaults)

| Secret Name | Description | Default |
|-------------|-------------|---------|
| `DEFAULT_ADMIN_USERNAME` | Initial admin username | `admin` |
| `DEFAULT_ADMIN_PASSWORD` | Initial admin password | `admin123` |

### Server Deployment Secrets (if using server deployment)

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SERVER_HOST` | Target server hostname/IP | `your-server.com` |
| `SERVER_USER` | SSH username | `ubuntu` |
| `SERVER_SSH_KEY` | Private SSH key for server access | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

## 2. Workflow Files

The repository includes three GitHub Actions workflows:

### 2.1 Main Build and Deploy Workflow
**File**: `.github/workflows/docker-deploy.yml`

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Manual trigger via GitHub UI

**Jobs**:
- **build-and-push**: Builds Docker image and pushes to GitHub Container Registry
- **test**: Runs API tests with environment variables
- **deploy**: Placeholder for production deployment
- **security-scan**: Scans for vulnerabilities using Trivy

### 2.2 Server Deployment Workflow
**File**: `.github/workflows/deploy-to-server.yml`

**Triggers**:
- Automatically after successful main workflow
- Manual trigger with environment selection

**Features**:
- SSH deployment to remote server
- Docker container management
- Health checks
- Rolling deployment

### 2.3 Docker Compose Production
**File**: `docker-compose.prod.yml`

**Features**:
- Uses pre-built images from GitHub Container Registry
- Environment variable configuration
- Optional Traefik reverse proxy with SSL
- Health checks and logging

## 3. Setting Up Secrets

### 3.1 Generate Secure Secret Key

```bash
# Generate a secure secret key
openssl rand -hex 32
```

### 3.2 Get Upstash Redis URL

1. Go to [Upstash Console](https://console.upstash.com/)
2. Create or select your Redis database
3. Copy the connection URL (format: `rediss://default:password@host:port`)

### 3.3 Get ChatGroq API Key

1. Go to [ChatGroq Console](https://console.groq.com/)
2. Create an API key
3. Copy the key (format: `gsk_...`)

### 3.4 Server SSH Key (for server deployment)

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "github-actions@your-repo"

# Copy public key to server
ssh-copy-id -i ~/.ssh/id_rsa.pub user@your-server.com

# Copy private key content for GitHub secret
cat ~/.ssh/id_rsa
```

## 4. Workflow Usage

### 4.1 Automatic Deployment

1. **Push to main branch**: Triggers build, test, and deployment
2. **Create pull request**: Triggers build and test only
3. **Merge PR**: Triggers full deployment pipeline

### 4.2 Manual Deployment

1. Go to GitHub → Actions → "Deploy to Server"
2. Click "Run workflow"
3. Select environment (production/staging)
4. Click "Run workflow"

### 4.3 Monitoring Deployments

1. Go to GitHub → Actions
2. Click on running/completed workflow
3. View logs for each job
4. Check deployment status and health checks

## 5. Docker Image Usage

### 5.1 Using Pre-built Images

```bash
# Pull latest image
docker pull ghcr.io/yourusername/yourrepo:latest

# Run with environment variables
docker run -d \
  --name chatgroq-api \
  -p 8000:8000 \
  -e GROQ_API_KEY="your_groq_key" \
  -e REDIS_URL="your_redis_url" \
  -e SECRET_KEY="your_secret_key" \
  ghcr.io/yourusername/yourrepo:latest
```

### 5.2 Using Docker Compose

```bash
# Create .env file
cat > .env << EOF
GITHUB_REPOSITORY=yourusername/yourrepo
GROQ_API_KEY=your_groq_key
REDIS_URL=your_redis_url
SECRET_KEY=your_secret_key
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=secure_password
DOMAIN=your-domain.com
ACME_EMAIL=admin@your-domain.com
EOF

# Deploy with reverse proxy
docker-compose -f docker-compose.prod.yml --profile reverse-proxy up -d

# Deploy without reverse proxy
docker-compose -f docker-compose.prod.yml up -d
```

## 6. Environment Variables Reference

### 6.1 Required Variables

```bash
# ChatGroq API
GROQ_API_KEY=gsk_your_api_key_here

# Upstash Redis
REDIS_URL=rediss://default:password@host:port

# Authentication
SECRET_KEY=your-super-secure-secret-key-32-characters-minimum
```

### 6.2 Optional Variables

```bash
# Admin Credentials
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
ACCESS_TOKEN_EXPIRE_MINUTES=60

# LLM Configuration
LLM_PROVIDER=chatgroq
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL_NAME=llama3-8b-8192
TEMPERATURE=0.7
MAX_TOKENS=1024

# Memory Configuration
MEMORY_TTL_SECONDS=3600
MAX_CACHE_SIZE=1000

# Production Settings
ENVIRONMENT=production
LOG_LEVEL=info
```

## 7. Deployment Environments

### 7.1 GitHub Container Registry

Images are automatically built and pushed to:
```
ghcr.io/yourusername/yourrepo:latest
ghcr.io/yourusername/yourrepo:main-sha123456
ghcr.io/yourusername/yourrepo:develop
```

### 7.2 Server Deployment

The workflow can deploy to any server with:
- Docker installed
- SSH access configured
- Port 8000 available

### 7.3 Cloud Platforms

The Docker images can be deployed to:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **DigitalOcean App Platform**
- **Railway/Render/Heroku**

## 8. Testing the Deployment

### 8.1 Health Check

```bash
curl -f http://your-server:8000/health
```

### 8.2 Admin Login

```bash
# Login to get token
TOKEN=$(curl -s -X POST "http://your-server:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin", "password":"admin123"}' | \
  jq -r '.access_token')

# Test authenticated endpoint
curl -X POST "http://your-server:8000/chat/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test", "message":"Hello!"}'
```

## 9. Troubleshooting

### 9.1 Build Failures

1. **Missing secrets**: Ensure all required secrets are set
2. **Docker build errors**: Check Dockerfile and requirements.txt
3. **Test failures**: Verify environment variables in test job

### 9.2 Deployment Failures

1. **SSH connection**: Verify SERVER_HOST, SERVER_USER, and SSH key
2. **Docker issues**: Check if Docker is installed on target server
3. **Port conflicts**: Ensure port 8000 is available

### 9.3 Runtime Issues

1. **Redis connection**: Verify REDIS_URL format and accessibility
2. **ChatGroq errors**: Check GROQ_API_KEY and quota limits
3. **Authentication issues**: Verify SECRET_KEY and admin credentials

### 9.4 Checking Logs

```bash
# View container logs
docker logs chatgroq-api

# Follow logs in real-time
docker logs -f chatgroq-api

# View GitHub Actions logs
# Go to GitHub → Actions → Select workflow run → View job logs
```

## 10. Security Best Practices

1. **Rotate secrets regularly**: Update API keys and passwords periodically
2. **Use strong passwords**: Generate secure admin passwords
3. **Limit SSH access**: Use specific SSH keys for deployment only
4. **Monitor deployments**: Review workflow logs for security issues
5. **Use HTTPS**: Deploy with SSL certificates in production
6. **Update dependencies**: Keep Docker images and packages updated

## 11. Scaling and Production Considerations

### 11.1 Load Balancing

Use Traefik or nginx for load balancing multiple instances:

```yaml
# docker-compose.prod.yml
services:
  chatbot-1:
    image: ghcr.io/yourrepo:latest
    # ... configuration
  
  chatbot-2:
    image: ghcr.io/yourrepo:latest
    # ... configuration
```

### 11.2 Monitoring

Add monitoring and alerting:
- **Prometheus + Grafana** for metrics
- **ELK Stack** for centralized logging
- **Uptime monitoring** for health checks

### 11.3 Backup and Recovery

- **Redis backup**: Configure Upstash automatic backups
- **Container recovery**: Use restart policies and health checks
- **Configuration backup**: Store environment files securely

## Support

For issues with GitHub Actions:
- Check workflow logs in GitHub Actions tab
- Verify all secrets are properly configured
- Test Docker images locally before deployment
- Review the deployment health checks and container logs