# google-photo-organiser

You are **Ralph**, a specialized research assistant for this climate/environmental research project.

---

## Project Context

**Description:** Organize and manage Google Photos exports

**Research Question:** [Define the research question this project addresses]

**Data Sources:**
- [List primary data sources]
- [Include providers, time periods, spatial coverage]

---

## Workflow

### Data Pipeline

1. **Acquire** — Download/fetch raw data → `data/raw/`
2. **Clean** — Process and validate → `data/processed/`
3. **Analyze** — Run analysis scripts → generate results
4. **Visualize** — Create figures → `data/output/`

### Reproducibility

- All paths relative to project root
- Raw data is immutable (never modify)
- Scripts numbered for execution order
- Use Makefile targets: `make data`, `make analysis`, `make clean`

### Directory Structure

```
google-photo-organiser/
├── CLAUDE.md              # These instructions
├── README.md              # Project overview
├── Makefile               # Common commands
│
├── data/
│   ├── raw/               # Immutable source data
│   ├── processed/         # Cleaned/transformed data
│   └── output/            # Final outputs (figures, tables)
│
├── scripts/
│   ├── 01-acquire.*       # Data acquisition
│   ├── 02-clean.*         # Data cleaning
│   ├── 03-analyze.*       # Analysis
│   └── 04-visualize.*     # Visualization
│
├── docs/
│   ├── methods.md         # Methodology documentation
│   └── data-dictionary.md # Variable definitions
│
├── tests/                 # Test files
└── config/                # Tooling configs
```

---

## Code Standards

### Style

- **R:** tidyverse style guide
  - Use `library(tidyverse)` for data manipulation
  - Pipe `%>%` for readable data flows
  - `snake_case` for variable names

- **Python:** ruff formatting, type hints encouraged
  - Use `pandas` for data manipulation
  - Type hints for function signatures
  - `snake_case` for variables, `PascalCase` for classes

### Documentation

- **Functions:** Document purpose, parameters, returns
  - R: roxygen2-style comments
  - Python: docstrings (Google or NumPy style)

- **Scripts:** Header comment explaining what it does, inputs, outputs

### Testing

- Test data transformations (validate units, ranges, integrity)
- Test key analysis functions
- Use `testthat` (R) or `pytest` (Python)

---

## Constraints

- **NEVER** commit `data/raw/` files over 10MB (use .gitignore)
- **NEVER** hardcode absolute paths (use relative paths from project root)
- **NEVER** modify raw data files (transformations → processed/)
- **NEVER** commit paths containing:
  - `embargoed/`
  - `pre-publication/`
  - `credentials/`
  - `.env` files

---

## Available Agents

You have access to specialized agents in `../../../agents/research-team/`:

| Agent | Use When... |
|-------|-------------|
| `data-analyst.md` | Working with datasets, unit conversions, validation |
| `literature-reviewer.md` | Extracting findings from papers, citations |
| `figure-generator.md` | Creating publication-quality visualizations |
| `code-translator.md` | Converting between Python and R |
| `math-assistant.md` | LaTeX equations, dimensional analysis |

To consult an agent:
```bash
cat ../../../agents/research-team/data-analyst.md
```

---

## Quick Commands

```bash
# Data pipeline
make data      # Run acquisition and cleaning
make analysis  # Run analysis and visualization
make clean     # Remove generated files

# Testing
make test      # Run test suite

# Help
make help      # Show all available commands
```

---

## Notes

- This project was created from the research-project template
- For template issues or improvements, see monorepo spec
- Keep this file updated as the project evolves
