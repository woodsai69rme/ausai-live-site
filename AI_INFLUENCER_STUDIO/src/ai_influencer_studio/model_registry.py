"""Live Ollama/OpenRouter model discovery and LiteLLM routing config."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import requests

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OPENROUTER_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
CATALOG_TTL = timedelta(days=1)

# Verified OpenRouter free-tier limits (2026-08, from awesome-ai-gateway).
# The :free tier is 50 req/day below $10 lifetime credits and 1000 req/day after
# a $10 top-up, with a shared 20 req/min rate limit. Prompts may train a model
# per provider ToS — this is a fact, not an endorsement.
OPENROUTER_FREE_TIER_LIMITS: dict[str, Any] = {
    "requests_per_day": 50,
    "requests_per_minute": 20,
    "note": "50 req/day below $10 lifetime credits; 1000 req/day after $10 top-up. 20 req/min shared.",
}

# Parameter names that indicate a provider supports prompt caching.
_CACHE_PARAM_KEYS = ("prompt_cache_key", "cache_control", "prompt_caching", "caching")


@dataclass
class ModelRecord:
    """Normalized metadata for one discovered model deployment."""

    model_id: str
    display_name: str
    provider: str
    source: str
    local: bool
    checked_at: str
    context_length: int | None = None
    input_modalities: list[str] = field(default_factory=lambda: ["text"])
    output_modalities: list[str] = field(default_factory=lambda: ["text"])
    supports_tools: bool = False
    supported_parameters: list[str] = field(default_factory=list)
    prompt_price: float | None = None
    completion_price: float | None = None
    cost_class: str = "unknown"
    license: str = "unknown"
    license_source: str = "unknown"
    availability_status: str = "listed"
    availability_checked_at: str | None = None
    availability_source: str = "unknown"
    field_sources: dict[str, str] = field(default_factory=dict)
    size_bytes: int | None = None
    parameter_size: str | None = None
    quantization: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    health_status: str = "unknown"
    health_checked_at: str | None = None
    health_latency_ms: float | None = None
    health_error: str | None = None
    free_tier_limits: dict[str, Any] = field(default_factory=dict)
    maintenance_status: str = "unknown"
    supports_prompt_caching: bool = False

    @property
    def is_available(self) -> bool:
        """Whether the record is safe to consider for current routing."""
        return self.availability_status not in {"unlisted", "unavailable", "stale", "expired", "unknown"}

    @property
    def is_free_hosted(self) -> bool:
        """Whether a hosted provider advertises zero token pricing."""
        return (
            not self.local
            and self.prompt_price is not None
            and self.completion_price is not None
            and self.prompt_price == 0
            and self.completion_price == 0
        )

    def cost_per_million(self) -> tuple[float | None, float | None]:
        """Return (prompt, completion) cost in USD per 1M tokens, or None if unknown."""
        prompt = self.prompt_price * 1_000_000 if self.prompt_price is not None else None
        completion = self.completion_price * 1_000_000 if self.completion_price is not None else None
        return prompt, completion

    def supports(self, capability: str) -> bool:
        """Return whether the model supports a normalized capability."""
        if capability == "vision":
            return "image" in self.input_modalities or "video" in self.input_modalities
        if capability == "audio":
            return "audio" in self.input_modalities
        if capability == "video":
            return "video" in self.input_modalities
        if capability == "tools":
            return self.supports_tools
        if capability == "free":
            return self.local or self.is_free_hosted
        return capability in self.input_modalities or capability in self.output_modalities


@dataclass
class RegistrySnapshot:
    """Persisted result of one registry refresh."""

    checked_at: str
    models: list[ModelRecord]
    errors: list[dict[str, str]] = field(default_factory=list)
    aliases: dict[str, list[str]] = field(default_factory=dict)
    schema_version: int = 2
    verification_status: str = "unverified"
    verified: bool = False
    provider_status: dict[str, str] = field(default_factory=dict)
    source_urls: dict[str, str] = field(default_factory=dict)
    fresh_until: str | None = None
    refresh_mode: str = "manual"

    def to_dict(self) -> dict[str, Any]:
        return {
            "checked_at": self.checked_at,
            "models": [asdict(model) for model in self.models],
            "errors": self.errors,
            "aliases": self.aliases,
            "schema_version": self.schema_version,
            "verification_status": self.verification_status,
            "verified": self.verified,
            "provider_status": self.provider_status,
            "source_urls": self.source_urls,
            "fresh_until": self.fresh_until,
            "refresh_mode": self.refresh_mode,
        }


class ModelRegistry:
    """Discover models and generate a secret-free local-first LiteLLM config."""

    def __init__(
        self,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        openrouter_url: str = DEFAULT_OPENROUTER_URL,
        openrouter_api_key: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.ollama_url = ollama_url.rstrip("/")
        self.openrouter_url = openrouter_url.rstrip("/")
        self.openrouter_api_key = openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.timeout = timeout

    def refresh(
        self,
        include_ollama: bool = True,
        include_openrouter: bool = True,
        previous_snapshot: RegistrySnapshot | None = None,
        refresh_mode: str = "manual",
        extra_providers: list[dict[str, Any]] | None = None,
    ) -> RegistrySnapshot:
        """Fetch live metadata and retain last-known-good provider data on failure.

        OpenRouter's models endpoint is authoritative for catalog listing, pricing,
        capabilities, and published license metadata. It does not prove that every
        provider endpoint is currently serving traffic, so availability is recorded
        as catalog availability rather than claimed runtime health.

        ``extra_providers`` accepts optional OpenRouter-compatible catalogs (e.g.
        Groq, Cerebras, SambaNova, Hugging Face) as ``{"name", "base_url",
        "models_path", "api_key", "enabled"}`` dicts. They are fetched only when
        ``enabled`` is true; OpenRouter remains the sole always-on hosted provider.
        """
        checked_at = datetime.now(UTC).isoformat()
        models: list[ModelRecord] = []
        errors: list[dict[str, str]] = []
        provider_status: dict[str, str] = {}
        extra_providers = list(extra_providers or [])
        requested: list[tuple[str, bool, dict[str, Any] | None]] = [
            ("ollama", include_ollama, None),
            ("openrouter", include_openrouter, None),
        ]
        requested.extend(
            (str(cfg.get("name", "")), bool(cfg.get("enabled")), cfg)
            for cfg in extra_providers
            if isinstance(cfg, dict) and cfg.get("name") and cfg.get("base_url")
        )

        for provider, enabled, extra_cfg in requested:
            if not enabled:
                continue
            try:
                if provider == "ollama":
                    fetched = self._fetch_ollama(checked_at)
                elif provider == "openrouter":
                    fetched = self._fetch_openrouter(checked_at)
                    if not fetched:
                        raise ValueError("OpenRouter returned an empty model catalog")
                else:
                    fetched = self._fetch_extra_provider(extra_cfg, checked_at)
                    if not fetched:
                        raise ValueError(f"{provider} returned an empty model catalog")
                models.extend(fetched)
                provider_status[provider] = "verified"
            except (OSError, TypeError, KeyError, requests.RequestException, ValueError) as exc:
                error = _safe_error(exc)
                errors.append({"provider": provider, "error": error})
                provider_status[provider] = "stale" if previous_snapshot else "failed"
                if previous_snapshot:
                    models.extend(_stale_provider_models(previous_snapshot, provider, checked_at))

        if previous_snapshot:
            refreshed_providers = {provider for provider, enabled, _cfg in requested if enabled}
            models = _merge_unlisted_models(models, previous_snapshot, checked_at, refreshed_providers)
        enabled_providers = [provider for provider, enabled, _cfg in requested if enabled]
        verified = bool(enabled_providers) and all(provider_status.get(provider) == "verified" for provider in enabled_providers)
        return RegistrySnapshot(
            checked_at=checked_at,
            models=models,
            errors=errors,
            aliases=self.select_aliases(models),
            verification_status="verified" if verified else "degraded",
            verified=verified,
            provider_status=provider_status,
            source_urls={
                **({"ollama": f"{self.ollama_url}/api/tags"} if include_ollama else {}),
                **({"openrouter": f"{self.openrouter_url}/models"} if include_openrouter else {}),
                **{
                    str(cfg["name"]): f'{str(cfg["base_url"]).rstrip("/")}{cfg.get("models_path", "/models")}'
                    for cfg in extra_providers
                    if isinstance(cfg, dict)
                    and cfg.get("name")
                    and cfg.get("base_url")
                    and cfg.get("enabled")
                },
            },
            fresh_until=(datetime.fromisoformat(checked_at) + CATALOG_TTL).isoformat(),
            refresh_mode=refresh_mode,
        )

    def refresh_daily(
        self,
        path: Path,
        force: bool = False,
        include_ollama: bool = True,
        include_openrouter: bool = True,
    ) -> RegistrySnapshot:
        """Refresh at most once per 24 hours, atomically preserving prior data."""
        previous = self.load_snapshot(path) if path.exists() else None
        if previous and not force and _snapshot_is_fresh(previous):
            return previous
        snapshot = self.refresh(
            include_ollama=include_ollama,
            include_openrouter=include_openrouter,
            previous_snapshot=previous,
            refresh_mode="daily",
        )
        self.save_snapshot(snapshot, path)
        return snapshot

    def probe_health(
        self,
        snapshot: RegistrySnapshot,
        model_refs: set[str] | None = None,
        limit: int = 10,
        include_hosted: bool = False,
    ) -> RegistrySnapshot:
        """Probe selected models without changing catalog availability or aliases.

        Health probing is deliberately separate from catalog refresh. It sends a
        minimal request only to selected models, skips hosted models unless the
        operator explicitly opts in, and records health fields on each model.
        """
        if limit < 1:
            raise ValueError("Health probe limit must be at least 1")
        selected = model_refs or set()
        candidates = [
            model for model in snapshot.models
            if (not selected or _model_ref(model) in selected)
            and model.availability_status == "listed"
            and (model.local or include_hosted)
        ][:limit]
        checked_at = datetime.now(UTC).isoformat()
        by_ref = {_model_ref(model): model for model in snapshot.models}
        for model in candidates:
            reference = _model_ref(model)
            try:
                latency_ms = self._probe_model(model)
                by_ref[reference] = replace(
                    model,
                    health_status="healthy",
                    health_checked_at=checked_at,
                    health_latency_ms=latency_ms,
                    health_error=None,
                )
            except (OSError, TypeError, ValueError, requests.RequestException) as exc:
                by_ref[reference] = replace(
                    model,
                    health_status="unhealthy",
                    health_checked_at=checked_at,
                    health_latency_ms=None,
                    health_error=_safe_error(exc),
                )
        return replace(snapshot, models=[by_ref[_model_ref(model)] for model in snapshot.models])

    def _probe_model(self, model: ModelRecord) -> float:
        """Send one minimal provider request and return elapsed milliseconds."""
        started = datetime.now(UTC)
        if model.provider == "ollama":
            # /api/show returns model metadata without loading weights, so the
            # probe is fast and works for embedding models that reject
            # /api/generate. The explicit no-proxy mapping bypasses any
            # system-wide HTTP proxy (e.g. a dead 127.0.0.1 mitm proxy) for
            # localhost traffic.
            response = requests.post(
                f"{self.ollama_url}/api/show",
                json={"model": model.model_id},
                timeout=self.timeout,
                proxies={"http": None, "https": None},
            )
        elif model.provider == "openrouter":
            headers = {"Authorization": f"Bearer {self.openrouter_api_key}"} if self.openrouter_api_key else {}
            response = requests.post(
                f"{self.openrouter_url}/chat/completions",
                headers=headers,
                json={"model": model.model_id, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1},
                timeout=self.timeout,
                proxies={"http": None, "https": None},
            )
        else:
            api_base = model.metadata.get("api_base")
            if not isinstance(api_base, str) or not api_base:
                raise ValueError(f"Provider {model.provider} has no API base for health probe")
            api_key_env = model.metadata.get("api_key_env")
            api_key = os.environ.get(api_key_env, "") if isinstance(api_key_env, str) and api_key_env else ""
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            response = requests.post(
                f"{api_base.rstrip('/')}/chat/completions",
                headers=headers,
                json={"model": model.model_id, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1},
                timeout=self.timeout,
                proxies={"http": None, "https": None},
            )
        response.raise_for_status()
        return (datetime.now(UTC) - started).total_seconds() * 1000

    def _fetch_ollama(self, checked_at: str) -> list[ModelRecord]:
        response = requests.get(f"{self.ollama_url}/api/tags", timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise TypeError("Ollama model response must be a JSON object")
        if "models" not in payload:
            raise ValueError("Ollama model response is missing 'models'")
        raw_models = payload["models"]
        if not isinstance(raw_models, list):
            raise TypeError("Ollama model response 'models' must be a list")

        records: list[ModelRecord] = []
        for item in raw_models:
            if not isinstance(item, dict):
                continue
            model_id = str(item.get("name", "")).strip()
            if not model_id:
                continue
            details = item.get("details") if isinstance(item.get("details"), dict) else {}
            modalities = _infer_ollama_modalities(model_id)
            records.append(
                ModelRecord(
                    model_id=model_id,
                    display_name=model_id,
                    provider="ollama",
                    source="ollama",
                    local=True,
                    checked_at=checked_at,
                    input_modalities=modalities,
                    cost_class="local_free",
                    maintenance_status="local",
                    size_bytes=_as_int(item.get("size")),
                    parameter_size=_as_str(details.get("parameter_size")),
                    quantization=_as_str(details.get("quantization_level")),
                    field_sources={
                        "model_id": "ollama-tags",
                        "size": "ollama-tags",
                        "parameter_size": "ollama-tags",
                        "quantization": "ollama-tags",
                        "modalities": "model-name-heuristic" if len(modalities) > 1 else "unknown",
                    },
                    metadata={
                        "digest": item.get("digest"),
                        "modified_at": item.get("modified_at"),
                        "family": details.get("family"),
                        "format": details.get("format"),
                        "capability_source": "model-name-heuristic" if len(modalities) > 1 else "unknown",
                    },
                )
            )
        return records

    def _fetch_openrouter(self, checked_at: str) -> list[ModelRecord]:
        headers: dict[str, str] = {}
        if self.openrouter_api_key:
            headers["Authorization"] = f"Bearer {self.openrouter_api_key}"
        response = requests.get(
            f"{self.openrouter_url}/models",
            headers=headers,
            timeout=self.timeout,
            proxies={"http": None, "https": None},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise TypeError("OpenRouter model response must be a JSON object")
        if "data" not in payload:
            raise ValueError("OpenRouter model response is missing 'data'")
        raw_models = payload["data"]
        if not isinstance(raw_models, list):
            raise TypeError("OpenRouter model response 'data' must be a list")

        return _parse_catalog_models(raw_models, "openrouter", checked_at)

    def _fetch_extra_provider(self, config: dict[str, Any], checked_at: str) -> list[ModelRecord]:
        """Fetch an OpenRouter-compatible catalog from a configured extra provider.

        Extra providers (Groq, Cerebras, SambaNova, Hugging Face, ...) are
        fetched only when explicitly enabled in ``refresh(extra_providers=...)``;
        OpenRouter stays the sole always-on hosted provider per project policy.
        """
        base_url = str(config["base_url"]).rstrip("/")
        models_path = str(config.get("models_path", "/models"))
        headers: dict[str, str] = {}
        api_key = config.get("api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        response = requests.get(
            f"{base_url}{models_path}",
            headers=headers,
            timeout=self.timeout,
            proxies={"http": None, "https": None},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise TypeError(f"{config['name']} model response must be a JSON object")
        if "data" not in payload:
            raise ValueError(f"{config['name']} model response is missing 'data'")
        raw_models = payload["data"]
        if not isinstance(raw_models, list):
            raise TypeError(f"{config['name']} model response 'data' must be a list")
        records = _parse_catalog_models(raw_models, str(config["name"]), checked_at)
        api_base = base_url
        api_key_env = str(config.get("api_key_env", "")).strip()
        for record in records:
            record.metadata.update({"api_base": api_base, "api_key_env": api_key_env})
        return records

    @staticmethod
    def select_aliases(models: list[ModelRecord]) -> dict[str, list[str]]:
        """Choose provider-qualified, local-first fallback chains."""
        local = [model for model in models if model.local and model.is_available]
        hosted_free = [model for model in models if model.is_free_hosted and model.is_available]
        aliases: dict[str, list[str]] = {}
        definitions = (
            ("coding", "text", ("coder", "code", "devstral", "north-mini", "ornith")),
            ("reasoning", "text", ("reason", "deepseek-r1", "nemotron", "qwq", "o1")),
            ("vision", "vision", ("vision", "vl", "gemma", "minicpm", "llava", "omni")),
            ("general", "text", ("instruct", "chat", "general", "gemma", "llama", "gpt-oss")),
        )
        for alias, capability, keywords in definitions:
            local_candidates = _rank_candidates(local, capability, keywords)
            hosted_candidates = _rank_candidates(hosted_free, capability, keywords)
            if capability == "vision":
                local_candidates = [model for model in local_candidates if model.supports("vision")]
                hosted_candidates = [model for model in hosted_candidates if model.supports("vision")]
            candidates = local_candidates + hosted_candidates
            aliases[alias] = _unique_model_refs(candidates)
        return aliases

    @staticmethod
    def save_snapshot(snapshot: RegistrySnapshot, path: Path) -> Path:
        """Write a registry snapshot atomically as UTF-8 JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(snapshot.to_dict(), indent=2), encoding="utf-8")
        temporary.replace(path)
        return path

    @staticmethod
    def load_snapshot(path: Path) -> RegistrySnapshot:
        """Load and validate a saved snapshot, including older registry files."""
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("models"), list):
            raise ValueError(f"Invalid registry snapshot: {path}")
        models = [_model_from_dict(item) for item in data["models"] if isinstance(item, dict)]
        return RegistrySnapshot(
            checked_at=str(data.get("checked_at", "")),
            models=models,
            errors=[item for item in data.get("errors", []) if isinstance(item, dict)],
            aliases=data.get("aliases", {}) if isinstance(data.get("aliases"), dict) else {},
            schema_version=_as_int(data.get("schema_version")) or 1,
            verification_status=str(data.get("verification_status", "unverified")),
            verified=bool(data.get("verified", False)),
            provider_status=data.get("provider_status", {}) if isinstance(data.get("provider_status"), dict) else {},
            source_urls=data.get("source_urls", {}) if isinstance(data.get("source_urls"), dict) else {},
            fresh_until=data.get("fresh_until"),
            refresh_mode=str(data.get("refresh_mode", "manual")),
        )

    @staticmethod
    def export_catalog_markdown(snapshot: RegistrySnapshot, path: Path) -> Path:
        """Write a secret-free, offline operator report from a saved snapshot."""
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Model Registry Snapshot Report",
            "",
            f"- Checked at: `{snapshot.checked_at or 'unknown'}`",
            f"- Fresh until: `{snapshot.fresh_until or 'unknown'}`",
            f"- Verification: `{snapshot.verification_status}`",
            f"- Refresh mode: `{snapshot.refresh_mode}`",
            f"- Models: **{len(snapshot.models)}**",
            "",
            "## Provider status",
            "",
            "| Provider | Status | Source |",
            "|---|---|---|",
        ]
        for provider in sorted(snapshot.provider_status):
            lines.append(
                f"| {_markdown_cell(provider)} | {_markdown_cell(snapshot.provider_status[provider])} | "
                f"{_markdown_cell(snapshot.source_urls.get(provider, 'unknown'))} |"
            )
        if not snapshot.provider_status:
            lines.append("| (none) | unknown | unknown |")
        lines.extend(["", "## Models", "", "| Provider | Model | Cost | Modalities | Context | Tools | License | Availability |", "|---|---|---|---|---:|---|---|---|"])
        for model in sorted(snapshot.models, key=lambda item: (item.provider, item.model_id)):
            modalities = ", ".join(model.input_modalities) or "unknown"
            context = str(model.context_length) if model.context_length is not None else "unknown"
            lines.append(
                f"| {_markdown_cell(model.provider)} | {_markdown_cell(model.display_name)} ({_markdown_cell(model.model_id)}) | "
                f"{_markdown_cell(model.cost_class)} | {_markdown_cell(modalities)} | {context} | "
                f"{'yes' if model.supports_tools else 'no'} | {_markdown_cell(model.license)} | "
                f"{_markdown_cell(model.availability_status)} |"
            )
        if not snapshot.models:
            lines.append("| (none) | (none) | unknown | unknown | unknown | unknown | unknown | unknown |")
        lines.extend(["", "## Routing aliases", ""])
        for alias in sorted(snapshot.aliases):
            chain = ", ".join(_markdown_cell(ref) for ref in snapshot.aliases[alias]) or "(none)"
            lines.append(f"- **{_markdown_cell(alias)}:** {chain}")
        lines.extend(["", "## Provider errors", ""])
        if snapshot.errors:
            for error in snapshot.errors:
                lines.append(f"- **{_markdown_cell(error.get('provider', 'unknown'))}:** {_markdown_cell(error.get('error', 'unknown'))}")
        else:
            lines.append("- None recorded.")
        lines.extend([
            "",
            "## Interpretation",
            "",
            "- `listed` means the provider catalog reported the model; it is not a live inference-health check.",
            "- `stale`, `expired`, `unavailable`, `unknown`, and `unlisted` records are excluded from routing aliases.",
            "- This report contains metadata only; credentials are never exported.",
            "",
        ])
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    @staticmethod
    def emit_litellm_config(snapshot: RegistrySnapshot, path: Path, ollama_url: str = DEFAULT_OLLAMA_URL) -> Path:
        """Emit a complete secret-free LiteLLM YAML config from a snapshot."""
        path.parent.mkdir(parents=True, exist_ok=True)
        by_ref = {_model_ref(model): model for model in snapshot.models}
        lines = [
            "# Generated by aisocial model-registry refresh.",
            "# Secrets are read from environment variables; do not add keys here.",
            "# Retries may bill twice on streaming failures; keep requests idempotent.",
            "model_list:",
        ]
        fallbacks: dict[str, list[str]] = {}
        for alias, chain in snapshot.aliases.items():
            route_names: list[str] = []
            for index, model_ref in enumerate(chain):
                model = by_ref.get(model_ref)
                if model is None:
                    continue
                route_name = alias if not route_names else f"{alias}-fallback-{index}"
                route_names.append(route_name)
                if model.provider == "ollama":
                    provider_model = f"ollama_chat/{model.model_id}"
                    api_base = ollama_url
                    api_key_env = None
                elif model.provider == "openrouter":
                    provider_model = f"openrouter/{model.model_id}"
                    api_base = None
                    api_key_env = "OPENROUTER_API_KEY"
                else:
                    provider_model = f"openai/{model.model_id}"
                    api_base = model.metadata.get("api_base")
                    api_key_env = model.metadata.get("api_key_env") or None
                lines.extend(_litellm_entry(route_name, provider_model, api_base, api_key_env))
            if len(route_names) > 1:
                fallbacks[alias] = route_names[1:]

        lines.extend([
            "litellm_settings:",
            "  num_retries: 2",
            "  request_timeout: 120",
            "router_settings:",
            "  fallbacks:",
            "  cooldown_time: 30",
            "  allowed_fails: 3",
        ])
        if fallbacks:
            for alias, chain in fallbacks.items():
                lines.append(f"    - {alias}: [{', '.join(chain)}]")
        else:
            lines.append("    []")
        lines.extend([
            "general_settings:",
            "  master_key: os.environ/LITELLM_MASTER_KEY",
        ])
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path


def _parse_catalog_models(raw_models: list[Any], provider: str, checked_at: str) -> list[ModelRecord]:
    """Parse an OpenRouter-compatible ``data`` list into model records.

    Shared by the OpenRouter fetch and every enabled extra provider. Records
    carry the provider name so fallback chains and stale/unlisted tracking
    work uniformly across sources.
    """
    records: list[ModelRecord] = []
    for item in raw_models:
        if not isinstance(item, dict):
            continue
        model_id = str(item.get("id", "")).strip()
        if not model_id:
            continue
        architecture = item.get("architecture") if isinstance(item.get("architecture"), dict) else {}
        pricing = item.get("pricing") if isinstance(item.get("pricing"), dict) else {}
        input_modalities = _as_str_list(
            architecture.get("input_modalities") or architecture.get("input_modality") or ["text"]
        )
        output_modalities = _as_str_list(
            architecture.get("output_modalities") or architecture.get("output_modality") or ["text"]
        )
        supported_parameters = _as_str_list(item.get("supported_parameters", []))
        prompt_price = _as_float(pricing.get("prompt"))
        completion_price = _as_float(pricing.get("completion"))
        if prompt_price == 0 and completion_price == 0:
            cost_class = "hosted_free"
        elif prompt_price is not None or completion_price is not None:
            cost_class = "hosted_paid"
        else:
            cost_class = "unknown"
        availability = _normalize_availability(item)
        records.append(
            ModelRecord(
                model_id=model_id,
                display_name=str(item.get("name") or model_id),
                provider=provider,
                source=provider,
                local=False,
                checked_at=checked_at,
                context_length=_as_int(item.get("context_length")),
                input_modalities=input_modalities,
                output_modalities=output_modalities,
                supports_tools="tools" in supported_parameters or "tool_choice" in supported_parameters,
                supported_parameters=supported_parameters,
                prompt_price=prompt_price,
                completion_price=completion_price,
                cost_class=cost_class,
                license=_normalize_license(item.get("license")),
                license_source=f"{provider}-models" if item.get("license") else "unknown",
                availability_status=availability,
                availability_checked_at=checked_at,
                availability_source=f"{provider}-models",
                free_tier_limits=(
                    dict(OPENROUTER_FREE_TIER_LIMITS)
                    if provider == "openrouter" and cost_class == "hosted_free"
                    else {}
                ),
                maintenance_status=_maintenance_status(availability, False),
                supports_prompt_caching=any(key in supported_parameters for key in _CACHE_PARAM_KEYS),
                field_sources={
                    "pricing": f"{provider}-models",
                    "modalities": f"{provider}-models",
                    "context_length": f"{provider}-models",
                    "tools": f"{provider}-models",
                    "license": f"{provider}-models" if item.get("license") else "unknown",
                    "availability": f"{provider}-models",
                },
                metadata={
                    "canonical_slug": item.get("canonical_slug"),
                    "hugging_face_id": item.get("hugging_face_id"),
                    "supported_parameters": supported_parameters,
                    "created": item.get("created"),
                    "released": item.get("released"),
                    "expiration_date": item.get("expiration_date"),
                    "top_provider": item.get("top_provider"),
                    "per_request_limits": item.get("per_request_limits"),
                    "architecture": architecture,
                },
            )
        )
    return records


def _markdown_cell(value: Any) -> str:
    """Keep generated Markdown tables structurally valid."""
    return str(value).replace("|", "\\|").replace("\n", " ").strip() or "unknown"


def _litellm_entry(
    model_name: str,
    model: str,
    api_base: str | None,
    api_key_env: str | None = None,
) -> list[str]:
    lines = [
        f"  - model_name: {json.dumps(model_name)}",
        "    litellm_params:",
        f"      model: {json.dumps(model)}",
    ]
    if api_base:
        lines.append(f"      api_base: {json.dumps(api_base)}")
    if api_key_env:
        lines.append(f"      api_key: os.environ/{api_key_env}")
    return lines


def _rank_candidates(candidates: list[ModelRecord], capability: str, keywords: tuple[str, ...]) -> list[ModelRecord]:
    def score(model: ModelRecord) -> tuple[int, int, str]:
        haystack = f"{model.model_id} {model.display_name}".lower()
        keyword_score = sum(2 for keyword in keywords if keyword in haystack)
        capability_score = 3 if model.supports(capability) else 0
        context_score = min(model.context_length or 0, 1_000_000)
        return keyword_score + capability_score, context_score, model.model_id

    return sorted(candidates, key=score, reverse=True)


def _model_ref(model: ModelRecord) -> str:
    return f"{model.provider}::{model.model_id}"


def _unique_model_refs(models: list[ModelRecord]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for model in models:
        reference = _model_ref(model)
        if reference not in seen:
            seen.add(reference)
            result.append(reference)
    return result


def _model_from_dict(data: dict[str, Any]) -> ModelRecord:
    """Construct a record while tolerating snapshots written before schema v2."""
    known = {field_name for field_name in ModelRecord.__dataclass_fields__}
    values = {key: value for key, value in data.items() if key in known}
    values.setdefault("license", "unknown")
    values.setdefault("availability_status", "listed")
    values.setdefault("checked_at", "")
    values.setdefault("provider", "unknown")
    values.setdefault("source", values["provider"])
    values.setdefault("local", False)
    values.setdefault("display_name", values.get("model_id", "unknown"))
    values.setdefault("model_id", "unknown")
    return ModelRecord(**values)


def _normalize_license(value: Any) -> str:
    """Normalize a published license value without treating missing data as permissive."""
    if isinstance(value, dict):
        value = value.get("id") or value.get("name")
    normalized = str(value).strip() if value is not None else ""
    return normalized or "unknown"


def _normalize_availability(item: dict[str, Any]) -> str:
    """Represent catalog listing status; runtime health is not asserted by /models."""
    if item.get("expiration_date"):
        try:
            expiration = datetime.fromisoformat(str(item["expiration_date"]).replace("Z", "+00:00"))
            if expiration.tzinfo is None:
                expiration = expiration.replace(tzinfo=UTC)
            if expiration <= datetime.now(UTC):
                return "expired"
        except (ValueError, TypeError):
            pass
    if item.get("is_active") is False or item.get("available") is False:
        return "unavailable"
    return "listed"


def _maintenance_status(availability_status: str, local: bool) -> str:
    """Map catalog availability to a coarse provider-maintenance signal."""
    if local:
        return "local"
    if availability_status == "listed":
        return "active"
    return availability_status


def _stale_provider_models(snapshot: RegistrySnapshot, provider: str, checked_at: str) -> list[ModelRecord]:
    """Reuse prior provider records while marking their metadata stale."""
    return [
        replace(
            model,
            checked_at=checked_at,
            availability_status="stale",
            availability_checked_at=checked_at,
            availability_source="last-known-good",
            metadata={**model.metadata, "stale": True},
        )
        for model in snapshot.models
        if model.provider == provider
    ]


def _merge_unlisted_models(
    current: list[ModelRecord],
    previous: RegistrySnapshot,
    checked_at: str,
    refreshed_providers: set[str],
) -> list[ModelRecord]:
    """Keep disappeared models visible as unlisted for auditability, never for routing."""
    current_refs = {_model_ref(model) for model in current}
    merged = list(current)
    for model in previous.models:
        if model.provider in refreshed_providers and _model_ref(model) not in current_refs:
            merged.append(
                replace(
                    model,
                    checked_at=checked_at,
                    availability_status="unlisted",
                    availability_checked_at=checked_at,
                    availability_source="openrouter-models",
                    metadata={**model.metadata, "unlisted_at": checked_at},
                )
            )
    return merged


def _snapshot_is_fresh(snapshot: RegistrySnapshot) -> bool:
    """Return true only for a verified, non-expired daily snapshot."""
    if not snapshot.fresh_until or snapshot.verification_status != "verified":
        return False
    try:
        return datetime.now(UTC) < datetime.fromisoformat(snapshot.fresh_until)
    except (TypeError, ValueError):
        return False


def _infer_ollama_modalities(model_id: str) -> list[str]:
    """Infer only obvious capabilities; Ollama tags are not a full schema."""
    lowered = model_id.lower()
    modalities = ["text"]
    if any(token in lowered for token in ("-vl", ":vl", "vision", "minicpm-v", "llava", "gemma3")):
        modalities.append("image")
    if any(token in lowered for token in ("audio", "omni")):
        modalities.append("audio")
    return modalities


def _safe_error(exc: Exception) -> str:
    """Persist a bounded provider error without copying credentials or query strings."""
    message = str(exc)
    lowered = message.lower()
    for marker in ("bearer ", "api_key=", "token=", "key=", "password="):
        index = lowered.find(marker)
        if index >= 0:
            message = message[:index].rstrip(" ?&;,:") + " [redacted]"
            lowered = message.lower()
    if "?" in message:
        message = message.split("?", 1)[0] + " [query redacted]"
    return message[:500]


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_str(value: Any) -> str | None:
    return str(value) if value is not None else None


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    return []
