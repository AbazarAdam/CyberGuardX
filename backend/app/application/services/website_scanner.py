"""
Application Service — Website Security Scanner
===============================================
Orchestrates comprehensive website security assessments by coordinating
multiple infrastructure scanners and persisting results.

This service implements the Use Case layer of Clean Architecture.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

from sqlalchemy.orm import Session

from app.infrastructure.database.models import WebsiteScan
from app.application.services.progress_tracker import ProgressTracker
from app.infrastructure.security.http_scanner import HTTPSecurityScanner
from app.infrastructure.security.ssl_scanner import SSLTLSScanner
from app.infrastructure.security.dns_scanner import DNSSecurityScanner
from app.infrastructure.security.tech_detector import TechnologyDetector
from app.infrastructure.security.owasp_assessor import OWASPAssessor
from app.infrastructure.security.risk_scorer import RiskScorer
from app.infrastructure.security.vulnerability_engine import AdvancedVulnerabilityEngine
from app.infrastructure.security.safety_validator import SafetyValidator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WebsiteScanService:
    """
    Coordinates website security scanning workflow.
    
    Responsibilities:
    - Validate scan requests for safety and permissions
    - Orchestrate security scanners (HTTP, SSL, DNS, Tech)
    - Calculate risk scores and OWASP mappings
    - Perform vulnerability analysis
    - Track scan progress
    - Persist results to database
    """

    def __init__(self, db: Session):
        self.db = db
        self.tracker = ProgressTracker(db)
        self.validator = SafetyValidator()
        self.http_scanner = HTTPSecurityScanner()
        self.ssl_scanner = SSLTLSScanner()
        self.dns_scanner = DNSSecurityScanner()
        self.tech_detector = TechnologyDetector()
        self.risk_scorer = RiskScorer()
        self.owasp_assessor = OWASPAssessor()
        self.vuln_engine = AdvancedVulnerabilityEngine()

    def scan_website(
        self,
        url: str,
        client_ip: str,
        confirmed_permission: bool,
        owner_confirmation: bool,
        legal_responsibility: bool,
    ) -> Dict[str, Any]:
        """
        Execute comprehensive website security scan.
        
        Args:
            url: Target URL to scan
            client_ip: Client IP address for rate limiting
            confirmed_permission: Permission flag
            owner_confirmation: Ownership flag
            legal_responsibility: Legal disclaimer acceptance
            
        Returns:
            Complete scan results with risk analysis
            
        Raises:
            ValueError: If validation fails
        """
        start_time = time.time()
        scan_id = self.tracker.create_scan(url)

        try:
            # Step 1: Validate request
            self._validate_request(
                scan_id, url, client_ip,
                confirmed_permission, owner_confirmation, legal_responsibility
            )

            # Steps 2-5: Run security scans
            scan_results = self._run_security_scans(scan_id, url)

            # Step 6: Calculate risk
            risk_analysis = self._calculate_risk(scan_id, scan_results)

            # Additional analysis
            owasp_findings = self._assess_owasp(scan_results)
            vulnerability_analysis = self._analyze_vulnerabilities(scan_results)

            # Step 7: Build results
            scan_duration = time.time() - start_time
            recommendations = self._build_recommendations(scan_results)

            # Step 8: Persist to database
            db_scan = self._persist_scan(
                url, client_ip, scan_results,
                risk_analysis, vulnerability_analysis,
                owasp_findings, recommendations, scan_duration
            )

            # Mark complete
            self.tracker.set_complete(scan_id)

            return self._build_response(
                db_scan, scan_results, risk_analysis,
                vulnerability_analysis, owasp_findings,
                recommendations, scan_duration
            )

        except Exception as e:
            self.tracker.set_error(scan_id, str(e))
            logger.error(f"Scan failed for {url}: {e}", exc_info=True)
            raise

    def _validate_request(
        self, scan_id: str, url: str, client_ip: str,
        confirmed_permission: bool, owner_confirmation: bool,
        legal_responsibility: bool
    ) -> None:
        """Validate scan request for safety and permissions."""
        self.tracker.update_progress(scan_id, 1, 0)

        is_valid, error_message, _ = self.validator.validate_scan_request(
            url=url,
            client_ip=client_ip,
            confirmed_permission=confirmed_permission,
            owner_confirmation=owner_confirmation,
            legal_responsibility=legal_responsibility,
        )

        if not is_valid:
            self.tracker.set_error(scan_id, error_message)
            raise ValueError(error_message)

    def _run_security_scans(self, scan_id: str, url: str) -> Dict[str, Any]:
        """Execute all security scanner modules (parallel where possible)."""
        results = {}
        errors = []

        # Try async-parallel execution; fall back to sequential sync
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # We're inside an async context (FastAPI) — run scans concurrently
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                # Submit all sync scanners to thread pool
                futures = {
                    "http_headers": pool.submit(self._scan_http, scan_id, url),
                    "ssl_tls": pool.submit(self._scan_ssl, scan_id, url),
                    "dns_security": pool.submit(self._scan_dns, scan_id, url),
                    "technologies": pool.submit(self._scan_tech, scan_id, url),
                }
                for key, future in futures.items():
                    try:
                        results[key] = future.result(timeout=30)
                    except Exception as exc:
                        logger.error(f"{key} scan failed: {exc}")
                        errors.append(f"{key} scan failed: {exc}")
                        results[key] = {"error": str(exc), "success": False}
        else:
            # Sequential fallback
            results["http_headers"] = self._scan_http(scan_id, url)
            results["ssl_tls"] = self._scan_ssl(scan_id, url)
            results["dns_security"] = self._scan_dns(scan_id, url)
            results["technologies"] = self._scan_tech(scan_id, url)

        if errors:
            results["scan_errors"] = errors

        return results

    def _scan_http(self, scan_id: str, url: str) -> Dict[str, Any]:
        """Run HTTP headers scan."""
        self.tracker.update_progress(scan_id, 2, 0)
        try:
            result = self.http_scanner.scan(url)
            self.tracker.update_progress(scan_id, 2, 3)
            return result
        except Exception as exc:
            logger.error(f"HTTP scan failed: {exc}")
            return {"error": str(exc), "success": False}

    def _scan_ssl(self, scan_id: str, url: str) -> Dict[str, Any]:
        """Run SSL/TLS scan."""
        self.tracker.update_progress(scan_id, 3, 0)
        try:
            result = self.ssl_scanner.scan(url)
            self.tracker.update_progress(scan_id, 3, 2)
            return result
        except Exception as exc:
            logger.error(f"SSL scan failed: {exc}")
            return {"error": str(exc), "success": False}

    def _scan_dns(self, scan_id: str, url: str) -> Dict[str, Any]:
        """Run DNS security scan."""
        self.tracker.update_progress(scan_id, 4, 0)
        try:
            result = self.dns_scanner.scan(url)
            self.tracker.update_progress(scan_id, 4, 4)
            return result
        except Exception as exc:
            logger.error(f"DNS scan failed: {exc}")
            return {"error": str(exc), "success": False}

    def _scan_tech(self, scan_id: str, url: str) -> Dict[str, Any]:
        """Run technology detection scan."""
        self.tracker.update_progress(scan_id, 5, 0)
        try:
            result = self.tech_detector.scan(url)
            self.tracker.update_progress(scan_id, 5, 3)
            return result
        except Exception as exc:
            logger.error(f"Tech scan failed: {exc}")
            return {"error": str(exc), "success": False}

    def _calculate_risk(self, scan_id: str, scan_results: Dict) -> Dict[str, Any]:
        """Calculate comprehensive risk score."""
        self.tracker.update_progress(scan_id, 6, 0)
        risk_analysis = self.risk_scorer.calculate_risk(scan_results)
        self.tracker.update_progress(scan_id, 6, 1)
        return risk_analysis

    def _assess_owasp(self, scan_results: Dict) -> Dict[str, Any]:
        """Map findings to OWASP Top 10."""
        return self.owasp_assessor.assess(
            scan_results.get("http_headers", {}),
            scan_results.get("ssl_tls", {}),
            scan_results.get("dns_security", {}),
            scan_results.get("technologies", {}),
        )

    def _analyze_vulnerabilities(self, scan_results: Dict) -> Dict[str, Any]:
        """Perform deep vulnerability analysis."""
        return self.vuln_engine.analyze(
            scan_results.get("http_headers", {}),
            scan_results.get("ssl_tls", {}),
            scan_results.get("dns_security", {}),
            scan_results.get("technologies", {}),
        )

    def _build_recommendations(self, scan_results: Dict) -> List[str]:
        """Generate actionable security recommendations."""
        recommendations = []

        http_scan = scan_results.get("http_headers", {})
        ssl_scan = scan_results.get("ssl_tls", {})
        dns_scan = scan_results.get("dns_security", {})

        # HTTP headers
        missing_headers = http_scan.get("missing_headers", [])
        if "Content-Security-Policy" in missing_headers:
            recommendations.append("Implement Content-Security-Policy header to prevent XSS attacks")
        if "Strict-Transport-Security" in missing_headers:
            recommendations.append("Enable HSTS to enforce HTTPS connections")

        # SSL/TLS
        if not ssl_scan.get("valid", False):
            recommendations.append("Fix SSL/TLS configuration - certificate or protocol issues detected")
        
        # DNS
        if not dns_scan.get("spf_record"):
            recommendations.append("Add SPF record to prevent email spoofing")
        if not dns_scan.get("dmarc_record"):
            recommendations.append("Implement DMARC for email authentication")

        if not recommendations:
            recommendations.append("Excellent security posture - maintain current protections")

        return recommendations

    def _persist_scan(
        self,
        url: str,
        client_ip: str,
        scan_results: Dict,
        risk_analysis: Dict,
        vulnerability_analysis: Dict,
        owasp_findings: Dict,
        recommendations: List[str],
        scan_duration: float,
    ) -> WebsiteScan:
        """Save scan results to database."""
        website_scan = WebsiteScan(
            url=url,
            client_ip=client_ip,
            risk_score=risk_analysis["weighted_risk_score"],
            risk_level=risk_analysis["overall_risk_level"],
            overall_grade=risk_analysis["overall_grade"],
            http_scan_json=json.dumps(scan_results.get("http_headers", {})),
            ssl_scan_json=json.dumps(scan_results.get("ssl_tls", {})),
            dns_scan_json=json.dumps(scan_results.get("dns_security", {})),
            tech_scan_json=json.dumps(scan_results.get("technologies", {})),
            vulnerabilities_json=json.dumps(vulnerability_analysis),
            owasp_findings_json=json.dumps(owasp_findings),
            recommendations_json=json.dumps(recommendations),
            scan_duration_ms=int(scan_duration * 1000),
        )

        self.db.add(website_scan)
        self.db.commit()
        self.db.refresh(website_scan)

        logger.info(f"Scan persisted: {url} (ID: {website_scan.id})")
        return website_scan

    def _build_response(
        self,
        db_scan: WebsiteScan,
        scan_results: Dict,
        risk_analysis: Dict,
        vulnerability_analysis: Dict,
        owasp_findings: Dict,
        recommendations: List[str],
        scan_duration: float,
    ) -> Dict[str, Any]:
        """Build API response."""
        http_scan = scan_results.get("http_headers", {})
        ssl_scan = scan_results.get("ssl_tls", {})
        dns_scan = scan_results.get("dns_security", {})
        tech_scan = scan_results.get("technologies", {})

        risk_breakdown = risk_analysis.get("risk_breakdown", {})
        critical_count = len(risk_breakdown.get("critical_issues", []))
        high_count = len(risk_breakdown.get("high_issues", []))

        return {
            "scan_id": db_scan.id,
            "url": db_scan.url,
            "scan_timestamp": db_scan.scanned_at.isoformat(),
            "scan_duration_ms": db_scan.scan_duration_ms,
            "risk_score": db_scan.risk_score,
            "risk_level": db_scan.risk_level,
            "overall_grade": db_scan.overall_grade,
            "critical_issues": critical_count,
            "high_issues": high_count,
            "http_security": {
                "grade": http_scan.get("grade", "N/A"),
                "score": http_scan.get("score", 0),
                "missing_headers": http_scan.get("missing_headers", []),
                "risk_points": http_scan.get("risk_points", 0),
            },
            "ssl_tls": {
                "grade": ssl_scan.get("grade", "N/A"),
                "valid": ssl_scan.get("valid", False),
                "protocol": ssl_scan.get("protocol", "N/A"),
                "risk_points": ssl_scan.get("risk_points", 0),
            },
            "dns_security": {
                "grade": dns_scan.get("grade", "N/A"),
                "spf_record": dns_scan.get("spf_record"),
                "dmarc_record": dns_scan.get("dmarc_record"),
                "risk_points": dns_scan.get("risk_points", 0),
            },
            "technologies": {
                "detected": tech_scan.get("technologies_detected", []),
                "vulnerabilities": tech_scan.get("vulnerabilities", []),
            },
            "owasp_top_10": {
                "findings": owasp_findings.get("findings", []),
                "total_risks": owasp_findings.get("total_risks", 0),
            },
            "vulnerabilities": {
                "total": vulnerability_analysis.get("total_vulnerabilities", 0),
                "by_severity": vulnerability_analysis.get("severity_counts", {}),
                "top_5": vulnerability_analysis.get("vulnerabilities", [])[:5],
            },
            "recommendations": recommendations,
            "component_scores": risk_analysis.get("component_scores", {}),
        }
