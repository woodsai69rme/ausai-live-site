"""ComfyUI execution hardening: pre-flight checks and workflow validation.

The execute stage of the pipeline is the link that has never been proven
against a real ComfyUI instance. This module gives the operator the checks
to run before (or while) generating:

- ``ComfyUIRuntimeCheck`` — live checks against a running ComfyUI server
  (``/system_stats`` for VRAM/torch, ``/object_info`` for the node catalog)
  with clear failure messages instead of a wall of subprocess stderr.
- ``validate_workflow`` — structural validation of a workflow JSON before it
  is submitted: every node must carry an id and a ``class_type``, every node
  referenced by a link must exist, and (when object info is available) every
  required input must be present.
- ``vram_budget_report`` — a heuristic per-workflow VRAM estimate against the
  GPU budget so the operator knows before generation whether a workflow is
  likely to OOM on an 8GB card.

The checks are deliberately read-only: nothing here submits a workflow or
mutates server state.
"""

from __future__ import annotations

from typing import Any

import requests

from ai_influencer_studio.config import StudioConfig

# Heuristic VRAM cost (GB) per heavy node class, used by the budget report.
# These are rough per-node working-set estimates for 8GB-class GPUs, not
# benchmarks; the report is a tripwire, not a billing meter.
_HEAVY_NODE_VRAM_GB: dict[str, float] = {
    "UNETLoader": 3.5,
    "CheckpointLoaderSimple": 4.0,
    "CheckpointLoader": 4.0,
    "DiffusionModelLoader": 3.5,
    "VAELoader": 1.0,
    "CLIPLoader": 1.2,
    "KSampler": 1.5,
    "KSamplerAdvanced": 1.5,
    "SamplerCustom": 2.0,
    "LoraLoader": 0.8,
    "LoraLoaderModelOnly": 0.6,
    "IPAdapterUnifiedLoader": 1.2,
    "IPAdapterAdvanced": 1.2,
    "ControlNetLoader": 0.9,
    "ControlNetApplyAdvanced": 0.8,
    "EmptyLatentImage": 0.4,
}

# Node classes that contribute a resolution-dependent working set.
_RESOLUTION_SENSITIVE = ("KSampler", "KSamplerAdvanced", "SamplerCustom", "VAEDecode", "VAEEncode")

_BASE_OVERHEAD_GB = 2.5


class ComfyUIRuntimeCheck:
    """Read-only live checks against a ComfyUI server."""

    def __init__(self, config: StudioConfig | None = None) -> None:
        self.config = config or StudioConfig.from_file()
        self.url = self.config.comfyui_url.rstrip("/")
        self.timeout = 10.0

    def server_status(self) -> dict[str, Any]:
        """Query ``/system_stats`` and return a bounded status dict.

        Raises ``requests.RequestException`` on connection failure so callers
        can surface the exact reason ComfyUI is unreachable.
        """
        response = requests.get(
            f"{self.url}/system_stats",
            timeout=self.timeout,
            proxies={"http": None, "https": None},
        )
        response.raise_for_status()
        payload = response.json()
        devices = payload.get("devices", [])
        gpu = devices[0] if devices else {}
        vram_total = _as_float(gpu.get("vram_total"))
        vram_free = _as_float(gpu.get("vram_free"))
        return {
            "online": True,
            "url": self.url,
            "device": gpu.get("name") or payload.get("system", {}).get("name", "unknown"),
            "vram_total_gb": round(vram_total / 1e9, 1) if vram_total else None,
            "vram_free_gb": round(vram_free / 1e9, 1) if vram_free else None,
            "torch_version": payload.get("system", {}).get("torch_version", "unknown"),
            "python_version": payload.get("system", {}).get("python_version", "unknown"),
            "comfyui_version": payload.get("system", {}).get("comfyui_version", "unknown"),
        }

    def object_info(self) -> dict[str, Any]:
        """Return the ``/object_info`` node catalog, or {} when unavailable."""
        response = requests.get(
            f"{self.url}/object_info",
            timeout=self.timeout,
            proxies={"http": None, "https": None},
        )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}

    def check(self) -> dict[str, Any]:
        """Run the full pre-flight: server status plus catalog size."""
        status = self.server_status()
        try:
            catalog = self.object_info()
            status["object_info_classes"] = len(catalog)
            status["catalog_available"] = True
        except requests.RequestException as exc:
            status["catalog_available"] = False
            status["catalog_error"] = _safe_error(exc)
        return status


def validate_workflow(
    workflow: dict[str, Any],
    object_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Structurally validate a ComfyUI workflow JSON.

    Accepts both the API format (``class_type`` + dict ``inputs``, connected
    inputs as ``["node_id", output_index]``) and the legacy UI format
    (``type`` + list ``inputs`` + ``links``). Returns ``{"valid": bool,
    "errors": [...], "warnings": [...]}``; errors mean the workflow should not
    be submitted, warnings are advisory (usually missing object info).
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(workflow, dict):
        return {"valid": False, "errors": ["workflow must be a JSON object"], "warnings": []}
    nodes = workflow.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return {"valid": False, "errors": ["workflow.nodes must be a non-empty list"], "warnings": []}

    node_ids: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"node[{index}] is not an object")
            continue
        node_id = node.get("id")
        if node_id is None:
            errors.append(f"node[{index}] is missing an 'id'")
        else:
            normalized = str(node_id)
            if normalized in node_ids:
                errors.append(f"duplicate node id: {node_id}")
            else:
                node_ids.add(normalized)
        class_type = node.get("class_type", node.get("type"))
        if not class_type:
            errors.append(f"node[{index}] (id={node_id}) is missing 'class_type'")

    # Connected-input references: API format uses ["node_id", output_index] where
    # node_id may be int or str; normalize both sides before comparing.
    for _index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs")
        if isinstance(inputs, dict):
            for key, value in inputs.items():
                if isinstance(value, list) and len(value) == 2 and isinstance(value[0], int | str):
                    if str(value[0]) not in node_ids:
                        errors.append(
                            f"node {node.get('id')} input '{key}' references missing node {value[0]}"
                        )

    # Legacy format: validate the links table (from/to node ids).
    links = workflow.get("links")
    if isinstance(links, list):
        for link in links:
            if not (isinstance(link, list) and len(link) >= 5):
                warnings.append("malformed legacy link entry (expected 6-element list)")
                continue
            from_node, to_node = link[1], link[3]
            for reference, label in ((from_node, "from"), (to_node, "to")):
                if str(reference) not in node_ids:
                    errors.append(f"legacy link {link[0]} references missing {label} node {reference}")

    # Required-input coverage, only when the catalog is available.
    if object_info:
        for _index, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            class_type = node.get("class_type", node.get("type"))
            definition = object_info.get(class_type) if isinstance(object_info, dict) else None
            if not isinstance(definition, dict):
                warnings.append(f"class '{class_type}' is not in the object_info catalog")
                continue
            required = definition.get("input", {}).get("required", {})
            inputs = node.get("inputs")
            provided = set(inputs.keys()) if isinstance(inputs, dict) else set()
            for name in required:
                if name not in provided:
                    errors.append(
                        f"node {node.get('id')} ({class_type}) is missing required input '{name}'"
                    )
    else:
        warnings.append("object_info not provided; required-input coverage not checked")

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def vram_budget_report(
    server_status: dict[str, Any],
    workflows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Estimate per-workflow VRAM against the GPU budget from ``server_status``.

    Each workflow's estimate is the sum of its heavy node classes plus a
    resolution-sensitive working set. Verdicts: ``green`` (fits comfortably),
    ``yellow`` (tight but plausible), ``red`` (likely to OOM).
    """
    total_gb = _as_float(server_status.get("vram_total_gb"))
    if total_gb is None or total_gb <= 0:
        return {"verdict": "unknown", "estimates": [], "note": "vram_total_gb not reported by server"}
    estimates: list[dict[str, Any]] = []
    for index, workflow in enumerate(workflows):
        nodes = workflow.get("nodes", []) if isinstance(workflow, dict) else []
        heavy_nodes: list[str] = []
        estimated = _BASE_OVERHEAD_GB
        resolution_scale = 1.0
        for node in nodes:
            if not isinstance(node, dict):
                continue
            class_type = str(node.get("class_type", node.get("type", "")))
            cost = _HEAVY_NODE_VRAM_GB.get(class_type)
            if cost is not None:
                estimated += cost
                heavy_nodes.append(class_type)
            if class_type in _RESOLUTION_SENSITIVE and isinstance(node.get("inputs"), dict):
                resolution_scale = max(resolution_scale, _resolution_scale(node["inputs"]))
        estimated *= resolution_scale
        verdict = _verdict_for(estimated, total_gb)
        name = workflow.get("_meta", {}).get("title") if isinstance(workflow.get("_meta"), dict) else None
        estimates.append({
            "workflow": name or f"workflow-{index}",
            "estimated_gb": round(estimated, 1),
            "budget_gb": round(total_gb, 1),
            "verdict": verdict,
            "heavy_nodes": sorted(set(heavy_nodes)),
        })
    overall = "red" if any(item["verdict"] == "red" for item in estimates) else (
        "yellow" if any(item["verdict"] == "yellow" for item in estimates) else "green"
    )
    return {"vram_total_gb": round(total_gb, 1), "verdict": overall, "estimates": estimates}


def _resolution_scale(inputs: dict[str, Any]) -> float:
    """Scale factor for latent/image dimensions relative to 1024x1024-ish."""
    width = _as_float(inputs.get("width"))
    height = _as_float(inputs.get("height"))
    if not width or not height:
        return 1.0
    return max(1.0, round((width * height) / (1024 * 1024), 2))


def _verdict_for(estimated_gb: float, total_gb: float) -> str:
    ratio = estimated_gb / total_gb
    if ratio <= 0.7:
        return "green"
    if ratio <= 0.95:
        return "yellow"
    return "red"


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_error(exc: Exception) -> str:
    return str(exc)[:500]
