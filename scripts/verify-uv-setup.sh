#!/bin/bash
# Verification script for uv setup with Dispatch

set -e

echo "🧪 Verifying uv setup for Dispatch..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed: $(uv --version)"

# Check if we're in the dispatch directory
if [ ! -f "pyproject.toml" ] || [ ! -f "setup.py" ]; then
    echo "❌ Please run this script from the dispatch repository root"
    exit 1
fi

echo "✅ Running from dispatch repository root"

# Test dry-run installation
echo "🔍 Testing dry-run installation..."
if uv pip install --dry-run -e . > /dev/null 2>&1; then
    echo "✅ Dry-run installation successful"
else
    echo "❌ Dry-run installation failed"
    exit 1
fi

# Test dry-run with dev dependencies
echo "🔍 Testing dry-run installation with dev dependencies..."
if DISPATCH_LIGHT_BUILD=1 uv pip install --dry-run -e ".[dev]" > /dev/null 2>&1; then
    echo "✅ Dry-run installation with dev dependencies successful"
else
    echo "❌ Dry-run installation with dev dependencies failed"
    exit 1
fi

# Check pyproject.toml syntax
echo "🔍 Checking pyproject.toml syntax..."
if python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))" 2>/dev/null; then
    echo "✅ pyproject.toml syntax is valid"
else
    # Fallback for Python < 3.11
    if python -c "import tomli; tomli.load(open('pyproject.toml', 'rb'))" 2>/dev/null; then
        echo "✅ pyproject.toml syntax is valid"
    else
        echo "❌ pyproject.toml syntax is invalid"
        exit 1
    fi
fi

# Check if requirements files exist
if [ -f "requirements-base.txt" ] && [ -f "requirements-dev.txt" ]; then
    echo "✅ Requirements files are present"
else
    echo "❌ Requirements files are missing"
    exit 1
fi

echo ""
echo "🎉 All checks passed! uv is ready to use with Dispatch."
echo ""
echo "Next steps:"
echo "1. Create a virtual environment: uv venv"
echo "2. Activate it: source .venv/bin/activate"
echo "3. Install dispatch: DISPATCH_LIGHT_BUILD=1 uv pip install -e \".[dev]\""
