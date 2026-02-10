# CyberGuardX – Intelligent Web Security Assessment Platform

> Professional-grade cybersecurity tool combining email breach detection, ML-powered phishing URL classification, password strength analysis, and deep website vulnerability scanning.

---

## Quick Start

### Easiest Way (One-Click Scripts)

**Option A: Full Docker Setup** (Recommended for production-like environment)

```powershell
scripts\run_docker.bat
```

**Option B: Local Development** (Best for coding with hot-reload)

```powershell
scripts\run_full_local.bat
```

**First Time?** Run setup first:

```powershell
scripts\setup_dev_environment.bat
```

See [scripts/README.md](scripts/README.md) for all run scripts.

---

### Manual Setup

#### Docker (Recommended)

```powershell
docker-compose up
```

See [docs/DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md) for full Docker documentation.

#### Local Development

##### 1. Start Backend

```powershell
cd backend
..\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

##### 2. Start Frontend

```powershell
cd frontend
python -m http.server 3000
```

##### 3. Open Browser

```text
http://localhost:3000
```

> **API Docs**: <http://localhost:8000/docs> (Swagger) | <http://localhost:8000/redoc>

---

## Features

| Module | Description |
| --- | --- |
| **Email Breach Checker** | Checks emails against 100K+ offline breach records across 15 real-world breaches (Adobe, LinkedIn, Yahoo, etc.) |
| **URL Phishing Detector** | ML-powered (Logistic Regression, 10 features) with explainability — shows feature impacts, confidence scores |
| **Password Strength Analyzer** | Entropy calculation, pattern detection (keyboard walks, leet speak, sequences), crack time estimates, breach DB check, password generator |
| **Website Security Scanner** | Deep vulnerability analysis with 18 checks, CWE/CVSS scoring, OWASP Top 10 mapping, compliance frameworks (PCI-DSS, GDPR, HIPAA, SOC 2, NIST), WAF detection, fix instructions per platform |
| **PDF Security Report** | Professional HTML report generation with cyberpunk styling, print-to-PDF ready |
| **Scan History** | Persistent audit trail of all scans stored in PostgreSQL |
| **Real-Time Progress** | 7-step animated progress tracker with 2-second polling |

---

## Test Data

### Breach Emails

| Email                      | Breaches                      | Risk Level |
| -------------------------- | ----------------------------- | ---------- |
| `test@example.com`         | 3 (Adobe, LinkedIn, Yahoo)    | HIGH       |
| `demo@cyberguardx.com`     | 5                             | CRITICAL   |
| `user@test.com`            | 2                             | HIGH       |
| `admin@sample.com`         | 4                             | HIGH       |
| `safe@example.com`         | 0                             | LOW        |

### Phishing URLs

| URL                                                           | Expected Result          |
| ------------------------------------------------------------- | ------------------------ |
| `https://google.com`                                          | Legitimate (low score)   |
| `http://paypal-login-verify.suspicious-site.com/secure`       | Phishing (high score)    |
| `http://192.168.1.1/admin/login.php?user=admin`               | Phishing (IP-based)      |

### Website Scan Targets (Authorized)

| URL | Notes |
| --- | --- |
| `https://example.com` | Basic test target |
| `https://httpbin.org` | Returns useful security header mix |
| `http://testphp.vulnweb.com` | Intentionally vulnerable (educational) |

---

## Technology Stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Database | PostgreSQL + SQLAlchemy ORM + Alembic |
| Cache | Redis 7 (distributed caching) |
| ML | scikit-learn (Logistic Regression) |
| Frontend | Vanilla HTML/CSS/JS, Cyberpunk theme |
| Security | dnspython, cryptography, hashlib |

---

## Project Structure (Clean Architecture)

```text
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
│   │   │   │   └── models.py                # ORM models
│   │   │   ├── ml/                          # ML pipeline
│   │   │   ├── security/                    # 9 scanner modules
│   │   │   └── external/                    # HIBP client, breach data
│   │   ├── presentation/                    # HTTP layer (FastAPI routes)
│   │   └── utils/                           # Hashing, logging
│   ├── scripts/                             # CLI utilities
│   ├── tests/                               # Backend unit tests
│   ├── data/                                # Datasets (breach CSV, etc.)
│   └── models/                              # Trained ML artefacts (.pkl)
├── frontend/
│   ├── index.html                           # Main SPA page
│   ├── app.js                               # Application logic
│   ├── style-cyberpunk-modular.css          # Modular CSS entry (28 modules)
│   ├── styles/                              # Modular CSS architecture
│   │   ├── core/                            # Variables, reset, base
│   │   ├── layout/                          # Header, main, footer, responsive
│   │   ├── components/                      # 16 reusable UI modules
│   │   └── features/                        # 5 feature-specific styles
│   └── components/                          # JS components
├── scripts/                                 # Run scripts (Docker, local, etc.)
├── docs/                                    # All documentation
├── requirements.txt                         # Python dependencies
├── docker-compose.yml                       # Multi-container orchestration
├── README.md                                # This file
└── CHANGELOG.md                             # Version history
```

---

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/check-email` | Email breach detection |
| POST | `/check-url` | ML phishing URL classification |
| POST | `/check-password` | Password strength analysis |
| POST | `/generate-password` | Secure password generation |
| POST | `/scan-website` | Website security scan |
| GET | `/scan-progress/{id}` | Real-time scan progress |
| GET | `/generate-report/{id}` | HTML security report |
| GET | `/scan-history` | Scan audit trail (paginated) |
| GET | `/` | Health check |

---

## Docker Deployment

```powershell
# Quick start (one command)
scripts\run_docker.bat

# Or manual
docker-compose up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Full documentation: [docs/DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md)

---

## Architecture and Performance

- **Tech Stack Evaluation** — [docs/TECH_STACK_EVALUATION.md](docs/TECH_STACK_EVALUATION.md)
- **Quick Reference Guide** — [docs/TECH_STACK_QUICK_REFERENCE.md](docs/TECH_STACK_QUICK_REFERENCE.md)
- **Architecture Evolution** — [docs/ARCHITECTURE_EVOLUTION.md](docs/ARCHITECTURE_EVOLUTION.md)

**Completed Upgrades:**

1. PostgreSQL + Redis (10,000+ concurrent users capable)
2. Distributed caching (50-100x faster cache hits)
3. Pagination + Indexing (30-50x faster queries)
4. ML model preloading (7x faster predictions)
5. CSS modularization (2,967 lines → 28 modules)

See [docs/PERFORMANCE_OPTIMIZATIONS.md](docs/PERFORMANCE_OPTIMIZATIONS.md) for full details.

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

## Documentation

All documentation organized in [docs/README.md](docs/README.md).

**Quick links:**

- [Getting Started](docs/START_HERE.md)
- [Architecture](docs/TECHNICAL_DOCS.md)
- [Performance](docs/PERFORMANCE_OPTIMIZATIONS.md)
- [Docker Guide](docs/DOCKER_GUIDE.md)
- [Remaining Work](docs/REMAINING_WORK_DETAILED.md)
- [Academic Report](docs/FYP_REPORT.md)

---

## Development Scripts

All run scripts in [scripts/README.md](scripts/README.md).

```powershell
scripts\setup_dev_environment.bat    # First-time setup
scripts\run_docker.bat               # Full Docker
scripts\run_full_local.bat           # Local development
scripts\stop_all.bat                 # Stop everything
```

---

## License

MIT License — Academic Research Project
**Academic Year**: 2025–2026

> **Important**: The website scanner is passive-only. Always obtain permission before scanning websites you don't own. See [docs/TECHNICAL_DOCS.md](docs/TECHNICAL_DOCS.md) for ethical guidelines.
