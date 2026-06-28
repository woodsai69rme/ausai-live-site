"""
Autonomous SaaS Launcher.

Scans for SaaS-ready projects and prepares launch checklists,
environment configs, and deployment manifests.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Set

from revenue_utils import setup_logging, ensure_revenue_dir, write_json, REVENUE_DIR

logger = setup_logging(__name__)

VALID_MARKERS: Set[str] = {"package.json", "main.py", "app.py", "pyproject.toml", "requirements.txt"}


def find_saas_projects() -> List[Dict[str, Any]]:
    """Find directories that look like deployable SaaS projects."""
    projects: List[Dict[str, Any]] = []
    logger.info(f"Scanning {REVENUE_DIR} for SaaS projects...")

    if not os.path.exists(REVENUE_DIR):
        logger.error(f"Target directory {REVENUE_DIR} not found.")
        return projects

    try:
        items = os.listdir(REVENUE_DIR)
    except Exception as e:
        logger.error(f"Failed to list {REVENUE_DIR}: {e}")
        return projects

    for item in items:
        full_path = os.path.join(REVENUE_DIR, item)
        if os.path.isdir(full_path):
            try:
                files = set(os.listdir(full_path))
                if any(marker in files for marker in VALID_MARKERS):
                    projects.append({
                        "name": item,
                        "path": full_path,
                        "markers_found": list(files & VALID_MARKERS)
                    })
            except PermissionError:
                logger.warning(f"Permission denied accessing {full_path}")
                continue

    return projects


def generate_launch_manifest(project: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a launch checklist for a project."""
    return {
        "project": project["name"],
        "generated_at": datetime.now().isoformat(),
        "checklist": [
            {"step": 1, "task": "Validate environment variables", "status": "pending"},
            {"step": 2, "task": "Run test suite", "status": "pending"},
            {"step": 3, "task": "Build Docker image", "status": "pending"},
            {"step": 4, "task": "Push to container registry", "status": "pending"},
            {"step": 5, "task": "Deploy to production", "status": "pending"},
            {"step": 6, "task": "Configure monitoring and alerts", "status": "pending"},
        ],
        "status": "ready_for_launch"
    }


def main() -> None:
    logger.info("Starting Autonomous SaaS Launcher...")
    ensure_revenue_dir()
    projects = find_saas_projects()

    if not projects:
        logger.warning("No SaaS projects found.")
        return

    logger.info(f"Found {len(projects)} potential SaaS project(s).")

    manifests: List[Dict[str, Any]] = []
    for proj in projects:
        manifest = generate_launch_manifest(proj)
        manifests.append(manifest)
        logger.info(f"Prepared launch manifest for: {proj['name']}")

    output_path = os.path.join(REVENUE_DIR, "saas_launch_manifests.json")
    write_json(output_path, manifests)
    logger.info(f"Launch manifests saved to {output_path}")
    logger.info("SaaS Launcher complete.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaaS launch preparation aborted by user.")
