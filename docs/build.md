# Build Instructions

This document provides detailed instructions for building the Google Photo Organiser from source.

## Prerequisites

### Required Tools

- **Python 3.11 or higher** - The application is built and tested on Python 3.11+
- **uv** - Fast Python package manager and environment manager
  - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh` (Linux/macOS)
  - Or: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` (Windows)
  - Documentation: https://github.com/astral-sh/uv

### System Requirements

- **Windows 10/11** (for running the built executable)
- **Disk space**: ~500MB for development environment
- **RAM**: 4GB minimum (8GB recommended for large Takeout files)

## Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd google-photo-organiser
```

### 2. Install Dependencies

```bash
# Install all dependencies and create virtual environment
uv sync
```

This will:
- Create a `.venv` virtual environment
- Install all dependencies from `pyproject.toml`
- Set up the development environment

### 3. Verify Installation

```bash
# Run tests to verify setup
make test

# Or manually with uv
uv run pytest
```

## Building the Executable

### Quick Build

```bash
# Build executable using Makefile
make build
```

The executable will be created at `dist/photo-organiser.exe`.

### Manual Build

```bash
# Install PyInstaller if not already installed
uv sync

# Run PyInstaller with the spec file
uv run pyinstaller build.spec
```

### Build Process Details

The build process:
1. Reads configuration from `build.spec`
2. Analyzes dependencies and imports
3. Bundles Python runtime and all dependencies
4. Creates a single executable file
5. Outputs to `dist/photo-organiser.exe`

Build time: ~30-60 seconds on modern hardware.

## PyInstaller Configuration

The `build.spec` file configures the PyInstaller build:

```python
# Key configuration options:
- name='photo-organiser'      # Output executable name
- onefile=True                # Single executable file
- console=True                # Console application (not GUI)
- noconfirm=True              # Overwrite existing build
```

### Entry Point

The application entry point is defined in `src/photo_organiser/main.py` via the `main()` function, which is registered in `pyproject.toml`:

```toml
[project.scripts]
photo-organiser = "photo_organiser.main:main"
```

### Bundled Dependencies

The following dependencies are bundled into the executable:

- **Pillow** - Image processing and EXIF reading
- **tqdm** - Progress bar display
- Python standard library modules

Total executable size: ~30-40MB

## Testing

### Run Full Test Suite

```bash
# Using Makefile
make test

# Or directly with pytest
uv run pytest

# With coverage report
uv run pytest --cov=src/photo_organiser --cov-report=html
```

### Test Structure

```
tests/
├── test_extractor.py      # Zip extraction and file discovery
├── test_metadata.py       # Date parsing (JSON, EXIF, mtime)
├── test_organizer.py      # File classification and organization
└── fixtures/              # Test data
    ├── sample.jpg         # Image with EXIF data
    ├── sample.jpg.json    # Google Takeout metadata
    └── test_export.zip    # Sample Takeout structure
```

### Test Coverage

Target coverage: >80% on core modules
- `extractor.py` - ~90%
- `metadata.py` - ~95%
- `organizer.py` - ~95%
- `main.py` - ~80%

## Code Quality

### Linting

```bash
# Run ruff linter
make lint

# Or manually
uv run ruff check src/ tests/
```

### Format Checking

```bash
# Check code formatting
uv run ruff format --check src/ tests/

# Auto-format code
uv run ruff format src/ tests/
```

### Type Checking (Optional)

The codebase uses type hints but doesn't currently enforce strict type checking. To add type checking:

```bash
# Install mypy
uv add --dev mypy

# Run type checker
uv run mypy src/photo_organiser/
```

## Build Artifacts

After building, the following directories are created:

```
google-photo-organiser/
├── build/              # Temporary build files (can be deleted)
├── dist/               # Final executable output
│   └── photo-organiser.exe
└── __pycache__/        # Python bytecode cache
```

### Cleaning Build Artifacts

```bash
# Remove all build artifacts
make clean

# Manual cleanup
rm -rf build/ dist/ __pycache__/ .pytest_cache/ .coverage htmlcov/
```

## Distribution

### Packaging for Users

To distribute the application:

1. Build the executable: `make build`
2. Test the executable: `dist/photo-organiser.exe --version`
3. Package the executable:
   ```bash
   # Create distribution package
   mkdir photo-organiser-v0.1.0
   cp dist/photo-organiser.exe photo-organiser-v0.1.0/
   cp README.md photo-organiser-v0.1.0/
   zip -r photo-organiser-v0.1.0-windows.zip photo-organiser-v0.1.0/
   ```

### Release Checklist

Before releasing:

- [ ] All tests pass (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] Version updated in `pyproject.toml` and `main.py`
- [ ] README.md updated with new features/changes
- [ ] Executable tested on clean Windows 10/11 system
- [ ] Test with real Google Takeout export (multi-GB)
- [ ] Verify output structure is correct
- [ ] Check executable size (<50MB)

## Troubleshooting

### Build Fails with Import Errors

**Problem**: PyInstaller can't find certain modules

**Solution**: Add hidden imports to `build.spec`:
```python
hiddenimports=['PIL._tkinter_finder', 'PIL._imaging']
```

### Executable Size Too Large

**Problem**: Executable is >50MB

**Solution**:
- Remove unused dependencies from `pyproject.toml`
- Use `--exclude-module` in PyInstaller
- Check for accidentally bundled data files

### Executable Crashes on Startup

**Problem**: Built executable crashes when run

**Solution**:
- Test in verbose mode: `photo-organiser.exe --verbose`
- Check `photo_organiser.log` for error details
- Verify all dependencies are correctly bundled
- Test with `uv run python -m photo_organiser` first

### Missing DLL on Windows

**Problem**: "DLL not found" error when running executable

**Solution**:
- Install Microsoft Visual C++ Redistributable
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe

## Development Workflow

### Making Changes

1. **Create feature branch**: `git checkout -b feature/my-feature`
2. **Make changes**: Edit source files in `src/photo_organiser/`
3. **Add tests**: Create/update tests in `tests/`
4. **Run tests**: `make test`
5. **Run linter**: `make lint`
6. **Test manually**: `uv run python -m photo_organiser test.zip`
7. **Build executable**: `make build`
8. **Test executable**: `dist/photo-organiser.exe test.zip`
9. **Commit changes**: `git commit -m "feat: add my feature"`

### Code Style

- Follow PEP 8 (enforced by ruff)
- Use type hints for function signatures
- Write docstrings for all public functions (Google style)
- Maximum line length: 100 characters
- Use descriptive variable names

## Advanced Configuration

### Customizing the Build

Edit `build.spec` to customize the build:

```python
# Add application icon
icon='icon.ico'

# Add data files
datas=[('config/', 'config/')],

# Exclude unnecessary modules
excludes=['tkinter', 'matplotlib'],

# Add runtime hooks
runtime_hooks=['hooks/runtime_hook.py'],
```

### Cross-Platform Builds

**Note**: PyInstaller builds are platform-specific. To build for Windows, you must build on Windows.

For cross-platform support:
1. Set up Windows VM or CI/CD pipeline
2. Build on each target platform separately
3. Test thoroughly on each platform

### Optimizing Performance

To optimize the executable:

```bash
# Use UPX compression (reduces size but slower startup)
pyinstaller build.spec --upx-dir=/path/to/upx

# Enable optimizations
uv run python -O -m PyInstaller build.spec
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Executable

on: [push, pull_request]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync
      - name: Run tests
        run: uv run pytest
      - name: Build executable
        run: uv run pyinstaller build.spec
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: photo-organiser-exe
          path: dist/photo-organiser.exe
```

## Getting Help

- **Documentation**: See [README.md](../README.md) for user documentation
- **Issues**: Report bugs or request features on the issue tracker
- **Development**: Check `IMPLEMENTATION_PLAN.md` for development roadmap

## References

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
