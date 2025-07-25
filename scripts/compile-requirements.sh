#!/bin/bash
# Script to compile requirements files using uv

set -e

echo "Compiling requirements files with uv..."

# Compile base requirements
echo "Compiling requirements-base.txt..."
uv pip compile requirements-base.in --python-version 3.11 -o requirements-base.txt

# Compile dev requirements
echo "Compiling requirements-dev.txt..."
uv pip compile requirements-dev.in --python-version 3.11 -o requirements-dev.txt

echo "Requirements compilation complete!"

# Optional: Show the diff
if command -v git &> /dev/null; then
    echo -e "\nChanges to requirements files:"
    git diff requirements-base.txt requirements-dev.txt || true
fi
