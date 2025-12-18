# Security Incident Analysis - Attack Findings

**Date:** 2025-12-18
**Status:** Post-incident analysis after VPS reinstallation
**Severity:** CRITICAL

## Executive Summary

The VPS was compromised through **publicly exposed database services** (PostgreSQL and Redis) that were inadvertently made accessible to the internet. The docker-compose.dev.yml configuration exposed critical services on all network interfaces (0.0.0.0), creating multiple attack vectors.

---

## Attack Vectors Identified

### 1. **PostgreSQL Publicly Exposed** ⚠️ CRITICAL

**Configuration Issue:**
```yaml
# backend/docker-compose.dev.yml:13-14
ports:
  - "${DB_FORWARD_PORT:-5432}:5432"  # ❌ Exposed to 0.0.0.0
```

**Current Status:**
```
LISTEN 0  4096  0.0.0.0:5432  0.0.0.0:*
```

**Evidence from Logs:**
```
2025-12-18 23:30:21.266 UTC [1012] FATAL:  password authentication failed for user "postgres"
2025-12-18 23:30:21.513 UTC [1013] FATAL:  password authentication failed for user "postgres"
2025-12-18 23:34:05.348 UTC [1313] FATAL:  password authentication failed for user "refactorian"
2025-12-18 23:34:05.621 UTC [1314] FATAL:  password authentication failed for user "refactorian"
2025-12-18 23:34:05.981 UTC [1315] FATAL:  password authentication failed for user "zope"
2025-12-18 23:34:06.248 UTC [1316] FATAL:  password authentication failed for user "zope"
2025-12-18 23:34:06.503 UTC [1317] FATAL:  password authentication failed for user "pgadmin"
2025-12-18 23:34:06.748 UTC [1325] FATAL:  password authentication failed for user "pgadmin"
2025-12-18 23:34:07.035 UTC [1326] FATAL:  password authentication failed for user "pgbouncer"
2025-12-18 23:34:07.294 UTC [1327] FATAL:  password authentication failed for user "pgbouncer"
2025-12-18 23:34:07.700 UTC [1328] FATAL:  password authentication failed for user "postgresql"
2025-12-18 23:34:08.261 UTC [1330] FATAL:  password authentication failed for user "postgres"
```

**Analysis:**
- Automated brute force attacks targeting common PostgreSQL usernames
- Attackers probing for weak credentials
- Multiple authentication attempts within seconds
- Common PostgreSQL-related usernames targeted: postgres, pgadmin, pgbouncer, postgresql, refactorian, zope

**Impact:**
- If weak credentials were used, full database access could be obtained
- Access to all user data, authentication tokens, API keys
- Potential for data exfiltration, modification, or deletion

---

### 2. **Redis Publicly Exposed WITHOUT Password** ⚠️ CRITICAL

**Configuration Issue:**
```yaml
# backend/docker-compose.dev.yml:33-37
redis:
  ports:
    - "${REDIS_FORWARD_PORT:-6379}:6379"  # ❌ Exposed to 0.0.0.0
  command: redis-server --appendonly yes  # ❌ NO PASSWORD!
```

**Current Status:**
```
LISTEN 0  4096  0.0.0.0:6399  0.0.0.0:*  (custom port, but still exposed)
```

**Impact:**
- **REMOTE CODE EXECUTION (RCE)** possible through Redis
- Redis can write files to disk (appendonly mode enabled)
- Attackers can:
  - Write SSH keys to `/root/.ssh/authorized_keys`
  - Write cron jobs for persistence
  - Dump all cached data (tokens, session data)
  - Use Redis as pivot point for further attacks
  - Execute Lua scripts for arbitrary code execution

---

### 3. **Weak Default Credentials in .env.example**

**Default credentials found:**
```bash
# backend/.env.example
POSTGRES_PASSWORD=changeme          # ❌ Extremely weak
MINIO_ROOT_PASSWORD=minioadmin123   # ❌ Publicly known default
SECRET_KEY=change-me-in-production-min-32-chars!  # ❌ If not changed
```

**Actual .env Status:**
- ✅ POSTGRES_PASSWORD changed to stronger password
- ✅ REDIS_FORWARD_PORT changed to non-standard 6399
- ⚠️ Redis still has NO PASSWORD configured

---

### 4. **Development Configuration Used in Production**

**Root Cause:**
Using `docker-compose.dev.yml` in production environment instead of a hardened production configuration.

**Problems:**
- Services exposed on all interfaces (0.0.0.0)
- No authentication on Redis
- Debug logging enabled
- Development volumes mounted
- No firewall rules or network isolation

---

## Timeline of Compromise (Hypothetical)

1. **Initial Reconnaissance**
   - Port scanner discovers open ports 5432 and 6379/6399
   - Identifies PostgreSQL and Redis services

2. **Attack on Redis** (Most Likely)
   - No password required
   - Attacker connects directly: `redis-cli -h <VPS_IP> -p 6399`
   - Writes malicious files or extracts cached data
   - Possible RCE through file write operations

3. **Attack on PostgreSQL** (Secondary)
   - Brute force attempts with common usernames
   - If successful, full database access obtained
   - Extraction of user credentials, API keys, tokens

4. **Lateral Movement**
   - Using compromised data to access other services
   - Potential privilege escalation
   - Persistence mechanisms installed

---

## Immediate Remediation Steps Taken

1. ✅ VPS reinstalled (clean slate)
2. ✅ Public access to website disabled via Caddy
3. ✅ PostgreSQL password changed from default
4. ✅ Redis port changed to non-standard 6399

---

## Required Security Hardening

### Priority 1: Network Isolation

**PostgreSQL - Bind to localhost only:**
```yaml
# docker-compose.yml
db:
  ports:
    - "127.0.0.1:5432:5432"  # ✅ Only local access
```

**Redis - Bind to localhost only AND add password:**
```yaml
redis:
  ports:
    - "127.0.0.1:6379:6379"  # ✅ Only local access
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
```

**Add to .env:**
```bash
REDIS_PASSWORD=<generate_strong_random_password>
```

### Priority 2: Remove Production Port Forwarding

**For production, do NOT expose database ports at all:**
```yaml
# docker-compose.prod.yml
db:
  # NO ports section - only accessible within Docker network
  networks:
    - gearstack-network

redis:
  # NO ports section - only accessible within Docker network
  networks:
    - gearstack-network
```

### Priority 3: Firewall Rules

```bash
# Allow only necessary ports
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw enable
```

### Priority 4: Credential Rotation

Generate new strong credentials:
```bash
# PostgreSQL password
openssl rand -base64 32

# Redis password
openssl rand -base64 32

# SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# AI_TOKEN_ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Priority 5: Create Separate Production Config

Create `docker-compose.prod.yml` with:
- No database port forwarding
- Redis with authentication
- Minimal mounted volumes
- Production environment variables
- Proper network isolation

---

## Security Best Practices for Future

1. **Never expose databases to public internet**
2. **Always use strong, randomly generated passwords**
3. **Always require authentication for Redis**
4. **Use separate dev/prod configurations**
5. **Implement firewall rules (ufw/iptables)**
6. **Regular security audits**
7. **Monitor logs for suspicious activity**
8. **Use VPN or SSH tunneling for remote database access**
9. **Enable fail2ban for brute force protection**
10. **Regular backup strategy**

---

## Log Evidence

### Redis Warning
```
1:C 18 Dec 2025 23:18:40.229 # WARNING Memory overcommit must be enabled!
```

### PostgreSQL Brute Force Attempts
Multiple FATAL authentication failures for users:
- postgres (most common)
- refactorian
- zope
- pgadmin
- pgbouncer
- postgresql

All within seconds, indicating automated attack.

---

## Recommendations

### Immediate (Within 24 hours)
1. ✅ Change all database ports to localhost binding
2. ✅ Add Redis password authentication
3. ✅ Enable firewall (ufw)
4. ✅ Rotate all credentials
5. ✅ Create docker-compose.prod.yml

### Short-term (Within 1 week)
1. Implement fail2ban for SSH and database protection
2. Set up centralized logging (e.g., Loki, ELK)
3. Configure automated backups
4. Security audit of all environment variables
5. Review all exposed services and APIs

### Long-term
1. Implement intrusion detection system (IDS)
2. Set up security monitoring and alerts
3. Regular penetration testing
4. Security training for team
5. Incident response plan documentation

---

## Conclusion

The compromise was highly likely due to **publicly exposed database services** with either weak or no authentication. Redis without password protection provides trivial RCE opportunities. PostgreSQL exposed to the internet was subject to brute force attacks.

The fix is straightforward: **NEVER expose database services to the public internet**. Use localhost binding, strong authentication, and proper network isolation.

**Status:** System reinstalled, immediate threats removed, hardening in progress.
