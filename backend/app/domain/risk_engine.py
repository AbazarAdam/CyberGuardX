"""
Domain — Risk Engine
=====================
Pure business rule: given breach status and phishing score, return a risk level.
No database, no HTTP, no framework imports — just logic.
"""

from typing import Optional


def calculate_risk_level(
    email_breached: bool,
    phishing_score: Optional[float] = None,
) -> str:
    """
    Calculate risk level based on breach status and phishing score.

    Args:
        email_breached: Whether the email was found in a breach dataset.
        phishing_score: ML-generated phishing probability (0.0 – 1.0).

    Returns:
        One of ``"LOW"``, ``"MEDIUM"``, ``"HIGH"``, or ``"CRITICAL"``.
    """
    # High-confidence phishing → CRITICAL
    if phishing_score is not None and phishing_score >= 0.85:
        return "CRITICAL"

    # Likely phishing → HIGH
    if phishing_score is not None and phishing_score >= 0.7:
        return "HIGH"

    # Breached email → MEDIUM
    if email_breached:
        return "MEDIUM"

    return "LOW"
