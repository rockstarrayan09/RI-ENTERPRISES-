#!/bin/bash
cd "$(dirname "$0")"

echo "============================================"
echo "  RI ENTERPRISES - Mac Setup"
echo "============================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: Python 3 is not installed."
    echo "Install from https://www.python.org/downloads/"
    exit 1
fi

echo "Creating Mac virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Could not create virtual environment."
    exit 1
fi

echo "Installing packages..."
venv/bin/pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Could not install required packages."
    exit 1
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Created .env file - you can change admin password there."
fi

chmod +x START_WEBSITE.sh STARTUP_WEBSITE.sh ENABLE_AUTOSTART.sh

echo
echo "Setup complete!"
echo "Run: ./START_WEBSITE.sh"
echo "Auto-start on boot: ./ENABLE_AUTOSTART.sh"
echo
