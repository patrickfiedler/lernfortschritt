# Notes: Page View Logging Toggle Research

## Current Implementation

### Analytics Logging Architecture
1. **Async Queue System** (`analytics_queue.py`):
   - Events queued with `enqueue_event()`
   - Background worker thread writes to database
   - Non-blocking for request handling
   - Queue size: max 1000 events

2. **Logging Entry Point** (`app.py` line 1452-1497):
   - `@app.before_request` decorator on `log_analytics()` function
   - Automatically logs ALL authenticated page views
   - Calls `models.log_analytics_event('page_view', ...)`

3. **Event Types**:
   - `page_view` - Every page load (the one we want to disable)
   - `login` - User authentication
   - `file_download` - Material downloads
   - `task_start`, `task_complete` - Learning progress
   - `subtask_complete` - Subtask completion
   - `quiz_attempt` - Quiz attempts
   - `self_eval` - Self-evaluations

### Current Exclusions (app.py:1456-1473)
- Static files (`/static/`)
- Favicon
- Analytics pages (`/admin/analytics`)
- Error logs page (`/admin/errors`)
- File downloads (logged manually with different event type)

## Database Schema

### Existing Tables
- No `settings` or `config` table exists
- Need to create new table for app-wide settings

### Analytics Events Table (models.py:362-364)
```sql
CREATE TABLE analytics_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,  -- 'login', 'page_view', etc.
    user_id INTEGER,
    user_type TEXT,  -- 'admin' or 'student'
    metadata TEXT    -- JSON
)
```

## Implementation Strategy

### Option A: Simple Boolean Flag (Recommended)
Create `app_settings` table with key-value pairs:
```sql
CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
```

Benefits:
- Simple and extensible
- Can add more settings later
- Easy to query: `SELECT value FROM app_settings WHERE key = 'log_page_views'`

### Option B: Dedicated Settings Table
Create structured table with columns for each setting.

Drawbacks:
- Requires schema changes for new settings
- Overkill for single boolean

## Performance Considerations

### Current Impact
- Async logging means minimal request blocking
- Already using background queue
- Main cost: queue operation (~0.001ms per request)

### Expected Improvement
- Disabling page_view logging eliminates:
  - Queue operation per request
  - Database write per page view
  - Estimated: 1-5ms saved per request (mostly on DB write side)

### Trade-off
- Lose page view analytics (visitor counts, popular pages)
- Keep important activity logging (learning progress, logins, etc.)

## Implementation Plan

1. **Database**: Create `app_settings` table with default value
2. **Models**: Add functions to get/set settings
3. **Admin UI**: Add checkbox in admin dashboard/settings page
4. **Code**: Wrap page_view logging in conditional check
5. **Default**: Start with logging ENABLED (don't break existing behavior)

## Files to Modify

1. `models.py` - Add settings table schema and helper functions
2. `app.py` - Add conditional check in `log_analytics()` function
3. `templates/admin/dashboard.html` or new settings page - Add toggle UI
4. `migrate_add_settings_table.py` - Migration script

## Cached Value Consideration

For performance, cache the setting value in memory instead of querying DB on every request:
- Load setting at app startup
- Reload when setting changes
- Store in global variable or Flask config
