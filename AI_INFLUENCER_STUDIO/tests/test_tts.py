"""Tests for the text-to-speech adapter."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_influencer_studio.adapters.tts import TTSAdapter
from ai_influencer_studio.config import StudioConfig


def test_synthesize_rejects_unknown_provider(tmp_path: Path) -> None:
    adapter = TTSAdapter(StudioConfig())
    with pytest.raises(ValueError, match="Unsupported TTS provider"):
        adapter.synthesize("hello", tmp_path / "out.mp3", provider="nope")


def test_synthesize_rejects_empty_text(tmp_path: Path) -> None:
    adapter = TTSAdapter(StudioConfig())
    with pytest.raises(ValueError, match="must not be empty"):
        adapter.synthesize("   ", tmp_path / "out.mp3", provider="openai")


def test_openai_backend_writes_file(tmp_path: Path) -> None:
    config = StudioConfig(openai_api_key="test-key", tts_provider="openai", tts_voice="alloy")
    adapter = TTSAdapter(config)

    response = MagicMock()
    response.content = b"FAKE_MP3"
    response.raise_for_status.return_value = None
    output = tmp_path / "out.mp3"
    with patch("ai_influencer_studio.adapters.tts.requests.post", return_value=response) as mock_post:
        result = adapter.synthesize("hello", output)

    assert result["provider"] == "openai"
    assert result["voice"] == "alloy"
    assert output.read_bytes() == b"FAKE_MP3"
    assert mock_post.call_args.kwargs["headers"] == {"Authorization": "Bearer test-key"}


def test_elevenlabs_backend_writes_file(tmp_path: Path) -> None:
    config = StudioConfig(elevenlabs_api_key="el-key", tts_provider="elevenlabs", tts_voice="voice-id-1")
    adapter = TTSAdapter(config)

    response = MagicMock()
    response.content = b"FAKE_MP3"
    response.raise_for_status.return_value = None
    output = tmp_path / "out.mp3"
    with patch("ai_influencer_studio.adapters.tts.requests.post", return_value=response):
        result = adapter.synthesize("hello", output)

    assert result["provider"] == "elevenlabs"
    assert result["voice"] == "voice-id-1"
    assert output.read_bytes() == b"FAKE_MP3"


def test_openai_backend_requires_key(tmp_path: Path) -> None:
    config = StudioConfig(openai_api_key="", tts_provider="openai")
    adapter = TTSAdapter(config)
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY is not set"):
            adapter.synthesize("hello", tmp_path / "out.mp3", provider="openai")


def test_edge_backend_raises_when_missing(tmp_path: Path) -> None:
    config = StudioConfig(tts_provider="edge")
    adapter = TTSAdapter(config)
    real_import = __import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "edge_tts":
            raise ImportError("no edge_tts")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    with patch("builtins.__import__", side_effect=fake_import):
        with pytest.raises(RuntimeError, match="edge-tts is not installed"):
            adapter.synthesize("hello", tmp_path / "out.mp3", provider="edge")


def test_kokoro_backend_raises_when_package_missing(tmp_path: Path) -> None:
    config = StudioConfig(tts_provider="kokoro")
    adapter = TTSAdapter(config)
    real_import = __import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name.startswith("kokoro_onnx"):
            raise ImportError("no kokoro-onnx")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    with patch("builtins.__import__", side_effect=fake_import):
        with pytest.raises(RuntimeError, match="kokoro-onnx is not installed"):
            adapter.synthesize("hello", tmp_path / "out.mp3", provider="kokoro")


def test_kokoro_backend_raises_when_model_files_missing(tmp_path: Path) -> None:
    import types

    fake_module = types.ModuleType("kokoro_onnx")
    fake_module.KokoroOnnx = MagicMock()
    config = StudioConfig(tts_provider="kokoro")  # no kokoro_model_path set
    adapter = TTSAdapter(config)
    with patch.dict("sys.modules", {"kokoro_onnx": fake_module}):
        with pytest.raises(RuntimeError, match="Kokoro model files not found"):
            adapter.synthesize("hello", tmp_path / "out.mp3", provider="kokoro")


def test_kokoro_backend_writes_wav(tmp_path: Path) -> None:
    import types

    import numpy as np

    model_path = tmp_path / "kokoro-v1.0.onnx"
    voices_path = tmp_path / "voices-v1.0.bin"
    model_path.write_bytes(b"M")
    voices_path.write_bytes(b"V")

    fake_module = types.ModuleType("kokoro_onnx")
    fake_kokoro = MagicMock()
    fake_kokoro.create.return_value = (np.array([0.1, -0.2, 0.3], dtype=np.float32), 24000)
    fake_module.KokoroOnnx = MagicMock(return_value=fake_kokoro)

    config = StudioConfig(
        tts_provider="kokoro",
        kokoro_model_path=model_path,
        kokoro_voices_path=voices_path,
    )
    adapter = TTSAdapter(config)
    output = tmp_path / "out.wav"

    with patch.dict("sys.modules", {"kokoro_onnx": fake_module}):
        result = adapter.synthesize("hello", output, provider="kokoro")

    assert result["provider"] == "kokoro"
    assert result["output"] == str(output)
    assert output.read_bytes().startswith(b"RIFF")
    fake_module.KokoroOnnx.assert_called_once_with(str(model_path), str(voices_path))
