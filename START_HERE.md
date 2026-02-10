# 🚀 CyberGuardX — Quick Start Guide

**Status:** ✅ **RUNNING** — Your application is currently live!

- **Frontend:** http://localhost:3000 *(Open in your browser)*
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs *(Interactive Swagger UI)*

---

## 📋 How to Start CyberGuardX

### **Method 1: Simple Batch File (Recommended)**

Double-click or run:
```cmd
run_cyberguardx.bat
```

This automatically starts both servers in separate windows.

---

### **Method 2: Manual Start**

**Terminal 1 - Backend:**
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
python -m http.server 3000
```

---

### **Method 3: Docker (Advanced)**

> ⚠️ **Requires Docker Desktop** — Not currently installed on your system.

If you install Docker Desktop from https://www.docker.com/products/docker-desktop:

```powershell
.\start-docker.ps1        # Development mode
.\start-docker.ps1 prod   # Production mode
```

---

## 🛠️ First Time Setup

If you get errors about missing packages:

```powershell
pip install -r requirements.txt
```

This installs all required dependencies including:
- FastAPI + Uvicorn (web framework)
- SQLAlchemy (database)
- scikit-learn (machine learning)
- Cryptography (security scanning)

---

## 🧪 Test the Application

1. **Open Frontend:** http://localhost:3000
2. **Try scanning a URL:**
   - Example: `https://google.com` (safe)
   - Example: `http://phishing-test.com` (will detect as phishing)

3. **Check email breach:**
   - Enter any email to check if it's in the breach database

4. **Analyze password:**
   - Test password strength and get security recommendations

---

## 📚 Available Features

| Feature | Endpoint | Description |
|---------|----------|-------------|
| **Website Scanner** | `/api/scan` | Full security analysis (OWASP, SSL, DNS, HTTP headers) |
| **URL Phishing Detection** | `/api/check-url` | ML-powered phishing URL detection |
| **Email Breach Check** | `/api/check-email` | Checks 100K+ breach records offline |
| **Password Analyzer** | `/api/check-password` | Strength analysis + security tips |
| **Scan History** | `/api/history` | View past security scans |

---

## 🐛 Troubleshooting

### Backend Won't Start
```powershell
# Reinstall dependencies
pip install -r requirements.txt

# Check if port 8000 is in use
netstat -ano | findstr :8000
```

### Frontend Won't Load
```powershell
# Check if port 3000 is in use
netstat -ano | findstr :3000

# Try different port
cd frontend
python -m http.server 8080
```

### Missing Module Errors
```powershell
# Install specific missing module
pip install pydantic[email]
pip install scikit-learn
pip install cryptography
```

---

## 🔒 Security Notes

- The application runs **locally** on your machine
- No data is sent to external servers (except HIBP API for optional online breach checks)
- Breach database is **offline** (100K+ records in local CSV)
- ML model is **local** (no cloud dependencies)

---

## 📖 Documentation

- **Technical Docs:** [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)
- **Docker Guide:** [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- **Deployment:** [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)
- **Project Report:** [FYP_REPORT.md](FYP_REPORT.md)

---

## 🎯 Current System Status

**✅ Backend Running:** Port 8000  
**✅ Frontend Running:** Port 3000  
**✅ Dependencies Installed:** All required packages available  
**✅ Database Ready:** SQLite database configured  
**✅ ML Model Ready:** Phishing detection model loaded  
**❌ Docker:** Not installed (optional)

---

### Need Help?

Check the logs in the terminal windows or visit http://localhost:8000/docs for interactive API testing.
