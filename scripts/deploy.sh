#!/bin/bash

# Gear Stack Complete Deployment Script
# This script builds the frontend and restarts/migrates the backend
#
# Usage: scripts/deploy_all.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_DIR="/var/www/gear-stack"
BACKEND_DIR="$PROJECT_DIR/backend"
COMPOSE_FILE="docker-compose.dev.yml"

echo -e "${GREEN}🚀 Starting complete Gear Stack deployment...${NC}"

# Prompt for sudo password upfront
echo -e "${YELLOW}🔐 Requesting sudo access...${NC}"
sudo -v

# Keep sudo alive in background
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# Step 1: Pull latest changes
echo -e "${YELLOW}📦 Step 1: Pulling latest changes...${NC}"
cd "$PROJECT_DIR"
git pull

# Step 2: Install frontend dependencies
echo -e "${YELLOW}📦 Step 2: Installing frontend dependencies...${NC}"
pnpm install --frozen-lockfile

# Step 3: Build frontend
echo -e "${YELLOW}🔨 Step 3: Building frontend...${NC}"
# Clean up dist directory to avoid permission issues
rm -rf dist
pnpm build
echo -e "${GREEN}✅ Frontend build completed${NC}"

# Step 4: Deploy to /var/www/gear-stack
echo -e "${YELLOW}📋 Step 4: Deploying to ${DEPLOY_DIR}...${NC}"

# Remove old files (uses sudo via sudoers configuration)
sudo rm -rf "${DEPLOY_DIR:?}"/*

# Copy new build (uses sudo via sudoers configuration)
sudo cp -r dist/* "$DEPLOY_DIR/"

# Fix ownership to caddy:deploy
sudo chown -R caddy:deploy "$DEPLOY_DIR"

echo -e "${GREEN}✅ Deployed to ${DEPLOY_DIR}${NC}"

# Step 5: Restart backend and migrate
echo -e "${YELLOW}🐳 Step 5: Restarting backend and running migrations...${NC}"

if [ -d "$BACKEND_DIR" ] && [ -f "$BACKEND_DIR/$COMPOSE_FILE" ]; then
  cd "$BACKEND_DIR"

  echo "🔄 Stopping Docker Compose services..."
  docker compose -f "$COMPOSE_FILE" down

  echo ""
  echo "🚀 Starting Docker Compose services..."
  docker compose -f "$COMPOSE_FILE" up -d

  echo ""
  echo "⏳ Waiting for services to be healthy..."
  sleep 5

  echo ""
  echo "🔄 Running database migrations..."
  docker compose -f "$COMPOSE_FILE" exec app python cli.py db migrate

  echo -e "${GREEN}✅ Backend restarted and migrations applied${NC}"
else
  echo -e "${YELLOW}⚠️  Backend not found or docker-compose.dev.yml missing, skipping backend deployment${NC}"
fi

echo ""
echo -e "${GREEN}✅ Complete deployment finished successfully!${NC}"
