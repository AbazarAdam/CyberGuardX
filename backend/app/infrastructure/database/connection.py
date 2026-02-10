"""
Database Connection
====================
Creates the SQLAlchemy engine and session factory.

Usage::

    from app.infrastructure.database.connection import SessionLocal, engine, Base
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

# ---------------------------------------------------------------------------
# Engine — single connection pool shared across the application
# ---------------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},   # Required for SQLite
)

# ---------------------------------------------------------------------------
# Session factory — call ``SessionLocal()`` to get a new DB session
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# Declarative base — all ORM models inherit from this
# ---------------------------------------------------------------------------
Base = declarative_base()
