#!/bin/bash
# Unified Docker management script for Trusted Services Framework and Applications
# Usage: ./docker-manage.sh [command] [target] [environment]
# Location: deploy/compose/docker-manage.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0;m' # No Color

# Fonctions de log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

header() {
    echo -e "${CYAN}=========================================="
    echo "$1"
    echo -e "==========================================${NC}"
}

# Parse arguments
COMMAND="${1:-help}"
TARGET="${2:-framework}"
ENV="${3:-dev}"

# Determine compose file and context based on target
# Context for compose commands is deploy/compose/
case "$TARGET" in
    framework)
        if [ "$ENV" = "prod" ]; then
            COMPOSE_FILE="$SCRIPT_DIR/docker-compose.trusted-services-backend.yml"
            TARGET_NAME="Trusted Services Framework (Backend Only)"
        else
            COMPOSE_FILE="$SCRIPT_DIR/docker-compose.trusted-services-dev.yml"
            TARGET_NAME="Trusted Services Framework (Backend + Test Client)"
        fi
        ;;
    delphes)
        if [ "$ENV" = "prod" ]; then
            COMPOSE_FILE="$SCRIPT_DIR/docker-compose.delphes-production.yml"
            TARGET_NAME="Delphes Application"
        else
            COMPOSE_FILE="$SCRIPT_DIR/docker-compose.delphes-integration.yml"
            TARGET_NAME="Delphes Application"
        fi
        ;;
    aisa)
        # AISA uses the framework test client for now
        if [ "$ENV" = "prod" ]; then
            COMPOSE_FILE="$SCRIPT_DIR/docker-compose.trusted-services-backend.yml"
            TARGET_NAME="AISA Application (using Framework Backend)"
        else
            COMPOSE_FILE="$SCRIPT_DIR/docker-compose.trusted-services-dev.yml"
            TARGET_NAME="AISA Application (using Framework Test Client)"
        fi
        ;;
    connexion)
        # conneXion uses the framework test client
        if [ "$ENV" = "prod" ]; then
            COMPOSE_FILE="$SCRIPT_DIR/docker-compose.trusted-services-backend.yml"
            TARGET_NAME="conneXion Application (using Framework Backend)"
        else
            COMPOSE_FILE="$SCRIPT_DIR/docker-compose.trusted-services-dev.yml"
            TARGET_NAME="conneXion Application (using Framework Test Client)"
        fi
        ;;
    *)
        error "Unknown target: $TARGET"
        echo "Valid targets: framework, delphes, aisa, connexion"
        exit 1
        ;;
esac

# Functions
show_usage() {
    cat << 'EOF'
Docker Management Script for Trusted Services Framework

Usage: ./docker-manage.sh [command] [target] [environment]

Commands:
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

Targets:
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

Environments:
  dev         Development (default)
  prod        Production

Examples:
  # Framework development
  ./docker-manage.sh start                     # Backend + test client
  ./docker-manage.sh start framework           # Same as above
  ./docker-manage.sh start framework prod      # Backend only (production)

  # Delphes application
  ./docker-manage.sh start delphes             # Full Delphes stack (dev)
  ./docker-manage.sh start delphes prod        # Delphes frontend (production)
  ./docker-manage.sh logs delphes              # View Delphes logs

  # AISA application
  ./docker-manage.sh start aisa                # Backend + test client
  ./docker-manage.sh status aisa               # Check AISA status

  # Utility commands
  ./docker-manage.sh list-apps                 # Show available apps
  ./docker-manage.sh shell framework           # Access backend shell
  ./docker-manage.sh rebuild delphes           # Clean rebuild Delphes

Services:
  Framework Backend:    http://localhost:8002
  Test Client:          http://localhost:8501
  Delphes Frontend:     http://localhost:3000
  API Health:           http://localhost:8002/api/health

EOF
}

start_services() {
    header "Starting: $TARGET_NAME ($ENV)"
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "$COMPOSE_FILE not found!"
        exit 1
    fi
    
    # Check if .env file exists, create if not
    if [ ! -f .env ]; then
        warning "Creating .env file..."
        touch .env
    fi
    
    log "Starting Docker Compose services..."
    docker compose -f "$COMPOSE_FILE" up -d
    
    echo ""
    log "Waiting for services to be healthy..."
    sleep 5
    
    echo ""
    docker compose -f "$COMPOSE_FILE" ps
    
    echo ""
    success "Services started successfully!"
    
    # Show relevant URLs based on target and env
    echo ""
    echo "Access your services:"
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
    echo "Useful commands:"
    echo "   View logs:    ./docker-manage.sh logs $TARGET $ENV"
    echo "   Stop:         ./docker-manage.sh stop $TARGET $ENV"
    echo "   Restart:      ./docker-manage.sh restart $TARGET $ENV"
    echo ""
}

stop_services() {
    header "Stopping: $TARGET_NAME ($ENV)"
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "$COMPOSE_FILE not found!"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" down
    
    echo ""
    success "Services stopped successfully!"
    echo ""
    echo "To remove volumes as well:"
    echo "   ./docker-manage.sh clean $TARGET $ENV"
    echo ""
}

restart_services() {
    header "Restarting: $TARGET_NAME ($ENV)"
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "$COMPOSE_FILE not found!"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" restart
    
    echo ""
    success "Services restarted successfully!"
    echo ""
}

show_status() {
    header "Status: $TARGET_NAME ($ENV)"
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "$COMPOSE_FILE not found!"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
}

show_logs() {
    header "Logs: $TARGET_NAME ($ENV)"
    echo "Press Ctrl+C to exit"
    echo ""
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "$COMPOSE_FILE not found!"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" logs -f
}

build_images() {
    header "Building: $TARGET_NAME ($ENV)"
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "$COMPOSE_FILE not found!"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" build
    
    echo ""
    success "Images built successfully!"
    echo ""
}

rebuild_images() {
    header "Rebuilding from scratch: $TARGET_NAME ($ENV)"
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "$COMPOSE_FILE not found!"
        exit 1
    fi
    
    docker compose -f "$COMPOSE_FILE" build --no-cache
    
    echo ""
    success "Images rebuilt successfully!"
    echo ""
}

clean_all() {
    header "Cleaning: $TARGET_NAME ($ENV)"
    warning "This will remove containers AND volumes!"
    read -p "Are you sure? (yes/no): " -r
    echo
    
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        if [ ! -f "$COMPOSE_FILE" ]; then
            error "$COMPOSE_FILE not found!"
            exit 1
        fi
        
        docker compose -f "$COMPOSE_FILE" down -v
        
        echo ""
        success "Cleaned successfully!"
        echo ""
    else
        echo "Cancelled."
    fi
}

open_shell() {
    header "Opening Shell in Backend Container"

    CONTAINER_ID="$(docker compose -f "$COMPOSE_FILE" ps -q backend)"
    if [ -z "$CONTAINER_ID" ]; then
        error "No backend service found in $COMPOSE_FILE"
        echo ""
        echo "Start services first:"
        echo "  ./docker-manage.sh start $TARGET $ENV"
        exit 1
    fi

    if ! docker ps -q --no-trunc | grep -q "$CONTAINER_ID"; then
        error "Backend container is not running!"
        echo ""
        echo "Start services first:"
        echo "  ./docker-manage.sh start $TARGET $ENV"
        exit 1
    fi

    docker exec -it "$CONTAINER_ID" /bin/sh
}

list_apps() {
    header "Available Trusted Services Applications"
    echo ""
    
    echo "Framework:"
    echo "  Name:        Trusted Services Framework"
    echo "  Target:      framework"
    echo "  Description: Generic AI framework with test client"
    echo ""
    
    RUNTIME_APPS_DIR="$SCRIPT_DIR/../../runtime/apps"
    APPS_DIR="$SCRIPT_DIR/../../apps"

    if [ -d "$RUNTIME_APPS_DIR" ]; then
        for app_dir in "$RUNTIME_APPS_DIR"/*/; do
            if [ -d "$app_dir" ]; then
                app_name=$(basename "$app_dir")
                echo "Application:"
                echo "  Name:        $app_name"
                echo "  Target:      $(echo "$app_name" | tr '[:upper:]' '[:lower:]')"
                echo "  Config:      runtime/apps/$app_name/"
                
                # Check for custom frontend
                if [ -d "$APPS_DIR/$app_name/frontend" ]; then
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
