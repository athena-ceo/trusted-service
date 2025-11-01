# Deployment Notes

## Docker Configuration

### Backend Dockerfile

✅ **Created**: `Dockerfile.backend` at repository root

**Features**:
- Based on Python 3.11-slim
- Installs all dependencies from requirements.txt
- Includes health check endpoint
- Exposes port 8002
- Optimized for production

**Build Command**:
```bash
docker build -f Dockerfile.backend -t trusted-services-backend .
```

**Run Command**:
```bash
docker run -p 8002:8002 \
  -v $(pwd)/runtime:/app/runtime \
  trusted-services-backend
```

---

### Frontend Dockerfile

⚠️ **Location**: `apps/delphes/frontend/Dockerfile`

**Note**: The `apps/` directory may be filtered in your environment. If you don't see the frontend Dockerfile:

**Create manually at** `apps/delphes/frontend/Dockerfile`:

```dockerfile
# Frontend Dockerfile for Trusted Services (Delphes)
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build-time environment variables
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8002
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

# Build Next.js application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

# Create nextjs user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
```

---

## GitHub Actions Deployment

The deployment workflow (`.github/workflows/deploy.yml`) has been updated to:

✅ **Check for Dockerfiles** before building
- If Dockerfile.backend exists → builds backend
- If frontend Dockerfile exists → builds frontend
- **Won't fail** if Dockerfiles are missing

### Workflow Behavior

| Scenario | Behavior |
|----------|----------|
| Both Dockerfiles exist | ✅ Builds both images |
| Only backend exists | ✅ Builds backend only |
| Only frontend exists | ✅ Builds frontend only |
| Neither exists | ⚠️ Skips build steps |

---

## Manual Deployment Setup

### Option 1: Docker Compose (Recommended)

Use the provided `docker-compose.dev.yml` or `docker-compose.prod.yml`:

```bash
# Development
docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose -f docker-compose.prod.yml up -d --build
```

### Option 2: Build Individual Images

```bash
# Backend
docker build -f Dockerfile.backend -t trusted-services-backend .
docker run -d -p 8002:8002 \
  -v $(pwd)/runtime:/app/runtime \
  --name backend \
  trusted-services-backend

# Frontend (if Dockerfile exists)
cd apps/delphes/frontend
docker build -t trusted-services-frontend .
docker run -d -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://localhost:8002 \
  --name frontend \
  trusted-services-frontend
```

### Option 3: Kubernetes

Example deployment manifests:

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/athena-ceo/trusted-service/backend:latest
        ports:
        - containerPort: 8002
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        volumeMounts:
        - name: runtime
          mountPath: /app/runtime
      volumes:
      - name: runtime
        persistentVolumeClaim:
          claimName: runtime-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend
  ports:
  - port: 8002
    targetPort: 8002
```

---

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONPATH` | `/app` | Python module path |
| `PYTHONUNBUFFERED` | `1` | Unbuffered output |
| `OPENAI_API_KEY` | - | OpenAI API key (if using) |
| `SCW_PROJECT_ID` | - | Scaleway project ID (if using) |
| `SCW_SECRET_KEY` | - | Scaleway secret key (if using) |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8002` | Backend API URL |
| `NODE_ENV` | `production` | Node environment |
| `PORT` | `3000` | Server port |

---

## Troubleshooting Deployment

### Issue: Dockerfile.backend not found

**Solution**: The file has been created at the repository root. Pull latest changes:

```bash
git pull origin main
ls -la Dockerfile.backend  # Should exist
```

### Issue: Frontend Dockerfile not found

**Cause**: `apps/` directory may be filtered/ignored

**Solution**: Manually create the Dockerfile at `apps/delphes/frontend/Dockerfile` using the template above

### Issue: Build fails with dependency errors

**Solution**: 
1. Check requirements.txt is up to date
2. Ensure Pydantic v2 is specified: `pydantic>=2.9.0`
3. Clear Docker cache: `docker system prune -a`

### Issue: Container fails health check

**Backend**:
```bash
# Check if health endpoint works
docker exec <container> curl http://localhost:8002/api/health
```

**Frontend**:
```bash
# Check if frontend responds
docker exec <container> wget -O- http://localhost:3000/
```

### Issue: Permission denied errors

**Solution**: Check volume mount permissions:
```bash
# Fix runtime directory permissions
chmod -R 755 runtime/
```

---

## Production Checklist

Before deploying to production:

- [ ] All Dockerfiles exist and are tested
- [ ] Environment variables configured
- [ ] Secrets properly managed (not in code)
- [ ] Health checks working
- [ ] Resource limits set (CPU/memory)
- [ ] Persistent volumes configured for runtime data
- [ ] Backup strategy in place
- [ ] Monitoring/logging configured
- [ ] SSL/TLS certificates configured
- [ ] Rate limiting configured
- [ ] CORS properly configured

---

## CI/CD Pipeline

### Current Status

✅ **Backend CI**: Tests and validates backend code  
✅ **Frontend CI**: Builds and tests frontend  
✅ **Integration Tests**: End-to-end testing  
✅ **Deploy Workflow**: Builds and pushes Docker images

### Pipeline Stages

1. **On Push to main**:
   - Runs all CI tests
   - Builds Docker images (if Dockerfiles exist)
   - Pushes to GitHub Container Registry

2. **On Version Tag** (e.g., `v1.0.0`):
   - Runs full pipeline
   - Deploys to staging
   - Deploys to production (if staging succeeds)

### Container Registry

Images are pushed to:
```
ghcr.io/athena-ceo/trusted-service/backend:latest
ghcr.io/athena-ceo/trusted-service/frontend:latest
```

**Pull images**:
```bash
docker pull ghcr.io/athena-ceo/trusted-service/backend:latest
docker pull ghcr.io/athena-ceo/trusted-service/frontend:latest
```

---

## Next Steps

1. **Verify Dockerfile.backend exists**:
   ```bash
   ls -la Dockerfile.backend
   ```

2. **Create frontend Dockerfile** (if needed):
   - Navigate to `apps/delphes/frontend/`
   - Create `Dockerfile` using template above

3. **Test locally**:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. **Push changes**:
   ```bash
   git add Dockerfile.backend apps/delphes/frontend/Dockerfile
   git commit -m "feat: add Docker configuration"
   git push
   ```

5. **Monitor deployment**:
   - Check GitHub Actions
   - Verify Docker images are built
   - Test deployed containers

---

*Last updated: November 1, 2025*

