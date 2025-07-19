#!/bin/bash

# ChatGroq & Llama Conversational Chatbot Stop Script
# Gracefully stops all running services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping ChatGroq & Llama Conversational Chatbot${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Determine environment
ENVIRONMENT=${ENVIRONMENT:-development}
COMPOSE_FILE="docker-compose.yml"

if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

# Function to stop services
stop_services() {
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    
    # Stop services using docker-compose
    if command -v docker-compose > /dev/null 2>&1; then
        docker-compose -f $COMPOSE_FILE --profile ollama down
    else
        docker compose -f $COMPOSE_FILE --profile ollama down
    fi
    
    echo -e "${GREEN}✅ Services stopped successfully${NC}"
}

# Function to clean up (optional)
cleanup() {
    local cleanup_volumes=${1:-false}
    
    if [ "$cleanup_volumes" = "true" ]; then
        echo -e "${YELLOW}🧹 Cleaning up volumes...${NC}"
        echo -e "${RED}⚠️  This will remove all Ollama models and data!${NC}"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v docker-compose > /dev/null 2>&1; then
                docker-compose -f $COMPOSE_FILE --profile ollama down -v
            else
                docker compose -f $COMPOSE_FILE --profile ollama down -v
            fi
            echo -e "${GREEN}✅ Volumes cleaned up${NC}"
        else
            echo -e "${YELLOW}ℹ️  Volume cleanup cancelled${NC}"
        fi
    fi
}

# Function to show status
show_status() {
    echo ""
    echo -e "${BLUE}📊 Container Status:${NC}"
    docker ps -a --filter "name=chatbot" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
}

# Main execution
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean-volumes)
                cleanup true
                shift
                ;;
            --status)
                show_status
                exit 0
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --clean-volumes    Remove all volumes (including Ollama models)"
                echo "  --status           Show container status"
                echo "  --help            Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    stop_services
    show_status
    
    echo -e "${GREEN}🎉 Shutdown completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}🔄 To restart the services, run: ${GREEN}./start.sh${NC}"
}

# Run main function
main "$@"