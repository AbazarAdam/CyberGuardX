"""
CyberGuardX — Centralized Configuration
========================================
All application-wide settings live here for easy modification.
Change database URLs, CORS origins, rate-limit windows, etc. in one place.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths — resolved relative to the *backend/* directory
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]          # backend/
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./cyberguardx.db"

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
