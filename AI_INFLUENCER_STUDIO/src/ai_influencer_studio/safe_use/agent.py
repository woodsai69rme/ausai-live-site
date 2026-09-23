"""Autonomous multi-model task agent over safe browser/computer use.

The agent turns a natural-language task into a loop: observe state (with a
screenshot for vision models) → ask N models concurrently → majority-vote the
next action → execute through the policy-enforcing :class:`SafeUseEngine` →
repeat until a model declares the task done (or the step budget runs out).

Every executed action still passes the safe-use policy allowlists, and each
sensitive action is recorded as an auto-approval in the audit log.
"""

from __future__ import annotations

import json
import re
from typing import Any

from ai_influencer_studio.safe_use.engine import SafeUseEngine
from ai_influencer_studio.safe_use.models import ActionIntent, ActionTarget, Observation
from ai_influencer_studio.safe_use.multi_model import ModelResult, MultiModelClient
from ai_influencer_studio.safe_use.policy import PolicyDenied

AGENT_SYSTEM_PROMPT = (
    "You are an autonomous web/computer-use agent. Given a task and the current page or "
    "application state, reply with ONLY one JSON object and nothing else:\n"
    '{"action": "<one allowed action>", "parameters": {<key: value>}, "reason": "<why>", "done": false}\n'
    "Use the screenshot to understand visual state when provided. Set done to true only when "
    "the task is fully complete."
)


class MultiModelAgent:
    """Run a natural-language task with several concurrent vision models."""

    def __init__(
        self,
        engine: SafeUseEngine,
        models: list[str],
        client: MultiModelClient | None = None,
        max_steps: int = 12,
        system_prompt: str = AGENT_SYSTEM_PROMPT,
        aggregator: str | None = None,
    ) -> None:
        if not models:
            raise ValueError("At least one model reference is required")
        self.engine = engine
        self.models = models
        self.client = client or MultiModelClient()
        self.max_steps = max_steps
        self.system_prompt = system_prompt
        self.aggregator = aggregator

    def run_task(
        self,
        task: str,
        target: str = "browser",
        url: str | None = None,
        app: str | None = None,
    ) -> dict[str, Any]:
        """Run the agent loop and return a structured trace."""
        steps: list[dict[str, Any]] = []
        navigate_once = url
        last_error: str | None = None
        last_action_key: str | None = None
        stall_count = 0
        for step_number in range(1, self.max_steps + 1):
            try:
                observation = self._observe(target, url=navigate_once, app=app)
            except PermissionError as exc:
                steps.append({"step": step_number, "executed": {"error": str(exc)}})
                return {"status": "denied", "steps": steps, "message": f"Policy denied: {exc}"}
            navigate_once = None  # only navigate on the first step
            results = self.client.complete_many(
                self.models,
                self._build_prompt(task, observation, last_error),
                system=self.system_prompt,
                image_path=observation.screenshot,
            )
            decision = self._merge(task, observation, results, last_error)
            step: dict[str, Any] = {
                "step": step_number,
                "models": [result.to_dict() for result in results],
                "decision": decision,
            }
            if decision.get("done"):
                step["executed"] = None
                steps.append(step)
                return {"status": "done", "steps": steps, "message": "Task completed"}
            intent = self._to_intent(decision, target, observation)
            try:
                executed = self._execute(intent)
            except PermissionError as exc:
                step["executed"] = {"error": str(exc)}
                steps.append(step)
                return {"status": "denied", "steps": steps, "message": f"Policy denied: {exc}"}
            except Exception as exc:
                last_error = str(exc)
                step["executed"] = {"error": str(exc)}
                steps.append(step)
                continue
            last_error = None
            step["executed"] = executed.to_dict()
            steps.append(step)
            action_key = f"{decision.get('action')}:{json.dumps(decision.get('parameters'), sort_keys=True, default=str)}"
            if action_key == last_action_key:
                stall_count += 1
            else:
                stall_count = 0
                last_action_key = action_key
            if stall_count >= 3:
                return {"status": "stalled", "steps": steps, "message": "No progress after repeated identical actions"}
        return {"status": "max_steps", "steps": steps, "message": f"Stopped after {self.max_steps} steps"}

    def _observe(self, target: str, url: str | None, app: str | None) -> Observation:
        if target == "browser":
            if url:
                navigation = ActionIntent(
                    target=ActionTarget.BROWSER,
                    action="navigate",
                    parameters={"url": url},
                    reason="agent navigation to start the task",
                    requested_by="multi-model-agent",
                )
                self._execute(navigation)
            assert self.engine.browser is not None
            return self.engine.browser.observe(selector="body", screenshot=True)
        if target == "windows":
            assert self.engine.windows is not None
            return self.engine.windows.observe(app=app, screenshot=True)
        raise PolicyDenied(f"Unknown automation target: {target}")

    def _execute(self, intent: ActionIntent) -> Any:
        approval = self.engine.approve(intent, approved_by="multi-model-agent")
        return self.engine.execute(intent, approval_token=approval.token)

    def _to_intent(self, decision: dict[str, Any], target: str, observation: Observation) -> ActionIntent:
        parameters = decision.get("parameters") or {}
        if not isinstance(parameters, dict):
            parameters = {}
        if target == "browser" and "current_url" not in parameters:
            parameters = {**parameters, "current_url": observation.url}
        return ActionIntent(
            target=ActionTarget(str(target)),
            action=str(decision.get("action", "observe")),
            parameters=dict(parameters),
            reason=str(decision.get("reason", "")),
            requested_by="multi-model-agent",
        )

    def _merge(
        self,
        task: str,
        observation: Observation,
        results: list[ModelResult],
        last_error: str | None,
    ) -> dict[str, Any]:
        """Merge proposals: Mixture-of-Agents aggregator when configured, else majority vote."""
        if not self.aggregator:
            return aggregate(results)
        proposals = "\n".join(f"- {result.ref}: {result.text}" for result in results if result.ok)
        if not proposals:
            return aggregate(results)
        merge_prompt = (
            f"Task: {task}\n\nHere are model proposals:\n{proposals}\n\n"
            "Choose or synthesize the single best next action. Reply with ONLY one JSON object."
        )
        merged = self.client.complete(
            self.aggregator,
            merge_prompt,
            system=self.system_prompt,
            image_path=observation.screenshot,
        )
        decision = _parse_json(merged.text) if merged.ok else None
        return decision if decision is not None else aggregate(results)

    @staticmethod
    def _build_prompt(task: str, observation: Observation, last_error: str | None = None) -> str:
        parts = [
            f"Task: {task}",
            f"Current title: {observation.title or '(none)'}",
            f"Current URL: {observation.url or '(none)'}",
            f"Page/app text:\n{observation.text[:8000] or '(no text captured)'}",
        ]
        if observation.elements:
            elements_text = "\n".join(
                f"{item.get('role', '')}: {item.get('name', '')}" for item in observation.elements[:200]
            )
            parts.append(f"Accessible UI elements:\n{elements_text}")
        if last_error:
            parts.append(f"Previous action failed ({last_error}); try a different approach.")
        return "\n\n".join(parts)


def pick_free_vision_models(snapshot: Any, limit: int = 4) -> list[str]:
    """Return up to ``limit`` free, vision-capable model refs (local first).

    Accepts any object with a ``models`` list of records exposing ``local``,
    ``is_available``, ``provider``, ``model_id``, and ``supports(capability)`` —
    which matches ``RegistrySnapshot``.

    Hosted free vision models are filtered to general-purpose, agent-usable ones:
    the OpenRouter ``:free`` catalog includes safety classifiers, preview stubs,
    and content moderators that accept images but cannot act as an agent.
    """
    local = [model for model in snapshot.models if model.local and model.is_available and model.supports("vision")]
    hosted = [
        model
        for model in snapshot.models
        if not model.local
        and model.is_available
        and model.supports("vision")
        and model.supports("free")
        and _is_agent_usable(model)
    ]
    ordered = local + hosted
    return [f"{model.provider}::{model.model_id}" for model in ordered[:limit]]


# Slug fragments that mark a hosted model as single-purpose rather than a
# general assistant, even though it may technically accept image input.
_NON_AGENT_SLUG_MARKERS = (
    "safety",
    "classifier",
    "moderation",
    "guard",
    "note-preview",
    "preview",
    "rerank",
    "embed",
    "detect",
)


def _is_agent_usable(model: Any) -> bool:
    """Return true only for a hosted model that can act as a general agent."""
    slug = f"{model.model_id} {getattr(model, 'display_name', '')}".lower()
    if any(marker in slug for marker in _NON_AGENT_SLUG_MARKERS):
        return False
    # The model must actually emit text to return an action JSON.
    return "text" in getattr(model, "output_modalities", ["text"])


def aggregate(results: list[ModelResult]) -> dict[str, Any]:
    """Majority-vote the parsed JSON decisions across the models."""
    parsed: list[dict[str, Any]] = []
    for result in results:
        if not result.ok:
            continue
        decision = _parse_json(result.text)
        if decision is not None:
            parsed.append(decision)
    if not parsed:
        return {"action": "observe", "parameters": {}, "reason": "no model produced a valid action", "done": False, "votes": 0}

    done_votes = sum(1 for decision in parsed if decision.get("done") is True)
    if done_votes >= len(parsed) / 2:
        return {"done": True, "votes": done_votes}

    actions = [str(decision.get("action", "")).strip() for decision in parsed]
    action, votes = max(((item, actions.count(item)) for item in set(actions)), key=lambda pair: pair[1])
    winner = next(decision for decision in parsed if str(decision.get("action", "")).strip() == action)
    return {**dict(winner), "votes": votes}


def _parse_json(text: str) -> dict[str, Any] | None:
    """Extract the first JSON object from a model response, if any."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except (ValueError, TypeError):
        return None
    return data if isinstance(data, dict) else None
