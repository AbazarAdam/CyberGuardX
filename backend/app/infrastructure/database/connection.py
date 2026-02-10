"""
Database Connection
====================
Creates the SQLAlchemy engine and session factory.

Strategy:
    1. Try PostgreSQL (primary) — full connection pooling
    2. Auto-fallback to SQLite if PostgreSQL is unreachable

Usage::

    from app.infrastructure.database.connection import SessionLocal, engine, Base
"""

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

from app.config import DATABASE_URL, SQLITE_FALLBACK_URL

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper — build engine with the right settings for the given URL
# ---------------------------------------------------------------------------
def _build_engine(url: str):
    """Create a SQLAlchemy engine with appropriate settings."""
    kwargs = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs.update(
            poolclass=QueuePool,
            pool_size=20,           # Steady-state connections
            max_overflow=40,        # Burst capacity (total 60)
            pool_pre_ping=True,     # Auto-reconnect stale connections
            pool_recycle=3600,      # Recycle connections after 1 hour
        )
    return create_engine(url, **kwargs)


# ---------------------------------------------------------------------------
# Engine — PostgreSQL (primary) → SQLite (automatic fallback)
# ---------------------------------------------------------------------------
def _create_engine_with_fallback():
    """Try PostgreSQL first; fall back to SQLite if unreachable."""
    _engine = _build_engine(DATABASE_URL)
    active_url = DATABASE_URL

    if not DATABASE_URL.startswith("sqlite"):
        try:
            # Quick connectivity check
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Connected to PostgreSQL")
        except Exception as exc:
            logger.warning(
                "PostgreSQL unavailable (%s). Falling back to SQLite.", exc
            )
            _engine.dispose()
            _engine = _build_engine(SQLITE_FALLBACK_URL)
            active_url = SQLITE_FALLBACK_URL
            logger.info("✓ Using SQLite fallback: %s", SQLITE_FALLBACK_URL)
    else:
        logger.info("✓ Using SQLite: %s", DATABASE_URL)

    return _engine, active_url


engine, ACTIVE_DATABASE_URL = _create_engine_with_fallback()

# ---------------------------------------------------------------------------
# Session factory — call ``SessionLocal()`` to get a new DB session
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# Declarative base — all ORM models inherit from this
# ---------------------------------------------------------------------------
Base = declarative_base()
