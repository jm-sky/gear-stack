#!/bin/bash

# Gear Stack Deployment Script
# This script builds the application and deploys it to production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DEST="/var/www/gear-stack"
BACKEND_DEST="$PROJECT_DIR"

# Determine branch to deploy
if [ -n "$DEPLOY_BRANCH" ]; then
  BRANCH="$DEPLOY_BRANCH"
else
  BRANCH="$(git branch --show-current)"
fi

echo -e "${GREEN}🚀 Starting Gear Stack deployment...${NC}"

# Step 1: Git pull
echo -e "${YELLOW}📦 Step 1: Pulling latest changes from git (branch: $BRANCH)...${NC}"
cd "$PROJECT_DIR"
git fetch origin

if [ -n "$DEPLOY_BRANCH" ]; then
  # If DEPLOY_BRANCH is specified, switch to it and reset hard
  git checkout "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH" "origin/$BRANCH"
  git reset --hard "origin/$BRANCH"
  git clean -fd
else
  # If not specified, stay on current branch and pull latest changes
  git pull origin "$BRANCH" || true
  git clean -fd
fi

# Step 2: Install frontend dependencies
echo -e "${YELLOW}📦 Step 2: Installing frontend dependencies...${NC}"
pnpm install --frozen-lockfile

# Step 3: Build frontend
echo -e "${YELLOW}🔨 Step 3: Building frontend...${NC}"
pnpm build
echo -e "${GREEN}✅ Frontend build completed${NC}"

# Step 4: Copy frontend to destination
echo -e "${YELLOW}📋 Step 4: Copying frontend to $FRONTEND_DEST...${NC}"

# Try without sudo first (if user is in caddy group), fallback to sudo
if mkdir -p "$FRONTEND_DEST" 2>/dev/null && [ -w "$FRONTEND_DEST" ] 2>/dev/null; then
  mkdir -p "$FRONTEND_DEST"
  rsync -av --delete dist/ "$FRONTEND_DEST/"
else
  sudo mkdir -p "$FRONTEND_DEST"
  sudo rsync -av --delete dist/ "$FRONTEND_DEST/"
fi
echo -e "${GREEN}✅ Frontend copied to $FRONTEND_DEST${NC}"

# Step 5: Build and restart backend (Docker Compose)
echo -e "${YELLOW}🐳 Step 5: Building and restarting backend...${NC}"
if [ -f "backend/docker-compose.yml" ]; then
  cd "$PROJECT_DIR/backend"
  docker-compose build
  docker-compose down
  docker-compose up -d
  echo -e "${GREEN}✅ Backend services restarted${NC}"
  cd "$PROJECT_DIR"
else
  echo -e "${YELLOW}⚠️  Backend docker-compose.yml not found, skipping backend deployment${NC}"
fi

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
