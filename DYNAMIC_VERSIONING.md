# Dynamic Versioning with versioningit

Dispatch now uses **dynamic versioning** with `versioningit` to automatically generate version numbers from Git tags and commits.

## How It Works

The version is automatically determined using:

1. **Git tags** (e.g., `v1.2.3`) for released versions
2. **Git commits** for development versions
3. **Build date** for dirty working directories

## Version Format Examples

| Git State                | Generated Version             | Description               |
| ------------------------ | ----------------------------- | ------------------------- |
| `v1.2.3` tag (clean)     | `1.2.3`                       | Official release          |
| `v1.2.3` tag + 5 commits | `1.2.3.5+g<commit>`           | Development after release |
| Dirty working directory  | `1.2.3.5+g<commit>.d20250725` | Uncommitted changes       |
| No tags                  | `0.1.0.123+g<commit>`         | Pre-release development   |

## Configuration

The versioning is configured in `pyproject.toml`:

```toml
[tool.versioningit]
default-version = "0.1.0"

[tool.versioningit.vcs]
method = "git"
match = ["v*"]

[tool.versioningit.format]
distance = "{base_version}.{distance}+{vcs}{rev}"
dirty = "{base_version}.{distance}+d{build_date:%Y%m%d}"
distance-dirty = "{base_version}.{distance}+{vcs}{rev}.d{build_date:%Y%m%d}"
```

## Usage

### In Python Code

```python
import dispatch
print(dispatch.__version__)  # e.g., "1.2.3.5+gd2ce81f2d"

# Or using importlib.metadata
from importlib.metadata import version
print(version("dispatch"))
```

### In CLI

```bash
dispatch --version  # Shows the dynamic version
```

### During Build

The version is automatically embedded during package building with:

```bash
uv pip install -e .
# or
pip install .
```

## Creating Releases

To create a new release:

1. **Tag the release**:

   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

2. **Build/install** - the version will automatically be `1.2.3`

3. **Continue development** - future commits will be `1.2.3.N+g<commit>`

## Benefits

✅ **Automatic**: No manual version updates needed
✅ **Accurate**: Version reflects exact Git state
✅ **Traceable**: Each build has unique version
✅ **PEP 440 Compliant**: Works with all Python tooling
✅ **CI/CD Friendly**: Perfect for automated builds

## Migration from pkg_resources

The old `pkg_resources` approach has been replaced with modern `importlib.metadata`:

```python
# Old (deprecated)
VERSION = __import__("pkg_resources").get_distribution("dispatch").version

# New (modern)
from importlib.metadata import version
VERSION = version("dispatch")
```

This eliminates the `pkg_resources` deprecation warnings and is faster.

## Troubleshooting

### No Version Found

If you see `version = "unknown"`, ensure:

- You're in a Git repository
- The package is properly installed (not just PYTHONPATH)
- Git is available in PATH

### Invalid Version Format

Ensure Git tags follow semantic versioning:

- ✅ `v1.2.3`, `v2.0.0`, `v1.0.0-rc1`
- ❌ `release-1.2.3`, `v1.2.3-final`

### Build Failures

If versioningit fails:

```bash
# Check current version manually
python -c "import versioningit; print(versioningit.get_version('.'))"

# Or set a fallback
export SETUPTOOLS_SCM_PRETEND_VERSION=1.0.0
```
