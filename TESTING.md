# Testing Guide - Trusted Services

Complete guide for running tests locally and understanding the CI/CD pipeline.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Types](#test-types)
- [Running Tests Locally](#running-tests-locally)
- [Security Scans](#security-scans)
- [CI/CD Pipeline](#cicd-pipeline)
- [Writing Tests](#writing-tests)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Install Test Dependencies

```bash
# Install Python test dependencies
pip install -r tests/requirements.txt

# Install Playwright for frontend tests
playwright install chromium
```

### Run Smoke Tests

```bash
# Using Python script (cross-platform)
python run_tests.py smoke

# Using bash script (Unix/macOS/Linux)
chmod +x run_smoke_tests.sh
./run_smoke_tests.sh all
```

### Run All Tests

```bash
python run_tests.py all
```

---

## Test Types

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual components in isolation

**Characteristics**:
- Fast execution (< 1s per test)
- No external dependencies
- Use mocks for external services
- High code coverage

**Run Command**:
```bash
pytest tests/unit/ -v --cov=src --cov-report=html
```

**Example**:
```python
def test_case_validation():
    case_data = {"nom": "Dupont", "prenom": "Jean"}
    assert validate_case(case_data) == True
```

---

### 2. Smoke Tests (`tests/smoke/`)

**Purpose**: Verify critical functionality works end-to-end

**Characteristics**:
- Tests critical user paths
- Requires running services
- Fast execution (1-5 min total)
- Run on every commit

**Run Command**:
```bash
# Backend smoke tests only
python run_tests.py smoke --backend

# Frontend smoke tests only  
python run_tests.py smoke --frontend

# All smoke tests
python run_tests.py smoke
```

**What's Tested**:
- ✅ API endpoints respond
- ✅ Health checks pass
- ✅ Critical pages load
- ✅ Basic form functionality
- ✅ API-Frontend integration

---

### 3. Integration Tests (`tests/integration/`)

**Purpose**: Test interactions between multiple components

**Characteristics**:
- Tests complete workflows
- Requires all services running
- Moderate execution time (5-15 min)
- Run on main branch pushes

**Run Command**:
```bash
python run_tests.py integration

# Or with pytest directly
pytest tests/integration/ -v --tb=long
```

**What's Tested**:
- ✅ Complete user journeys
- ✅ API-Backend integration
- ✅ Frontend-Backend communication
- ✅ Multi-service workflows
- ✅ Data persistence

---

## Running Tests Locally

### Method 1: Python Test Runner (Recommended)

Cross-platform Python script that works on Windows, macOS, and Linux.

```bash
# Run specific test type
python run_tests.py smoke
python run_tests.py unit
python run_tests.py integration
python run_tests.py all

# Run backend smoke tests only
python run_tests.py smoke --backend

# Get help
python run_tests.py --help
```

**Features**:
- ✅ Automatic service startup/shutdown
- ✅ Colored output
- ✅ Test summary
- ✅ Works on all platforms

---

### Method 2: Bash Script (Unix/macOS/Linux)

```bash
# Make script executable (first time only)
chmod +x run_smoke_tests.sh

# Run all smoke tests
./run_smoke_tests.sh all

# Run backend tests only
./run_smoke_tests.sh backend

# Run frontend tests only
./run_smoke_tests.sh frontend
```

---

### Method 3: Direct Pytest

For advanced usage and customization.

```bash
# Run specific test file
pytest tests/smoke/test_backend_api.py -v

# Run with markers
pytest -m "smoke and not requires_llm" -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=term --cov-report=html

# Run in parallel (faster)
pytest tests/unit/ -n auto

# Run specific test class
pytest tests/smoke/test_backend_api.py::TestAPIHealth -v

# Run specific test
pytest tests/smoke/test_backend_api.py::TestAPIHealth::test_health_endpoint -v
```

---

### Manual Service Setup

If you prefer to manage services manually:

```bash
# Terminal 1: Start Backend
python launcher_api.py ./runtime

# Terminal 2: Start Frontend
cd apps/delphes/frontend
npm run dev

# Terminal 3: Run Tests
export API_BASE_URL=http://localhost:8002
export FRONTEND_BASE_URL=http://localhost:3000
pytest tests/smoke/ -v
```

---

## Security Scans

Run security checks with the Makefile target (Bandit + Safety + `npm audit` for the frontend):

```bash
make security
```

Safety requires authentication and network access. Use one of the following options:

```bash
# Option 1: API key for this shell session
export SAFETY_API_KEY="your_safety_api_key"
make security

# Option 2: interactive login (stores credentials locally)
safety auth login
make security
```

Keep the API key out of source control and avoid committing it to `.env` files.

`npm audit` also needs network access to reach the npm registry. If it fails with
`ENOTFOUND registry.npmjs.org`, ensure the network is available.

---

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Backend CI (`.github/workflows/backend-ci.yml`)

**Triggers**:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Changes to `src/`, `requirements.txt`, or `tests/`

**Jobs**:
1. **Lint**: Code quality checks
   - Ruff (fast linting)
   - Black (formatting)
   - isort (import sorting)

2. **Test**: Run unit tests
   - Matrix: Python 3.11, 3.12
   - Coverage reporting
   - Upload to Codecov

3. **Smoke Test**: Critical functionality
   - Start backend server
   - Run smoke tests
   - Auto cleanup

4. **Security**: Security scanning
   - Bandit (security issues)
   - Safety (dependency vulnerabilities)

---

#### 2. Frontend CI (`.github/workflows/frontend-ci.yml`)

**Triggers**:
- Push to `main` or `develop`
- Pull requests
- Changes to `apps/delphes/frontend/`

**Jobs**:
1. **Lint and Build**
   - ESLint checks
   - TypeScript type checking
   - Build verification
   - Upload build artifacts

2. **Test**
   - Run Jest tests
   - Coverage reporting

3. **Smoke Test**
   - Start backend and frontend
   - Run Playwright tests
   - Verify integration

---

#### 3. Integration Tests (`.github/workflows/integration-tests.yml`)

**Triggers**:
- Push to `main`
- Pull requests to `main`
- Daily at 2 AM UTC (scheduled)

**Jobs**:
- Start services with Docker Compose
- Run complete integration test suite
- Collect logs on failure

---

#### 4. Deployment (`.github/workflows/deploy.yml`)

**Triggers**:
- Push to `main`
- Version tags (`v*`)
- Manual workflow dispatch

**Jobs**:
1. **Build and Push**
   - Build Docker images
   - Push to GitHub Container Registry
   - Tag with version/SHA

2. **Deploy Staging**
   - Deploy to staging environment
   - Run post-deployment smoke tests

3. **Deploy Production**
   - Deploy to production (requires staging success)
   - Run post-deployment verification
   - Send notifications

---

### Test Markers

Tests can be organized using pytest markers:

```python
@pytest.mark.smoke         # Smoke tests
@pytest.mark.integration   # Integration tests
@pytest.mark.unit          # Unit tests
@pytest.mark.slow          # Slow tests
@pytest.mark.requires_llm  # Requires LLM service
@pytest.mark.requires_db   # Requires database
```

**Usage**:
```bash
# Run only smoke tests
pytest -m smoke

# Run all except slow tests
pytest -m "not slow"

# Run smoke tests that don't require LLM
pytest -m "smoke and not requires_llm"
```

---

## Writing Tests

### Backend API Tests

```python
import pytest
import httpx

@pytest.fixture
def api_client():
    client = httpx.Client(base_url="http://localhost:8002")
    yield client
    client.close()

def test_api_endpoint(api_client):
    """Test API endpoint"""
    response = api_client.post(
        "/api/analyze_request",
        json={"app_name": "delphes", "locale": "fr", "message": "test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "intentions" in data
```

---

### Frontend Tests (Playwright)

```python
def test_page_loads(page):
    """Test page loads successfully"""
    page.goto("http://localhost:3000/accueil-etrangers")
    
    # Wait for form to load
    page.wait_for_selector("form")
    
    # Verify form fields
    assert page.locator("input[name='nom']").is_visible()
    
    # Fill form
    page.fill("input[name='nom']", "Test")
    
    # Submit
    page.click("button[type='submit']")
```

---

### Unit Tests with Mocks

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test using mock objects"""
    mock_llm = Mock()
    mock_llm.analyze.return_value = {"intent": "renouvellement"}
    
    result = process_request("test message", llm_service=mock_llm)
    
    assert result["intent"] == "renouvellement"
    mock_llm.analyze.assert_called_once()
```

---

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test async function"""
    result = await async_function()
    assert result is not None
```

---

### Parametrized Tests

```python
@pytest.mark.parametrize("locale,expected_lang", [
    ("fr", "French"),
    ("en", "English"),
    ("es", "Spanish"),
])
def test_locale_detection(locale, expected_lang):
    """Test multiple inputs with one test"""
    result = detect_language(locale)
    assert result == expected_lang
```

---

## Test Configuration

### pytest.ini

Main pytest configuration file. Key settings:

```ini
[pytest]
testpaths = tests
markers =
    smoke: Smoke tests
    integration: Integration tests
    requires_llm: Needs LLM service
addopts = -v --tb=short
```

### Coverage Configuration

```ini
[coverage:run]
source = src
omit = */tests/*, */__pycache__/*

[coverage:report]
precision = 2
show_missing = true
```

---

## Troubleshooting

### Common Issues

#### 1. Tests Can't Connect to Backend

**Symptom**: `Connection refused` errors

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8002/api/health

# Start backend if not running
python launcher_api.py ./runtime
```

---

#### 2. Frontend Tests Fail

**Symptom**: Playwright can't find elements

**Solution**:
```bash
# Install/update Playwright browsers
playwright install chromium

# Run with headed mode to debug
pytest tests/smoke/test_frontend.py --headed
```

---

#### 3. Port Already in Use

**Symptom**: `Address already in use`

**Solution**:
```bash
# Find process using port
lsof -i :8002  # macOS/Linux
netstat -ano | findstr :8002  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

---

#### 4. Import Errors

**Symptom**: `ModuleNotFoundError`

**Solution**:
```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Verify installation
python -c "import pytest; print(pytest.__version__)"
```

---

#### 5. Slow Tests

**Solution**:
```bash
# Run tests in parallel
pytest tests/unit/ -n auto

# Skip slow tests
pytest -m "not slow"

# Run only failed tests
pytest --lf
```

---

### Debug Mode

```bash
# Run with verbose output
pytest tests/ -vv

# Show print statements
pytest tests/ -s

# Drop into debugger on failure
pytest tests/ --pdb

# Show local variables on failure
pytest tests/ -l

# Run specific failing test
pytest tests/smoke/test_backend_api.py::test_health_endpoint -vv
```

---

### Useful Commands

```bash
# List all tests
pytest --collect-only

# Run tests that match name pattern
pytest -k "test_health"

# Show test durations
pytest --durations=10

# Generate HTML report
pytest --html=report.html

# Generate JUnit XML (for CI)
pytest --junitxml=results.xml

# Watch for file changes and rerun tests
pytest-watch
```

---

## Application-Specific Testing

### Testing the Framework

Test framework functionality independently of applications:

```bash
# Start framework with generic test client
./deploy/compose/docker-manage.sh start framework

# Run backend smoke tests
pytest tests/smoke/test_backend_api.py -v

# Access test client UI for manual testing
# Navigate to: http://localhost:8501
# - Select different applications from dropdown
# - Test intent detection
# - Verify decision engine responses
```

### Testing Applications

#### Delphes Application

**Full stack testing**:
```bash
# Start Delphes (backend + custom frontend)
./deploy/compose/docker-manage.sh start delphes

# Run Delphes-specific tests
pytest tests/smoke/test_backend_api.py -v --app=delphes
pytest tests/smoke/test_frontend.py -v

# Manual testing
# - Frontend: http://localhost:3000
# - Test user flow: contact form → analysis → case handling → confirmation
```

**Frontend-only testing**:
```bash
cd apps/delphes/frontend

# Linting
npm run lint

# Build verification
npm run build

# Type checking
npx tsc --noEmit

# Run tests (if configured)
npm test
```

**Configuration testing**:
```bash
# Test with generic client (validates config without custom UI)
./deploy/compose/docker-manage.sh start framework

# In test client:
# 1. Select "delphes" application
# 2. Choose "fr" or "en" locale
# 3. Enter test messages
# 4. Verify intents are detected correctly
# 5. Check all required fields appear
```

#### AISA Application

**Testing AISA configuration**:
```bash
# Start AISA with generic client
./deploy/compose/docker-manage.sh start aisa

# Verify AISA configuration
pytest tests/smoke/test_backend_api.py -v
# Manually test at: http://localhost:8501

# Test both locales
# - Finnish (fi): Test Finnish-language intents
# - English (en): Test English translations
```

**Configuration validation**:
```bash
# Check AISA config files exist
ls -la runtime/apps/AISA/

# Verify Excel config structure
python -c "import pandas as pd; df = pd.read_excel('runtime/apps/AISA/AISA.xlsx', sheet_name='intentions'); print(df.head())"

# Test decision engine
python -c "from runtime.apps.AISA.decision_engine import *; print('Decision engine loads successfully')"
```

#### conneXion Application

**Testing conneXion**:
```bash
# Start conneXion
./deploy/compose/docker-manage.sh start connexion

# Access at: http://localhost:8501
# Test telecom-specific scenarios
```

### Multi-Application Testing

**Test multiple applications in sequence**:
```bash
#!/bin/bash
# test-all-apps.sh

apps=("delphes" "aisa" "connexion")

for app in "${apps[@]}"; do
    echo "Testing $app..."
    ./deploy/compose/docker-manage.sh stop
    ./deploy/compose/docker-manage.sh start $app
    sleep 10  # Wait for services to be ready
    
    # Run tests for this app
    pytest tests/smoke/ -v --app=$app
    
    if [ $? -ne 0 ]; then
        echo "❌ $app tests failed"
        exit 1
    fi
    
    echo "✅ $app tests passed"
done

./deploy/compose/docker-manage.sh stop
echo "✅ All applications tested successfully"
```

### Testing Configuration Changes

**After updating application configuration**:

```bash
# 1. Clear cache (important!)
rm -rf runtime/cache/*

# 2. Rebuild Docker images if needed
./deploy/compose/docker-manage.sh rebuild framework

# 3. Test with generic client first
./deploy/compose/docker-manage.sh start framework
# Manually verify changes at http://localhost:8501

# 4. Run automated tests
pytest tests/smoke/ -v

# 5. Test custom frontend (if applicable)
./deploy/compose/docker-manage.sh start delphes
pytest tests/smoke/test_frontend.py -v
```

### Testing Intent Detection

**Validate intent detection for each application**:

```python
# test_custom_intents.py
import pytest
import httpx

@pytest.mark.parametrize("app,locale,text,expected_intent", [
    ("delphes", "fr", "Je veux renouveler mon titre de séjour", "renouvellement_titre_sejour"),
    ("AISA", "fi", "Haluan tilata jätekortin", "waste_card_request"),
    ("conneXion", "en", "I need help with my bill", "billing_inquiry"),
])
def test_intent_detection(app, locale, text, expected_intent):
    """Test intent detection for different applications"""
    client = httpx.Client(base_url="http://localhost:8002", timeout=30.0)
    
    response = client.post(
        f"/trusted_services/v2/apps/{app}/{locale}/analyze",
        params={
            "field_values": "{}",
            "text": text,
            "read_from_cache": "false",
            "llm_config_id": "default"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check if expected intent is in top results
    intents = data.get('text_analysis_response', {}).get('user_intention', [])
    intent_ids = [i['intention_id'] for i in intents]
    
    assert expected_intent in intent_ids, \
        f"Expected intent '{expected_intent}' not found in {intent_ids}"
    
    client.close()
```

Run with:
```bash
# Start framework
./deploy/compose/docker-manage.sh start framework

# Run intent tests
pytest test_custom_intents.py -v
```

### Integration Testing Across Applications

**Test framework serves multiple apps correctly**:

```python
# test_multi_app_integration.py
import pytest
import httpx

def test_all_apps_available():
    """Verify all applications are registered"""
    client = httpx.Client(base_url="http://localhost:8002")
    
    response = client.get("/trusted_services/v2/app_ids")
    assert response.status_code == 200
    
    apps = response.json()
    assert "delphes" in apps
    assert "AISA" in apps
    assert "conneXion" in apps
    
    client.close()

def test_app_locales():
    """Verify each app has correct locales"""
    client = httpx.Client(base_url="http://localhost:8002")
    
    expected_locales = {
        "delphes": ["fr", "en"],
        "AISA": ["fi", "en"],
        "conneXion": ["en"]
    }
    
    for app, expected in expected_locales.items():
        response = client.get(f"/trusted_services/v2/apps/{app}/locales")
        assert response.status_code == 200
        
        locales = response.json()
        for locale in expected:
            assert locale in locales, \
                f"Expected locale '{locale}' not found for app '{app}'"
    
    client.close()
```

### Performance Testing

**Test application response times**:

```bash
# Install Apache Bench
# macOS: brew install httpd
# Ubuntu: apt-get install apache2-utils

# Test backend performance
ab -n 1000 -c 10 http://localhost:8002/api/health

# Test analyze endpoint (requires valid JSON)
ab -n 100 -c 5 -p analyze_payload.json -T application/json \
   http://localhost:8002/trusted_services/v2/apps/delphes/fr/analyze
```

### Load Testing

```python
# test_load.py
import httpx
import asyncio
import time

async def call_analyze(client, app, locale, text):
    """Single analyze API call"""
    response = await client.post(
        f"/trusted_services/v2/apps/{app}/{locale}/analyze",
        params={
            "field_values": "{}",
            "text": text,
            "read_from_cache": "false"
        }
    )
    return response.status_code

async def load_test():
    """Simulate multiple concurrent users"""
    async with httpx.AsyncClient(base_url="http://localhost:8002", timeout=60.0) as client:
        # Simulate 50 concurrent requests
        tasks = [
            call_analyze(client, "delphes", "fr", f"Test message {i}")
            for i in range(50)
        ]
        
        start = time.time()
        results = await asyncio.gather(*tasks)
        end = time.time()
        
        success_count = sum(1 for r in results if r == 200)
        print(f"Completed {len(results)} requests in {end-start:.2f}s")
        print(f"Success rate: {success_count}/{len(results)}")

if __name__ == "__main__":
    asyncio.run(load_test())
```

### Docker Image Testing

**Verify Docker images build and run correctly**:

```bash
# Test framework backend image
docker build -t test-backend -f src/Dockerfile.backend .
docker run --rm -p 8002:8002 test-backend &
sleep 10
curl http://localhost:8002/api/health
docker stop $(docker ps -q --filter ancestor=test-backend)

# Test Delphes frontend image
cd apps/delphes/frontend
docker build -t test-delphes-frontend -f Dockerfile.delphes-frontend .
docker run --rm -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8002 test-delphes-frontend &
sleep 15
curl http://localhost:3000/
docker stop $(docker ps -q --filter ancestor=test-delphes-frontend)
```

---

## Best Practices

### ✅ DO

- Write tests before fixing bugs
- Use descriptive test names
- Keep tests independent
- Mock external services
- Use fixtures for common setup
- Test edge cases and errors
- Keep tests fast
- Use appropriate markers

### ❌ DON'T

- Test implementation details
- Write dependent tests
- Hardcode test data
- Skip error handling
- Write long, complex tests
- Test third-party libraries
- Commit failing tests
- Ignore flaky tests

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Python](https://playwright.dev/python/)
- [HTTPX Documentation](https://www.python-httpx.org/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## Support

For questions or issues with tests:

1. Check this documentation
2. Review test examples in `tests/unit/test_example.py`
3. Check CI/CD logs in GitHub Actions
4. Create an issue with test output

---

*Last updated: November 2025*
