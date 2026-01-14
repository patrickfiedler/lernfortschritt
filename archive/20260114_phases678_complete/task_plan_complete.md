# Task Plan: Multiple Feature Implementations

## Goal
Implement remaining features from todo.md plus enhance the class schedule system with smart dashboard filtering.

## User Requirements

### 1. Date Picker Format (Quick Win)
- Change from US format (mm/dd/yyyy) to German format (dd.mm.yyyy)
- Apply to admin's student assessment page date picker

### 2. Dashboard Schedule Filter (New Feature)
- "Unterricht heute" section should only show classes with scheduled lessons TODAY
- Use the class_schedule system we just implemented
- Filter based on current weekday (Monday=0, Sunday=6)

### 3. Error Logging
- Track and log application errors
- Determine: storage location, rotation policy, detail level

### 4. Usage Analytics
- Track users and page calls
- Consider GDPR compliance
- Determine: which metrics, storage method

### 5. Student Progress Reports (PDF)
- Generate PDF reports per class
- Determine: content, permissions, format

### 6. Update Planning Files
- Update future_features_plan.md to reflect completed items
- Clean up todo.md

## Phases

- [x] Phase 1: Explore current implementation and plan approach
- [x] Phase 2: Quick win - Change date picker to German format
- [x] Phase 3: Implement dashboard schedule filter
- [x] Phase 4: Design and implement error logging system
- [x] Phase 5: Design and implement usage analytics & activity logging
- [x] Phase 6: Design and implement PDF report generation
- [x] Phase 7: Update and clean up planning files
- [x] Phase 8: Test all features
- [x] Phase 9: Deploy and verify
- [x] Phase 10: Clean up repository files and remove unused files from git tracking
- [x] Phase 11: Create updated README.md for GitHub
- [ ] **Ongoing**: Archive planning files after phase completion (never marks complete)

## Key Questions

### Date Picker Format
1. Where is the date picker currently used? (unterricht page confirmed, anywhere else?)
2. HTML5 date input or custom widget?
3. Display format vs data format?

### Dashboard Schedule Filter
1. Which route handles the admin dashboard?
2. How is "Unterricht heute" data currently fetched?
3. Should we show a message if no classes scheduled today?
4. What about classes without a schedule set - show or hide?

### Error Logging
1. Log to file or database?
2. Rotation policy (daily, weekly, size-based)?
3. Detail level (stack traces, user context, request info)?
4. Who can view logs (admin only)?
5. Integration with Python logging module?

### Usage Analytics
1. Which metrics to track?
   - Page views per route?
   - User login/logout?
   - Feature usage (quiz taken, task completed)?
   - Session duration?
2. Storage: database table or log files?
3. GDPR: anonymize IP addresses?
4. Retention period?
5. Admin dashboard for viewing analytics?

### PDF Reports
1. Content structure:
   - Class overview (students, tasks)?
   - Individual student progress?
   - Time period selection?
   - Quiz results?
2. PDF library: ReportLab, WeasyPrint, or xhtml2pdf?
3. Permissions: admin only or students too?
4. Download vs email?
5. Template design?

## Decisions Made

### Phase 1: Analysis Complete

**Date Picker (USER CHOICE):**
- ✅ Keep HTML5 date input (simple, browser-native)
- Verify lang="de" is set in base.html
- Browser will respect locale settings

**Dashboard Filter (USER CHOICE):**
- ✅ Filter classes to show only those with schedule matching today's weekday
- ✅ Hide classes without schedules completely
- ✅ Show message "Keine Unterrichtsstunden heute geplant" when no classes scheduled
- Route: `app.py:113-116` admin_dashboard()
- Template: `templates/admin/dashboard.html:30-41`

**Error Logging:**
- Use database table approach (best for school context)
- Self-hosted for data privacy
- Include: timestamp, level, message, traceback, user_id, route
- 30-day retention with automatic cleanup
- Admin-only UI to view errors

**Usage Analytics:**
- Single `analytics_events` table with JSON metadata
- Track: page views, logins, quiz completions, task completions
- No IP addresses (GDPR-friendly)
- 90-day retention
- Admin dashboard for aggregated stats

**PDF Reports:**
- Use WeasyPrint (HTML/CSS to PDF)
- Can reuse existing templates
- Need user input on report content before implementation

## Implementation Order

1. **Phase 1**: Exploration and planning
2. **Phase 2**: Date picker format (quick win, builds confidence)
3. **Phase 3**: Dashboard filter (extends recent schedule work)
4. **Phase 4**: Error logging (high priority, foundational)
5. **Phase 5**: Usage analytics (builds on logging infrastructure)
6. **Phase 6**: PDF reports (most complex, saved for last)
7. **Phase 7**: Cleanup planning files
8. **Phase 8-9**: Testing and deployment

## Progress Updates

### Phase 2 Summary - Date Picker Format ✅
- Verified `lang="de"` is set in base.html (line 2)
- HTML5 date input will use German formatting based on browser locale
- No code changes needed - already configured correctly

### Phase 3 Summary - Dashboard Schedule Filter ✅
- Modified `app.py:113-125` admin_dashboard() route
- Added import: `from datetime import date, datetime`
- Filter logic: Get today's weekday, check each class schedule, only include matches
- Updated `templates/admin/dashboard.html:30-43`
- Changed to use `klassen_heute` instead of `klassen`
- Added empty state message: "Keine Unterrichtsstunden heute geplant"
- Card always visible, shows message when no classes scheduled today

### Phase 4 Summary - Error Logging System ✅
**Database Schema:**
- Added `error_log` table to models.py:323-341
- Columns: id, timestamp, level, message, traceback, user_id, user_type, route, method, url
- Added index on timestamp for efficient retrieval

**Model Functions (models.py:1173-1261):**
- `log_error()` - Log errors to database with try/catch to prevent logging failures
- `get_error_logs()` - Retrieve logs with pagination and level filtering
- `get_error_log_count()` - Count total errors (for pagination)
- `get_error_log_stats()` - Get statistics (today, week, by level)
- `cleanup_old_error_logs()` - Delete logs older than N days (default 30)
- `clear_all_error_logs()` - Delete all logs

**Error Handlers (app.py:969-1032):**
- Added `traceback` import
- `get_current_user_info()` - Helper to extract user context from session
- `@app.errorhandler(400)` - Log bad requests with WARNING level
- `@app.errorhandler(403)` - Log forbidden access with WARNING level
- `@app.errorhandler(404)` - Show error page (not logged to avoid noise)
- `@app.errorhandler(500)` - Log internal errors with ERROR level
- `@app.errorhandler(Exception)` - Catch all unhandled exceptions with CRITICAL level

**Admin UI:**
- Route: `/admin/errors` - View logs with pagination (50 per page)
- Route: `/admin/errors/clear` - Clear all logs (POST with confirmation)
- Template: `templates/admin/errors.html` - Statistics cards, level filtering, detailed view with traceback toggle
- Navigation: Added "Fehlerprotokolle" link to admin nav in base.html:22
- Generic error page: `templates/error.html` for 404s

**Features:**
- Statistics dashboard (today, week, by level)
- Filter by level (CRITICAL, ERROR, WARNING)
- Pagination for large log sets
- Expandable traceback details
- Auto-cleanup on page view (30 days retention)
- Manual "Clear all" button
- No IP addresses or request data (privacy-first)
- Logged context: user_id, user_type, route, method, URL

**Testing:**
- Tested with ZeroDivisionError - logged successfully as CRITICAL
- Verified database storage and retrieval
- Confirmed error handlers redirect correctly

### Phase 5 Summary - Analytics & Activity Logging ✅
**Unified System:** Single solution for both usage analytics and student activity tracking

**Database Schema:**
- Added `analytics_events` table to models.py:346-363
- Columns: id, timestamp, event_type, user_id, user_type, metadata (JSON)
- Three indexes: timestamp, user+timestamp, event_type+timestamp
- 210-day retention (covers one school term)

**Model Functions (models.py:1286-1589):**
- `log_analytics_event()` - Log any event with flexible metadata
- `get_analytics_events()` - Retrieve with filtering (type, user, date range) and pagination
- `get_analytics_count()` - Count events for pagination
- `get_analytics_overview()` - Dashboard statistics (active users, page views, tasks, popular routes, active students)
- `get_student_activity_log()` - Individual student activity
- `get_student_activity_summary()` - Aggregate stats for reports (event counts, login days, tasks completed)
- `cleanup_old_analytics_events()` - 210-day automatic cleanup
- `clear_all_analytics_events()` - Manual clear all

**Event Tracking:**

*Automatic (Middleware - app.py:1073-1118):*
- `page_view` - All authenticated page views
- Filters: /static/, /favicon.ico, /admin/analytics, /admin/errors, /download routes

*Manual Logging:*
- `login` - User login (app.py:88, 103)
- `file_download` - Material downloads (app.py:552) with filename and material_id
- `subtask_complete` - When student checks off subtask (app.py:856)
- `task_complete` - Task fully completed (app.py:870, 960)
- `quiz_attempt` - Quiz taken (app.py:943) with score, percentage, pass/fail

**Admin UI:**
- Route: `/admin/analytics` - Overview dashboard
- Template: `templates/admin/analytics.html`
  - Cards: Active users today/week, page views, tasks completed
  - Tables: Most active students (clickable to activity log), popular pages
  - Event type breakdown

- Route: `/admin/analytics/student/<id>` - Individual activity log
- Template: `templates/admin/student_activity.html`
  - Summary cards: Login days, tasks, quizzes, downloads
  - Date range filtering (from/to)
  - Paginated activity timeline (50 per page)
  - Event badges with details (login, page views, downloads, subtasks, tasks, quizzes)
  - Quiz details show score and pass/fail

- Navigation: Added "Aktivität" link to admin menu (base.html:22)

**Privacy & GDPR:**
- Educational purpose justification
- No IP addresses or sensitive browsing patterns
- 210-day retention = one school term
- Transparent logging (students/parents can see activity)
- Individual tracking for legitimate educational assessment
- Foundation for progress reports (Phase 6)

**Benefits:**
- ✅ Track platform usage (admin analytics)
- ✅ Monitor student engagement (activity logs)
- ✅ Identify active/inactive students
- ✅ Data for parent-teacher conferences
- ✅ Foundation for PDF progress reports
- ✅ Evidence of learning activity
- ✅ Identify popular/unpopular materials

**Design Decisions:**
- 210 days (not 90) - covers full school term + buffer
- Unified table (not separate) - simpler, more flexible
- Hybrid capture (middleware + manual) - complete coverage
- JSON metadata - flexible event data without schema changes
- Separate event types - easy filtering and analysis

### Phase 7 Summary - Update and Clean Up Planning Files ✅
**Actions Taken:**
- Updated `todo.md`: Marked completed features (error logging, analytics, class schedule)
- Updated `future_features_plan.md`: Added all completed phases with commit references
- Organized remaining work into clear priorities
- Struck through completed bugs and features

**Files Updated:**
- `todo.md`: Marked 8 items as complete
- `future_features_plan.md`: Added 5 completed items with commit hashes, reorganized priorities

**Remaining Work (from todo.md):**
- PDF progress reports (Phase 6)
- Student view improvements (future)
- Admin improvements (future)

### Phase 6 Summary - PDF Report Generation ✅

**User Requirements:**
1. Class report: Simple student list with task status (table format)
2. Student report: Admin chooses Summary (default) or Complete report
3. Access method: Buttons on class/student pages
4. Student access: Yes - students can download own summary report
5. Weekly reports: Infrastructure ready (auto-generation can be added via cron later)

**Implementation Complete:**

**Database Schema (models.py:365-386):**
- Added `saved_reports` table with fields: id, report_type, klasse_id, student_id, date_generated, date_from, date_to, filename
- Indexes on klasse_id and student_id for efficient retrieval

**Model Functions (models.py:1614-1812):**
- `save_report_record()` - Save generated report metadata
- `get_saved_reports()` - Retrieve saved reports by class or student
- `delete_old_saved_reports()` - Cleanup old reports (365 days default)
- `get_report_data_for_class()` - Aggregate class data for PDF
- `get_report_data_for_student()` - Aggregate student data for PDF (summary or complete)

**PDF Generation Functions (utils.py:303-820):**
- `generate_class_report_pdf()` - Class progress report with student table, statistics, task status
- `generate_student_report_pdf()` - Admin version with summary or complete option
- `generate_student_self_report_pdf()` - Student-facing version with **positive framing**
  - Progress-focused language: "Du hast...", "Dein Fortschritt..."
  - Encouraging messages based on activity
  - Metrics: Active learning days, tasks completed, current task progress
  - Quiz data with positive framing (shows passes only)
  - Motivational footer: "Jeder Schritt bringt dich weiter. Bleib dran!"

**Routes (app.py):**
- `/admin/klasse/<id>/bericht` - Download class report (lines 201-227)
- `/admin/schueler/<id>/bericht?type=summary|complete` - Download student report (lines 362-400)
- `/schueler/bericht` - Student self-report download (lines 947-980)
- Logs report downloads in analytics

**UI Updates:**
- `templates/admin/klasse_detail.html:10` - Added "📊 Klassenbericht" button
- `templates/admin/schueler_detail.html:9-13` - Added "Aktivität" button and two report buttons (Summary/Vollständig)
- `templates/student/dashboard.html:6-9` - Added "📊 Mein Lernfortschritt" button

**Pedagogical Considerations:**
- Student reports use progress-focused language (not evaluative)
- Simple key metrics that enable self-reflection
- Positive framing for quiz data (shows passes, improvements)
- Encouragement based on actual progress
- Builds confidence and ownership of learning

**Features:**
- ✅ Class reports with student list, progress, and statistics
- ✅ Admin student reports (summary or complete with activity log)
- ✅ Student self-reports with positive, confidence-building language
- ✅ All reports use German text and proper formatting
- ✅ PDF generation uses ReportLab (no new dependencies)
- ✅ Responsive buttons in templates for easy access
- ✅ Infrastructure ready for weekly report automation

## Status
**ALL PHASES COMPLETE** - Project fully documented and ready
**Task complete!** All planned features implemented, tested, deployed, and documented.

### Phase 11 Summary - README.md Created ✅
**Content Includes:**
- Project overview and feature list (teacher and student perspectives)
- Technology stack and architecture
- Installation instructions (local, Docker, production)
- Automated deployment process documentation
- Project structure and database schema
- Recent updates section highlighting January 2026 features
- Configuration and security information
- Development workflow
- Contributing and attribution

### Phase 10 Summary - Repository Cleanup ✅
**Actions Taken:**
- Created archive folder: `archive/20260114_phases678_complete/`
- Archived 14 completed planning files:
  - PDF report fix plan and notes
  - Performance optimization research (notes, plan, QA, recommendations)
  - Subtask advancement bugfix plan and notes
  - Subtask assignment implementation files (notes, plan, diagram, summary)
  - Student assessment completion plan
  - Test results documentation
- Updated `.gitignore`:
  - Added `instance/` (Flask instance folder)
  - Added `test_*.py` (test scripts pattern)
- Result: Clean repository with only active planning files in root
