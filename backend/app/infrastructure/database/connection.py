"""
Database Connection
====================
Creates the SQLAlchemy engine and session factory.

Usage::

    from app.infrastructure.database.connection import SessionLocal, engine, Base
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

from app.config import DATABASE_URL

# ---------------------------------------------------------------------------
# Engine — PostgreSQL connection pool shared across the application
# ---------------------------------------------------------------------------
_is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {}
if _is_sqlite:
    # SQLite needs this for thread safety
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL: optimized connection pooling
    engine_kwargs.update(
        poolclass=QueuePool,
        pool_size=20,           # Steady-state connections
        max_overflow=40,        # Burst capacity (total 60)
        pool_pre_ping=True,     # Auto-reconnect stale connections
        pool_recycle=3600,      # Recycle connections after 1 hour
    )

engine = create_engine(DATABASE_URL, **engine_kwargs)

# ---------------------------------------------------------------------------
# Session factory — call ``SessionLocal()`` to get a new DB session
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# Declarative base — all ORM models inherit from this
# ---------------------------------------------------------------------------
Base = declarative_base()
