# Security Improvement Plan

**Created:** 2024-12-24
**Status:** ✅ Done (WAF deferred)
**Ostatnia aktualizacja statusu:** 2026-07-24
**Based On:** Production Security Audit (VPS + Caddy environment)

> **Status audit (2026-07-24):** Done in code — CSP/HSTS headers, rate limiting, prod CORS forbid `*`, httpOnly refresh cookie + access in memory, general CSRF double-submit middleware.  
> **Docs (2026-07-24):** [BACKUP_RECOVERY.md](../deployment/BACKUP_RECOVERY.md), [SECRETS_ROTATION.md](../deployment/SECRETS_ROTATION.md).  
> **Monitoring:** covered outside this plan — app errors via **Sentry** (BE+FE); uptime / infra / service health via **Ops Monitor** (`../ops-monitor`, see that repo’s docs / deployment). Do not rebuild a separate SIEM here.  
> **WAF:** deferred (custom `xcaddy`+Coraza has high ops cost for Caddy upgrades; revisit only if traffic/risk justifies Cloudflare or custom build).  
> **Still open in this plan:** none of the three leftovers (backup/CSRF/secrets) — WAF remains deferred only.

---

## Executive Summary

This document outlines security improvements based on a comprehensive security audit of the Gear Stack application running on a VPS with Caddy reverse proxy. The audit revealed an overall **STRONG** security posture with excellent foundational practices, but identified key areas for enhancement.

### Overall Security Assessment

**Backend Security Posture:** ✅ STRONG
**Frontend Security Posture:** ✅ GOOD

The application demonstrates strong security fundamentals but requires implementation of additional defense-in-depth measures, particularly around HTTP security headers and infrastructure hardening.

---

## 🎯 Priority Matrix

| Priority | Backend Items | Frontend Items | Infrastructure Items |
|----------|---------------|----------------|---------------------|
| **Critical** | Security Headers (CSP, HSTS) | CSP Configuration | - |
| **High** | WAF Implementation | httpOnly Cookies Migration | Backup/Recovery Procedures |
| **Medium** | Secrets Rotation | CSRF Protection | Monitoring & Alerting |
| **Low** | Documentation Updates | Strict CORS Refinement | PostgreSQL SSL/TLS, Security Automation |

---

## 🛡️ Current Security Strengths

### Backend ✅

1. **Excellent Docker Security**
   - Multi-stage builds minimize attack surface
   - Non-root user execution in containers
   - Localhost binding prevents direct external access

2. **Strong Authentication System**
   - bcrypt password hashing (industry standard)
   - JWT token-based authentication
   - WebAuthn/passkey support (modern, phishing-resistant)

3. **Active Vulnerability Management**
   - Recent critical security fixes applied
   - Dependency updates maintained

4. **Rate Limiting & DDoS Protection**
   - Active rate limiting implemented
   - DDoS protection mechanisms in place

5. **SQL Injection Prevention**
   - Proper ORM usage (SQLAlchemy)
   - Parameterized queries throughout

6. **Environment-Aware Configuration**
   - Separate dev/prod configurations
   - Environment variable management

### Frontend ✅

1. **XSS Prevention**
   - Vue.js automatic escaping
   - Proper sanitization practices
   - Markdown sanitization implemented

2. **Modern Framework Security**
   - Vue 3.5+ with latest security patches
   - Type-safe TypeScript implementation

3. **Dependency Management**
   - Regular updates via pnpm
   - Vulnerability scanning enabled

---

## 🔧 Required Improvements

### HIGH PRIORITY

#### 1. Implement Content Security Policy (CSP) Headers

**Impact:** Critical - Prevents XSS, clickjacking, and code injection attacks
**Complexity:** Medium
**Location:** Backend middleware + Caddy configuration

**Implementation:**

```python
# backend/app/middleware/security_headers.py

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' blob: https://www.google.com https://www.gstatic.com",  # Google reCaptcha + Web Workers
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' https://*.gear-stack.ovh https://www.google.com https://*.sentry.io",  # All subdomains + Google reCaptcha + Sentry
            "worker-src 'self' blob:",  # Web Workers
            "frame-src 'self' https://www.google.com https://www.gstatic.com",  # Google reCaptcha iframe
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers['Content-Security-Policy'] = "; ".join(csp_directives)

        return response
```

**Caddy Configuration:**

```caddyfile
# Caddyfile
yourdomain.com {
    header {
        # CSP (primary - backend should also set this)
        Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' blob: https://www.google.com https://www.gstatic.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://*.gear-stack.ovh https://www.google.com https://*.sentry.io; worker-src 'self' blob:; frame-src 'self' https://www.google.com https://www.gstatic.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"

        # Report-Only mode for testing
        # Content-Security-Policy-Report-Only "default-src 'self'; report-uri /api/csp-report"
    }
}
```

**Testing:**
```bash
# Test CSP headers
curl -I https://yourdomain.com | grep -i "content-security-policy"

# Browser DevTools Console will show CSP violations
# Monitor and refine policy based on violations
```

**Checklist:**
- [ ] Create `SecurityHeadersMiddleware` in backend
- [ ] Register middleware in FastAPI app
- [ ] Configure CSP in Caddy as backup
- [ ] Test with Report-Only mode first
- [ ] Monitor browser console for violations
- [ ] Refine CSP directives based on violations
- [ ] Switch to enforcement mode
- [ ] Document CSP policy and rationale

---

#### 2. Add Missing Security Headers

**Impact:** High - Defense-in-depth against various attacks
**Complexity:** Low
**Location:** Backend middleware + Caddy configuration

**Required Headers:**

```python
# backend/app/middleware/security_headers.py

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'

        # Prevent MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Enable XSS filter (legacy browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # HSTS - Force HTTPS (only in production!)
        if settings.ENVIRONMENT == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions policy
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        return response
```

**Caddy Configuration:**

```caddyfile
yourdomain.com {
    header {
        # Security headers
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"

        # Remove server fingerprinting
        -Server
    }
}
```

**Verification:**

```bash
# Check all security headers
curl -I https://yourdomain.com

# Should show:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# Referrer-Policy: strict-origin-when-cross-origin
```

**Checklist:**
- [ ] Add all security headers to middleware
- [ ] Configure Caddy with security headers
- [ ] Test headers in production
- [ ] Verify headers with SecurityHeaders.com
- [ ] Submit domain to HSTS preload list (optional)
- [ ] Document header purposes

---

#### 3. PostgreSQL SSL/TLS (Optional - Docker Network Context)

**Impact:** Low - Docker network isolation provides sufficient protection
**Complexity:** Low
**Location:** Database configuration

**Current State:** Not Required - Docker network isolation

**Decision Rationale:**

After security analysis, **SSL/TLS for PostgreSQL is NOT required** when both application and database containers run in the same Docker bridge network. This decision is based on:

1. **Docker Network Isolation:**
   - Docker bridge networks provide network-level isolation
   - Traffic between containers is not accessible from the host or external networks
   - Containers communicate via internal Docker DNS (e.g., `db:5432`)

2. **Risk Assessment:**
   - **Low risk:** Intercepting traffic would require:
     - Root access to the Docker host, OR
     - Compromised container with network access
   - In both cases, SSL/TLS wouldn't provide meaningful protection

3. **Performance Overhead:**
   - SSL/TLS adds CPU overhead and latency
   - Self-signed certificates require certificate management
   - No security benefit in isolated Docker network context

4. **When SSL/TLS WOULD be Required:**
   - Compliance requirements (PCI-DSS, HIPAA, ISO 27001)
   - Sensitive data (financial, medical, PII) with strict compliance needs
   - Migration to Kubernetes/microservices architecture
   - Multi-host deployments where traffic crosses network boundaries

**Current Configuration:**
- ✅ Application and database in same Docker network
- ✅ Database port not exposed to host (localhost binding)
- ✅ Network isolation via Docker bridge network
- ✅ No external database access

**Conclusion:** SSL/TLS encryption for PostgreSQL is **optional** and **not recommended** for this deployment architecture. Focus security efforts on higher-impact areas (security headers, WAF, authentication).

**Verification Steps (if SSL/TLS is required for compliance):**

```bash
# 1. Check PostgreSQL SSL settings
docker exec gear-stack-db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SHOW ssl;"

# Expected: ssl = on

# 2. Check SSL connection from app
docker exec gear-stack-app python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql+asyncpg://user:pass@db:5432/dbname?ssl=require')
print('SSL check:', engine.url.query.get('ssl'))
"
```

**Implementation:**

```yaml
# docker-compose.prod.yml
services:
  db:
    image: postgres:17-alpine
    environment:
      - POSTGRES_SSL_MODE=require
    command: >
      postgres
      -c ssl=on
      -c ssl_cert_file=/var/lib/postgresql/server.crt
      -c ssl_key_file=/var/lib/postgresql/server.key
    volumes:
      - ./ssl/server.crt:/var/lib/postgresql/server.crt:ro
      - ./ssl/server.key:/var/lib/postgresql/server.key:ro
```

**Generate SSL Certificates:**

```bash
# Self-signed for internal Docker network
openssl req -new -x509 -days 3650 -nodes -text \
  -out backend/ssl/server.crt \
  -keyout backend/ssl/server.key \
  -subj "/CN=gear-stack-db"

chmod 600 backend/ssl/server.key
```

**Update Connection String:**

```bash
# .env
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}?ssl=require
```

**Checklist:**
- [ ] Generate SSL certificates for PostgreSQL
- [ ] Configure PostgreSQL to use SSL
- [ ] Update DATABASE_URL with ssl=require
- [ ] Test database connectivity
- [ ] Verify SSL is enforced (attempt non-SSL connection should fail)
- [ ] Document SSL setup in deployment guide

---

#### 4. Implement Web Application Firewall (WAF)

**Impact:** High - Protection against common web attacks
**Complexity:** Medium
**Location:** Caddy reverse proxy layer

**Option 1: Caddy with Coraza WAF (Recommended)**

```bash
# Install Caddy with Coraza plugin
# https://github.com/corazawaf/coraza-caddy

# Build custom Caddy with Coraza
xcaddy build --with github.com/corazawaf/coraza-caddy
```

**Caddyfile with WAF:**

```caddyfile
{
    order coraza_waf first
}

yourdomain.com {
    coraza_waf {
        load_owasp_crs
        directives {
            SecRuleEngine On
            SecRequestBodyAccess On

            # Block SQL injection
            SecRule ARGS "@detectSQLi" "id:1001,phase:2,deny,status:403,msg:'SQL Injection Detected'"

            # Block XSS
            SecRule ARGS "@detectXSS" "id:1002,phase:2,deny,status:403,msg:'XSS Detected'"

            # Rate limiting
            SecRule REQUEST_LINE "@streq GET /" "id:1003,phase:1,pass,setvar:ip.requests=+1,expirevar:ip.requests=60"
            SecRule IP:REQUESTS "@gt 100" "id:1004,phase:1,deny,status:429,msg:'Rate limit exceeded'"
        }
    }

    reverse_proxy localhost:8000
}
```

**Option 2: Cloudflare WAF (Cloud-based)**

```bash
# Configure Cloudflare as reverse proxy
# Enable WAF rules in Cloudflare dashboard
# - OWASP ModSecurity Core Rule Set
# - Custom rules for API protection
# - Rate limiting
```

**Option 3: ModSecurity with Nginx (Alternative)**

If switching from Caddy to Nginx:

```nginx
# nginx.conf
load_module modules/ngx_http_modsecurity_module.so;

http {
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsec/main.conf;
}
```

**Checklist:**
- [ ] Choose WAF solution (Coraza/Cloudflare/ModSecurity)
- [ ] Install and configure WAF
- [ ] Enable OWASP Core Rule Set
- [ ] Configure custom rules for API endpoints
- [ ] Test WAF with attack simulations
- [ ] Monitor WAF logs for false positives
- [ ] Tune rules to reduce false positives
- [ ] Document WAF configuration

---

### MEDIUM PRIORITY

#### 5. Migrate to httpOnly Cookies for Token Storage

**Impact:** Medium - Better protection against XSS token theft
**Complexity:** Medium
**Location:** Backend auth endpoints + Frontend auth composables

**Current:** Tokens stored in localStorage (vulnerable to XSS)
**Target:** Tokens stored in httpOnly cookies (not accessible to JavaScript)

**Backend Changes:**

```python
# backend/app/api/endpoints/auth.py

from fastapi import Response

@router.post("/login")
async def login(response: Response, credentials: LoginRequest):
    # ... authentication logic ...

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Set httpOnly cookies instead of returning in body
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Not accessible via JavaScript
        secure=True,    # HTTPS only
        samesite="strict",  # CSRF protection
        max_age=15 * 60  # 15 minutes
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60  # 7 days
    )

    return {"message": "Login successful"}
```

**Frontend Changes:**

```typescript
// src/shared/services/authInterceptors.ts

// Remove localStorage token retrieval
// Cookies are sent automatically with requests

// No changes needed in axios config - cookies sent automatically
```

**CSRF Protection (Required with Cookies):**

```python
# backend/app/middleware/csrf.py

from fastapi import Request, HTTPException
from secrets import token_urlsafe

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            csrf_token = request.headers.get("X-CSRF-Token")
            cookie_token = request.cookies.get("csrf_token")

            if not csrf_token or csrf_token != cookie_token:
                raise HTTPException(status_code=403, detail="CSRF token missing or invalid")

        response = await call_next(request)

        # Set CSRF token cookie on first request
        if "csrf_token" not in request.cookies:
            csrf_token = token_urlsafe(32)
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=False,  # Must be readable by JS to send in header
                secure=True,
                samesite="strict"
            )

        return response
```

**Checklist:**
- [x] Implement cookie-based auth in backend (refresh HttpOnly; access in memory)
- [x] Add CSRF protection middleware
- [x] Update frontend to use cookies (refresh) + CSRF header
- [x] Remove localStorage token storage (access in memory)
- [x] Add CSRF token to request headers
- [x] Test authentication flow (cookie router tests + CSRF unit tests)
- [x] Test token refresh flow
- [ ] Update documentation (ops notes optional)
---

#### 6. Implement CSRF Protection

**Impact:** Medium - Required if using cookie-based auth
**Complexity:** Low-Medium
**Location:** Backend middleware + frontend interceptor
**Status (2026-07-24):** ✅ Done — `CSRFMiddleware` + `GET /api/auth/csrf-token` + FE `X-CSRF-Token`
**Implementation:** See section #5 above (included in httpOnly cookie migration)

**Additional Endpoint:**

```python
# backend/app/api/endpoints/auth.py

@router.get("/csrf-token")
async def get_csrf_token(request: Request):
    """Get CSRF token for subsequent requests"""
    return {"csrf_token": request.cookies.get("csrf_token")}
```

**Frontend Usage:**

```typescript
// Get CSRF token on app initialization
const csrfToken = document.cookie
  .split('; ')
  .find(row => row.startsWith('csrf_token='))
  ?.split('=')[1]

// Add to all mutation requests
axios.defaults.headers.common['X-CSRF-Token'] = csrfToken
```

**Checklist:**
- [x] Implement CSRF middleware (`backend/app/core/csrf.py`)
- [x] Add CSRF token endpoint (`GET /api/auth/csrf-token`)
- [x] Configure token in frontend (`csrf.ts` + auth interceptor)
- [x] Exempt safe methods (GET, HEAD, OPTIONS) + Stripe webhooks
- [x] Test CSRF protection (`tests/test_csrf_middleware.py`)
- [x] Handle token bootstrap (ensure on app boot / before mutating calls)
---

#### 7. Enable Strict CORS

**Impact:** Medium - Prevents unauthorized API access
**Complexity:** Low
**Location:** Backend CORS configuration

**Current State:** Verify if wildcards are used in production

```python
# backend/app/main.py

from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# ❌ AVOID in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # BAD - allows any origin
)

# ✅ STRICT CORS for production
if settings.ENVIRONMENT == "production":
    allowed_origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ]
else:
    # Allow localhost for development
    allowed_origins = [
        "http://localhost:5176",
        "http://localhost:5173",
        "http://127.0.0.1:5176",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],  # If using pagination headers
)
```

**Checklist:**
- [ ] Remove wildcard origins in production
- [ ] Configure explicit allowed origins
- [ ] Set allow_credentials=True (for cookies)
- [ ] Restrict allowed methods
- [ ] Test CORS from browser
- [ ] Verify preflight OPTIONS requests work

---

### LOW PRIORITY (Documentation & Procedures)

#### 8. Document Database Backup/Recovery Procedures

**Impact:** Medium (disaster recovery)
**Complexity:** Low
**Location:** docs/deployment/
**Status (2026-07-24):** ✅ Done — [BACKUP_RECOVERY.md](../deployment/BACKUP_RECOVERY.md)

**Create:** `docs/deployment/BACKUP_RECOVERY.md` (canonical; short pointer in `production-manual.md`)

**Checklist:**
- [x] Document backup procedure (`.backups/`, `pg_dump`, naming)
- [x] Document safe restore (throwaway `backend_restore_test` — no prod wipe)
- [x] Document optional cron + off-site copy
- [x] Document S3/media backup when `STORAGE_TYPE=s3`
- [ ] Configure automated backups on the VPS (ops — cron from runbook)
- [ ] Configure off-site backup bucket (ops)
- [ ] Run quarterly restore drill and record date
---

#### 9. Implement Secrets Rotation Procedures

**Impact:** Medium (reduces exposure window)
**Complexity:** Low
**Location:** docs/deployment/
**Status (2026-07-24):** ✅ Done — [SECRETS_ROTATION.md](../deployment/SECRETS_ROTATION.md)

**Checklist:**
- [x] Document rotation procedures for JWT, OAuth, DB, Redis, S3 (+ Stripe/reCAPTCHA notes)
- [x] Document rollback and “no secrets in git/docs” rules
- [ ] Create calendar reminders for rotation schedule (ops)
- [ ] Test rotation procedures in non-prod when convenient (ops)
---

#### 10. Security Monitoring & Alerting

**Impact:** Medium (early threat detection)
**Complexity:** Medium
**Location:** Infrastructure
**Status (2026-07-24):** ✅ Covered — no separate Gear Stack implementation needed

**Current stack:**

1. **Sentry (in this repo)** — application errors, traces, replay (BE `init_sentry` / FE `src/shared/services/sentry.ts`). Configure product alerts in Sentry UI as needed.
2. **Ops Monitor (`../ops-monitor`)** — project-level / infra monitoring (uptime, health, ops dashboards). Source of truth for “is the service up / healthy?” lives there, not in a duplicate Gear Stack monitoring plan.
3. **Optional later:** Fail2ban / centralized Caddy logs — only if Ops Monitor gaps appear; not a blocker for closing this item.

**Checklist:**
- [x] Application error monitoring (Sentry)
- [x] Uptime / ops monitoring (Ops Monitor — sibling project)
- [ ] (Optional) Sentry alert rules tuned for auth spikes
- [ ] (Optional) Incident response runbook cross-link to Ops Monitor

---

## 📋 Implementation Roadmap

### Phase 1: Critical Security Headers (Week 1)
- [ ] Implement SecurityHeadersMiddleware
- [ ] Configure CSP in Report-Only mode
- [ ] Add all security headers
- [ ] Test and verify headers
- [ ] Switch CSP to enforcement mode

### Phase 2: Infrastructure Hardening (Week 2)
- [ ] Consider PostgreSQL SSL/TLS (if compliance required)
- [ ] Configure strict CORS
- [ ] Implement WAF (Coraza or Cloudflare)
- [ ] Test WAF rules

### Phase 3: Authentication Security (Week 3-4)
- [x] Implement httpOnly cookie auth (refresh)
- [x] Add CSRF protection
- [x] Access token in memory (not localStorage)
- [x] Test authentication / refresh / CSRF flows

### Phase 4: Operational Security (Week 5-6)
- [x] Document backup/recovery procedures
- [ ] Implement automated backups on VPS (ops — see runbook)
- [x] Create secrets rotation procedures
- [x] Security monitoring covered (Sentry + Ops Monitor)
- [ ] Quarterly restore / rotation drills (ops)
### Phase 5: Continuous Improvement (Ongoing)
- [ ] Quarterly security audits
- [ ] Regular dependency updates
- [ ] Security training for team
- [ ] Penetration testing (annual)

---

## 🧪 Testing & Verification

### Security Header Testing

```bash
# Test with curl
curl -I https://yourdomain.com

# Test with online tools
# - https://securityheaders.com
# - https://observatory.mozilla.org
# - https://csp-evaluator.withgoogle.com
```

### WAF Testing

```bash
# Test SQL injection blocking
curl "https://yourdomain.com/api/containers?id=1' OR '1'='1"
# Should return 403 Forbidden

# Test XSS blocking
curl "https://yourdomain.com/api/search?q=<script>alert('xss')</script>"
# Should return 403 Forbidden
```

### SSL/TLS Testing

```bash
# Test SSL connection
openssl s_client -connect yourdomain.com:443 -tls1_2

# Test with online tools
# - https://www.ssllabs.com/ssltest/
```

### CSRF Testing

```bash
# Attempt request without CSRF token
curl -X POST https://yourdomain.com/api/containers \
  -H "Content-Type: application/json" \
  -d '{"name":"Test"}'
# Should return 403 Forbidden
```

---

## 📚 References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
- [Caddy Security Best Practices](https://caddyserver.com/docs/conventions#security)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [CSP Reference](https://content-security-policy.com/)

---

## 📊 Progress Tracking

| Item | Priority | Status | Completed |
|------|----------|--------|-----------|
| Security Headers | Critical | ✅ Done | v2.47.0 |
| CSP Implementation | Critical | ✅ Done | v2.47.0 |
| PostgreSQL SSL | Low | ✅ Not Required | - |
| WAF Implementation | High | ⏸️ Deferred | Custom Caddy/Coraza ops cost; revisit later |
| httpOnly Cookies | Medium | ✅ Done | 2026-07-24 |
| CSRF Protection | Medium | ✅ Done | 2026-07-24 (double-submit + FE header) |
| Strict CORS | Medium | ✅ Done | `validate_production()` |
| Backup Procedures | Low | ✅ Done (docs) | [BACKUP_RECOVERY.md](../deployment/BACKUP_RECOVERY.md) — cron/off-site still ops |
| Secrets Rotation | Low | ✅ Done (docs) | [SECRETS_ROTATION.md](../deployment/SECRETS_ROTATION.md) |
| Monitoring & Alerting | Low | ✅ Covered | Sentry + Ops Monitor (`../ops-monitor`) |

---

**Last Updated:** 2026-07-24
**Next Review:** ops cron/off-site backup + quarterly drills; WAF only if reconsidered