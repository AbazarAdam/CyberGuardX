"""
CyberGuardX — Centralized Configuration
========================================
All application-wide settings live here for easy modification.
Change database URLs, CORS origins, rate-limit windows, etc. in one place.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths — resolved relative to the *backend/* directory
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]          # backend/
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# ---------------------------------------------------------------------------
# Database — PostgreSQL (production) or SQLite (development)
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cyberguardx:cyberguardx_secure_2026@localhost:5432/cyberguardx"
    # Fallback to SQLite for development: "sqlite:///./cyberguardx.db"
)

# ---------------------------------------------------------------------------
# Redis Cache
# ---------------------------------------------------------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
CACHE_TTL = 86400  # 24 hours

# ---------------------------------------------------------------------------
# CORS — allowed frontend origins
# ---------------------------------------------------------------------------
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ---------------------------------------------------------------------------
# Rate Limiting (website scanner)
# ---------------------------------------------------------------------------
RATE_LIMIT_WINDOW_SECONDS = 600          # 10 minutes between scans per IP

# ---------------------------------------------------------------------------
# ML Model
# ---------------------------------------------------------------------------
PHISHING_MODEL_PATH = MODELS_DIR / "phishing_model.pkl"
PHISHING_METADATA_PATH = MODELS_DIR / "phishing_model_metadata.json"

# ---------------------------------------------------------------------------
# Breach Database
# ---------------------------------------------------------------------------
BREACH_DB_PATH = DATA_DIR / "breaches.db"

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
DEFAULT_BACKEND_PORT = 8000
DEFAULT_FRONTEND_PORT = 3000
