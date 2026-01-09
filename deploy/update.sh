#!/bin/bash
#
# Lernmanager Update Script
#
# This script updates an existing Lernmanager installation by pulling
# the latest code from GitHub and restarting the service. It automatically
# rolls back if the service fails to start.
#
# Usage:
#   sudo ./update.sh                          # Run locally on server
#   ssh user@server 'sudo /opt/lernmanager/deploy/update.sh'  # Run remotely
#
# Prerequisites:
#   - Lernmanager already installed (run deploy/setup.sh first)
#   - Root or sudo access
#   - Internet connectivity
#

set -e  # Exit on error
set -o pipefail  # Catch errors in pipes

# Configuration
APP_DIR="/opt/lernmanager"
APP_USER="lernmanager"
SYSTEMD_SERVICE="/etc/systemd/system/lernmanager.service"
BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# Helper functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${BLUE}=== $1 ===${NC}"; }

# Variables for rollback
CURRENT_COMMIT=""
NEW_COMMIT=""
DEPS_UPDATED=false
SERVICE_UPDATED=false

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root or with sudo"
        echo "Usage: sudo $0"
        exit 1
    fi
}

# Rollback function
rollback() {
    log_error "Deployment failed, initiating rollback..."

    cd "$APP_DIR"

    # Rollback git
    log_info "Reverting to commit $CURRENT_COMMIT..."
    sudo -u "$APP_USER" git reset --hard "$CURRENT_COMMIT"

    # Rollback dependencies if they were updated
    if [ "$DEPS_UPDATED" = true ]; then
        log_info "Restoring previous dependencies..."
        sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"
    fi

    # Rollback systemd service if it was updated
    if [ "$SERVICE_UPDATED" = true ]; then
        log_info "Restoring previous systemd service..."
        sudo -u "$APP_USER" git show "$CURRENT_COMMIT:deploy/lernmanager.service" > /tmp/lernmanager.service.rollback

        # Preserve SECRET_KEY
        if grep -q "SECRET_KEY=" "$SYSTEMD_SERVICE"; then
            CURRENT_SECRET=$(grep "SECRET_KEY=" "$SYSTEMD_SERVICE" | sed -n 's/.*"\(.*\)".*/\1/p')
            sed -i "s/CHANGE_ME_TO_RANDOM_STRING/$CURRENT_SECRET/" /tmp/lernmanager.service.rollback
        fi

        cp /tmp/lernmanager.service.rollback "$SYSTEMD_SERVICE"
        rm /tmp/lernmanager.service.rollback
        systemctl daemon-reload
    fi

    # Restart service
    log_info "Restarting service..."
    systemctl restart lernmanager
    sleep 3

    # Verify rollback
    if systemctl is-active --quiet lernmanager; then
        log_info "✓ Rollback successful, service is running"
        log_info "Current commit: $(git rev-parse --short HEAD)"
        exit 1
    else
        log_error "✗ CRITICAL: Rollback failed, service still not starting"
        log_error "Manual intervention required"
        log_error "View logs: journalctl -u lernmanager -n 50"
        exit 2
    fi
}

# Set trap for errors
trap 'rollback' ERR

# Main deployment function
main() {
    log_step "Lernmanager Deployment"

    # 1. Validate environment
    log_step "Step 1/7: Validating Environment"
    check_root

    if [ ! -d "$APP_DIR" ]; then
        log_error "Directory $APP_DIR does not exist"
        log_error "Run deploy/setup.sh first to perform initial installation"
        exit 1
    fi

    if [ ! -d "$APP_DIR/.git" ]; then
        log_error "$APP_DIR is not a git repository"
        exit 1
    fi

    if [ ! -f "$SYSTEMD_SERVICE" ]; then
        log_error "Systemd service file not found at $SYSTEMD_SERVICE"
        log_error "Run deploy/setup.sh first to perform initial installation"
        exit 1
    fi

    # Verify service is known to systemd
    if ! systemctl list-units --all --full | grep -q "lernmanager.service"; then
        log_warn "Service file exists but may need systemctl daemon-reload"
        systemctl daemon-reload
    fi

    log_info "Environment validated successfully"

    # 2. Pre-deployment snapshot
    log_step "Step 2/7: Creating Pre-Deployment Snapshot"
    cd "$APP_DIR"

    # Get current commit
    CURRENT_COMMIT=$(sudo -u "$APP_USER" git rev-parse HEAD)
    CURRENT_COMMIT_SHORT=$(sudo -u "$APP_USER" git rev-parse --short HEAD)
    log_info "Current commit: $CURRENT_COMMIT_SHORT"

    # Check for local changes
    if ! sudo -u "$APP_USER" git diff --quiet; then
        log_warn "Local changes detected in working directory"
        sudo -u "$APP_USER" git status --short
        log_warn "These will be discarded"
    fi

    # 3. Pull latest code
    log_step "Step 3/7: Pulling Latest Code"
    log_info "Fetching from origin/$BRANCH..."
    sudo -u "$APP_USER" git fetch origin "$BRANCH"

    log_info "Resetting to origin/$BRANCH..."
    sudo -u "$APP_USER" git reset --hard "origin/$BRANCH"

    NEW_COMMIT=$(sudo -u "$APP_USER" git rev-parse HEAD)
    NEW_COMMIT_SHORT=$(sudo -u "$APP_USER" git rev-parse --short HEAD)

    if [ "$CURRENT_COMMIT" = "$NEW_COMMIT" ]; then
        log_info "Already up to date at commit $CURRENT_COMMIT_SHORT"
        log_info "No deployment needed"
        exit 0
    fi

    log_info "Updated to commit: $NEW_COMMIT_SHORT"
    echo ""
    log_info "Changes in this deployment:"
    git log --oneline "$CURRENT_COMMIT..$NEW_COMMIT"
    echo ""

    # 4. Update dependencies if requirements.txt changed
    log_step "Step 4/7: Checking Dependencies"
    if git diff --name-only "$CURRENT_COMMIT" "$NEW_COMMIT" | grep -q "^requirements.txt$"; then
        log_info "requirements.txt changed, updating dependencies..."
        sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"
        DEPS_UPDATED=true
        log_info "Dependencies updated successfully"
    else
        log_info "No changes to requirements.txt"
    fi

    # 5. Update systemd service if changed
    log_step "Step 5/7: Checking Systemd Service"
    if git diff --name-only "$CURRENT_COMMIT" "$NEW_COMMIT" | grep -q "^deploy/lernmanager.service$"; then
        log_info "Systemd service file changed, updating..."

        # Preserve SECRET_KEY and SQLCIPHER_KEY from current service
        CURRENT_SECRET=""
        CURRENT_SQLCIPHER=""

        if grep -q "SECRET_KEY=" "$SYSTEMD_SERVICE"; then
            CURRENT_SECRET=$(grep "SECRET_KEY=" "$SYSTEMD_SERVICE" | sed -n 's/.*"\(.*\)".*/\1/p')
        fi

        if grep -q "SQLCIPHER_KEY=" "$SYSTEMD_SERVICE"; then
            CURRENT_SQLCIPHER=$(grep "SQLCIPHER_KEY=" "$SYSTEMD_SERVICE" | sed -n 's/.*"\(.*\)".*/\1/p')
        fi

        # Copy new service file
        cp "$APP_DIR/deploy/lernmanager.service" "$SYSTEMD_SERVICE"

        # Restore secrets
        if [ -n "$CURRENT_SECRET" ]; then
            sed -i "s/CHANGE_ME_TO_RANDOM_STRING/$CURRENT_SECRET/" "$SYSTEMD_SERVICE"
            log_info "SECRET_KEY preserved"
        fi

        if [ -n "$CURRENT_SQLCIPHER" ]; then
            # Uncomment and set SQLCIPHER_KEY if it was previously set
            sed -i "s/# Environment=\"SQLCIPHER_KEY=CHANGE_ME_TO_RANDOM_STRING\"/Environment=\"SQLCIPHER_KEY=$CURRENT_SQLCIPHER\"/" "$SYSTEMD_SERVICE"
            log_info "SQLCIPHER_KEY preserved"
        fi

        systemctl daemon-reload
        SERVICE_UPDATED=true
        log_info "Systemd service updated successfully"
    else
        log_info "No changes to systemd service"
    fi

    # 6. Restart service
    log_step "Step 6/7: Restarting Service"
    log_info "Restarting lernmanager service..."
    systemctl restart lernmanager

    log_info "Waiting for service to start..."
    sleep 3

    # 7. Verify deployment
    log_step "Step 7/7: Verifying Deployment"

    if systemctl is-active --quiet lernmanager; then
        log_info "✓ Service is active"
    else
        log_error "✗ Service failed to start"
        log_error "Triggering rollback..."
        rollback
    fi

    # Disable error trap now that deployment succeeded
    trap - ERR

    # Print summary
    log_step "Deployment Successful!"
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Lernmanager Successfully Updated!                   ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Deployment Details:${NC}"
    echo "  Previous commit:  $CURRENT_COMMIT_SHORT"
    echo "  New commit:       $NEW_COMMIT_SHORT"
    echo "  Dependencies:     $([ "$DEPS_UPDATED" = true ] && echo "Updated" || echo "No changes")"
    echo "  Service file:     $([ "$SERVICE_UPDATED" = true ] && echo "Updated" || echo "No changes")"
    echo "  Service status:   $(systemctl is-active lernmanager)"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  View logs:        sudo journalctl -u lernmanager -f"
    echo "  Check status:     sudo systemctl status lernmanager"
    echo "  Manual rollback:  cd $APP_DIR && sudo -u $APP_USER git reset --hard $CURRENT_COMMIT_SHORT && sudo systemctl restart lernmanager"
    echo ""
}

# Run main function
main "$@"
