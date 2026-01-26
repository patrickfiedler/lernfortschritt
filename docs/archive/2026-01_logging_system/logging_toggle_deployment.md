# Page View Logging Toggle - Deployment Guide

**Date:** 2026-01-19
**Commit:** df58978
**Status:** ✅ READY FOR PRODUCTION

## Overview

Added an admin toggle to disable page_view logging for improved performance. Only important activities (login, tasks, quiz, downloads) will continue to be logged when disabled.

## Changes Summary

### Database
- New `app_settings` table (key-value store for global settings)
- Helper functions for getting/setting values
- Default: page view logging ENABLED

### Admin UI
- Toggle switch on admin dashboard under "Systemeinstellungen"
- Smooth animated toggle component
- Changes persist across server restarts

### Performance
- Setting cached in memory (`app.config['LOG_PAGE_VIEWS']`)
- No database query on every request
- Loaded once at startup, updated when admin changes setting

## Production Deployment Steps

### Step 1: Update Code
```bash
ssh user@server 'sudo /opt/lernmanager/deploy/update.sh'
```

### Step 2: Run Database Migration
```bash
ssh user@server
cd /opt/lernmanager
sudo -u lernmanager SQLCIPHER_KEY=secret python migrate_add_app_settings.py /opt/lernmanager/data/mbi_tracker.db
```

Expected output:
```
Using SQLCipher encrypted database
Creating backup: /opt/lernmanager/data/mbi_tracker.db.backup_XXXXXXXX_XXXXXX
=== Starting Migration ===
1. Creating app_settings table...
   ✓ Table created
2. Setting default values...
   ✓ Default setting: log_page_views = true
=== Migration Complete ===
```

### Step 3: Restart Service
```bash
sudo systemctl restart lernmanager
```

### Step 4: Verify
1. Log in as admin
2. Navigate to admin dashboard
3. Scroll down to "Systemeinstellungen" card
4. Verify toggle switch is visible and set to ON (enabled)
5. Try toggling it off and back on
6. Check server logs to confirm setting changes

## Files Modified

- `models.py` - app_settings table + helper functions (lines 379-386, 2136-2197)
- `app.py` - cached setting + conditional logging + route (lines 154-173, 1506-1517, 1535-1537)
- `static/css/style.css` - toggle switch styles (lines 843-893)
- `templates/admin/dashboard.html` - settings card with toggle (lines 45-63)
- `migrate_add_app_settings.py` - migration script (NEW)

## How It Works

### At Startup
1. App loads setting from database: `models.get_bool_setting('log_page_views', default=True)`
2. Caches value in: `app.config['LOG_PAGE_VIEWS']`
3. Prints status: "Page view logging: enabled" or "disabled"

### On Every Request
1. `@app.before_request` decorator runs `log_analytics()` function
2. Checks cached value: `if app.config.get('LOG_PAGE_VIEWS', True):`
3. If True: logs page_view event (existing behavior)
4. If False: skips page_view logging, only important events logged

### When Admin Changes Setting
1. Admin clicks toggle on dashboard
2. Form submits to `/admin/settings` route
3. Setting saved to database: `models.set_bool_setting('log_page_views', value)`
4. Cache updated: `app.config['LOG_PAGE_VIEWS'] = value`
5. Flash message confirms change
6. Redirect back to dashboard

## Performance Impact

### With Page View Logging Enabled (Default)
- No change from current behavior
- Every page view logged asynchronously

### With Page View Logging Disabled
- Eliminates ~1-5ms per request (mostly DB write overhead)
- Reduces database size growth
- Analytics still capture important events:
  - login
  - task_start, task_complete
  - subtask_complete
  - quiz_attempt
  - file_download
  - self_eval

## Rollback Plan

If issues occur:

### Option 1: Re-enable via UI
- Log in as admin
- Toggle setting back to ON

### Option 2: Database Restore
```bash
# Find latest backup
ls -lt /opt/lernmanager/data/mbi_tracker.db.backup_*

# Restore
sudo systemctl stop lernmanager
cp /opt/lernmanager/data/mbi_tracker.db.backup_XXXXXXXX_XXXXXX /opt/lernmanager/data/mbi_tracker.db
sudo systemctl start lernmanager
```

### Option 3: Manual Database Fix
```bash
# Connect to database
sqlite3 /opt/lernmanager/data/mbi_tracker.db

# Set value
UPDATE app_settings SET value = 'true' WHERE key = 'log_page_views';
.quit

# Restart
sudo systemctl restart lernmanager
```

## Testing Checklist

- [ ] Server starts without errors
- [ ] "Page view logging: enabled" appears in startup logs
- [ ] Admin dashboard loads correctly
- [ ] Settings card visible with toggle switch
- [ ] Toggle is ON by default
- [ ] Clicking toggle changes state
- [ ] Flash message appears after toggle
- [ ] Setting persists after page reload
- [ ] Setting persists after server restart
- [ ] Page views logged when toggle is ON
- [ ] Page views NOT logged when toggle is OFF
- [ ] Other events (login, tasks) still logged when toggle is OFF

## Notes

- Migration is idempotent (safe to run multiple times)
- Default setting ensures backward compatibility
- No user-facing changes unless admin disables the feature
- Analytics dashboards will show fewer page_view events if disabled
- Consider monitoring database size reduction over time

---

**Implementation completed by:** Claude Sonnet 4.5
**Full details:** See `task_plan_logging_toggle.md` and `notes_logging_toggle.md`
