from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.schemas import ScanHistoryResponse
from app.db.database import SessionLocal
from app.db.models import ScanHistory

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/scan-history", response_model=List[ScanHistoryResponse])
def get_scan_history(db: Session = Depends(get_db)):
    try:
        # Only query basic columns that exist in all database versions
        records = (
            db.query(
                ScanHistory.id,
                ScanHistory.email,
                ScanHistory.email_breached,
                ScanHistory.phishing_score,
                ScanHistory.risk_level,
                ScanHistory.scanned_at
            )
            .order_by(ScanHistory.scanned_at.desc())
            .limit(50)  # Limit to last 50 records
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
            detail=f"Failed to load history: {str(exc)}"
        ) from exc
