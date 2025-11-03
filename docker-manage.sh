#!/bin/bash
# Unified Docker management script for Trusted Services Framework and Applications
# Usage: ./docker-manage.sh [command] [target] [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
COMMAND="${1:-help}"
TARGET="${2:-framework}"
ENV="${3:-dev}"

# Determine compose file and context based on target
case "$TARGET" in
    framework)
        if [ "$ENV" = "prod" ]; then
            COMPOSE_FILE="docker-compose.prod.yml"
            CONTEXT_DIR="."
            TARGET_NAME="Trusted Services Framework (Backend Only)"
        else
            COMPOSE_FILE="docker-compose.dev.yml"
            CONTEXT_DIR="."
            TARGET_NAME="Trusted Services Framework (Backend + Test Client)"
        fi
        ;;
    delphes)
        COMPOSE_FILE="docker-compose.${ENV}.yml"
        CONTEXT_DIR="apps/delphes"
        TARGET_NAME="Delphes Application"
        ;;
    aisa)
        # AISA uses the framework test client for now
        if [ "$ENV" = "prod" ]; then
            COMPOSE_FILE="docker-compose.prod.yml"
            CONTEXT_DIR="."
            TARGET_NAME="AISA Application (using Framework Backend)"
        else
            COMPOSE_FILE="docker-compose.dev.yml"
            CONTEXT_DIR="."
            TARGET_NAME="AISA Application (using Framework Test Client)"
        fi
        ;;
    connexion)
        # conneXion uses the framework test client
        if [ "$ENV" = "prod" ]; then
            COMPOSE_FILE="docker-compose.prod.yml"
            CONTEXT_DIR="."
            TARGET_NAME="conneXion Application (using Framework Backend)"
        else
            COMPOSE_FILE="docker-compose.dev.yml"
            CONTEXT_DIR="."
            TARGET_NAME="conneXion Application (using Framework Test Client)"
        fi
        ;;
    *)
        echo -e "${RED}❌ Unknown target: $TARGET${NC}"
        echo "Valid targets: framework, delphes, aisa, connexion"
        exit 1
        ;;
esac

# Functions
show_usage() {
    cat << EOF
${CYAN}🐳 Trusted Services - Docker Management${NC}

${BLUE}Usage:${NC} ./docker-manage.sh [command] [target] [environment]

${BLUE}Commands:${NC}
  start       Start services
  stop        Stop services
  restart     Restart services
  status      Show service status
  logs        View logs (follow mode, Ctrl+C to exit)
  build       Build Docker images
  rebuild     Rebuild from scratch (no cache)
  clean       Remove containers + volumes
  shell       Open shell in backend container
  list-apps   List available applications

${BLUE}Targets:${NC}
  framework   Trusted Services framework (default)
              - dev: Backend + Streamlit test client
              - prod: Backend only
  delphes     Delphes application (French prefecture)
              - dev: Backend + Delphes frontend
              - prod: Delphes frontend only
  aisa        AISA application (Helsinki city)
              - Uses framework test client (for now)
  connexion   conneXion test application (telecom)
              - Uses framework test client

${BLUE}Environments:${NC}
  dev         Development (default)
  prod        Production

${BLUE}Examples:${NC}
  ${GREEN}# Framework development${NC}
  ./docker-manage.sh start                     # Backend + test client
  ./docker-manage.sh start framework           # Same as above
  ./docker-manage.sh start framework prod      # Backend only (production)

  ${GREEN}# Delphes application${NC}
  ./docker-manage.sh start delphes             # Full Delphes stack (dev)
  ./docker-manage.sh start delphes prod        # Delphes frontend (production)
  ./docker-manage.sh logs delphes              # View Delphes logs

  ${GREEN}# AISA application${NC}
  ./docker-manage.sh start aisa                # Backend + test client
  ./docker-manage.sh status aisa               # Check AISA status

  ${GREEN}# Utility commands${NC}
  ./docker-manage.sh list-apps                 # Show available apps
  ./docker-manage.sh shell framework           # Access backend shell
  ./docker-manage.sh rebuild delphes           # Clean rebuild Delphes

${BLUE}Services:${NC}
  Framework Backend:    http://localhost:8002
  Test Client:          http://localhost:8501
  Delphes Frontend:     http://localhost:3000
  API Health:           http://localhost:8002/api/health

EOF
}

start_services() {
    echo -e "${BLUE}🚀 Starting: ${TARGET_NAME} (${ENV})${NC}"
    echo "=========================================="
    
    # Navigate to context directory
    cd "$CONTEXT_DIR" || exit 1
    
    # Check if .env file exists, create if not (only at root)
    if [ "$CONTEXT_DIR" = "." ] && [ ! -f .env ]; then
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
    
    # Show relevant URLs based on target and env
    echo ""
    echo "🌐 Access your services:"
    if [ "$TARGET" = "framework" ]; then
        if [ "$ENV" = "prod" ]; then
            echo "   Backend API:  http://localhost:8002"
            echo "   API Health:   http://localhost:8002/api/health"
        else
            echo "   Backend API:  http://localhost:8002"
            echo "   Test Client:  http://localhost:8501"
            echo "   API Health:   http://localhost:8002/api/health"
        fi
    elif [ "$TARGET" = "delphes" ]; then
        if [ "$ENV" = "prod" ]; then
            echo "   Delphes:      http://localhost:3000"
        else
            echo "   Backend API:  http://localhost:8002"
            echo "   Delphes:      http://localhost:3000"
            echo "   API Health:   http://localhost:8002/api/health"
        fi
    else
        # AISA, conneXion
        echo "   Backend API:  http://localhost:8002"
        echo "   Test Client:  http://localhost:8501"
        echo "   API Health:   http://localhost:8002/api/health"
    fi
    
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:    ./docker-manage.sh logs $TARGET $ENV"
    echo "   Stop:         ./docker-manage.sh stop $TARGET $ENV"
    echo "   Restart:      ./docker-manage.sh restart $TARGET $ENV"
    echo ""
    
    # Return to original directory
    cd - > /dev/null || exit 1
}

stop_services() {
    echo -e "${BLUE}🛑 Stopping: ${TARGET_NAME} (${ENV})${NC}"
    echo "=========================================="
    
    cd "$CONTEXT_DIR" || exit 1
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" down
    
    echo ""
    echo -e "${GREEN}✅ Services stopped successfully!${NC}"
    echo ""
    echo "💡 To remove volumes as well:"
    echo "   ./docker-manage.sh clean $TARGET $ENV"
    echo ""
    
    cd - > /dev/null || exit 1
}

restart_services() {
    echo -e "${BLUE}🔄 Restarting: ${TARGET_NAME} (${ENV})${NC}"
    echo "=========================================="
    
    cd "$CONTEXT_DIR" || exit 1
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" restart
    
    echo ""
    echo -e "${GREEN}✅ Services restarted successfully!${NC}"
    echo ""
    
    cd - > /dev/null || exit 1
}

show_status() {
    echo -e "${BLUE}📊 Status: ${TARGET_NAME} (${ENV})${NC}"
    echo "=========================================="
    echo ""
    
    cd "$CONTEXT_DIR" || exit 1
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    
    cd - > /dev/null || exit 1
}

show_logs() {
    echo -e "${BLUE}📋 Logs: ${TARGET_NAME} (${ENV})${NC}"
    echo "=========================================="
    echo "Press Ctrl+C to exit"
    echo ""
    
    cd "$CONTEXT_DIR" || exit 1
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" logs -f
    
    cd - > /dev/null || exit 1
}

build_images() {
    echo -e "${BLUE}🔨 Building: ${TARGET_NAME} (${ENV})${NC}"
    echo "=========================================="
    
    cd "$CONTEXT_DIR" || exit 1
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" build
    
    echo ""
    echo -e "${GREEN}✅ Images built successfully!${NC}"
    echo ""
    
    cd - > /dev/null || exit 1
}

rebuild_images() {
    echo -e "${BLUE}🔨 Rebuilding from scratch: ${TARGET_NAME} (${ENV})${NC}"
    echo "=========================================="
    
    cd "$CONTEXT_DIR" || exit 1
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" build --no-cache
    
    echo ""
    echo -e "${GREEN}✅ Images rebuilt successfully!${NC}"
    echo ""
    
    cd - > /dev/null || exit 1
}

clean_all() {
    echo -e "${YELLOW}🧹 Cleaning: ${TARGET_NAME} (${ENV})${NC}"
    echo "=========================================="
    echo -e "${RED}⚠️  WARNING: This will remove containers AND volumes!${NC}"
    read -p "Are you sure? (yes/no): " -r
    echo
    
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        cd "$CONTEXT_DIR" || exit 1
        
        if [ ! -f "$COMPOSE_FILE" ]; then
            echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
            exit 1
        fi
        
        docker compose -f "$COMPOSE_FILE" down -v
        
        echo ""
        echo -e "${GREEN}✅ Cleaned successfully!${NC}"
        echo ""
        
        cd - > /dev/null || exit 1
    else
        echo "Cancelled."
    fi
}

open_shell() {
    echo -e "${BLUE}🐚 Opening Shell in Backend Container${NC}"
    echo "=========================================="
    
    # Determine container name based on target and env
    if [ "$TARGET" = "delphes" ] && [ "$ENV" = "dev" ]; then
        CONTAINER="delphes-backend-dev"
    elif [ "$ENV" = "prod" ]; then
        CONTAINER="trusted-services-backend-prod"
    else
        CONTAINER="trusted-services-backend-dev"
    fi
    
    if ! docker ps | grep -q "$CONTAINER"; then
        echo -e "${RED}❌ Error: Container $CONTAINER is not running!${NC}"
        echo ""
        echo "Start services first:"
        echo "  ./docker-manage.sh start $TARGET $ENV"
        exit 1
    fi
    
    docker exec -it "$CONTAINER" /bin/bash
}

list_apps() {
    echo -e "${CYAN}📦 Available Trusted Services Applications${NC}"
    echo "=========================================="
    echo ""
    
    echo -e "${BLUE}Framework:${NC}"
    echo "  Name:        Trusted Services Framework"
    echo "  Target:      framework"
    echo "  Description: Generic AI framework with test client"
    echo ""
    
    if [ -d "runtime/apps" ]; then
        for app_dir in runtime/apps/*/; do
            if [ -d "$app_dir" ]; then
                app_name=$(basename "$app_dir")
                echo -e "${BLUE}Application:${NC}"
                echo "  Name:        $app_name"
                echo "  Target:      $(echo "$app_name" | tr '[:upper:]' '[:lower:]')"
                echo "  Config:      runtime/apps/$app_name/"
                
                # Check for custom frontend
                if [ -d "apps/$app_name/frontend" ]; then
                    echo "  Frontend:    Custom (apps/$app_name/frontend/)"
                else
                    echo "  Frontend:    Generic test client"
                fi
                echo ""
            fi
        done
    fi
    
    echo "To start an application:"
    echo "  ./docker-manage.sh start [target]"
    echo ""
}

# Main script
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
    list-apps)
        list_apps
        ;;
    help|--help|-h|*)
        show_usage
        ;;
esac
