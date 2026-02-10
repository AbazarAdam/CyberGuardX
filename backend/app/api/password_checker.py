"""
CyberGuardX - Password Strength Checker API Endpoint
Provides comprehensive password analysis and secure generation.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any

from ..security.password_analyzer import PasswordStrengthAnalyzer

router = APIRouter()
analyzer = PasswordStrengthAnalyzer()


class PasswordCheckRequest(BaseModel):
    password: str


class PasswordGenerateRequest(BaseModel):
    length: int = 16
    mode: str = "random"  # "random" or "memorable"
    include_upper: bool = True
    include_lower: bool = True
    include_digits: bool = True
    include_special: bool = True


@router.post("/check-password")
async def check_password(request: PasswordCheckRequest):
    """
    Analyze password strength with comprehensive metrics.
    
    Returns:
        - Strength score (0-100)
        - Entropy calculation
        - Pattern detection (keyboard walks, sequences, leet speak)
        - Time-to-crack estimates
        - Breach database check
        - Actionable recommendations
    """
    if not request.password:
        raise HTTPException(status_code=400, detail="Password cannot be empty")
    
    if len(request.password) > 256:
        raise HTTPException(status_code=400, detail="Password too long (max 256 characters)")
    
    result = analyzer.analyze(request.password)
    
    # Don't return the actual password in the response
    return result


@router.post("/generate-password")
async def generate_password(request: PasswordGenerateRequest):
    """
    Generate a secure password.
    
    Args:
        length: Password length (8-128)
        mode: 'random' for random characters, 'memorable' for passphrase
    
    Returns:
        Generated password with strength analysis.
    """
    if request.length < 8:
        raise HTTPException(status_code=400, detail="Minimum password length is 8")
    if request.length > 128:
        raise HTTPException(status_code=400, detail="Maximum password length is 128")
    
    result = analyzer.generate_password(
        length=request.length,
        mode=request.mode,
        include_upper=request.include_upper,
        include_lower=request.include_lower,
        include_digits=request.include_digits,
        include_special=request.include_special
    )
    
    return result
