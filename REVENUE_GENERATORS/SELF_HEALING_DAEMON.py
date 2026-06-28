"""
Self-Healing Daemon.

Monitors critical services and plans recovery actions
when they are detected as down.
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Any

import httpx

from revenue_utils import setup_logging, write_json, REVENUE_DIR

logger = setup_logging(__name__)

OUTPUT_FILE = os.path.join(REVENUE_DIR, "healing_report.json")

SERVICES: List[Dict[str, Any]] = [
    {"name": "AI Army", "url": "http://localhost:8001/", "port": 8001},
    {"name": "n8n", "url": "http://localhost:5678/", "port": 5678},
    {"name": "ComfyUI", "url": "http://localhost:8188/", "port": 8188},
    {"name": "Ollama", "url": "http://localhost:11434/api/tags", "port": 11434},
]


def check_service(service: Dict[str, Any]) -> Dict[str, Any]:
    """Check if a service is responding."""
    result: Dict[str, Any] = {
        "name": service["name"],
        "url": service["url"],
        "checked_at": datetime.now().isoformat(),
        "status": "unknown",
        "response_time_ms": None
    }

    try:
        start = time.time()
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(service["url"])
            resp.raise_for_status()
        elapsed = (time.time() - start) * 1000
        result["status"] = "healthy"
        result["response_time_ms"] = round(elapsed, 2)
        logger.info(f"  -> {service['name']}: healthy ({result['response_time_ms']}ms)")
    except Exception as e:
        result["status"] = "down"
        result["error"] = str(e)
        logger.warning(f"  -> {service['name']}: down ({e})")

    return result


def plan_heal(service: Dict[str, Any]) -> Dict[str, Any]:
    """Plan a healing action for a down service."""
    heal_result: Dict[str, Any] = {
        "service": service["name"],
        "planned_at": datetime.now().isoformat(),
        "action": "none",
        "result": "plan_created"
    }

    if service["name"] == "AI Army":
        heal_result["action"] = "restart python server.py"
    elif service["name"] == "n8n":
        heal_result["action"] = "docker-compose restart"
    elif service["name"] == "ComfyUI":
        heal_result["action"] = "restart ComfyUI server"
    elif service["name"] == "Ollama":
        heal_result["action"] = "restart Ollama service"

    logger.info(f"Healing plan for {service['name']}: {heal_result['action']}")
    return heal_result


def main() -> None:
    logger.info("Starting Self-Healing Daemon scan...")
    health_results: List[Dict[str, Any]] = []
    heal_actions: List[Dict[str, Any]] = []

    for svc in SERVICES:
        result = check_service(svc)
        health_results.append(result)
        if result["status"] != "healthy":
            heal_actions.append(plan_heal(svc))

    report: Dict[str, Any] = {
        "scan_time": datetime.now().isoformat(),
        "services_checked": len(SERVICES),
        "healthy": sum(1 for r in health_results if r["status"] == "healthy"),
        "down": sum(1 for r in health_results if r["status"] == "down"),
        "health_results": health_results,
        "heal_actions": heal_actions
    }

    write_json(OUTPUT_FILE, report)
    logger.info(f"Healing report saved to {OUTPUT_FILE}")
    logger.info(f"Daemon scan complete. {report['healthy']}/{report['services_checked']} services healthy.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSelf-healing scan aborted by user.")
