# Testing Quick Start

## 🚀 Run Tests in 30 Seconds

### Install Test Dependencies (One Time)

```bash
pip install -r tests/requirements.txt
playwright install chromium
```

### Run Smoke Tests

```bash
# Option 1: Python script (recommended)
python run_tests.py smoke

# Option 2: Bash script (Unix/macOS)
./run_smoke_tests.sh all

# Option 3: Using Make
make test-smoke
```

## 📋 Common Commands

### Quick Testing

```bash
# Run all tests
make test

# Run only backend smoke tests (fastest)
python run_tests.py smoke --backend

# Run unit tests with coverage
make coverage
```

### Before Committing

```bash
# Check everything
make ci-all

# Or individually
make lint
make test-unit
make test-smoke
```

### Manual Service Testing

```bash
# Terminal 1: Backend
python launcher_api.py ./runtime

# Terminal 2: Frontend  
cd apps/delphes/frontend && npm run dev

# Terminal 3: Tests
pytest tests/smoke/test_backend_api.py -v
```

## ✅ Pre-Commit Checklist

- [ ] Run `make lint` - No linting errors
- [ ] Run `make test-unit` - All unit tests pass
- [ ] Run `make test-smoke` - Smoke tests pass
- [ ] Check `git status` - No unexpected files
- [ ] Write clear commit message

## 🐛 Troubleshooting

### Port in Use

```bash
# Check ports
make check-ports

# Kill servers
make kill-servers
```

### Tests Fail

```bash
# Run specific test with verbose output
pytest tests/smoke/test_backend_api.py::test_health_endpoint -vv

# Debug mode
pytest tests/smoke/ --pdb
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r tests/requirements.txt
```

## 📚 More Info

- Full testing guide: [TESTING.md](../TESTING.md)
- CI/CD workflows: [.github/workflows/](.github/workflows/)
- Writing tests: See `tests/unit/test_example.py`

## 🆘 Help

```bash
# Get help
python run_tests.py --help
make help
pytest --help
```

