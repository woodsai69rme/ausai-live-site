"""
GitHub Agent — Syncs local repos to GitHub using the user's PAT.
"""

import os
import subprocess
import logging
from typing import Dict, Any, List
from datetime import datetime
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Load from .env or environment
GITHUB_PAT = os.environ.get("GITHUB_PAT", "")
GITHUB_USER = "woodsai69rme"  # Derived from gocodeo email in settings


class GitHubAgent(BaseAgent):
    """Manages local git repos — init, commit, push to GitHub."""

    def __init__(self):
        super().__init__(agent_id="github-001", agent_type="github")
        self._load_pat()

    def _load_pat(self):
        """Try to load PAT from .env file."""
        global GITHUB_PAT
        if not GITHUB_PAT:
            env_path = r"C:\Users\karma\.env"
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith("GITHUB_PAT="):
                            GITHUB_PAT = line.split("=", 1)[1].strip()
                            break

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task format:
        {
            "title": "Sync repos",
            "type": "github",
            "action": "scan" | "sync" | "status",
            "target": "C:\\Users\\karma"  (for scan)
            "repos": ["C:\\path\\to\\repo"]  (for sync)
        }
        """
        action = task.get("action", "scan")
        self.status = "working"

        if action == "scan":
            return self._scan_repos(task.get("target", r"C:\Users\karma"))
        elif action == "sync":
            return self._sync_repos(task.get("repos", []))
        elif action == "status":
            return self._repo_status(task.get("repos", []))
        else:
            return {"error": f"Unknown action: {action}"}

    def _scan_repos(self, root: str) -> Dict[str, Any]:
        """Find all git repos in a directory."""
        repos = []
        root_depth = root.rstrip(os.sep).count(os.sep)

        for dirpath, dirnames, filenames in os.walk(root):
            depth = dirpath.count(os.sep) - root_depth
            if depth >= 2:
                dirnames.clear()
                continue

            dirnames[:] = [d for d in dirnames if d not in {
                'node_modules', '.cache', 'AppData', '.npm', '.pnpm-store'
            }]

            if '.git' in dirnames or '.git' in os.listdir(dirpath):
                name = os.path.basename(dirpath)
                has_remote = self._has_remote(dirpath)
                repos.append({
                    "name": name,
                    "path": dirpath,
                    "has_remote": has_remote
                })

        report = {
            "action": "scan",
            "total_repos": len(repos),
            "with_remote": sum(1 for r in repos if r["has_remote"]),
            "without_remote": sum(1 for r in repos if not r["has_remote"]),
            "repos": repos,
            "scanned_at": datetime.now().isoformat()
        }
        self.save_report(report)
        return report

    def _has_remote(self, repo_path: str) -> bool:
        """Check if a repo has a remote configured."""
        try:
            result = subprocess.run(
                ['git', 'remote', '-v'],
                cwd=repo_path,
                capture_output=True, text=True, timeout=5
            )
            return bool(result.stdout.strip())
        except Exception:
            return False

    def _repo_status(self, repos: List[str]) -> Dict[str, Any]:
        """Get git status for specified repos."""
        statuses = []
        for repo in repos:
            if not os.path.isdir(repo):
                statuses.append({"path": repo, "error": "not found"})
                continue
            try:
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=repo, capture_output=True, text=True, timeout=5
                )
                changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                statuses.append({
                    "path": repo,
                    "name": os.path.basename(repo),
                    "uncommitted_changes": len(changes),
                    "clean": len(changes) == 0
                })
            except Exception as e:
                statuses.append({"path": repo, "error": str(e)})

        report = {"action": "status", "repos": statuses}
        self.save_report(report)
        return report

    def _sync_repos(self, repos: List[str]) -> Dict[str, Any]:
        """Commit and push repos to their remotes."""
        results = []
        for repo in repos:
            if not os.path.isdir(repo):
                results.append({"path": repo, "status": "not found"})
                continue

            name = os.path.basename(repo)
            try:
                # Stage all
                subprocess.run(['git', 'add', '-A'], cwd=repo, capture_output=True, timeout=10)

                # Commit
                msg = f"Auto-sync {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                commit = subprocess.run(
                    ['git', 'commit', '-m', msg],
                    cwd=repo, capture_output=True, text=True, timeout=10
                )

                # Push
                push = subprocess.run(
                    ['git', 'push', 'origin', 'main'],
                    cwd=repo, capture_output=True, text=True, timeout=30
                )

                results.append({
                    "name": name,
                    "committed": commit.returncode == 0,
                    "pushed": push.returncode == 0,
                    "message": push.stdout[:200] or push.stderr[:200]
                })
            except Exception as e:
                results.append({"name": name, "status": "error", "message": str(e)})

        report = {"action": "sync", "results": results}
        self.save_report(report)
        return report
