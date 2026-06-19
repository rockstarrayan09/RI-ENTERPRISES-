#!/bin/bash
cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"
PLIST="$HOME/Library/LaunchAgents/com.ri-enterprises.website.plist"
STARTUP_SCRIPT="$PROJECT_DIR/STARTUP_WEBSITE.sh"

chmod +x "$PROJECT_DIR/START_WEBSITE.sh"
chmod +x "$STARTUP_SCRIPT"
chmod +x "$PROJECT_DIR/ENABLE_AUTOSTART.sh"
chmod +x "$PROJECT_DIR/INSTALL.sh"

if [ ! -x "$PROJECT_DIR/venv/bin/python3" ]; then
    echo "Mac setup required (first time)..."
    bash "$PROJECT_DIR/INSTALL.sh" || exit 1
fi

cat > "$STARTUP_SCRIPT" <<SCRIPT
#!/bin/bash
PROJECT_DIR="$PROJECT_DIR"

for _ in \$(seq 1 120); do
    if [ -f "\$PROJECT_DIR/app.py" ]; then
        break
    fi
    sleep 2
done

if [ ! -f "\$PROJECT_DIR/app.py" ]; then
    echo "Project folder not found: \$PROJECT_DIR" >&2
    exit 1
fi

cd "\$PROJECT_DIR" || exit 1

PYTHON=""
if [ -x "\$PROJECT_DIR/venv/bin/python3" ]; then
    PYTHON="\$PROJECT_DIR/venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="\$(command -v python3)"
else
    echo "Python 3 is not installed." >&2
    exit 1
fi

export AUTOSTART=1
export FLASK_DEBUG=0
exec "\$PYTHON" app.py
SCRIPT

chmod +x "$STARTUP_SCRIPT"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ri-enterprises.website</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$STARTUP_SCRIPT</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/ri-enterprises-website.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/ri-enterprises-website-error.log</string>
</dict>
</plist>
EOF

mkdir -p "$PROJECT_DIR/data"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || launchctl unload "$PLIST" 2>/dev/null
launchctl bootstrap "gui/$(id -u)" "$PLIST" 2>/dev/null || launchctl load "$PLIST"

echo "SUCCESS: Website will start automatically when macOS turns on."
echo "Phone link (same Wi-Fi) is saved to: $PROJECT_DIR/data/share-link.txt"
echo "Launch agent: $PLIST"
