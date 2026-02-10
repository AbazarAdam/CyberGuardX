"""
Route — Website Security Scanner
==================================
Orchestrates **passive** security scans across 7 modules, stores results
in the database, and exposes scan-progress / scan-detail / report
endpoints.

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
import time
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request
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

# Security scanner modules
from app.infrastructure.security.http_scanner import HTTPSecurityScanner
from app.infrastructure.security.ssl_scanner import SSLTLSScanner
from app.infrastructure.security.dns_scanner import DNSSecurityScanner
from app.infrastructure.security.tech_detector import TechnologyDetector
from app.infrastructure.security.owasp_assessor import OWASPAssessor
from app.infrastructure.security.risk_scorer import RiskScorer
from app.infrastructure.security.vulnerability_engine import AdvancedVulnerabilityEngine
from app.infrastructure.security.safety_validator import SafetyValidator

# Report generator
from app.application.services.report_generator import PDFReportGenerator

# Logging
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ======================================================================
# POST /scan-website — full passive security assessment
# ======================================================================

@router.post("/scan-website", response_model=WebsiteScanResponse)
async def scan_website(request: WebsiteScanRequest, http_request: Request):
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
    permission to scan.  Unauthorised scanning may be illegal under the
    CFAA and similar laws.
    """
    start_time = time.time()

    # Client IP for rate-limiting & audit trail
    client_ip = http_request.client.host if http_request.client else "unknown"

    # Database session (manual lifecycle — not via Depends)
    db = next(get_db())

    # Progress tracker
    tracker = ProgressTracker(db)
    scan_id = tracker.create_scan(request.url)

    try:
        # ── Step 1: Safety validation ─────────────────────────────────
        tracker.update_progress(scan_id, 1, 0)
        validator = SafetyValidator()

        is_valid, error_message, _meta = validator.validate_scan_request(
            url=request.url,
            client_ip=client_ip,
            confirmed_permission=request.confirmed_permission,
            owner_confirmation=request.owner_confirmation,
            legal_responsibility=request.legal_responsibility,
        )

        if not is_valid:
            tracker.set_error(scan_id, error_message)
            status = 403 if "permission" in error_message.lower() else 400
            raise HTTPException(status_code=status, detail=error_message)

        # ── Step 2–5: Passive scans ───────────────────────────────────
        scan_results: Dict[str, Any] = {}
        errors: list[str] = []

        # HTTP headers
        tracker.update_progress(scan_id, 2, 0)
        try:
            scan_results["http_headers"] = HTTPSecurityScanner().scan(request.url)
            tracker.update_progress(scan_id, 2, 3)
        except Exception as exc:
            errors.append(f"HTTP scan failed: {exc}")
            scan_results["http_headers"] = {"error": str(exc)}

        # SSL / TLS
        tracker.update_progress(scan_id, 3, 0)
        try:
            scan_results["ssl_tls"] = SSLTLSScanner().scan(request.url)
            tracker.update_progress(scan_id, 3, 2)
        except Exception as exc:
            errors.append(f"SSL scan failed: {exc}")
            scan_results["ssl_tls"] = {"error": str(exc)}

        # DNS security
        tracker.update_progress(scan_id, 4, 0)
        try:
            scan_results["dns_security"] = DNSSecurityScanner().scan(request.url)
            tracker.update_progress(scan_id, 4, 4)
        except Exception as exc:
            errors.append(f"DNS scan failed: {exc}")
            scan_results["dns_security"] = {"error": str(exc)}

        # Technology fingerprinting
        tracker.update_progress(scan_id, 5, 0)
        try:
            scan_results["technologies"] = TechnologyDetector().scan(request.url)
            tracker.update_progress(scan_id, 5, 3)
        except Exception as exc:
            errors.append(f"Tech detection failed: {exc}")
            scan_results["technologies"] = {"error": str(exc)}

        # ── Step 6: Risk scoring ──────────────────────────────────────
        tracker.update_progress(scan_id, 6, 0)
        risk_scorer = RiskScorer()
        risk_analysis = risk_scorer.calculate_risk(scan_results)
        tracker.update_progress(scan_id, 6, 1)

        # ── OWASP Top-10 mapping ─────────────────────────────────────
        owasp_assessor = OWASPAssessor()
        owasp_findings = owasp_assessor.assess(
            scan_results.get("http_headers", {}),
            scan_results.get("ssl_tls", {}),
            scan_results.get("dns_security", {}),
            scan_results.get("technologies", {}),
        )

        # ── Deep vulnerability analysis ──────────────────────────────
        vuln_engine = AdvancedVulnerabilityEngine()
        vulnerability_analysis = vuln_engine.analyze(
            scan_results.get("http_headers", {}),
            scan_results.get("ssl_tls", {}),
            scan_results.get("dns_security", {}),
            scan_results.get("technologies", {}),
        )

        # ── Step 7: Build recommendations ────────────────────────────
        tracker.update_progress(scan_id, 7, 0)
        scan_duration = time.time() - start_time
        scan_duration_ms = int(scan_duration * 1000)

        recommendations = _build_recommendations(scan_results)

        # Component grades
        http_grade = scan_results.get("http_headers", {}).get("grade", "N/A")
        ssl_grade = scan_results.get("ssl_tls", {}).get("grade", "N/A")
        dns_grade = scan_results.get("dns_security", {}).get("grade", "N/A")
        tech_grade = "B"  # sensible default

        risk_breakdown = risk_analysis.get("risk_breakdown", {})
        critical_count = len(risk_breakdown.get("critical_issues", []))
        high_count = len(risk_breakdown.get("high_issues", []))

        # ── Step 8: Persist to DB ────────────────────────────────────
        website_scan = WebsiteScan(
            url=request.url,
            client_ip=client_ip,
            risk_score=risk_analysis["weighted_risk_score"],
            risk_level=risk_analysis["overall_risk_level"],
            overall_grade=risk_analysis["overall_grade"],
            http_scan_json=json.dumps(scan_results.get("http_headers", {})),
            ssl_scan_json=json.dumps(scan_results.get("ssl_tls", {})),
            dns_scan_json=json.dumps(scan_results.get("dns_security", {})),
            tech_scan_json=json.dumps(scan_results.get("technologies", {})),
            owasp_assessment_json=json.dumps(owasp_findings),
            scan_duration_ms=scan_duration_ms,
            scanned_at=datetime.utcnow(),
            permission_confirmed=request.confirmed_permission,
            owner_confirmed=request.owner_confirmation,
            legal_accepted=request.legal_responsibility,
        )
        db.add(website_scan)
        db.commit()
        db.refresh(website_scan)

        tracker.complete_scan(scan_id)

        # ── Step 9: Build response ───────────────────────────────────
        security_summary = risk_analysis.get("security_summary", {})
        security_posture = security_summary.get("security_posture", "UNKNOWN")

        return WebsiteScanResponse(
            scan_id=website_scan.id,
            url=request.url,
            scan_timestamp=datetime.utcnow().isoformat(),
            progress_scan_id=str(scan_id),
            risk_score=risk_analysis["weighted_risk_score"],
            risk_level=risk_analysis["overall_risk_level"],
            overall_grade=risk_analysis["overall_grade"],
            security_posture=security_posture,
            http_grade=http_grade,
            ssl_grade=ssl_grade,
            dns_grade=dns_grade,
            tech_grade=tech_grade,
            owasp_compliance_score=owasp_findings.get("compliance_score", 0),
            compliant_categories=owasp_findings.get("compliant_count", 0),
            non_compliant_categories=owasp_findings.get("non_compliant_count", 0),
            top_risks=risk_analysis.get("top_risks", []),
            critical_issues_count=critical_count,
            high_issues_count=high_count,
            http_scan=scan_results.get("http_headers"),
            ssl_scan=scan_results.get("ssl_tls"),
            dns_scan=scan_results.get("dns_security"),
            tech_scan=scan_results.get("technologies"),
            owasp_assessment=owasp_findings,
            risk_analysis=risk_analysis,
            vulnerability_analysis=vulnerability_analysis,
            scan_duration_ms=scan_duration_ms,
            recommendations=recommendations,
        )

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        if "scan_id" in locals():
            tracker.set_error(scan_id, str(exc))
        raise HTTPException(status_code=500, detail=f"Scan failed: {exc}") from exc
    finally:
        db.close()


# ======================================================================
# GET /website-scan-history — website-specific scan list
# ======================================================================
# NOTE: renamed from ``/scan-history`` to avoid collision with the
# email/URL history route in ``history.py``.

@router.get("/website-scan-history")
async def get_website_scan_history(limit: int = 10):
    """Return the most recent website-scan summaries (max 100)."""
    limit = min(limit, 100)
    db = next(get_db())
    try:
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
    finally:
        db.close()


# ======================================================================
# GET /scan-details/{scan_id}
# ======================================================================

@router.get("/scan-details/{scan_id}")
async def get_scan_details(scan_id: int):
    """Retrieve the full result set for a single website scan."""
    db = next(get_db())
    try:
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
    finally:
        db.close()


# ======================================================================
# GET /scan-progress/{scan_id}  &  POST .../cancel
# ======================================================================

@router.get("/scan-progress/{scan_id}", response_model=ScanProgressResponse)
async def get_scan_progress(scan_id: str):
    """Get real-time progress for a running website scan (UUID)."""
    db = next(get_db())
    try:
        tracker = ProgressTracker(db)
        progress = tracker.get_progress(scan_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Scan not found")
        return ScanProgressResponse(**progress)
    finally:
        db.close()


@router.post("/scan-progress/{scan_id}/cancel")
async def cancel_scan(scan_id: str):
    """Cancel a running website scan by UUID."""
    db = next(get_db())
    try:
        tracker = ProgressTracker(db)
        tracker.cancel_scan(scan_id)
        return {"message": "Scan cancelled successfully", "scan_id": scan_id}
    finally:
        db.close()


# ======================================================================
# GET /generate-report/{scan_id}
# ======================================================================

@router.get("/generate-report/{scan_id}", response_class=HTMLResponse)
async def generate_report(scan_id: int):
    """
    Generate a professional HTML security report for a completed scan.

    The HTML can be viewed in a browser or printed to PDF via the
    browser's native print dialog.
    """
    db = next(get_db())
    try:
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

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {exc}",
        ) from exc
    finally:
        db.close()


# ======================================================================
# Private helpers
# ======================================================================

def _build_recommendations(scan_results: Dict[str, Any]) -> list[str]:
    """
    Compile actionable recommendations from the raw scan results.

    Categories: HTTP headers, SSL/TLS, and DNS.
    """
    recs: list[str] = []

    # HTTP headers
    http = scan_results.get("http_headers", {})
    if "missing_headers" in http:
        for header in http["missing_headers"]:
            hint = http.get("recommendations", {}).get(header, "Add this header")
            recs.append(f"[HTTP] {header}: {hint}")

    # SSL / TLS
    ssl = scan_results.get("ssl_tls", {})
    if not ssl.get("error"):
        if not ssl.get("valid_certificate", True):
            recs.append("[SSL] Obtain a valid SSL certificate from a trusted CA")
        if ssl.get("tls_version", "") < "TLSv1.2":
            recs.append("[SSL] Upgrade to TLS 1.2 or higher")

    # DNS
    dns = scan_results.get("dns_security", {})
    if not dns.get("error"):
        if not dns.get("spf_record"):
            recs.append("[DNS] Add SPF record to prevent email spoofing")
        if not dns.get("dmarc_record"):
            recs.append("[DNS] Add DMARC record for email authentication")

    return recs
