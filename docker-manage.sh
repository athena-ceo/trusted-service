#!/bin/bash
# Unified Docker management script for Trusted Services
# Usage: ./docker-manage.sh [command] [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default environment
ENV="${2:-dev}"

# Set compose file based on environment
if [ "$ENV" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV_NAME="Production"
else
    COMPOSE_FILE="docker-compose.dev.yml"
    ENV_NAME="Development"
fi

# Functions
show_usage() {
    cat << EOF
🐳 Trusted Services - Docker Management

Usage: ./docker-manage.sh [command] [environment]

Commands:
  start       Start services
  stop        Stop services
  restart     Restart services
  status      Show service status
  logs        View logs (follow mode)
  build       Build Docker images
  rebuild     Rebuild images from scratch (no cache)
  clean       Stop and remove containers + volumes
  shell       Open shell in backend container

Environments:
  dev         Development (default) - uses docker-compose.dev.yml
  prod        Production - uses docker-compose.prod.yml

Examples:
  ./docker-manage.sh start          # Start development services
  ./docker-manage.sh start prod     # Start production services
  ./docker-manage.sh logs           # View development logs
  ./docker-manage.sh status prod    # Check production status
  ./docker-manage.sh rebuild dev    # Rebuild dev images from scratch

Services:
  Development:
    - Backend:  http://localhost:8002
    - Frontend: http://localhost:3000
    - Health:   http://localhost:8002/api/health

EOF
}

start_services() {
    echo -e "${BLUE}🚀 Starting Trusted Services (${ENV_NAME})${NC}"
    echo "=========================================="
    
    # Check if .env file exists, create if not
    if [ ! -f .env ]; then
        echo -e "${YELLOW}📝 Creating .env file...${NC}"
        touch .env
    fi
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    echo "🐳 Starting Docker Compose services..."
    docker compose -f "$COMPOSE_FILE" up -d
    
    echo ""
    echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
    sleep 5
    
    echo ""
    docker compose -f "$COMPOSE_FILE" ps
    
    echo ""
    echo -e "${GREEN}✅ Services started successfully!${NC}"
    
    if [ "$ENV" = "dev" ]; then
        echo ""
        echo "🌐 Access your services:"
        echo "   Backend API:  http://localhost:8002"
        echo "   Frontend:     http://localhost:3000"
        echo "   API Health:   http://localhost:8002/api/health"
    fi
    
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:    ./docker-manage.sh logs $ENV"
    echo "   Stop:         ./docker-manage.sh stop $ENV"
    echo "   Restart:      ./docker-manage.sh restart $ENV"
    echo ""
}

stop_services() {
    echo -e "${BLUE}🛑 Stopping Trusted Services (${ENV_NAME})${NC}"
    echo "=========================================="
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" down
    
    echo ""
    echo -e "${GREEN}✅ Services stopped successfully!${NC}"
    echo ""
    echo "💡 To remove volumes as well:"
    echo "   ./docker-manage.sh clean $ENV"
    echo ""
}

restart_services() {
    echo -e "${BLUE}🔄 Restarting Trusted Services (${ENV_NAME})${NC}"
    echo "=========================================="
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" restart
    
    echo ""
    echo -e "${GREEN}✅ Services restarted successfully!${NC}"
    echo ""
}

show_status() {
    echo -e "${BLUE}📊 Trusted Services Status (${ENV_NAME})${NC}"
    echo "=========================================="
    echo ""
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
}

show_logs() {
    echo -e "${BLUE}📋 Trusted Services Logs (${ENV_NAME})${NC}"
    echo "=========================================="
    echo "Press Ctrl+C to exit"
    echo ""
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" logs -f
}

build_images() {
    echo -e "${BLUE}🔨 Building Docker Images (${ENV_NAME})${NC}"
    echo "=========================================="
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" build
    
    echo ""
    echo -e "${GREEN}✅ Images built successfully!${NC}"
    echo ""
}

rebuild_images() {
    echo -e "${BLUE}🔨 Rebuilding Docker Images from Scratch (${ENV_NAME})${NC}"
    echo "=========================================="
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" build --no-cache
    
    echo ""
    echo -e "${GREEN}✅ Images rebuilt successfully!${NC}"
    echo ""
}

clean_all() {
    echo -e "${YELLOW}🧹 Cleaning Trusted Services (${ENV_NAME})${NC}"
    echo "=========================================="
    echo -e "${RED}⚠️  WARNING: This will remove containers AND volumes!${NC}"
    read -p "Are you sure? (yes/no): " -r
    echo
    
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        if [ ! -f "$COMPOSE_FILE" ]; then
            echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
            exit 1
        fi
        
        docker compose -f "$COMPOSE_FILE" down -v
        
        echo ""
        echo -e "${GREEN}✅ Cleaned successfully!${NC}"
        echo ""
    else
        echo "Cancelled."
    fi
}

open_shell() {
    echo -e "${BLUE}🐚 Opening Shell in Backend Container (${ENV_NAME})${NC}"
    echo "=========================================="
    
    if [ "$ENV" = "prod" ]; then
        CONTAINER="trusted-services-backend-prod"
    else
        CONTAINER="trusted-services-backend-dev"
    fi
    
    if ! docker ps | grep -q "$CONTAINER"; then
        echo -e "${RED}❌ Error: Container $CONTAINER is not running!${NC}"
        echo ""
        echo "Start services first:"
        echo "  ./docker-manage.sh start $ENV"
        exit 1
    fi
    
    docker exec -it "$CONTAINER" /bin/bash
}

# Main script
COMMAND="${1:-help}"

case "$COMMAND" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    build)
        build_images
        ;;
    rebuild)
        rebuild_images
        ;;
    clean)
        clean_all
        ;;
    shell)
        open_shell
        ;;
    help|--help|-h|*)
        show_usage
        ;;
esac

