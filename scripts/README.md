# 🚀 CyberGuardX — Run Scripts

Convenient scripts to run CyberGuardX in different configurations.

---

## 📋 Available Scripts

### 🐳 Docker Scripts

#### `run_docker.bat`
**Full Docker deployment** — Everything runs in containers

```bash
scripts\run_docker.bat
```

- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ Backend API (port 8000)
- ✅ Frontend (port 3000)

**Best for:** Production-like environment, quick testing

---

### 💻 Local Development Scripts

#### `run_backend_local.bat`
**Backend local + Infrastructure in Docker**

```bash
scripts\run_backend_local.bat
```

- 🐳 PostgreSQL in Docker
- 🐳 Redis in Docker
- 💻 Backend FastAPI (local Python)

**Best for:** Backend development with hot-reload

---

#### `run_frontend_local.bat`
**Frontend local server**

```bash
scripts\run_frontend_local.bat
```

- 💻 Frontend (Python HTTP server on port 3000)

**Best for:** Frontend development, CSS/JS changes

---

#### `run_full_local.bat`
**Everything local except infrastructure**

```bash
scripts\run_full_local.bat
```

- 🐳 PostgreSQL + Redis in Docker
- 💻 Backend in new window (hot-reload)
- 💻 Frontend in new window

**Best for:** Full-stack local development

---

### 🛠️ Utility Scripts

#### `setup_dev_environment.bat`
**One-time setup** — Prepares development environment

```bash
scripts\setup_dev_environment.bat
```

**Sets up:**
- Python virtual environment
- Dependencies installation
- Docker images pull
- .env configuration

**Run this first!**

---

#### `stop_all.bat`
**Stop everything** — Cleanup script

```bash
scripts\stop_all.bat
```

- Stops all Docker containers
- Cleans up processes

---

## 🎯 Quick Start Guide

### First Time Setup

1. **Run setup script:**
   ```bash
   scripts\setup_dev_environment.bat
   ```

2. **Choose your workflow:**

   **Option A: Full Docker (Easiest)**
   ```bash
   scripts\run_docker.bat
   ```

   **Option B: Local Development (Best for coding)**
   ```bash
   scripts\run_full_local.bat
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 📊 Comparison Table

| Script | PostgreSQL | Redis | Backend | Frontend | Use Case |
|--------|-----------|-------|---------|----------|----------|
| `run_docker.bat` | 🐳 Docker | 🐳 Docker | 🐳 Docker | 🐳 Docker | Production-like |
| `run_backend_local.bat` | 🐳 Docker | 🐳 Docker | 💻 Local | ❌ Manual | Backend dev |
| `run_frontend_local.bat` | ❌ Manual | ❌ Manual | ❌ Manual | 💻 Local | Frontend dev |
| `run_full_local.bat` | 🐳 Docker | 🐳 Docker | 💻 Local | 💻 Local | Full-stack dev |

---

## 🔧 Prerequisites

### Required
- **Python 3.10+** — https://www.python.org/downloads/
- **Docker Desktop** — https://www.docker.com/products/docker-desktop/

### Optional
- **Git** — For version control
- **VS Code** — Recommended IDE

---

## 🐛 Troubleshooting

### "Docker is not running"
**Solution:** Start Docker Desktop and wait for it to fully start

### "Python is not installed"
**Solution:** Install Python 3.10+ and add to PATH

### "Port already in use"
**Solutions:**
1. Stop other services using those ports
2. Change ports in `docker-compose.yml`
3. Run `scripts\stop_all.bat` first

### "Module not found"
**Solution:** Re-run `scripts\setup_dev_environment.bat`

---

## 📝 Development Workflow

### Backend Changes (Hot-Reload)
```bash
# Terminal 1: Infrastructure
docker-compose up -d postgres redis

# Terminal 2: Backend (auto-reloads on changes)
scripts\run_backend_local.bat
```

### Frontend Changes
```bash
# Make changes to HTML/CSS/JS
# Refresh browser (no restart needed)
```

### Database Changes
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

---

## 🚀 Production Deployment

For production, use:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Production checklist:**
- [ ] Update `.env` with secure passwords
- [ ] Set `DEBUG=False`
- [ ] Configure CORS origins
- [ ] Enable HTTPS
- [ ] Set up monitoring

---

## 📚 Related Documentation

- [Main README](../README.md) — Project overview
- [Technical Docs](../docs/TECHNICAL_DOCS.md) — Architecture
- [Docker Compose](../docker-compose.yml) — Container configuration
- [Requirements](../requirements.txt) — Python dependencies

---

**Need help?** Check the [documentation folder](../docs/) or open an issue!
