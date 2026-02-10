"""
Domain Enumerations
====================
Shared enums used across every layer of the application.
"""

from enum import Enum


class RiskLevel(str, Enum):
    """Unified risk and severity classification."""
    MINIMAL = "MINIMAL"
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


class SecurityPosture(str, Enum):
    """Overall security health summary."""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    CRITICAL = "CRITICAL"
