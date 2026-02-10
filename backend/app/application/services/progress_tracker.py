"""
Application Service — Scan Progress Tracker
=============================================
Tracks step-by-step progress for long-running website scans so the
frontend can poll ``GET /scan-progress/{id}`` and render a live progress bar.

7 scan steps
------------
1. URL validation & permission check
2. HTTP security headers
3. SSL / TLS configuration
4. DNS security records
5. Technology stack detection
6. Risk score calculation
7. Report generation
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.infrastructure.database.models import ScanProgress


class ProgressTracker:
    """Manages ``ScanProgress`` rows in the database."""

    # Each step has a human-readable name, a progress % range, and sub-steps.
    STEPS = {
        1: {
            "name": "Validating URL and permissions",
            "range": (0, 10),
            "substeps": ["URL validation", "Permission check"],
        },
        2: {
            "name": "Checking HTTP Security Headers",
            "range": (10, 30),
            "substeps": [
                "HSTS", "CSP", "X-Frame-Options",
                "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy",
            ],
        },
        3: {
            "name": "Analyzing SSL/TLS Configuration",
            "range": (30, 45),
            "substeps": ["Certificate validation", "Protocol versions", "Cipher strength"],
        },
        4: {
            "name": "Scanning DNS Security Records",
            "range": (45, 60),
            "substeps": ["SPF check", "DMARC check", "DKIM check", "DNSSEC check", "CAA check"],
        },
        5: {
            "name": "Detecting Technology Stack",
            "range": (60, 75),
            "substeps": ["Web server detection", "Framework detection", "Library detection", "Security headers"],
        },
        6: {
            "name": "Calculating Risk Score",
            "range": (75, 90),
            "substeps": ["Weighting findings", "OWASP mapping", "Grade calculation"],
        },
        7: {
            "name": "Generating Comprehensive Report",
            "range": (90, 100),
            "substeps": ["Report assembly", "Recommendations", "Finalization"],
        },
    }

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def create_scan(self, url: str) -> str:
        """Create a new progress record and return its UUID."""
        scan_id = str(uuid.uuid4())
        first_step = self.STEPS[1]
        progress = ScanProgress(
            scan_id=scan_id,
            url=url,
            current_step=first_step["name"],
            progress_percentage=0,
            step_details=json.dumps({
                "completed": [],
                "current": first_step["substeps"][0] if first_step["substeps"] else None,
                "remaining": first_step["substeps"][1:],
            }),
            start_time=datetime.utcnow(),
            last_update=datetime.utcnow(),
            estimated_seconds_remaining=50,
        )
        self.db.add(progress)
        self.db.commit()
        return scan_id

    def update_progress(
        self,
        scan_id: str,
        step_number: int,
        substep_index: int = 0,
        force_percentage: Optional[int] = None,
    ) -> None:
        """Move the progress indicator to *step_number* / *substep_index*."""
        progress = self.db.query(ScanProgress).filter(ScanProgress.scan_id == scan_id).first()
        if not progress or progress.is_cancelled:
            return

        step_info = self.STEPS.get(step_number)
        if not step_info:
            return

        start_pct, end_pct = step_info["range"]
        substeps = step_info["substeps"]

        # Calculate overall percentage
        if force_percentage is not None:
            pct = force_percentage
        elif substeps:
            ratio = substep_index / len(substeps)
            pct = int(start_pct + (end_pct - start_pct) * ratio)
        else:
            pct = start_pct

        # Build sub-step details
        completed = substeps[:substep_index] if substeps else []
        current = substeps[substep_index] if substeps and substep_index < len(substeps) else None
        remaining = substeps[substep_index + 1:] if substeps and substep_index < len(substeps) - 1 else []

        # Estimate time remaining
        elapsed = (datetime.utcnow() - progress.start_time).total_seconds()
        if pct > 0:
            total_est = (elapsed / pct) * 100
            time_remaining = max(0, int(total_est - elapsed))
        else:
            time_remaining = 50

        progress.current_step = step_info["name"]
        progress.progress_percentage = pct
        progress.step_details = json.dumps({"completed": completed, "current": current, "remaining": remaining})
        progress.last_update = datetime.utcnow()
        progress.estimated_seconds_remaining = time_remaining
        self.db.commit()

    def complete_scan(self, scan_id: str) -> None:
        progress = self.db.query(ScanProgress).filter(ScanProgress.scan_id == scan_id).first()
        if progress:
            progress.current_step = "Complete"
            progress.progress_percentage = 100
            progress.is_complete = True
            progress.last_update = datetime.utcnow()
            progress.estimated_seconds_remaining = 0
            self.db.commit()

    def set_error(self, scan_id: str, error_message: str) -> None:
        progress = self.db.query(ScanProgress).filter(ScanProgress.scan_id == scan_id).first()
        if progress:
            progress.has_error = True
            progress.error_message = error_message
            progress.last_update = datetime.utcnow()
            self.db.commit()

    def cancel_scan(self, scan_id: str) -> None:
        progress = self.db.query(ScanProgress).filter(ScanProgress.scan_id == scan_id).first()
        if progress:
            progress.is_cancelled = True
            progress.last_update = datetime.utcnow()
            self.db.commit()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_progress(self, scan_id: str) -> Optional[Dict]:
        """Return the current progress dict for the frontend to consume."""
        progress = self.db.query(ScanProgress).filter(ScanProgress.scan_id == scan_id).first()
        if not progress:
            return None

        elapsed = (datetime.utcnow() - progress.start_time).total_seconds()
        elapsed_str = str(timedelta(seconds=int(elapsed)))[2:]  # MM:SS

        remaining_str = None
        if progress.estimated_seconds_remaining is not None:
            remaining_str = str(timedelta(seconds=progress.estimated_seconds_remaining))[2:]

        step_details = None
        if progress.step_details:
            try:
                step_details = json.loads(progress.step_details)
            except json.JSONDecodeError:
                pass

        return {
            "scan_id": progress.scan_id,
            "url": progress.url,
            "current_step": progress.current_step,
            "progress_percentage": progress.progress_percentage,
            "step_details": step_details,
            "time_elapsed": elapsed_str,
            "estimated_remaining": remaining_str,
            "is_complete": progress.is_complete,
            "has_error": progress.has_error,
            "error_message": progress.error_message,
            "is_cancelled": progress.is_cancelled,
        }

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def cleanup_old_scans(self, hours: int = 24) -> None:
        """Delete progress rows older than *hours*."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        self.db.query(ScanProgress).filter(ScanProgress.start_time < cutoff).delete()
        self.db.commit()
