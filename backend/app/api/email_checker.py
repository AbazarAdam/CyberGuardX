from pathlib import Path
import json

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import EmailCheckRequest, EmailCheckResponse, BreachDetail
from app.core.risk_engine import calculate_risk_level
from app.db.database import SessionLocal
from app.db.models import ScanHistory
from app.utils.hashing import hash_email
from app.services.breach_checker import get_breach_checker

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/check-email", response_model=EmailCheckResponse)
def check_email(payload: EmailCheckRequest, db: Session = Depends(get_db)):
    """
    Enhanced email breach checker with hybrid approach:
    1. Check local dataset first (fast)
    2. Try Have I Been Pwned API if not found
    3. Provide intelligent simulation if API unavailable
    """
    try:
        # Get breach checker service
        breach_checker = get_breach_checker()
        
        # Perform hybrid breach check
        breach_result = breach_checker.check_email_breach(payload.email)
        
        # Extract results
        breached = breach_result["breached"]
        pwned_count = breach_result.get("pwned_count", 0)
        breaches_data = breach_result.get("breaches", [])
        risk_level = breach_result["risk_level"]
        recommendations = breach_result.get("recommendations", [])
        breach_source = breach_result.get("breach_source", "unknown")
        last_checked = breach_result.get("last_checked")
        message = breach_result["message"]
        
        # Convert breaches to BreachDetail models
        breach_details = [
            BreachDetail(
                name=b["name"],
                date=b["date"],
                accounts=b["accounts"],
                data_classes=b["data_classes"]
            )
            for b in breaches_data
        ]
        
        # Save to database
        scan = ScanHistory(
            email=payload.email,
            email_breached=breached,
            phishing_score=None,
            risk_level=risk_level,
            pwned_count=pwned_count,
            breach_details=json.dumps(breaches_data) if breaches_data else None,
            breach_source=breach_source,
            last_checked=last_checked
        )
        
        try:
            db.add(scan)
            db.commit()
            db.refresh(scan)
        except Exception as exc:
            db.rollback()
            print(f"Warning: Failed to save scan record: {exc}")
            # Continue anyway - don't fail the request
        
        return EmailCheckResponse(
            email=payload.email,
            breached=breached,
            pwned_count=pwned_count,
            risk_level=risk_level,
            message=message,
            breaches=breach_details,
            recommendations=recommendations,
            last_checked=last_checked,
            breach_source=breach_source
        )
    
    except Exception as exc:
        print(f"Error in check_email endpoint: {exc}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while checking email breach status"
        )
