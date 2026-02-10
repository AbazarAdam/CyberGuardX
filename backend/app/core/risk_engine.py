from typing import Optional


def calculate_risk_level(
    email_breached: bool,
    phishing_score: Optional[float] = None,
) -> str:
    """
    Calculate risk level based on breach status and phishing score.
    
    Args:
        email_breached: Whether the email was found in breach dataset
        phishing_score: ML-generated phishing probability (0.0 to 1.0)
    
    Returns:
        Risk level: "LOW", "MEDIUM", or "HIGH"
    """
    if phishing_score is not None and phishing_score >= 0.7:
        return "HIGH"
    
    if email_breached:
        return "MEDIUM"
    
    return "LOW"
