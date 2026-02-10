"""
Comprehensive Risk Scoring Engine

Aggregates risk points from all security scanners and calculates
an overall security risk score (0-100).
"""

from typing import Dict, List, Tuple
from datetime import datetime


class RiskScorer:
    """
    Calculates comprehensive security risk score based on all scan results.
    
    Risk points are accumulated from:
    - HTTP security headers (weight: 30%)
    - SSL/TLS configuration (weight: 35%)
    - DNS security (weight: 15%)
    - Technology vulnerabilities (weight: 20%)
    """
    
    # Weighted importance of each scan component
    WEIGHTS = {
        "http": 0.30,      # 30% - HTTP headers are important but not critical
        "ssl": 0.35,       # 35% - SSL/TLS is most critical (encryption)
        "dns": 0.15,       # 15% - DNS security is supplementary
        "tech": 0.20       # 20% - Technology vulns are significant
    }
    
    # Risk level thresholds
    RISK_LEVELS = {
        "CRITICAL": (80, 100),
        "HIGH": (60, 79),
        "MEDIUM": (40, 59),
        "LOW": (20, 39),
        "MINIMAL": (0, 19)
    }
    
    # Grade thresholds
    GRADE_THRESHOLDS = {
        'A': (0, 10),      # 0-10 risk points
        'B': (11, 25),     # 11-25 risk points
        'C': (26, 45),     # 26-45 risk points
        'D': (46, 70),     # 46-70 risk points
        'F': (71, 100)     # 71-100 risk points
    }
    
    def calculate_risk(self, scan_results: Dict) -> Dict[str, any]:
        """
        Calculate risk from consolidated scan results dictionary.
        
        Args:
            scan_results: Dictionary containing all scan results
            
        Returns:
            Dictionary with comprehensive risk assessment
        """
        http_scan = scan_results.get("http_headers", {})
        ssl_scan = scan_results.get("ssl_tls", {})
        dns_scan = scan_results.get("dns_security", {})
        tech_scan = scan_results.get("technologies", {})
        
        return self.calculate_risk_score(http_scan, ssl_scan, dns_scan, tech_scan)
    
    def calculate_risk_score(
        self,
        http_scan: Dict,
        ssl_scan: Dict,
        dns_scan: Dict,
        tech_scan: Dict
    ) -> Dict[str, any]:
        """
        Calculate comprehensive risk score from all scan results.
        
        Args:
            http_scan: HTTP headers scan results
            ssl_scan: SSL/TLS scan results
            dns_scan: DNS security scan results
            tech_scan: Technology detection scan results
            
        Returns:
            Dictionary with risk scoring details
        """
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "component_scores": {},
            "weighted_risk_score": 0,
            "overall_risk_level": None,
            "overall_grade": None,
            "risk_breakdown": {},
            "top_risks": [],
            "security_summary": {}
        }
        
        # Extract risk points from each component
        http_risk = http_scan.get("risk_points", 0) if http_scan.get("success") else 100
        ssl_risk = ssl_scan.get("risk_points", 0) if ssl_scan.get("success") else 100
        dns_risk = dns_scan.get("risk_points", 0) if dns_scan.get("success") else 50
        tech_risk = self._calculate_tech_risk(tech_scan) if tech_scan.get("success") else 50
        
        # Store component scores
        result["component_scores"] = {
            "http_headers": {
                "risk_points": http_risk,
                "weight": self.WEIGHTS["http"],
                "grade": http_scan.get("overall_grade", "F"),
                "status": "scanned" if http_scan.get("success") else "error"
            },
            "ssl_tls": {
                "risk_points": ssl_risk,
                "weight": self.WEIGHTS["ssl"],
                "grade": ssl_scan.get("grade", "F"),
                "status": "scanned" if ssl_scan.get("success") else "error"
            },
            "dns_security": {
                "risk_points": dns_risk,
                "weight": self.WEIGHTS["dns"],
                "grade": dns_scan.get("grade", "F"),
                "status": "scanned" if dns_scan.get("success") else "error"
            },
            "technology": {
                "risk_points": tech_risk,
                "weight": self.WEIGHTS["tech"],
                "grade": tech_scan.get("grade", "F"),
                "status": "scanned" if tech_scan.get("success") else "error"
            }
        }
        
        # Calculate weighted risk score
        weighted_score = (
            http_risk * self.WEIGHTS["http"] +
            ssl_risk * self.WEIGHTS["ssl"] +
            dns_risk * self.WEIGHTS["dns"] +
            tech_risk * self.WEIGHTS["tech"]
        )
        
        result["weighted_risk_score"] = int(weighted_score)
        
        # Determine risk level
        result["overall_risk_level"] = self._get_risk_level(weighted_score)
        
        # Determine overall grade
        result["overall_grade"] = self._get_grade(weighted_score)
        
        # Generate risk breakdown
        result["risk_breakdown"] = self._generate_risk_breakdown(
            http_scan, ssl_scan, dns_scan, tech_scan
        )
        
        # Identify top risks
        result["top_risks"] = self._identify_top_risks(
            http_scan, ssl_scan, dns_scan, tech_scan
        )
        
        # Generate security summary
        result["security_summary"] = self._generate_security_summary(result)
        
        return result
    
    def _calculate_tech_risk(self, tech_scan: Dict) -> int:
        """Calculate risk from technology scan."""
        risk_points = 0
        
        # Version disclosure
        if tech_scan.get("web_server_version"):
            risk_points += 10
        
        # Vulnerabilities
        vulnerabilities = tech_scan.get("vulnerabilities", [])
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "LOW")
            if severity == "HIGH":
                risk_points += 15
            elif severity == "MEDIUM":
                risk_points += 8
            elif severity == "LOW":
                risk_points += 3
        
        # Missing security technologies
        if not tech_scan.get("security_technologies"):
            risk_points += 20
        
        return min(risk_points, 100)
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Determine risk level from score."""
        for level, (min_score, max_score) in self.RISK_LEVELS.items():
            if min_score <= risk_score <= max_score:
                return level
        return "UNKNOWN"
    
    def _get_grade(self, risk_score: int) -> str:
        """Determine letter grade from risk score."""
        for grade, (min_score, max_score) in self.GRADE_THRESHOLDS.items():
            if min_score <= risk_score <= max_score:
                return grade
        return "F"
    
    def _generate_risk_breakdown(
        self,
        http_scan: Dict,
        ssl_scan: Dict,
        dns_scan: Dict,
        tech_scan: Dict
    ) -> Dict[str, List[str]]:
        """Generate detailed breakdown of risk factors."""
        breakdown = {
            "critical_issues": [],
            "high_issues": [],
            "medium_issues": [],
            "low_issues": []
        }
        
        # HTTP issues
        if http_scan.get("success"):
            for header, analysis in http_scan.get("header_analysis", {}).items():
                if not analysis["present"] and analysis["severity"] == "CRITICAL":
                    breakdown["critical_issues"].append(f"Missing critical header: {header}")
                elif not analysis["present"] and analysis["severity"] == "HIGH":
                    breakdown["high_issues"].append(f"Missing header: {header}")
        
        # SSL issues
        if ssl_scan.get("success"):
            for issue in ssl_scan.get("issues", []):
                if "expired" in issue.lower() or "weak" in issue.lower():
                    breakdown["critical_issues"].append(f"SSL/TLS: {issue}")
                elif "hsts" in issue.lower():
                    breakdown["high_issues"].append(f"SSL/TLS: {issue}")
                else:
                    breakdown["medium_issues"].append(f"SSL/TLS: {issue}")
        
        # DNS issues
        if dns_scan.get("success"):
            for issue in dns_scan.get("issues", []):
                if "spf" in issue.lower() or "dmarc" in issue.lower():
                    breakdown["high_issues"].append(f"DNS: {issue}")
                else:
                    breakdown["medium_issues"].append(f"DNS: {issue}")
        
        # Technology issues
        if tech_scan.get("success"):
            for vuln in tech_scan.get("vulnerabilities", []):
                severity = vuln.get("severity", "LOW")
                issue_text = f"Tech: {vuln.get('description', 'Unknown issue')}"
                
                if severity == "HIGH":
                    breakdown["high_issues"].append(issue_text)
                elif severity == "MEDIUM":
                    breakdown["medium_issues"].append(issue_text)
                else:
                    breakdown["low_issues"].append(issue_text)
        
        return breakdown
    
    def _identify_top_risks(
        self,
        http_scan: Dict,
        ssl_scan: Dict,
        dns_scan: Dict,
        tech_scan: Dict
    ) -> List[Dict[str, str]]:
        """Identify top 5 security risks."""
        risks = []
        
        # Prioritize by severity
        # 1. No HTTPS (critical)
        if ssl_scan.get("error") and "not HTTPS" in str(ssl_scan.get("error", "")):
            risks.append({
                "rank": 1,
                "severity": "CRITICAL",
                "category": "Encryption",
                "issue": "Website not using HTTPS",
                "impact": "All data transmitted in plaintext",
                "fix": "Enable HTTPS with valid SSL certificate"
            })
        
        # 2. Expired or invalid certificate (critical)
        if ssl_scan.get("success") and ssl_scan.get("certificate", {}).get("expired"):
            risks.append({
                "rank": 2,
                "severity": "CRITICAL",
                "category": "Certificate",
                "issue": "SSL certificate expired",
                "impact": "Site inaccessible, users see security warnings",
                "fix": "Renew SSL certificate immediately"
            })
        
        # 3. Missing critical headers (critical)
        if http_scan.get("success"):
            critical_missing = []
            for header, analysis in http_scan.get("header_analysis", {}).items():
                if not analysis["present"] and analysis["severity"] == "CRITICAL":
                    critical_missing.append(header)
            
            if critical_missing:
                risks.append({
                    "rank": 3,
                    "severity": "CRITICAL",
                    "category": "HTTP Headers",
                    "issue": f"Missing critical security headers: {', '.join(critical_missing[:2])}",
                    "impact": "Vulnerable to XSS, clickjacking, and injection attacks",
                    "fix": "Implement recommended security headers"
                })
        
        # 4. Weak TLS (high)
        if ssl_scan.get("success"):
            for issue in ssl_scan.get("issues", []):
                if "tls" in issue.lower() or "cipher" in issue.lower():
                    risks.append({
                        "rank": 4,
                        "severity": "HIGH",
                        "category": "Encryption",
                        "issue": issue,
                        "impact": "Vulnerable to protocol-level attacks",
                        "fix": "Upgrade to TLS 1.2+ with strong ciphers"
                    })
                    break
        
        # 5. Missing email security (high)
        if dns_scan.get("success"):
            if not dns_scan.get("spf", {}).get("present") or not dns_scan.get("dmarc", {}).get("present"):
                risks.append({
                    "rank": 5,
                    "severity": "HIGH",
                    "category": "Email Security",
                    "issue": "Missing SPF/DMARC records",
                    "impact": "Domain can be spoofed in phishing emails",
                    "fix": "Configure SPF and DMARC DNS records"
                })
        
        # Sort by rank and return top 5
        risks.sort(key=lambda x: x["rank"])
        return risks[:5]
    
    def _generate_security_summary(self, result: Dict) -> Dict[str, any]:
        """Generate executive security summary."""
        risk_score = result["weighted_risk_score"]
        risk_level = result["overall_risk_level"]
        grade = result["overall_grade"]
        
        # Determine security posture
        if risk_score <= 10:
            posture = "EXCELLENT"
            description = "Strong security controls in place across all areas"
        elif risk_score <= 25:
            posture = "GOOD"
            description = "Solid security with minor improvements needed"
        elif risk_score <= 45:
            posture = "FAIR"
            description = "Moderate security gaps requiring attention"
        elif risk_score <= 70:
            posture = "POOR"
            description = "Significant security vulnerabilities identified"
        else:
            posture = "CRITICAL"
            description = "Major security risks requiring immediate action"
        
        # Count issues by severity
        breakdown = result["risk_breakdown"]
        
        return {
            "security_posture": posture,
            "description": description,
            "overall_grade": grade,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "total_issues": {
                "critical": len(breakdown["critical_issues"]),
                "high": len(breakdown["high_issues"]),
                "medium": len(breakdown["medium_issues"]),
                "low": len(breakdown["low_issues"])
            },
            "recommendation": self._get_overall_recommendation(risk_score)
        }
    
    def _get_overall_recommendation(self, risk_score: int) -> str:
        """Get overall security recommendation."""
        if risk_score <= 10:
            return "Maintain current security controls and monitor for new threats"
        elif risk_score <= 25:
            return "Address minor security gaps to achieve optimal security"
        elif risk_score <= 45:
            return "Prioritize implementing missing security controls"
        elif risk_score <= 70:
            return "Immediate action required to fix multiple security vulnerabilities"
        else:
            return "URGENT: Critical security issues require immediate remediation"


def calculate_comprehensive_risk(
    http_scan: Dict,
    ssl_scan: Dict,
    dns_scan: Dict,
    tech_scan: Dict
) -> Dict[str, any]:
    """
    Convenience function to calculate comprehensive risk score.
    
    Args:
        http_scan: HTTP headers scan results
        ssl_scan: SSL/TLS scan results
        dns_scan: DNS security scan results
        tech_scan: Technology detection scan results
        
    Returns:
        Dictionary with comprehensive risk assessment
    """
    scorer = RiskScorer()
    return scorer.calculate_risk_score(http_scan, ssl_scan, dns_scan, tech_scan)
