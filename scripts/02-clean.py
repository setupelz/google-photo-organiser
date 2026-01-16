#!/usr/bin/env python3
"""
Data Cleaning Script

Purpose: Process raw data, validate, transform, and save to data/processed/

Usage:
    uv run python scripts/02-clean.py
"""

from pathlib import Path


def main():
    """
    Clean and process raw data.

    Read from data/raw/, apply transformations, validate data quality,
    and save cleaned datasets to data/processed/.

    NEVER modify files in data/raw/ - keep raw data immutable.
    """
    # Create processed data directory if it doesn't exist
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    raw_dir = Path("data/raw")

    # TODO: Implement data cleaning logic
    # Example:
    # import pandas as pd
    # df = pd.read_csv(raw_dir / "dataset.csv")
    # df_clean = df.dropna().query("value > 0")
    # df_clean.to_parquet(processed_dir / "dataset_clean.parquet")

    print("✓ Data cleaning complete")


if __name__ == "__main__":
    main()
