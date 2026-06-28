"""
Self-Healing Daemon.

Monitors critical services and attempts basic recovery
actions when they are detected as down.
"""

import os
import json
import logging
import urllib.request
from datetime import datetime

# Configuration
OUTPUT_FILE = r"C:\Users\karma\REVENUE_GENERATORS\healing_report.json"
SERVICES = [
    {"name": "AI Army", "url": "http://localhost:8001/", "port": 8001},
    {"name": "n8n", "url": "http://localhost:5678/", "port": 5678},
    {"name": "ComfyUI", "url": "http://localhost:8188/", "port": 8188},
    {"name": "Ollama", "url": "http://localhost:11434/api/tags", "port": 11434},
]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def check_service(service: dict) -> dict:
    """Check if a service is responding."""
    result = {
        "name": service["name"],
        "url": service["url"],
        "checked_at": datetime.now().isoformat(),
        "status": "unknown",
        "response_time_ms": None
    }

    try:
        import time
        start = time.time()
        req = urllib.request.Request(service["url"], method="GET")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            _ = resp.read()
        elapsed = (time.time() - start) * 1000
        result["status"] = "healthy"
        result["response_time_ms"] = round(elapsed, 2)
        logger.info(f"  -> {service['name']}: healthy ({result['response_time_ms']}ms)")
    except Exception as e:
        result["status"] = "down"
        result["error"] = str(e)
        logger.warning(f"  -> {service['name']}: down ({e})")

    return result


def attempt_heal(service: dict) -> dict:
    """Attempt a basic healing action for a down service."""
    heal_result = {
        "service": service["name"],
        "attempted_at": datetime.now().isoformat(),
        "action": "none",
        "result": "skipped"
    }

    if service["name"] == "AI Army":
        heal_result["action"] = "would restart python server.py"
    elif service["name"] == "n8n":
        heal_result["action"] = "would docker-compose restart"
    elif service["name"] == "ComfyUI":
        heal_result["action"] = "would restart ComfyUI server"
    elif service["name"] == "Ollama":
        heal_result["action"] = "would restart Ollama service"

    logger.info(f"Healing plan for {service['name']}: {heal_result['action']}")
    return heal_result


def main() -> None:
    logger.info("Starting Self-Healing Daemon scan...")
    health_results = []
    heal_actions = []

    for svc in SERVICES:
        result = check_service(svc)
        health_results.append(result)
        if result["status"] != "healthy":
            heal_actions.append(attempt_heal(svc))

    report = {
        "scan_time": datetime.now().isoformat(),
        "services_checked": len(SERVICES),
        "healthy": sum(1 for r in health_results if r["status"] == "healthy"),
        "down": sum(1 for r in health_results if r["status"] == "down"),
        "health_results": health_results,
        "heal_actions": heal_actions
    }

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Healing report saved to {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
        raise

    logger.info(f"Daemon scan complete. {report['healthy']}/{report['services_checked']} services healthy.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSelf-healing scan aborted by user.")
