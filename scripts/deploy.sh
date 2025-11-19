#!/bin/bash

# Gear Stack Deployment Script
# This script builds the application and deploys it to /var/www/gear-stack/

set -e  # Exit on any error

echo "🚀 Starting Gear Stack deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
pnpm install

# Build the application
echo "🔨 Building application..."
pnpm build

# Clean target directory
echo "🧹 Cleaning target directory..."
sudo rm -rf /var/www/gear-stack/*

# Copy built files
echo "📋 Copying files to /var/www/gear-stack/..."
sudo cp -r dist/* /var/www/gear-stack/

echo "✅ Deployment completed successfully!"
