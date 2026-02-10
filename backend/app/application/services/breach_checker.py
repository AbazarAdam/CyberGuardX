"""
Application Service — Email Breach Checker
============================================
100 % offline breach lookup backed by a local SQLite database
of 100 000+ email records across 15 real-world breaches.

Design decisions
----------------
* **No external API calls** — privacy-first, zero network latency.
* **LRU cache** — repeat queries are answered from memory (~0 ms).
* **Single entry-point** — ``check_email_breach(email)`` returns a rich dict
  that the presentation layer can serialise directly.
"""

import hashlib
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from app.config import BREACH_DB_PATH
from app.utils.logger import get_logger

logger = get_logger(__name__)


def hash_email(email: str) -> str:
    """SHA-1 hash an email for privacy (compatible with HIBP API)."""
    normalized = email.strip().lower()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()


class BreachCheckerService:
    """Service for checking email breaches using the local SQLite database."""

    def __init__(self):
        self.db_path = BREACH_DB_PATH
        self._ensure_database_exists()
        # Simple bounded cache (last 1 000 queries kept in memory)
        self._cache: Dict[str, Dict] = {}
        self._cache_size = 1_000

    # ------------------------------------------------------------------
    # Database bootstrap
    # ------------------------------------------------------------------

    def _ensure_database_exists(self) -> None:
        """Warn (but don't crash) if the breach DB hasn't been generated yet."""
        if not self.db_path.exists():
            logger.warning(
                f"Breach database not found at {self.db_path}. "
                f"Run: python -m scripts.generate_breach_db --size 100000"
            )

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _get_from_cache(self, email_hash: str) -> Optional[Dict]:
        return self._cache.get(email_hash)

    def _add_to_cache(self, email_hash: str, data: Dict) -> None:
        if len(self._cache) >= self._cache_size:
            # Evict the oldest entry (insertion-order dict since Python 3.7)
            self._cache.pop(next(iter(self._cache)))
        self._cache[email_hash] = data

    # ------------------------------------------------------------------
    # SQLite queries
    # ------------------------------------------------------------------

    def _query_database(self, email_hash: str) -> Optional[Dict]:
        """Return breach row for *email_hash* or ``None``."""
        if not self.db_path.exists():
            return None
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT email_hash, total_breaches, first_breach_date,
                       last_breach_date, total_accounts_affected, breach_details
                FROM breached_emails
                WHERE email_hash = ?
                """,
                (email_hash,),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "email_hash": row[0],
                    "total_breaches": row[1],
                    "first_breach_date": row[2],
                    "last_breach_date": row[3],
                    "total_accounts_affected": row[4],
                    "breach_details": json.loads(row[5]) if row[5] else [],
                }
            return None
        except Exception as exc:
            logger.error(f"Database query error: {exc}", exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Risk calculation (domain logic kept close for cohesion)
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_risk_level(total_breaches: int) -> str:
        if total_breaches == 0:
            return "LOW"
        if total_breaches == 1:
            return "MEDIUM"
        if total_breaches <= 3:
            return "HIGH"
        return "CRITICAL"

    @staticmethod
    def _calculate_risk_score(total_breaches: int, breaches: List[Dict]) -> int:
        """
        Weighted risk score (0–100).

        Factors:
            40 % — breach count
            30 % — average severity
            20 % — recency of last breach
            10 % — total accounts affected
        """
        if total_breaches == 0:
            return 0

        # Breach count component (max 40)
        count_score = min(total_breaches * 8, 40)

        # Severity component (max 30)
        severity_map = {"CRITICAL": 30, "HIGH": 25, "MEDIUM": 15, "LOW": 10}
        severity_score = (
            sum(severity_map.get(b.get("severity", "MEDIUM"), 15) for b in breaches)
            / len(breaches)
            if breaches
            else 15
        )

        # Recency component (max 20)
        try:
            if breaches and breaches[-1].get("date"):
                last_year = int(breaches[-1]["date"][:4])
                years_ago = 2026 - last_year
                recency_score = max(20 - years_ago, 0)
            else:
                recency_score = 10
        except (ValueError, TypeError):
            recency_score = 10

        # Accounts component (max 10)
        total_accounts = sum(b.get("accounts", 0) for b in breaches)
        if total_accounts > 1_000_000_000:
            accounts_score = 10
        elif total_accounts > 100_000_000:
            accounts_score = 8
        elif total_accounts > 10_000_000:
            accounts_score = 6
        else:
            accounts_score = 4

        return min(int(count_score + severity_score + recency_score + accounts_score), 100)

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_recommendations(total_breaches: int, breaches: List[Dict]) -> List[str]:
        if total_breaches == 0:
            return [
                "✅ Your email appears safe in our database",
                "🔐 Continue using unique passwords for different services",
                "📱 Enable two-factor authentication where available",
                "🔔 Set up breach alerts at haveibeenpwned.com for real-time monitoring",
            ]

        recs = [
            "🚨 URGENT: Change passwords immediately for all affected accounts",
            "🔐 Enable two-factor authentication (2FA) on all services",
            "🔍 Check for reused passwords across different accounts",
            "📧 Be extra cautious of phishing emails targeting these services",
        ]

        # Flag sensitive data exposure
        sensitive_keywords = {"credit", "social security", "ssn", "bank", "financial"}
        has_sensitive = any(
            any(kw in dc.lower() for kw in sensitive_keywords)
            for b in breaches
            for dc in b.get("data_classes", [])
        )
        if has_sensitive:
            recs += [
                "⚠️  CRITICAL: Monitor credit reports for suspicious activity",
                "💳 Consider placing a fraud alert with credit bureaus",
                "🔒 Review financial accounts for unauthorised transactions",
            ]

        if total_breaches >= 3:
            recs += [
                "🔁 Use a password manager to generate unique passwords",
                "📊 Consider using privacy-focused email aliases",
            ]
        recs.append("🔔 Set up breach monitoring at haveibeenpwned.com")
        return recs

    # ------------------------------------------------------------------
    # Timeline & exposure helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _create_breach_timeline(breaches: List[Dict]) -> List[Dict]:
        return [
            {
                "date": b.get("date"),
                "event": f"{b.get('name')} breach",
                "accounts": b.get("accounts"),
                "severity": b.get("severity", "MEDIUM"),
            }
            for b in sorted(breaches, key=lambda x: x.get("date", ""))
        ]

    @staticmethod
    def _create_data_exposure_summary(breaches: List[Dict]) -> Dict[str, bool]:
        exposure = {
            "email_addresses": False,
            "passwords": False,
            "usernames": False,
            "password_hints": False,
            "phone_numbers": False,
            "physical_addresses": False,
            "credit_cards": False,
            "social_security_numbers": False,
            "dates_of_birth": False,
        }
        for breach in breaches:
            for dc in breach.get("data_classes", []):
                low = dc.lower()
                if "email" in low:
                    exposure["email_addresses"] = True
                if "password" in low and "hint" not in low:
                    exposure["passwords"] = True
                if "username" in low:
                    exposure["usernames"] = True
                if "hint" in low:
                    exposure["password_hints"] = True
                if "phone" in low:
                    exposure["phone_numbers"] = True
                if "address" in low and "email" not in low:
                    exposure["physical_addresses"] = True
                if "credit" in low or "card" in low:
                    exposure["credit_cards"] = True
                if "social security" in low or "ssn" in low:
                    exposure["social_security_numbers"] = True
                if "birth" in low or "dob" in low:
                    exposure["dates_of_birth"] = True
        return exposure

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_email_breach(self, email: str) -> Dict:
        """
        Check email breach status against the local SQLite database.

        This is 100 % offline — no external API calls are made.

        Args:
            email: Email address to check.

        Returns:
            Rich dictionary with breach info, risk score, recommendations, etc.
        """
        email_hash = hash_email(email)

        # 1. Cache hit?
        cached = self._get_from_cache(email_hash)
        if cached:
            cached["breach_source"] = "cache"
            return cached

        # 2. Database lookup
        db_result = self._query_database(email_hash)

        if db_result is None:
            # Email is clean
            result: Dict = {
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
                "note": "Based on comprehensive local dataset of 100,000+ breached email patterns",
            }
            self._add_to_cache(email_hash, result)
            return result

        # 3. Breached — enrich the result
        total = db_result["total_breaches"]
        breaches = db_result["breach_details"]
        risk_level = self._calculate_risk_level(total)
        risk_score = self._calculate_risk_score(total, breaches)

        result = {
            "breached": True,
            "pwned_count": total,
            "total_breaches": total,
            "total_accounts_affected": db_result["total_accounts_affected"],
            "breaches": breaches,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "recommendations": self._generate_recommendations(total, breaches),
            "breach_source": "local_database",
            "last_checked": datetime.utcnow().isoformat(),
            "message": (
                f"⚠️  This email was found in {total} known data breach(es) "
                f"affecting {db_result['total_accounts_affected']:,} total accounts."
            ),
            "timeline": self._create_breach_timeline(breaches),
            "data_exposure_summary": self._create_data_exposure_summary(breaches),
            "source": "CyberGuardX Local Breach Database",
            "first_breached": db_result["first_breach_date"],
            "last_breached": db_result["last_breach_date"],
            "note": "Based on comprehensive local dataset of 100,000+ breached email patterns",
        }
        self._add_to_cache(email_hash, result)
        return result

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_database_stats(self) -> Dict:
        """Return summary statistics about the breach database."""
        if not self.db_path.exists():
            return {"exists": False, "message": "Database not found."}
        try:
            conn = sqlite3.connect(str(self.db_path))
            cur = conn.cursor()
            total = cur.execute("SELECT COUNT(*) FROM breached_emails").fetchone()[0]
            clean = cur.execute("SELECT COUNT(*) FROM breached_emails WHERE total_breaches = 0").fetchone()[0]
            breached = cur.execute("SELECT COUNT(*) FROM breached_emails WHERE total_breaches > 0").fetchone()[0]
            avg = cur.execute("SELECT AVG(total_breaches) FROM breached_emails WHERE total_breaches > 0").fetchone()[0] or 0
            conn.close()
            return {
                "exists": True,
                "total_records": total,
                "clean_emails": clean,
                "breached_emails": breached,
                "avg_breaches_per_email": round(avg, 2),
                "database_size_mb": round(self.db_path.stat().st_size / 1024 / 1024, 2),
                "cache_hits": len(self._cache),
            }
        except Exception as exc:
            return {"exists": True, "error": str(exc)}


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------
_breach_checker_service: Optional[BreachCheckerService] = None


def get_breach_checker() -> BreachCheckerService:
    """Return a module-level singleton ``BreachCheckerService``."""
    global _breach_checker_service
    if _breach_checker_service is None:
        _breach_checker_service = BreachCheckerService()
    return _breach_checker_service
