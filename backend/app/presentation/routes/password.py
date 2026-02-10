"""
Route — Password Checker & Generator
======================================
``POST /check-password``   — Analyse strength with entropy, pattern
detection, and breach-check.
``POST /generate-password`` — Securely generate a random or memorable
password.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any

from app.infrastructure.security.password_analyzer import PasswordStrengthAnalyzer

router = APIRouter()

# Singleton analyser — initialised once, reused by all requests.
analyzer = PasswordStrengthAnalyzer()


# ──────────────────────────────────────────────────────────────────────────
# Request schemas (kept co-located for self-contained readability)
# ──────────────────────────────────────────────────────────────────────────

class PasswordCheckRequest(BaseModel):
    """Payload for the check-password endpoint."""
    password: str


class PasswordGenerateRequest(BaseModel):
    """Payload for the generate-password endpoint."""
    length: int = 16
    mode: str = "random"          # "random" or "memorable"
    include_upper: bool = True
    include_lower: bool = True
    include_digits: bool = True
    include_special: bool = True


# ──────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────

@router.post("/check-password")
async def check_password(request: PasswordCheckRequest):
    """
    Analyse password strength with comprehensive metrics.

    Returns strength score (0–100), entropy, pattern detection
    (keyboard walks, sequences, leet-speak), time-to-crack estimates,
    breach-database check, and actionable recommendations.
    """
    if not request.password:
        raise HTTPException(status_code=400, detail="Password cannot be empty")

    if len(request.password) > 256:
        raise HTTPException(
            status_code=400,
            detail="Password too long (max 256 characters)",
        )

    # Delegate to the analyser — never return the raw password.
    return analyzer.analyze(request.password)


@router.post("/generate-password")
async def generate_password(request: PasswordGenerateRequest):
    """
    Securely generate a password.

    Args:
        length: 8–128 characters.
        mode: ``"random"`` for random chars, ``"memorable"`` for passphrase.

    Returns the generated password together with its strength analysis.
    """
    if request.length < 8:
        raise HTTPException(status_code=400, detail="Minimum password length is 8")
    if request.length > 128:
        raise HTTPException(status_code=400, detail="Maximum password length is 128")

    return analyzer.generate_password(
        length=request.length,
        mode=request.mode,
        include_upper=request.include_upper,
        include_lower=request.include_lower,
        include_digits=request.include_digits,
        include_special=request.include_special,
    )
