#!/bin/bash
# Launch the Liquid Galaxy Demo Suite (Ubuntu desktop).
# Creates a venv on first run and installs deps, then starts the app.
set -e
cd "$(dirname "$0")"

PY=python3
if ! command -v "$PY" >/dev/null 2>&1; then PY=python; fi

VENV=.venv
if [ ! -x "$VENV/bin/python" ]; then
    echo "Creating virtualenv…"
    "$PY" -m venv "$VENV"
    "$VENV/bin/pip" install --quiet --upgrade pip
    "$VENV/bin/pip" install --quiet -r requirements.txt
fi

exec "$VENV/bin/python" main.py
