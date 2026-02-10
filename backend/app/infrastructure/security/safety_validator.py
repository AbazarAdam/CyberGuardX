"""
Safety Validator for Website Vulnerability Scanner

CRITICAL: This module implements MANDATORY safety controls to ensure
ethical and legal use of the website vulnerability scanner.

All scans MUST pass through this validator before execution.
"""

import ipaddress
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
import socket


class ScanRateLimiter:
    """Rate limiting to prevent abuse and ensure ethical scanning."""
    
    def __init__(self):
        self._scan_history: Dict[str, datetime] = {}
        self._rate_limit_minutes = 10
    
    def can_scan(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if IP address can perform a scan.
        
        Args:
            ip_address: Client IP address
            
        Returns:
            Tuple of (can_scan: bool, reason: str if blocked)
        """
        now = datetime.utcnow()
        
        if ip_address in self._scan_history:
            last_scan = self._scan_history[ip_address]
            time_since_last = now - last_scan
            
            if time_since_last < timedelta(minutes=self._rate_limit_minutes):
                remaining = self._rate_limit_minutes - (time_since_last.seconds // 60)
                return False, f"Rate limit exceeded. Please wait {remaining} minutes before scanning again."
        
        # Record this scan attempt
        self._scan_history[ip_address] = now
        return True, None
    
    def clear_old_entries(self):
        """Clean up scan history older than rate limit window."""
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=self._rate_limit_minutes * 2)
        
        self._scan_history = {
            ip: timestamp 
            for ip, timestamp in self._scan_history.items() 
            if timestamp > cutoff
        }


class TargetValidator:
    """Validates scan targets to prevent illegal or unethical scanning."""
    
    # Whitelist for testing (safe domains that explicitly allow scanning)
    ALLOWED_TEST_DOMAINS = [
        'example.com',
        'example.org',
        'example.net',
        'localhost',
        '127.0.0.1',
        'scanme.nmap.org',  # Explicitly allows scanning
        'testphp.vulnweb.com',  # Security testing site
    ]
    
    # Blocked top-level domains (government, military, critical infrastructure)
    BLOCKED_TLDS = [
        '.gov',
        '.mil',
        '.edu',  # Educational institutions require permission
    ]
    
    # Private IP ranges (RFC 1918)
    PRIVATE_IP_RANGES = [
        ipaddress.IPv4Network('10.0.0.0/8'),
        ipaddress.IPv4Network('172.16.0.0/12'),
        ipaddress.IPv4Network('192.168.0.0/16'),
        ipaddress.IPv4Network('127.0.0.0/8'),  # Loopback
    ]
    
    @staticmethod
    def is_valid_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format and protocol.
        
        Args:
            url: Target URL to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: str if invalid)
        """
        try:
            parsed = urlparse(url)
            
            # Must have http or https protocol
            if parsed.scheme not in ['http', 'https']:
                return False, "URL must use HTTP or HTTPS protocol"
            
            # Must have valid domain
            if not parsed.netloc:
                return False, "Invalid URL: missing domain"
            
            # Extract domain without port
            domain = parsed.netloc.split(':')[0]
            
            # Basic domain format validation
            if not re.match(r'^[a-zA-Z0-9.-]+$', domain):
                return False, "Invalid domain format"
            
            return True, None
            
        except Exception as e:
            return False, f"URL parsing error: {str(e)}"
    
    @classmethod
    def is_allowed_target(cls, url: str) -> Tuple[bool, Optional[str]]:
        """
        Check if target is allowed for scanning.
        
        Args:
            url: Target URL to validate
            
        Returns:
            Tuple of (is_allowed: bool, reason: str if blocked)
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0]  # Remove port
            
            # Check if domain is in whitelist (use endswith to prevent
            # bypass via subdomains like "example.com.evil.com")
            if any(domain == allowed or domain.endswith("." + allowed) for allowed in cls.ALLOWED_TEST_DOMAINS):
                return True, None
            
            # Check for blocked TLDs
            for blocked_tld in cls.BLOCKED_TLDS:
                if domain.endswith(blocked_tld):
                    return False, f"Scanning {blocked_tld} domains is prohibited without explicit authorization"
            
            # Try to resolve IP address
            try:
                ip_str = socket.gethostbyname(domain)
                ip = ipaddress.IPv4Address(ip_str)
                
                # Check if IP is private/internal
                for private_range in cls.PRIVATE_IP_RANGES:
                    if ip in private_range and domain not in ['localhost', '127.0.0.1']:
                        return False, "Scanning private/internal IP addresses is prohibited"
                
            except socket.gaierror:
                return False, "Cannot resolve domain name"
            except Exception as e:
                return False, f"IP validation error: {str(e)}"
            
            # If not whitelisted, require explicit permission confirmation
            return True, None
            
        except Exception as e:
            return False, f"Target validation error: {str(e)}"
    
    @staticmethod
    def validate_permission(url: str, confirmed_permission: bool, owner_confirmation: bool, legal_responsibility: bool) -> Tuple[bool, Optional[str]]:
        """
        Validate that user has confirmed legal permissions.
        
        Args:
            url: Target URL
            confirmed_permission: User confirmed they have permission
            owner_confirmation: User confirmed ownership or written permission
            legal_responsibility: User accepts legal responsibility
            
        Returns:
            Tuple of (is_valid: bool, error_message: str if invalid)
        """
        parsed = urlparse(url)
        domain = parsed.netloc.split(':')[0]
        
        # Whitelisted domains don't require all confirmations
        if any(domain == allowed or domain.endswith("." + allowed) for allowed in TargetValidator.ALLOWED_TEST_DOMAINS):
            if not confirmed_permission:
                return False, "You must acknowledge scanning terms even for test domains"
            return True, None
        
        # Non-whitelisted domains require ALL confirmations
        if not confirmed_permission:
            return False, "You must confirm you have permission to scan this website"
        
        if not owner_confirmation:
            return False, "You must confirm you own this website or have written permission"
        
        if not legal_responsibility:
            return False, "You must accept legal responsibility for this scan"
        
        return True, None


class SafetyValidator:
    """
    Main safety validation coordinator.
    
    CRITICAL: All website scans MUST pass through this validator.
    """
    
    def __init__(self):
        self.rate_limiter = ScanRateLimiter()
        self.target_validator = TargetValidator()
    
    def validate_scan_request(
        self,
        url: str,
        client_ip: str,
        confirmed_permission: bool = False,
        owner_confirmation: bool = False,
        legal_responsibility: bool = False
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Comprehensive validation of scan request.
        
        Args:
            url: Target URL to scan
            client_ip: Client IP address for rate limiting
            confirmed_permission: User confirmed they have permission
            owner_confirmation: User confirmed ownership or written permission
            legal_responsibility: User accepts legal responsibility
            
        Returns:
            Tuple of (is_valid: bool, error_message: str if invalid, validation_metadata: dict)
        """
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "url": url,
            "client_ip": client_ip,
            "validations_passed": []
        }
        
        # Step 1: Rate limiting check
        can_scan, rate_msg = self.rate_limiter.can_scan(client_ip)
        if not can_scan:
            metadata["blocked_reason"] = "rate_limit"
            return False, rate_msg, metadata
        metadata["validations_passed"].append("rate_limit")
        
        # Step 2: URL format validation
        is_valid_url, url_msg = self.target_validator.is_valid_url(url)
        if not is_valid_url:
            metadata["blocked_reason"] = "invalid_url"
            return False, url_msg, metadata
        metadata["validations_passed"].append("url_format")
        
        # Step 3: Target allowlist check
        is_allowed, target_msg = self.target_validator.is_allowed_target(url)
        if not is_allowed:
            metadata["blocked_reason"] = "blocked_target"
            return False, target_msg, metadata
        metadata["validations_passed"].append("target_allowed")
        
        # Step 4: Legal permission validation
        has_permission, permission_msg = self.target_validator.validate_permission(
            url, confirmed_permission, owner_confirmation, legal_responsibility
        )
        if not has_permission:
            metadata["blocked_reason"] = "missing_permission"
            return False, permission_msg, metadata
        metadata["validations_passed"].append("legal_permission")
        
        # All validations passed
        metadata["scan_authorized"] = True
        return True, None, metadata
    
    def get_legal_disclaimer(self) -> Dict[str, Any]:
        """
        Get the legal disclaimer that must be shown to users.
        
        Returns:
            Dictionary with disclaimer text and required confirmations
        """
        return {
            "title": "LEGAL DISCLAIMER AND TERMS OF USE",
            "warning": "⚠️ UNAUTHORIZED WEBSITE SCANNING MAY BE ILLEGAL",
            "terms": [
                "You MUST own the website you are scanning OR have explicit written permission from the owner",
                "Scanning websites without permission may violate the Computer Fraud and Abuse Act (CFAA) and similar laws",
                "This tool performs PASSIVE security checks only - no exploits or payloads",
                "You accept FULL LEGAL RESPONSIBILITY for any scans performed",
                "All scan activity is logged for legal protection and audit purposes",
                "Rate limiting (1 scan per 10 minutes per IP) is enforced",
                "Certain domains (.gov, .mil, .edu) are blocked without authorization"
            ],
            "required_confirmations": [
                {
                    "id": "owner_confirmation",
                    "text": "☐ I confirm I own this website or have written permission to scan it"
                },
                {
                    "id": "legal_understanding",
                    "text": "☐ I understand scanning without permission may be illegal"
                },
                {
                    "id": "legal_responsibility",
                    "text": "☐ I accept full legal responsibility for this scan"
                }
            ],
            "rate_limiting": "Maximum 1 scan per 10 minutes per IP address",
            "scope": "Only HTTP/HTTPS standard ports (80, 443) - No port scanning",
            "methods": "Passive checks only: HTTP headers, SSL handshake, public DNS records"
        }


# Global validator instance
_safety_validator = SafetyValidator()


def get_safety_validator() -> SafetyValidator:
    """Get the global safety validator instance."""
    return _safety_validator


def validate_scan(
    url: str,
    client_ip: str,
    confirmed_permission: bool = False,
    owner_confirmation: bool = False,
    legal_responsibility: bool = False
) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Convenience function for validating scan requests.
    
    This should be called by the API endpoint before any scanning.
    """
    validator = get_safety_validator()
    return validator.validate_scan_request(
        url, client_ip, confirmed_permission, owner_confirmation, legal_responsibility
    )
