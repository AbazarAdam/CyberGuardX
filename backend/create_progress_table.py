"""
Create ScanProgress table in database
Run this once to add the new table for real-time progress tracking
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.database import Base, engine
from app.db.models import ScanProgress

def create_scan_progress_table():
    """Create the scan_progress table."""
    print("Creating ScanProgress table...")
    try:
        Base.metadata.create_all(bind=engine, tables=[ScanProgress.__table__])
        print("✅ ScanProgress table created successfully!")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_scan_progress_table()
