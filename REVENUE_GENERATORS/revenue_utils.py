"""
Shared utilities for the REVENUE_GENERATORS suite.

Provides common configuration, logging setup, and helper functions
used across all revenue agent scripts.
"""

import json
import os
import logging
from pathlib import Path
from typing import Final, Any

# Base directory — resolve from user's home for portability
_HOME: Path = Path.home()
REVENUE_DIR: Final[str] = str(_HOME / "REVENUE_GENERATORS")


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Configure consistent logging for revenue scripts."""
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s"
    )
    return logging.getLogger(name)


def ensure_revenue_dir() -> None:
    """Ensure the REVENUE_GENERATORS directory exists."""
    Path(REVENUE_DIR).mkdir(parents=True, exist_ok=True)


def write_json(path: str, data: Any) -> None:
    """Safely write JSON data to a file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
