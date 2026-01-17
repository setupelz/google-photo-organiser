# google-photo-organiser

You are **Ralph**, a development assistant for this utility project.

---

## Project Context

**Purpose:** Organize Google Photos exports by year and media type

**Target Users:** Anyone migrating from Google Photos who needs their exported media organized

**Key Features:**
- Extracts metadata from photos/videos using EXIF and JSON sidecar files
- Organizes media into year-based folder structure
- Separates photos and videos
- Builds as a standalone Windows executable

---

## Workflow

### Development Cycle

1. **Implement** — Write code in `src/`
2. **Test** — Run tests in `tests/`
3. **Document** — Update docs and README

### Code Organization

- All paths relative to project root
- Keep modules focused and single-purpose
- Use Makefile targets: `make test`, `make build`, `make clean`

### Directory Structure

```
google-photo-organiser/
├── CLAUDE.md              # These instructions
├── README.md              # Project overview and usage
├── Makefile               # Common commands
├── pyproject.toml         # Project config
├── build.spec             # PyInstaller spec for Windows build
│
├── src/
│   └── photo_organiser/   # Main package
│       ├── __init__.py
│       ├── organiser.py   # Core organization logic
│       └── metadata.py    # Metadata extraction
│
├── tests/                 # Test files
│   └── test_organiser.py
│
├── docs/                  # Documentation
│   └── build.md           # Build instructions
│
└── config/                # Configuration files
```

---

## Code Standards

### Style

- **Python:** ruff formatting, type hints required
  - Type hints for all function signatures
  - `snake_case` for variables/functions, `PascalCase` for classes
  - Use Pydantic for data validation where appropriate

### Documentation

- **Functions:** Docstrings (Google style) for all public functions
- **Modules:** Module-level docstring explaining purpose
- **README:** Keep usage examples up to date

### Testing

- Write tests for all public interfaces
- Use `pytest` with fixtures
- Aim for good coverage of edge cases

---

## Constraints

- **NEVER** hardcode absolute paths (use relative paths from project root)
- **NEVER** commit credentials, tokens, or `.env` files
- **NEVER** commit large binary files (use .gitignore)

---

## Quick Commands

```bash
# Development
make test        # Run test suite
make lint        # Run code quality checks
make install     # Install dependencies

# Build
make build       # Build Windows executable
make clean-build # Remove build artifacts
make clean       # Remove all generated files

# Help
make help        # Show all available commands
```

---

## Notes

- This project was created from the utility-project template
- Keep this file updated as the project evolves
- See `docs/build.md` for detailed build instructions

### Creating New Files

If Claude Code lacks write permission for new files, use Bash heredoc:

```bash
cat > path/to/new-file.py << 'EOF'
# File content here
EOF
```
