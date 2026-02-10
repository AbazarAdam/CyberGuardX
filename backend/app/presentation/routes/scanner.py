"""
Route — Website Security Scanner
==================================
Thin presentation layer for website security scanning endpoints.
Delegates business logic to WebsiteScanService (Clean Architecture).

Endpoints
---------
``POST /scan-website``                  — run a full passive scan
``GET  /website-scan-history``          — recent website scans
``GET  /scan-details/{scan_id}``        — full results for one scan
``GET  /scan-progress/{scan_id}``       — real-time progress (UUID)
``POST /scan-progress/{scan_id}/cancel``— cancel a running scan
``GET  /generate-report/{scan_id}``     — HTML security report
"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.presentation.schemas import (
    WebsiteScanRequest,
    WebsiteScanResponse,
    ScanProgressResponse,
)
from app.presentation.dependencies import get_db
from app.infrastructure.database.models import WebsiteScan
from app.application.services.progress_tracker import ProgressTracker
from app.application.services.website_scanner import WebsiteScanService
from app.application.services.report_generator import PDFReportGenerator
from app.infrastructure.security.vulnerability_engine import AdvancedVulnerabilityEngine
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ======================================================================
# POST /scan-website — full passive security assessment
# ======================================================================

@router.post("/scan-website", response_model=WebsiteScanResponse)
async def scan_website(
    request: WebsiteScanRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Comprehensive website security assessment (**passive checks only**).

    Performs:
      1. Safety validation (rate-limit, URL, permission flags)
      2. HTTP security headers analysis
      3. SSL / TLS configuration check
      4. DNS security records validation
      5. Technology fingerprinting
      6. Risk scoring & OWASP Top-10 mapping
      7. Deep vulnerability analysis
      8. Database persistence

    **LEGAL DISCLAIMER**: Only scan websites you own or have written
    permission to scan. Unauthorized scanning may be illegal under the
    CFAA and similar laws.
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    
    try:
        scanner_service = WebsiteScanService(db)
        result = scanner_service.scan_website(
            url=request.url,
            client_ip=client_ip,
            confirmed_permission=request.confirmed_permission,
            owner_confirmation=request.owner_confirmation,
            legal_responsibility=request.legal_responsibility,
        )
        
        return WebsiteScanResponse(**result)
        
    except ValueError as e:
        # Validation failed
        status = 403 if "permission" in str(e).lower() else 400
        raise HTTPException(status_code=status, detail=str(e))
    except Exception as e:
        logger.error(f"Scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


# ======================================================================
# GET /website-scan-history — website-specific scan list
# ======================================================================

@router.get("/website-scan-history")
async def get_website_scan_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Return the most recent website-scan summaries (max 100)."""
    limit = min(limit, 100)
    
    scans = (
        db.query(WebsiteScan)
        .order_by(WebsiteScan.scanned_at.desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "scan_id": s.id,
            "url": s.url,
            "risk_score": s.risk_score,
            "risk_level": s.risk_level,
            "overall_grade": s.overall_grade,
            "scanned_at": s.scanned_at.isoformat(),
            "scan_duration_ms": s.scan_duration_ms,
        }
        for s in scans
    ]


# ======================================================================
# GET /scan-details/{scan_id}
# ======================================================================

@router.get("/scan-details/{scan_id}")
async def get_scan_details(scan_id: int, db: Session = Depends(get_db)):
    """Retrieve the full result set for a single website scan."""
    scan = db.query(WebsiteScan).filter(WebsiteScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "scan_id": scan.id,
        "url": scan.url,
        "risk_score": scan.risk_score,
        "risk_level": scan.risk_level,
        "overall_grade": scan.overall_grade,
        "http_scan": json.loads(scan.http_scan_json) if scan.http_scan_json else {},
        "ssl_scan": json.loads(scan.ssl_scan_json) if scan.ssl_scan_json else {},
        "dns_scan": json.loads(scan.dns_scan_json) if scan.dns_scan_json else {},
        "tech_scan": json.loads(scan.tech_scan_json) if scan.tech_scan_json else {},
        "owasp_assessment": json.loads(scan.owasp_assessment_json) if scan.owasp_assessment_json else {},
        "scan_duration_ms": scan.scan_duration_ms,
        "scanned_at": scan.scanned_at.isoformat(),
        "client_ip": scan.client_ip,
    }


# ======================================================================
# GET /scan-progress/{scan_id}  &  POST .../cancel
# ======================================================================

@router.get("/scan-progress/{scan_id}", response_model=ScanProgressResponse)
async def get_scan_progress(scan_id: str, db: Session = Depends(get_db)):
    """Get real-time progress for a running website scan (UUID)."""
    tracker = ProgressTracker(db)
    progress = tracker.get_progress(scan_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanProgressResponse(**progress)


@router.post("/scan-progress/{scan_id}/cancel")
async def cancel_scan(scan_id: str, db: Session = Depends(get_db)):
    """Cancel a running website scan by UUID."""
    tracker = ProgressTracker(db)
    tracker.cancel_scan(scan_id)
    return {"message": "Scan cancelled successfully", "scan_id": scan_id}


# ======================================================================
# GET /generate-report/{scan_id}
# ======================================================================

@router.get("/generate-report/{scan_id}", response_class=HTMLResponse)
async def generate_report(scan_id: int, db: Session = Depends(get_db)):
    """
    Generate a professional HTML security report for a completed scan.

    The HTML can be viewed in a browser or printed to PDF via the
    browser's native print dialog.
    """
    scan = db.query(WebsiteScan).filter(WebsiteScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Parse stored JSON blobs
    http_scan = json.loads(scan.http_scan_json) if scan.http_scan_json else {}
    ssl_scan = json.loads(scan.ssl_scan_json) if scan.ssl_scan_json else {}
    dns_scan = json.loads(scan.dns_scan_json) if scan.dns_scan_json else {}
    tech_scan = json.loads(scan.tech_scan_json) if scan.tech_scan_json else {}
    owasp_data = json.loads(scan.owasp_assessment_json) if scan.owasp_assessment_json else {}

    # Re-run vulnerability analysis (lightweight)
    vuln_engine = AdvancedVulnerabilityEngine()
    vulnerability_analysis = vuln_engine.analyze(http_scan, ssl_scan, dns_scan, tech_scan)

    scan_data = {
        "url": scan.url,
        "scan_timestamp": scan.scanned_at.isoformat() if scan.scanned_at else "",
        "overall_grade": scan.overall_grade or "N/A",
        "risk_score": scan.risk_score or 0,
        "risk_level": scan.risk_level or "UNKNOWN",
        "http_grade": http_scan.get("grade", "N/A"),
        "ssl_grade": ssl_scan.get("grade", "N/A"),
        "dns_grade": dns_scan.get("grade", "N/A"),
        "scan_duration_ms": scan.scan_duration_ms or 0,
    }

    generator = PDFReportGenerator()
    html = generator.generate_html_report(
        scan_data=scan_data,
        vulnerability_analysis=vulnerability_analysis,
        owasp_data=owasp_data,
    )
    return HTMLResponse(content=html)
