#!/bin/bash
# Verification script for the complete uv + pyproject.toml setup

set -e

echo "🧪 Verifying complete uv setup for Dispatch..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed: $(uv --version)"

# Check if we're in the dispatch directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the dispatch repository root"
    exit 1
fi

echo "✅ Running from dispatch repository root"

# Check pyproject.toml has project table
echo "🔍 Checking pyproject.toml configuration..."
if grep -q "^\[project\]" pyproject.toml; then
    echo "✅ pyproject.toml has [project] table"
else
    echo "❌ pyproject.toml missing [project] table"
    exit 1
fi

# Test modern uv commands
echo "🔍 Testing modern uv commands..."

# Test uv sync (dry run)
echo "  Testing uv sync..."
if DISPATCH_LIGHT_BUILD=1 uv sync --dev --no-install-project --python 3.11 > /dev/null 2>&1; then
    echo "✅ uv sync works correctly"
else
    echo "❌ uv sync failed"
    exit 1
fi

# Test uv add (dry run with remove)
echo "  Testing uv add/remove..."
if uv add --dev pytest-timeout --python 3.11 > /dev/null 2>&1; then
    if uv remove --dev pytest-timeout > /dev/null 2>&1; then
        echo "✅ uv add/remove works correctly"
    else
        echo "❌ uv remove failed"
        exit 1
    fi
else
    echo "❌ uv add failed"
    exit 1
fi

# Test legacy pip install still works
echo "🔍 Testing legacy pip install..."
if DISPATCH_LIGHT_BUILD=1 uv pip install --dry-run -e . --python 3.11 > /dev/null 2>&1; then
    echo "✅ Legacy uv pip install still works"
else
    echo "❌ Legacy uv pip install failed"
    exit 1
fi

# Check if lock file exists or can be created
echo "🔍 Checking lock file..."
if [ -f "uv.lock" ]; then
    echo "✅ uv.lock file exists"
else
    echo "  Generating uv.lock..."
    if DISPATCH_LIGHT_BUILD=1 uv lock --python 3.11 > /dev/null 2>&1; then
        echo "✅ uv.lock generated successfully"
    else
        echo "❌ Failed to generate uv.lock"
        exit 1
    fi
fi

# Test dynamic versioning
echo "🔍 Testing dynamic versioning..."
if python -c "import importlib.metadata; version = importlib.metadata.version('dispatch'); print(f'Version: {version}'); assert version != 'unknown'" 2>/dev/null; then
    echo "✅ Dynamic versioning works correctly"
else
    echo "❌ Dynamic versioning failed"
    exit 1
fi

# Check if setup.py is disabled
if [ -f "setup.py" ]; then
    echo "⚠️  setup.py still exists (should be setup.py.bak)"
    echo "   Consider running: mv setup.py setup.py.bak"
else
    echo "✅ setup.py is disabled/removed"
fi

echo ""
echo "🎉 All checks passed! Full uv migration is working correctly."
echo ""
echo "Modern workflow:"
echo "1. Setup: DISPATCH_LIGHT_BUILD=1 uv sync --dev"
echo "2. Add deps: uv add package-name"
echo "3. Remove deps: uv remove package-name"
echo "4. Update: uv sync --upgrade"
echo ""
echo "Legacy workflow (still works):"
echo "1. Create venv: uv venv --python 3.11"
echo "2. Activate: source .venv/bin/activate"
echo "3. Install: DISPATCH_LIGHT_BUILD=1 uv pip install -e \".[dev]\""
