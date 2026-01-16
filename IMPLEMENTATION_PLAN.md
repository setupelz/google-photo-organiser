# Implementation Plan

**Generated:** 2026-01-17
**Spec:** `specs/windows-build.md`

---

## Current Focus: GitHub Actions Windows Build

Implement GitHub Actions workflow to build Windows executable automatically on Windows runners.

---

## Task Checklist

### Phase 1: Create GitHub Actions Workflow

- [x] Create `.github/workflows/` directory structure
- [ ] Create `build-windows.yml` workflow file
- [ ] Configure workflow triggers (push, PR, tags, manual dispatch)
- [ ] Set up Windows runner with Python 3.11
- [ ] Add dependency installation step using pip and uv
- [ ] Add test execution step
- [ ] Add PyInstaller build step using `build.spec`
- [ ] Add executable verification step (smoke test with `--help`)
- [ ] Configure artifact upload for built executable

### Phase 2: Release Automation

- [ ] Add release job that depends on successful build
- [ ] Configure release job to trigger only on version tags
- [ ] Add artifact download step in release job
- [ ] Add GitHub Release creation step
- [ ] Configure release to attach the `.exe` file
- [ ] Enable auto-generated release notes

### Phase 3: Documentation

- [ ] Update README with CI/CD badge
- [ ] Document release process (tagging workflow)
- [ ] Document artifact download process for testing

---

## Critical Files

1. `.github/workflows/build-windows.yml` — Main workflow definition
2. `build.spec` — Existing PyInstaller spec file (already present)
3. `pyproject.toml` — Project dependencies (already present)

---

## Workflow Structure

The workflow will have two jobs:

**Build Job:**
- Runs on: `windows-latest`
- Triggers: push to main, PRs, tags, manual dispatch
- Steps: checkout → setup Python → install deps → run tests → build exe → verify → upload artifact

**Release Job:**
- Runs on: `ubuntu-latest`
- Triggers: only on version tags (`v*`)
- Depends on: successful build job
- Steps: download artifact → create GitHub release → attach exe

---

## Assumptions

- Using Python 3.11 to match local development environment
- Using pip for dependency installation (standard on GitHub runners)
- Workflow will use `pip install -e .[dev]` to install project + dev dependencies
- PyInstaller will be installed separately via pip
- Existing `build.spec` file is correctly configured for GitHub Actions
- No code signing required (out of scope)
- Artifact retention: 30 days default (GitHub Actions standard)
- Build time expected under 10 minutes

---

## Verification

After implementation:
- Push to main branch → workflow runs, artifact uploaded
- Open PR → workflow runs on PR
- Create tag `v0.1.0` → workflow builds, creates release with attached exe
- Manual trigger via GitHub UI → workflow runs on demand
- Downloaded exe runs successfully with `--help` flag

---

## Notes

- This completes the Windows build automation requirement
- Manual Windows testing of full functionality (processing zip files) remains out of scope
- Once implemented, spec status should be updated to `✅ Complete`
