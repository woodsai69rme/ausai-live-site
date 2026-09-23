"""Tests for the character-consistency tooling (E6)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_influencer_studio.character_consistency import (
    build_character_sheet,
    instant_character_workflow,
    load_character_sheet,
    lora_training_manifest,
)


def _sheet(tmp_path: Path) -> dict:
    return build_character_sheet(
        name="Chloe",
        reference_path=str(tmp_path / "refs" / "chloe_1.png"),
        output_path=tmp_path / "sheets" / "chloe.json",
        traits=["pink hair", "neon jacket"],
    )


def test_build_character_sheet_writes_file_and_derives_trigger(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path)
    assert sheet["name"] == "Chloe"
    assert sheet["trigger_word"] == "chloe"
    assert "photo of chloe" in sheet["prompts"]["positive"]
    assert "pink hair" in sheet["prompts"]["positive"]
    path = tmp_path / "sheets" / "chloe.json"
    assert path.is_file()
    # Roundtrip through the loader.
    assert load_character_sheet(path) == sheet


def test_build_character_sheet_rejects_empty_name(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        build_character_sheet("  ", "ref.png", tmp_path / "x.json")


def test_build_character_sheet_refuses_to_overwrite(tmp_path: Path) -> None:
    _sheet(tmp_path)
    with pytest.raises(FileExistsError, match="already exists"):
        _sheet(tmp_path)


def test_build_character_sheet_accepts_custom_trigger(tmp_path: Path) -> None:
    sheet = build_character_sheet(
        "Zaya",
        "z.png",
        tmp_path / "z.json",
        trigger_word="zayastar",
    )
    assert sheet["trigger_word"] == "zayastar"


def test_instant_character_workflow_injects_reference(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path)
    workflow = instant_character_workflow(sheet, tmp_path / "wf" / "chloe.json")
    assert workflow["6"]["class_type"] == "LoadImage"
    assert workflow["6"]["inputs"]["image"] == sheet["reference_path"]
    assert workflow["5"]["class_type"] == "IPAdapterUnifiedLoader"
    assert workflow["7"]["class_type"] == "IPAdapterAdvanced"
    # Deterministic wiring: KSampler model comes from the IPAdapter chain, not the raw checkpoint.
    assert workflow["11"]["inputs"]["model"] == ["7", 0]
    assert workflow["_meta"]["required_custom_nodes"]
    assert "chloe" in workflow["_meta"]["trigger_word"]
    # Resolution respected.
    assert workflow["10"]["inputs"] == {"width": 896, "height": 512, "batch_size": 1}


def test_instant_character_workflow_requires_reference(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="reference_path is required"):
        instant_character_workflow({"name": "X"}, tmp_path / "wf.json")


def test_lora_training_manifest_captions_all_images(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path)
    images = [tmp_path / "refs" / f"chloe_{i}.png" for i in range(1, 4)]
    manifest = lora_training_manifest(sheet, images, tmp_path / "lora" / "chloe.json")
    assert manifest["trigger_word"] == "chloe"
    assert manifest["network"]["type"] == "lora"
    assert manifest["network"]["alpha"] == 16  # dim // 2
    assert len(manifest["dataset"]) == 3
    for entry in manifest["dataset"]:
        assert entry["caption"] == "photo of chloe"
    assert Path(tmp_path / "lora" / "chloe.json").is_file()


def test_lora_training_manifest_requires_images(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path)
    with pytest.raises(ValueError, match="At least one reference image"):
        lora_training_manifest(sheet, [], tmp_path / "lora" / "x.json")


def test_load_character_sheet_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_character_sheet(tmp_path / "missing.json")


def test_load_character_sheet_rejects_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid character sheet JSON"):
        load_character_sheet(path)
