#!/bin/bash
# Local smoke test runner for Trusted Services
# Usage: ./run_smoke_tests.sh [backend|frontend|all]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8002
FRONTEND_PORT=3000
API_BASE_URL="http://localhost:${BACKEND_PORT}"
FRONTEND_BASE_URL="http://localhost:${FRONTEND_PORT}"

# Parse arguments
TEST_TARGET="${1:-all}"

echo -e "${BLUE}=== Trusted Services Smoke Tests ===${NC}"
echo -e "${BLUE}Test target: ${TEST_TARGET}${NC}\n"

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :${port} -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}Waiting for ${name} to be ready...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "${url}" > /dev/null 2>&1; then
            echo -e "${GREEN}${name} is ready!${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo -e "${RED}${name} failed to start${NC}"
    return 1
}

# Function to run backend smoke tests
run_backend_tests() {
    echo -e "\n${BLUE}=== Running Backend Smoke Tests ===${NC}"
    
    # Check if backend is running
    if ! check_port ${BACKEND_PORT}; then
        echo -e "${YELLOW}Backend not running. Starting...${NC}"
        python launcher_api.py ./runtime > backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > .backend.pid
        
        # Wait for backend to be ready
        if ! wait_for_service "${API_BASE_URL}/api/health" "Backend API"; then
            echo -e "${RED}Failed to start backend. Check backend.log${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}Backend already running on port ${BACKEND_PORT}${NC}"
    fi
    
    # Run backend smoke tests
    export API_BASE_URL="${API_BASE_URL}"
    pytest tests/smoke/test_backend_api.py -v -m "not requires_llm" --tb=short
    local result=$?
    
    # Clean up if we started the backend
    if [ -f .backend.pid ]; then
        echo -e "${YELLOW}Stopping backend...${NC}"
        kill $(cat .backend.pid) 2>/dev/null || true
        rm .backend.pid
    fi
    
    return $result
}

# Function to run frontend smoke tests
run_frontend_tests() {
    echo -e "\n${BLUE}=== Running Frontend Smoke Tests ===${NC}"
    
    # Check if services are running
    local need_backend=false
    local need_frontend=false
    
    if ! check_port ${BACKEND_PORT}; then
        need_backend=true
    fi
    
    if ! check_port ${FRONTEND_PORT}; then
        need_frontend=true
    fi
    
    # Start backend if needed
    if [ "$need_backend" = true ]; then
        echo -e "${YELLOW}Starting backend...${NC}"
        python launcher_api.py ./runtime > backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > .backend.pid
        wait_for_service "${API_BASE_URL}/api/health" "Backend API"
    fi
    
    # Start frontend if needed
    if [ "$need_frontend" = true ]; then
        echo -e "${YELLOW}Starting frontend...${NC}"
        cd apps/delphes/frontend
        npm run build > ../../../frontend-build.log 2>&1
        npm start > ../../../frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../../../.frontend.pid
        cd ../../..
        wait_for_service "${FRONTEND_BASE_URL}" "Frontend"
    fi
    
    # Install Playwright if needed
    if ! command -v playwright &> /dev/null; then
        echo -e "${YELLOW}Installing Playwright browsers...${NC}"
        playwright install chromium
    fi
    
    # Run frontend smoke tests
    export API_BASE_URL="${API_BASE_URL}"
    export FRONTEND_BASE_URL="${FRONTEND_BASE_URL}"
    pytest tests/smoke/test_frontend.py -v --tb=short
    local result=$?
    
    # Clean up if we started services
    if [ -f .frontend.pid ]; then
        echo -e "${YELLOW}Stopping frontend...${NC}"
        kill $(cat .frontend.pid) 2>/dev/null || true
        rm .frontend.pid
    fi
    
    if [ -f .backend.pid ]; then
        echo -e "${YELLOW}Stopping backend...${NC}"
        kill $(cat .backend.pid) 2>/dev/null || true
        rm .backend.pid
    fi
    
    return $result
}

# Main execution
case $TEST_TARGET in
    backend)
        run_backend_tests
        ;;
    frontend)
        run_frontend_tests
        ;;
    all)
        run_backend_tests
        backend_result=$?
        
        run_frontend_tests
        frontend_result=$?
        
        echo -e "\n${BLUE}=== Test Summary ===${NC}"
        if [ $backend_result -eq 0 ]; then
            echo -e "${GREEN}✓ Backend tests passed${NC}"
        else
            echo -e "${RED}✗ Backend tests failed${NC}"
        fi
        
        if [ $frontend_result -eq 0 ]; then
            echo -e "${GREEN}✓ Frontend tests passed${NC}"
        else
            echo -e "${RED}✗ Frontend tests failed${NC}"
        fi
        
        if [ $backend_result -eq 0 ] && [ $frontend_result -eq 0 ]; then
            echo -e "\n${GREEN}All smoke tests passed!${NC}"
            exit 0
        else
            echo -e "\n${RED}Some tests failed${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Invalid target: ${TEST_TARGET}${NC}"
        echo "Usage: $0 [backend|frontend|all]"
        exit 1
        ;;
esac

