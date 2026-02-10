"""
Have I Been Pwned (HIBP) API Client for CyberGuardX
Implements k-anonymity model for secure email breach checking
"""
import hashlib
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests


class HIBPClient:
    """
    Client for Have I Been Pwned API v3 (Passwords)
    Uses k-anonymity model - only sends first 5 characters of SHA-1 hash
    """
    
    API_BASE_URL = "https://api.pwnedpasswords.com/range/"
    RATE_LIMIT_SECONDS = 2  # Respect 1 request per 2 seconds
    REQUEST_TIMEOUT = 10  # seconds
    
    def __init__(self):
        self.last_request_time = 0
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 86400  # 24 hours in seconds
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.RATE_LIMIT_SECONDS:
            sleep_time = self.RATE_LIMIT_SECONDS - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _hash_email(self, email: str) -> str:
        """Hash email using SHA-1 for HIBP API."""
        normalized = email.strip().lower()
        return hashlib.sha1(normalized.encode("utf-8")).hexdigest().upper()
    
    def _get_from_cache(self, email_hash: str) -> Optional[Dict]:
        """Check if result is in cache and still valid."""
        if email_hash in self.cache:
            cached_data, timestamp = self.cache[email_hash]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                # Cache expired
                del self.cache[email_hash]
        return None
    
    def _add_to_cache(self, email_hash: str, data: Dict):
        """Add result to cache with timestamp."""
        self.cache[email_hash] = (data, time.time())
    
    def check_email_pwned(self, email: str) -> Dict:
        """
        Check if an email has been pwned using HIBP API.
        
        Args:
            email: Email address to check
            
        Returns:
            Dict with breach information:
            {
                "pwned": bool,
                "pwned_count": int,
                "checked_at": datetime,
                "source": "hibp_api" | "cache" | "offline_simulation",
                "error": Optional[str]
            }
        """
        # Generate hash
        email_hash = self._hash_email(email)
        
        # Check cache first
        cached_result = self._get_from_cache(email_hash)
        if cached_result:
            cached_result["source"] = "cache"
            return cached_result
        
        # Get first 5 characters of hash (k-anonymity)
        hash_prefix = email_hash[:5]
        hash_suffix = email_hash[5:]
        
        try:
            # Enforce rate limiting
            self._rate_limit()
            
            # Make API request
            url = f"{self.API_BASE_URL}{hash_prefix}"
            headers = {
                "User-Agent": "CyberGuardX-Educational-Tool",
                "Add-Padding": "true"  # Request padding for additional privacy
            }
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                # Parse response
                pwned = False
                pwned_count = 0
                
                # Response format: SUFFIX:COUNT\r\n for each match
                for line in response.text.strip().split('\r\n'):
                    if ':' in line:
                        suffix, count = line.split(':')
                        if suffix.upper() == hash_suffix:
                            pwned = True
                            pwned_count = int(count)
                            break
                
                result = {
                    "pwned": pwned,
                    "pwned_count": pwned_count,
                    "checked_at": datetime.utcnow(),
                    "source": "hibp_api",
                    "error": None
                }
                
                # Cache the result
                self._add_to_cache(email_hash, result)
                
                return result
            
            elif response.status_code == 429:
                # Rate limited
                return {
                    "pwned": False,
                    "pwned_count": 0,
                    "checked_at": datetime.utcnow(),
                    "source": "offline_simulation",
                    "error": "Rate limited by HIBP API - using fallback"
                }
            
            else:
                # Other error
                return {
                    "pwned": False,
                    "pwned_count": 0,
                    "checked_at": datetime.utcnow(),
                    "source": "offline_simulation",
                    "error": f"API returned status {response.status_code}"
                }
        
        except requests.exceptions.Timeout:
            return {
                "pwned": False,
                "pwned_count": 0,
                "checked_at": datetime.utcnow(),
                "source": "offline_simulation",
                "error": "API request timeout - using fallback"
            }
        
        except requests.exceptions.ConnectionError:
            return {
                "pwned": False,
                "pwned_count": 0,
                "checked_at": datetime.utcnow(),
                "source": "offline_simulation",
                "error": "Connection error - using fallback"
            }
        
        except Exception as e:
            return {
                "pwned": False,
                "pwned_count": 0,
                "checked_at": datetime.utcnow(),
                "source": "offline_simulation",
                "error": f"Unexpected error: {str(e)}"
            }
    
    def get_breach_details_mock(self, pwned_count: int) -> List[Dict]:
        """
        Generate mock breach details when actual HIBP breaches API is not available.
        This simulates realistic breach scenarios for educational purposes.
        """
        from app.infrastructure.external.breach_data import REALISTIC_BREACHES
        import random
        
        if pwned_count == 0:
            return []
        
        # Select random breaches based on count
        num_breaches = min(pwned_count, len(REALISTIC_BREACHES))
        selected = random.sample(REALISTIC_BREACHES, num_breaches)
        
        return selected


# Singleton instance
_hibp_client = None


def get_hibp_client() -> HIBPClient:
    """Get singleton HIBP client instance."""
    global _hibp_client
    if _hibp_client is None:
        _hibp_client = HIBPClient()
    return _hibp_client
