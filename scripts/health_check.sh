#!/bin/bash
# Health check script for services
# Can be used in Docker healthchecks or monitoring

set -e

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8002}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
TIMEOUT="${TIMEOUT:-5}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local name=$2
    
    if curl -sf --max-time $TIMEOUT "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name is healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ $name is not responding${NC}"
        return 1
    fi
}

# Function to check port
check_port() {
    local host=$1
    local port=$2
    local name=$3
    
    if nc -z -w $TIMEOUT $host $port 2>/dev/null; then
        echo -e "${GREEN}✓ $name port $port is open${NC}"
        return 0
    else
        echo -e "${RED}✗ $name port $port is not accessible${NC}"
        return 1
    fi
}

# Main health check
main() {
    echo "=== Service Health Check ==="
    echo ""
    
    local exit_code=0
    
    # Check backend API
    echo "Checking Backend API..."
    if ! check_http "${BACKEND_URL}/api/health" "Backend API"; then
        exit_code=1
    fi
    echo ""
    
    # Check frontend (if requested)
    if [ "${CHECK_FRONTEND:-true}" = "true" ]; then
        echo "Checking Frontend..."
        if ! check_http "${FRONTEND_URL}" "Frontend"; then
            exit_code=1
        fi
        echo ""
    fi
    
    # Summary
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}All services are healthy ✓${NC}"
    else
        echo -e "${RED}Some services are unhealthy ✗${NC}"
    fi
    
    return $exit_code
}

# Run main function
main "$@"

