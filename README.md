# CyberGuardX – Intelligent Web Security Assessment Platform

> Professional-grade cybersecurity tool combining email breach detection, ML-powered phishing URL classification, password strength analysis, and deep website vulnerability scanning.

---

## Quick Start (3 Steps)

### 1. Start Backend
```powershell
cd backend
..\venv\Scripts\activate       # or: ..\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend
```powershell
cd frontend
python -m http.server 3000
```

### 3. Open Browser
```
http://localhost:3000
```

> **API Docs**: http://localhost:8000/docs (Swagger) | http://localhost:8000/redoc

---

## Features

| Module | Description |
|--------|-------------|
| **Email Breach Checker** | Checks emails against 100K+ offline breach records across 15 real-world breaches (Adobe, LinkedIn, Yahoo, etc.) |
| **URL Phishing Detector** | ML-powered (Logistic Regression, 10 features) with explainability — shows feature impacts, confidence scores |
| **Password Strength Analyzer** | Entropy calculation, pattern detection (keyboard walks, leet speak, sequences), crack time estimates, breach DB check, password generator |
| **Website Security Scanner** | Deep vulnerability analysis with 18 checks, CWE/CVSS scoring, OWASP Top 10 mapping, compliance frameworks (PCI-DSS, GDPR, HIPAA, SOC 2, NIST), WAF detection, fix instructions per platform |
| **PDF Security Report** | Professional HTML report generation with cyberpunk styling, print-to-PDF ready |
| **Scan History** | Persistent audit trail of all scans stored in SQLite |
| **Real-Time Progress** | 7-step animated progress tracker with 2-second polling |

---

## Test Data

### Breach Emails
| Email | Breaches | Risk Level |
|-------|----------|------------|
| `test@example.com` | 3 (Adobe, LinkedIn, Yahoo) | HIGH |
| `demo@cyberguardx.com` | 5 | CRITICAL |
| `user@test.com` | 2 | HIGH |
| `admin@sample.com` | 4 | HIGH |
| `safe@example.com` | 0 | LOW |

### Phishing URLs
| URL | Expected Result |
|-----|-----------------|
| `https://google.com` | Legitimate (low score) |
| `http://paypal-login-verify.suspicious-site.com/secure` | Phishing (high score) |
| `http://192.168.1.1/admin/login.php?user=admin` | Phishing (IP-based) |

### Website Scan Targets (Authorized)
| URL | Notes |
|-----|-------|
| `https://example.com` | Basic test target |
| `https://httpbin.org` | Returns useful security header mix |
| `http://testphp.vulnweb.com` | Intentionally vulnerable (educational) |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Database | SQLite + SQLAlchemy ORM |
| ML | scikit-learn (Logistic Regression) |
| Frontend | Vanilla HTML/CSS/JS, Cyberpunk theme |
| Security | dnspython, cryptography, hashlib |

---

## Project Structure (Clean Architecture)

```
CyberGuardX/
├── backend/
│   ├── app/
│   │   ├── main.py                          # Composition root — wires all layers
│   │   ├── config.py                        # Centralised settings (paths, CORS, etc.)
│   │   ├── domain/                          # Pure business logic (zero dependencies)
│   │   │   ├── enums.py                     # RiskLevel, Grade, Severity, SecurityPosture
│   │   │   └── risk_engine.py               # calculate_risk_level() — deterministic rules
│   │   ├── application/                     # Use-cases / orchestration
│   │   │   └── services/
│   │   │       ├── breach_checker.py         # Offline breach lookup service
│   │   │       ├── progress_tracker.py       # Scan progress state-machine
│   │   │       └── report_generator.py       # HTML security report builder
│   │   ├── infrastructure/                  # External concerns
│   │   │   ├── database/
│   │   │   │   ├── connection.py             # SQLAlchemy engine & SessionLocal
│   │   │   │   └── models.py                # ORM models (ScanHistory, WebsiteScan, ScanProgress)
│   │   │   ├── ml/
│   │   │   │   ├── feature_extractor.py      # 10 lexical URL features
│   │   │   │   ├── trainer.py                # Model training pipeline
│   │   │   │   └── evaluator.py              # Metrics & evaluation
│   │   │   ├── security/                    # 9 scanner modules
│   │   │   │   ├── http_scanner.py           # 15 HTTP security headers
│   │   │   │   ├── ssl_scanner.py            # TLS / certificate analysis
│   │   │   │   ├── dns_scanner.py            # SPF, DMARC, DNSSEC
│   │   │   │   ├── tech_detector.py          # Server / framework fingerprinting
│   │   │   │   ├── risk_scorer.py            # Weighted 0-100 risk scoring
│   │   │   │   ├── owasp_assessor.py         # OWASP Top 10 mapping
│   │   │   │   ├── vulnerability_engine.py   # 18 deep vulnerability definitions
│   │   │   │   ├── password_analyzer.py      # Password strength + generator
│   │   │   │   └── safety_validator.py       # Rate limiting, legal checks
│   │   │   └── external/
│   │   │       ├── hibp_client.py            # HIBP API client (k-anonymity)
│   │   │       └── breach_data.py            # 15 realistic breach definitions
│   │   ├── presentation/                    # HTTP layer (FastAPI)
│   │   │   ├── schemas.py                   # All Pydantic request / response models
│   │   │   ├── dependencies.py              # Shared get_db() dependency
│   │   │   └── routes/
│   │   │       ├── email.py                  # POST /check-email
│   │   │       ├── url.py                    # POST /check-url
│   │   │       ├── password.py               # POST /check-password, /generate-password
│   │   │       ├── scanner.py                # POST /scan-website, GET /generate-report/{id}
│   │   │       └── history.py                # GET /scan-history
│   │   └── utils/
│   │       └── hashing.py                   # SHA-1 k-anonymity email hashing
│   ├── scripts/                             # CLI utilities
│   │   ├── generate_breach_db.py            # Build offline breach SQLite DB
│   │   └── train_model.py                   # Standalone model trainer
│   ├── tests/                               # Backend unit tests
│   ├── data/                                # Datasets (breach CSV, etc.)
│   └── models/                              # Trained ML artefacts (.pkl)
├── frontend/
│   ├── index.html                           # Main SPA page
│   ├── app.js                               # Application logic (~755 lines)
│   ├── style-cyberpunk.css                  # Cyberpunk neon theme (1500+ lines)
│   ├── server.py                            # Python HTTP server
│   └── components/
│       └── ScanProgress.js                  # Real-time progress tracker
├── tests/                                   # Integration / E2E test scripts (.ps1)
├── requirements.txt                         # Python dependencies
├── .gitignore
├── README.md                                # This file
├── FYP_REPORT.md                            # Academic report
├── TECHNICAL_DOCS.md                        # Technical documentation
└── CHANGELOG.md                             # Version history & bug fixes
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/check-email` | Email breach detection |
| POST | `/check-url` | ML phishing URL classification |
| POST | `/check-password` | Password strength analysis |
| POST | `/generate-password` | Secure password generation |
| POST | `/scan-website` | Website security assessment |
| GET | `/generate-report/{scan_id}` | HTML security report |
| GET | `/scan-history` | Email / URL scan history |
| GET | `/website-scan-history` | Website scan history |
| GET | `/scan-details/{scan_id}` | Full website scan results |
| GET | `/scan-progress/{scan_id}` | Real-time scan progress |
| POST | `/scan-progress/{scan_id}/cancel` | Cancel running scan |
| GET | `/` | Health check |

---

## Retrain ML Model

```powershell
cd backend
python -m app.infrastructure.ml.trainer
python -m app.infrastructure.ml.evaluator
```

---

## Browser Compatibility

Chrome 90+ | Firefox 88+ | Safari 14+ | Edge 90+

---

## License

MIT License — Academic Research Project  
**Academic Year**: 2025–2026

> **Important**: The website scanner is passive-only. Always obtain permission before scanning websites you don't own. See [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md) for ethical guidelines.
