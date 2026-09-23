"""
Revenue Agent — Wraps REVENUE_GENERATORS scripts and dispatches revenue tasks.
"""

import os
import subprocess
import logging
from typing import Dict, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

REVENUE_DIR = r"C:\Users\karma\REVENUE_GENERATORS"

# Registry of known revenue scripts
REVENUE_SCRIPTS = {
    "deploy_revenue": "REVENUE_DEPLOY_ENGINE.py",
    "content_factory": "AUTONOMOUS_CONTENT_FACTORY.py",
    "saas_launcher": "AUTONOMOUS_SAAS_LAUNCHER.py",
    "brain_crawler": "GLOBAL_BRAIN_CRAWLER.py",
    "singularity": "REVENUE_SINGULARITY_ENGINE.py",
    "self_healing": "SELF_HEALING_DAEMON.py",
    "health_check": "SERVICE_HEALTH_MONITOR.py",
}


class RevenueAgent(BaseAgent):
    """Triggers revenue-generating scripts from the REVENUE_GENERATORS directory."""

    def __init__(self):
        super().__init__(agent_id="revenue-001", agent_type="revenue")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a revenue task.

        Task format:
        {
            "title": "Deploy Revenue Engine",
            "type": "revenue",
            "action": "deploy_revenue"
        }
        """
        action = task.get("action", "")
        
        if action == "list":
            return self._list_available()

        if action not in REVENUE_SCRIPTS:
            return {"status": "error", "message": f"Unknown action: {action}. Available: {list(REVENUE_SCRIPTS.keys())}"}

        return self._run_script(action)

    def _list_available(self) -> Dict[str, Any]:
        """List all available revenue scripts and their existence on disk."""
        available = {}
        for key, filename in REVENUE_SCRIPTS.items():
            path = os.path.join(REVENUE_DIR, filename)
            available[key] = {
                "file": filename,
                "exists": os.path.exists(path),
                "path": path
            }
        return {"status": "ok", "scripts": available}

    def _run_script(self, action: str) -> Dict[str, Any]:
        """Run a revenue script and capture output."""
        script = REVENUE_SCRIPTS[action]
        script_path = os.path.join(REVENUE_DIR, script)

        if not os.path.exists(script_path):
            return {"status": "error", "message": f"Script not found: {script_path}"}

        self.status = "executing"
        logger.info(f"[{self.agent_id}] Running revenue script: {action} -> {script_path}")

        try:
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=REVENUE_DIR
            )

            report = {
                "status": "success" if result.returncode == 0 else "failed",
                "action": action,
                "script": script,
                "return_code": result.returncode,
                "stdout": result.stdout[-2000:] if result.stdout else "",
                "stderr": result.stderr[-1000:] if result.stderr else ""
            }

        except subprocess.TimeoutExpired:
            report = {"status": "timeout", "action": action, "script": script}
        except Exception as e:
            report = {"status": "error", "action": action, "message": str(e)}

        self.save_report(report)
        return report
