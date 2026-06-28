"""
Revenue Singularity Engine.

Aggregates revenue data from multiple sources and generates
a unified revenue dashboard snapshot.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple

from revenue_utils import setup_logging, write_json, REVENUE_DIR

logger = setup_logging(__name__)

OUTPUT_FILE = os.path.join(REVENUE_DIR, "revenue_singularity_snapshot.json")

POTENTIAL_SOURCES: List[Tuple[str, str]] = [
    ("revenue_stats.json", "stats"),
    ("revenue_content/affiliate_review.md", "affiliate"),
    ("saas_launch_manifests.json", "saas"),
    ("content_plan.json", "content"),
]


def aggregate_revenue() -> Dict[str, Any]:
    """Aggregate revenue signals from local sources."""
    logger.info("Scanning for revenue signals...")

    signals: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "sources_checked": [],
        "total_estimated_monthly": 0.0,
        "currency": "AUD",
        "streams": []
    }

    for filename, source_type in POTENTIAL_SOURCES:
        path = os.path.join(REVENUE_DIR, filename)
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
    write_json(OUTPUT_FILE, snapshot)
    logger.info(f"Revenue snapshot saved to {OUTPUT_FILE}")
    logger.info("Revenue Singularity Engine complete.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRevenue aggregation aborted by user.")
