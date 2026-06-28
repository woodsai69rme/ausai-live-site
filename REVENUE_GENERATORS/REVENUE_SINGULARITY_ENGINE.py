"""
Revenue Singularity Engine.

Aggregates revenue data from multiple sources and generates
a unified revenue dashboard snapshot.
"""

import os
import json
import logging
from datetime import datetime

# Configuration
TARGET_DIR = r"C:\Users\karma\REVENUE_GENERATORS"
OUTPUT_FILE = os.path.join(TARGET_DIR, "revenue_singularity_snapshot.json")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def aggregate_revenue() -> dict:
    """Aggregate revenue signals from local sources."""
    logger.info("Scanning for revenue signals...")

    signals = {
        "timestamp": datetime.now().isoformat(),
        "sources_checked": [],
        "total_estimated_monthly": 0.0,
        "currency": "AUD",
        "streams": []
    }

    # Check for known revenue files
    potential_sources = [
        ("revenue_stats.json", "stats"),
        ("revenue_content/affiliate_review.md", "affiliate"),
        ("saas_launch_manifests.json", "saas"),
        ("content_plan.json", "content"),
    ]

    for filename, source_type in potential_sources:
        path = os.path.join(TARGET_DIR, filename)
        if os.path.exists(path):
            signals["sources_checked"].append(filename)
            try:
                if filename.endswith(".json"):
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    signals["streams"].append({
                        "source": source_type,
                        "status": "active",
                        "records": len(data) if isinstance(data, list) else 1
                    })
                else:
                    size = os.path.getsize(path)
                    signals["streams"].append({
                        "source": source_type,
                        "status": "active",
                        "size_bytes": size
                    })
            except Exception as e:
                logger.warning(f"Could not read {filename}: {e}")

    logger.info(f"Aggregated {len(signals['streams'])} revenue stream(s).")
    return signals


def main() -> None:
    logger.info("Starting Revenue Singularity Engine...")
    snapshot = aggregate_revenue()

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
        logger.info(f"Revenue snapshot saved to {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"Failed to save snapshot: {e}")
        raise

    logger.info("Revenue Singularity Engine complete.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRevenue aggregation aborted by user.")
