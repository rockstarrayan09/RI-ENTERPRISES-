@echo off
title RI ENTERPRISES - Website (Auto Start)
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    call INSTALL.bat
)

if not exist ".env" (
    if exist ".env.example" copy .env.example .env
)

set AUTOSTART=1
set FLASK_DEBUG=0
venv\Scripts\python.exe app.py
