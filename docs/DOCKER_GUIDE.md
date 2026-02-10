# 🐳 CyberGuardX — Docker Deployment Guide

Complete guide for containerized deployment of CyberGuardX using Docker.

---

## 📋 Prerequisites

- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ (included with Docker Desktop)
- **Git**: For cloning the repository

---

## 🚀 Quick Start (3 Commands)

### 1️⃣ **Development Mode**
```powershell
# Start all services
docker-compose up

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 2️⃣ **Production Mode**
```powershell
# Build and start with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3️⃣ **Stop Services**
```powershell
# Stop containers (keep data)
docker-compose down

# Stop and remove volumes (delete data)
docker-compose down -v
```

---

## 📦 What's Included

### **Services:**

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| **Backend** | cyberguardx-backend | 8000 | FastAPI application |
| **Frontend** | cyberguardx-frontend | 3000 | Nginx serving static files |

### **Volumes (Persistent Data):**

| Volume | Purpose |
|--------|---------|
| `cyberguardx-database` | SQLite database files |
| `cyberguardx-logs` | Application logs |

---

## 🔧 Configuration

### **Environment Variables**

Create a `.env` file in the project root:

```env
# Server Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Database
DATABASE_URL=sqlite:///./database/cyberguardx.db

# Logging
LOG_LEVEL=INFO

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Security
RATE_LIMIT_WINDOW_SECONDS=600

# Development
DEBUG=False
```

Copy from template:
```powershell
cp .env.example .env
```

---

## 🛠️ Common Operations

### **Rebuild Containers**
```powershell
# Rebuild after code changes
docker-compose build

# Force rebuild (no cache)
docker-compose build --no-cache

# Rebuild and restart
docker-compose up --build
```

### **View Logs**
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### **Execute Commands in Container**
```powershell
# Open shell in backend container
docker-compose exec backend bash

# Run Python command
docker-compose exec backend python -c "from backend.app.main import app; print(app)"

# Generate breach database
docker-compose exec backend python -m backend.scripts.generate_breach_db --size 100000

# Train ML model
docker-compose exec backend python -m backend.app.infrastructure.ml.trainer
```

### **Database Operations**
```powershell
# Backup database
docker-compose exec backend cp /app/database/cyberguardx.db /app/database/backup.db

# Copy database out of container
docker cp cyberguardx-backend:/app/database/cyberguardx.db ./backup.db

# Restore database
docker cp ./backup.db cyberguardx-backend:/app/database/cyberguardx.db
```

### **Health Checks**
```powershell
# Check container health
docker-compose ps

# Test backend directly
curl http://localhost:8000/

# Test frontend
curl http://localhost:3000/
```

---

## 🏗️ Build Process

### **Multi-Stage Dockerfile**

The Dockerfile uses a multi-stage build for optimization:

1. **Builder Stage**: Installs dependencies
2. **Production Stage**: Copies only what's needed
   - Uses non-root user (`cyberguard`)
   - Minimal attack surface
   - Optimized for production

### **Image Size**
- **Full image**: ~450 MB
- **Python base**: ~130 MB
- **Dependencies**: ~320 MB

---

## 🔒 Security Best Practices

### **1. Non-Root User**
```dockerfile
# Container runs as user 'cyberguard' (UID 1000)
USER cyberguard
```

### **2. Read-Only Volumes**
```yaml
volumes:
  - ./backend:/app/backend:ro  # Read-only source code
```

### **3. Resource Limits**
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

### **4. Health Checks**
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 🌐 Network Architecture

```
┌─────────────────────────────────────────┐
│         External Network                │
│  (Internet / Local Network)             │
└────────────┬────────────────────────────┘
             │
             │ Port 3000 (HTTP)
             ▼
┌─────────────────────────────────────────┐
│     Nginx Frontend Container            │
│  - Serves static HTML/CSS/JS            │
│  - Reverse proxy to backend             │
└────────────┬────────────────────────────┘
             │
             │ Internal network (cyberguardx-network)
             │
             ▼
┌─────────────────────────────────────────┐
│     FastAPI Backend Container           │
│  - REST API on port 8000                │
│  - ML inference                         │
│  - Security scanning                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│     Persistent Volumes                  │
│  - Database (SQLite)                    │
│  - Logs                                 │
│  - ML models                            │
└─────────────────────────────────────────┘
```

---

## 📊 Monitoring & Debugging

### **Container Stats**
```powershell
# Real-time resource usage
docker stats cyberguardx-backend cyberguardx-frontend

# Disk usage
docker system df
```

### **Debugging Failed Containers**
```powershell
# Check container logs
docker-compose logs backend

# Inspect container
docker inspect cyberguardx-backend

# Check exit code
docker-compose ps
```

### **Performance Tuning**

**Increase workers** (production):
```yaml
command: ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]
```

**Memory limits**:
```yaml
deploy:
  resources:
    limits:
      memory: 4G
```

---

## 🚢 Production Deployment

### **Docker Hub**
```powershell
# Build and tag
docker build -t yourusername/cyberguardx:latest .

# Push to registry
docker push yourusername/cyberguardx:latest

# Pull on server
docker pull yourusername/cyberguardx:latest
```

### **Cloud Platforms**

#### **AWS ECS**
1. Push image to ECR
2. Create ECS task definition
3. Deploy to Fargate or EC2

#### **Google Cloud Run**
```powershell
gcloud run deploy cyberguardx \
  --image gcr.io/PROJECT_ID/cyberguardx \
  --platform managed \
  --region us-central1
```

#### **Azure Container Instances**
```powershell
az container create \
  --resource-group cyberguardx-rg \
  --name cyberguardx \
  --image yourusername/cyberguardx:latest \
  --dns-name-label cyberguardx \
  --ports 8000
```

---

## 🔧 Troubleshooting

### **Common Issues**

#### **Port Already in Use**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in .env
BACKEND_PORT=8001
```

#### **Permission Denied**
```powershell
# Ensure proper ownership
docker-compose exec backend chown -R cyberguard:cyberguard /app
```

#### **Database Locked**
```powershell
# Stop all containers
docker-compose down

# Remove database volume
docker volume rm cyberguardx-database

# Restart
docker-compose up
```

#### **Container Exits Immediately**
```powershell
# Check logs
docker-compose logs backend

# Run interactively to debug
docker-compose run --rm backend bash
```

---

## 🧹 Cleanup

### **Remove All Data**
```powershell
# Stop and remove everything
docker-compose down -v

# Remove images
docker rmi cyberguardx

# Clean system
docker system prune -a
```

### **Selective Cleanup**
```powershell
# Remove stopped containers only
docker-compose down

# Remove unused volumes
docker volume prune

# Remove unused images
docker image prune
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)

---

## ✅ Next Steps

After Docker setup:
1. ✅ Test locally: `docker-compose up`
2. ✅ Configure environment variables
3. ✅ Push to Git repository
4. ✅ Set up CI/CD (already configured in `.github/workflows/`)
5. ✅ Deploy to production cloud platform

---

**Need Help?** Check the main [README.md](../README.md) or open an issue on GitHub.
