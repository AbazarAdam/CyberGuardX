"""
SSL/TLS Security Scanner

Performs PASSIVE analysis of SSL/TLS configuration.
Only performs standard TLS handshakes - NO EXPLOITS.
"""

import ssl
import socket
import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import requests


class SSLTLSScanner:
    """
    PASSIVE SSL/TLS security scanner.
    
    Only performs standard TLS handshakes and certificate validation.
    NO EXPLOITS, NO ACTIVE ATTACKS.
    """
    
    # Secure TLS versions
    SECURE_TLS_VERSIONS = ['TLSv1.2', 'TLSv1.3']
    
    # Insecure/deprecated protocols
    INSECURE_PROTOCOLS = ['SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1']
    
    # Strong cipher suites (simplified list)
    STRONG_CIPHERS = [
        'TLS_AES_128_GCM_SHA256',
        'TLS_AES_256_GCM_SHA384',
        'TLS_CHACHA20_POLY1305_SHA256',
        'ECDHE-RSA-AES128-GCM-SHA256',
        'ECDHE-RSA-AES256-GCM-SHA384',
    ]
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def scan(self, url: str) -> Dict[str, any]:
        """
        Scan SSL/TLS configuration of target website.
        
        Args:
            url: Target URL to scan
            
        Returns:
            Dictionary with SSL/TLS scan results
        """
        result = {
            "url": url,
            "scan_timestamp": datetime.datetime.utcnow().isoformat(),
            "success": False,
            "error": None,
            "certificate": {},
            "tls_version": None,
            "cipher_suite": None,
            "grade": None,
            "score": 0,
            "issues": [],
            "recommendations": [],
            "risk_points": 0
        }
        
        try:
            parsed = urlparse(url)
            
            # Only scan HTTPS URLs
            if parsed.scheme != 'https':
                result["error"] = "URL is not HTTPS - SSL/TLS scan skipped"
                result["issues"].append("Website does not use HTTPS encryption")
                result["risk_points"] = 20
                result["grade"] = "F"
                result["recommendations"].append({
                    "priority": "CRITICAL",
                    "issue": "No HTTPS",
                    "fix": "Enable HTTPS with valid SSL certificate",
                    "impact": "All data transmitted in plaintext - highly vulnerable to interception"
                })
                return result
            
            hostname = parsed.netloc.split(':')[0]
            port = parsed.port if parsed.port else 443
            
            # Perform SSL/TLS analysis
            cert_info = self._check_certificate(hostname, port)
            result["certificate"] = cert_info["details"]
            result["tls_version"] = cert_info.get("tls_version")
            result["cipher_suite"] = cert_info.get("cipher_suite")
            
            # Analyze certificate validity
            issues = []
            risk_points = 0
            
            if not cert_info["valid"]:
                issues.append(cert_info["error"])
                risk_points += 20
            
            # Check certificate expiration
            if cert_info["details"].get("expired"):
                issues.append("Certificate has expired")
                risk_points += 20
            elif cert_info["details"].get("expires_soon"):
                issues.append(f"Certificate expires soon ({cert_info['details']['days_until_expiry']} days)")
                risk_points += 5
            
            # Check TLS version
            tls_version = cert_info.get("tls_version", "")
            if any(insecure in tls_version for insecure in self.INSECURE_PROTOCOLS):
                issues.append(f"Using insecure protocol: {tls_version}")
                risk_points += 20
            elif tls_version not in self.SECURE_TLS_VERSIONS:
                issues.append(f"TLS version not optimal: {tls_version}")
                risk_points += 10
            
            # Check cipher suite strength
            cipher = cert_info.get("cipher_suite", "")
            if cipher:
                if "RC4" in cipher or "MD5" in cipher or "NULL" in cipher:
                    issues.append(f"Weak cipher suite detected: {cipher}")
                    risk_points += 15
                elif "CBC" in cipher:
                    issues.append(f"CBC mode cipher (potential vulnerability): {cipher}")
                    risk_points += 5
            
            # Check HSTS via headers
            hsts_check = self._check_hsts(url)
            if not hsts_check["present"]:
                issues.append("HSTS header not configured")
                risk_points += 10
            
            result["hsts"] = hsts_check
            result["issues"] = issues
            result["risk_points"] = min(risk_points, 100)
            
            # Calculate grade
            grade, score = self._calculate_grade(cert_info, issues, risk_points)
            result["grade"] = grade
            result["score"] = score
            
            # Generate recommendations
            result["recommendations"] = self._generate_recommendations(cert_info, issues)
            
            result["success"] = True
            
        except socket.gaierror:
            result["error"] = "Cannot resolve hostname"
        except socket.timeout:
            result["error"] = "Connection timeout"
        except ssl.SSLError as e:
            result["error"] = f"SSL error: {str(e)}"
            result["risk_points"] = 20
        except Exception as e:
            result["error"] = f"Scan error: {str(e)}"
        
        return result
    
    def _check_certificate(self, hostname: str, port: int) -> Dict[str, any]:
        """
        Retrieve and validate SSL certificate.
        
        Args:
            hostname: Target hostname
            port: Target port (usually 443)
            
        Returns:
            Dictionary with certificate information
        """
        result = {
            "valid": False,
            "error": None,
            "details": {},
            "tls_version": None,
            "cipher_suite": None
        }
        
        try:
            # Create SSL context with secure defaults
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Get TLS version and cipher
                    result["tls_version"] = ssock.version()
                    result["cipher_suite"] = ssock.cipher()[0] if ssock.cipher() else None
                    
                    # Parse certificate details
                    subject = dict(x[0] for x in cert.get('subject', []))
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    
                    # Parse dates
                    not_before = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    now = datetime.datetime.utcnow()
                    
                    days_until_expiry = (not_after - now).days
                    
                    result["details"] = {
                        "common_name": subject.get('commonName', 'Unknown'),
                        "organization": subject.get('organizationName', 'Unknown'),
                        "issuer": issuer.get('organizationName', 'Unknown'),
                        "valid_from": not_before.isoformat(),
                        "valid_until": not_after.isoformat(),
                        "days_until_expiry": days_until_expiry,
                        "expired": days_until_expiry < 0,
                        "expires_soon": 0 <= days_until_expiry < 30,
                        "serial_number": cert.get('serialNumber', 'Unknown'),
                        "version": cert.get('version', 'Unknown'),
                        "subject_alt_names": [name[1] for name in cert.get('subjectAltName', [])]
                    }
                    
                    result["valid"] = True
                    
        except ssl.CertificateError as e:
            result["error"] = f"Certificate validation failed: {str(e)}"
        except ssl.SSLError as e:
            result["error"] = f"SSL connection error: {str(e)}"
        except Exception as e:
            result["error"] = f"Certificate check failed: {str(e)}"
        
        return result
    
    def _check_hsts(self, url: str) -> Dict[str, any]:
        """
        Check for HSTS (HTTP Strict Transport Security) header.
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with HSTS information
        """
        result = {
            "present": False,
            "value": None,
            "max_age": None,
            "include_subdomains": False,
            "preload": False
        }
        
        try:
            response = requests.get(url, timeout=self.timeout, verify=True)
            hsts_header = response.headers.get('Strict-Transport-Security')
            
            if hsts_header:
                result["present"] = True
                result["value"] = hsts_header
                
                # Parse HSTS directives
                if 'max-age=' in hsts_header.lower():
                    try:
                        max_age_str = hsts_header.lower().split('max-age=')[1].split(';')[0].strip()
                        result["max_age"] = int(max_age_str)
                    except:
                        pass
                
                result["include_subdomains"] = 'includesubdomains' in hsts_header.lower()
                result["preload"] = 'preload' in hsts_header.lower()
        
        except Exception:
            pass
        
        return result
    
    def _calculate_grade(self, cert_info: Dict, issues: List[str], risk_points: int) -> Tuple[str, int]:
        """
        Calculate overall SSL/TLS security grade.
        
        Args:
            cert_info: Certificate information
            issues: List of identified issues
            risk_points: Accumulated risk points
            
        Returns:
            Tuple of (grade: str, score: int)
        """
        score = 100 - risk_points
        
        if score >= 95:
            return 'A', score
        elif score >= 85:
            return 'B', score
        elif score >= 70:
            return 'C', score
        elif score >= 50:
            return 'D', score
        else:
            return 'F', score
    
    def _generate_recommendations(self, cert_info: Dict, issues: List[str]) -> List[Dict[str, str]]:
        """Generate actionable SSL/TLS recommendations."""
        recommendations = []
        
        if not cert_info["valid"]:
            recommendations.append({
                "priority": "CRITICAL",
                "issue": cert_info.get("error", "Invalid certificate"),
                "fix": "Install a valid SSL certificate from a trusted CA",
                "impact": "Users will see security warnings, search engines penalize site"
            })
        
        if cert_info["details"].get("expired"):
            recommendations.append({
                "priority": "CRITICAL",
                "issue": "Certificate expired",
                "fix": "Renew SSL certificate immediately",
                "impact": "Site is inaccessible to most users, major security risk"
            })
        
        if cert_info["details"].get("expires_soon"):
            recommendations.append({
                "priority": "HIGH",
                "issue": f"Certificate expires in {cert_info['details']['days_until_expiry']} days",
                "fix": "Renew certificate before expiration",
                "impact": "Prevent service disruption"
            })
        
        tls_version = cert_info.get("tls_version", "")
        if tls_version not in self.SECURE_TLS_VERSIONS:
            recommendations.append({
                "priority": "HIGH",
                "issue": f"Using outdated TLS version: {tls_version}",
                "fix": "Upgrade to TLS 1.2 or TLS 1.3",
                "impact": "Vulnerable to protocol-level attacks"
            })
        
        if "HSTS header not configured" in issues:
            recommendations.append({
                "priority": "HIGH",
                "issue": "Missing HSTS header",
                "fix": "Add Strict-Transport-Security header with max-age=31536000",
                "impact": "Vulnerable to SSL stripping and downgrade attacks"
            })
        
        cipher = cert_info.get("cipher_suite", "")
        if cipher and ("RC4" in cipher or "MD5" in cipher):
            recommendations.append({
                "priority": "CRITICAL",
                "issue": f"Weak cipher suite: {cipher}",
                "fix": "Disable weak ciphers, use only AES-GCM or ChaCha20",
                "impact": "Encryption can be broken"
            })
        
        return recommendations


def scan_ssl_tls(url: str) -> Dict[str, any]:
    """
    Convenience function to scan SSL/TLS configuration.
    
    Args:
        url: Target URL to scan
        
    Returns:
        Dictionary with SSL/TLS scan results
    """
    scanner = SSLTLSScanner()
    return scanner.scan(url)
