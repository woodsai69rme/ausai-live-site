"""
Recon Agent — Filesystem scanner that audits directories and creates reports.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ReconAgent(BaseAgent):
    """Scans directories, catalogs files, and produces audit reports."""

    def __init__(self):
        super().__init__(agent_id="recon-001", agent_type="recon")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a recon scan.
        
        Task format:
        {
            "title": "Scan Downloads",
            "type": "recon",
            "target": "C:\\Users\\karma\\Downloads",
            "max_depth": 2
        }
        """
        target = task.get("target") or "C:\\Users\\karma"
        max_depth = task.get("max_depth", 2)
        
        self.status = "scanning"
        logger.info(f"[{self.agent_id}] Scanning: {target} (depth={max_depth})")

        results = self._scan_directory(target, max_depth)
        
        report = {
            "scan_target": target,
            "max_depth": max_depth,
            "total_files": results["total_files"],
            "total_dirs": results["total_dirs"],
            "total_size_mb": round(results["total_size"] / (1024 * 1024), 2),
            "largest_files": results["largest_files"][:20],
            "file_types": dict(sorted(results["extensions"].items(), key=lambda x: x[1], reverse=True)[:30]),
            "scanned_at": datetime.now().isoformat()
        }

        filename = self.save_report(report)
        return {"report_file": filename, **report}

    def _scan_directory(self, root: str, max_depth: int) -> Dict[str, Any]:
        """Walk a directory tree up to max_depth and collect stats."""
        stats = {
            "total_files": 0,
            "total_dirs": 0,
            "total_size": 0,
            "extensions": {},
            "largest_files": []
        }

        if not root or not os.path.exists(root):
            root = os.path.expanduser("~")
            logger.warning(f"Invalid target path, falling back to: {root}")

        root_depth = root.rstrip(os.sep).count(os.sep)

        for dirpath, dirnames, filenames in os.walk(root):
            current_depth = dirpath.count(os.sep) - root_depth
            if current_depth >= max_depth:
                dirnames.clear()
                continue

            # Skip common junk directories
            dirnames[:] = [d for d in dirnames if d not in {
                'node_modules', '.git', '__pycache__', '.venv', 'venv', 
                '.next', 'dist', 'build', '.cache'
            }]

            stats["total_dirs"] += len(dirnames)

            for fname in filenames:
                filepath = os.path.join(dirpath, fname)
                try:
                    size = os.path.getsize(filepath)
                except OSError:
                    continue

                stats["total_files"] += 1
                stats["total_size"] += size

                ext = os.path.splitext(fname)[1].lower() or "(no ext)"
                stats["extensions"][ext] = stats["extensions"].get(ext, 0) + 1

                stats["largest_files"].append({
                    "path": filepath,
                    "size_mb": round(size / (1024 * 1024), 2)
                })

        # Sort largest files
        stats["largest_files"].sort(key=lambda x: x["size_mb"], reverse=True)
        return stats
