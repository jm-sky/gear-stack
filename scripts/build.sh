#!/bin/bash

# Gear Stack Build Script
# This script installs dependencies and builds the application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${GREEN}🔨 Starting Gear Stack build...${NC}"

# Step 1: Install frontend dependencies
echo -e "${YELLOW}📦 Step 1: Installing frontend dependencies...${NC}"
cd "$PROJECT_DIR"
pnpm install --frozen-lockfile

# Step 2: Build frontend
echo -e "${YELLOW}🔨 Step 2: Building frontend...${NC}"
pnpm build
echo -e "${GREEN}✅ Frontend build completed${NC}"

echo -e "${GREEN}✅ Build completed successfully!${NC}"
