"""
Revenue Generator Deployment Engine.

Scans for deployable revenue-focused projects and triggers their
deployment via the J.A.R.V.I.S. Kernel API.
"""

import os
import httpx
import asyncio
import logging
from typing import List, Set

# Configuration
API_URL = "http://localhost:8000/api/v3/revenue/deploy"
TARGET_DIR = r"C:\Users\karma\REVENUE_GENERATORS"
VALID_MARKERS: Set[str] = {"package.json", "main.py", "app.py", "pyproject.toml", "Cargo.toml"}
MAX_CONCURRENT_DEPLOYMENTS = 3
AUTH_HEADERS = {"Authorization": "Bearer army-master-key-2026"}

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def find_and_deploy() -> None:
    """
    Search for valid project directories and trigger deployment for a limited set.
    """
    deployable: List[str] = []
    logger.info(f"Scanning {TARGET_DIR} for revenue projects...")
    
    if not os.path.exists(TARGET_DIR):
        logger.error(f"Target directory {TARGET_DIR} not found.")
        return

    # Find directories with valid entry points (markers)
    try:
        items = os.listdir(TARGET_DIR)
    except Exception as e:
        logger.error(f"Failed to list {TARGET_DIR}: {e}")
        return

    for item in items:
        full_path = os.path.join(TARGET_DIR, item)
        if os.path.isdir(full_path):
            try:
                files = set(os.listdir(full_path))
                if any(marker in files for marker in VALID_MARKERS):
                    deployable.append(full_path)
            except PermissionError:
                logger.warning(f"Permission denied accessing {full_path}")
                continue

    if not deployable:
        logger.warning("No deployable revenue projects found.")
        return
        
    logger.info(f"Found {len(deployable)} projects. Initializing OS Kernel deployments for top {MAX_CONCURRENT_DEPLOYMENTS}...")
    
    # Deploy a capped number to manage system load
    async with httpx.AsyncClient() as client:
        for idx, path in enumerate(deployable[:MAX_CONCURRENT_DEPLOYMENTS]):
            logger.info(f"[{idx+1}/{MAX_CONCURRENT_DEPLOYMENTS}] Deploying: {path}")
            try:
                resp = await client.post(
                    API_URL, 
                    json={"path": path}, 
                    timeout=15.0,
                    headers=AUTH_HEADERS
                )
                if resp.status_code == 200:
                    logger.info(f"  -> SUCCESS: {resp.json()}")
                else:
                    logger.error(f"  -> FAILED: HTTP {resp.status_code} - {resp.text}")
            except httpx.ConnectError:
                logger.error("  -> ERROR: Could not connect to orchestrator API at :8000")
            except Exception as e:
                logger.error(f"  -> UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(find_and_deploy())
    except KeyboardInterrupt:
        print("\nDeployment scan aborted by user.")
