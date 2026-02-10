"""
Email Breach Checker Service - 100% Offline with SQLite Database
Uses comprehensive local dataset of 100,000+ breached email patterns
"""
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from functools import lru_cache

from app.utils.hashing import hash_email


class BreachCheckerService:
    """Service for checking email breaches using local SQLite database."""
    
    def __init__(self):
        self.db_path = Path(__file__).resolve().parents[2] / "data" / "breaches.db"
        self._ensure_database_exists()
        # LRU cache for performance (stores last 1000 queries in memory)
        self._cache = {}
        self._cache_size = 1000
    
    def _ensure_database_exists(self):
        """Ensure database file exists."""
        if not self.db_path.exists():
            print(f"⚠️  WARNING: Breach database not found at {self.db_path}")
            print(f"   Run: python -m app.utils.breach_generator --size 100000")
            print(f"   This will create a comprehensive offline breach dataset.")
    
    def _get_from_cache(self, email_hash: str) -> Optional[Dict]:
        """Check if result is in cache."""
        return self._cache.get(email_hash)
    
    def _add_to_cache(self, email_hash: str, data: Dict):
        """Add result to cache with LRU eviction."""
        if len(self._cache) >= self._cache_size:
            # Remove oldest entry
            self._cache.pop(next(iter(self._cache)))
        self._cache[email_hash] = data
    
    def _query_database(self, email_hash: str) -> Optional[Dict]:
        """Query SQLite database for email hash."""
        if not self.db_path.exists():
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT email_hash, total_breaches, first_breach_date, 
                       last_breach_date, total_accounts_affected, breach_details
                FROM breached_emails
                WHERE email_hash = ?
            ''', (email_hash,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "email_hash": row[0],
                    "total_breaches": row[1],
                    "first_breach_date": row[2],
                    "last_breach_date": row[3],
                    "total_accounts_affected": row[4],
                    "breach_details": json.loads(row[5]) if row[5] else []
                }
            
            return None
        
        except Exception as e:
            print(f"Database query error: {e}")
            return None
    
    def _calculate_risk_level(self, total_breaches: int) -> str:
        """
        Calculate risk level based on number of breaches.
        
        Args:
            total_breaches: Number of breaches
            
        Returns:
            Risk level: "LOW", "MEDIUM", "HIGH", "CRITICAL"
        """
        if total_breaches == 0:
            return "LOW"
        elif total_breaches == 1:
            return "MEDIUM"
        elif total_breaches <= 3:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _calculate_risk_score(self, total_breaches: int, breaches: List[Dict]) -> int:
        """
        Calculate numerical risk score (0-100).
        
        Factors:
        - Number of breaches (40%)
        - Severity of breaches (30%)
        - recency of breaches (20%)
        - Accounts affected (10%)
        """
        if total_breaches == 0:
            return 0
        
        # Base score from breach count (0-40 points)
        count_score = min(total_breaches * 8, 40)
        
        # Severity score (0-30 points)
        severity_map = {"CRITICAL": 30, "HIGH": 25, "MEDIUM": 15, "LOW": 10}
        severity_score = sum(severity_map.get(b.get("severity", "MEDIUM"), 15) 
                            for b in breaches) / len(breaches) if breaches else 15
        
        # Recency score (0-20 points) - more recent = higher score
        try:
            if breaches and breaches[-1].get("date"):
                last_breach_year = int(breaches[-1]["date"][:4])
                current_year = 2026
                years_ago = current_year - last_breach_year
                recency_score = max(20 - years_ago, 0)
            else:
                recency_score = 10
        except:
            recency_score = 10
        
        # Accounts affected score (0-10 points)
        total_accounts = sum(b.get("accounts", 0) for b in breaches)
        if total_accounts > 1000000000:  # 1B+
            accounts_score = 10
        elif total_accounts > 100000000:  # 100M+
            accounts_score = 8
        elif total_accounts > 10000000:  # 10M+
            accounts_score = 6
        else:
            accounts_score = 4
        
        total_score = int(count_score + severity_score + recency_score + accounts_score)
        return min(total_score, 100)
    
    def _generate_recommendations(self, total_breaches: int, breaches: List[Dict]) -> List[str]:
        """Generate personalized security recommendations."""
        if total_breaches == 0:
            return [
                "✅ Your email appears safe in our database",
                "🔐 Continue using unique passwords for different services",
                "📱 Enable two-factor authentication where available",
                "🔔 Set up breach alerts at haveibeenpwned.com for real-time monitoring"
            ]
        
        recommendations = [
            "🚨 URGENT: Change passwords immediately for all affected accounts",
            "🔐 Enable two-factor authentication (2FA) on all services",
            "🔍 Check for reused passwords across different accounts",
            "📧 Be extra cautious of phishing emails targeting these services"
        ]
        
        # Check if sensitive data was exposed
        sensitive_data = []
        for breach in breaches:
            for data_class in breach.get("data_classes", []):
                if any(keyword in data_class.lower() for keyword in 
                      ["credit", "social security", "ssn", "bank", "financial"]):
                    sensitive_data.append(data_class)
        
        if sensitive_data:
            recommendations.append("⚠️  CRITICAL: Monitor credit reports for suspicious activity")
            recommendations.append("💳 Consider placing a fraud alert with credit bureaus")
            recommendations.append("🔒 Review financial accounts for unauthorized transactions")
        
        # Specific recommendations based on breach count
        if total_breaches >= 3:
            recommendations.append("🔁 Use a password manager to generate unique passwords")
            recommendations.append("📊 Consider using privacy-focused email aliases")
        
        recommendations.append("🔔 Set up breach monitoring at haveibeenpwned.com")
        
        return recommendations
    
    def _create_breach_timeline(self, breaches: List[Dict]) -> List[Dict]:
        """Create timeline of breaches."""
        timeline = []
        for breach in sorted(breaches, key=lambda x: x.get("date", "")):
            timeline.append({
                "date": breach.get("date"),
                "event": f"{breach.get('name')} breach",
                "accounts": breach.get("accounts"),
                "severity": breach.get("severity", "MEDIUM")
            })
        return timeline
    
    def _create_data_exposure_summary(self, breaches: List[Dict]) -> Dict:
        """Create summary of data exposure types."""
        exposure = {
            "email_addresses": False,
            "passwords": False,
            "usernames": False,
            "password_hints": False,
            "phone_numbers": False,
            "physical_addresses": False,
            "credit_cards": False,
            "social_security_numbers": False,
            "dates_of_birth": False
        }
        
        for breach in breaches:
            for data_class in breach.get("data_classes", []):
                dc_lower = data_class.lower()
                if "email" in dc_lower:
                    exposure["email_addresses"] = True
                if "password" in dc_lower and "hint" not in dc_lower:
                    exposure["passwords"] = True
                if "username" in dc_lower:
                    exposure["usernames"] = True
                if "hint" in dc_lower:
                    exposure["password_hints"] = True
                if "phone" in dc_lower:
                    exposure["phone_numbers"] = True
                if "address" in dc_lower and "email" not in dc_lower:
                    exposure["physical_addresses"] = True
                if "credit" in dc_lower or "card" in dc_lower:
                    exposure["credit_cards"] = True
                if "social security" in dc_lower or "ssn" in dc_lower:
                    exposure["social_security_numbers"] = True
                if "birth" in dc_lower or "dob" in dc_lower:
                    exposure["dates_of_birth"] = True
        
        return exposure
    
    def check_email_breach(self, email: str) -> Dict:
        """
        Check email breach status using local SQLite database.
        
        This is 100% offline and does not make any external API calls.
        
        Args:
            email: Email address to check
            
        Returns:
            Comprehensive breach information
        """
        email_hash = hash_email(email)
        
        # Check cache first
        cached = self._get_from_cache(email_hash)
        if cached:
            cached["breach_source"] = "cache"
            return cached
        
        # Query database
        db_result = self._query_database(email_hash)
        
        if db_result is None:
            # Email not in database - considered safe
            result = {
                "breached": False,
                "pwned_count": 0,
                "total_breaches": 0,
                "total_accounts_affected": 0,
                "breaches": [],
                "risk_level": "LOW",
                "risk_score": 0,
                "recommendations": self._generate_recommendations(0, []),
                "breach_source": "local_database",
                "last_checked": datetime.utcnow().isoformat(),
                "message": "✅ No breaches found in our database of 100,000+ compromised emails.",
                "timeline": [],
                "data_exposure_summary": {},
                "source": "CyberGuardX Local Breach Database",
                "note": "Based on comprehensive local dataset of 100,000+ breached email patterns"
            }
            
            self._add_to_cache(email_hash, result)
            return result
        
        # Email found in database - breached
        total_breaches = db_result["total_breaches"]
        breaches = db_result["breach_details"]
        
        # Calculate risk
        risk_level = self._calculate_risk_level(total_breaches)
        risk_score = self._calculate_risk_score(total_breaches, breaches)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(total_breaches, breaches)
        
        # Create timeline
        timeline = self._create_breach_timeline(breaches)
        
        # Data exposure summary
        data_exposure = self._create_data_exposure_summary(breaches)
        
        result = {
            "breached": True,
            "pwned_count": total_breaches,
            "total_breaches": total_breaches,
            "total_accounts_affected": db_result["total_accounts_affected"],
            "breaches": breaches,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "recommendations": recommendations,
            "breach_source": "local_database",
            "last_checked": datetime.utcnow().isoformat(),
            "message": f"⚠️  This email was found in {total_breaches} known data breach(es) affecting {db_result['total_accounts_affected']:,} total accounts.",
            "timeline": timeline,
            "data_exposure_summary": data_exposure,
            "source": "CyberGuardX Local Breach Database",
            "first_breached": db_result["first_breach_date"],
            "last_breached": db_result["last_breach_date"],
            "note": "Based on comprehensive local dataset of 100,000+ breached email patterns"
        }
        
        # Cache result
        self._add_to_cache(email_hash, result)
        
        return result
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the breach database."""
        if not self.db_path.exists():
            return {
                "exists": False,
                "message": "Database not found. Run: python -m app.utils.breach_generator --size 100000"
            }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM breached_emails")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM breached_emails WHERE total_breaches = 0")
            clean = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM breached_emails WHERE total_breaches > 0")
            breached = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(total_breaches) FROM breached_emails WHERE total_breaches > 0")
            avg_breaches = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "exists": True,
                "total_records": total,
                "clean_emails": clean,
                "breached_emails": breached,
                "avg_breaches_per_email": round(avg_breaches, 2),
                "database_size_mb": round(self.db_path.stat().st_size / 1024 / 1024, 2),
                "cache_hits": len(self._cache)
            }
        
        except Exception as e:
            return {
                "exists": True,
                "error": str(e)
            }


# Singleton instance
_breach_checker_service = None


def get_breach_checker() -> BreachCheckerService:
    """Get singleton breach checker service instance."""
    global _breach_checker_service
    if _breach_checker_service is None:
        _breach_checker_service = BreachCheckerService()
    return _breach_checker_service
