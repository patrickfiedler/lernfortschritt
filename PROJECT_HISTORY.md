# Lernmanager Project History

## Overview

Lernmanager is a German-language learning progress tracker for schools that allows teachers to manage classes, students, and learning tasks, while students track their progress, complete subtasks, and take quizzes.

**Repository**: https://github.com/patrickfiedler/lernmanager

---

## Timeline

### 2025-12-23 | Project Inception
**Initial commit and setup**

- Created initial Flask application
- Basic class, student, and task management
- Implemented username/password generation system
- Added MIT license (later changed to AGPL-v3)

**Key Features:**
- Admin and student authentication
- Class and student management
- Task creation with subtasks
- Quiz functionality

---

### 2025-12-24 | Advanced Task System
**Multiple prerequisites and electives**

- Implemented task prerequisites system
- Added support for elective tasks
- Enhanced task dependency tracking

**Commits:**
- `expand username word lists and match student initials`
- `implement electives and multiple prerequisites`

---

### 2026-01-06 | Quiz Improvements
**Quiz randomization and UX enhancements**

Enhanced quiz system for better learning outcomes:
- Randomized question and answer order
- Hide correct answers in results (show only score)
- Improved subtask display

**Commits:**
- `randomize quiz question and answer order`
- `improve subtask display in student task view`
- `fix quiz key mismatch between JSON and templates`
- `hide correct answers in quiz results`

---

### 2026-01-07 | Security & Deployment Foundation
**Major security hardening and deployment setup**

Initial production deployment preparation:
- Removed plaintext passwords from database
- Implemented SQLCipher database encryption
- Added PDF credential generation for students
- Comprehensive security hardening
- Created deployment scripts and documentation
- Switched from Docker to systemd-based deployment

**Key Changes:**
- Password field removed from student table
- Added PDF credential generation with QR codes
- Deployed with systemd service management
- Git-based deployment workflow

**Commits:**
- `add deployment configuration files`
- `document git workflow in CLAUDE.md`
- `add comprehensive security hardening`
- `remove plaintext passwords, add PDF credentials and SQLCipher`
- `remove Docker files (using systemd deployment)`
- `update deploy script to use rsync instead of git`
- `add admin password change feature`

---

### 2026-01-07 | Markdown Support
**Enhanced content editing**

- Added markdown support for task descriptions
- Implemented markdown preview in subtask editor
- Improved content formatting capabilities

**Commits:**
- `add markdown support and improve subtask editing`
- `improve subtask editor with markdown preview`

---

### 2026-01-08 | Deployment Automation v1
**Automated deployment with rollback**

First major deployment system improvements:
- Redesigned deployment scripts with auto-rollback
- Added secret management (sed-based extraction/injection)
- Git ownership checks and error handling
- Improved reliability of updates

**Commits:**
- `redesign deployment scripts with auto-rollback and secret management`
- `fix setup.sh: set ownership before creating venv`
- `improve update.sh: add ownership checks and git error handling`

---

### 2026-01-09 | Bug Fixes & Improvements
**Student assessment and progress tracking**

Multiple improvements to student experience:
- Fixed task sorting and class assessment display
- Improved student progress tracking with attendance visibility
- Enhanced student assessment UI with schedule and navigation
- Database migration improvements (SQLCipher support)

**Commits:**
- `fix two bugs: task sorting and class assessment display`
- `fix update.sh service detection issue`
- `fix sqlcipher migration: skip internal sqlite_ objects`
- `improve student progress tracking: attendance visibility and grey-out`
- `implement student assessment improvements: schedule, navigation, manual save`

---

### 2026-01-11 | Dashboard Enhancements
**Schedule filtering and deployment improvements**

- Added dashboard filter to show only today's classes
- Further deployment script improvements

**Commits:**
- `add dashboard schedule filter: show only today's classes`

---

### 2026-01-12 | Analytics & Reporting System
**Comprehensive logging and PDF reports**

Major analytics infrastructure:
- Implemented unified analytics and activity logging
- Added error logging system with admin UI
- PDF report generation system
- Weekly report generation

**Key Features:**
- Page view tracking
- Error monitoring dashboard
- Automated PDF report generation
- Weekly progress reports

**Commits:**
- `implement error logging system with admin UI`
- `implement unified analytics and activity logging system`
- `implement PDF report generation (Phase 6)`
- `Add PDF report generation`
- `add weekly report generation system`

---

### 2026-01-13 | Performance & UX Improvements
**Subtask management enhancements**

Multiple improvements to subtask handling:
- Added performance benchmarking tools
- Implemented subtask-level assignment control
- Fixed Jinja2 template syntax errors
- Improved subtask display (number instead of "Aktuell")
- Added "Erledigt" label for better UX
- Fixed database locking during subtask toggles
- Added subtask anchor navigation

**Commits:**
- `add performance benchmarking tools`
- `fix benchmark scripts: correct static file path`
- `implement subtask-level assignment control`
- `fix Jinja2 template syntax error in student detail page`
- `fix: display subtask number instead of 'Aktuell' in badge`
- `improve: add 'Erledigt' label below checkbox for better UX`
- `fix: resolve database locking issue when toggling subtasks`
- `improve: remove unused self-evaluation and add subtask anchor navigation`

---

### 2026-01-14 | Documentation Milestone
**Project organization and archiving**

- Added comprehensive README
- Created archive system for completed planning files
- First documentation organization effort

**Commits:**
- `docs: add comprehensive README and archive completed planning files`

---

### 2026-01-15 | Performance Optimization Sprint
**Major performance improvements (3x faster)**

Comprehensive performance investigation and optimization:

**Problems Identified:**
- Slow dashboard loads (~1-2 seconds)
- Analytics logging blocking requests
- Inefficient database queries

**Solutions Implemented:**
1. **Async Logging** - 99% performance improvement
   - ThreadPoolExecutor for non-blocking logging
   - Queue-based approach for safety

2. **SQLite WAL Mode** - 70-75% faster database operations
   - Write-Ahead Logging enabled
   - Better concurrency

3. **Query Caching** - Flask-Caching for expensive queries
   - Dashboard queries cached
   - Analytics queries optimized

4. **Python Bytecode Caching** - Faster startup
   - PYTHONPYCACHEPREFIX in systemd service

**Results:**
- Dashboard load times: ~1s → ~200-300ms
- Logging overhead: nearly eliminated
- Better user experience overall

**Commits:**
- `feat: add activity logging performance benchmark tool`
- `fix: add database encryption support to benchmark script`
- `perf: enable SQLite WAL mode for 70-75% faster analytics logging`
- `docs: update performance analysis with production VPS benchmark results`
- `feat: implement async logging for 99% performance improvement`
- `docs: add async logging design documents and update investigation`
- `docs: mark performance investigation complete with production results`
- `perf: add PYTHONPYCACHEPREFIX to systemd service`
- `perf: implement comprehensive performance optimizations`
- `perf: add caching to remaining dashboard queries`

**Documentation:** See `docs/archive/2026-01_performance_optimization/`

---

### 2026-01-19 | Unterricht Page Rewrite
**Complete redesign of attendance/evaluation system**

Major overhaul of the teacher's attendance and evaluation (unterricht) interface:

**Problems:**
- Unclear what data was saved vs unsaved
- Confusing 1-2-3 rating scale
- No lesson-wide comments

**New Features:**
1. **New Rating System**
   - Changed from `1-2-3` to `-` (criticism), `ok` (neutral), `+` (praise)
   - Color-coded: red, yellow, green
   - Default to "ok" for neutral

2. **Manual Save Workflow**
   - Clear visual indicators for unsaved changes
   - Change tracking with counter
   - Single save button for all changes
   - Success feedback after save
   - Browser warning for unsaved changes

3. **Enhanced Commenting**
   - Lesson-wide comment field
   - Pre-defined comment dropdown (7 common German phrases)
   - Append functionality for quick input

**Database Changes:**
- Migrated rating columns from INTEGER to TEXT
- Added `unterricht.kommentar` column
- Created migration script with SQLCipher support

**Commits:**
- `feat: complete rewrite of unterricht page with new rating system`
- `chore: add database migration script for unterricht rating system`
- `fix: add SQLCipher support to migration script`

**Documentation:** See `docs/archive/2026-01_unterricht_rewrite/`

---

### 2026-01-19 | Logging System Toggle
**Admin control over page view logging**

Added settings page with toggle for page view logging:
- Admin can enable/disable logging via settings UI
- Fixed CSRF token handling in settings form
- Improved comment dropdown UX
- Fixed CSS styling issues

**Commits:**
- `feat: add admin toggle to disable page view logging`
- `fix: use hidden input for CSRF token in settings form`
- `improve: shorten dropdown label and sort comment options`
- `fix: correct CSS class names for rating buttons`
- `fix: move rating button styles to main stylesheet`

**Documentation:** See `docs/archive/2026-01_logging_system/`

---

### 2026-01-19 | Class Assignment Bug Fix
**Fixed subtask display issue**

Fixed bug where students saw "Keine Teilaufgaben definiert" after class-wide task assignment:
- Added fallback logic for invalid `current_subtask_id`
- Shows all subtasks when specific subtask doesn't exist

**Commits:**
- `fix: show all subtasks when current subtask doesn't exist`

**Documentation:** See `docs/archive/2026-01_class_assignment_bug/`

---

### 2026-01-20 | Student Experience Redesign
**Major UX improvements for student interface**

Complete redesign of student task view with focus on engagement and clarity:

**Design Process:**
- Created 3 mockup styles (clean minimal, warm friendly, bold focused)
- Implemented hybrid design combining best elements
- User-centered design approach

**New Features:**
1. **Purpose Banner** - "Why Learn This"
   - Added `why_learn_this` field to tasks
   - Displays prominently in student view
   - Helps students understand learning goals
   - Database migration with SQLCipher support

2. **Improved Navigation**
   - Previous/Next buttons for subtask navigation
   - Clear progress indicators
   - Better visual hierarchy

3. **Testing Infrastructure**
   - Comprehensive testing checklist created
   - Covers all aspects of redesign

**Commits:**
- `feat: add 'why_learn_this' field to tasks for student engagement`
- `feat: redesign student interface with hybrid mockup design`
- `docs: add comprehensive testing checklist for student redesign`

**Documentation:**
- See `docs/archive/2026-01_student_redesign/`
- Active: `student_redesign_roadmap.md` and `student_redesign_testing.md`

---

### 2026-01-26 | Subtask Navigation Enhancement
**Further UX improvements**

Added previous/next navigation buttons for easier subtask traversal:
- More intuitive navigation between subtasks
- Consistent with modern web UX patterns

**Commits:**
- `feat: improve subtask navigation with prev/next buttons`

---

### 2026-01-26 | Production Crisis & Resolution
**HTTPS redirect loop and missing migrations**

**Problem:**
Production server stopped working after deployment. Localhost worked fine.

**Root Causes:**
1. Missing database migration (`migrate_add_why_learn_this.py`)
2. HTTPS redirect loop - `SESSION_COOKIE_SECURE` enabled without HTTPS configured

**Investigation:**
- Traced through recent commits
- Identified that commit `06eb4af` was last known working
- Discovered migrations work on localhost but weren't run on production
- Found HTTPS configuration issue

**Solutions:**
1. **Migration Detection** - Led to automatic migration system (see next section)
2. **HTTPS Fix** - Changed from `FLASK_ENV=production` check to explicit `FORCE_HTTPS` env var
   - Allows HTTP operation by default
   - Opt-in for HTTPS after SSL setup
   - Prevents redirect loops

**Commits:**
- `fix: prevent redirect loop when HTTPS not configured`

**Documentation:** See `docs/archive/2026-01-26_production_debugging/`

---

### 2026-01-26 | Deployment System Overhaul
**EnvironmentFile secrets & automatic migrations**

Major deployment system improvements addressing critical weaknesses:

#### Problem 1: Fragile Secrets Management
Secrets were extracted from and injected into service file using brittle `sed` parsing:
```bash
SECRET_KEY=$(grep "SECRET_KEY=" ... | sed -n 's/.*"\(.*\)".*/\1/p')
sed -i "s/CHANGE_ME/$SECRET_KEY/" ...
```

**Risks:**
- Service file format changes could break extraction
- Secrets could be lost during updates
- Complex, error-prone code (~40 lines)

#### Problem 2: Manual Migrations
Database migrations had to be run manually after deployment, often forgotten (as happened in production crisis).

#### Solutions Implemented

**1. EnvironmentFile-Based Secrets**
- Moved secrets to `/opt/lernmanager/.env`
- Service file uses `EnvironmentFile=` directive (systemd best practice)
- Secrets persist across all service file updates
- Simple to modify: edit `.env`, restart service

**2. Automatic Migration Detection & Execution**
- `update.sh` detects changed migration files in commits
- Runs all `migrate_*.py` files automatically
- Exports `SQLCIPHER_KEY` from `.env` for encrypted databases
- Reports success/failure for each migration
- Continues deployment even if migrations fail (with warning)

**Impact:**
- Eliminated ~40 lines of complex sed logic
- Secrets never lost during updates
- Migrations never forgotten
- Safer, simpler deployments
- Follows systemd best practices

**Files Changed:**
- `deploy/lernmanager.service` - Uses `EnvironmentFile=/opt/lernmanager/.env`
- `deploy/setup.sh` - Creates `.env` with secrets (no injection)
- `deploy/update.sh` - Simplified secrets + Step 6: auto-migrations

**Documentation Created:**
- `DEPLOYMENT_IMPROVEMENTS_SUMMARY.md` - Complete overview
- `MIGRATION_GUIDE.md` - Migration instructions for existing deployments
- `MIGRATE_PRODUCTION.md` - Quick-start one-liner
- `deploy/QUICK_REFERENCE.md` - Common operations reference

**Commits:**
- `feat: improve deployment with EnvironmentFile secrets and auto-migrations`

**Documentation:** See `docs/archive/2026-01-26_deployment_improvements/`

---

## Major Milestones Summary

### Phase 1: Foundation (Dec 2025)
- ✅ Initial Flask application
- ✅ Core features (classes, students, tasks, quizzes)
- ✅ User authentication system

### Phase 2: Security & Production (Jan 2026 Week 1)
- ✅ Security hardening (removed plaintext passwords, SQLCipher)
- ✅ Deployment automation (systemd, git-based)
- ✅ PDF credential generation
- ✅ Markdown support

### Phase 3: Analytics & Monitoring (Jan 2026 Week 2)
- ✅ Unified analytics system
- ✅ Error logging dashboard
- ✅ PDF report generation
- ✅ Weekly reports

### Phase 4: Performance Optimization (Jan 2026 Mid)
- ✅ Async logging (99% improvement)
- ✅ SQLite WAL mode (70-75% faster)
- ✅ Query caching
- ✅ Bytecode optimization
- ✅ **Result: 3x faster application**

### Phase 5: UX Improvements (Jan 2026 Late)
- ✅ Unterricht page redesign (new rating system)
- ✅ Student interface redesign (navigation, purpose banners)
- ✅ Subtask management enhancements
- ✅ Admin logging toggle

### Phase 6: Deployment Excellence (Jan 2026 Latest)
- ✅ EnvironmentFile-based secrets management
- ✅ Automatic database migrations
- ✅ Production debugging and fixes
- ✅ Comprehensive deployment documentation

---

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLCipher encryption
- **Server**: Waitress (WSGI)
- **Deployment**: systemd service management

### Frontend
- **Templates**: Jinja2
- **Styling**: Custom CSS
- **JavaScript**: Vanilla JS for interactivity

### Performance
- **Caching**: Flask-Caching (SimpleCache)
- **Async**: ThreadPoolExecutor for logging
- **Database**: WAL mode enabled
- **Compression**: Flask-Compress (gzip)

### Development
- **VCS**: Git + GitHub
- **Deployment**: Git-based with auto-rollback
- **Documentation**: Markdown + comprehensive guides

---

## Current State (January 2026)

### Production Features
- ✅ Multi-class student management
- ✅ Task system with subtasks and quizzes
- ✅ Progress tracking and attendance
- ✅ Analytics and reporting
- ✅ PDF credential generation
- ✅ Encrypted database support
- ✅ Comprehensive admin dashboard
- ✅ Redesigned student interface
- ✅ Advanced deployment automation

### Performance Metrics
- Dashboard load time: ~200-300ms
- Logging overhead: <1ms (async)
- Database operations: 70-75% faster (WAL mode)
- Overall: 3x performance improvement from initial state

### Deployment
- Automated deployment with auto-rollback
- Automatic migration execution
- Persistent secrets management
- Production-tested and stable

---

## Future Roadmap

See `future_features_plan.md` and `student_redesign_roadmap.md` for detailed plans.

### Planned Features
- Game-like learning progression
- Enhanced quiz types
- Mobile-responsive design improvements
- Additional analytics dashboards
- Parent access portal

---

## Documentation

### For Users & Admins
- `README.md` - Project overview
- `docs/guides/MIGRATION_GUIDE.md` - Deployment migration
- `docs/guides/MIGRATE_PRODUCTION.md` - Quick migration
- `deploy/QUICK_REFERENCE.md` - Common operations

### For Developers
- `CLAUDE.md` - AI assistant instructions
- `docs/README.md` - Documentation index
- `docs/archive/` - Historical implementation docs
- `PROJECT_HISTORY.md` - This file

### For Deployment
- `deploy/setup.sh` - Initial server setup
- `deploy/update.sh` - Update deployment
- `deploy/lernmanager.service` - systemd service
- `DEPLOYMENT_IMPROVEMENTS_SUMMARY.md` - Deployment system overview

---

## Statistics

**Total Commits**: 80+
**Major Features**: 15+
**Bug Fixes**: 20+
**Performance Improvements**: 5 major initiatives
**Documentation Files**: 50+
**Active Development Period**: December 2025 - January 2026

---

## Contributors

- Patrick Fiedler (@patrickfiedler)
- Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

---

## License

AGPL-v3 (GNU Affero General Public License v3.0)

---

*This document tracks the complete history of the Lernmanager project from inception to current state. For archived documentation of specific features and investigations, see `docs/archive/`.*
