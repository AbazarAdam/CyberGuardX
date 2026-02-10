from datetime import datetime
from typing import Optional, Dict, List, Any

from pydantic import BaseModel, EmailStr, HttpUrl


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
    breach_source: Optional[str] = None  # "local", "hibp_api", "cache", "simulation"


class URLCheckRequest(BaseModel):
    url: str


class FeatureAnalysis(BaseModel):
    """Detailed feature analysis for ML explainability."""
    feature: str
    value: float
    impact: float
    risk: str
    explanation: str


class ModelInfo(BaseModel):
    """ML model metadata."""
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
    confidence: float  # How confident the model is
    risk_level: str
    message: str
    model_info: Optional[ModelInfo] = None
    feature_importance: Optional[Dict[str, float]] = None
    feature_analysis: Optional[List[FeatureAnalysis]] = []
    recommendations: Optional[List[str]] = []


class ScanHistoryResponse(BaseModel):
    id: int
    email: str
    email_breached: bool
    phishing_score: Optional[float]
    risk_level: str
    scanned_at: datetime


# Website Security Scanner Schemas

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
    progress_scan_id: Optional[str] = None  # UUID for progress tracking
    
    # Overall assessment
    risk_score: int  # 0-100
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW, MINIMAL
    overall_grade: str  # A, B, C, D, F
    security_posture: str  # EXCELLENT, GOOD, FAIR, POOR, CRITICAL
    
    # Component grades
    http_grade: str
    ssl_grade: str
    dns_grade: str
    tech_grade: str
    
    # OWASP compliance
    owasp_compliance_score: int
    compliant_categories: int
    non_compliant_categories: int
    
    # Top risks
    top_risks: List[Dict[str, Any]]
    critical_issues_count: int
    high_issues_count: int
    
    # Detailed results (optional, can be fetched separately)
    http_scan: Optional[Dict[str, Any]] = None
    ssl_scan: Optional[Dict[str, Any]] = None
    dns_scan: Optional[Dict[str, Any]] = None
    tech_scan: Optional[Dict[str, Any]] = None
    owasp_assessment: Optional[Dict[str, Any]] = None
    risk_analysis: Optional[Dict[str, Any]] = None
    vulnerability_analysis: Optional[Dict[str, Any]] = None
    
    scan_duration_ms: int
    recommendations: List[str]


class WebsiteScanHistoryResponse(BaseModel):
    """Historical website scan record."""
    id: int
    url: str
    risk_score: int
    risk_level: str
    overall_grade: str
    scanned_at: datetime


class LegalDisclaimerResponse(BaseModel):
    """Legal disclaimer and terms of use."""
    title: str
    warning: str
    terms: List[str]
    required_confirmations: List[Dict[str, str]]
    rate_limiting: str
    scope: str
    methods: str


# Real-Time Scan Progress Schemas

class ScanProgressStepDetail(BaseModel):
    """Details about scan sub-steps."""
    completed: List[str] = []
    current: Optional[str] = None
    remaining: List[str] = []


class ScanProgressResponse(BaseModel):
    """Real-time scan progress information."""
    scan_id: str
    url: str
    current_step: str
    progress_percentage: int  # 0-100
    step_details: Optional[ScanProgressStepDetail] = None
    time_elapsed: str  # "00:00:12"
    estimated_remaining: Optional[str] = None  # "00:00:38"
    is_complete: bool
    has_error: bool = False
    error_message: Optional[str] = None
    is_cancelled: bool = False
