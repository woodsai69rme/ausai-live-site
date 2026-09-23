"""
Cleanup Agent — Finds and purges junk files, duplicates, old caches, and temp data.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

JUNK_EXTENSIONS = {
    '.log', '.tmp', '.bak', '.old', '.orig', '.swp', '.swo',
    '.pyc', '.pyo', '.cache', '.DS_Store'
}

JUNK_DIRS = {
    '__pycache__', '.pytest_cache', 'node_modules', '.next',
    'dist', 'build', '.cache', 'htmlcov', '.mypy_cache'
}

SAFE_DELETE_PATTERNS = {
    'Thumbs.db', 'desktop.ini', '.DS_Store', 'npm-debug.log',
    'yarn-error.log', 'yarn-debug.log'
}


class CleanupAgent(BaseAgent):
    """Scans for junk files and optionally purges them."""

    def __init__(self):
        super().__init__(agent_id="cleanup-001", agent_type="cleanup")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task format:
        {
            "title": "Clean junk files",
            "type": "cleanup",
            "target": "C:\\Users\\karma",
            "max_depth": 2,
            "dry_run": true,      # true = report only, false = delete
            "extensions": [".log", ".tmp"]  # optional filter
        }
        """
        target = task.get("target", r"C:\Users\karma")
        max_depth = task.get("max_depth", 2)
        dry_run = task.get("dry_run", True)
        ext_filter = set(task.get("extensions", JUNK_EXTENSIONS))

        self.status = "scanning"
        logger.info(f"[{self.agent_id}] Cleanup scan: {target} (dry_run={dry_run})")

        junk_files = []
        total_size = 0
        deleted_count = 0
        root_depth = target.rstrip(os.sep).count(os.sep)

        for dirpath, dirnames, filenames in os.walk(target):
            depth = dirpath.count(os.sep) - root_depth
            if depth >= max_depth:
                dirnames.clear()
                continue

            # Skip protected directories
            dirnames[:] = [d for d in dirnames if d not in {
                '.git', '.vscode', '.gemini', 'AppData', '.ssh', '.env'
            }]

            for fname in filenames:
                filepath = os.path.join(dirpath, fname)
                ext = os.path.splitext(fname)[1].lower()

                is_junk = (
                    ext in ext_filter or
                    fname in SAFE_DELETE_PATTERNS or
                    (ext == '' and fname.startswith('nul'))
                )

                if is_junk:
                    try:
                        size = os.path.getsize(filepath)
                    except OSError:
                        continue

                    junk_files.append({
                        "path": filepath,
                        "size_mb": round(size / (1024 * 1024), 3),
                        "ext": ext or fname
                    })
                    total_size += size

                    if not dry_run:
                        try:
                            os.remove(filepath)
                            deleted_count += 1
                        except OSError as e:
                            logger.warning(f"Could not delete {filepath}: {e}")

        report = {
            "target": target,
            "dry_run": dry_run,
            "junk_files_found": len(junk_files),
            "total_junk_mb": round(total_size / (1024 * 1024), 2),
            "deleted": deleted_count if not dry_run else 0,
            "top_junk": sorted(junk_files, key=lambda x: x["size_mb"], reverse=True)[:30],
            "by_extension": self._group_by_ext(junk_files),
            "scanned_at": datetime.now().isoformat()
        }

        self.save_report(report)
        return report

    def _group_by_ext(self, files: List[Dict]) -> Dict[str, Dict]:
        groups = {}
        for f in files:
            ext = f["ext"]
            if ext not in groups:
                groups[ext] = {"count": 0, "size_mb": 0}
            groups[ext]["count"] += 1
            groups[ext]["size_mb"] = round(groups[ext]["size_mb"] + f["size_mb"], 3)
        return dict(sorted(groups.items(), key=lambda x: x[1]["size_mb"], reverse=True))
