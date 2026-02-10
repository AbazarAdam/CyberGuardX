"""
Technology Fingerprinting / Detection

Performs PASSIVE technology detection from HTTP headers and responses.
NO EXPLOITS - Only analyzes public response data.
"""

import requests
import re
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import urlparse


class TechnologyDetector:
    """
    PASSIVE technology fingerprinting.
    
    Detects web technologies from:
    - HTTP response headers
    - HTML meta tags
    - JavaScript library signatures
    - Framework patterns
    
    NO EXPLOITS, NO INTRUSIVE SCANNING.
    """
    
    # Technology signatures from headers
    HEADER_SIGNATURES = {
        # Web Servers
        'Apache': {'header': 'Server', 'pattern': r'Apache'},
        'Nginx': {'header': 'Server', 'pattern': r'nginx'},
        'IIS': {'header': 'Server', 'pattern': r'Microsoft-IIS'},
        'LiteSpeed': {'header': 'Server', 'pattern': r'LiteSpeed'},
        'Cloudflare': {'header': 'Server', 'pattern': r'cloudflare'},
        
        # Frameworks (from X-Powered-By)
        'PHP': {'header': 'X-Powered-By', 'pattern': r'PHP'},
        'ASP.NET': {'header': 'X-Powered-By', 'pattern': r'ASP\.NET'},
        'Express': {'header': 'X-Powered-By', 'pattern': r'Express'},
        'Django': {'header': 'Server', 'pattern': r'WSGIServer'},
        
        # CDNs and Security
        'Varnish': {'header': 'Via', 'pattern': r'varnish'},
        'Akamai': {'header': 'Server', 'pattern': r'AkamaiGHost'},
    }
    
    # HTML patterns for frontend frameworks
    HTML_SIGNATURES = {
        'React': [
            r'react',
            r'data-reactroot',
            r'__REACT',
        ],
        'Vue': [
            r'vue\.js',
            r'data-v-',
            r'__VUE',
        ],
        'Angular': [
            r'ng-version',
            r'ng-app',
            r'angular\.js',
        ],
        'jQuery': [
            r'jquery',
            r'jQuery',
        ],
        'Bootstrap': [
            r'bootstrap',
        ],
        'WordPress': [
            r'wp-content',
            r'wp-includes',
            r'wordpress',
        ],
        'Drupal': [
            r'Drupal',
            r'/sites/default/',
        ],
        'Joomla': [
            r'Joomla',
            r'/components/com_',
        ],
    }
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.user_agent = "CyberGuardX-TechDetector/1.0 (Educational/Research)"
    
    def scan(self, url: str) -> Dict[str, any]:
        """
        Detect technologies used by target website.
        
        Args:
            url: Target URL to scan
            
        Returns:
            Dictionary with detected technologies
        """
        result = {
            "url": url,
            "scan_timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "error": None,
            "web_server": None,
            "web_server_version": None,
            "programming_language": [],
            "frameworks": [],
            "content_management_system": None,
            "javascript_libraries": [],
            "cdn": None,
            "security_technologies": [],
            "all_headers": {},
            "grade": None,
            "vulnerabilities": [],
            "recommendations": []
        }
        
        try:
            # Make request
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent},
                allow_redirects=True,
                verify=True
            )
            
            # Store all headers for analysis
            result["all_headers"] = dict(response.headers)
            
            # Detect from headers
            self._detect_from_headers(response.headers, result)
            
            # Detect from HTML content
            html_content = response.text[:50000]  # First 50KB only
            self._detect_from_html(html_content, result)
            
            # Check for version disclosure vulnerabilities
            result["vulnerabilities"] = self._check_version_disclosure(result)
            
            # Generate recommendations
            result["recommendations"] = self._generate_recommendations(result)
            
            # Grade technology stack security
            result["grade"] = self._grade_tech_stack(result)
            
            result["success"] = True
            
        except requests.exceptions.Timeout:
            result["error"] = "Request timeout"
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"Connection error: {str(e)}"
        except Exception as e:
            result["error"] = f"Detection error: {str(e)}"
        
        return result
    
    def _detect_from_headers(self, headers: Dict, result: Dict):
        """Detect technologies from HTTP response headers."""
        
        # Server header analysis
        server_header = headers.get('Server', '')
        if server_header:
            # Extract server name and version
            match = re.match(r'([A-Za-z0-9\-]+)(?:/([0-9\.]+))?', server_header)
            if match:
                result["web_server"] = match.group(1)
                result["web_server_version"] = match.group(2)
        
        # X-Powered-By analysis
        powered_by = headers.get('X-Powered-By', '')
        if powered_by:
            if 'PHP' in powered_by:
                version_match = re.search(r'PHP/([0-9\.]+)', powered_by)
                lang = 'PHP'
                if version_match:
                    lang += f' {version_match.group(1)}'
                result["programming_language"].append(lang)
            
            if 'ASP.NET' in powered_by:
                result["programming_language"].append('ASP.NET')
                result["frameworks"].append('ASP.NET')
        
        # Check all header signatures
        for tech_name, signature in self.HEADER_SIGNATURES.items():
            header_value = headers.get(signature['header'], '')
            if re.search(signature['pattern'], header_value, re.IGNORECASE):
                if tech_name in ['Apache', 'Nginx', 'IIS', 'LiteSpeed']:
                    if not result["web_server"]:
                        result["web_server"] = tech_name
                elif tech_name in ['Cloudflare', 'Akamai', 'Varnish']:
                    result["cdn"] = tech_name
                elif tech_name not in result["frameworks"]:
                    result["frameworks"].append(tech_name)
        
        # Security headers detection
        security_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options'
        ]
        
        for sec_header in security_headers:
            if sec_header in headers:
                result["security_technologies"].append(sec_header)
    
    def _detect_from_html(self, html_content: str, result: Dict):
        """Detect technologies from HTML content."""
        
        html_lower = html_content.lower()
        
        # Detect frontend frameworks and libraries
        for tech_name, patterns in self.HTML_SIGNATURES.items():
            for pattern in patterns:
                if re.search(pattern, html_lower):
                    if tech_name in ['WordPress', 'Drupal', 'Joomla']:
                        result["content_management_system"] = tech_name
                    elif tech_name in ['React', 'Vue', 'Angular']:
                        if tech_name not in result["frameworks"]:
                            result["frameworks"].append(tech_name)
                    elif tech_name in ['jQuery', 'Bootstrap']:
                        if tech_name not in result["javascript_libraries"]:
                            result["javascript_libraries"].append(tech_name)
                    break
        
        # Detect meta generator tags
        generator_match = re.search(r'<meta\s+name=["\']generator["\']\s+content=["\']([^"\']+)["\']', html_lower)
        if generator_match:
            generator = generator_match.group(1)
            if 'wordpress' in generator:
                result["content_management_system"] = 'WordPress'
            elif 'drupal' in generator:
                result["content_management_system"] = 'Drupal'
    
    def _check_version_disclosure(self, result: Dict) -> List[Dict[str, str]]:
        """Check for version disclosure vulnerabilities."""
        vulnerabilities = []
        
        if result["web_server_version"]:
            vulnerabilities.append({
                "type": "Information Disclosure",
                "severity": "LOW",
                "component": result["web_server"],
                "version": result["web_server_version"],
                "description": f"Server version disclosed: {result['web_server']}/{result['web_server_version']}",
                "risk": "Attackers can target known vulnerabilities for this specific version"
            })
        
        for lang in result["programming_language"]:
            if any(char.isdigit() for char in lang):
                vulnerabilities.append({
                    "type": "Information Disclosure",
                    "severity": "LOW",
                    "component": lang.split()[0],
                    "version": lang,
                    "description": f"Programming language version disclosed: {lang}",
                    "risk": "Attackers can target version-specific vulnerabilities"
                })
        
        # Check for outdated technologies (simplified check)
        if 'PHP 5' in str(result["programming_language"]):
            vulnerabilities.append({
                "type": "Outdated Software",
                "severity": "HIGH",
                "component": "PHP",
                "version": "5.x",
                "description": "PHP 5 is end-of-life and unsupported",
                "risk": "No security patches available, highly vulnerable"
            })
        
        return vulnerabilities
    
    def _generate_recommendations(self, result: Dict) -> List[Dict[str, str]]:
        """Generate security recommendations based on detected technologies."""
        recommendations = []
        
        if result["web_server_version"]:
            recommendations.append({
                "priority": "MEDIUM",
                "issue": "Server version disclosure",
                "fix": "Remove or mask server version in HTTP headers",
                "implement": "Configure server to not send version information"
            })
        
        if result["programming_language"] and any(char.isdigit() for char in str(result["programming_language"])):
            recommendations.append({
                "priority": "MEDIUM",
                "issue": "Programming language version exposed",
                "fix": "Remove X-Powered-By header",
                "implement": "Configure web server/framework to suppress version headers"
            })
        
        if not result["security_technologies"]:
            recommendations.append({
                "priority": "HIGH",
                "issue": "No security headers detected",
                "fix": "Implement security headers (HSTS, CSP, X-Frame-Options)",
                "implement": "Add security headers via web server configuration"
            })
        
        if result["content_management_system"]:
            recommendations.append({
                "priority": "HIGH",
                "issue": f"CMS detected: {result['content_management_system']}",
                "fix": "Keep CMS and plugins updated to latest versions",
                "implement": "Enable automatic updates and regular security audits"
            })
        
        return recommendations
    
    def _grade_tech_stack(self, result: Dict) -> str:
        """Grade the security of the technology stack."""
        score = 100
        
        # Version disclosure penalty
        if result["web_server_version"]:
            score -= 10
        
        if result["programming_language"]:
            score -= 10
        
        # Missing security technologies penalty
        if not result["security_technologies"]:
            score -= 20
        
        # Oudated tech penalty
        if result["vulnerabilities"]:
            high_severity_count = sum(1 for v in result["vulnerabilities"] if v["severity"] == "HIGH")
            score -= (high_severity_count * 15)
        
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'


def detect_technologies(url: str) -> Dict[str, any]:
    """
    Convenience function to detect website technologies.
    
    Args:
        url: Target URL to scan
        
    Returns:
        Dictionary with detected technologies
    """
    detector = TechnologyDetector()
    return detector.scan(url)
