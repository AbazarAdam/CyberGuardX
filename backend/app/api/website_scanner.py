"""
CyberGuardX - Website Security Scanner API Endpoint
Orchestrates passive security assessments with ethical safeguards.
Enhanced with deep vulnerability analysis, compliance mapping, and report generation.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import time
import json

from ..api.schemas import WebsiteScanRequest, WebsiteScanResponse, ScanProgressResponse
from ..db.database import SessionLocal
from ..db.models import WebsiteScan
from ..security.safety_validator import SafetyValidator
from ..services.progress_tracker import ProgressTracker
from ..security.http_scanner import HTTPSecurityScanner
from ..security.ssl_scanner import SSLTLSScanner
from ..security.dns_scanner import DNSSecurityScanner
from ..security.tech_detector import TechnologyDetector
from ..security.owasp_assessor import OWASPAssessor
from ..security.risk_scorer import RiskScorer
from ..security.vulnerability_engine import AdvancedVulnerabilityEngine
from ..services.pdf_generator import PDFReportGenerator

router = APIRouter()


def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/scan-website", response_model=WebsiteScanResponse)
async def scan_website(request: WebsiteScanRequest, http_request: Request):
    """
    Comprehensive website security assessment (PASSIVE CHECKS ONLY).
    
    Performs:
    - HTTP security headers analysis
    - SSL/TLS configuration check
    - DNS security records validation
    - Technology fingerprinting
    - OWASP Top 10 compliance mapping
    
    **LEGAL DISCLAIMER**: Only scan websites you own or have written permission to scan.
    Unauthorized scanning may be illegal under CFAA and similar laws.
    
    Args:
        request: WebsiteScanRequest with URL and permission confirmation
        http_request: FastAPI request object for IP extraction
    
    Returns:
        WebsiteScanResponse with comprehensive security report
    
    Raises:
        HTTPException: If validation fails or scanning error occurs
    """
    start_time = time.time()
    
    # Extract client IP
    client_ip = http_request.client.host if http_request.client else "unknown"
    
    # Initialize database session
    db = next(get_db())
    
    # Initialize progress tracker
    tracker = ProgressTracker(db)
    scan_id = tracker.create_scan(request.url)
    
    try:
        # ===== STEP 1: SAFETY VALIDATION =====
        tracker.update_progress(scan_id, 1, 0)  # Step 1, substep 0
        validator = SafetyValidator()
        
        # Comprehensive validation including rate limiting, URL validation, and permission checks
        is_valid, error_message, validation_metadata = validator.validate_scan_request(
            url=request.url,
            client_ip=client_ip,
            confirmed_permission=request.confirmed_permission,
            owner_confirmation=request.owner_confirmation,
            legal_responsibility=request.legal_responsibility
        )
        
        if not is_valid:
            tracker.set_error(scan_id, error_message)
            raise HTTPException(
                status_code=403 if "permission" in error_message.lower() else 400,
                detail=error_message
            )
        
        # ===== STEP 2: PASSIVE SECURITY SCANS =====
        tracker.update_progress(scan_id, 2, 0)  # Step 2 - HTTP Headers
        scan_results = {}
        errors = []
        
        # HTTP Headers Scan
        try:
            http_scanner = HTTPSecurityScanner()
            scan_results["http_headers"] = http_scanner.scan(request.url)
            tracker.update_progress(scan_id, 2, 3)  # Midway through HTTP scan
        except Exception as e:
            errors.append(f"HTTP scan failed: {str(e)}")
            scan_results["http_headers"] = {"error": str(e)}
        
        # SSL/TLS Scan
        tracker.update_progress(scan_id, 3, 0)  # Step 3 - SSL/TLS
        try:
            ssl_scanner = SSLTLSScanner()
            scan_results["ssl_tls"] = ssl_scanner.scan(request.url)
            tracker.update_progress(scan_id, 3, 2)  # SSL scan complete
        except Exception as e:
            errors.append(f"SSL scan failed: {str(e)}")
            scan_results["ssl_tls"] = {"error": str(e)}
        
        # DNS Security Scan
        tracker.update_progress(scan_id, 4, 0)  # Step 4 - DNS Security
        try:
            dns_scanner = DNSSecurityScanner()
            scan_results["dns_security"] = dns_scanner.scan(request.url)
            tracker.update_progress(scan_id, 4, 4)  # DNS scan complete
        except Exception as e:
            errors.append(f"DNS scan failed: {str(e)}")
            scan_results["dns_security"] = {"error": str(e)}
        
        # Technology Detection
        tracker.update_progress(scan_id, 5, 0)  # Step 5 - Technology Detection
        try:
            tech_detector = TechnologyDetector()
            scan_results["technologies"] = tech_detector.scan(request.url)
            tracker.update_progress(scan_id, 5, 3)  # Tech detection complete
        except Exception as e:
            errors.append(f"Tech detection failed: {str(e)}")
            scan_results["technologies"] = {"error": str(e)}
        
        # ===== STEP 3: RISK SCORING =====
        tracker.update_progress(scan_id, 6, 0)  # Step 6 - Risk Calculation
        risk_scorer = RiskScorer()
        risk_analysis = risk_scorer.calculate_risk(scan_results)
        tracker.update_progress(scan_id, 6, 1)  # Risk weighing done
        
        # ===== STEP 4: OWASP TOP 10 MAPPING =====
        owasp_assessor = OWASPAssessor()
        owasp_findings = owasp_assessor.assess(
            scan_results.get("http_headers", {}),
            scan_results.get("ssl_tls", {}),
            scan_results.get("dns_security", {}),
            scan_results.get("technologies", {})
        )
        
        # ===== STEP 4.5: DEEP VULNERABILITY ANALYSIS =====
        vuln_engine = AdvancedVulnerabilityEngine()
        vulnerability_analysis = vuln_engine.analyze(
            scan_results.get("http_headers", {}),
            scan_results.get("ssl_tls", {}),
            scan_results.get("dns_security", {}),
            scan_results.get("technologies", {})
        )
        
        # ===== STEP 5: GENERATE EXECUTIVE SUMMARY =====
        tracker.update_progress(scan_id, 7, 0)  # Step 7 - Report Generation
        scan_duration = time.time() - start_time
        scan_duration_ms = int(scan_duration * 1000)
        
        # ===== STEP 6: COMPILE RECOMMENDATIONS =====
        recommendations = []
        
        # HTTP Headers recommendations
        if "http_headers" in scan_results and "missing_headers" in scan_results["http_headers"]:
            for header in scan_results["http_headers"]["missing_headers"]:
                rec = scan_results["http_headers"]["recommendations"].get(header, "Add this header")
                recommendations.append(f"[HTTP] {header}: {rec}")
        
        # SSL/TLS recommendations  
        if "ssl_tls" in scan_results and not scan_results["ssl_tls"].get("error"):
            ssl_data = scan_results["ssl_tls"]
            if not ssl_data.get("valid_certificate", True):
                recommendations.append("[SSL] Obtain a valid SSL certificate from a trusted CA")
            if ssl_data.get("tls_version", "") < "TLSv1.2":
                recommendations.append("[SSL] Upgrade to TLS 1.2 or higher")
        
        # DNS recommendations
        if "dns_security" in scan_results and not scan_results["dns_security"].get("error"):
            dns_data = scan_results["dns_security"]
            if not dns_data.get("spf_record"):
                recommendations.append("[DNS] Add SPF record to prevent email spoofing")
            if not dns_data.get("dmarc_record"):
                recommendations.append("[DNS] Add DMARC record for email authentication")
        
        # Calculate component grades
        http_grade = scan_results.get("http_headers", {}).get("grade", "N/A")
        ssl_grade = scan_results.get("ssl_tls", {}).get("grade", "N/A")
        dns_grade = scan_results.get("dns_security", {}).get("grade", "N/A")
        tech_grade = "B"  # Default tech grade
        
        # Extract issue counts from risk breakdown
        risk_breakdown = risk_analysis.get("risk_breakdown", {})
        critical_count = len(risk_breakdown.get("critical_issues", []))
        high_count = len(risk_breakdown.get("high_issues", []))
        medium_count = len(risk_breakdown.get("medium_issues", []))
        
        # ===== STEP 7: SAVE TO DATABASE =====
        import json
        
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
            legal_accepted=request.legal_responsibility
        )
        
        db.add(website_scan)
        db.commit()
        db.refresh(website_scan)
        
        # Mark scan as complete
        tracker.complete_scan(scan_id)
        
        # ===== STEP 8: BUILD RESPONSE =====
        # Get security summary from risk analysis
        security_summary = risk_analysis.get("security_summary", {})
        security_posture = security_summary.get("security_posture", "UNKNOWN")
        
        response = WebsiteScanResponse(
            scan_id=website_scan.id,
            url=request.url,
            scan_timestamp=datetime.utcnow().isoformat(),
            progress_scan_id=str(scan_id),  # Return progress tracking UUID
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
            recommendations=recommendations
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        if 'scan_id' in locals():
            tracker.set_error(scan_id, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Scan failed: {str(e)}"
        )
    finally:
        db.close()


@router.get("/scan-history")
async def get_scan_history(limit: int = 10):
    """
    Retrieve recent website scan history.
    
    Args:
        limit: Maximum number of records to return (default: 10, max: 100)
    
    Returns:
        List of recent scans with summary information
    """
    if limit > 100:
        limit = 100
    
    db = next(get_db())
    
    try:
        scans = db.query(WebsiteScan).order_by(
            WebsiteScan.scanned_at.desc()
        ).limit(limit).all()
        
        return [
            {
                "scan_id": scan.id,
                "url": scan.url,
                "risk_score": scan.risk_score,
                "risk_level": scan.risk_level,
                "overall_grade": scan.overall_grade,
                "scanned_at": scan.scanned_at.isoformat(),
                "scan_duration_ms": scan.scan_duration_ms
            }
            for scan in scans
        ]
    finally:
        db.close()


@router.get("/scan-details/{scan_id}")
async def get_scan_details(scan_id: int):
    """
    Retrieve full details of a specific scan.
    
    Args:
        scan_id: Database ID of the scan
    
    Returns:
        Complete scan results including all findings
    """
    import json
    
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
            "client_ip": scan.client_ip
        }
    finally:
        db.close()


@router.get("/scan-progress/{scan_id}", response_model=ScanProgressResponse)
async def get_scan_progress(scan_id: str):
    """
    Get real-time progress of a website scan.
    
    Args:
        scan_id: UUID of the scan
    
    Returns:
        Current progress information including steps, percentage, and time estimates
    """
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
    """
    Cancel a running website scan.
    
    Args:
        scan_id: UUID of the scan to cancel
    
    Returns:
        Success message
    """
    db = next(get_db())
    
    try:
        tracker = ProgressTracker(db)
        tracker.cancel_scan(scan_id)
        
        return {"message": "Scan cancelled successfully", "scan_id": scan_id}
    finally:
        db.close()


@router.get("/generate-report/{scan_id}", response_class=HTMLResponse)
async def generate_report(scan_id: int):
    """
    Generate a professional HTML security report for a completed scan.
    
    Args:
        scan_id: Database ID of the scan
    
    Returns:
        HTML report that can be viewed in browser or printed to PDF
    """
    db = next(get_db())
    
    try:
        scan = db.query(WebsiteScan).filter(WebsiteScan.id == scan_id).first()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Parse stored scan data
        http_scan = json.loads(scan.http_scan_json) if scan.http_scan_json else {}
        ssl_scan = json.loads(scan.ssl_scan_json) if scan.ssl_scan_json else {}
        dns_scan = json.loads(scan.dns_scan_json) if scan.dns_scan_json else {}
        tech_scan = json.loads(scan.tech_scan_json) if scan.tech_scan_json else {}
        owasp_data = json.loads(scan.owasp_assessment_json) if scan.owasp_assessment_json else {}
        
        # Re-run vulnerability analysis for the report
        vuln_engine = AdvancedVulnerabilityEngine()
        vulnerability_analysis = vuln_engine.analyze(http_scan, ssl_scan, dns_scan, tech_scan)
        
        # Build scan_data dict for report
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
        
        # Generate HTML report
        generator = PDFReportGenerator()
        html = generator.generate_html_report(
            scan_data=scan_data,
            vulnerability_analysis=vulnerability_analysis,
            owasp_data=owasp_data,
        )
        
        return HTMLResponse(content=html)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
    finally:
        db.close()
