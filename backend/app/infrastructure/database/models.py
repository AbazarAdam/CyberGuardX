"""
ORM Models
===========
SQLAlchemy table definitions for every persistent entity.

Tables
------
- **scan_history**   — email / URL scan audit log
- **website_scans**  — comprehensive website security assessments
- **scan_progress**  — real-time progress tracking for long-running scans
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from app.infrastructure.database.connection import Base


# ---------------------------------------------------------------------------
# Email / URL Scan History
# ---------------------------------------------------------------------------
class ScanHistory(Base):
    """Stores every email-breach and URL-phishing scan for audit purposes."""

    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    email_breached = Column(Boolean, nullable=False)
    phishing_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Enhanced breach information (added in v2.0)
    pwned_count = Column(Integer, nullable=True, default=0)
    breach_details = Column(Text, nullable=True)        # JSON string
    breach_source = Column(String, nullable=True)        # "local", "hibp_api", "cache"
    last_checked = Column(DateTime, nullable=True)


# ---------------------------------------------------------------------------
# Website Security Scan
# ---------------------------------------------------------------------------
class WebsiteScan(Base):
    """Stores full website security assessment results."""

    __tablename__ = "website_scans"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False, index=True)
    client_ip = Column(String, nullable=False)

    # Overall risk assessment
    risk_score = Column(Integer, nullable=False)         # 0-100
    risk_level = Column(String, nullable=False)          # CRITICAL / HIGH / MEDIUM / LOW / MINIMAL
    overall_grade = Column(String, nullable=False)       # A / B / C / D / F

    # Individual scan results (stored as JSON text for flexibility)
    http_scan_json = Column(Text, nullable=True)
    ssl_scan_json = Column(Text, nullable=True)
    dns_scan_json = Column(Text, nullable=True)
    tech_scan_json = Column(Text, nullable=True)
    owasp_assessment_json = Column(Text, nullable=True)

    # Metadata
    scan_duration_ms = Column(Integer, nullable=True)
    scanned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Legal / safety tracking
    permission_confirmed = Column(Boolean, default=False)
    owner_confirmed = Column(Boolean, default=False)
    legal_accepted = Column(Boolean, default=False)


# ---------------------------------------------------------------------------
# Scan Progress — real-time tracking for website scans
# ---------------------------------------------------------------------------
class ScanProgress(Base):
    """Tracks step-by-step progress for long-running website scans."""

    __tablename__ = "scan_progress"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String, unique=True, nullable=False, index=True)  # UUID

    url = Column(String, nullable=False)

    # Progress tracking
    current_step = Column(String, nullable=False)
    progress_percentage = Column(Integer, nullable=False, default=0)    # 0-100
    step_details = Column(Text, nullable=True)                          # JSON

    # Timing
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_update = Column(DateTime, default=datetime.utcnow, nullable=False)
    estimated_seconds_remaining = Column(Integer, nullable=True)

    # Status flags
    is_complete = Column(Boolean, default=False)
    has_error = Column(Boolean, default=False)
    error_message = Column(String, nullable=True)
    is_cancelled = Column(Boolean, default=False)
