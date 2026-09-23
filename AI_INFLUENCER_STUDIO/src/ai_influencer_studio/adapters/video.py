"""Adapter for the legacy video generation pipeline.

Wraps ``ai_influencer_factory.py`` (Ollama -> TTS -> ComfyUI -> n8n) and
``ComfyUI/tools/orchestrator.py`` (music/social video orchestrator) so the
studio can trigger them without duplicating code.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from ai_influencer_studio.config import StudioConfig


class VideoAdapter:
    """High-level wrapper around legacy video generation scripts."""

    def __init__(self, config: StudioConfig | None = None) -> None:
        self.config = config or StudioConfig.from_file()

    def generate_talking_head_short(
        self,
        topic: str,
    ) -> dict[str, Any]:
        """Generate a short-form talking-head video via ``ai_influencer_factory.py``.

        This runs the legacy script as a subprocess because it has its own
        environment expectations (Ollama, ComfyUI, n8n).
        """
        script_path = Path(self.config.ai_influencer_factory_script)
        if not script_path.exists():
            raise FileNotFoundError(f"Legacy factory script not found: {script_path}")

        result = subprocess.run(
            [sys.executable, str(script_path), topic],
            capture_output=True,
            text=True,
            timeout=600,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "topic": topic,
        }

    def generate_music_video(
        self,
        mp3_path: Path | str,
        genre: str | None = None,
        mood: str | None = None,
        platforms: list[str] | None = None,
    ) -> dict[str, Any]:
        """Generate a music video via ``ComfyUI/tools/orchestrator.py``.

        Runs the orchestrator in a subprocess so system-Python dependencies
        (whisper, mutagen, etc.) do not pollute the studio environment.
        """
        script_path = Path(self.config.comfyui_orchestrator_script)
        if not script_path.exists():
            raise FileNotFoundError(f"ComfyUI orchestrator not found: {script_path}")

        cmd = [sys.executable, str(script_path), "music", "--mp3", str(mp3_path)]
        if genre:
            cmd += ["--genre", genre]
        if mood:
            cmd += ["--mood", mood]
        if platforms:
            if len(platforms) == 1:
                cmd += ["--platform", platforms[0]]
            else:
                cmd += ["--all"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "mp3": str(mp3_path),
        }

    def generate_social_video(
        self,
        topic: str,
        platform: str = "youtube",
        style: str | None = None,
    ) -> dict[str, Any]:
        """Generate a topic-based social video via the ComfyUI orchestrator."""
        script_path = Path(self.config.comfyui_orchestrator_script)
        if not script_path.exists():
            raise FileNotFoundError(f"ComfyUI orchestrator not found: {script_path}")

        cmd = [
            sys.executable,
            str(script_path),
            "social",
            "--topic",
            topic,
            "--platform",
            platform,
        ]
        if style:
            cmd += ["--style", style]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "topic": topic,
            "platform": platform,
        }

    def _build_orchestrator_cmd(
        self,
        script_path: Path,
        plan: dict[str, Any],
        plan_file: Path,
        platforms: list[str] | None = None,
    ) -> list[str]:
        """Build the ComfyUI orchestrator command for a song plan."""
        audio_path = Path(plan["audio_path"])
        cmd: list[str] = [
            sys.executable,
            str(script_path),
            "music",
            "--mp3",
            str(audio_path),
            "--plan",
            str(plan_file),
        ]
        if plan.get("genre"):
            cmd += ["--genre", plan["genre"]]
        if plan.get("mood"):
            cmd += ["--mood", plan["mood"]]
        if plan.get("character_ref"):
            cmd += ["--character-ref", str(plan["character_ref"])]
        mode = plan.get("generation_mode", "full")
        if mode == "clip_only":
            cmd += ["--generate-clips-only"]
        elif mode == "assembly_only":
            cmd += ["--assemble-only"]
        if platforms:
            if len(platforms) == 1:
                cmd += ["--platform", platforms[0]]
            else:
                cmd += ["--all"]
        return cmd

    def execute_music_video_plan(
        self,
        plan: dict[str, Any],
        platforms: list[str] | None = None,
    ) -> dict[str, Any]:
        """Execute a single song plan via ``ComfyUI/tools/orchestrator.py``.

        The plan dict is persisted to a temporary JSON file and passed to the
        orchestrator with ``--plan`` so it can follow the generated timeline.
        """
        script_path = Path(self.config.comfyui_orchestrator_script)
        if not script_path.exists():
            raise FileNotFoundError(f"ComfyUI orchestrator not found: {script_path}")

        audio_path = Path(plan["audio_path"])
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(plan, tmp, indent=2)
            plan_file = Path(tmp.name)

        try:
            cmd = self._build_orchestrator_cmd(script_path, plan, plan_file, platforms)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "mp3": str(audio_path),
                "plan_file": str(plan_file),
            }
        finally:
            plan_file.unlink(missing_ok=True)

    async def execute_music_video_plan_streaming(
        self,
        plan: dict[str, Any],
        platforms: list[str] | None = None,
    ) -> AsyncIterator[str]:
        """Execute a single song plan and yield stdout/stderr lines as they arrive."""
        script_path = Path(self.config.comfyui_orchestrator_script)
        if not script_path.exists():
            raise FileNotFoundError(f"ComfyUI orchestrator not found: {script_path}")

        audio_path = Path(plan["audio_path"])
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(plan, tmp, indent=2)
            plan_file = Path(tmp.name)

        try:
            cmd = self._build_orchestrator_cmd(script_path, plan, plan_file, platforms)

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            assert process.stdout is not None
            assert process.stderr is not None

            queue: asyncio.Queue[str] = asyncio.Queue()

            async def _reader(stream: asyncio.StreamReader, stream_type: str) -> None:
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    await queue.put({
                        "type": stream_type,
                        "line": line.decode("utf-8", errors="replace").rstrip(),
                    })

            async def _waiter() -> None:
                await process.wait()
                await queue.put({"type": "done", "returncode": process.returncode})

            tasks = [
                asyncio.create_task(_reader(process.stdout, "stdout")),
                asyncio.create_task(_reader(process.stderr, "stderr")),
                asyncio.create_task(_waiter()),
            ]

            while True:
                item = await asyncio.wait_for(queue.get(), timeout=1800)
                yield item
                if item.startswith("done:"):
                    break

            for task in tasks:
                if not task.done():
                    task.cancel()
        finally:
            plan_file.unlink(missing_ok=True)
            try:
                if process.returncode is None:
                    process.kill()
                    await process.wait()
            except Exception:
                pass
