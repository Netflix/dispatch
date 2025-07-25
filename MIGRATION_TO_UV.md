# Migration Guide: From pip to uv

This guide outlines the steps taken to migrate the Dispatch project from pip to uv for Python dependency management.

## What is uv?

uv is a fast Python package and project manager written in Rust. It's designed to be a drop-in replacement for pip, pip-tools, pipx, poetry, pyenv, virtualenv, and more.

## Benefits of uv

- **Speed**: 10-100x faster than pip
- **Compatibility**: Drop-in replacement for pip commands
- **Resolution**: Better dependency resolution
- **Caching**: Smart caching for faster subsequent installs
- **Virtual Environments**: Built-in virtual environment management

## Migration Steps Completed

### 1. Updated pyproject.toml

- Added `[build-system]` section
- Added `[project]` section with all dependencies from `requirements-base.in`
- Added `[project.optional-dependencies]` with dev dependencies from `requirements-dev.in`
- Maintained all existing tool configurations (black, ruff)

### 2. Updated CI/CD Workflows

- Modified `.github/workflows/python.yml` to use uv
- Modified `.github/workflows/playwright.yml` to use uv
- Added uv installation step in workflows
- Updated dependency installation commands

### 3. Updated Dockerfile

- Added uv installation in the Docker image
- Replaced `pip install` with `uv pip install --system`

### 4. Updated Documentation

- Updated all documentation files to use uv commands
- Modified contribution guidelines
- Updated plugin development instructions

### 5. Updated Development Setup Files

- Modified `.devcontainer/postCreateCommand.sh`
- Updated `.pre-commit-config.yaml` comments
- Updated `requirements-dev.in` comments

## How to Use uv

### Installation

```bash
# macOS
brew install uv

# Linux/Windows
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Common Commands

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e ".[dev]"

# Install a specific package
uv pip install package-name

# Compile requirements
uv pip compile pyproject.toml -o requirements.txt

# Sync dependencies
uv pip sync requirements.txt
```

### Development Workflow

1. **Setup Environment**:

   ```bash
   uv venv
   source .venv/bin/activate
   export DISPATCH_LIGHT_BUILD=1
   uv pip install -e ".[dev]"
   ```

2. **Run Tests**:

   ```bash
   pytest
   ```

3. **Lint Code**:
   ```bash
   ruff check src tests
   black src tests
   ```

## Compatibility Notes

- The `requirements-base.txt` and `requirements-dev.txt` files are still maintained for compatibility
- You can still use pip commands if needed, but uv is recommended for speed
- All uv commands that mirror pip commands work the same way (e.g., `uv pip install` vs `pip install`)

## Rollback Instructions

If you need to rollback to pip:

1. Replace all `uv pip` commands with `pip` in:

   - GitHub workflows
   - Dockerfile
   - Documentation
   - Development scripts

2. Remove uv installation steps from CI/CD workflows and Dockerfile

3. Continue using the existing requirements files as before

## Additional Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [uv vs pip Comparison](https://github.com/astral-sh/uv#uv-vs-pip)
- [Python Packaging Guide](https://packaging.python.org/)
