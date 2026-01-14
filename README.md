# Lernmanager

A German-language learning progress tracker for schools. Teachers manage classes, students, and learning tasks, while students track their progress, complete subtasks, and take quizzes.

**Live Demo:** [lernen.mrfiedler.de](https://lernen.mrfiedler.de) (if available)

## Features

### For Teachers (Admin)

- **Class Management**
  - Create and manage classes with schedules
  - Batch import students (simple "Nachname, Vorname" format)
  - Auto-generated student credentials (e.g., "happypanda" / "bacado42")

- **Task Management**
  - Create learning tasks with subtasks and materials
  - Attach files and links as learning materials
  - Build interactive quizzes with multiple-choice questions
  - Assign tasks to entire classes or individual students
  - Assign specific subtasks (not just entire tasks)

- **Progress Tracking**
  - Dashboard with today's scheduled classes
  - View student progress in real-time
  - Track task completion and quiz results
  - Lesson attendance and evaluation system

- **Analytics & Reports** (NEW)
  - **Error Logging**: Track application errors with detailed tracebacks (30-day retention)
  - **Usage Analytics**: Monitor platform usage, active users, and popular pages
  - **Activity Logs**: Individual student activity tracking (210-day retention)
  - **PDF Reports**:
    - Class progress reports (student list with task status)
    - Individual student reports (summary or complete with activity log)
    - Export for parent-teacher conferences

### For Students

- **Task Completion**
  - View assigned tasks with clear progress indicators
  - Complete subtasks step-by-step (see only current subtask)
  - Access learning materials (files and links)
  - Take quizzes (80% pass threshold)

- **Progress Reports** (NEW)
  - Download personal progress reports (PDF)
  - Positive, encouraging language focused on growth
  - View learning days, completed tasks, and quiz scores

## Technology Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite with SQLCipher encryption
- **Server**: Waitress WSGI server
- **PDF Generation**: ReportLab
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Deployment**: systemd service, automated deployment scripts

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/patrickfiedler/lernmanager.git
cd lernmanager
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Run development server:
```bash
python app.py
```

The app will be available at `http://localhost:5000`

### Docker

```bash
docker compose up --build
```

### Production Deployment

**One-command setup:**
```bash
curl -sSL https://raw.githubusercontent.com/patrickfiedler/lernmanager/main/deploy/setup.sh | sudo bash
```

This automatically:
- Creates lernmanager user
- Clones repository
- Sets up Python virtual environment
- Generates secure SECRET_KEY
- Configures systemd service
- Starts the application

**Updates:**
```bash
ssh user@server 'sudo /opt/lernmanager/deploy/update.sh'
```

The update script:
- Pulls latest code from GitHub
- Detects and installs new dependencies
- Updates systemd service if needed
- Restarts application
- Automatically rolls back on failure

## Project Structure

```
lernmanager/
├── app.py              # Main Flask application with routes
├── models.py           # Database layer (SQLite with raw SQL)
├── config.py           # Configuration constants
├── utils.py            # Helper functions (username/password generators, PDF generation)
├── run.py              # Production server entry point
├── templates/
│   ├── admin/          # Teacher interface templates
│   └── student/        # Student interface templates
├── static/
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── uploads/        # User-uploaded materials
├── deploy/
│   ├── setup.sh        # Initial server setup script
│   └── update.sh       # Update deployment script
└── data/               # SQLite database (gitignored)
```

## Database Schema

Key tables:
- `admin` - Teacher accounts
- `klasse` - Classes
- `student` - Student accounts
- `task` - Learning tasks with optional quizzes
- `subtask` - Task subdivisions
- `material` - Files and links attached to tasks
- `student_task` - Task assignments (many-to-many)
- `unterricht` - Lesson attendance/evaluation
- `analytics_events` - Usage analytics and activity tracking (210-day retention)
- `error_log` - Application error logging (30-day retention)
- `saved_reports` - PDF report metadata

## Recent Updates

### January 2026 - Major Feature Release

- **German Date Format**: Date pickers now use dd.mm.yyyy format
- **Smart Dashboard**: "Unterricht heute" now shows only classes scheduled for today
- **Error Logging System**: Complete error tracking with admin UI, 30-day retention
- **Analytics & Activity Tracking**: Unified system for usage stats and student progress (210-day retention)
- **PDF Report Generation**: Class and student progress reports with positive framing
- **Subtask-Level Assignment**: Assign specific subtasks, not just entire tasks
- **Bugfixes**: Subtask auto-advancement, database locking issues

## Configuration

### Environment Variables

- `SECRET_KEY` - Flask secret key (auto-generated in production)
- `FLASK_ENV` - Set to `development` for debug mode

### Key Settings (config.py)

- Database path: `data/lernmanager.db`
- Upload folder: `static/uploads`
- Max file size: 16MB
- Subjects: Informatik, Mathematik, Naturwissenschaft, Deutsch, Englisch, etc.
- Levels: Stufe 1-10

## Security

- Password-based authentication (no OAuth)
- Session-based authorization with role decorators
- SQLCipher database encryption
- No IP address logging (GDPR-friendly)
- 210-day data retention for analytics
- Upload file type restrictions

## Development Workflow

1. Work on **main** branch
2. Commit and push to GitHub
3. SSH to server and run update script
4. Changes deployed automatically

## Contributing

This is a personal project for educational use. Feel free to fork and adapt for your needs.

## License

[Add license information]

## Author

Patrick Fiedler
- GitHub: [@patrickfiedler](https://github.com/patrickfiedler)

## Acknowledgments

Built with Claude Code for efficient development and testing.
