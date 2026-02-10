"""
Route — Email Breach Checker
==============================
``POST /check-email`` — checks an email against the offline breach database.
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.presentation.schemas import (
    EmailCheckRequest,
    EmailCheckResponse,
    BreachDetail,
)
from app.presentation.dependencies import get_db
from app.domain.risk_engine import calculate_risk_level
from app.infrastructure.database.models import ScanHistory
from app.application.services.breach_checker import get_breach_checker
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/check-email", response_model=EmailCheckResponse)
def check_email(payload: EmailCheckRequest, db: Session = Depends(get_db)):
    """
    Hybrid email breach checker.

    1. Check the local offline dataset (fast, ~0 ms cached).
    2. Return breach details, risk level, and recommendations.
    """
    try:
        breach_checker = get_breach_checker()
        breach_result = breach_checker.check_email_breach(payload.email)

        breached = breach_result["breached"]
        pwned_count = breach_result.get("pwned_count", 0)
        breaches_data = breach_result.get("breaches", [])
        risk_level = breach_result["risk_level"]
        recommendations = breach_result.get("recommendations", [])
        breach_source = breach_result.get("breach_source", "unknown")
        last_checked = breach_result.get("last_checked")
        message = breach_result["message"]

        breach_details = [
            BreachDetail(
                name=b["name"],
                date=b["date"],
                accounts=b["accounts"],
                data_classes=b["data_classes"],
            )
            for b in breaches_data
        ]

        # Persist audit record (best-effort — never fail the request)
        scan = ScanHistory(
            email=payload.email,
            email_breached=breached,
            phishing_score=None,
            risk_level=risk_level,
            pwned_count=pwned_count,
            breach_details=json.dumps(breaches_data) if breaches_data else None,
            breach_source=breach_source,
            last_checked=last_checked,
        )
        try:
            db.add(scan)
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.warning(f"Failed to save email scan record: {exc}")

        return EmailCheckResponse(
            email=payload.email,
            breached=breached,
            pwned_count=pwned_count,
            risk_level=risk_level,
            message=message,
            breaches=breach_details,
            recommendations=recommendations,
            last_checked=last_checked,
            breach_source=breach_source,
        )

    except Exception as exc:
        logger.error(f"Error in /check-email endpoint: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Email breach check failed")
