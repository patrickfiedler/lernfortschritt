# Task Plan: Debug Production Deployment Failure

## Goal
Identify why recent commits broke production server while working on localhost, and provide fix.

## Phases
- [x] Phase 1: Examine recent commits since 06eb4af
- [x] Phase 2: Identify root cause
- [ ] Phase 3: Provide solution and verification steps
- [ ] Phase 4: Document findings

## Key Questions
1. ✅ What changed between 06eb4af and current HEAD?
2. ✅ Are there environment-specific configurations?
3. ✅ Did dependencies or deployment scripts change?
4. ❓ What error logs are available from production?

## Root Cause Analysis - IDENTIFIED ✅

**Primary Issue**: Database schema mismatch due to missing migration

### The Problem
- **Commit 080d06c** (Jan 20) added `why_learn_this` column to task table
- Migration script created: `migrate_add_why_learn_this.py`
- App code updated to use the new column (app.py, models.py, templates)
- **Migration was run locally** = localhost works fine
- **Migration NOT run on production** = production crashes

### Evidence
1. `app.py:514, 554` - code uses `why_learn_this` field
2. `models.py:871, 883, 1182` - SQL queries include `why_learn_this`
3. Migration script exists and is SQLCipher-compatible
4. Localhost works = database has the column
5. Production fails = database missing the column

### Expected Error
When production server tries to access task-related pages:
```
SQL error: no such column: why_learn_this
```

### Why da542cf is NOT the cause
The most recent commit (HTTPS redirect fix) actually makes the app MORE stable:
- Changed from `FLASK_ENV=production` to `FORCE_HTTPS` env var
- Allows HTTP operation by default (prevents redirect loops)
- This commit HELPS, doesn't break

## Solution

### Step 1: Verify the problem
SSH to production and check logs:
```bash
sudo journalctl -u lernmanager -n 100 --no-pager
```
Look for SQL errors mentioning "why_learn_this"

### Step 2: Run the migration
```bash
cd /opt/lernmanager
sudo -u lernmanager python migrate_add_why_learn_this.py
```

The migration is:
- ✅ Idempotent (safe to run multiple times)
- ✅ Creates automatic backup
- ✅ SQLCipher compatible (checks for SQLCIPHER_KEY env var)
- ✅ Verbose output shows progress

### Step 3: Restart service
```bash
sudo systemctl restart lernmanager
```

### Step 4: Verify fix
```bash
sudo systemctl status lernmanager
```

## Status
**Phase 2 Complete** - Root cause identified, solution ready to provide to user
