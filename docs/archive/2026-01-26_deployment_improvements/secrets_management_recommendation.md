# Secrets Management Recommendation

## Executive Summary

**Current Problem**: When the systemd service file is updated, secrets must be extracted from the old file and injected into the new one. This is brittle and error-prone.

**Recommended Solution**: Use systemd's `EnvironmentFile=` directive to load secrets from a separate file that never changes during updates.

---

## Recommended Approach: EnvironmentFile=

### What Changes

**1. Create persistent secrets file** (`/opt/lernmanager/.env`)
```bash
# /opt/lernmanager/.env
SECRET_KEY=<generated-value>
SQLCIPHER_KEY=<generated-value>
FORCE_HTTPS=true
FLASK_ENV=production
```

**2. Update systemd service file** (`deploy/lernmanager.service`)
```ini
[Service]
Type=simple
User=lernmanager
Group=lernmanager
WorkingDirectory=/opt/lernmanager

# Load secrets from file (never changes during updates)
EnvironmentFile=/opt/lernmanager/.env

# Non-secret environment variables (can stay here or move to .env)
Environment="TMPDIR=/opt/lernmanager/instance/tmp"
Environment="PYTHONPYCACHEPREFIX=/opt/lernmanager/instance/tmp"

ExecStart=/opt/lernmanager/venv/bin/python run.py
```

**3. Update setup.sh**
- Generate secrets and write to `/opt/lernmanager/.env`
- Set permissions: `chmod 600`, `chown root:root`
- Copy service file as-is (no sed injection needed)

**4. Update update.sh**
- Remove secret extraction logic (lines 230-255)
- Simply copy new service file (no modification needed)
- Secrets persist in `.env` file automatically

---

## Benefits

### For You
✅ **Service file is now a template** - no secret injection needed
✅ **Updates are safer** - secrets can't be lost during updates
✅ **Easy to modify secrets** - just edit `/opt/lernmanager/.env`
✅ **Add new secrets easily** - just add lines to `.env` file
✅ **Cleaner code** - no complex sed parsing in update.sh

### Technical
✅ **Standard systemd feature** - well-documented, battle-tested
✅ **Separation of concerns** - config vs secrets
✅ **No app code changes** - works with existing Flask code
✅ **Backwards compatible** - can support both methods during transition

---

## Implementation Changes Required

### File: `deploy/lernmanager.service`

**Remove**:
```ini
Environment="SECRET_KEY=CHANGE_ME_TO_RANDOM_STRING"
Environment="FLASK_ENV=production"
# Environment="SQLCIPHER_KEY=CHANGE_ME_TO_RANDOM_STRING"
```

**Add**:
```ini
# Load environment variables (including secrets) from file
EnvironmentFile=/opt/lernmanager/.env
```

**Keep**:
```ini
# Non-secret variables can stay in service file
Environment="TMPDIR=/opt/lernmanager/instance/tmp"
Environment="PYTHONPYCACHEPREFIX=/opt/lernmanager/instance/tmp"
```

Or move ALL environment variables to `.env` for consistency.

---

### File: `deploy/setup.sh`

**Replace secret generation section** (lines 150-168):

**OLD**:
```bash
# Generate SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Save to .secrets file
SECRET_FILE="$APP_DIR/.secrets"
echo "SECRET_KEY=$SECRET_KEY" > "$SECRET_FILE"
chmod 600 "$SECRET_FILE"
chown root:root "$SECRET_FILE"

# Inject into service file
cp "$APP_DIR/deploy/lernmanager.service" "$SYSTEMD_SERVICE"
sed -i "s/CHANGE_ME_TO_RANDOM_STRING/$SECRET_KEY/" "$SYSTEMD_SERVICE"
```

**NEW**:
```bash
# Generate secrets
log_info "Generating secrets..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Create .env file with secrets
ENV_FILE="$APP_DIR/.env"
cat > "$ENV_FILE" << EOF
# Lernmanager Environment Configuration
# Generated on: $(date)
# DO NOT commit this file to git!

# Flask secret key (required)
SECRET_KEY=$SECRET_KEY

# Production mode
FLASK_ENV=production

# HTTPS-only cookies (uncomment after setting up SSL/TLS)
# FORCE_HTTPS=true

# Database encryption (optional, requires sqlcipher3-binary)
# SQLCIPHER_KEY=CHANGE_ME_TO_RANDOM_STRING
EOF

chmod 600 "$ENV_FILE"
chown root:root "$ENV_FILE"
log_info "Secrets saved to $ENV_FILE (root access only)"

# Copy service file as-is (no injection needed!)
cp "$APP_DIR/deploy/lernmanager.service" "$SYSTEMD_SERVICE"
```

---

### File: `deploy/update.sh`

**Remove entire secret preservation section** (lines 225-262):

**OLD** (delete this):
```bash
if git diff --name-only "$CURRENT_COMMIT" "$NEW_COMMIT" | grep -q "^deploy/lernmanager.service$"; then
    log_info "Systemd service file changed, updating..."

    # Preserve SECRET_KEY and SQLCIPHER_KEY from current service
    CURRENT_SECRET=$(grep "SECRET_KEY=" "$SYSTEMD_SERVICE" | sed -n 's/.*"\(.*\)".*/\1/p')
    # ... complex sed extraction logic ...

    # Copy new service file
    cp "$APP_DIR/deploy/lernmanager.service" "$SYSTEMD_SERVICE"

    # Restore secrets
    sed -i "s/CHANGE_ME_TO_RANDOM_STRING/$CURRENT_SECRET/" "$SYSTEMD_SERVICE"
    # ... more injection logic ...
fi
```

**NEW** (simple!):
```bash
if git diff --name-only "$CURRENT_COMMIT" "$NEW_COMMIT" | grep -q "^deploy/lernmanager.service$"; then
    log_info "Systemd service file changed, updating..."

    # Copy new service file (secrets are in .env, not in service file!)
    cp "$APP_DIR/deploy/lernmanager.service" "$SYSTEMD_SERVICE"

    systemctl daemon-reload
    SERVICE_UPDATED=true
    log_info "Systemd service updated successfully"
fi
```

**Rollback also simplifies** (lines 73-86):
```bash
if [ "$SERVICE_UPDATED" = true ]; then
    log_info "Restoring previous systemd service..."
    sudo -u "$APP_USER" git show "$CURRENT_COMMIT:deploy/lernmanager.service" > /tmp/lernmanager.service.rollback
    # No need to preserve secrets - they're already in .env!
    cp /tmp/lernmanager.service.rollback "$SYSTEMD_SERVICE"
    rm /tmp/lernmanager.service.rollback
    systemctl daemon-reload
fi
```

---

## Migration Path for Existing Installations

For servers already deployed with the old method:

```bash
# SSH to server
ssh user@server

# Extract secrets from current service file
sudo grep 'SECRET_KEY=' /etc/systemd/system/lernmanager.service | sed 's/.*"\(.*\)".*/SECRET_KEY=\1/' > /tmp/secrets.env
sudo grep 'SQLCIPHER_KEY=' /etc/systemd/system/lernmanager.service | sed 's/.*"\(.*\)".*/SQLCIPHER_KEY=\1/' >> /tmp/secrets.env 2>/dev/null || true

# Add standard variables
echo 'FLASK_ENV=production' >> /tmp/secrets.env
echo '# FORCE_HTTPS=true  # Uncomment after setting up SSL' >> /tmp/secrets.env

# Move to proper location
sudo mv /tmp/secrets.env /opt/lernmanager/.env
sudo chmod 600 /opt/lernmanager/.env
sudo chown root:root /opt/lernmanager/.env

# Deploy new code (with updated service file)
sudo /opt/lernmanager/deploy/update.sh

# Verify secrets are loaded
sudo systemctl restart lernmanager
sudo systemctl status lernmanager
```

---

## Security Considerations

### File Permissions
```bash
# .env file
-rw------- root root /opt/lernmanager/.env
```
- Only root can read/write
- Service runs as `lernmanager` user but systemd loads it as root first

### File Location Options

**Option A: `/opt/lernmanager/.env` (Recommended)**
- ✅ Co-located with app
- ✅ Easy to find/manage
- ✅ Backed up with app directory
- ⚠️ Must ensure app user can't write to it

**Option B: `/etc/lernmanager/secrets.env`**
- ✅ Traditional system config location
- ✅ Clear separation from app code
- ⚠️ Requires creating `/etc/lernmanager/` directory
- ⚠️ Not backed up with app

**Recommendation**: Use `/opt/lernmanager/.env` for simplicity.

### Git Safety

Add to `.gitignore`:
```
.env
.secrets
*.env
```

---

## Testing the Implementation

1. **Test new installation**:
   ```bash
   # Fresh install should create .env file
   sudo /opt/lernmanager/deploy/setup.sh
   # Check .env exists and has correct permissions
   sudo ls -la /opt/lernmanager/.env
   # Verify service can read secrets
   sudo systemctl status lernmanager
   ```

2. **Test updates without service file changes**:
   ```bash
   # Make code change, commit, push
   # Run update
   sudo /opt/lernmanager/deploy/update.sh
   # .env should be untouched
   ```

3. **Test updates WITH service file changes**:
   ```bash
   # Change service file, commit, push
   # Run update
   sudo /opt/lernmanager/deploy/update.sh
   # .env should still be untouched
   # New service file should be deployed
   # App should still work with same secrets
   ```

4. **Test rollback**:
   ```bash
   # Simulate failed deployment
   # Verify secrets still work after rollback
   ```

---

## Summary: Why This Is Better

| Aspect | Current (sed injection) | New (EnvironmentFile) |
|--------|-------------------------|----------------------|
| **Secret storage** | In service file | In `.env` file |
| **Service file updates** | Extract + inject secrets | Just copy new file |
| **Adding secrets** | Edit setup.sh + update.sh | Add line to .env |
| **Risk of loss** | Medium (sed parsing) | None (file persists) |
| **Code complexity** | ~30 lines sed logic | ~3 lines |
| **Standard practice** | No | Yes (systemd docs) |
| **Debugging** | Check service file | Check `.env` file |
| **Manual secret change** | Edit service + reload | Edit `.env` + reload |

---

## Next Steps

If you want to implement this:

1. I can update the deployment scripts (setup.sh, update.sh, lernmanager.service)
2. Test locally with Docker
3. Create migration script for existing deployments
4. Update deployment documentation

Would you like me to proceed with the implementation?
