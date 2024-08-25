#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install system-level Chromium
apt-get update && apt-get install -y chromium-browser

# Set environment variables for Playwright
export PLAYWRIGHT_CHROMIUM_PATH=$(which chromium-browser)
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1