# Production Deployment Debug Notes

## Problem Summary
- Localhost works fine
- Production server broken after recent commits
- Last known working: commit 06eb4af (2026-01-19)
- Recent commits between 06eb4af and da542cf

## Recent Commits Analysis

### Commit da542cf (2026-01-26) - HTTPS/Redirect Fix
**This is the most recent commit - likely the culprit!**

Changes made:
1. Changed `FLASK_ENV=production` check to `FORCE_HTTPS` env var
2. `SESSION_COOKIE_SECURE` now only enabled when `FORCE_HTTPS=true`
3. Updated `deploy/lernmanager.service` to include commented-out `FORCE_HTTPS` line

**Problem**: The service file was updated but `FLASK_ENV=production` is STILL SET in the service file!

### Other Commits (fe60b86, 876a50b, 7253d66, 080d06c)
- Student interface redesign
- Subtask navigation improvements
- New database field `why_learn_this`
- Documentation updates

## Hypothesis: Environment Variable Issue

The commit da542cf changed the logic from:
```python
if os.environ.get('FLASK_ENV') == 'production':
```

To:
```python
if os.environ.get('FORCE_HTTPS', '').lower() in ('true', '1', 'yes'):
```

**BUT** the systemd service still has:
```
Environment="FLASK_ENV=production"
```

This means production server may have:
- `FLASK_ENV=production` set (old env var, now unused)
- `FORCE_HTTPS` NOT set (new env var required)
- Result: `SESSION_COOKIE_SECURE` NOT enabled (intended for HTTP)

**However**, this shouldn't break the app! This should make it WORK over HTTP!

## Alternative Hypothesis: Dependencies or Migration

Looking at git diff stats:
- `migrate_add_why_learn_this.py` - new migration script
- Database schema changes in models.py
- Major template changes

**Possible issues:**
1. Migration script not run on production
2. Database schema mismatch
3. Template syntax error only visible in production

## Most Likely Cause: Missing Database Migration

**Commit 080d06c** added a new field `why_learn_this` to the task table:
- Migration script: `migrate_add_why_learn_this.py`
- Changes to app.py to use the field
- Changes to templates to display/edit the field

**If migration wasn't run on production:**
- app.py tries to query/save `why_learn_this` field
- Database doesn't have the column
- SQL error occurs: "no such column: why_learn_this"
- App crashes/errors on any task-related page

## Verification Steps
1. Check production logs for SQL errors mentioning "why_learn_this"
2. Confirm if migration script was run on production server
3. If not run, need to execute: `python migrate_add_why_learn_this.py`

## Solution
SSH to production and run:
```bash
cd /opt/lernmanager
sudo -u lernmanager python migrate_add_why_learn_this.py
```

## Why it works on localhost
- Migration was run locally during development
- Database schema matches code expectations
- Production database is out of sync
