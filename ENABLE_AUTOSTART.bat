@echo off
title RI ENTERPRISES - Enable Auto Start
cd /d "%~dp0"

set "START_SCRIPT=%~dp0STARTUP_WEBSITE.bat"
set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\RI_ENTERPRISES_Website.lnk"

echo Adding website to Windows Startup...
powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%START_SCRIPT%'; $s.WorkingDirectory='%~dp0'; $s.WindowStyle=7; $s.Description='RI ENTERPRISES Website'; $s.Save()"

echo.
echo Adding Windows Firewall rule for port 5000 (phone / other devices)...
netsh advfirewall firewall delete rule name="RI ENTERPRISES Website" >nul 2>&1
netsh advfirewall firewall add rule name="RI ENTERPRISES Website" dir=in action=allow protocol=TCP localport=5000

if exist "%SHORTCUT%" (
    echo.
    echo SUCCESS: Website will start automatically when Windows turns on.
    echo Phones on the same Wi-Fi can open the link shown in data\share-link.txt
    echo Shortcut: %SHORTCUT%
) else (
    echo.
    echo ERROR: Could not create startup shortcut.
)

echo.
pause
