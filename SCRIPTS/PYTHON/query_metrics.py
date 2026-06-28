"""
Swarm Metrics Telemetry Query Utility.

Asynchronously queries specialized oversight agents for status reports
and aggregates their responses into a unified view.
"""

import asyncio
import httpx
import json
import logging
from typing import Dict, Any, Tuple, List

# Configuration
API_URL = "http://localhost:8000/api/v2/tasks"
HEADERS = {"Authorization": "Bearer army-master-key-2026"}
AGENTS = ["oversight_crypto_hub", "oversight_saas_ops", "oversight_revenue_treasury"]

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def query_agent(client: httpx.AsyncClient, agent_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Dispatch a report request task to a specific agent and poll for results.
    
    Args:
        client: The HTTPX async client instance.
        agent_id: The target agent identifier.
        
    Returns:
        Tuple of (agent_id, result_dict).
    """
    try:
        logger.info(f"Requesting report from {agent_id}...")
        resp = await client.post(
            API_URL,
            json={
                "agent_type": agent_id,
                "action": "report",
                "params": {"query": "Generate a summary metric report of the subsystems you manage. Keep it brief."}
            },
            headers=HEADERS,
            timeout=30.0
        )
        resp.raise_for_status()
        task_data = resp.json()
        task_id = task_data.get("id")
        
        if not task_id:
            return agent_id, {"error": f"No task ID returned from orchestrator: {task_data}"}
            
        # Poll for completion (up to 30 seconds)
        for i in range(15):
            await asyncio.sleep(2)
            poll_resp = await client.get(f"http://localhost:8000/api/v2/tasks/{task_id}", headers=HEADERS)
            if poll_resp.status_code == 200:
                status_data = poll_resp.json()
                status = status_data.get("status")
                if status == "completed":
                    logger.info(f"Task {task_id} ({agent_id}) completed successfully.")
                    return agent_id, status_data
                elif status == "failed":
                    logger.error(f"Task {task_id} ({agent_id}) failed.")
                    return agent_id, status_data
            else:
                logger.warning(f"Polling error for {task_id}: HTTP {poll_resp.status_code}")
                
        return agent_id, {"error": "Timeout waiting for background task."}
    except httpx.HTTPError as http_err:
        return agent_id, {"error": f"HTTP Error: {http_err}"}
    except Exception as e:
        logger.error(f"Unexpected error querying {agent_id}: {e}")
        return agent_id, {"error": str(e)}

async def main() -> None:
    """Main execution loop for telemetry aggregation."""
    print("\n" + "="*40)
    print("   SWARM METRICS TELEMETRY REQUEST   ")
    print("="*40 + "\n")
    
    async with httpx.AsyncClient() as client:
        tasks = [query_agent(client, a) for a in AGENTS]
        results = await asyncio.gather(*tasks)
        
        for agent_id, res in results:
            print(f"\n[AGENT: {agent_id.upper()}]")
            if "error" in res:
                print(f"Status: ❌ ERROR")
                print(f"Detail: {res['error']}")
            else:
                print(f"Status: ✅ {res.get('status', 'Unknown').upper()}")
                print(json.dumps(res, indent=2))
    print("\n" + "="*40)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTelemetry request cancelled by user.")
