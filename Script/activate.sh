#!/bin/bash
# To use:  source scripts/activate.sh 

# Activates the virtual environment

ROOT_DIR="$(cd "$(dirname "$0")/.."; pwd)"
VENV_DIR="$ROOT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: no virtual environment found at: $VENV_DIR"
    echo "Run: ./scripts/create_venv.sh"

    return 1 2>/dev/null || exit 1
fi

source "$VENV_DIR/bin/activate"
echo "Activated virtual environment at: $VENV_DIR"
