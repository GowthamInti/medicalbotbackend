#!/bin/bash

# ChatGroq & Llama Conversational Chatbot Startup Script
# Automatically starts the appropriate services based on LLM provider configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
LLM_PROVIDER=${LLM_PROVIDER:-ollama}
ENVIRONMENT=${ENVIRONMENT:-development}
GPU_SUPPORT=${GPU_SUPPORT:-false}

echo -e "${BLUE}🚀 ChatGroq & Llama Conversational Chatbot${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""

# Load environment variables if .env exists
if [ -f .env ]; then
    echo -e "${GREEN}📁 Loading environment variables from .env${NC}"
    set -a
    source .env
    set +a
else
    echo -e "${YELLOW}⚠️  No .env file found. Using default configuration.${NC}"
    echo -e "${YELLOW}   Copy .env.example to .env and configure as needed.${NC}"
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo -e "   LLM Provider: ${GREEN}$LLM_PROVIDER${NC}"
echo -e "   Environment: ${GREEN}$ENVIRONMENT${NC}"
echo -e "   GPU Support: ${GREEN}$GPU_SUPPORT${NC}"
echo ""

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is running${NC}"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose and try again.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker Compose is available${NC}"
}

# Function to start services
start_services() {
    local compose_file="docker-compose.yml"
    local profiles=""
    
    if [ "$ENVIRONMENT" = "production" ]; then
        compose_file="docker-compose.prod.yml"
    fi
    
    echo -e "${BLUE}🏗️  Starting services...${NC}"
    
    # Determine which profiles to activate
    case $LLM_PROVIDER in
        "ollama")
            profiles="--profile ollama"
            echo -e "${GREEN}🦙 Starting with Ollama (local LLM hosting)${NC}"
            echo -e "${YELLOW}📥 Note: First startup will download the model (llama3.2:1b ~1GB)${NC}"
            ;;
        "chatgroq")
            echo -e "${GREEN}☁️  Starting with ChatGroq (cloud API)${NC}"
            if [ -z "$GROQ_API_KEY" ]; then
                echo -e "${RED}❌ GROQ_API_KEY is required for ChatGroq provider${NC}"
                echo -e "${YELLOW}   Please set GROQ_API_KEY in your .env file${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}❌ Unknown LLM provider: $LLM_PROVIDER${NC}"
            echo -e "${YELLOW}   Supported providers: ollama, chatgroq${NC}"
            exit 1
            ;;
    esac
    
    # Build and start services
    if command -v docker-compose > /dev/null 2>&1; then
        docker-compose -f $compose_file $profiles up --build -d
    else
        docker compose -f $compose_file $profiles up --build -d
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Services started successfully!${NC}"
    echo ""
    
    # Display service information
    display_service_info
}

# Function to display service information
display_service_info() {
    echo -e "${BLUE}📊 Service Information:${NC}"
    echo -e "   🌐 Chatbot API: ${GREEN}http://localhost:8000${NC}"
    echo -e "   📚 API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "   🏥 Health Check: ${GREEN}http://localhost:8000/health${NC}"
    
    if [ "$LLM_PROVIDER" = "ollama" ]; then
        echo -e "   🦙 Ollama API: ${GREEN}http://localhost:11434${NC}"
        echo ""
        echo -e "${YELLOW}📥 Model Download Status:${NC}"
        echo -e "   Monitor model download progress:"
        echo -e "   ${BLUE}docker logs -f chatbot-ollama${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}🛠️  Useful Commands:${NC}"
    echo -e "   📊 View logs: ${BLUE}docker-compose logs -f${NC}"
    echo -e "   🔄 Restart: ${BLUE}./start.sh${NC}"
    echo -e "   🛑 Stop: ${BLUE}./stop.sh${NC}"
    echo -e "   🧪 Test API: ${BLUE}python test_chat.py${NC}"
}

# Function to wait for services
wait_for_services() {
    echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
    
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Chatbot API is ready!${NC}"
            break
        fi
        
        attempt=$((attempt + 1))
        echo -e "   Attempt $attempt/$max_attempts: Waiting for API..."
        sleep 5
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}❌ Services failed to start within expected time${NC}"
        echo -e "${YELLOW}   Check logs: docker-compose logs${NC}"
        exit 1
    fi
}

# Main execution
main() {
    check_docker
    check_docker_compose
    
    echo ""
    start_services
    wait_for_services
    
    echo ""
    echo -e "${GREEN}🎉 Startup completed successfully!${NC}"
    echo -e "${GREEN}🚀 Your chatbot is ready at: http://localhost:8000${NC}"
}

# Run main function
main "$@"