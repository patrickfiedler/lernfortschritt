# Secrets Management Research Notes

## Current Implementation Analysis

### How Secrets Are Currently Handled

#### setup.sh (Initial Installation)
1. **Generation** (lines 151-160):
   - Generates `SECRET_KEY` using `python3 -c "import secrets; print(secrets.token_hex(32))"`
   - 64-character hex string

2. **Storage - Two Locations** (lines 162-176):
   - **File**: `$APP_DIR/.secrets` (lines 163-168)
     - Format: `SECRET_KEY=<value>`
     - Permissions: `600` (root only)
     - Owner: `root:root`
   - **Systemd service**: `/etc/systemd/system/lernmanager.service`
     - Injected via `sed -i "s/CHANGE_ME_TO_RANDOM_STRING/$SECRET_KEY/"` (line 176)
     - Embedded as `Environment="SECRET_KEY=<value>"`

#### update.sh (Updates)
**Current behavior when service file changes** (lines 225-262):

1. Detects if `deploy/lernmanager.service` changed in git
2. Extracts secrets from OLD service file:
   ```bash
   CURRENT_SECRET=$(grep "SECRET_KEY=" "$SYSTEMD_SERVICE" | sed -n 's/.*"\(.*\)".*/\1/p')
   CURRENT_SQLCIPHER=$(grep "SQLCIPHER_KEY=" "$SYSTEMD_SERVICE" | sed -n 's/.*"\(.*\)".*/\1/p')
   ```
3. Copies NEW service file
4. Injects OLD secrets into NEW service file
5. Reloads systemd

**The Problem**:
- If secret format changes (e.g., variable name, line format)
- If sed extraction fails (wrong regex)
- If service template changes structure
- Secrets could be lost

**Mitigation that exists**:
- `.secrets` file backup exists (from setup.sh line 163)
- But update.sh doesn't USE this backup file!
- Rollback preserves secrets (lines 73-85)

## The Issue - Confirmed

You're right! The weakness is:
1. `update.sh` extracts secrets from the SERVICE FILE itself (brittle sed parsing)
2. `.secrets` file exists (created by setup.sh) but NOT used by update.sh
3. If the service file format changes significantly, extraction could fail
4. Secrets stored in two places creates sync issues

**Specific risks**:
- Service file format change breaks sed regex
- Someone manually edits service file (breaks extraction)
- New environment variables added (need manual extraction logic)
- Secrets drift between `.secrets` file and service file

## Options for Secrets Management

### Option 1: systemd EnvironmentFile= (Recommended)

**How it works**:
- Store secrets in separate file: `/opt/lernmanager/.env` or `/etc/lernmanager/secrets.env`
- systemd service loads it with `EnvironmentFile=` directive
- File never changes during updates

**Service file change**:
```ini
[Service]
# Load environment variables from file
EnvironmentFile=/opt/lernmanager/.env
# or for more security:
EnvironmentFile=/etc/lernmanager/secrets.env
```

**Secrets file format** (`/opt/lernmanager/.env`):
```bash
SECRET_KEY=abc123...
SQLCIPHER_KEY=xyz789...
FORCE_HTTPS=true
```

**Pros**:
- ✅ Clean separation of secrets and config
- ✅ Secrets file NEVER touched during updates
- ✅ Standard systemd feature, well-documented
- ✅ Easy to add/modify secrets (edit one file)
- ✅ Service file becomes template (no secret injection needed)
- ✅ Can use multiple files if needed
- ✅ Supports comments and blank lines

**Cons**:
- ⚠️ File must be readable by service user (or root)
- ⚠️ Requires file permissions management

**Security considerations**:
- File ownership: `root:root`
- File permissions: `600` (read/write for root only)
- Location: `/opt/lernmanager/.env` (same as current `.secrets`)
  - Or `/etc/lernmanager/secrets.env` (more traditional for system configs)

---

### Option 2: systemd LoadCredential= (Modern, Secure)

**How it works**:
- Store secrets in `/etc/credstore/` or `/var/lib/systemd/credentials/`
- systemd loads them as files in `$CREDENTIALS_DIRECTORY`
- App reads from file at runtime

**Service file change**:
```ini
[Service]
LoadCredential=secret_key:/etc/credstore/lernmanager-secret-key
LoadCredential=sqlcipher_key:/etc/credstore/lernmanager-sqlcipher-key
```

**App change required**:
```python
# In app.py, instead of os.environ.get('SECRET_KEY'):
import os
creds_dir = os.environ.get('CREDENTIALS_DIRECTORY')
if creds_dir:
    with open(f'{creds_dir}/secret_key') as f:
        app.secret_key = f.read().strip()
else:
    app.secret_key = os.environ.get('SECRET_KEY')  # fallback
```

**Pros**:
- ✅ Most secure systemd method
- ✅ Secrets encrypted at rest (if using systemd-creds)
- ✅ Secrets not in environment variables
- ✅ Modern systemd best practice

**Cons**:
- ❌ Requires app code changes (read from files, not env vars)
- ❌ More complex setup
- ❌ Requires systemd 246+ (Ubuntu 20.10+)
- ❌ Overkill for this project

---

### Option 3: .env File + EnvironmentFile= + Fallback

**How it works**:
- Use EnvironmentFile= to load `.env`
- If missing, fall back to inline Environment= directives
- Best of both worlds

**Service file**:
```ini
[Service]
# Load from file if it exists (won't fail if missing)
EnvironmentFile=-/opt/lernmanager/.env
# Fallback defaults (overridden by file if it exists)
Environment="FLASK_ENV=production"
Environment="TMPDIR=/opt/lernmanager/instance/tmp"
```

**Note**: `-` prefix means "don't fail if file missing"

**Pros**:
- ✅ Graceful fallback
- ✅ Works for both secrets and non-secrets
- ✅ Backwards compatible

**Cons**:
- ⚠️ Slightly more complex
- ⚠️ Could mask misconfiguration

---

### Option 4: Keep Current + Use .secrets File

**How it works**:
- Improve `update.sh` to read from `.secrets` file instead of parsing service
- Keep secrets in service file for runtime

**Changes to update.sh**:
```bash
# Instead of parsing service file:
if [ -f "$APP_DIR/.secrets" ]; then
    source "$APP_DIR/.secrets"
    CURRENT_SECRET="$SECRET_KEY"
fi
```

**Pros**:
- ✅ Minimal changes
- ✅ Uses existing `.secrets` file
- ✅ No service file format change

**Cons**:
- ❌ Still duplicates secrets (file + service)
- ❌ Secrets still in service file (less clean)
- ❌ .secrets file must be kept in sync

---

### Option 5: External Secret Management (Overkill)

Tools like HashiCorp Vault, AWS Secrets Manager, etc.

**Assessment**: Way too complex for a single-server Flask app

---

## Recommendation Summary

| Option | Complexity | Security | Best For |
|--------|-----------|----------|----------|
| 1. EnvironmentFile= | Low | Good | **This project** ✅ |
| 2. LoadCredential= | High | Best | High-security orgs |
| 3. EnvironmentFile + Fallback | Medium | Good | Complex deployments |
| 4. Improve current | Low | OK | Quick fix |
| 5. External tools | Very High | Excellent | Enterprise |
