"""
Application Layer — CyberGuardX
=================================
Orchestrates use-cases by combining domain rules with infrastructure services.
Each service here represents a single user-facing capability.

Structure::

    application/
    ├── __init__.py
    └── services/
        ├── breach_checker.py       — email breach lookup
        ├── progress_tracker.py     — real-time scan progress
        ├── report_generator.py     — HTML security report builder
        └── website_scan_service.py — orchestrates the full website scan
"""
