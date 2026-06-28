"""
Global Brain Crawler.

Indexes knowledge sources, bookmarks, and local documents
into a searchable brain for the AI ecosystem.
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Any

from revenue_utils import setup_logging, write_json, REVENUE_DIR

logger = setup_logging(__name__)

EXTENSIONS = {".md", ".txt", ".pdf", ".py", ".json", ".html"}
MAX_FILES = 100
INDEX_FILE = os.path.join(REVENUE_DIR, "brain_index.json")


def crawl_directory(root: str) -> List[Dict[str, Any]]:
    """Recursively crawl for indexable files."""
    findings: List[Dict[str, Any]] = []
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
                except (OSError, PermissionError) as e:
                    logger.warning(f"Cannot access {full_path}: {e}")
                    continue

            if len(findings) >= MAX_FILES:
                logger.info(f"Reached max file limit ({MAX_FILES}).")
                break
        if len(findings) >= MAX_FILES:
            break

    return findings


def main() -> None:
    logger.info("Starting Global Brain Crawler...")
    start = time.time()
    findings = crawl_directory(os.path.expanduser("~"))
    elapsed = time.time() - start

    if not findings:
        logger.warning("No indexable files found.")
        return

    logger.info(f"Indexed {len(findings)} files in {elapsed:.2f}s.")

    index: Dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "root": os.path.expanduser("~"),
        "total_files": len(findings),
        "files": findings[:MAX_FILES]
    }

    write_json(INDEX_FILE, index)
    logger.info(f"Brain index saved to {INDEX_FILE}")
    logger.info("Brain Crawler complete.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBrain crawl aborted by user.")
