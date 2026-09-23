"""Character consistency tooling for AI music videos.

Bridges the style bibles (JSON character descriptors) to the two practical
ways stable-diffusion keeps a character consistent across clips:

- ``instant_character_workflow`` — a ComfyUI API workflow that injects the
  character's reference image through IPAdapter-style nodes, so every
  generation of that character starts from the same face/outfit.
- ``lora_training_manifest`` — a kohya-style training manifest that turns a
  folder of reference images into a small LoRA on a trigger word.

Neither function runs a model; each emits a machine-readable artifact the
operator can hand to ComfyUI or a training tool. ``build_character_sheet``
writes the JSON descriptor that both workflows consume.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_TRIGGER_PREFIX = "photo of"
DEFAULT_NEGATIVE_PROMPT = (
    "blurry, low quality, deformed face, extra fingers, watermark, text, logo"
)


def build_character_sheet(
    name: str,
    reference_path: str,
    output_path: Path | str,
    traits: list[str] | None = None,
    trigger_word: str | None = None,
    continuity_rules: list[str] | None = None,
) -> dict[str, Any]:
    """Write a JSON character sheet and return it.

    The trigger word is derived from the character name (lowercased,
    alphanumeric) when not supplied; ``photo of <trigger>`` becomes the
    positive prompt every workflow keys on.
    """
    if not name.strip():
        raise ValueError("Character name must not be empty")
    trigger = trigger_word or _trigger_from_name(name)
    traits = traits or []
    if not isinstance(traits, list):
        raise ValueError("traits must be a list of strings")
    positive = f"{DEFAULT_TRIGGER_PREFIX} {trigger}"
    if traits:
        positive += ", " + ", ".join(str(trait).strip() for trait in traits if str(trait).strip())
    sheet: dict[str, Any] = {
        "name": name,
        "reference_path": reference_path,
        "trigger_word": trigger,
        "traits": traits,
        "continuity_rules": continuity_rules or [],
        "prompts": {
            "positive": positive,
            "negative": DEFAULT_NEGATIVE_PROMPT,
        },
    }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Character sheet already exists: {path}")
    path.write_text(json.dumps(sheet, indent=2), encoding="utf-8")
    return sheet


def instant_character_workflow(
    sheet: dict[str, Any],
    output_path: Path | str,
    width: int = 896,
    height: int = 512,
    seed: int | None = None,
    steps: int = 20,
) -> dict[str, Any]:
    """Emit a ComfyUI API workflow that injects the character reference.

    Uses an IPAdapter chain so the reference image steers every frame toward
    the same character. Node ids are deterministic; the workflow carries a
    ``_meta`` note listing the custom nodes the operator must have installed.
    """
    reference = sheet.get("reference_path")
    if not reference or not isinstance(reference, str):
        raise ValueError("Character sheet reference_path is required")
    trigger = str(sheet.get("trigger_word") or _trigger_from_name(str(sheet.get("name", "character"))))
    prompts = sheet.get("prompts", {}) if isinstance(sheet.get("prompts"), dict) else {}
    positive = str(prompts.get("positive") or f"{DEFAULT_TRIGGER_PREFIX} {trigger}")
    negative = str(prompts.get("negative") or DEFAULT_NEGATIVE_PROMPT)

    workflow: dict[str, Any] = {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "model.safetensors"},
        },
        "5": {
            "class_type": "IPAdapterUnifiedLoader",
            "inputs": {
                "model": ["4", 0],
                "preset": "PLUS",
            },
        },
        "6": {
            "class_type": "LoadImage",
            "inputs": {"image": reference},
        },
        "7": {
            "class_type": "IPAdapterAdvanced",
            "inputs": {
                "model": ["5", 0],
                "image": ["6", 0],
                "weight": 0.85,
                "start_at": 0.0,
                "end_at": 1.0,
                "combine_embeds": "concat",
            },
        },
        "8": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": positive},
        },
        "9": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": negative},
        },
        "10": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "11": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["7", 0],
                "positive": ["8", 0],
                "negative": ["9", 0],
                "latent_image": ["10", 0],
                "seed": seed if seed is not None else 0,
                "steps": steps,
                "cfg": 6.5,
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "denoise": 1.0,
            },
        },
        "12": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["11", 0], "vae": ["4", 2]},
        },
        "13": {
            "class_type": "SaveImage",
            "inputs": {"images": ["12", 0], "filename_prefix": f"char_{_trigger_from_name(str(sheet.get('name', 'char')))}"},
        },
        "_meta": {
            "title": f"Instant character: {sheet.get('name', 'unknown')}",
            "required_custom_nodes": [
                "ComfyUI_IPAdapter_plus (IPAdapterUnifiedLoader / IPAdapterAdvanced)",
                "ComfyUI-Custom-Scripts or core checkpoints",
            ],
            "reference_image": reference,
            "trigger_word": trigger,
        },
    }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(workflow, indent=2), encoding="utf-8")
    return workflow


def lora_training_manifest(
    sheet: dict[str, Any],
    reference_images: list[Path | str],
    output_path: Path | str,
    resolution: int = 1024,
    epochs: int = 10,
    network_dim: int = 32,
) -> dict[str, Any]:
    """Emit a kohya-style LoRA training manifest from a character sheet.

    Every reference image is captioned with the character's trigger word so
    the trained LoRA binds the appearance to that token.
    """
    trigger = str(sheet.get("trigger_word") or _trigger_from_name(str(sheet.get("name", "character"))))
    images = [Path(image) for image in reference_images]
    if not images:
        raise ValueError("At least one reference image is required")
    manifest: dict[str, Any] = {
        "character": sheet.get("name", "unknown"),
        "trigger_word": trigger,
        "caption_prefix": f"{DEFAULT_TRIGGER_PREFIX} {trigger}",
        "network": {
            "type": "lora",
            "dim": network_dim,
            "alpha": network_dim // 2,
        },
        "training": {
            "resolution": resolution,
            "epochs": epochs,
            "batch_size": 1,
            "learning_rate": 1e-4,
            "optimizer": "AdamW8bit",
            "scheduler": "cosine",
        },
        "dataset": [
            {
                "image": str(image),
                "caption": f"{DEFAULT_TRIGGER_PREFIX} {trigger}",
            }
            for image in images
        ],
    }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def load_character_sheet(path: Path | str) -> dict[str, Any]:
    """Load a JSON character sheet, failing clearly on malformed input."""
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"Character sheet not found: {file_path}")
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid character sheet JSON: {file_path}") from exc
    if not isinstance(data, dict):
        raise ValueError("Character sheet must be a JSON object")
    return data


def _trigger_from_name(name: str) -> str:
    """Derive a lowercase alphanumeric trigger word from a character name."""
    cleaned = "".join(character.lower() for character in name if character.isalnum())
    return cleaned or "character"
