@echo off
title RI ENTERPRISES - Setup
cd /d "%~dp0"

echo ============================================
echo   RI ENTERPRISES - First Time Setup
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed.
    echo Download Python from https://www.python.org/downloads/
    echo During install, check "Add Python to PATH".
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Could not create virtual environment.
    pause
    exit /b 1
)

echo Installing packages...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Could not install required packages.
    pause
    exit /b 1
)

if not exist ".env" (
    copy .env.example .env
    echo Created .env file - you can change admin password there.
)

echo.
echo Setup complete!
echo Double-click START_WEBSITE.bat to run your website.
echo.
pause
