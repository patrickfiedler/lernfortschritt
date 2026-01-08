#!/bin/bash
#
# Lernmanager Deployment Script
#
# Usage:
#   ./deploy/deploy.sh                    # Uses LERNMANAGER_SERVER env var
#   LERNMANAGER_SERVER=user@host ./deploy/deploy.sh
#
# Prerequisites:
#   - SSH key authentication to server
#   - sudo access for systemctl (passwordless recommended for deploy user)
#   - Repository cloned on server at /opt/lernmanager
#

set -e

# Configuration
SERVER="${LERNMANAGER_SERVER:-}"
APP_DIR="/opt/lernmanager"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check server is configured
if [ -z "$SERVER" ]; then
    echo -e "${RED}Error: LERNMANAGER_SERVER not set${NC}"
    echo "Usage: LERNMANAGER_SERVER=user@host ./deploy/deploy.sh"
    exit 1
fi

# Check we're on main branch
CURRENT_BRANCH=$(git -C "$LOCAL_DIR" rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo -e "${RED}Error: Not on $BRANCH branch (currently on '$CURRENT_BRANCH')${NC}"
    echo "Switch to $BRANCH branch before deploying."
    exit 1
fi

# Check for uncommitted changes
if ! git -C "$LOCAL_DIR" diff-index --quiet HEAD --; then
    echo -e "${RED}Error: You have uncommitted changes${NC}"
    echo "Commit or stash your changes before deploying."
    exit 1
fi

# Check if local is ahead of remote
LOCAL_COMMIT=$(git -C "$LOCAL_DIR" rev-parse HEAD)
git -C "$LOCAL_DIR" fetch origin $BRANCH
REMOTE_COMMIT=$(git -C "$LOCAL_DIR" rev-parse origin/$BRANCH)

if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
    echo -e "${YELLOW}Local branch is not in sync with remote${NC}"
    echo "Local:  $LOCAL_COMMIT"
    echo "Remote: $REMOTE_COMMIT"
    echo ""
    read -p "Push local changes to remote? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Pushing to origin/$BRANCH..."
        git -C "$LOCAL_DIR" push origin $BRANCH
    else
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}Deploying Lernmanager to ${SERVER}...${NC}"
echo ""

# Pull latest code on server
echo "Pulling latest code from repository..."
ssh "$SERVER" "cd $APP_DIR && sudo -u lernmanager git fetch origin && sudo -u lernmanager git reset --hard origin/$BRANCH"

# Create writable directories
echo ""
echo "Creating writable directories..."
ssh "$SERVER" "sudo mkdir -p $APP_DIR/instance/uploads $APP_DIR/instance/tmp $APP_DIR/data && sudo chown -R lernmanager:lernmanager $APP_DIR/instance $APP_DIR/data && sudo chmod 755 $APP_DIR/instance/uploads $APP_DIR/instance/tmp $APP_DIR/data"

# Update dependencies
echo ""
echo "Updating dependencies..."
ssh "$SERVER" "sudo -u lernmanager $APP_DIR/venv/bin/pip install -q -r $APP_DIR/requirements.txt"

# Update systemd service file
echo ""
echo "Updating systemd service..."
ssh "$SERVER" "sudo cp $APP_DIR/deploy/lernmanager.service /etc/systemd/system/lernmanager.service && sudo systemctl daemon-reload"

# Restart service
echo ""
echo "Restarting service..."
ssh "$SERVER" "sudo systemctl restart lernmanager"

echo ""
echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "Deployed commit:"
ssh "$SERVER" "cd $APP_DIR && git log -1 --oneline"
echo ""
echo "Service status:"
ssh "$SERVER" "systemctl status lernmanager --no-pager -l"
