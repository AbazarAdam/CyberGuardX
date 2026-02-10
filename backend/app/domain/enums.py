"""
Domain Enumerations
====================
Shared enums used across every layer of the application.
Centralising them here avoids circular imports and keeps the domain pure.
"""

from enum import Enum


class RiskLevel(str, Enum):
    """Risk classification returned to users."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Grade(str, Enum):
    """Letter-grade scale for security scoring."""
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class Severity(str, Enum):
    """Vulnerability severity aligned with CVSS qualitative ratings."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class SecurityPosture(str, Enum):
    """Human-readable summary of overall security health."""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    CRITICAL = "CRITICAL"
