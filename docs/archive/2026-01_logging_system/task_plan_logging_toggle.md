# Task Plan: Add Admin Toggle for Page View Logging

## Goal
Add an admin setting to disable page_view logging to improve performance, while keeping activity logging enabled for important user actions.

## Phases
- [x] Phase 1: Research current logging implementation
- [x] Phase 2: Create app_settings table and helper functions
- [x] Phase 3: Add admin UI for the toggle setting
- [x] Phase 4: Implement conditional logging in code with caching
- [x] Phase 5: Test functionality
- [x] Phase 6: Commit and deploy

## Key Questions
1. ✅ Where is page_view logging currently implemented? → `app.py` line 1452, `@app.before_request` decorator
2. ✅ How to store the setting? → New `app_settings` table (key-value pairs)
3. ✅ Should this be a global setting or per-admin setting? → Global setting (affects all users)
4. ✅ What's the current performance impact? → Minimal (async queue), ~1-5ms savings expected

## Decisions Made
- **Storage**: Use `app_settings` table with key-value structure (extensible for future settings)
- **Default**: Keep logging ENABLED by default (backward compatible)
- **Caching**: Cache setting value in memory to avoid DB query on every request
- **Scope**: Global setting, not per-admin
- **UI Location**: Add toggle to admin dashboard with other system info

## Errors Encountered
- None yet

## Status
**ALL PHASES COMPLETE** - Ready for production deployment

**Commit:** df58978 - "feat: add admin toggle to disable page view logging"
**Pushed to:** GitHub main branch
**Date:** 2026-01-19

### Phase 5 Complete ✅
- Server starts successfully with default setting loaded
- "Page view logging: enabled" message shown at startup
- Migration script created and tested with SQLCipher support
- Ready for deployment

## Implementation Progress

### Phase 2 Complete ✅
- Added `app_settings` table to database schema (models.py:382-386)
- Created helper functions:
  - `get_setting(key, default)` - Get string value
  - `set_setting(key, value)` - Set value
  - `get_bool_setting(key, default)` - Get boolean
  - `set_bool_setting(key, value)` - Set boolean

### Phase 3 Complete ✅
- Added toggle switch CSS to style.css (lines 843-893)
- Added settings card to admin dashboard (templates/admin/dashboard.html:45-63)
- Created admin_update_settings route (app.py:161-173)
- Modified admin_dashboard to pass log_page_views value to template (app.py:154-158)

### Phase 4 Complete ✅
- Added conditional check in log_analytics() function (app.py:1506-1517)
- Cached setting value in app.config['LOG_PAGE_VIEWS'] for performance
- Load setting at app startup (app.py:1535-1537)
- Update cached value when setting changes (app.py:169)
