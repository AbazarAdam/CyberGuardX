# CyberGuardX – Changelog & Version History

All notable changes, enhancements, bug fixes, and test results.

---

## v5.0 – Clean Architecture Refactoring (Feb 2026)

### Architecture Migration
Migrated from flat directory structure (`api/`, `db/`, `security/`, `services/`, `ml/`) to **Clean Architecture** with four distinct layers:

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| **Domain** | `app/domain/` | Pure business logic — zero external dependencies |
| **Application** | `app/application/services/` | Use-case orchestration — breach checking, progress tracking, report generation |
| **Infrastructure** | `app/infrastructure/` | External concerns — database, ML models, security scanners, external APIs |
| **Presentation** | `app/presentation/` | HTTP layer — FastAPI routes, Pydantic schemas, shared dependencies |

### New Files Created
- `app/config.py` — Centralised configuration (paths, CORS, rate limits)
- `app/domain/enums.py` — `RiskLevel`, `Grade`, `Severity`, `SecurityPosture` enums
- `app/domain/risk_engine.py` — Pure `calculate_risk_level()` function (added CRITICAL threshold ≥0.85)
- `app/infrastructure/database/connection.py` — SQLAlchemy engine & `SessionLocal`
- `app/infrastructure/database/models.py` — All 3 ORM models with full docstrings
- `app/infrastructure/external/breach_data.py` — Single source of truth for 15 breach definitions
- `app/application/services/breach_checker.py` — Fully rewritten with LRU cache & clear docstrings
- `app/application/services/progress_tracker.py` — Rewritten with 7-step state machine
- `app/presentation/schemas.py` — All Pydantic models with section headers
- `app/presentation/dependencies.py` — Shared `get_db()` (consolidated from 4 duplicates)
- `app/presentation/routes/` — 5 route modules: `email.py`, `url.py`, `password.py`, `scanner.py`, `history.py`
- `.gitignore` — Python, IDE, DB, ML model, OS exclusions
- `requirements.txt` — All Python dependencies

### Bug Fixes
| Bug | Severity | Fix |
|-----|----------|-----|
| `vulnerability_engine.py` reads `ssl_scan.get("cipher")` but SSL scanner stores `"cipher_suite"` — cipher analysis always skipped | **HIGH** | Changed to `ssl_scan.get("cipher_suite")` |
| `safety_validator.py` uses `any(allowed in domain ...)` — `example.com.evil.com` bypasses whitelist | **HIGH** | Changed to `domain.endswith()` check |
| `Dict[str, any]` (lowercase) across 7 security modules | **MEDIUM** | Fixed 25 occurrences → `Dict[str, Any]` |
| Duplicate `/scan-history` route in `history.py` and `website_scanner.py` | **MEDIUM** | Renamed website scanner's to `/website-scan-history` |
| `test_enhancements.ps1` tests port 5000 instead of correct 3000 | **LOW** | Fixed to `localhost:3000` |

### Cleanup
- **Removed dead frontend files**: `style.css` (1115 lines), `WebsiteScanner.jsx` (296 lines), `WebsiteScanner.css` (542 lines)
- **Removed orphaned backend root scripts** — moved to `scripts/` and `tests/`
- **Consolidated duplicated code**: 4× `get_db()` → 1, 3× `hash_email()` → 1, breach constants → single `breach_data.py`
- **Added comprehensive docstrings** and section comments throughout all new files
- **Deleted old directories**: `api/`, `core/`, `db/`, `ml/`, `security/`, `services/`

### Files Changed Summary
102 files changed, 2723 insertions, 2842 deletions

---

## v4.0 – Professional-Grade Security Enhancements (Feb 2026)

### New Features

#### Deep Vulnerability Engine (`infrastructure/security/vulnerability_engine.py`, ~810 lines)
- **18 vulnerability definitions** with full metadata: CWE ID, CVSS score, severity, OWASP mapping, exploit difficulty
- **Plain-language explanations** — each vulnerability includes "what this means" in simple terms
- **Real-world examples** — reference to actual breaches/incidents for each vulnerability
- **Platform-specific fix instructions** — code snippets for Nginx, Apache, Node.js, IIS
- **Priority timeframes** — Immediate, 24 hours, 7 days, 30 days, or consider
- **WAF detection** — 8 WAF signatures: Cloudflare, AWS WAF, Akamai, Imperva, Sucuri, F5, Barracuda, ModSecurity
- **Compliance mapping** — PCI-DSS, GDPR, HIPAA, SOC 2, NIST, OWASP ASVS
- **Security scorecard** — 5 categories scored independently (Transport, Headers, DNS, Server, WAF)

#### Password Strength Analyzer (`infrastructure/security/password_analyzer.py`, ~557 lines)
- **Pattern detection**: Keyboard walks (qwerty, etc.), alphabetic/numeric sequences, leet speak (15 substitutions), repeated characters, common words (35), common passwords (50)
- **Entropy calculation** with charset size analysis
- **Crack time estimates** for 4 attack scenarios (online, bcrypt, MD5, GPU cluster)
- **Breach database check** using SHA-1 k-anonymity
- **Score formula**: 0-100 with breakdown (length + diversity + uniqueness + entropy − penalties)
- **Password generator**: Random mode (cryptographic) and memorable passphrase mode (50-word list)

#### PDF/HTML Report Generator (`application/services/report_generator.py`, ~459 lines)
- Self-contained HTML with dark cyberpunk styling
- Sections: Grade circle, executive summary, scorecard, priority timeline, vulnerability details with fix code, compliance grid
- Print-friendly CSS with `@media print` rules
- Accessible via `GET /generate-report/{scan_id}`

#### New API Endpoints
- `POST /check-password` — Full password strength analysis
- `POST /generate-password` — Secure password generation (random or memorable)
- `GET /generate-report/{scan_id}` — HTML security report

### Modified Files
- **website_scanner.py** — Integrated vulnerability engine + report generation, fixed `tech_detector.detect()` → `tech_detector.scan()` bug
- **schemas.py** — Added `vulnerability_analysis` field to `WebsiteScanResponse`
- **main.py** — Added `password_checker` router
- **index.html** — Added Password Strength Analyzer section with generate buttons
- **app.js** — Complete rewrite (~700 lines): password analyzer UI, deep vulnerability cards (expandable), severity counters, scorecard grid, compliance display, priority timeline, PDF download button
- **style-cyberpunk.css** — Added 400+ lines for password analyzer, vulnerability cards, scorecard, compliance, priority timeline

### Test Results (v4.0)
| Test | Status | Result |
|------|--------|--------|
| Password check (`Test123!`) | PASS | WEAK, 42/100, 52.4 bits entropy |
| Password generate (random) | PASS | 20-char secure password |
| Password generate (memorable) | PASS | e.g. `nexus_prism_fortress_Quantum_battery_42` |
| Website scan (httpbin.org) | PASS | Grade C, 11 vulns, 5 severity categories |
| Vulnerability analysis | PASS | Scorecard, WAF detection, compliance mapping |

---

## v3.0 – ML Explainability & Real-Time Progress (Jan 2026)

### New Features

#### ML Explainability
- Expanded from 6 → **10 URL features** (added: num_subdomains, path_length, has_ip_address, num_special_chars)
- **Feature importance analysis** — shows each feature's impact percentage and risk rating (HIGH/MEDIUM/LOW)
- **Confidence scores** with model metadata (name, version, features, training date)
- Dual model training: backward-compatible 6-feature + enhanced 10-feature

#### Real-Time Progress Tracking
- **7-step animated progress tracker**: DNS Resolution → SSL/TLS Analysis → HTTP Headers → Technology Detection → OWASP Assessment → Risk Calculation → Report Generation
- **2-second polling** from frontend to `GET /scan-progress/{scan_id}`
- **ScanProgress DB table** for persistent state
- Progress container minimizes (doesn't disappear) after scan completion

### Files Created (v3.0)
- `backend/app/application/services/progress_tracker.py` (~222 lines)
- `backend/app/infrastructure/ml/evaluator.py` (~180 lines)
- `frontend/components/ScanProgress.js` (~200 lines)

### Files Modified
- `feature_extractor.py` — Added 4 new features + `FEATURE_EXPLANATIONS` dict
- `train_phishing_model.py` — Dual model training + metadata generation
- `url_checker.py` — Feature analysis in response
- `website_scanner.py` — Progress tracking integration
- `schemas.py` — Added feature_analysis, model_info, progress fields
- `models.py` — Added ScanProgress model

### Test Results (v3.0)
| Test | Status | Result |
|------|--------|--------|
| URL check (google.com) | PASS | Legitimate, confidence 95%+ |
| URL check (phishing URL) | PASS | Phishing detected, feature analysis shown |
| Progress tracking | PASS | 7/7 steps, 2s polling works |
| ML explainability | PASS | 10 features with impact + risk + explanation |
| Model metadata | PASS | Version, features, training date returned |

**Performance**: Progress latency ~30ms, ML inference ~3ms, feature extraction ~1ms

---

## v2.0 – Offline Breach Detection System (Jan 2026)

### Changes from v1.0
- **Removed**: HIBP API dependency, CSV file loading, Pandas requirement
- **Added**: 100,000+ record SQLite breach database (`breaches.db`, 98.6 MB)
- **15 real-world breaches**: Adobe (153M), LinkedIn (165M), Yahoo (3B), Equifax (147M), Marriott (500M), MyFitnessPal (150M), Capital One (106M), and 8 more
- **LRU caching** for repeat queries
- **Enhanced risk calculation**: 40% breach count + 30% severity + 20% recency + 10% accounts

### Files Created (v2.0)
- `backend/app/application/services/breach_checker.py` — Offline-first breach lookup
- `backend/scripts/generate_breach_db.py` — 100K record generator
- `backend/data/breach_emails_enhanced.csv` — Enhanced breach dataset

### Test Results (v2.0)
| Test | Status | Result |
|------|--------|--------|
| test@example.com | PASS | 3 breaches found, HIGH risk |
| safe@example.com | PASS | 0 breaches, LOW risk |
| Lookup performance | PASS | <50ms local, <10ms cached |

---

## v1.5 – Website Security Scanner (Dec 2025)

### New Features
- **HTTP Header Scanner** — 15 critical headers, A-F grading
- **SSL/TLS Scanner** — Certificate, TLS version, cipher analysis
- **DNS Security Scanner** — SPF, DMARC, DNSSEC checks
- **Technology Detector** — Server, framework, library fingerprinting
- **Risk Scoring Engine** — Weighted 0-100 scoring with letter grades
- **OWASP Top 10 Assessor** — Educational mapping and compliance scoring
- **Safety Validator** — Rate limiting (10 min), legal disclaimers, domain restrictions

### Files Created (11 total)
- 7 backend files: `http_scanner.py`, `ssl_scanner.py`, `dns_scanner.py`, `tech_detector.py`, `risk_scorer.py`, `owasp_assessor.py`, `safety_validator.py`
- 2 frontend files: `WebsiteScanner.jsx`, `WebsiteScanner.css`
- 2 docs (now consolidated into this file)

---

## v1.0 – Initial Release (Nov 2025)

### Core Features
- Email breach detection (HIBP API + 10,005-record CSV dataset)
- ML phishing URL classification (Logistic Regression, 6 features, 98%+ accuracy)
- Scan history with SQLite persistence
- FastAPI backend with auto-generated Swagger docs
- Vanilla JS frontend with responsive design

---

## Bug Fixes Log

### Fix #1: URL Checker 500 Error
- **Symptom**: POST `/check-url` returned HTTP 500
- **Root Cause**: Database save operation failed, blocking the entire response pipeline
- **Fix**: Wrapped DB save in try/except; URL check works even if history save fails
- **File**: `url_checker.py`

### Fix #2: History Loading Failure
- **Symptom**: GET `/scan-history` returned error or empty
- **Root Cause**: Poor error handling when DB had no records or mixed scan types
- **Fix**: Added proper exception handling and empty-state responses
- **File**: `history.py`

### Fix #3: Cyberpunk Theme Not Applied
- **Symptom**: UI showed default white/gray styles instead of cyberpunk neon
- **Root Cause**: `style-cyberpunk.css` was not linked in `index.html`
- **Fix**: Created comprehensive `style-cyberpunk.css` (1100+ lines) and linked it
- **Files**: `style-cyberpunk.css` (new), `index.html` (updated)
- **Color palette**: Electric Cyan (#00f3ff), Neon Magenta (#ff00ff), Bright Green (#00ff9d), Hot Pink (#ff003c)

### Fix #4: Progress Bar Visibility
- **Symptom**: Scan progress tracker disappeared completely after scan finished
- **Root Cause**: Progress container was hidden entirely via `display: none`
- **Fix**: Changed to minimized state (`.minimized` CSS class) with hover-to-expand
- **Files**: `ScanProgress.css`, `app.js`

### Fix #5: tech_detector.detect() Bug
- **Symptom**: Website scanner crashed calling `tech_detector.detect(url)`
- **Root Cause**: `TechnologyDetector` class method is named `scan()`, not `detect()`
- **Fix**: Changed call to `tech_detector.scan(url)`
- **File**: `website_scanner.py`

---

## Known Limitations

### ML Model
- Lexical features only (no content/DNS/WHOIS analysis)
- 1000-URL training dataset (production would need 100K+)
- Linear model can't capture complex feature interactions
- Needs periodic retraining for evolving phishing patterns

### Website Scanner
- Passive-only: cannot detect application-layer vulns (SQLi, XSS, auth bypass)
- Snapshot assessment (security posture at scan time only)
- CDN/load balancers may return different responses per geography
- Single-page analysis (no site crawling)

### Breach Detection
- Offline dataset (not real-time HIBP data)
- Simulated breach records (realistic but synthetic email addresses)

### General
- Development-only security (needs WAF, DDoS protection for production)
- No GDPR/CCPA compliance mechanisms
- SQLite not suitable for high-concurrency production use

---

## Future Roadmap

### Near-Term
- Deep learning phishing detection (LSTM, transformer)
- Cookie security analysis (HttpOnly, Secure, SameSite)
- CORS misconfiguration detection
- CSP directive-level parsing
- Browser extension for real-time protection

### Long-Term
- Cloud deployment (Azure/AWS containers)
- Enterprise multi-site management
- SIEM integration (Splunk, QRadar)
- Continuous monitoring with scheduled scans
- Mobile application (iOS/Android)
- Federated learning for privacy-preserving threat intelligence
