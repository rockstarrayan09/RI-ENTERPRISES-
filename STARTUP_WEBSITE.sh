#!/bin/bash
PROJECT_DIR="/Volumes/ESD-USB/PY 1"

for _ in $(seq 1 120); do
    if [ -f "$PROJECT_DIR/app.py" ]; then
        break
    fi
    sleep 2
done

if [ ! -f "$PROJECT_DIR/app.py" ]; then
    echo "Project folder not found: $PROJECT_DIR" >&2
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

PYTHON=""
if [ -x "$PROJECT_DIR/venv/bin/python3" ]; then
    PYTHON="$PROJECT_DIR/venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
else
    echo "Python 3 is not installed." >&2
    exit 1
fi

export AUTOSTART=1
export FLASK_DEBUG=0
exec "$PYTHON" app.py
