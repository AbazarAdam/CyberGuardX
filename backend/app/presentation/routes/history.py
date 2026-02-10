"""
Route — Scan History (Email / URL Checks)
==========================================
``GET /scan-history`` — returns the most recent email & URL scan records.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.presentation.schemas import ScanHistoryResponse
from app.presentation.dependencies import get_db
from app.infrastructure.database.models import ScanHistory

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────
# Endpoint
# ──────────────────────────────────────────────────────────────────────────

@router.get("/scan-history", response_model=List[ScanHistoryResponse])
def get_scan_history(db: Session = Depends(get_db)):
    """
    Retrieve the last 50 email / URL scan records ordered newest-first.

    URL-only scans (where ``email == 'URL_SCAN'``) are relabelled as
    *"URL Check"* for readability in the frontend.
    """
    try:
        records = (
            db.query(
                ScanHistory.id,
                ScanHistory.email,
                ScanHistory.email_breached,
                ScanHistory.phishing_score,
                ScanHistory.risk_level,
                ScanHistory.scanned_at,
            )
            .order_by(ScanHistory.scanned_at.desc())
            .limit(50)
            .all()
        )

        return [
            ScanHistoryResponse(
                id=record.id,
                email=record.email if record.email != "URL_SCAN" else "URL Check",
                email_breached=record.email_breached,
                phishing_score=record.phishing_score,
                risk_level=record.risk_level,
                scanned_at=record.scanned_at,
            )
            for record in records
        ]
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load history: {exc}",
        ) from exc
