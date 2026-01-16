

# GitHub Actions Windows Build

**Status:** ✅ Implemented
**Created:** 2026-01-17
**Completed:** 2026-01-17
**Scope:** Project: google-photo-organiser

---

## Problem

The project requires a Windows executable (`.exe`) built with PyInstaller. Currently, the build can only be tested manually on a Windows machine. This creates friction because:

1. Development happens on macOS
2. PyInstaller produces platform-specific executables (no cross-compilation)
3. Manual Windows access is required for every build verification

---

## Solution

Create a GitHub Actions workflow that:
1. Builds the Windows executable on `windows-latest` runner
2. Runs tests on Windows to verify functionality
3. Uploads the built `.exe` as a release artifact
4. Triggers on push to main and tagged releases

---

## Requirements

### Workflow Triggers
- [ ] Build on push to `main` branch
- [ ] Build on pull requests to `main`
- [ ] Build on version tags (`v*.*.*`)
- [ ] Allow manual trigger (`workflow_dispatch`)

### Build Job
- [ ] Use `windows-latest` runner
- [ ] Install Python 3.11+
- [ ] Install dependencies with `uv` or `pip`
- [ ] Run test suite (`pytest`)
- [ ] Build executable with PyInstaller using `build.spec`
- [ ] Verify executable runs (`photo-organiser.exe --help`)

### Artifacts
- [ ] Upload built executable as workflow artifact
- [ ] Artifact named `photo-organiser-windows` with `.exe` inside
- [ ] Retain artifacts for 30 days (or until release)

### Release Automation (on tags)
- [ ] Create GitHub Release when `v*` tag is pushed
- [ ] Attach `photo-organiser.exe` to release
- [ ] Auto-generate release notes from commits

---

## Implementation

### File Structure

.github/
└── workflows/
    └── build-windows.yml

### Workflow

yaml
name: Build Windows Executable

on:
  push:
    branches: main
    tags: 'v*'
  pullrequest:
    branches: [main]
  workflowdispatch:

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -e .dev
          pip install pyinstaller

      - name: Run tests
        run: pytest

      - name: Build executable
        run: pyinstaller build.spec

      - name: Verify executable
        run: dist/photo-organiser.exe --help

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: photo-organiser-windows
          path: dist/photo-organiser.exe

  release:
    needs: build
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          name: photo-organiser-windows

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: photo-organiser.exe
          generatereleasenotes: true

---

## Success Criteria

- [ ] Workflow runs successfully on push to main
- [ ] Tests pass on Windows runner
- [ ] Executable builds without errors
- [ ] Built `.exe` passes smoke test (`--help` runs)
- [ ] Artifacts downloadable from workflow run
- [ ] Tagged releases include the `.exe` attachment

---

## Constraints

- Windows runner has ~14GB disk space available
- Build should complete in under 10 minutes
- Use Python 3.11 to match local development
- No secrets required (public artifact)

---

## Future Enhancements (Out of Scope)

- Multi-platform builds (macOS, Linux)
- Code signing for Windows executable
- Automated version bumping
- Caching for faster builds


---