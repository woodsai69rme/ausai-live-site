"""
Base Agent for the AI Army.

All agents inherit from this class and implement the execute() method.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base agent that all AI Army agents extend."""

    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = "idle"
        self.created_at = datetime.now().isoformat()
        self.current_task: Optional[Dict[str, Any]] = None

        self.tasks_dir = os.path.join(os.path.dirname(__file__), '..', 'tasks')
        self.reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(self.tasks_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results. Must be implemented by subclasses."""
        pass

    def pick_up_task(self, task_file: str) -> Optional[Dict[str, Any]]:
        """Load a task JSON file from the tasks directory."""
        path = os.path.join(self.tasks_dir, task_file)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                task = json.load(f)
            self.current_task = task
            self.status = "working"
            logger.info(f"[{self.agent_id}] Picked up task: {task.get('title', task_file)}")
            return task
        except Exception as e:
            logger.error(f"[{self.agent_id}] Failed to load task {task_file}: {e}")
            return None

    def save_report(self, report: Dict[str, Any]) -> str:
        """Save an execution report to the reports directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.agent_id}_{timestamp}.json"
        path = os.path.join(self.reports_dir, filename)

        report_data = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "timestamp": datetime.now().isoformat(),
            "task": self.current_task,
            "results": report
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"[{self.agent_id}] Report saved: {filename}")
        self.status = "idle"
        self.current_task = None
        return filename

    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent state for the API."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "created_at": self.created_at,
            "current_task": self.current_task
        }
