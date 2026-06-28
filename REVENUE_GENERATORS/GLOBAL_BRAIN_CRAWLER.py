"""
Global Brain Crawler.

Indexes knowledge sources, bookmarks, and local documents
into a searchable brain for the AI ecosystem.
"""

import os
import json
import logging
from datetime import datetime

# Configuration
TARGET_DIR = r"C:\Users\karma"
INDEX_FILE = r"C:\Users\karma\REVENUE_GENERATORS\brain_index.json"
EXTENSIONS = {".md", ".txt", ".pdf", ".py", ".json", ".html"}
MAX_FILES = 100

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def crawl_directory(root: str) -> list:
    """Recursively crawl for indexable files."""
    findings = []
    logger.info(f"Crawling {root} for knowledge sources...")

    if not os.path.exists(root):
        logger.error(f"Root directory {root} not found.")
        return findings

    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            _, ext = os.path.splitext(fname)
            if ext.lower() in EXTENSIONS:
                full_path = os.path.join(dirpath, fname)
                try:
                    size = os.path.getsize(full_path)
                    findings.append({
                        "path": full_path,
                        "name": fname,
                        "extension": ext,
                        "size_bytes": size,
                        "indexed_at": datetime.now().isoformat()
                    })
                except (OSError, PermissionError):
                    continue

            if len(findings) >= MAX_FILES:
                logger.info(f"Reached max file limit ({MAX_FILES}).")
                break
        if len(findings) >= MAX_FILES:
            break

    return findings


def main() -> None:
    logger.info("Starting Global Brain Crawler...")
    findings = crawl_directory(TARGET_DIR)

    if not findings:
        logger.warning("No indexable files found.")
        return

    logger.info(f"Indexed {len(findings)} files.")

    index = {
        "generated_at": datetime.now().isoformat(),
        "root": TARGET_DIR,
        "total_files": len(findings),
        "files": findings[:MAX_FILES]
    }

    try:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
        logger.info(f"Brain index saved to {INDEX_FILE}")
    except Exception as e:
        logger.error(f"Failed to save index: {e}")
        raise

    logger.info("Brain Crawler complete.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBrain crawl aborted by user.")
