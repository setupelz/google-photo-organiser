#!/usr/bin/env python3
"""
Data Acquisition Script

Purpose: Download or fetch raw data from sources and save to data/raw/

Usage:
    uv run python scripts/01-acquire.py
"""

from pathlib import Path


def main():
    """
    Download raw data from sources.

    Modify this function to fetch data from APIs, download files,
    or read from databases. Save all raw data to data/raw/.
    """
    # Create raw data directory if it doesn't exist
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    # TODO: Implement data acquisition logic
    # Example:
    # import requests
    # response = requests.get("https://example.com/data.csv")
    # with open(raw_dir / "dataset.csv", "wb") as f:
    #     f.write(response.content)

    print("✓ Data acquisition complete")


if __name__ == "__main__":
    main()
