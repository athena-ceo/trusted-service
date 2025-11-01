# Testing Guide - Trusted Services

Complete guide for running tests locally and understanding the CI/CD pipeline.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Types](#test-types)
- [Running Tests Locally](#running-tests-locally)
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

