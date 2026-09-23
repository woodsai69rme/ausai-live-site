"""Text-to-speech adapter for faceless voiceover generation.

Provides four backends behind one interface:

- ``edge`` (default) — free local Microsoft Edge TTS via ``edge-tts``; no API key.
- ``kokoro`` — free local Kokoro ONNX TTS on CPU (``kokoro-onnx`` package +
  model files); no API key and fully offline.
- ``openai`` — OpenAI ``tts-1`` API (MP3).
- ``elevenlabs`` — ElevenLabs TTS API (MP3), the highest-quality paid option.

Keys are read from ``StudioConfig`` or the environment; no credentials are ever
written into the generated audio or returned to callers.
"""

from __future__ import annotations

import os
import subprocess
import wave
from pathlib import Path
from typing import Any

import requests

from ai_influencer_studio.config import StudioConfig

OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"
ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
DEFAULT_OPENAI_VOICE = "alloy"
DEFAULT_ELEVENLABS_VOICE = "21m00Tcm4TlvDq8ikWAM"  # Rachel
DEFAULT_EDGE_VOICE = "en-US-AriaNeural"
DEFAULT_KOKORO_VOICE = "af_heart"
KOKORO_MODEL_PATH_ENV = "KOKORO_MODEL_PATH"
KOKORO_VOICES_PATH_ENV = "KOKORO_VOICES_PATH"


class TTSAdapter:
    """Synthesize voiceover audio for faceless content."""

    def __init__(self, config: StudioConfig | None = None) -> None:
        self.config = config or StudioConfig.from_file()

    def synthesize(
        self,
        text: str,
        output_path: Path | str,
        provider: str | None = None,
        voice: str | None = None,
    ) -> dict[str, Any]:
        """Synthesize ``text`` into an audio file at ``output_path``.

        Returns a dict with ``provider``, ``voice``, and ``output``. The chosen
        provider defaults to ``StudioConfig.tts_provider`` (``edge`` when unset).
        """
        provider = (provider or self.config.tts_provider or "edge").lower()
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        if not text.strip():
            raise ValueError("TTS input text must not be empty")

        if provider == "edge":
            return self._synthesize_edge(text, output, voice)
        if provider == "kokoro":
            return self._synthesize_kokoro(text, output, voice)
        if provider == "openai":
            return self._synthesize_openai(text, output, voice)
        if provider == "elevenlabs":
            return self._synthesize_elevenlabs(text, output, voice)
        raise ValueError(f"Unsupported TTS provider: {provider}")

    def _synthesize_edge(self, text: str, output: Path, voice: str | None) -> dict[str, Any]:
        try:
            import asyncio

            import edge_tts  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "edge-tts is not installed. Run `pip install edge-tts` to enable the free local backend."
            ) from exc
        voice_arg = voice or self.config.tts_voice or DEFAULT_EDGE_VOICE
        asyncio.run(edge_tts.Communicate(text, voice_arg).save(str(output)))
        return {"provider": "edge", "voice": voice_arg, "output": str(output)}

    def _synthesize_kokoro(self, text: str, output: Path, voice: str | None) -> dict[str, Any]:
        """Synthesize offline on CPU with Kokoro ONNX (free, no API key).

        Requires ``pip install kokoro-onnx`` plus the model and voices files
        (paths from ``StudioConfig.kokoro_model_path``/``kokoro_voices_path``
        or the ``KOKORO_MODEL_PATH``/``KOKORO_VOICES_PATH`` env vars). The
        model emits 24 kHz mono PCM, written as WAV; when the caller asked for
        MP3 and ffmpeg is available the WAV is transcoded in place.
        """
        try:
            from kokoro_onnx import KokoroOnnx  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "kokoro-onnx is not installed. Run `pip install kokoro-onnx` and download "
                "the kokoro-v1.0.onnx + voices-v1.0.bin files to enable the free local backend."
            ) from exc
        configured_model_path = getattr(self.config, "kokoro_model_path", None)
        configured_voices_path = getattr(self.config, "kokoro_voices_path", None)
        model_path = Path(
            configured_model_path or os.environ.get(KOKORO_MODEL_PATH_ENV, "")
        ).expanduser()
        voices_path = Path(
            configured_voices_path or os.environ.get(KOKORO_VOICES_PATH_ENV, "")
        ).expanduser()
        if not model_path.is_file() or not voices_path.is_file():
            raise RuntimeError(
                "Kokoro model files not found. Set kokoro_model_path/kokoro_voices_path in config "
                "or the KOKORO_MODEL_PATH/KOKORO_VOICES_PATH env vars to the .onnx and .bin files."
            )
        voice_arg = voice or self.config.tts_voice or DEFAULT_KOKORO_VOICE
        kokoro = KokoroOnnx(str(model_path), str(voices_path))
        samples, sample_rate = kokoro.create(text=text, voice=voice_arg, speed=1.0, lang="en-us")

        wav_path = output if output.suffix.lower() == ".wav" else output.with_suffix(".wav")
        wav_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(wav_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes((samples * 32767).astype("<i2").tobytes())

        final_path = wav_path
        if output.suffix.lower() == ".mp3":
            try:
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(wav_path), str(output)],
                    capture_output=True,
                    timeout=120,
                    check=True,
                )
                wav_path.unlink(missing_ok=True)
                final_path = output
            except (OSError, subprocess.CalledProcessError):
                # ffmpeg missing or failed: keep the WAV rather than dropping audio.
                final_path = wav_path
        return {"provider": "kokoro", "voice": voice_arg, "output": str(final_path)}

    def _synthesize_openai(self, text: str, output: Path, voice: str | None) -> dict[str, Any]:
        api_key = self.config.openai_api_key or os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        voice_arg = voice or self.config.tts_voice or DEFAULT_OPENAI_VOICE
        response = requests.post(
            OPENAI_TTS_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "tts-1", "voice": voice_arg, "input": text, "response_format": "mp3"},
            timeout=120,
        )
        response.raise_for_status()
        output.write_bytes(response.content)
        return {"provider": "openai", "voice": voice_arg, "output": str(output)}

    def _synthesize_elevenlabs(self, text: str, output: Path, voice: str | None) -> dict[str, Any]:
        api_key = self.config.elevenlabs_api_key or os.environ.get("ELEVENLABS_API_KEY", "")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is not set")
        voice_id = voice or self.config.tts_voice or DEFAULT_ELEVENLABS_VOICE
        response = requests.post(
            ELEVENLABS_TTS_URL.format(voice_id=voice_id),
            headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
            json={"text": text, "model_id": "eleven_monolingual_v1"},
            timeout=120,
        )
        response.raise_for_status()
        output.write_bytes(response.content)
        return {"provider": "elevenlabs", "voice": voice_id, "output": str(output)}
