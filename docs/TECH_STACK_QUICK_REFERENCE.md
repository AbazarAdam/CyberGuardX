# ⚡ CyberGuardX — Tech Stack Quick Reference

**Created:** February 10, 2026  
**For:** Rapid decision-making and prioritization

---

## 🚦 Technology Health Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                   COMPONENT SCORECARD                        │
├──────────────────────┬──────────┬──────────┬────────────────┤
│ Component            │  Grade   │ Priority │ Action         │
├──────────────────────┼──────────┼──────────┼────────────────┤
│ FastAPI + Uvicorn    │    A+    │   LOW    │ ✅ KEEP        │
│ PostgreSQL (needed)  │    F     │ CRITICAL │ 🔴 MIGRATE NOW │
│ SQLite (current)     │    C+    │ CRITICAL │ ⚠️  REPLACE    │
│ Vanilla JavaScript   │    B-    │   HIGH   │ 🟠 UPGRADE     │
│ Logistic Regression  │    C+    │   HIGH   │ 🟠 IMPROVE     │
│ scikit-learn         │    B+    │   LOW    │ ✅ KEEP        │
│ Docker + Compose     │    A     │   LOW    │ ✅ KEEP        │
│ Nginx                │    A+    │   LOW    │ ✅ KEEP        │
│ GitHub Actions       │    A     │   LOW    │ ✅ KEEP        │
│ Redis (needed)       │    F     │   HIGH   │ 🟠 ADD         │
│ Monitoring (needed)  │    F     │  MEDIUM  │ 🟡 ADD         │
│ Tests (needed)       │    F     │  MEDIUM  │ 🟡 ADD         │
└──────────────────────┴──────────┴──────────┴────────────────┘

Overall System Grade: B+ (73/100)
Production Readiness: 68% → Target: 92%
```

---

## 🎯 Critical Path (Must Do Before Production)

### 1. 🔴 Database Migration: SQLite → PostgreSQL

**Problem:** 
- SQLite locks entire database on writes
- Cannot scale beyond ~100 concurrent users
- Single point of failure

**Solution:**
```bash
# Add to requirements.txt
psycopg2-binary>=2.9.9

# Update config.py (change 1 line!)
DATABASE_URL = "postgresql://user:pass@postgres:5432/cyberguardx"

# Add to docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: cyberguardx
      POSTGRES_USER: cyberguard
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
```

**Effort:** 1 day  
**Impact:** 🚀🚀🚀🚀🚀 Unlocks 10,000+ user capacity  
**When:** BEFORE public launch

---

### 2. 🟠 Add Redis for Caching & Rate Limiting

**Problem:**
- Cache lost on restart (in-memory only)
- Rate limiting doesn't work across multiple instances

**Solution:**
```bash
# Add to requirements.txt
redis>=5.0.0
fastapi-limiter>=0.1.5

# Update docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
```

```python
# In main.py
from redis import Redis
from fastapi_limiter import FastAPILimiter

redis = Redis(host="redis", port=6379, decode_responses=True)
await FastAPILimiter.init(redis)
```

**Effort:** 1 day  
**Impact:** 🚀🚀🚀🚀 Distributed state, better performance  
**When:** Week 1 post-launch

---

## 🔧 High Priority Upgrades

### 3. 🟠 Frontend: Vanilla JS → React + TypeScript

**Current Problems:**
- 755-line monolithic JavaScript file
- No component reusability
- No type safety → runtime errors
- Cannot unit test
- Hard to maintain

**Migration Path:**
```bash
# Create new React app with TypeScript
npm create vite@latest frontend-v2 -- --template react-ts

# Install essential tools
cd frontend-v2
npm install axios zustand react-router-dom @tanstack/react-query
npm install -D vitest @testing-library/react playwright
```

**Component Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── EmailChecker/     (replaces lines 101-234)
│   │   ├── URLScanner/        (replaces lines 235-367)
│   │   ├── WebsiteScanner/    (replaces lines 368-501)
│   │   └── PasswordAnalyzer/  (replaces lines 502-635)
│   ├── hooks/
│   │   ├── useEmailCheck.ts
│   │   └── useWebsiteScan.ts
│   └── App.tsx
```

**Benefits:**
✅ Reusable components  
✅ TypeScript catches errors at compile-time  
✅ Unit + E2E tests  
✅ Better developer experience  
✅ Industry standard (React = 40% of all web apps)

**Effort:** 2 weeks  
**Impact:** 🚀🚀🚀🚀 Maintainability for future growth  
**When:** Month 1 post-launch

---

### 4. 🟠 ML Model: Logistic Regression → XGBoost

**Current Accuracy:** 85% (15% false positives = bad UX)  
**Target Accuracy:** 92-95%

**Why XGBoost?**
- ✅ **Non-linear patterns:** Logistic Regression is too simple
- ✅ **Better accuracy:** 92-95% on phishing benchmarks
- ✅ **Interpretable:** Can explain why URL is phishing
- ✅ **Fast:** <5ms inference time
- ✅ **Small model:** <10MB (vs 50KB current, but acceptable)

**Feature Expansion:**
```python
# Current: 10 features (too few!)
current_features = [
    'url_length', 'num_dots', 'num_hyphens', 'num_underscores',
    'num_slashes', 'num_digits', 'has_ip_address', 
    'has_suspicious_tld', 'entropy', 'num_special_chars'
]

# Target: 50+ features
new_features = [
    # Domain reputation (10)
    'domain_age_days', 'ssl_cert_valid', 'whois_privacy_enabled',
    'dns_mx_records_count', 'ssl_issuer_reputation',
    
    # Content features (10)
    'page_title_brand_similarity', 'form_count', 'password_input_count',
    'external_links_ratio', 'iframe_count',
    
    # Network features (10)
    'ip_geolocation_suspicious', 'asn_reputation_score',
    'reverse_dns_matches', 'cdn_detected', 'hosting_provider_reputation',
    
    # Behavioral (10)
    'domain_typosquatting_score', 'punycode_detected',
    'redirect_count', 'page_load_time', 'javascript_obfuscation'
]
```

**Implementation:**
```python
# requirements.txt
xgboost>=2.0.0

# trainer.py
import xgboost as xgb

model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    objective='binary:logistic'
)

model.fit(X_train, y_train)
```

**Effort:** 1 week  
**Impact:** 🚀🚀🚀🚀🚀 Core product quality  
**When:** Month 1 post-launch

---

## 🟡 Medium Priority Enhancements

### 5. Monitoring Stack: Prometheus + Grafana

**What's Missing:**
- No visibility into API performance
- Cannot see error rates in real-time
- No alerting on issues

**Add:**
```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports: ["9090:9090"]
  
  grafana:
    image: grafana/grafana:latest
    ports: ["3001:3000"]
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
```

```python
# main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

**Dashboards:**
- API response times (p50, p95, p99)
- Error rates by endpoint
- Database query performance
- ML model inference latency

**Effort:** 2 days  
**Impact:** 🚀🚀🚀 Production debugging  
**When:** Month 2

---

### 6. Authentication: JWT + API Keys

**Current:** No auth, rate limiting by IP only

**Add:**
```python
# requirements.txt
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# routes/scanner.py
from fastapi import Depends
from app.auth import get_current_user

@app.post("/api/scan")
async def scan_website(
    payload: ScanRequest,
    user: User = Depends(get_current_user)  # Requires valid JWT
):
    # Now rate limit per user, not per IP
    ...
```

**Benefits:**
- ✅ Rate limit per user (not per IP)
- ✅ Track API usage per customer
- ✅ Monetization-ready (API keys for premium tier)

**Effort:** 3 days  
**Impact:** 🚀🚀🚀 Enable user accounts  
**When:** Month 2

---

### 7. Testing Suite (80%+ Coverage)

**Current:** Manual testing only (high risk!)

**Add:**
```bash
# requirements-dev.txt
pytest>=8.0.0
pytest-cov>=4.1.0
pytest-asyncio>=0.23.0
httpx>=0.26.0

# Frontend
npm install -D vitest @testing-library/react playwright
```

**Test Structure:**
```
backend/tests/
├── unit/
│   ├── test_breach_checker.py
│   ├── test_ml_evaluator.py
│   ├── test_risk_scorer.py
│   └── test_validators.py
├── integration/
│   ├── test_email_api.py
│   ├── test_url_api.py
│   └── test_scanner_api.py
└── e2e/
    └── test_full_scan_flow.py

frontend/tests/
├── unit/
│   ├── EmailChecker.test.tsx
│   └── URLScanner.test.tsx
└── e2e/
    └── scan-flow.spec.ts (Playwright)
```

**Run:**
```bash
# Backend
pytest --cov=app --cov-report=html
# Target: 80%+ coverage

# Frontend
npm run test:unit
npm run test:e2e
```

**Effort:** 1 week  
**Impact:** 🚀🚀🚀🚀 Confidence in changes  
**When:** Month 2

---

## 📊 Scalability Limits

### Current System (SQLite + Single Instance)

```
┌──────────────────────────────────────────────────────┐
│  CURRENT CAPACITY (v2.0.0)                           │
├──────────────────────────────────────────────────────┤
│  Max Concurrent Users:     ~100                      │
│  Max Requests/Second:      ~500                      │
│  Database Growth:          Limited to ~100MB         │
│  Availability:             99% (single server)       │
│  Geographic Distribution:  Single region only        │
│                                                       │
│  🚨 BOTTLENECK: SQLite write locks                   │
└──────────────────────────────────────────────────────┘
```

### After PostgreSQL + Redis (Phase 1)

```
┌──────────────────────────────────────────────────────┐
│  UPGRADED CAPACITY (Phase 1 Complete)                │
├──────────────────────────────────────────────────────┤
│  Max Concurrent Users:     ~10,000                   │
│  Max Requests/Second:      ~5,000                    │
│  Database Growth:          Scales to 1TB+            │
│  Availability:             99.9% (primary + replica) │
│  Geographic Distribution:  Single region             │
│                                                       │
│  💰 COST: ~$50/month (DigitalOcean/Linode)           │
└──────────────────────────────────────────────────────┘
```

### Kubernetes Deployment (Phase 4)

```
┌──────────────────────────────────────────────────────┐
│  ENTERPRISE CAPACITY (Kubernetes + Cloud)            │
├──────────────────────────────────────────────────────┤
│  Max Concurrent Users:     100,000+                  │
│  Max Requests/Second:      50,000+                   │
│  Database Growth:          Petabyte-scale            │
│  Availability:             99.99% (multi-region)     │
│  Geographic Distribution:  Global (CDN + edge)       │
│                                                       │
│  💰 COST: ~$450/month (AWS/GCP)                      │
└──────────────────────────────────────────────────────┘
```

---

## ⏱️ Implementation Timeline

```
Week 1-2: Production Readiness
├── Day 1-2:   PostgreSQL migration
├── Day 3:     Redis setup
├── Day 4-5:   Rate limiting with Redis
├── Day 6-7:   Monitoring (Prometheus)
└── Day 8-10:  Load testing & optimization
                ✅ Can handle 10,000 users

Week 3-4: ML Enhancement
├── Day 1-3:   Expand features (10 → 50)
├── Day 4-5:   Larger training dataset
├── Day 6-8:   Train XGBoost model
└── Day 9-10:  A/B test & deploy
                ✅ 92-95% accuracy

Week 5-6: Frontend Modernization
├── Day 1-2:   React + TypeScript setup
├── Day 3-7:   Component migration
├── Day 8-9:   State management
└── Day 10:    Deploy & validate
                ✅ Maintainable codebase

Month 2-3: Hardening
├── Authentication (JWT)
├── Comprehensive test suite
├── Security audit (OWASP)
├── Kubernetes deployment
└── Multi-region setup
                ✅ Enterprise-ready
```

---

## 🎓 Industry Standards Checklist

```
✅ = Meets standard
⚠️  = Partial/needs improvement
❌ = Missing/inadequate

Backend:
  ✅ Async API framework (FastAPI)
  ✅ Type validation (Pydantic v2)
  ✅ Auto-generated docs (OpenAPI)
  ❌ Scalable database (SQLite → PostgreSQL needed)
  ❌ Distributed cache (Need Redis)
  ⚠️  Rate limiting (Per-IP only, need per-user)
  ❌ Authentication (No JWT)
  ❌ Monitoring (No Prometheus/Grafana)

Frontend:
  ⚠️  Modern framework (Vanilla JS → React needed)
  ❌ Type safety (Need TypeScript)
  ❌ State management (Need Zustand/Redux)
  ❌ Unit tests (Need Vitest/Jest)
  ❌ E2E tests (Need Playwright)
  ✅ Responsive design
  ✅ Accessibility basics

ML/AI:
  ✅ Standard library (scikit-learn)
  ⚠️  Model complexity (Logistic Regression → XGBoost)
  ⚠️  Feature engineering (10 features → 50+ needed)
  ❌ Model versioning (Need MLflow)
  ❌ A/B testing framework
  ✅ Offline evaluation

Infrastructure:
  ✅ Containerization (Docker)
  ✅ Orchestration (Docker Compose)
  ⚠️  Production orchestration (Need Kubernetes)
  ✅ CI/CD (GitHub Actions)
  ✅ Web server (Nginx)
  ❌ Auto-scaling
  ❌ Multi-region deployment

DevOps:
  ✅ Version control (Git)
  ✅ Code linting (flake8, black)
  ✅ Security scanning (Bandit)
  ⚠️  Test coverage (0% → need 80%)
  ❌ Performance testing (Need Locust)
  ❌ Chaos engineering

──────────────────────────────────────
OVERALL ALIGNMENT: 68% → Target: 92%
──────────────────────────────────────
```

---

## 💡 Quick Decision Matrix

**When to prioritize what:**

### Immediate (This Week)
```
IF deploying to production WITHIN 1 MONTH:
  → MUST migrate to PostgreSQL
  → MUST add Redis
  → MUST add basic monitoring
ELSE:
  → Document tech debt
  → Focus on feature completion
```

### High Priority (Month 1)
```
IF expecting >1,000 users:
  → Migrate frontend to React + TypeScript
  → Upgrade ML model to XGBoost
  → Add authentication

IF expecting <1,000 users:
  → Keep vanilla JS (document refactor plan)
  → Keep Logistic Regression (add feature expansion to roadmap)
```

### Medium Priority (Month 2-3)
```
IF building commercial product:
  → Add comprehensive tests (80%+ coverage)
  → Implement monitoring + alerting
  → Security audit (penetration testing)

IF academic/demo only:
  → Document limitations clearly
  → Focus on functionality over infrastructure
```

---

## 📞 Emergency Triage Guide

**If you're experiencing:**

### 🔥 Database locks / "database is locked" errors
```
ROOT CAUSE: SQLite cannot handle concurrent writes
IMMEDIATE FIX: Reduce concurrent requests (rate limiting)
PERMANENT FIX: Migrate to PostgreSQL (1 day effort)
PRIORITY: 🔴 CRITICAL
```

### 🔥 High memory usage / OOM crashes
```
ROOT CAUSE: In-memory cache growing unbounded
IMMEDIATE FIX: Restart application, reduce cache size
PERMANENT FIX: Add Redis for distributed caching
PRIORITY: 🔴 CRITICAL
```

### ⚠️ Slow inference times (>100ms per prediction)
```
ROOT CAUSE: ML model not optimized / feature extraction slow
IMMEDIATE FIX: Add caching for repeated URLs
PERMANENT FIX: Profile code, optimize feature extraction
PRIORITY: 🟠 HIGH
```

### ⚠️ High false positive rate (>10%)
```
ROOT CAUSE: Logistic Regression too simple
IMMEDIATE FIX: Adjust classification threshold
PERMANENT FIX: Upgrade to XGBoost with more features
PRIORITY: 🟠 HIGH
```

### 🟡 Frontend becoming hard to maintain
```
ROOT CAUSE: 755-line monolithic JavaScript
IMMEDIATE FIX: Refactor into modules (ESM)
PERMANENT FIX: Migrate to React + TypeScript
PRIORITY: 🟡 MEDIUM
```

---

## 📚 One-Liner Summary of Each Technology

| Tech | Verdict | Reason |
|------|---------|--------|
| **FastAPI** | ✅ Perfect | Modern, fast, async, auto-docs |
| **SQLite** | ⚠️ Replace | Cannot scale beyond 100 users |
| **PostgreSQL** | ⭐ Needed | Industry standard, scales to millions |
| **Vanilla JS** | ⚠️ Upgrade | Maintainability issues at 755+ lines |
| **React** | ⭐ Recommended | Component reuse, testing, industry standard |
| **Logistic Regression** | ⚠️ Improve | Too simple for production (85% accuracy) |
| **XGBoost** | ⭐ Recommended | Better accuracy (92-95%), still fast |
| **Docker** | ✅ Perfect | Standard containerization |
| **Nginx** | ✅ Perfect | Best web server for static files |
| **Redis** | ⭐ Needed | Distributed cache & rate limiting |
| **Kubernetes** | 🟡 Future | For 100k+ users, overkill for now |

---

## 🎯 Final Recommendations Priority Order

```
1. 🔴 PostgreSQL migration      [1 day]   → Unlocks scaling
2. 🔴 Redis setup                [1 day]   → Enables distribution
3. 🟠 XGBoost + features         [1 week]  → Better accuracy
4. 🟠 React + TypeScript         [2 weeks] → Maintainability
5. 🟡 Monitoring stack           [2 days]  → Production visibility
6. 🟡 Authentication             [3 days]  → User management
7. 🟡 Test suite (80%+ coverage) [1 week]  → Code confidence
```

**Total Effort:** ~6 weeks for full production readiness

---

**Last Updated:** February 10, 2026  
**Document:** Quick Reference v1.0  
**See Also:** [TECH_STACK_EVALUATION.md](TECH_STACK_EVALUATION.md) for deep-dive analysis
