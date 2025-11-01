#!/bin/bash
# Wait for services to be ready before running tests
# Usage: ./wait_for_services.sh [backend] [frontend]

set -e

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8002/api/health}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
MAX_WAIT="${MAX_WAIT:-60}"
POLL_INTERVAL="${POLL_INTERVAL:-2}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

wait_for_url() {
    local url=$1
    local name=$2
    local elapsed=0
    
    echo -e "${YELLOW}Waiting for $name at $url...${NC}"
    
    while [ $elapsed -lt $MAX_WAIT ]; do
        if curl -sf --max-time 2 "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $name is ready!${NC}"
            return 0
        fi
        
        sleep $POLL_INTERVAL
        elapsed=$((elapsed + POLL_INTERVAL))
        echo -n "."
    done
    
    echo ""
    echo -e "${RED}✗ Timeout waiting for $name${NC}"
    return 1
}

# Main
main() {
    local services=("$@")
    
    # Default to checking both if no args
    if [ ${#services[@]} -eq 0 ]; then
        services=("backend" "frontend")
    fi
    
    local exit_code=0
    
    for service in "${services[@]}"; do
        case $service in
            backend)
                if ! wait_for_url "$BACKEND_URL" "Backend"; then
                    exit_code=1
                fi
                ;;
            frontend)
                if ! wait_for_url "$FRONTEND_URL" "Frontend"; then
                    exit_code=1
                fi
                ;;
            *)
                echo -e "${RED}Unknown service: $service${NC}"
                exit_code=1
                ;;
        esac
    done
    
    return $exit_code
}

main "$@"

