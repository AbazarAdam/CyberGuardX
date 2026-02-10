"""
DNS Security Scanner

Performs PASSIVE DNS lookups for security records.
Only queries public DNS servers - NO ATTACKS.
"""

import dns.resolver
import dns.exception
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import urlparse


class DNSSecurityScanner:
    """
    PASSIVE DNS security scanner.
    
    Only performs standard DNS lookups for security-related records.
    NO ZONE TRANSFERS, NO EXPLOITS.
    """
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout
    
    def scan(self, url: str) -> Dict[str, any]:
        """
        Scan DNS configuration for security records.
        
        Args:
            url: Target URL to scan
            
        Returns:
            Dictionary with DNS security scan results
        """
        result = {
            "url": url,
            "scan_timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "error": None,
            "domain": None,
            "spf": {},
            "dmarc": {},
            "dkim": {},
            "dnssec": {},
            "mx_records": [],
            "caa_records": [],
            "grade": None,
            "score": 0,
            "issues": [],
            "recommendations": [],
            "risk_points": 0
        }
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0]
            result["domain"] = domain
            
            # Check SPF record
            result["spf"] = self._check_spf(domain)
            
            # Check DMARC record
            result["dmarc"] = self._check_dmarc(domain)
            
            # Check MX records (for DKIM context)
            result["mx_records"] = self._check_mx(domain)
            
            # Check CAA records
            result["caa_records"] = self._check_caa(domain)
            
            # Check DNSSEC
            result["dnssec"] = self._check_dnssec(domain)
            
            # Analyze results and calculate risk
            issues = []
            risk_points = 0
            
            if not result["spf"]["present"]:
                issues.append("No SPF record configured")
                risk_points += 8
            elif result["spf"]["too_permissive"]:
                issues.append("SPF record too permissive (allows +all)")
                risk_points += 12
            
            if not result["dmarc"]["present"]:
                issues.append("No DMARC record configured")
                risk_points += 8
            elif result["dmarc"]["policy"] == "none":
                issues.append("DMARC policy set to 'none' (monitoring only)")
                risk_points += 5
            
            if not result["dnssec"]["enabled"]:
                issues.append("DNSSEC not enabled")
                risk_points += 10
            
            if not result["caa_records"]:
                issues.append("No CAA record (Certificate Authority Authorization)")
                risk_points += 4
            
            result["issues"] = issues
            result["risk_points"] = min(risk_points, 100)
            
            # Calculate grade
            grade, score = self._calculate_grade(result, risk_points)
            result["grade"] = grade
            result["score"] = score
            
            # Generate recommendations
            result["recommendations"] = self._generate_recommendations(result)
            
            result["success"] = True
            
        except dns.resolver.NXDOMAIN:
            result["error"] = "Domain does not exist"
        except dns.resolver.NoNameservers:
            result["error"] = "No nameservers available"
        except dns.exception.Timeout:
            result["error"] = "DNS query timeout"
        except Exception as e:
            result["error"] = f"DNS scan error: {str(e)}"
        
        return result
    
    def _check_spf(self, domain: str) -> Dict[str, any]:
        """Check for SPF (Sender Policy Framework) record."""
        result = {
            "present": False,
            "record": None,
            "too_permissive": False,
            "mechanisms": []
        }
        
        try:
            answers = self.resolver.resolve(domain, 'TXT')
            
            for rdata in answers:
                txt_string = str(rdata).strip('"')
                
                if txt_string.startswith('v=spf1'):
                    result["present"] = True
                    result["record"] = txt_string
                    
                    # Check if too permissive
                    if '+all' in txt_string or '?all' in txt_string:
                        result["too_permissive"] = True
                    
                    # Extract mechanisms
                    mechanisms = txt_string.split()[1:]  # Skip 'v=spf1'
                    result["mechanisms"] = mechanisms
                    break
        
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
        except Exception:
            pass
        
        return result
    
    def _check_dmarc(self, domain: str) -> Dict[str, any]:
        """Check for DMARC (Domain-based Message Authentication) record."""
        result = {
            "present": False,
            "record": None,
            "policy": None,
            "subdomain_policy": None,
            "percentage": None,
            "reporting_enabled": False
        }
        
        try:
            dmarc_domain = f'_dmarc.{domain}'
            answers = self.resolver.resolve(dmarc_domain, 'TXT')
            
            for rdata in answers:
                txt_string = str(rdata).strip('"')
                
                if txt_string.startswith('v=DMARC1'):
                    result["present"] = True
                    result["record"] = txt_string
                    
                    # Parse DMARC tags
                    tags = {}
                    for part in txt_string.split(';'):
                        part = part.strip()
                        if '=' in part:
                            key, value = part.split('=', 1)
                            tags[key.strip()] = value.strip()
                    
                    result["policy"] = tags.get('p')
                    result["subdomain_policy"] = tags.get('sp')
                    result["percentage"] = tags.get('pct')
                    result["reporting_enabled"] = 'rua' in tags or 'ruf' in tags
                    break
        
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
        except Exception:
            pass
        
        return result
    
    def _check_mx(self, domain: str) -> List[str]:
        """Check MX (Mail Exchange) records."""
        mx_records = []
        
        try:
            answers = self.resolver.resolve(domain, 'MX')
            mx_records = [str(rdata.exchange) for rdata in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
        except Exception:
            pass
        
        return mx_records
    
    def _check_caa(self, domain: str) -> List[Dict[str, str]]:
        """Check CAA (Certificate Authority Authorization) records."""
        caa_records = []
        
        try:
            answers = self.resolver.resolve(domain, 'CAA')
            
            for rdata in answers:
                caa_records.append({
                    "flags": rdata.flags,
                    "tag": rdata.tag.decode() if isinstance(rdata.tag, bytes) else rdata.tag,
                    "value": rdata.value.decode() if isinstance(rdata.value, bytes) else rdata.value
                })
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
        except Exception:
            pass
        
        return caa_records
    
    def _check_dnssec(self, domain: str) -> Dict[str, any]:
        """Check if DNSSEC is enabled."""
        result = {
            "enabled": False,
            "details": None
        }
        
        try:
            # Check for DNSKEY record (indicates DNSSEC)
            answers = self.resolver.resolve(domain, 'DNSKEY')
            
            if answers:
                result["enabled"] = True
                result["details"] = f"Found {len(answers)} DNSKEY records"
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
        except Exception:
            pass
        
        return result
    
    def _calculate_grade(self, scan_result: Dict, risk_points: int) -> tuple:
        """Calculate overall DNS security grade."""
        score = 100 - risk_points
        
        if score >= 90:
            return 'A', score
        elif score >= 80:
            return 'B', score
        elif score >= 70:
            return 'C', score
        elif score >= 60:
            return 'D', score
        else:
            return 'F', score
    
    def _generate_recommendations(self, scan_result: Dict) -> List[Dict[str, str]]:
        """Generate DNS security recommendations."""
        recommendations = []
        
        if not scan_result["spf"]["present"]:
            recommendations.append({
                "priority": "HIGH",
                "issue": "No SPF record",
                "fix": "Add SPF TXT record: 'v=spf1 mx -all'",
                "impact": "Email spoofing protection missing"
            })
        elif scan_result["spf"]["too_permissive"]:
            recommendations.append({
                "priority": "HIGH",
                "issue": "SPF record too permissive",
                "fix": "Change +all to -all or ~all",
                "impact": "Attackers can send email claiming to be from your domain"
            })
        
        if not scan_result["dmarc"]["present"]:
            recommendations.append({
                "priority": "HIGH",
                "issue": "No DMARC record",
                "fix": "Add DMARC TXT record at _dmarc.yourdomain.com: 'v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com'",
                "impact": "No email authentication policy enforcement"
            })
        elif scan_result["dmarc"]["policy"] == "none":
            recommendations.append({
                "priority": "MEDIUM",
                "issue": "DMARC policy set to 'none'",
                "fix": "Upgrade to p=quarantine or p=reject",
                "impact": "Monitoring only - no enforcement of email authentication"
            })
        
        if not scan_result["dnssec"]["enabled"]:
            recommendations.append({
                "priority": "MEDIUM",
                "issue": "DNSSEC not enabled",
                "fix": "Enable DNSSEC at your domain registrar",
                "impact": "Vulnerable to DNS spoofing and cache poisoning"
            })
        
        if not scan_result["caa_records"]:
            recommendations.append({
                "priority": "LOW",
                "issue": "No CAA record",
                "fix": "Add CAA record to specify authorized certificate authorities",
                "impact": "Any CA can issue certificates for your domain"
            })
        
        return recommendations


def scan_dns_security(url: str) -> Dict[str, any]:
    """
    Convenience function to scan DNS security.
    
    Args:
        url: Target URL to scan
        
    Returns:
        Dictionary with DNS security scan results
    """
    scanner = DNSSecurityScanner()
    return scanner.scan(url)
