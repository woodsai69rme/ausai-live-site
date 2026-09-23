"""Concurrent multi-model inference for vision-capable agent tasks.

Runs several free models at once — local Ollama and hosted OpenRouter — and
returns each response for aggregation. Vision input (a screenshot) is passed as
base64 PNG. Credentials are read from the environment and never included in any
result.
"""

from __future__ import annotations

import base64
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

from ai_influencer_studio.model_registry import DEFAULT_OLLAMA_URL, DEFAULT_OPENROUTER_URL


@dataclass
class ModelResult:
    """One model's response to a single prompt."""

    ref: str
    provider: str
    model_id: str
    text: str
    ok: bool
    error: str | None = None
    latency_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref": self.ref,
            "provider": self.provider,
            "model_id": self.model_id,
            "text": self.text,
            "ok": self.ok,
            "error": self.error,
            "latency_ms": self.latency_ms,
        }


def parse_model_ref(reference: str) -> tuple[str, str]:
    """Split ``provider::model_id`` into ``(provider, model_id)``."""
    if "::" in reference:
        provider, model_id = reference.split("::", 1)
        return provider.strip().lower(), model_id.strip()
    return "", reference.strip()


class MultiModelClient:
    """Call multiple models concurrently with optional vision input."""

    def __init__(
        self,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        openrouter_url: str = DEFAULT_OPENROUTER_URL,
        openrouter_api_key: str | None = None,
        timeout: float = 60.0,
        ollama_timeout: float = 300.0,
    ) -> None:
        self.ollama_url = ollama_url.rstrip("/")
        self.openrouter_url = openrouter_url.rstrip("/")
        self.openrouter_api_key = openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.timeout = timeout
        # Local Ollama models load weights on first call, which can take minutes.
        # Hosted models answer in seconds, so keep a separate, longer local budget.
        self.ollama_timeout = ollama_timeout

    def complete(
        self,
        reference: str,
        prompt: str,
        system: str | None = None,
        image_path: Path | str | None = None,
    ) -> ModelResult:
        """Run one model on one prompt, returning a non-raising ``ModelResult``."""
        provider, model_id = parse_model_ref(reference)
        started = datetime.now(UTC)
        try:
            if provider == "ollama":
                text = self._complete_ollama(model_id, prompt, system, image_path)
            elif provider == "openrouter":
                text = self._complete_openrouter(model_id, prompt, system, image_path)
            else:
                raise ValueError(f"Unsupported provider for model call: {provider or '(missing)'}")
            return ModelResult(
                ref=reference,
                provider=provider,
                model_id=model_id,
                text=text,
                ok=True,
                latency_ms=(datetime.now(UTC) - started).total_seconds() * 1000,
            )
        except (OSError, TypeError, ValueError, requests.RequestException) as exc:
            return ModelResult(
                ref=reference,
                provider=provider,
                model_id=model_id,
                text="",
                ok=False,
                error=_safe_error(exc),
            )

    def complete_many(
        self,
        references: list[str],
        prompt: str,
        system: str | None = None,
        image_path: Path | str | None = None,
        max_workers: int | None = None,
    ) -> list[ModelResult]:
        """Run ``references`` concurrently; results stay in input order."""
        workers = max_workers or max(1, len(references))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(self.complete, ref, prompt, system, image_path) for ref in references]
            return [future.result() for future in futures]

    def _complete_ollama(self, model_id: str, prompt: str, system: str | None, image_path: Path | str | None) -> str:
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        content: dict[str, Any] = {"content": prompt}
        if image_path:
            content["images"] = [_encode_image(image_path)]
        messages.append({"role": "user", **content})
        response = requests.post(
            f"{self.ollama_url}/api/chat",
            json={"model": model_id, "messages": messages, "stream": False},
            timeout=self.ollama_timeout,
            proxies={"http": None, "https": None},
        )
        response.raise_for_status()
        data = response.json()
        return str(data.get("message", {}).get("content", ""))

    def _complete_openrouter(self, model_id: str, prompt: str, system: str | None, image_path: Path | str | None) -> str:
        headers: dict[str, str] = {}
        if self.openrouter_api_key:
            headers["Authorization"] = f"Bearer {self.openrouter_api_key}"
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        user_content: Any = prompt
        if image_path:
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": _encode_image(image_path, data_uri=True)}},
            ]
        messages.append({"role": "user", "content": user_content})
        response = requests.post(
            f"{self.openrouter_url}/chat/completions",
            headers=headers,
            json={"model": model_id, "messages": messages},
            timeout=self.timeout,
            proxies={"http": None, "https": None},
        )
        response.raise_for_status()
        data = response.json()
        return str(data["choices"][0]["message"]["content"])


def _encode_image(path: Path | str, data_uri: bool = False) -> str:
    encoded = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}" if data_uri else encoded


def _safe_error(exc: Exception) -> str:
    """Bound an error message without copying credentials or query strings."""
    message = str(exc)
    lowered = message.lower()
    for marker in ("bearer ", "api_key=", "token=", "key=", "password="):
        index = lowered.find(marker)
        if index >= 0:
            message = message[:index].rstrip(" ?&;,") + " [redacted]"
            lowered = message.lower()
    if "?" in message:
        message = message.split("?", 1)[0] + " [query redacted]"
    return message[:500]
