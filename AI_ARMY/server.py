"""
AI Army Backend Server — FastAPI on port 8001.

Provides REST API for agent management, task dispatch, and report retrieval.
"""

import json
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from agents.recon_agent import ReconAgent
from agents.revenue_agent import RevenueAgent
from agents.cleanup_agent import CleanupAgent
from agents.monitor_agent import MonitorAgent
from agents.github_agent import GitHubAgent

# ── Setup ──────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-army")

@asynccontextmanager
async def lifespan(application):
    boot_agents()
    logger.info("AI Army Backend is ONLINE at http://localhost:8001")
    yield

app = FastAPI(
    title="AI Army Backend",
    description="Agent management, task dispatch, and report API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.join(BASE_DIR, "tasks")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(TASKS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── Agent Registry ─────────────────────────────────────────────

AGENTS: Dict[str, Any] = {}

def boot_agents():
    """Initialize default agents."""
    recon = ReconAgent()
    revenue = RevenueAgent()
    cleanup = CleanupAgent()
    monitor = MonitorAgent()
    github = GitHubAgent()
    AGENTS[recon.agent_id] = recon
    AGENTS[revenue.agent_id] = revenue
    AGENTS[cleanup.agent_id] = cleanup
    AGENTS[monitor.agent_id] = monitor
    AGENTS[github.agent_id] = github
    logger.info(f"Booted {len(AGENTS)} agents: {list(AGENTS.keys())}")

# ── Models ─────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    type: str  # "recon" or "revenue"
    target: Optional[str] = None
    action: Optional[str] = None
    max_depth: Optional[int] = 2

class TaskDispatch(BaseModel):
    agent_id: str
    task_file: str

# ── Routes ─────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "AI Army Backend",
        "version": "1.0.0",
        "agents_online": len(AGENTS),
        "uptime": datetime.now().isoformat()
    }

@app.get("/agents")
def list_agents():
    """List all registered agents and their statuses."""
    return [agent.to_dict() for agent in AGENTS.values()]

@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    """Get a specific agent's status."""
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return AGENTS[agent_id].to_dict()

@app.get("/tasks")
def list_tasks():
    """List all pending task files."""
    files = [f for f in os.listdir(TASKS_DIR) if f.endswith('.json')]
    tasks = []
    for f in files:
        try:
            with open(os.path.join(TASKS_DIR, f), 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                data["_filename"] = f
                tasks.append(data)
        except Exception:
            tasks.append({"_filename": f, "error": "unreadable"})
    return tasks

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    """Create a new task and save to the tasks directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"task_{task.type}_{timestamp}.json"
    filepath = os.path.join(TASKS_DIR, filename)

    task_data = task.dict()
    task_data["created_at"] = datetime.now().isoformat()
    task_data["status"] = "pending"

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(task_data, f, indent=2)

    logger.info(f"Task created: {filename}")
    return {"filename": filename, "task": task_data}

@app.post("/dispatch")
def dispatch_task(task: TaskCreate):
    """Immediately dispatch a task to the matching agent and return results."""
    # Route by task type
    if task.type == "recon":
        agent = AGENTS.get("recon-001")
    elif task.type == "revenue":
        agent = AGENTS.get("revenue-001")
    elif task.type == "cleanup":
        agent = AGENTS.get("cleanup-001")
    elif task.type == "monitor":
        agent = AGENTS.get("monitor-001")
    elif task.type == "github":
        agent = AGENTS.get("github-001")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown task type: {task.type}")

    if not agent:
        raise HTTPException(status_code=503, detail="Required agent is not online")

    task_data = task.dict()
    task_data["created_at"] = datetime.now().isoformat()

    try:
        results = agent.execute(task_data)
        return {"agent": agent.agent_id, "results": results}
    except Exception as e:
        logger.error(f"Dispatch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports")
def list_reports():
    """List all reports."""
    files = sorted(
        [f for f in os.listdir(REPORTS_DIR) if f.endswith('.json')],
        reverse=True
    )
    return [{"filename": f} for f in files[:50]]

@app.get("/reports/{filename}")
def get_report(filename: str):
    """Get the contents of a specific report."""
    filepath = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.delete("/tasks/{filename}")
def delete_task(filename: str):
    """Delete a pending task."""
    filepath = os.path.join(TASKS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Task not found")
    os.remove(filepath)
    return {"message": f"Task {filename} deleted"}

# ── Boot ───────────────────────────────────────────────────────

if __name__ == "__main__":
    reload = os.getenv("AI_ARMY_RELOAD", "").lower() in ("1", "true", "yes")
    # Harden: bind localhost only by default; set AI_ARMY_BIND=0.0.0.0 to expose LAN
    bind_host = os.getenv("AI_ARMY_BIND", "127.0.0.1")
    uvicorn.run("server:app", host=bind_host, port=8001, reload=reload)
