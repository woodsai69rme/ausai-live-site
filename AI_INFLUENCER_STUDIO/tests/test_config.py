"""Tests for ai_influencer_studio.config."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_influencer_studio.config import StudioConfig


def test_environment_keys_load_without_config_file(tmp_path: Path) -> None:
    with patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "openai-env",
            "OPENROUTER_API_KEY": "router-env",
            "YOUTUBE_API_KEY": "youtube-env",
            "ELEVENLABS_API_KEY": "eleven-env",
        },
        clear=False,
    ):
        loaded = StudioConfig.from_file(tmp_path / "missing.json")

    assert loaded.openai_api_key == "openai-env"
    assert loaded.openrouter_api_key == "router-env"
    assert loaded.youtube_api_key == "youtube-env"
    assert loaded.elevenlabs_api_key == "eleven-env"


def test_config_rejects_non_object_json(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="must contain a JSON object"):
        StudioConfig.from_file(config_path)


def test_default_paths_resolve() -> None:
    config = StudioConfig()
    assert config.data_dir.expanduser().is_absolute()
    assert config.media_dir.expanduser().is_absolute()
    # Default script paths are resolved relative to the current working directory.
    # They may not exist when tests run from a different directory, so only
    # assert that they are absolute paths.
    assert config.ai_influencer_pipeline_script.is_absolute()
    assert config.social_media_automation_script.is_absolute()
    assert config.ai_influencer_factory_script.is_absolute()
    assert config.comfyui_orchestrator_script.is_absolute()
    assert config.auto_poster_script.is_absolute()


def test_save_and_load(tmp_path: Path) -> None:
    config = StudioConfig(
        openai_api_key="test-key",
        data_dir=tmp_path / "data",
        media_dir=tmp_path / "media",
    )
    config_path = tmp_path / "config.json"
    config.save(config_path)

    # Isolate from environment variables so the saved value is preserved.
    env_vars = ["OPENAI_API_KEY", "OPENROUTER_API_KEY"]
    with patch.dict(os.environ, {k: "" for k in env_vars}, clear=False):
        loaded = StudioConfig.from_file(config_path)

    assert loaded.openai_api_key == "test-key"
    assert loaded.data_dir == tmp_path / "data"
    assert loaded.media_dir == tmp_path / "media"


def test_tts_fields_save_and_load(tmp_path: Path) -> None:
    config = StudioConfig(
        elevenlabs_api_key="el-key",
        tts_provider="kokoro",
        tts_voice="af_heart",
        kokoro_model_path=tmp_path / "kokoro.onnx",
        kokoro_voices_path=tmp_path / "voices.bin",
    )
    config_path = tmp_path / "config.json"
    config.save(config_path)

    with patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}, clear=False):
        loaded = StudioConfig.from_file(config_path)

    assert loaded.elevenlabs_api_key == "el-key"
    assert loaded.tts_provider == "kokoro"
    assert loaded.tts_voice == "af_heart"
    assert loaded.kokoro_model_path == tmp_path / "kokoro.onnx"
    assert loaded.kokoro_voices_path == tmp_path / "voices.bin"


def test_gdrive_fields_save_and_load(tmp_path: Path) -> None:
    config = StudioConfig(
        gdrive_folder_url="https://drive.google.com/drive/folders/abc123",
        gdrive_state_path=tmp_path / "gdrive_state.json",
    )
    config_path = tmp_path / "config.json"
    config.save(config_path)

    loaded = StudioConfig.from_file(config_path)
    assert loaded.gdrive_folder_url == "https://drive.google.com/drive/folders/abc123"
    assert loaded.gdrive_state_path == tmp_path / "gdrive_state.json"


def test_youtube_fields_save_and_load(tmp_path: Path) -> None:
    config = StudioConfig(
        youtube_token_path=tmp_path / "yt_token.json",
        youtube_client_secrets_path=tmp_path / "yt_secrets.json",
        youtube_category_id="22",
        youtube_default_privacy="unlisted",
        youtube_playlist_title="My Songs",
    )
    config_path = tmp_path / "config.json"
    config.save(config_path)

    loaded = StudioConfig.from_file(config_path)
    assert loaded.youtube_token_path == tmp_path / "yt_token.json"
    assert loaded.youtube_client_secrets_path == tmp_path / "yt_secrets.json"
    assert loaded.youtube_category_id == "22"
    assert loaded.youtube_default_privacy == "unlisted"
    assert loaded.youtube_playlist_title == "My Songs"


def test_gdrive_rclone_fields_save_and_load(tmp_path: Path) -> None:
    config = StudioConfig(
        gdrive_backend="rclone",
        gdrive_rclone_remote="gdrive:",
        gdrive_rclone_path="SharedRefMedia",
    )
    config_path = tmp_path / "config.json"
    config.save(config_path)

    loaded = StudioConfig.from_file(config_path)
    assert loaded.gdrive_backend == "rclone"
    assert loaded.gdrive_rclone_remote == "gdrive:"
    assert loaded.gdrive_rclone_path == "SharedRefMedia"


def test_gdrive_default_state_path_is_absolute() -> None:
    config = StudioConfig()
    assert config.gdrive_state_path.expanduser().is_absolute()
    assert config.gdrive_folder_url
