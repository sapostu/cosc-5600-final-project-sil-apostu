#!/bin/bash

# Finds and removes all __pycache__ directories and .pyc files from the project root downward

ROOT_DIR="$(cd "$(dirname "$0")/.."; pwd)"

cd "$ROOT_DIR" || {
    echo "Could not change to project root directory: $ROOT_DIR"
    exit 1
}

python Main.py

echo "###############\nPYTHON APPLICATION return above the '#' line"

# Python bloat ( __pycache__ and .pyc files ) removal starting

echo "\n-----------Python cache and bloat removal starting\n-----------Searching for __pycache__ directories and .pyc files in repo…"

pycache_count=$(find . -type d -name "__pycache__" | wc -l)
pycfile_count=$(find . -type f -name "*.pyc" | wc -l)

echo "Found $pycache_count __pycache__ directories and $pycfile_count .pyc files. Removing…"

find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

echo "Done. All __pycache__ directories and .pyc files removed."

# Deletes all .DS_Store files in the repository

# These files bloat environment and are not needed

echo "Searching for .DS_Store files in repo…"

count=$(find . -type f -name ".DS_Store" | wc -l)

if [ "$count" -eq 0 ]; then
    echo "No .DS_Store files found."
    exit 0
fi

echo "Found $count .DS_Store files. Removing…"
find . -type f -name ".DS_Store" -delete

echo "Done. All .DS_Store files removed."
