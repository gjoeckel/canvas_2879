#!/bin/bash
# Wrapper script to run Box API script with correct Python environment

# Use canvas_grab venv Python directly (has boxsdk installed)
VENV_PYTHON="/Users/a00288946/Projects/canvas_grab/venv/bin/python3"
SCRIPT_DIR="/Users/a00288946/Projects/canvas_2879"

cd "$SCRIPT_DIR"
"$VENV_PYTHON" get-box-file-ids-api.py "$@"

