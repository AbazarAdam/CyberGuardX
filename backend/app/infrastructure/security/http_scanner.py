"""
HTTP Security Headers Scanner

Performs PASSIVE analysis of HTTP security headers.
NO PAYLOADS - Only checks response headers from standard requests.
"""

import requests
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse


class SecurityHeader:
    """Represents a security header with grading criteria."""
    
    def __init__(
        self,
        name: str,
        description: str,
        recommended_value: str,
        severity: str,
        owasp_category: str
    ):
        self.name = name
        self.description = description
        self.recommended_value = recommended_value
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW
        self.owasp_category = owasp_category


# Security headers database with grading criteria
SECURITY_HEADERS = {
    "Strict-Transport-Security": SecurityHeader(
        name="Strict-Transport-Security",
        description="Forces HTTPS connections and prevents protocol downgrade attacks",
        recommended_value="max-age=31536000; includeSubDomains; preload",
        severity="CRITICAL",
        owasp_category="A02:2021 – Cryptographic Failures"
    ),
    "Content-Security-Policy": SecurityHeader(
        name="Content-Security-Policy",
        description="Prevents XSS, clickjacking, and other code injection attacks",
        recommended_value="default-src 'self'; script-src 'self'; object-src 'none'",
        severity="CRITICAL",
        owasp_category="A03:2021 – Injection"
    ),
    "X-Frame-Options": SecurityHeader(
        name="X-Frame-Options",
        description="Prevents clickjacking by controlling iframe embedding",
        recommended_value="DENY or SAMEORIGIN",
        severity="HIGH",
        owasp_category="A04:2021 – Insecure Design"
    ),
    "X-Content-Type-Options": SecurityHeader(
        name="X-Content-Type-Options",
        description="Prevents MIME-sniffing attacks",
        recommended_value="nosniff",
        severity="MEDIUM",
        owasp_category="A05:2021 – Security Misconfiguration"
    ),
    "Referrer-Policy": SecurityHeader(
        name="Referrer-Policy",
        description="Controls referrer information sent with requests",
        recommended_value="strict-origin-when-cross-origin or no-referrer",
        severity="MEDIUM",
        owasp_category="A01:2021 – Broken Access Control"
    ),
    "Permissions-Policy": SecurityHeader(
        name="Permissions-Policy",
        description="Controls browser features and APIs available to the page",
        recommended_value="geolocation=(), microphone=(), camera=()",
        severity="MEDIUM",
        owasp_category="A05:2021 – Security Misconfiguration"
    ),
    "X-XSS-Protection": SecurityHeader(
        name="X-XSS-Protection",
        description="Legacy XSS filter (deprecated but still widely used)",
        recommended_value="1; mode=block",
        severity="LOW",
        owasp_category="A03:2021 – Injection"
    ),
    "X-Permitted-Cross-Domain-Policies": SecurityHeader(
        name="X-Permitted-Cross-Domain-Policies",
        description="Controls cross-domain requests from Flash and PDF",
        recommended_value="none",
        severity="LOW",
        owasp_category="A05:2021 – Security Misconfiguration"
    ),
    "Cross-Origin-Embedder-Policy": SecurityHeader(
        name="Cross-Origin-Embedder-Policy",
        description="Controls loading of cross-origin resources",
        recommended_value="require-corp",
        severity="MEDIUM",
        owasp_category="A01:2021 – Broken Access Control"
    ),
    "Cross-Origin-Opener-Policy": SecurityHeader(
        name="Cross-Origin-Opener-Policy",
        description="Isolates browsing context to protect from cross-origin attacks",
        recommended_value="same-origin",
        severity="MEDIUM",
        owasp_category="A01:2021 – Broken Access Control"
    ),
    "Cross-Origin-Resource-Policy": SecurityHeader(
        name="Cross-Origin-Resource-Policy",
        description="Protects resources from being loaded by other origins",
        recommended_value="same-origin",
        severity="MEDIUM",
        owasp_category="A01:2021 – Broken Access Control"
    ),
    "Cache-Control": SecurityHeader(
        name="Cache-Control",
        description="Controls caching behavior (critical for sensitive data)",
        recommended_value="no-store, no-cache, must-revalidate (for sensitive pages)",
        severity="MEDIUM",
        owasp_category="A01:2021 – Broken Access Control"
    ),
    "Expect-CT": SecurityHeader(
        name="Expect-CT",
        description="Enforces Certificate Transparency requirements",
        recommended_value="max-age=86400, enforce",
        severity="LOW",
        owasp_category="A02:2021 – Cryptographic Failures"
    ),
    "Feature-Policy": SecurityHeader(
        name="Feature-Policy",
        description="Legacy version of Permissions-Policy",
        recommended_value="geolocation 'none'; microphone 'none'; camera 'none'",
        severity="LOW",
        owasp_category="A05:2021 – Security Misconfiguration"
    ),
    "X-Download-Options": SecurityHeader(
        name="X-Download-Options",
        description="Prevents IE from executing downloaded files in site context",
        recommended_value="noopen",
        severity="LOW",
        owasp_category="A05:2021 – Security Misconfiguration"
    )
}


class HeaderGrader:
    """Grades security header implementation."""
    
    GRADE_CRITERIA = {
        'A': {'score': 95, 'description': 'Excellent - All critical headers present with strong values'},
        'B': {'score': 85, 'description': 'Good - Most critical headers present, minor improvements needed'},
        'C': {'score': 70, 'description': 'Fair - Some critical headers missing, moderate risk'},
        'D': {'score': 50, 'description': 'Poor - Many critical headers missing, significant risk'},
        'F': {'score': 0, 'description': 'Failing - Critical security headers absent, high risk'}
    }
    
    @staticmethod
    def grade_header(header_name: str, header_value: Optional[str]) -> Tuple[str, int, str]:
        """
        Grade a single header implementation.
        
        Args:
            header_name: Name of the header
            header_value: Value of the header (None if missing)
            
        Returns:
            Tuple of (grade: str, score: int, feedback: str)
        """
        if header_name not in SECURITY_HEADERS:
            return 'N/A', 0, 'Unknown header'
        
        header_spec = SECURITY_HEADERS[header_name]
        
        # Missing header
        if header_value is None:
            severity_penalty = {
                'CRITICAL': ('F', 0),
                'HIGH': ('D', 40),
                'MEDIUM': ('C', 60),
                'LOW': ('B', 70)
            }
            grade, score = severity_penalty[header_spec.severity]
            feedback = f"Header missing. Severity: {header_spec.severity}. {header_spec.description}"
            return grade, score, feedback
        
        # Header present - analyze value quality
        value_lower = header_value.lower()
        
        # Specific header analysis
        if header_name == "Strict-Transport-Security":
            if 'max-age' not in value_lower:
                return 'D', 40, 'HSTS present but missing max-age directive'
            
            # Extract max-age value
            try:
                max_age = int(value_lower.split('max-age=')[1].split(';')[0].strip())
                if max_age >= 31536000:  # 1 year
                    score = 100
                    if 'includesubdomains' in value_lower and 'preload' in value_lower:
                        return 'A', 100, 'Perfect HSTS configuration with preload'
                    return 'A', 95, 'Strong HSTS configuration'
                elif max_age >= 15768000:  # 6 months
                    return 'B', 85, 'Good HSTS but consider longer max-age (1 year recommended)'
                else:
                    return 'C', 70, 'HSTS max-age too short, increase to at least 1 year'
            except:
                return 'D', 50, 'HSTS present but invalid max-age value'
        
        elif header_name == "Content-Security-Policy":
            if "default-src" not in value_lower and "script-src" not in value_lower:
                return 'D', 50, 'CSP present but missing critical directives (default-src or script-src)'
            if "'unsafe-inline'" in value_lower or "'unsafe-eval'" in value_lower:
                return 'C', 65, 'CSP present but uses unsafe directives that weaken protection'
            return 'A', 95, 'Strong CSP configuration'
        
        elif header_name == "X-Frame-Options":
            if value_lower in ['deny', 'sameorigin']:
                return 'A', 100, f'Perfect configuration: {value_lower.upper()}'
            return 'C', 70, 'X-Frame-Options present but value may not provide full protection'
        
        elif header_name == "X-Content-Type-Options":
            if value_lower == 'nosniff':
                return 'A', 100, 'Perfect configuration'
            return 'C', 70, 'Header present but incorrect value (should be "nosniff")'
        
        elif header_name == "Referrer-Policy":
            strong_policies = ['no-referrer', 'strict-origin-when-cross-origin', 'same-origin']
            if value_lower in strong_policies:
                return 'A', 95, 'Strong referrer policy'
            return 'B', 80, 'Referrer policy present but consider stricter option'
        
        elif header_name == "X-XSS-Protection":
            if '1' in value_lower and 'mode=block' in value_lower:
                return 'B', 80, 'Configured correctly (though header is deprecated, CSP preferred)'
            return 'C', 60, 'Present but not optimally configured'
        
        # Generic scoring for other headers
        return 'B', 85, f'Header present: {header_value[:50]}'
    
    @staticmethod
    def calculate_overall_grade(header_results: Dict[str, Dict]) -> Tuple[str, int]:
        """
        Calculate overall security grade based on all headers.
        
        Args:
            header_results: Dictionary of header scan results
            
        Returns:
            Tuple of (overall_grade: str, overall_score: int)
        """
        total_score = 0
        total_weight = 0
        
        severity_weights = {
            'CRITICAL': 4.0,
            'HIGH': 3.0,
            'MEDIUM': 2.0,
            'LOW': 1.0
        }
        
        for header_name, result in header_results.items():
            if header_name in SECURITY_HEADERS:
                severity = SECURITY_HEADERS[header_name].severity
                weight = severity_weights.get(severity, 1.0)
                total_score += result['score'] * weight
                total_weight += weight
        
        overall_score = int(total_score / total_weight) if total_weight > 0 else 0
        
        # Determine grade
        if overall_score >= 95:
            return 'A', overall_score
        elif overall_score >= 85:
            return 'B', overall_score
        elif overall_score >= 70:
            return 'C', overall_score
        elif overall_score >= 50:
            return 'D', overall_score
        else:
            return 'F', overall_score


class HTTPSecurityScanner:
    """
    PASSIVE HTTP security headers scanner.
    
    Only performs standard HTTP requests and analyzes response headers.
    NO PAYLOADS, NO EXPLOITS.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.user_agent = "CyberGuardX-SecurityScanner/1.0 (Educational/Research)"
    
    def scan(self, url: str) -> Dict[str, Any]:
        """
        Scan website for HTTP security headers.
        
        Args:
            url: Target URL to scan
            
        Returns:
            Dictionary with scan results
        """
        result = {
            "url": url,
            "scan_timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "error": None,
            "headers_found": {},
            "headers_missing": [],
            "header_analysis": {},
            "overall_grade": None,
            "overall_score": 0,
            "recommendations": [],
            "risk_points": 0
        }
        
        try:
            # Make PASSIVE request (standard GET)
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent},
                allow_redirects=True,
                verify=True  # Validate SSL certificates
            )
            
            result["status_code"] = response.status_code
            result["final_url"] = response.url
            
            # Analyze each security header
            header_results = {}
            risk_points = 0
            
            for header_name, header_spec in SECURITY_HEADERS.items():
                header_value = response.headers.get(header_name)
                
                grade, score, feedback = HeaderGrader.grade_header(header_name, header_value)
                
                header_results[header_name] = {
                    "present": header_value is not None,
                    "value": header_value,
                    "grade": grade,
                    "score": score,
                    "feedback": feedback,
                    "severity": header_spec.severity,
                    "description": header_spec.description,
                    "recommended_value": header_spec.recommended_value,
                    "owasp_category": header_spec.owasp_category
                }
                
                if header_value is not None:
                    result["headers_found"][header_name] = header_value
                else:
                    result["headers_missing"].append(header_name)
                    
                    # Add risk points for missing headers
                    severity_risk = {
                        'CRITICAL': 15,
                        'HIGH': 10,
                        'MEDIUM': 5,
                        'LOW': 2
                    }
                    risk_points += severity_risk.get(header_spec.severity, 0)
            
            result["header_analysis"] = header_results
            result["risk_points"] = min(risk_points, 100)  # Cap at 100
            
            # Calculate overall grade
            overall_grade, overall_score = HeaderGrader.calculate_overall_grade(header_results)
            result["overall_grade"] = overall_grade
            result["overall_score"] = overall_score
            
            # Generate recommendations
            result["recommendations"] = self._generate_recommendations(header_results)
            
            result["success"] = True
            
        except requests.exceptions.SSLError as e:
            result["error"] = f"SSL certificate error: {str(e)}"
            result["risk_points"] = 20
        except requests.exceptions.Timeout:
            result["error"] = "Request timeout - server did not respond"
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"Connection error: {str(e)}"
        except Exception as e:
            result["error"] = f"Scan error: {str(e)}"
        
        return result
    
    def _generate_recommendations(self, header_results: Dict[str, Dict]) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on scan results."""
        recommendations = []
        
        # Priority: Critical headers first
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            for header_name, result in header_results.items():
                if result['severity'] == severity and result['score'] < 90:
                    rec = {
                        "priority": severity,
                        "header": header_name,
                        "issue": result['feedback'],
                        "fix": f"Add or improve '{header_name}' header",
                        "recommended_value": result['recommended_value'],
                        "impact": result['description']
                    }
                    recommendations.append(rec)
        
        return recommendations[:10]  # Top 10 recommendations


def scan_http_headers(url: str) -> Dict[str, Any]:
    """
    Convenience function to scan HTTP security headers.
    
    Args:
        url: Target URL to scan
        
    Returns:
        Dictionary with scan results
    """
    scanner = HTTPSecurityScanner()
    return scanner.scan(url)
