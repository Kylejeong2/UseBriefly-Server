#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Ensure Playwright cache directory exists
mkdir -p /opt/render/.cache/ms-playwright

# Set Playwright browser path
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright