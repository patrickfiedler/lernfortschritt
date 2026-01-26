# Solution: NS_ERROR_REDIRECT_LOOP Fix

## Problem
The application was experiencing an infinite redirect loop when accessed on the VPS because:
1. `FLASK_ENV=production` was set in the systemd service
2. This triggered `SESSION_COOKIE_SECURE = True` in app.py
3. The site was accessed over HTTP (HTTPS not configured yet)
4. Browser couldn't save session cookies (they require HTTPS when SECURE flag is set)
5. Every request appeared unauthenticated, causing redirects to /login

## Solution Implemented

### Changes Made

**1. app.py (lines 23-28)**
- Changed from `FLASK_ENV` check to explicit `FORCE_HTTPS` environment variable
- SESSION_COOKIE_SECURE now only enabled when FORCE_HTTPS is explicitly set
- This prevents the redirect loop when HTTPS isn't configured yet

**Before:**
```python
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True
```

**After:**
```python
if os.environ.get('FORCE_HTTPS', '').lower() in ('true', '1', 'yes'):
    app.config['SESSION_COOKIE_SECURE'] = True
```

**2. deploy/lernmanager.service (lines 11-16)**
- Added commented-out FORCE_HTTPS environment variable
- Added clear instructions to uncomment after HTTPS is configured

**3. deploy/setup.sh (line 237)**
- Updated Next Steps to include enabling FORCE_HTTPS after certbot setup

## Deployment Instructions

### For Existing VPS (Immediate Fix)

1. **Update the code:**
   ```bash
   cd /opt/lernmanager
   sudo -u lernmanager git pull origin main
   ```

2. **Restart the service:**
   ```bash
   sudo systemctl restart lernmanager
   ```

3. **Verify it works:**
   - Access the site over HTTP - should work now
   - Login should succeed without redirect loop

4. **When ready to enable HTTPS:**
   ```bash
   # Set up certbot
   sudo certbot --nginx -d YOUR_DOMAIN

   # Enable FORCE_HTTPS
   sudo nano /etc/systemd/system/lernmanager.service
   # Uncomment: Environment="FORCE_HTTPS=true"

   # Reload and restart
   sudo systemctl daemon-reload
   sudo systemctl restart lernmanager
   ```

### For New Installations

The fix is already included in the setup script. After running setup:
1. The app will work over HTTP immediately
2. After configuring HTTPS with certbot, uncomment FORCE_HTTPS
3. Restart the service to enable secure cookies

## Testing

**Test over HTTP (before HTTPS):**
- Should be able to login successfully
- Session should persist across page loads
- No redirect loops

**Test over HTTPS (after certbot + FORCE_HTTPS):**
- Should be able to login successfully
- Cookies only sent over HTTPS (more secure)
- Still no redirect loops

## Why This Fix Is Better

1. **Explicit control:** FORCE_HTTPS clearly indicates HTTPS requirement
2. **Safe defaults:** Works over HTTP by default, secure over HTTPS when configured
3. **No deployment surprises:** Won't break when deploying without HTTPS
4. **Production-ready:** Can still run in production mode without HTTPS requirement
5. **Security when ready:** Easy to enable HTTPS-only cookies when SSL is configured
