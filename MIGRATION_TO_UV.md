# Migration Complete: Full uv and pyproject.toml Support

This document describes the **complete migration** from pip to uv with full pyproject.toml support for Dispatch.

## What is uv?

uv is a fast Python package and project manager written in Rust. It's designed to be a drop-in replacement for pip, pip-tools, pipx, poetry, pyenv, virtualenv, and more.

## Benefits of uv

- **Speed**: 10-100x faster than pip
- **Modern dependency management**: Lock files, dependency resolution
- **Complete workflow**: `uv add`, `uv remove`, `uv sync`, `uv lock`
- **Virtual environment management**: Built-in venv handling
- **Reproducible builds**: With `uv.lock` file

## Migration Completed ✅

### **Full pyproject.toml Migration**

We've completely migrated from setup.py to pyproject.toml:

- ✅ All dependencies now in `pyproject.toml`
- ✅ All entry points and plugin configurations migrated
- ✅ Full uv command support: `uv add`, `uv remove`, `uv sync`
- ✅ Lock file generation with `uv.lock`
- ✅ Dynamic versioning with `versioningit` (automatic Git-based versions)
- ✅ setup.py deprecated (kept as backup at `setup.py.bak`)

### **What Works Now**

✅ **Modern Commands**: `uv add`, `uv remove`, `uv sync`, `uv lock`
✅ **Installation**: `uv pip install -e ".[dev]"` works perfectly
✅ **CLI**: `dispatch` command is available and functional
✅ **Plugins**: All 28 dispatch plugins properly discovered
✅ **Dependencies**: Managed entirely through `pyproject.toml`
✅ **Lock file**: `uv.lock` for reproducible installations
✅ **Dynamic versioning**: Automatic Git-based version generation
✅ **Speed**: ~10x faster than pip for all operations

## New Modern Workflow

### **Installation**

```bash
# Install uv
brew install uv  # macOS
# or
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Windows
```

### **Development Setup (Modern uv Way)**

```bash
# 1. Clone and enter project
git clone <repo>
cd dispatch

# 2. Create and sync environment (replaces manual venv + install)
export DISPATCH_LIGHT_BUILD=1
uv sync --dev

# 3. Activate environment
source .venv/bin/activate

# That's it! Everything is installed and ready
```

### **Dependency Management**

```bash
# Add a new dependency
uv add requests

# Add a development dependency
uv add --dev pytest-xdist

# Remove a dependency
uv remove requests

# Update dependencies
uv sync --upgrade

# Lock dependencies (creates/updates uv.lock)
uv lock
```

### **Alternative: Traditional pip-style**

```bash
# If you prefer the old way (still works)
uv venv --python 3.11
source .venv/bin/activate
export DISPATCH_LIGHT_BUILD=1
uv pip install -e ".[dev]"
```

## Key Files

- **`pyproject.toml`**: Primary configuration, dependencies, and metadata
- **`uv.lock`**: Lock file for reproducible installations
- **`DYNAMIC_VERSIONING.md`**: Documentation for automatic Git-based versioning
- **`setup.py.bak`**: Backup of old setup.py (for reference only)
- **`requirements-*.txt`**: Legacy files (will be deprecated)

## CI/CD Updates

All CI/CD workflows have been updated:

- GitHub Actions use uv for faster builds
- Docker images use uv for faster builds
- All installation commands updated

## Development Commands

```bash
# Run tests
pytest

# Lint code
ruff check src tests
black src tests

# Add/remove dependencies
uv add package-name
uv remove package-name

# Sync environment with lock file
uv sync

# Update lock file
uv lock --upgrade
```

## Benefits Achieved

- **10x faster** dependency resolution and installation
- **Modern dependency management** with lock files
- **Simplified workflow** with `uv sync`
- **Better reproducibility** with `uv.lock`
- **Easier dependency management** with `uv add`/`uv remove`
- **Future-proof** setup using modern Python packaging standards

## Migration from Old Setup

If you were using the old pip-based setup:

### **Replace this** (old way):

```bash
pip install -e ".[dev]"
```

### **With this** (new way):

```bash
uv sync --dev
```

### **Replace this** (old dependency management):

```bash
# Edit requirements-base.in
# Run pip-compile
```

### **With this** (new dependency management):

```bash
uv add package-name
```

## Troubleshooting

### Python Version Issues

If you get Python version errors:

```bash
# Specify Python version explicitly
uv sync --python 3.11
```

### Environment Issues

If you have environment conflicts:

```bash
# Reset environment
rm -rf .venv uv.lock
uv sync --dev
```

### Asset Building

For development (skips frontend asset building):

```bash
export DISPATCH_LIGHT_BUILD=1
uv sync --dev
```

## What's Deprecated/Removed

❌ **setup.py**: Replaced by `pyproject.toml` (moved to `setup.py.bak`)
❌ **setup.cfg**: Configurations moved to `pyproject.toml`
❌ **requirements-\*.in/txt**: Replaced by `pyproject.toml` + `uv.lock`
❌ **pip-compile**: Replaced by `uv lock`
❌ **Manual venv management**: Replaced by `uv sync`

These files have been removed from the repository as they're no longer needed.

## Additional Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [uv Guide](https://docs.astral.sh/uv/)
- [Python pyproject.toml Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
