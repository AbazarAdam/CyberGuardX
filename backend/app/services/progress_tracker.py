"""
Real-time scan progress tracking service
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session

from app.db.models import ScanProgress


class ProgressTracker:
    """Track real-time progress of website scans."""
    
    # Step definitions with progress ranges
    STEPS = {
        1: {"name": "Validating URL and permissions", "range": (0, 10), "substeps": ["URL validation", "Permission check"]},
        2: {"name": "Checking HTTP Security Headers", "range": (10, 30), "substeps": ["HSTS", "CSP", "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy"]},
        3: {"name": "Analyzing SSL/TLS Configuration", "range": (30, 45), "substeps": ["Certificate validation", "Protocol versions", "Cipher strength"]},
        4: {"name": "Scanning DNS Security Records", "range": (45, 60), "substeps": ["SPF check", "DMARC check", "DKIM check", "DNSSEC check", "CAA check"]},
        5: {"name": "Detecting Technology Stack", "range": (60, 75), "substeps": ["Web server detection", "Framework detection", "Library detection", "Security headers"]},
        6: {"name": "Calculating Risk Score", "range": (75, 90), "substeps": ["Weighting findings", "OWASP mapping", "Grade calculation"]},
        7: {"name": "Generating Comprehensive Report", "range": (90, 100), "substeps": ["Report assembly", "Recommendations", "Finalization"]}
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_scan(self, url: str) -> str:
        """Create a new scan progress record."""
        scan_id = str(uuid.uuid4())
        
        progress = ScanProgress(
            scan_id=scan_id,
            url=url,
            current_step=self.STEPS[1]["name"],
            progress_percentage=0,
            step_details=json.dumps({
                "completed": [],
                "current": self.STEPS[1]["substeps"][0] if self.STEPS[1]["substeps"] else None,
                "remaining": self.STEPS[1]["substeps"][1:] if len(self.STEPS[1]["substeps"]) > 1 else []
            }),
            start_time=datetime.utcnow(),
            last_update=datetime.utcnow(),
            estimated_seconds_remaining=50  # Default estimate
        )
        
        self.db.add(progress)
        self.db.commit()
        
        return scan_id
    
    def update_progress(
        self, 
        scan_id: str, 
        step_number: int, 
        substep_index: int = 0,
        force_percentage: Optional[int] = None
    ):
        """Update scan progress to a specific step and substep."""
        progress = self.db.query(ScanProgress).filter(ScanProgress.scan_id == scan_id).first()
        if not progress:
            return
        
        # Check if cancelled
        if progress.is_cancelled:
            return
        
        step_info = self.STEPS.get(step_number)
        if not step_info:
            return
        
        # Calculate progress percentage
        start_pct, end_pct = step_info["range"]
        substeps = step_info["substeps"]
        
        if force_percentage is not None:
            progress_pct = force_percentage
        elif substeps:
            substep_progress = substep_index / len(substeps)
            progress_pct = int(start_pct + (end_pct - start_pct) * substep_progress)
        else:
            progress_pct = start_pct
        
        # Build step details
        completed = substeps[:substep_index] if substeps else []
        current = substeps[substep_index] if substeps and substep_index < len(substeps) else None
        remaining = substeps[substep_index + 1:] if substeps and substep_index < len(substeps) - 1 else []
        
        step_details = {
            "completed": completed,
            "current": current,
            "remaining": remaining
        }
        
        # Calculate estimated time remaining
        elapsed = (datetime.utcnow() - progress.start_time).total_seconds()
        if progress_pct > 0:
            total_estimated = (elapsed / progress_pct) * 100
            time_remaining = max(0, int(total_estimated - elapsed))
        else:
            time_remaining = 50  # Default estimate
        
        # Update record
        progress.current_step = step_info["name"]
        progress.progress_percentage = progress_pct
        progress.step_details = json.dumps(step_details)
        progress.last_update = datetime.utcnow()
        progress.estimated_seconds_remaining = time_remaining
        
        self.db.commit()
    
    def complete_scan(self, scan_id: str):
        """Mark scan as complete."""
        progress = self.db.query(ScanProgress).filter(ScanProgress.scan_id == scan_id).first()
        if progress:
            progress.current_step = "Complete"
            progress.progress_percentage = 100
            progress.is_complete = True
            progress.last_update = datetime.utcnow()
            progress.estimated_seconds_remaining = 0
            self.db.commit()
    
    def set_error(self, scan_id: str, error_message: str):
        """Mark scan as failed with error."""
        progress = self.db.query(ScanProgress).filter(ScanProgress.scan_id == scan_id).first()
        if progress:
            progress.has_error = True
            progress.error_message = error_message
            progress.last_update = datetime.utcnow()
            self.db.commit()
    
    def cancel_scan(self, scan_id: str):
        """Cancel a running scan."""
        progress = self.db.query(ScanProgress).filter(ScanProgress.scan_id == scan_id).first()
        if progress:
            progress.is_cancelled = True
            progress.last_update = datetime.utcnow()
            self.db.commit()
    
    def get_progress(self, scan_id: str) -> Optional[Dict]:
        """Get current progress for a scan."""
        progress = self.db.query(ScanProgress).filter(ScanProgress.scan_id == scan_id).first()
        if not progress:
            return None
        
        elapsed = (datetime.utcnow() - progress.start_time).total_seconds()
        elapsed_str = str(timedelta(seconds=int(elapsed)))[2:]  # Remove days, format as HH:MM:SS
        
        remaining_str = None
        if progress.estimated_seconds_remaining is not None:
            remaining_str = str(timedelta(seconds=progress.estimated_seconds_remaining))[2:]
        
        step_details = None
        if progress.step_details:
            try:
                step_details = json.loads(progress.step_details)
            except:
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
            "is_cancelled": progress.is_cancelled
        }
    
    def cleanup_old_scans(self, hours: int = 24):
        """Clean up progress records older than specified hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        self.db.query(ScanProgress).filter(ScanProgress.start_time < cutoff).delete()
        self.db.commit()
