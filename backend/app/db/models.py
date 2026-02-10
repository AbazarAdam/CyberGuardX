from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from .database import Base


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    email_breached = Column(Boolean, nullable=False)
    phishing_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Enhanced breach information
    pwned_count = Column(Integer, nullable=True, default=0)  # Number of breaches
    breach_details = Column(Text, nullable=True)  # JSON string with breach details
    breach_source = Column(String, nullable=True)  # "local", "hibp_api", "cache"
    last_checked = Column(DateTime, nullable=True)  # Timestamp of last HIBP check


class WebsiteScan(Base):
    """Store comprehensive website security scan results."""
    __tablename__ = "website_scans"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False, index=True)
    client_ip = Column(String, nullable=False)
    
    # Overall risk assessment
    risk_score = Column(Integer, nullable=False)  # 0-100
    risk_level = Column(String, nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW, MINIMAL
    overall_grade = Column(String, nullable=False)  # A, B, C, D, F
    
    # Individual scan results (stored as JSON text)
    http_scan_json = Column(Text, nullable=True)  # HTTP headers scan
    ssl_scan_json = Column(Text, nullable=True)   # SSL/TLS scan
    dns_scan_json = Column(Text, nullable=True)   # DNS security scan
    tech_scan_json = Column(Text, nullable=True)  # Technology detection
    owasp_assessment_json = Column(Text, nullable=True)  # OWASP Top 10 mapping
    
    # Metadata
    scan_duration_ms = Column(Integer, nullable=True)  # Scan duration in milliseconds
    scanned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Legal/safety tracking
    permission_confirmed = Column(Boolean, default=False)
    owner_confirmed = Column(Boolean, default=False)
    legal_accepted = Column(Boolean, default=False)


class ScanProgress(Base):
    """Track real-time progress of website scans."""
    __tablename__ = "scan_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String, unique=True, nullable=False, index=True)  # UUID
    url = Column(String, nullable=False)
    
    # Progress tracking
    current_step = Column(String, nullable=False)  # Current step name
    progress_percentage = Column(Integer, nullable=False, default=0)  # 0-100
    step_details = Column(Text, nullable=True)  # JSON with sub-steps
    
    # Timing
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_update = Column(DateTime, default=datetime.utcnow, nullable=False)
    estimated_seconds_remaining = Column(Integer, nullable=True)
    
    # Status
    is_complete = Column(Boolean, default=False)
    has_error = Column(Boolean, default=False)
    error_message = Column(String, nullable=True)
    
    # Cancellation
    is_cancelled = Column(Boolean, default=False)
