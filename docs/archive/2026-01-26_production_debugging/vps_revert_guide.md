# VPS Revert Guide

## If You Want to Revert the Latest Changes

### Option 1: Revert to Previous Commit (Recommended)

This reverts to the commit before the redirect loop fix:

```bash
# SSH to your VPS
ssh user@your-vps

# Navigate to app directory
cd /opt/lernmanager

# Switch to the lernmanager user context
sudo -u lernmanager git log --oneline -5
# This shows recent commits - note the commit hash you want

# Revert to the commit BEFORE the fix (fe60b86)
sudo -u lernmanager git checkout fe60b86

# Restart the service
sudo systemctl restart lernmanager
```

### Option 2: Revert Using Git Reset (More Permanent)

If you want to permanently roll back:

```bash
cd /opt/lernmanager

# Reset to previous commit
sudo -u lernmanager git reset --hard fe60b86

# Restart service
sudo systemctl restart lernmanager
```

### Option 3: Manual Fix Without Git

If you just want to fix the redirect issue without updating code:

```bash
# Edit the systemd service file
sudo nano /etc/systemd/system/lernmanager.service

# Find this line:
#   Environment="FLASK_ENV=production"
# Change it to:
#   Environment="FLASK_ENV=development"
# OR comment it out with #

# Save and exit (Ctrl+X, Y, Enter)

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart lernmanager
```

## To Return to Latest Code

After reverting, if you want to go back to the latest version:

```bash
cd /opt/lernmanager
sudo -u lernmanager git checkout main
sudo -u lernmanager git pull origin main
sudo systemctl restart lernmanager
```

## Commit Reference

- `da542cf` - Latest (redirect loop fix)
- `fe60b86` - Previous (subtask navigation improvements)
- `876a50b` - Before that (testing checklist)

## Which Option to Choose?

- **Option 1 (checkout)**: Temporary revert, easy to go back
- **Option 2 (reset)**: Permanent revert, use if you're sure
- **Option 3 (manual)**: Quick fix without changing code version

## After Reverting

If you reverted because of issues, please let me know:
1. What error you encountered
2. Which revert method you used
3. Whether the revert fixed the issue

This helps me understand what went wrong and provide a better fix.
