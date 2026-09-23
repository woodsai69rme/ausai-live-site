"""Configuration management for AI Influencer Studio."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class StudioConfig:
    """Runtime configuration for the studio."""

    # AI providers
    openai_api_key: str = ""
    openrouter_api_key: str = ""
    youtube_api_key: str = ""
    ollama_url: str = "http://localhost:11434"

    # YouTube publishing (OAuth2, same token convention as gdrive_uploader)
    youtube_token_path: Path = field(
        default_factory=lambda: Path("~/.ai_influencer_studio/youtube_token.json").expanduser()
    )
    youtube_client_secrets_path: Path = field(
        default_factory=lambda: Path("~/.ai_influencer_studio/youtube_client_secrets.json").expanduser()
    )
    youtube_category_id: str = "10"  # Music
    youtube_default_privacy: str = "private"
    youtube_playlist_title: str = ""

    # Text-to-speech
    elevenlabs_api_key: str = ""
    tts_provider: str = "edge"  # edge (free local) | kokoro (offline) | openai | elevenlabs
    tts_voice: str = ""
    kokoro_model_path: Path | None = None
    kokoro_voices_path: Path | None = None

    # External tools
    comfyui_url: str = "http://localhost:8188"
    n8n_webhook_url: str = "http://localhost:5678/webhook/publish-video"

    # Scheduler integrations
    postiz_api_url: str = ""
    postiz_api_key: str = ""
    mixpost_api_url: str = ""
    mixpost_api_key: str = ""

    # Google Drive reference-media sharing
    gdrive_folder_url: str = "https://drive.google.com/drive/folders/13Ck6VKzc2pVIPBNW33wWjSTSDmRjYP2f?usp=sharing"
    gdrive_state_path: Path = field(
        default_factory=lambda: Path("~/.ai_influencer_studio/gdrive_upload_state.json").expanduser()
    )
    # Chrome profile for uploads: empty = automated profile; set to the
    # operator's signed-in main profile dir (e.g. ".../User Data/Profile 7")
    # or use gdrive_cdp_url to attach to an already-running Chrome.
    gdrive_chrome_user_data_dir: str = ""
    gdrive_cdp_url: str = ""
    # Upload transport: "browser" (Playwright), "drive_api" (OAuth2), or "rclone".
    gdrive_backend: str = "browser"
    # rclone remote + folder inside it for the rclone backend (e.g. "gdrive:" / "refmedia").
    gdrive_rclone_remote: str = ""
    gdrive_rclone_path: str = "refmedia"
    gdrive_token_path: Path = field(
        default_factory=lambda: Path("~/.ai_influencer_studio/gdrive_token.json").expanduser()
    )
    gdrive_client_secrets_path: Path = field(
        default_factory=lambda: Path("~/.ai_influencer_studio/gdrive_client_secrets.json").expanduser()
    )

    # Workspace paths
    data_dir: Path = field(default_factory=lambda: Path("~/.ai_influencer_studio").expanduser())
    media_dir: Path = field(default_factory=lambda: Path("~/.ai_influencer_studio/media").expanduser())

    # AI model preferences
    default_model: str = "openai/gpt-4o-mini"
    local_model: str = "qwen2.5:latest"

    # Platform credentials / settings
    platforms: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Legacy script paths (relative to project root)
    ai_influencer_pipeline_script: Path = field(
        default_factory=lambda: Path("SCRIPTS/PYTHON/ai_influencer_pipeline.py").resolve()
    )
    social_media_automation_script: Path = field(
        default_factory=lambda: Path("SCRIPTS/PYTHON/social_media_automation.py").resolve()
    )
    ai_influencer_factory_script: Path = field(
        default_factory=lambda: Path("ai_influencer_factory.py").resolve()
    )
    comfyui_orchestrator_script: Path = field(
        default_factory=lambda: Path("ComfyUI/tools/orchestrator.py").resolve()
    )
    auto_poster_script: Path = field(
        default_factory=lambda: Path("ComfyUI/tools/auto_poster.py").resolve()
    )

    @classmethod
    def from_file(cls, path: Path | None = None) -> StudioConfig:
        """Load config from JSON file or environment variables."""
        if path is None:
            path = Path("~/.ai_influencer_studio/config.json").expanduser()

        defaults = cls()
        data: dict[str, Any] = {}
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                loaded = json.load(fh)
            if not isinstance(loaded, dict):
                raise ValueError("Studio config must contain a JSON object")
            data = loaded

        # Merge with defaults
        for key in cls.__dataclass_fields__:  # type: ignore[attr-defined]
            if key in data:
                if key in (
                    "data_dir", "media_dir",
                    "gdrive_state_path", "gdrive_token_path", "gdrive_client_secrets_path",
                    "youtube_token_path", "youtube_client_secrets_path",
                ):
                    data[key] = Path(data[key]).expanduser()
                elif key in ("kokoro_model_path", "kokoro_voices_path"):
                    data[key] = Path(data[key]).expanduser() if data[key] else None
                elif key.endswith("_script"):
                    data[key] = Path(data[key]).expanduser().resolve()
                setattr(defaults, key, data[key])

        # Environment overrides
        if os.environ.get("OPENAI_API_KEY"):
            defaults.openai_api_key = os.environ["OPENAI_API_KEY"]
        if os.environ.get("OPENROUTER_API_KEY"):
            defaults.openrouter_api_key = os.environ["OPENROUTER_API_KEY"]
        if os.environ.get("YOUTUBE_API_KEY"):
            defaults.youtube_api_key = os.environ["YOUTUBE_API_KEY"]
        if os.environ.get("ELEVENLABS_API_KEY"):
            defaults.elevenlabs_api_key = os.environ["ELEVENLABS_API_KEY"]
        if os.environ.get("KOKORO_MODEL_PATH"):
            defaults.kokoro_model_path = Path(os.environ["KOKORO_MODEL_PATH"]).expanduser()
        if os.environ.get("KOKORO_VOICES_PATH"):
            defaults.kokoro_voices_path = Path(os.environ["KOKORO_VOICES_PATH"]).expanduser()

        return defaults

    def save(self, path: Path | None = None) -> None:
        """Persist config to JSON."""
        if path is None:
            path = Path("~/.ai_influencer_studio/config.json").expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(
                {
                    "openai_api_key": self.openai_api_key,
                    "openrouter_api_key": self.openrouter_api_key,
                    "youtube_api_key": self.youtube_api_key,
                    "ollama_url": self.ollama_url,
                    "elevenlabs_api_key": self.elevenlabs_api_key,
                    "tts_provider": self.tts_provider,
                    "tts_voice": self.tts_voice,
                    "kokoro_model_path": str(self.kokoro_model_path) if self.kokoro_model_path else "",
                    "kokoro_voices_path": str(self.kokoro_voices_path) if self.kokoro_voices_path else "",
                    "comfyui_url": self.comfyui_url,
                    "n8n_webhook_url": self.n8n_webhook_url,
                    "postiz_api_url": self.postiz_api_url,
                    "postiz_api_key": self.postiz_api_key,
                    "mixpost_api_url": self.mixpost_api_url,
                    "mixpost_api_key": self.mixpost_api_key,
                    "gdrive_folder_url": self.gdrive_folder_url,
                    "gdrive_state_path": str(self.gdrive_state_path),
                    "gdrive_chrome_user_data_dir": self.gdrive_chrome_user_data_dir,
                    "gdrive_cdp_url": self.gdrive_cdp_url,
                    "gdrive_backend": self.gdrive_backend,
                    "gdrive_rclone_remote": self.gdrive_rclone_remote,
                    "gdrive_rclone_path": self.gdrive_rclone_path,
                    "gdrive_token_path": str(self.gdrive_token_path),
                    "gdrive_client_secrets_path": str(self.gdrive_client_secrets_path),
                    "youtube_token_path": str(self.youtube_token_path),
                    "youtube_client_secrets_path": str(self.youtube_client_secrets_path),
                    "youtube_category_id": self.youtube_category_id,
                    "youtube_default_privacy": self.youtube_default_privacy,
                    "youtube_playlist_title": self.youtube_playlist_title,
                    "data_dir": str(self.data_dir),
                    "media_dir": str(self.media_dir),
                    "default_model": self.default_model,
                    "local_model": self.local_model,
                    "platforms": self.platforms,
                    "ai_influencer_pipeline_script": str(self.ai_influencer_pipeline_script),
                    "social_media_automation_script": str(self.social_media_automation_script),
                    "ai_influencer_factory_script": str(self.ai_influencer_factory_script),
                    "comfyui_orchestrator_script": str(self.comfyui_orchestrator_script),
                    "auto_poster_script": str(self.auto_poster_script),
                },
                fh,
                indent=2,
            )
