"""Tests for the autonomous multi-model task agent."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from ai_influencer_studio.safe_use.agent import MultiModelAgent, _parse_json, aggregate, pick_free_vision_models
from ai_influencer_studio.safe_use.models import ActionIntent, ActionMode, ActionResult, ActionTarget, Observation
from ai_influencer_studio.safe_use.multi_model import ModelResult
from ai_influencer_studio.safe_use.policy import PolicyDenied


class FakeBrowser:
    def __init__(self) -> None:
        self.url = "https://example.test"

    def observe(self, selector: str = "body", screenshot: bool = False) -> Observation:
        return Observation(
            target=ActionTarget.BROWSER,
            captured_at="now",
            url=self.url,
            title="Example",
            text="hello world",
            screenshot=None,
        )


class FakeEngine:
    def __init__(self) -> None:
        self.browser: Any = FakeBrowser()
        self.windows = None
        self.executed: list[ActionIntent] = []
        self.approvals: list[tuple[ActionIntent, str]] = []
        self.raise_on: str | None = None
        self.fail_next: Exception | None = None
        self.fail_action: str | None = None

    def approve(self, intent: ActionIntent, approved_by: str = "operator") -> SimpleNamespace:
        self.approvals.append((intent, approved_by))
        return SimpleNamespace(token="tok", intent_id=intent.intent_id)

    def execute(self, intent: ActionIntent, approval_token: str | None = None) -> ActionResult:
        if self.raise_on and intent.action == self.raise_on:
            raise PolicyDenied(f"blocked {intent.action}")
        if self.fail_next is not None and (self.fail_action is None or intent.action == self.fail_action):
            exc = self.fail_next
            self.fail_next = None
            raise exc
        self.executed.append(intent)
        return ActionResult(mode=ActionMode.EXECUTE, intent=intent, executed=True, message="ok")


class FakeClient:
    def __init__(self, batches: list[list[str | None]]) -> None:
        self._batches = list(batches)
        self.calls = 0
        self.prompts: list[str] = []

    def complete_many(
        self,
        references: list[str],
        prompt: str,
        system: str | None = None,
        image_path: object = None,
    ) -> list[ModelResult]:
        self.calls += 1
        self.prompts.append(prompt)
        batch = self._batches.pop(0) if self._batches else [None] * len(references)
        results: list[ModelResult] = []
        for ref, text in zip(references, batch, strict=False):
            results.append(ModelResult(ref=ref, provider="a", model_id=ref, text=text or "", ok=text is not None))
        return results


def _result(text: str) -> ModelResult:
    return ModelResult(ref="a::1", provider="a", model_id="1", text=text, ok=True)


def test_parse_json_strips_code_fence() -> None:
    assert _parse_json('```json\n{"action": "click"}\n```') == {"action": "click"}
    assert _parse_json("prefix {\"action\": \"observe\"} suffix") == {"action": "observe"}
    assert _parse_json("not json") is None


def test_aggregate_majority_vote() -> None:
    results = [
        _result('{"action": "click", "parameters": {"selector": "x"}, "done": false}'),
        _result('{"action": "click", "parameters": {"selector": "y"}, "done": false}'),
        _result('{"action": "scroll", "parameters": {}, "done": false}'),
        _result("not json"),
    ]
    decision = aggregate(results)
    assert decision["action"] == "click"
    assert decision["votes"] == 2


def test_aggregate_done_when_majority() -> None:
    results = [
        _result('{"done": true}'),
        _result('{"done": true}'),
        _result('{"action": "click", "done": false}'),
    ]
    assert aggregate(results)["done"] is True


def test_aggregate_falls_back_when_no_valid_json() -> None:
    results = [_result("garbage"), _result("also garbage")]
    decision = aggregate(results)
    assert decision["action"] == "observe"
    assert decision["votes"] == 0


def test_run_task_completes_on_done() -> None:
    engine = FakeEngine()
    client = FakeClient([['{"done": true}', '{"done": true}']])
    agent = MultiModelAgent(engine, models=["a::1", "a::2"], client=client, max_steps=5)

    result = agent.run_task("say hi", url="https://example.test")

    assert result["status"] == "done"
    assert len(result["steps"]) == 1
    assert [intent.action for intent in engine.executed] == ["navigate"]


def test_run_task_executes_then_completes() -> None:
    engine = FakeEngine()
    client = FakeClient(
        [
            ['{"action": "click", "parameters": {"selector": "button.save"}, "reason": "save", "done": false}'] * 2,
            ['{"done": true}'] * 2,
        ]
    )
    agent = MultiModelAgent(engine, models=["a::1", "a::2"], client=client, max_steps=5)

    result = agent.run_task("click save", url="https://example.test")

    assert result["status"] == "done"
    assert [intent.action for intent in engine.executed] == ["navigate", "click"]
    assert all(approved_by == "multi-model-agent" for _, approved_by in engine.approvals)


def test_run_task_stops_on_policy_denied() -> None:
    engine = FakeEngine()
    engine.raise_on = "click"
    client = FakeClient([['{"action": "click", "parameters": {"selector": "x"}, "done": false}'] * 2])
    agent = MultiModelAgent(engine, models=["a::1", "a::2"], client=client, max_steps=3)

    result = agent.run_task("do it", url="https://example.test")

    assert result["status"] == "denied"
    assert "Policy denied" in result["message"]


def test_agent_requires_at_least_one_model() -> None:
    engine = FakeEngine()
    with pytest.raises(ValueError, match="At least one model"):
        MultiModelAgent(engine, models=[])


def test_build_prompt_includes_elements_and_error() -> None:
    observation = Observation(
        target=ActionTarget.BROWSER,
        captured_at="now",
        url="https://example.test",
        text="hi",
        elements=[{"role": "button", "name": "Save", "value": ""}],
    )
    prompt = MultiModelAgent._build_prompt("do it", observation, last_error="timeout")
    assert "Accessible UI elements" in prompt
    assert "button: Save" in prompt
    assert "timeout" in prompt


def test_run_task_feeds_back_transient_error_then_recovers() -> None:
    engine = FakeEngine()
    engine.fail_action = "click"
    engine.fail_next = RuntimeError("element not found")
    client = FakeClient(
        [
            ['{"action": "click", "parameters": {"selector": "x"}, "done": false}'] * 2,
            ['{"done": true}'] * 2,
        ]
    )
    agent = MultiModelAgent(engine, models=["a::1", "a::2"], client=client, max_steps=5)
    result = agent.run_task("do it", url="https://example.test")

    assert result["status"] == "done"
    # navigate succeeded; the click failed transiently and was fed back, then done.
    assert [intent.action for intent in engine.executed] == ["navigate"]
    assert any("element not found" in prompt for prompt in client.prompts)


def test_run_task_stalls_on_repeated_actions() -> None:
    engine = FakeEngine()
    client = FakeClient(
        [
            ['{"action": "click", "parameters": {"selector": "x"}, "done": false}'] * 2,
            ['{"action": "click", "parameters": {"selector": "x"}, "done": false}'] * 2,
            ['{"action": "click", "parameters": {"selector": "x"}, "done": false}'] * 2,
            ['{"action": "click", "parameters": {"selector": "x"}, "done": false}'] * 2,
        ]
    )
    agent = MultiModelAgent(engine, models=["a::1", "a::2"], client=client, max_steps=5)
    result = agent.run_task("do it", url="https://example.test")
    assert result["status"] == "stalled"


def test_merge_with_aggregator_overrides_majority_vote() -> None:
    engine = FakeEngine()

    class AggClient:
        def complete_many(self, references: list[str], prompt: str, system: str | None = None, image_path: object = None) -> list[ModelResult]:
            return [ModelResult(ref=r, provider="a", model_id=r, text='{"action": "click", "done": false}', ok=True) for r in references]

        def complete(self, reference: str, prompt: str, system: str | None = None, image_path: object = None) -> ModelResult:
            return ModelResult(ref=reference, provider="a", model_id=reference, text='{"action": "scroll", "done": false}', ok=True)

    agent = MultiModelAgent(engine, models=["a::1", "a::2"], client=AggClient(), aggregator="a::agg", max_steps=1)
    result = agent.run_task("do it", url="https://example.test")
    assert result["steps"][0]["decision"]["action"] == "scroll"


def test_pick_free_vision_models_local_first() -> None:
    from ai_influencer_studio.model_registry import ModelRecord

    snapshot = SimpleNamespace(
        models=[
            ModelRecord(
                model_id="paid/vision", display_name="P", provider="openrouter", source="openrouter", local=False,
                checked_at="now", input_modalities=["text", "image"], prompt_price=0.01, completion_price=0.01,
            ),
            ModelRecord(
                model_id="google/gemini:free", display_name="G", provider="openrouter", source="openrouter", local=False,
                checked_at="now", input_modalities=["text", "image"], prompt_price=0, completion_price=0, cost_class="hosted_free",
            ),
            ModelRecord(model_id="qwen", display_name="Q", provider="ollama", source="ollama", local=True, checked_at="now"),
            ModelRecord(
                model_id="minicpm-v", display_name="V", provider="ollama", source="ollama", local=True,
                checked_at="now", input_modalities=["text", "image"],
            ),
        ]
    )
    refs = pick_free_vision_models(snapshot, limit=4)
    assert refs == ["ollama::minicpm-v", "openrouter::google/gemini:free"]


def test_pick_free_vision_models_excludes_non_agent_models() -> None:
    from ai_influencer_studio.model_registry import ModelRecord

    snapshot = SimpleNamespace(
        models=[
            ModelRecord(
                model_id="nemotron-3.5-content-safety:free", display_name="Content Safety",
                provider="openrouter", source="openrouter", local=False, checked_at="now",
                input_modalities=["text", "image"], prompt_price=0, completion_price=0, cost_class="hosted_free",
            ),
            ModelRecord(
                model_id="dots-3-note-preview:free", display_name="Note Preview",
                provider="openrouter", source="openrouter", local=False, checked_at="now",
                input_modalities=["text", "image"], prompt_price=0, completion_price=0, cost_class="hosted_free",
            ),
            ModelRecord(
                model_id="google/gemini:free", display_name="Gemini",
                provider="openrouter", source="openrouter", local=False, checked_at="now",
                input_modalities=["text", "image"], prompt_price=0, completion_price=0, cost_class="hosted_free",
            ),
        ]
    )
    refs = pick_free_vision_models(snapshot, limit=4)
    assert refs == ["openrouter::google/gemini:free"]


def test_pick_free_vision_models_requires_text_output() -> None:
    from ai_influencer_studio.model_registry import ModelRecord

    snapshot = SimpleNamespace(
        models=[
            ModelRecord(
                model_id="google/gemini:free", display_name="Gemini",
                provider="openrouter", source="openrouter", local=False, checked_at="now",
                input_modalities=["text", "image"], output_modalities=["image"],
                prompt_price=0, completion_price=0, cost_class="hosted_free",
            ),
        ]
    )
    refs = pick_free_vision_models(snapshot, limit=4)
    assert refs == []
