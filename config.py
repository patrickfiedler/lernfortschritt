import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# SECRET_KEY is required in production
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('FLASK_ENV') == 'production':
        print("ERROR: SECRET_KEY environment variable is required in production!", file=sys.stderr)
        print("Generate one with: python3 -c \"import secrets; print(secrets.token_hex(32))\"", file=sys.stderr)
        sys.exit(1)
    else:
        # Development fallback - insecure but convenient
        SECRET_KEY = 'dev-secret-key-not-for-production'
        print("WARNING: Using insecure development SECRET_KEY. Set SECRET_KEY env var for production.", file=sys.stderr)
DATABASE = os.path.join(BASE_DIR, 'data', 'mbi_tracker.db')
# Store uploads outside static/ to require authentication for access
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'instance', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Subject and level options
SUBJECTS = ['Englisch', 'Chemie', 'MBI', 'Geographie']
LEVELS = ['5/6', '7/8', '9/10', '11s', '11/12']
