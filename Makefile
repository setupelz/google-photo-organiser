# Makefile for Google Photo Organiser
# Windows executable builder for organizing Google Takeout exports

.PHONY: help build clean-build test lint install

# Default target
help:
	@echo "Available targets:"
	@echo "  make install     - Install dependencies using uv"
	@echo "  make build       - Build Windows executable with PyInstaller"
	@echo "  make clean-build - Remove build artifacts"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run code quality checks"
	@echo "  make clean       - Remove all generated files"

# Install project dependencies
install:
	uv sync

# Build Windows executable
build: clean-build
	@echo "Building photo-organiser.exe..."
	uv run pyinstaller build.spec
	@echo "Build complete: dist/photo-organiser.exe"

# Clean build artifacts
clean-build:
	@echo "Cleaning previous build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -f *.spec~

# Run tests
test:
	uv run pytest tests/

# Code quality
lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

# Clean all generated files
clean: clean-build
	rm -rf data/output/*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
