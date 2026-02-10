"""
Pydantic Schemas
=================
Request and response models for every API endpoint.
Grouped by feature for easy navigation.

Naming convention
-----------------
- ``*Request``   — inbound JSON body
- ``*Response``  — outbound JSON response
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr


# ═══════════════════════════════════════════════════════════════════════════
# Email Breach Detection
# ═══════════════════════════════════════════════════════════════════════════

class EmailCheckRequest(BaseModel):
    email: EmailStr


class BreachDetail(BaseModel):
    """Individual breach information."""
    name: str
    date: str
    accounts: int
    data_classes: List[str]


class EmailCheckResponse(BaseModel):
    email: str
    breached: bool
    pwned_count: int = 0
    risk_level: str
    message: str
    breaches: Optional[List[BreachDetail]] = []
    recommendations: Optional[List[str]] = []
    last_checked: Optional[str] = None
    breach_source: Optional[str] = None          # "local", "hibp_api", "cache"


# ═══════════════════════════════════════════════════════════════════════════
# Phishing URL Detection
# ═══════════════════════════════════════════════════════════════════════════

class URLCheckRequest(BaseModel):
    url: str


class FeatureAnalysis(BaseModel):
    """Per-feature ML explainability detail."""
    feature: str
    value: float
    impact: float
    risk: str
    explanation: str


class ModelInfo(BaseModel):
    """Metadata about the trained ML model."""
    name: str
    version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float


class URLCheckResponse(BaseModel):
    url: str
    is_phishing: bool
    phishing_score: float
    confidence: float
    risk_level: str
    message: str
    model_info: Optional[ModelInfo] = None
    feature_importance: Optional[Dict[str, float]] = None
    feature_analysis: Optional[List[FeatureAnalysis]] = []
    recommendations: Optional[List[str]] = []


# ═══════════════════════════════════════════════════════════════════════════
# Scan History
# ═══════════════════════════════════════════════════════════════════════════

class ScanHistoryResponse(BaseModel):
    id: int
    email: str
    email_breached: bool
    phishing_score: Optional[float]
    risk_level: str
    scanned_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# Website Security Scanner
# ═══════════════════════════════════════════════════════════════════════════

class WebsiteScanRequest(BaseModel):
    """Request to scan a website for security vulnerabilities."""
    url: str
    confirmed_permission: bool = False
    owner_confirmation: bool = False
    legal_responsibility: bool = False


class WebsiteScanResponse(BaseModel):
    """Comprehensive website security scan response."""
    scan_id: int
    url: str
    scan_timestamp: str
    scan_duration_ms: int

    # Overall assessment
    risk_score: int                                # 0-100
    risk_level: str                                # CRITICAL / HIGH / MEDIUM / LOW / MINIMAL
    overall_grade: str                             # A / B / C / D / F

    # Issue counts
    critical_issues: int = 0
    high_issues: int = 0

    # Component results
    http_security: Optional[Dict[str, Any]] = None
    ssl_tls: Optional[Dict[str, Any]] = None
    dns_security: Optional[Dict[str, Any]] = None
    technologies: Optional[Dict[str, Any]] = None

    # OWASP & vulnerability analysis
    owasp_top_10: Optional[Dict[str, Any]] = None
    vulnerabilities: Optional[Dict[str, Any]] = None

    # Risk breakdown
    component_scores: Optional[Dict[str, Any]] = None

    # Recommendations
    recommendations: List[str] = []


class WebsiteScanHistoryResponse(BaseModel):
    id: int
    url: str
    risk_score: int
    risk_level: str
    overall_grade: str
    scanned_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# Real-Time Scan Progress
# ═══════════════════════════════════════════════════════════════════════════

class ScanProgressStepDetail(BaseModel):
    completed: List[str] = []
    current: Optional[str] = None
    remaining: List[str] = []


class ScanProgressResponse(BaseModel):
    scan_id: str
    url: str
    current_step: str
    progress_percentage: int                       # 0-100
    step_details: Optional[ScanProgressStepDetail] = None
    time_elapsed: str                              # "MM:SS"
    estimated_remaining: Optional[str] = None
    is_complete: bool
    has_error: bool = False
    error_message: Optional[str] = None
    is_cancelled: bool = False
