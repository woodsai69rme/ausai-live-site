"""
Monitor Agent — Watches system resources and produces health reports.
"""

import os
import platform
import logging
from typing import Dict, Any
from datetime import datetime
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MonitorAgent(BaseAgent):
    """Monitors CPU, RAM, disk, and running processes."""

    def __init__(self):
        super().__init__(agent_id="monitor-001", agent_type="monitor")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task format:
        {
            "title": "System Health Check",
            "type": "monitor",
            "checks": ["disk", "memory", "ports", "processes"]
        }
        """
        checks = task.get("checks", ["disk", "memory", "system"])
        self.status = "monitoring"
        
        report = {"timestamp": datetime.now().isoformat(), "checks": {}}

        if "disk" in checks:
            report["checks"]["disk"] = self._check_disk()
        if "memory" in checks:
            report["checks"]["memory"] = self._check_memory()
        if "system" in checks:
            report["checks"]["system"] = self._check_system()
        if "ports" in checks:
            report["checks"]["ports"] = self._check_ports()

        self.save_report(report)
        return report

    def _check_disk(self) -> Dict[str, Any]:
        """Check disk usage for common drives."""
        drives = {}
        for letter in ['C', 'D', 'X']:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    import shutil
                    total, used, free = shutil.disk_usage(drive)
                    drives[drive] = {
                        "total_gb": round(total / (1024**3), 1),
                        "used_gb": round(used / (1024**3), 1),
                        "free_gb": round(free / (1024**3), 1),
                        "used_pct": round(used / total * 100, 1)
                    }
                except Exception as e:
                    drives[drive] = {"error": str(e)}
        return drives

    def _check_memory(self) -> Dict[str, Any]:
        """Get memory info via OS commands."""
        try:
            import subprocess
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json'],
                capture_output=True, text=True, timeout=10
            )
            import json
            data = json.loads(result.stdout)
            total_mb = int(data['TotalVisibleMemorySize']) / 1024
            free_mb = int(data['FreePhysicalMemory']) / 1024
            return {
                "total_gb": round(total_mb / 1024, 1),
                "free_gb": round(free_mb / 1024, 1),
                "used_gb": round((total_mb - free_mb) / 1024, 1),
                "used_pct": round((total_mb - free_mb) / total_mb * 100, 1)
            }
        except Exception as e:
            return {"error": str(e)}

    def _check_system(self) -> Dict[str, Any]:
        """Basic system info."""
        return {
            "os": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": platform.python_version(),
            "hostname": platform.node()
        }

    def _check_ports(self) -> Dict[str, Any]:
        """Check if key services are listening."""
        import socket
        ports = {
            8001: "AI Army",
            5000: "Dashboard API",
            3142: "God-Mode",
            6969: "Claude Router",
            6972: "JEW System"
        }
        results = {}
        for port, name in ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            results[f"{port} ({name})"] = "LISTENING" if result == 0 else "CLOSED"
            sock.close()
        return results
