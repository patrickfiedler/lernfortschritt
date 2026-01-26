# Notes: NS_ERROR_REDIRECT_LOOP Investigation

## Common Causes

### 1. HTTPS Redirect Loop
- Flask app redirects HTTP → HTTPS
- Nginx redirects HTTPS → HTTP
- Creates infinite loop

### 2. Proxy Configuration Issues
- Missing X-Forwarded-Proto header
- Flask sees HTTP even when client uses HTTPS
- Triggers unwanted redirects

### 3. Multiple Redirect Rules
- Both nginx and Flask enforcing redirects
- Conflicting redirect logic

## Investigation Steps

### Step 1: Check Deployment Files
- [ ] Review deploy/setup.sh for nginx config
- [ ] Check if HTTPS is enforced
- [ ] Look for redirect rules in app.py

### Step 2: VPS Status
- [ ] Check if service is running
- [ ] Review nginx configuration
- [ ] Check SSL/TLS setup

## Findings

### Deployment Configuration Review

**Nginx Configuration (deploy/nginx.conf):**
- Listens on port 80
- Proxies to Flask app on 127.0.0.1:8080
- Has commented-out HTTPS redirect: `# return 301 https://$server_name$request_uri;`
- Sets X-Forwarded-Proto header correctly
- Comment says certbot will add HTTPS redirect automatically

**Flask App Configuration (app.py):**
- Line 25-26: Sets SESSION_COOKIE_SECURE = True when FLASK_ENV == 'production'
- This means cookies only work over HTTPS
- Multiple redirects use url_for() without _external or _scheme parameters

**Setup Script (deploy/setup.sh):**
- No HTTPS configuration included
- Mentions certbot setup in Next Steps (line 237)
- Doesn't set FLASK_ENV environment variable

### Likely Root Cause

**Hypothesis:** SESSION_COOKIE_SECURE is True but site is accessed over HTTP
- When FLASK_ENV='production', SESSION_COOKIE_SECURE = True
- Browser receives redirect to /login but can't store session cookie (HTTP only)
- Each request appears unauthenticated
- Infinite redirect loop: / → /login → / → /login

**CONFIRMED ROOT CAUSE:**

From `deploy/lernmanager.service` line 13:
```
Environment="FLASK_ENV=production"
```

From `app.py` lines 25-26:
```python
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True  # Only send over HTTPS
```

**The Problem:**
1. FLASK_ENV is set to 'production' in systemd service
2. This triggers SESSION_COOKIE_SECURE = True in app.py
3. User accesses site over HTTP (no HTTPS configured yet)
4. Browser cannot save session cookies (they require HTTPS)
5. Every request appears unauthenticated
6. App redirects to /login repeatedly
7. **REDIRECT LOOP**

**The Solution:**
Either:
- **Option A (Quick Fix):** Remove or comment out SESSION_COOKIE_SECURE setting temporarily
- **Option B (Proper Fix):** Set up HTTPS with certbot as mentioned in setup.sh
- **Option C (Best Fix):** Make SESSION_COOKIE_SECURE conditional on actual HTTPS availability
