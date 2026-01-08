# Server Setup Guide for Lernmanager

This guide walks you through setting up Lernmanager on a fresh Linux VServer.

## Prerequisites

- Ubuntu/Debian-based VServer
- SSH access with sudo privileges
- Domain name pointing to your server's IP (optional but recommended)

## Quick Start (Automated Setup)

**Recommended**: Use the automated setup script for a one-command installation:

```bash
# Download and run setup script
curl -sSL https://raw.githubusercontent.com/patrickfiedler/lernmanager/main/deploy/setup.sh | sudo bash
```

This will:
- Install all system dependencies
- Create the lernmanager user
- Clone the repository
- Set up Python virtual environment
- Generate and configure secrets automatically
- Configure and start the systemd service

After the script completes, skip to the **Post-Installation Setup** section below.

---

## Manual Setup (Alternative)

If you prefer manual installation or need to customize the setup:

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl
```

### 2. Create Application User

```bash
sudo useradd -r -s /usr/sbin/nologin -m -d /opt/lernmanager lernmanager
```

### 3. Clone Repository

```bash
sudo git clone https://github.com/patrickfiedler/lernmanager.git /opt/lernmanager
cd /opt/lernmanager
sudo chown -R lernmanager:lernmanager /opt/lernmanager
```

### 4. Set Up Python Environment

```bash
sudo -u lernmanager python3 -m venv /opt/lernmanager/venv
sudo -u lernmanager /opt/lernmanager/venv/bin/pip install --upgrade pip
sudo -u lernmanager /opt/lernmanager/venv/bin/pip install -r /opt/lernmanager/requirements.txt
```

### 5. Create Data Directories

```bash
sudo mkdir -p /opt/lernmanager/data /opt/lernmanager/instance/uploads /opt/lernmanager/instance/tmp
sudo chown -R lernmanager:lernmanager /opt/lernmanager/data /opt/lernmanager/instance
sudo chmod 755 /opt/lernmanager/instance/uploads /opt/lernmanager/instance/tmp /opt/lernmanager/data
```

### 6. Generate Secrets

```bash
# Generate SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "Generated SECRET_KEY: $SECRET_KEY"
echo "IMPORTANT: Save this key securely!"
```

### 7. Configure Systemd Service

```bash
# Copy service file
sudo cp /opt/lernmanager/deploy/lernmanager.service /etc/systemd/system/

# Inject SECRET_KEY into service file
sudo sed -i "s/CHANGE_ME_TO_RANDOM_STRING/$SECRET_KEY/" /etc/systemd/system/lernmanager.service

# Reload, enable, and start service
sudo systemctl daemon-reload
sudo systemctl enable lernmanager
sudo systemctl start lernmanager

# Check status
sudo systemctl status lernmanager

# Test HTTP endpoint
curl -I http://127.0.0.1:8080
```

---

## Post-Installation Setup

After installation (automated or manual), complete these steps:

### 1. Configure Nginx

```bash
# Copy nginx config
sudo cp /opt/lernmanager/deploy/nginx.conf /etc/nginx/sites-available/lernmanager

# Edit to set your domain
sudo nano /etc/nginx/sites-available/lernmanager
# Replace DOMAIN.TLD with your actual domain

# Enable site
sudo ln -s /etc/nginx/sites-available/lernmanager /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm -f /etc/nginx/sites-enabled/default

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### 2. Set Up HTTPS with Let's Encrypt

```bash
sudo certbot --nginx -d YOUR_DOMAIN.TLD
```

Follow the prompts. Certbot will automatically configure nginx for HTTPS and set up auto-renewal.

### 3. Configure Firewall

```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### 4. Change Default Admin Password

**CRITICAL**: The default admin credentials are `admin` / `admin`.

1. Navigate to your domain or http://server-ip
2. Login with admin/admin
3. Go to Settings → Change Password
4. Set a secure password

---

## Updating Your Installation

After the initial setup, use the update script to deploy new code:

```bash
# SSH to your server
ssh user@your-server.de

# Run the update script
sudo /opt/lernmanager/deploy/update.sh
```

The update script will:
1. Pull latest code from GitHub
2. Detect and update dependencies if requirements.txt changed
3. Preserve your SECRET_KEY and other secrets
4. Restart the service
5. Automatically rollback if the service fails to start

**Exit codes:**
- `0` = Update successful
- `1` = Update failed, rolled back successfully
- `2` = Critical failure, manual intervention required

---

## Advanced Configuration

### Optional: Database Encryption with SQLCipher

Enable AES-256 encryption for the SQLite database:

```bash
# Generate encryption key
SQLCIPHER_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "Generated SQLCIPHER_KEY: $SQLCIPHER_KEY"

# Edit systemd service
sudo nano /etc/systemd/system/lernmanager.service

# Uncomment and set the SQLCIPHER_KEY line:
# Environment="SQLCIPHER_KEY=your_generated_key_here"

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart lernmanager
```

**Note**: If you have an existing unencrypted database, use the migration script first:
```bash
cd /opt/lernmanager
sudo -u lernmanager -E SQLCIPHER_KEY="your_key" /opt/lernmanager/venv/bin/python migrate_to_sqlcipher.py
```

## Troubleshooting

### Check Application Logs
```bash
sudo journalctl -u lernmanager -f
```

### Check Nginx Logs
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Restart Services
```bash
sudo systemctl restart lernmanager
sudo systemctl restart nginx
```

### Test Application Directly
```bash
# Test if waitress is responding
curl http://127.0.0.1:8080
```

## Database Encryption (Optional but Recommended)

SQLCipher provides AES-256 encryption for the SQLite database. This protects student data if the database file is stolen.

### Enable Encryption on New Installation

1. Generate an encryption key:
```bash
SQLCIPHER_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "Your SQLCIPHER_KEY: $SQLCIPHER_KEY"
```

2. Edit the systemd service to add the key:
```bash
sudo nano /etc/systemd/system/lernmanager.service
# Uncomment and set SQLCIPHER_KEY
```

3. Reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart lernmanager
```

### Migrate Existing Database to Encrypted

If you already have an unencrypted database:

```bash
# As the lernmanager user
sudo -u lernmanager bash
cd /opt/lernmanager
source venv/bin/activate

# Generate key
export SQLCIPHER_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "Save this key: $SQLCIPHER_KEY"

# Run migration script
python migrate_to_sqlcipher.py

# After migration succeeds, add SQLCIPHER_KEY to systemd service
exit
sudo nano /etc/systemd/system/lernmanager.service
sudo systemctl daemon-reload
sudo systemctl restart lernmanager
```

**Important:** Store your SQLCIPHER_KEY securely. If lost, the database cannot be decrypted.

## Security Notes

1. **Change default admin password** after first login
2. **Keep SECRET_KEY secret** - never commit it to git
3. **Keep SQLCIPHER_KEY secret** - if using database encryption
4. **Regular updates**: `sudo apt update && sudo apt upgrade`
5. **Backup database**: `/opt/lernmanager/data/mbi_tracker.db`
6. **Backup encryption key**: Store SQLCIPHER_KEY separately from database backup
