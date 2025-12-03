#!/bin/bash

# Creates a venv at the project root, installing 'supplemental' necessary packages

ROOT_DIR="$(cd "$(dirname "$0")/.."; pwd)"
VENV_DIR="$ROOT_DIR/venv"

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at: $VENV_DIR"
    exit 0
fi

echo "Creating virtual environment at: $VENV_DIR"
python3 -m venv "$VENV_DIR" || {
    echo "Failed to create virtual environment."
    exit 1
}

echo "Activating venv to upgrade pip/setuptools/wheel..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel
pip install requests
pip install scikit-learn
deactivate

echo "Virtual environment created successfully."
