# Makefile for {{PROJECT_NAME}}
# Python-based research project using uv for dependency management

.PHONY: help data analysis clean test lint install

# Default target
help:
	@echo "Available targets:"
	@echo "  make install   - Install dependencies using uv"
	@echo "  make data      - Acquire and clean data"
	@echo "  make analysis  - Run analysis and generate visualizations"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run code quality checks"
	@echo "  make clean     - Remove generated files"

# Install project dependencies
install:
	uv sync

# Data pipeline
data:
	uv run python scripts/01-acquire.py
	uv run python scripts/02-clean.py

# Analysis pipeline
analysis:
	uv run python scripts/03-analyze.py
	uv run python scripts/04-visualize.py

# Run all pipelines
all: data analysis

# Run tests
test:
	uv run pytest tests/

# Code quality
lint:
	uv run ruff check scripts/ tests/
	uv run ruff format --check scripts/ tests/

# Clean generated files
clean:
	rm -rf data/processed/*
	rm -rf data/output/*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
