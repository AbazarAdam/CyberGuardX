"""
OWASP Top 10 2021 Assessment Module

Maps security findings to OWASP Top 10 categories for educational reporting.
"""

from typing import Dict, List, Optional
from datetime import datetime


class OWASPTop10:
    """OWASP Top 10 2021 categories with descriptions."""
    
    CATEGORIES = {
        "A01:2021": {
            "name": "Broken Access Control",
            "description": "Failures related to authentication and authorization lead to unauthorized access",
            "examples": [
                "Missing CORS headers",
                "Weak referrer policy",
                "Missing access control headers"
            ],
            "severity": "CRITICAL"
        },
        "A02:2021": {
            "name": "Cryptographic Failures",
            "description": "Failures related to cryptography leading to sensitive data exposure",
            "examples": [
                "Missing HTTPS",
                "Weak TLS version",
                "No HSTS header",
                "Expired SSL certificate",
                "Weak cipher suites"
            ],
            "severity": "CRITICAL"
        },
        "A03:2021": {
            "name": "Injection",
            "description": "Injection flaws occur when untrusted data is sent to an interpreter",
            "examples": [
                "Missing Content-Security-Policy",
                "Weak CSP allowing unsafe-inline",
                "Missing X-XSS-Protection"
            ],
            "severity": "CRITICAL"
        },
        "A04:2021": {
            "name": "Insecure Design",
            "description": "Risks related to design and architectural flaws",
            "examples": [
                "Missing X-Frame-Options (clickjacking)",
                "No anti-clickjacking measures"
            ],
            "severity": "HIGH"
        },
        "A05:2021": {
            "name": "Security Misconfiguration",
            "description": "Security misconfiguration is the most common vulnerability",
            "examples": [
                "Server version disclosure",
                "Missing security headers",
                "Default configurations",
                "Verbose error messages"
            ],
            "severity": "HIGH"
        },
        "A06:2021": {
            "name": "Vulnerable and Outdated Components",
            "description": "Using components with known vulnerabilities",
            "examples": [
                "Outdated server software",
                "Outdated PHP/programming language",
                "Vulnerable CMS versions"
            ],
            "severity": "HIGH"
        },
        "A07:2021": {
            "name": "Identification and Authentication Failures",
            "description": "Authentication-related implementations that could allow attackers to compromise passwords, keys, or session tokens",
            "examples": [
                "Weak session management",
                "Missing secure cookie flags",
                "No rate limiting"
            ],
            "severity": "HIGH"
        },
        "A08:2021": {
            "name": "Software and Data Integrity Failures",
            "description": "Code and infrastructure that does not protect against integrity violations",
            "examples": [
                "Missing Subresource Integrity (SRI)",
                "Insecure deserialization"
            ],
            "severity": "MEDIUM"
        },
        "A09:2021": {
            "name": "Security Logging and Monitoring Failures",
            "description": "Insufficient logging and monitoring coupled with missing or ineffective integration with incident response",
            "examples": [
                "No security event logging",
                "Missing audit trails"
            ],
            "severity": "MEDIUM"
        },
        "A10:2021": {
            "name": "Server-Side Request Forgery (SSRF)",
            "description": "SSRF flaws occur when web application fetches a remote resource without validating the user-supplied URL",
            "examples": [
                "Unvalidated URL redirects",
                "Missing DNS rebinding protections"
            ],
            "severity": "MEDIUM"
        }
    }


class OWASPAssessor:
    """
    Maps security scan findings to OWASP Top 10 2021 categories.
    
    Provides educational assessment showing how findings relate to
    industry-standard vulnerability classifications.
    """
    
    def __init__(self):
        self.owasp_categories = OWASPTop10.CATEGORIES
    
    def assess(
        self,
        http_scan: Dict,
        ssl_scan: Dict,
        dns_scan: Dict,
        tech_scan: Dict
    ) -> Dict[str, any]:
        """
        Assess security findings and map to OWASP Top 10.
        
        Args:
            http_scan: HTTP headers scan results
            ssl_scan: SSL/TLS scan results
            dns_scan: DNS security scan results
            tech_scan: Technology detection scan results
            
        Returns:
            Dictionary with OWASP Top 10 assessment
        """
        result = {
            "assessment_timestamp": datetime.utcnow().isoformat(),
            "owasp_findings": {},
            "compliance_score": 0,
            "compliant_categories": [],
            "non_compliant_categories": [],
            "critical_findings": [],
            "summary": {}
        }
        
        # Initialize all OWASP categories
        for category_id, category_info in self.owasp_categories.items():
            result["owasp_findings"][category_id] = {
                "name": category_info["name"],
                "description": category_info["description"],
                "severity": category_info["severity"],
                "your_status": "COMPLIANT",
                "issues_found": [],
                "recommendations": []
            }
        
        # Map HTTP scan findings
        self._map_http_findings(http_scan, result)
        
        # Map SSL/TLS findings
        self._map_ssl_findings(ssl_scan, result)
        
        # Map DNS findings
        self._map_dns_findings(dns_scan, result)
        
        # Map technology findings
        self._map_tech_findings(tech_scan, result)
        
        # Calculate compliance
        self._calculate_compliance(result)
        
        # Generate summary
        result["summary"] = self._generate_summary(result)
        
        return result
    
    def _map_http_findings(self, http_scan: Dict, result: Dict):
        """Map HTTP header findings to OWASP categories."""
        if not http_scan.get("success"):
            return
        
        header_analysis = http_scan.get("header_analysis", {})
        
        # A01: Broken Access Control
        access_control_headers = ["Referrer-Policy", "Cross-Origin-Opener-Policy", "Cross-Origin-Resource-Policy"]
        for header in access_control_headers:
            if header in header_analysis and not header_analysis[header]["present"]:
                result["owasp_findings"]["A01:2021"]["issues_found"].append(f"Missing {header} header")
                result["owasp_findings"]["A01:2021"]["your_status"] = "NON-COMPLIANT"
        
        # A03: Injection
        if "Content-Security-Policy" in header_analysis:
            csp = header_analysis["Content-Security-Policy"]
            if not csp["present"] or csp["score"] < 80:
                result["owasp_findings"]["A03:2021"]["issues_found"].append("Missing or weak Content-Security-Policy")
                result["owasp_findings"]["A03:2021"]["your_status"] = "NON-COMPLIANT"
        
        # A04: Insecure Design
        if "X-Frame-Options" in header_analysis and not header_analysis["X-Frame-Options"]["present"]:
            result["owasp_findings"]["A04:2021"]["issues_found"].append("Missing X-Frame-Options (clickjacking risk)")
            result["owasp_findings"]["A04:2021"]["your_status"] = "NON-COMPLIANT"
        
        # A05: Security Misconfiguration
        missing_headers = http_scan.get("headers_missing", [])
        if len(missing_headers) > 3:
            result["owasp_findings"]["A05:2021"]["issues_found"].append(f"{len(missing_headers)} security headers missing")
            result["owasp_findings"]["A05:2021"]["your_status"] = "NON-COMPLIANT"
    
    def _map_ssl_findings(self, ssl_scan: Dict, result: Dict):
        """Map SSL/TLS findings to OWASP categories."""
        if not ssl_scan.get("success"):
            return
        
        # A02: Cryptographic Failures
        issues = ssl_scan.get("issues", [])
        
        if ssl_scan.get("error") and "not HTTPS" in str(ssl_scan.get("error", "")):
            result["owasp_findings"]["A02:2021"]["issues_found"].append("Website not using HTTPS")
            result["owasp_findings"]["A02:2021"]["your_status"] = "NON-COMPLIANT"
            result["critical_findings"].append({
                "category": "A02:2021 - Cryptographic Failures",
                "issue": "No HTTPS encryption",
                "severity": "CRITICAL"
            })
        
        for issue in issues:
            if "expired" in issue.lower() or "tls" in issue.lower() or "cipher" in issue.lower():
                result["owasp_findings"]["A02:2021"]["issues_found"].append(issue)
                result["owasp_findings"]["A02:2021"]["your_status"] = "NON-COMPLIANT"
        
        if not ssl_scan.get("hsts", {}).get("present"):
            result["owasp_findings"]["A02:2021"]["issues_found"].append("Missing HSTS header")
            result["owasp_findings"]["A02:2021"]["your_status"] = "NON-COMPLIANT"
    
    def _map_dns_findings(self, dns_scan: Dict, result: Dict):
        """Map DNS findings to OWASP categories."""
        if not dns_scan.get("success"):
            return
        
        # A05: Security Misconfiguration (DNS security is part of proper configuration)
        if not dns_scan.get("spf", {}).get("present"):
            result["owasp_findings"]["A05:2021"]["issues_found"].append("Missing SPF record (email security)")
        
        if not dns_scan.get("dmarc", {}).get("present"):
            result["owasp_findings"]["A05:2021"]["issues_found"].append("Missing DMARC record (email security)")
        
        if not dns_scan.get("dnssec", {}).get("enabled"):
            result["owasp_findings"]["A05:2021"]["issues_found"].append("DNSSEC not enabled")
        
        if result["owasp_findings"]["A05:2021"]["issues_found"]:
            result["owasp_findings"]["A05:2021"]["your_status"] = "NON-COMPLIANT"
    
    def _map_tech_findings(self, tech_scan: Dict, result: Dict):
        """Map technology detection findings to OWASP categories."""
        if not tech_scan.get("success"):
            return
        
        # A05: Security Misconfiguration (version disclosure)
        if tech_scan.get("web_server_version"):
            result["owasp_findings"]["A05:2021"]["issues_found"].append(
                f"Server version disclosure: {tech_scan['web_server']}/{tech_scan['web_server_version']}"
            )
            result["owasp_findings"]["A05:2021"]["your_status"] = "NON-COMPLIANT"
        
        # A06: Vulnerable and Outdated Components
        vulnerabilities = tech_scan.get("vulnerabilities", [])
        for vuln in vulnerabilities:
            if vuln.get("type") == "Outdated Software":
                result["owasp_findings"]["A06:2021"]["issues_found"].append(vuln["description"])
                result["owasp_findings"]["A06:2021"]["your_status"] = "NON-COMPLIANT"
                
                if vuln.get("severity") == "HIGH":
                    result["critical_findings"].append({
                        "category": "A06:2021 - Vulnerable and Outdated Components",
                        "issue": vuln["description"],
                        "severity": "HIGH"
                    })
    
    def _calculate_compliance(self, result: Dict):
        """Calculate overall OWASP compliance score."""
        total_categories = len(self.owasp_categories)
        compliant_count = 0
        
        for category_id, finding in result["owasp_findings"].items():
            if finding["your_status"] == "COMPLIANT":
                compliant_count += 1
                result["compliant_categories"].append(category_id)
            else:
                result["non_compliant_categories"].append(category_id)
                
                # Generate recommendations
                finding["recommendations"] = self._get_recommendations(category_id, finding["issues_found"])
        
        result["compliance_score"] = int((compliant_count / total_categories) * 100)
    
    def _get_recommendations(self, category_id: str, issues: List[str]) -> List[str]:
        """Generate recommendations for OWASP category."""
        recommendations = []
        
        if category_id == "A01:2021":
            recommendations.append("Implement proper access control headers (CORS, Referrer-Policy)")
            recommendations.append("Use principle of least privilege for all resources")
        
        elif category_id == "A02:2021":
            recommendations.append("Enable HTTPS with TLS 1.2+ on all pages")
            recommendations.append("Implement HSTS with long max-age")
            recommendations.append("Use strong cipher suites only")
        
        elif category_id == "A03:2021":
            recommendations.append("Implement strict Content-Security-Policy")
            recommendations.append("Use parameterized queries to prevent SQL injection")
            recommendations.append("Validate and sanitize all user inputs")
        
        elif category_id == "A04:2021":
            recommendations.append("Implement anti-clickjacking headers (X-Frame-Options, CSP frame-ancestors)")
            recommendations.append("Use secure-by-design principles in architecture")
        
        elif category_id == "A05:2021":
            recommendations.append("Remove server version disclosure from headers")
            recommendations.append("Implement all recommended security headers")
            recommendations.append("Use principle of least privilege in configurations")
        
        elif category_id == "A06:2021":
            recommendations.append("Keep all software components up-to-date")
            recommendations.append("Remove unused dependencies and features")
            recommendations.append("Monitor CVE databases for known vulnerabilities")
        
        return recommendations
    
    def _generate_summary(self, result: Dict) -> Dict[str, any]:
        """Generate executive summary of OWASP assessment."""
        return {
            "overall_compliance": f"{result['compliance_score']}%",
            "compliant_count": len(result["compliant_categories"]),
            "non_compliant_count": len(result["non_compliant_categories"]),
            "critical_findings_count": len(result["critical_findings"]),
            "verdict": self._get_verdict(result["compliance_score"]),
            "priority_actions": self._get_priority_actions(result)
        }
    
    def _get_verdict(self, score: int) -> str:
        """Get verdict based on compliance score."""
        if score >= 90:
            return "EXCELLENT - Strong OWASP Top 10 compliance"
        elif score >= 70:
            return "GOOD - Moderate compliance with room for improvement"
        elif score >= 50:
            return "FAIR - Multiple OWASP categories need attention"
        else:
            return "POOR - Significant security gaps identified"
    
    def _get_priority_actions(self, result: Dict) -> List[str]:
        """Get top priority actions based on findings."""
        actions = []
        
        # Critical findings first
        for finding in result["critical_findings"][:3]:
            actions.append(f"[CRITICAL] {finding['issue']}")
        
        # Then non-compliant critical categories
        for category_id in result["non_compliant_categories"]:
            category = result["owasp_findings"][category_id]
            if category["severity"] == "CRITICAL" and len(actions) < 5:
                if category["issues_found"]:
                    actions.append(f"[{category_id}] {category['issues_found'][0]}")
        
        return actions[:5]  # Top 5 priority actions


def assess_owasp_compliance(
    http_scan: Dict,
    ssl_scan: Dict,
    dns_scan: Dict,
    tech_scan: Dict
) -> Dict[str, any]:
    """
    Convenience function to assess OWASP Top 10 compliance.
    
    Args:
        http_scan: HTTP headers scan results
        ssl_scan: SSL/TLS scan results
        dns_scan: DNS security scan results
        tech_scan: Technology detection scan results
        
    Returns:
        Dictionary with OWASP assessment
    """
    assessor = OWASPAssessor()
    return assessor.assess(http_scan, ssl_scan, dns_scan, tech_scan)
