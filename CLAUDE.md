# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lernmanager is a German-language learning progress tracker for schools. It allows teachers (admins) to manage classes, students, and learning tasks, while students can track their progress on assigned tasks, complete subtasks, and take quizzes.

**Repository**: https://github.com/patrickfiedler/lernmanager

## Commands

### Development
```bash
# Run development server (port 5000, debug mode)
python app.py

# Run production server with waitress (port 8080)
python run.py
```

### Docker
```bash
docker compose up --build
```

### Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Core Files
- `app.py` - Flask application with all routes. Two user types: admin (teachers) and student. Uses session-based auth with `@admin_required` and `@student_required` decorators.
- `models.py` - SQLite database layer with raw SQL queries. Uses `db_session()` context manager for transactions.
- `config.py` - Configuration constants (database path, upload settings, subjects/levels).
- `utils.py` - Username/password generators for student accounts.

### Database Schema (SQLite)
Key tables: `admin`, `klasse` (class), `student`, `task` (learning task with optional quiz), `subtask`, `material` (links/files), `student_task` (per-class assignment), `unterricht` (lesson attendance/evaluation).

Student-class is many-to-many. Each student has one active task per class. Tasks can have subtasks and quizzes (JSON in `quiz_json` column).

### Template Structure
- `templates/admin/` - Teacher interface (class/student/task management, lesson tracking)
- `templates/student/` - Student interface (task progress, quiz taking, self-evaluation)

### Data Flow
1. Admin creates classes and tasks with subtasks/materials/quizzes
2. Admin adds students to classes (batch input: "Nachname, Vorname" per line)
3. Admin assigns tasks to individual students or entire classes
4. Students complete subtasks and take quizzes (80% to pass)
5. Task auto-completes when all subtasks done + quiz passed (or admin manual override)

## Deployment

### Initial Server Setup
- Run `deploy/setup.sh` on the server (once per server)
- Automated one-command setup: `curl -sSL https://raw.githubusercontent.com/patrickfiedler/lernmanager/main/deploy/setup.sh | sudo bash`
- Auto-generates SECRET_KEY and stores in systemd service
- Creates lernmanager user, clones repo, sets up venv, starts service

### Updates
- Run `deploy/update.sh` on server after pushing to GitHub
- Usage: `ssh user@server 'sudo /opt/lernmanager/deploy/update.sh'`
- Auto-detects changes in requirements.txt and systemd service
- Preserves secrets across updates
- Automatically rolls back if service fails to start

### Git Workflow
- Work directly on **main** branch
- Commit and push changes to GitHub
- SSH to server and run update.sh
- The update script will pull latest code and restart service

## Conventions

- German terminology in code: Klasse (class), Schüler (student), Aufgabe (task), Teilaufgabe (subtask)
- Student usernames are auto-generated (adjective+animal, e.g., "happypanda")
- Student passwords follow cvcvcvnn pattern (e.g., "bacado42")
- Quiz JSON format: `{"questions": [{"text": "...", "options": ["..."], "correct": [0, 1]}]}`

## Common Issues and Solutions

### Template Block Structure
Jinja2 templates use `{% block scripts %}` and `{% block content %}` inheritance. The base template wraps `scripts` block with `<script>` tags. Never add additional `<script>` tags inside the block - this creates nested tags and breaks JavaScript execution.

### Browser Caching After AJAX Save
When saving via AJAX and reloading to show updated data, use cache-busting to prevent stale data: `window.location.href = url + '?_t=' + Date.now()` instead of `location.reload()`. This forces fresh data fetch.

### Unsaved Changes Detection
When tracking form state with `beforeunload` event listener, always update `initialState` after successful save and before reload to prevent false unsaved changes warnings.

### Static File Caching Strategy
Flask serves static files (CSS, JS) with aggressive browser caching. Changes to CSS/JS files may not appear even after CTRL+F5.

**Solution**: Add version parameter to static file URLs in templates:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}?v=YYYYMMDDNN">
```

**When to increment version**:
- After any CSS or JS file changes
- Use date + sequence number format (e.g., `?v=2026012702`)
- Update version in both `base.html` and `login.html`

**Note**: Future improvement tracked in todo.md - replace with proper Cache-Control headers for cleaner solution.

**See**: `frontend_patterns.md` for detailed patterns and examples
