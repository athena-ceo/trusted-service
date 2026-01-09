# Integration Tests Guide

## 🎯 What Was Fixed

The integration tests were failing because the backend service couldn't start in Docker. The issue was that the backend was configured to bind to `127.0.0.1` (localhost only), which doesn't work in Docker containers.

### The Solution

Created a **Docker entrypoint script** (`docker-entrypoint.sh`) that:
- Automatically converts `127.0.0.1` to `0.0.0.0` when running in Docker
- Maintains compatibility with local development
- No changes needed to Python code

## 🚀 Running Integration Tests Locally

### Option 1: Using Docker Compose (Recommended)

```bash
# Start all services
docker compose -f deploy/compose/docker-compose.trusted-services-dev.yml up -d

# Wait for services to be ready
timeout 90 bash -c 'until curl -f http://localhost:8002/api/health; do echo "Waiting..."; sleep 3; done'

# Run integration tests
pytest tests/integration/ -v

# Stop services
docker compose -f deploy/compose/docker-compose.trusted-services-dev.yml down -v
```

### Option 2: Using the Makefile

```bash
# Start services
make docker-up-dev

# In another terminal, run tests
pytest tests/integration/ -v

# Stop services
make docker-down-dev
```

## 🔍 Verifying Services are Running

### Check Backend Health

```bash
curl http://localhost:8002/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "trusted-services-backend",
  "timestamp": "2025-11-02T..."
}
```

### Check Frontend

```bash
curl http://localhost:3000/
```

### View Container Logs

```bash
# All services
docker compose -f deploy/compose/docker-compose.trusted-services-dev.yml logs

# Backend only
docker compose -f deploy/compose/docker-compose.trusted-services-dev.yml logs backend

# Frontend only
docker compose -f deploy/compose/docker-compose.trusted-services-dev.yml logs streamlit-client

# Follow logs in real-time
docker compose -f deploy/compose/docker-compose.trusted-services-dev.yml logs -f
```

## 📊 GitHub Actions CI/CD

Integration tests now run automatically on every push to `main`:

1. **Build backend Docker image** with entrypoint script
2. **Start services** via docker-compose
3. **Wait for health check** (90 second timeout)
4. **Verify services** are accessible
5. **Run pytest integration tests**
6. **Collect logs** on failure (uploaded as artifacts)

## 🐛 Troubleshooting

### Backend Not Starting

**Check container status:**
```bash
docker compose -f deploy/compose/docker-compose.trusted-services-dev.yml ps
```

**View backend logs:**
```bash
docker compose -f deploy/compose/docker-compose.trusted-services-dev.yml logs backend
```

**Common issues:**
- Missing `runtime/config_connection.yaml` → Entrypoint creates it automatically
- Port 8002 in use → Stop other services using that port
- Build cache issues → Run `docker compose build --no-cache backend`

### Connection Refused

**Problem:** Backend is running but connection refused

**Solution:** The entrypoint script should fix this automatically. Verify:
```bash
# Check if backend is binding to 0.0.0.0
docker compose -f deploy/compose/docker-compose.trusted-services-dev.yml exec backend netstat -tuln | grep 8002
```

Should show: `0.0.0.0:8002` not `127.0.0.1:8002`

### Tests Timing Out

**Increase timeout:**
```bash
# In pytest
pytest tests/integration/ -v --timeout=120

# In docker-compose health check
# Edit deploy/compose/docker-compose.trusted-services-dev.yml backend service:
healthcheck:
  start_period: 60s  # Increase from 30s
```

## 📝 Test Structure

### Integration Tests (`tests/integration/`)
- End-to-end workflows
- Multi-service interactions
- Real HTTP requests to backend

### Smoke Tests (`tests/smoke/`)
- Quick validation
- Critical endpoint checks
- Run on every build

### Unit Tests (`tests/unit/`)
- Individual component testing
- No external dependencies

## 🔧 Configuration Files

### For Docker:
- `deploy/compose/docker-compose.trusted-services-dev.yml` - Development/CI environment
- `src/Dockerfile.backend` - Backend image with entrypoint
- `deploy/compose/docker-entrypoint.sh` - Automatic 0.0.0.0 binding

### For Local Development:
- `runtime/config_connection.yaml` - Uses 127.0.0.1 (fine for local)
- Runs directly with `python launcher_api.py ./runtime`

## ✅ Success Criteria

Integration tests are working when:
- ✅ Backend starts in Docker without errors
- ✅ Health endpoint returns 200 OK
- ✅ Integration tests execute (not skipped)
- ✅ Tests pass or fail based on actual logic (not connection issues)

## 🎉 Next Steps

Now that integration tests work, you can:
1. Add more integration test scenarios
2. Test complex workflows
3. Validate multi-service interactions
4. Build confidence in deployments
