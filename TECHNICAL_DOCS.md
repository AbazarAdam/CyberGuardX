# CyberGuardX – Technical Documentation

## Table of Contents
1. [System Architecture](#1-system-architecture)
2. [Security Scanner Methodology](#2-security-scanner-methodology)
3. [Vulnerability Engine](#3-vulnerability-engine)
4. [Password Analyzer](#4-password-analyzer)
5. [Report Generation](#5-report-generation)
6. [ML Phishing Detection](#6-ml-phishing-detection)
7. [Breach Detection System](#7-breach-detection-system)
8. [Database Schema](#8-database-schema)
9. [Frontend Architecture](#9-frontend-architecture)
10. [Ethical & Legal Guidelines](#10-ethical--legal-guidelines)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. System Architecture

```
┌──────────────────────────────────────────────────────┐
│               Frontend (Port 3000)                   │
│  index.html + app.js + style-cyberpunk.css           │
│  [Email] [URL] [Password] [Scanner] [History]        │
└────────────────────┬─────────────────────────────────┘
                     │ HTTP REST / JSON / CORS
                     ▼
┌──────────────────────────────────────────────────────┐
│               Backend (FastAPI, Port 8000)            │
│                                                      │
│  API Layer:                                          │
│    email_checker → breach_checker service             │
│    url_checker → ML model (LogReg, 10 features)      │
│    password_checker → password_analyzer engine        │
│    website_scanner → scanner pipeline below           │
│                                                      │
│  Scanner Pipeline:                                   │
│    SafetyValidator → rate limit + legal check         │
│    ├─ HTTPSecurityScanner (15 headers)               │
│    ├─ SSLTLSScanner (cert + TLS + cipher)            │
│    ├─ DNSSecurityScanner (SPF/DMARC/DNSSEC)          │
│    ├─ TechnologyDetector (server/framework)           │
│    ├─ AdvancedVulnerabilityEngine (18 vulns)          │
│    ├─ RiskScorer (weighted 0-100)                    │
│    └─ OWASPAssessor (Top 10 mapping)                 │
│                                                      │
│  Services:                                           │
│    PDFReportGenerator → HTML security reports         │
│    ProgressTracker → real-time scan progress          │
│    BreachChecker → offline SQLite lookup              │
└────────────────────┬─────────────────────────────────┘
                     ▼
┌──────────────────────────────────────────────────────┐
│                   Data Layer                          │
│  SQLite (cyberguardx.db) + SQLAlchemy ORM            │
│    - ScanHistory (email/url scans)                   │
│    - WebsiteScan (website assessments)               │
│    - ScanProgress (real-time progress)               │
│  ML Artifacts: phishing_model.pkl + metadata.json    │
│  Breach DB: breach_emails_enhanced.csv (100K+)       │
└──────────────────────────────────────────────────────┘
```

### Technology Stack Justification

| Component | Choice | Reason |
|-----------|--------|--------|
| FastAPI | Backend framework | Async support, auto-docs, Pydantic validation, high performance |
| SQLite + SQLAlchemy | Database | Lightweight, zero-config, ORM for clean schema management |
| scikit-learn | ML | Standard library for LogReg, simple API, small model size (~2KB) |
| Vanilla JS | Frontend | No build step, fast load, direct DOM manipulation |
| dnspython | DNS queries | De-facto Python DNS library |
| cryptography | SSL/TLS | Secure certificate and cipher handling |

---

## 2. Security Scanner Methodology

All scanning is **passive-only** — no payloads, no port scanning, no exploitation.

### 2.1 HTTP Header Scanner (`http_scanner.py`)
- Checks **15 critical security headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, X-XSS-Protection, X-Permitted-Cross-Domain-Policies, Cross-Origin-Embedder-Policy, Cross-Origin-Opener-Policy, Cross-Origin-Resource-Policy, Cache-Control, Pragma, Expect-CT, Feature-Policy
- Grades each header A–F based on presence and configuration quality
- Risk points: CRITICAL=15, HIGH=10, MEDIUM=5, LOW=2
- Method: Single GET request, header-only analysis

### 2.2 SSL/TLS Scanner (`ssl_scanner.py`)
- Certificate validity (expiry, trusted CA, chain validation)
- TLS version detection (requires 1.2+; flags 1.0/1.1 as weak)
- Cipher suite strength assessment
- HSTS preload status check
- Grade: A≥95, B≥85, C≥70, D≥50, F<50
- Method: TLS handshake only

### 2.3 DNS Security Scanner (`dns_scanner.py`)
- SPF record verification (email spoofing prevention)
- DMARC policy detection (email authentication)
- MX record analysis, CAA records
- DNSSEC implementation status
- Grade: A≥90, B≥80, C≥70, D≥60, F<60
- Method: Standard DNS queries (public information)

### 2.4 Technology Detector (`tech_detector.py`)
- 11 header-based signatures (Apache, Nginx, IIS, Express, etc.)
- 8 HTML-based signatures (React, Angular, Vue, WordPress, etc.)
- Version extraction from headers only
- Method: Response header + HTML metadata analysis (no active probing)

### 2.5 Risk Scoring Engine (`risk_scorer.py`)
- Weighted formula: HTTP 30% + SSL 35% + DNS 15% + Tech 20%
- Grade thresholds: A+ (0-5), A (6-15), B (16-30), C (31-50), D (51-65), F (66-100)
- Risk levels: MINIMAL, LOW, MEDIUM, HIGH, CRITICAL
- Generates risk breakdown, top risks, security summary

### 2.6 OWASP Assessor (`owasp_assessor.py`)
Maps findings to OWASP Top 10 2021:
- A01: Broken Access Control → CORS analysis
- A02: Cryptographic Failures → TLS/HSTS check
- A03: Injection → CSP directives
- A05: Security Misconfiguration → Header assessment
- A07: Authentication Failures → Secure cookies
- Generates compliance score and "how to fix" guidance

---

## 3. Vulnerability Engine

`vulnerability_engine.py` provides deep analysis beyond basic header checks.

### 18 Vulnerability Definitions
Each vulnerability includes: CWE ID, CVSS score, severity, OWASP mapping, simple explanation, technical detail, real-world example, fix instructions (Nginx/Apache/Node.js/IIS), priority timeframe, compliance references.

| ID | Vulnerability | Severity | CVSS | CWE |
|----|--------------|----------|------|-----|
| MISSING_CSP | No Content Security Policy | HIGH | 7.1 | CWE-693 |
| MISSING_HSTS | No Strict Transport Security | HIGH | 7.4 | CWE-319 |
| MISSING_X_FRAME_OPTIONS | Clickjacking possible | MEDIUM | 6.1 | CWE-1021 |
| MISSING_X_CONTENT_TYPE | MIME sniffing risk | MEDIUM | 5.3 | CWE-16 |
| MISSING_REFERRER_POLICY | URL leakage | LOW | 3.1 | CWE-200 |
| MISSING_PERMISSIONS_POLICY | Browser feature abuse | MEDIUM | 4.3 | CWE-16 |
| WEAK_CSP | Ineffective CSP | HIGH | 6.5 | CWE-693 |
| CORS_MISCONFIGURATION | Cross-origin data theft | HIGH | 8.1 | CWE-942 |
| NO_HTTPS | Unencrypted traffic | CRITICAL | 9.1 | CWE-319 |
| EXPIRED_CERTIFICATE | Trust failure | CRITICAL | 9.1 | CWE-295 |
| WEAK_TLS_VERSION | Deprecated protocol | HIGH | 7.5 | CWE-326 |
| WEAK_CIPHER_SUITE | Breakable encryption | HIGH | 7.4 | CWE-327 |
| CERTIFICATE_EXPIRING_SOON | Upcoming trust loss | MEDIUM | 4.0 | CWE-298 |
| MISSING_SPF | Email spoofing possible | MEDIUM | 5.0 | CWE-290 |
| MISSING_DMARC | Email auth missing | MEDIUM | 5.0 | CWE-290 |
| MISSING_DNSSEC | DNS tampering risk | MEDIUM | 5.9 | CWE-350 |
| SERVER_VERSION_DISCLOSURE | Information leakage | LOW | 3.7 | CWE-200 |
| WAF_NOT_DETECTED | No web app firewall | LOW | 3.0 | CWE-693 |

### WAF Detection
Detects 8 WAF signatures: Cloudflare, AWS WAF, Akamai, Imperva, Sucuri, F5 BIG-IP, Barracuda, ModSecurity

### Compliance Frameworks
Maps findings to: PCI-DSS, GDPR, HIPAA, SOC 2, NIST, OWASP ASVS

### Security Scorecard
5 categories scored independently: Transport Security, Header Security, DNS & Email Security, Server Hardening, WAF Protection

### Risk Prioritization
Groups vulnerabilities by urgency: Immediate → 24 Hours → 7 Days → 30 Days → Consider

---

## 4. Password Analyzer

`password_analyzer.py` provides comprehensive password assessment.

### Analysis Components
- **Entropy calculation**: $H = L \times \log_2(C)$ where L=length, C=charset size
- **Pattern detection**: Keyboard walks (qwerty, asdf), alphabetic/numeric sequences, leet speak (15 substitutions), repeated characters, common words (35), common passwords (50)
- **Score formula**: Length (max 30) + Diversity (max 25) + Uniqueness (max 15) + Entropy (max 20) − Pattern penalties (8 each)
- **Strength labels**: EXCELLENT ≥90, STRONG ≥75, MODERATE ≥55, WEAK ≥30, VERY WEAK <30
- **Crack time estimates**: Online attack (10/s), Offline bcrypt (10K/s), Offline MD5 (10B/s), GPU cluster (1T/s)
- **Breach check**: SHA-1 k-anonymity lookup against local breach database

### Password Generator
- **Random mode**: Configurable length (8-128), required character types, cryptographic shuffle
- **Memorable mode**: Passphrase from 50-word list, random separator, capitalization, number suffix

### API Endpoints
```
POST /check-password     { "password": "MyP@ss123" }
POST /generate-password  { "length": 20, "mode": "random" | "memorable" }
```

---

## 5. Report Generation

`pdf_generator.py` creates self-contained HTML security reports.

### Report Sections
1. **Header** — Target URL, scan timestamp, report ID
2. **Grade Circle** — Overall grade with color-coded border + key metrics
3. **Executive Summary** — Severity count boxes (Critical/High/Medium/Low)
4. **Security Scorecard** — Category grid with individual grades
5. **Risk Prioritization** — Timeline brackets (Immediate → 30 Days)
6. **Detailed Vulnerabilities** — Cards with severity badges, CWE/CVSS, explanation, real-world examples, fix code blocks per platform (Nginx/Apache/Node.js/IIS)
7. **Compliance Summary** — Framework grid (PCI-DSS, GDPR, HIPAA, SOC 2, NIST, OWASP ASVS)
8. **Footer** — Disclaimer, tool version

### Access
```
GET /generate-report/{scan_id}   → Returns full HTML page (open in new tab, print to PDF)
```

---

## 6. ML Phishing Detection

### Model: Logistic Regression
- **Features**: 10 lexical URL features (url_length, num_dots, num_hyphens, num_digits, has_at, has_https, num_subdomains, path_length, has_ip_address, num_special_chars)
- **Performance**: 98–100% accuracy, <5ms inference, ~2KB model size
- **Explainability**: Feature importance analysis showing each feature's impact percentage and risk rating
- **Training**: 80/20 stratified split, max_iter=1000, random_state=42

### Feature Explanations
| Feature | Phishing Signal |
|---------|----------------|
| url_length | Phishing URLs tend to be longer (obfuscation) |
| num_dots | Multiple dots = subdomain spoofing |
| num_hyphens | Excessive hyphens = brand impersonation |
| has_at | @ symbol overrides apparent domain |
| has_ip_address | IP-based URLs bypass domain trust |
| num_special_chars | More special chars = more suspicious |

---

## 7. Breach Detection System

### Architecture (v2.0 — Offline-First)
- **100,000+ breach records** in enhanced CSV (replaced v1.0's HIBP API dependency)
- **15 real-world breaches**: Adobe (153M), LinkedIn (165M), Yahoo (3B), Equifax (147M), Marriott (500M), MyFitnessPal (150M), Capital One (106M), and more
- **Risk calculation**: 40% breach count + 30% severity + 20% recency + 10% accounts affected
- **Performance**: Local lookup <50ms, LRU caching for repeat queries
- **Email patterns**: 160 first names × 144 last names × 25 domains × 8 patterns

### Data Distribution
- 20% clean (no breaches) → LOW risk
- 30% single breach → MEDIUM risk
- 25% two breaches → HIGH risk
- 15% three breaches → HIGH risk
- 10% four+ breaches → CRITICAL risk

---

## 8. Database Schema

### ScanHistory
```sql
CREATE TABLE scan_history (
    id INTEGER PRIMARY KEY,
    email VARCHAR,
    email_breached BOOLEAN,
    phishing_score FLOAT,
    risk_level VARCHAR,
    scanned_at DATETIME
);
```

### WebsiteScan
```sql
CREATE TABLE website_scans (
    id INTEGER PRIMARY KEY,
    url VARCHAR INDEXED,
    client_ip VARCHAR,
    risk_score INTEGER,
    risk_level VARCHAR,
    overall_grade VARCHAR,
    http_scan_json TEXT,
    ssl_scan_json TEXT,
    dns_scan_json TEXT,
    tech_scan_json TEXT,
    owasp_assessment_json TEXT,
    scan_duration_ms INTEGER,
    scanned_at DATETIME,
    permission_confirmed BOOLEAN,
    owner_confirmed BOOLEAN,
    legal_accepted BOOLEAN
);
```

### ScanProgress
```sql
CREATE TABLE scan_progress (
    id INTEGER PRIMARY KEY,
    scan_id VARCHAR UNIQUE,
    current_step INTEGER,
    total_steps INTEGER DEFAULT 7,
    status VARCHAR DEFAULT 'in_progress',
    steps_json TEXT,
    started_at DATETIME,
    updated_at DATETIME
);
```

---

## 9. Frontend Architecture

### Technology
- **HTML5/CSS3/ES6+ JavaScript** — No build step required
- **Cyberpunk theme**: `style-cyberpunk.css` (1500+ lines)
  - Color palette: Electric Cyan (#00f3ff), Neon Magenta (#ff00ff), Bright Green (#00ff9d), Hot Pink (#ff003c), Electric Yellow (#ffaa00)
  - Scanline overlay, glow effects, neon borders
  - Responsive grid layouts, mobile-friendly
- **Python HTTP server** on port 3000

### Key JavaScript Functions (app.js)
| Function | Purpose |
|----------|---------|
| `checkEmail()` | POST /check-email → breach timeline display |
| `checkURL()` | POST /check-url → phishing score + ML explainability |
| `checkPassword()` | POST /check-password → strength meter, crack times, patterns |
| `generatePassword(mode)` | POST /generate-password → auto-fill + analyze |
| `scanWebsite()` | POST /scan-website → full vulnerability display |
| `displayWebsiteResults(data)` | Renders grade circle, scorecard, vuln cards, compliance, priority timeline |
| `loadHistory()` | GET /scan-history → table display |

### Components
- **ScanProgress.js** — Real-time 7-step progress tracker (2-second polling)
- **WebsiteScanner.jsx** — React-based scanner with legal disclaimers (legacy, still usable)

---

## 10. Ethical & Legal Guidelines

### Safety Mechanisms
1. **Mandatory Legal Disclaimer** — Triple-checkbox confirmation required:
   - Confirm website ownership or written permission
   - Acknowledge legal implications
   - Accept full legal responsibility
2. **Rate Limiting** — 10-minute cooldown per IP address
3. **Domain Restrictions** — Blocks government (.gov, .mil), private IPs (RFC 1918)
4. **Passive-Only Design** — No payloads, no port scanning, no exploitation
5. **Audit Trail** — 100% logging (timestamp, IP, target, permissions)

### What the Scanner Does NOT Do
- ❌ Port scanning (only 80/443)
- ❌ SQL injection / XSS / command injection attempts
- ❌ Brute force / credential stuffing
- ❌ Active exploitation of any vulnerability
- ❌ Content modification or data exfiltration
- ❌ DDoS or load testing
- ❌ Cookie manipulation or session hijacking
- ❌ File upload or download attempts

### Legal Framework
- **CFAA** (US): Authorized passive observation only
- **Computer Misuse Act** (UK): No unauthorized access
- **EU Cybersecurity Directive**: Lawful assessment with permission
- Users accept full legal responsibility via mandatory disclaimer

### Authorized Use Cases
- ✅ Scanning websites you own
- ✅ Testing with signed permission
- ✅ Educational/academic research on approved platforms
- ✅ Bug bounty programs (within scope)

---

## 11. Troubleshooting

### Backend Won't Start
```powershell
# Check dependencies
pip install fastapi uvicorn sqlalchemy dnspython cryptography scikit-learn requests

# Check port availability
netstat -ano | findstr :8000

# Start with verbose logging
uvicorn app.main:app --reload --port 8000 --log-level debug
```

### Frontend Not Loading
```powershell
# Verify backend is running
Invoke-RestMethod -Uri "http://localhost:8000/"

# Clear browser cache (Ctrl+Shift+Delete)
# Hard refresh: Ctrl+Shift+R
```

### Model Not Found
```powershell
cd backend
python -m app.ml.train_phishing_model
# Creates: models/phishing_model.pkl + phishing_model_metadata.json
```

### Database Issues
```powershell
# Reset database (delete and restart)
Remove-Item backend/cyberguardx.db
# Backend auto-creates tables on next startup
```

### CORS Errors
- Ensure frontend runs on `http://localhost:3000`
- Backend CORS is configured for localhost:3000 in `main.py`

### Website Scan Fails
- Verify target URL starts with `http://` or `https://`
- Check all 3 legal disclaimer boxes
- Wait 10 minutes between scans of the same target (rate limit)
- Target must be accessible (not behind firewall/VPN)

### Common Python Errors
| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: dnspython` | `pip install dnspython` |
| `ModuleNotFoundError: cryptography` | `pip install cryptography` |
| `FileNotFoundError: phishing_model.pkl` | Run `python -m app.ml.train_phishing_model` |
| `sqlalchemy.exc.OperationalError` | Delete `cyberguardx.db`, restart backend |
| `ConnectionRefusedError` | Start backend first: `uvicorn app.main:app --reload` |
