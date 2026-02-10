"""
CyberGuardX — Application Entry-Point
=======================================
Creates the FastAPI application, registers middleware, mounts all
route modules, and ensures the database tables exist at startup.

Architecture
------------
This module is the **Composition Root** that wires together the four
Clean-Architecture layers:

    Domain  →  Application  →  Infrastructure  →  Presentation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Infrastructure: database setup ────────────────────────────────────
from app.infrastructure.database.connection import Base, engine
from app.infrastructure.database import models  # noqa: F401  (registers ORM models)

# ── Presentation: route modules ──────────────────────────────────────
from app.presentation.routes import email, url, password, scanner, history

# ── Configuration ────────────────────────────────────────────────────
from app.config import CORS_ORIGINS

# ── Logging ──────────────────────────────────────────────────────────
from app.utils.logger import get_logger

logger = get_logger(__name__)

# =====================================================================
# Application factory
# =====================================================================

app = FastAPI(
    title="CyberGuardX",
    description=(
        "AI-powered cybersecurity platform — email breach checking, "
        "phishing URL detection, password strength analysis, and "
        "passive website security scanning."
    ),
    version="2.0.0",
)

# ── CORS middleware ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ────────────────────────────────────────────────
app.include_router(email.router,    tags=["Email"])
app.include_router(url.router,      tags=["URL"])
app.include_router(password.router, tags=["Password"])
app.include_router(scanner.router,  tags=["Website Scanner"])
app.include_router(history.router,  tags=["History"])

# ── Create database tables (idempotent) ─────────────────────────────
Base.metadata.create_all(bind=engine)
logger.info("Database tables initialized")


# ── Health-check ─────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """Simple health-check endpoint."""
    logger.debug("Health check requested")
    return {"project": "CyberGuardX", "version": "2.0.0", "status": "running"}

