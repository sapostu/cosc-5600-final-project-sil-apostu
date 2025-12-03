#!/bin/bash
# To use:  source scripts/deactivate.sh

# Deactivates the virtual environment

if type deactivate >/dev/null 2>&1; then
    deactivate
    echo "Deactivated virtual environment."
else
    echo "No active virtual environment to deactivate."
fi
