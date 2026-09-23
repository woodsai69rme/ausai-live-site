"""Video repurposing utilities for AI Influencer Studio.

Takes a generated video and produces platform-native vertical cuts
(e.g., TikTok, Instagram Reels, YouTube Shorts) with safe zones and
optional burned-in captions.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PlatformSpec:
    """Target platform specifications for a repurposed clip."""

    name: str
    width: int
    height: int
    min_duration: float = 0.0
    max_duration: float = 0.0
    safe_zone_top: float = 0.1
    safe_zone_bottom: float = 0.1


# Common vertical platform specs.
PLATFORM_SPECS: dict[str, PlatformSpec] = {
    "tiktok": PlatformSpec(
        name="tiktok",
        width=1080,
        height=1920,
        min_duration=1.0,
        max_duration=180.0,
        safe_zone_top=0.15,
        safe_zone_bottom=0.20,
    ),
    "instagram": PlatformSpec(
        name="instagram",
        width=1080,
        height=1920,
        min_duration=1.0,
        max_duration=90.0,
        safe_zone_top=0.15,
        safe_zone_bottom=0.20,
    ),
    "youtube": PlatformSpec(
        name="youtube",
        width=1080,
        height=1920,
        min_duration=1.0,
        max_duration=60.0,
        safe_zone_top=0.15,
        safe_zone_bottom=0.15,
    ),
}


class VideoRepurposer:
    """Repurpose a finished video into platform-native vertical clips."""

    def __init__(self, ffmpeg_path: str | None = None) -> None:
        self.ffmpeg_path = ffmpeg_path or "ffmpeg"

    def _run_ffmpeg(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        """Run ffmpeg with the given arguments."""
        cmd = [self.ffmpeg_path, *args]
        return subprocess.run(cmd, capture_output=True, text=True, check=False)

    def get_video_info(self, input_path: str | Path) -> dict[str, Any]:
        """Return ffprobe metadata for a video file."""
        ffprobe = shutil.which("ffprobe") or "ffprobe"
        cmd = [
            ffprobe,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration,r_frame_rate",
            "-of", "json",
            str(input_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {result.stderr}")
        data = json.loads(result.stdout)
        stream = data.get("streams", [{}])[0]
        width = stream.get("width", 0)
        height = stream.get("height", 0)
        duration = stream.get("duration")
        try:
            duration = float(duration) if duration is not None else 0.0
        except ValueError:
            duration = 0.0
        return {
            "width": width,
            "height": height,
            "duration": duration,
            "aspect_ratio": width / height if height else 0.0,
        }

    def create_vertical_cut(
        self,
        input_path: str | Path,
        output_path: str | Path,
        platform: str = "tiktok",
        start: float = 0.0,
        duration: float | None = None,
        caption: str | None = None,
    ) -> dict[str, Any]:
        """Create a vertical cut for a target platform.

        Crops/ scales the input to the platform's target resolution and burns
        in an optional caption inside the safe zone.
        """
        spec = PLATFORM_SPECS.get(platform)
        if spec is None:
            raise ValueError(f"Unsupported platform: {platform}")

        input_path = Path(input_path)
        output_path = Path(output_path)
        info = self.get_video_info(input_path)
        original_duration = info.get("duration", 0.0)

        if duration is None:
            duration = original_duration
        if spec.max_duration and duration > spec.max_duration:
            duration = spec.max_duration
        if duration <= 0:
            raise ValueError("duration must be positive")

        # Build crop filter to center-crop to 9:16.
        crop_filter = (
            f"scale={spec.width}:-1:force_original_aspect_ratio=decrease,"
            f"crop={spec.width}:{spec.height}"
        )

        # Burn caption inside safe zone if provided.
        drawtext = ""
        if caption:
            safe_y = int(spec.height * (spec.safe_zone_top + 0.05))
            escaped = caption.replace("'", "'\\''")
            drawtext = (
                f"drawtext=text='{escaped}':fontcolor=white:fontsize=48:"
                f"x=(w-text_w)/2:y={safe_y}:box=1:boxcolor=black@0.5"
            )

        filter_complex = crop_filter
        if drawtext:
            filter_complex += f",{drawtext}"

        args = [
            "-y",
            "-ss", str(start),
            "-t", str(duration),
            "-i", str(input_path),
            "-vf", filter_complex,
            "-c:a", "copy",
            str(output_path),
        ]

        result = self._run_ffmpeg(args)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr}")

        return {
            "input": str(input_path),
            "output": str(output_path),
            "platform": platform,
            "start": start,
            "duration": duration,
            "caption": caption,
        }

    def create_multi_clips(
        self,
        input_path: str | Path,
        output_dir: str | Path,
        platforms: list[str] | None = None,
        clip_duration: float = 15.0,
        captions: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Generate repurposed clips for multiple platforms.

        Splits the input into equal segments of ``clip_duration`` seconds and
        produces a vertical cut for each requested platform.
        """
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        info = self.get_video_info(input_path)
        total_duration = info.get("duration", 0.0)
        if total_duration <= 0:
            raise ValueError("Could not determine input video duration")

        platforms = platforms or ["tiktok"]
        results: list[dict[str, Any]] = []
        start = 0.0
        clip_index = 0
        while start < total_duration:
            remaining = total_duration - start
            duration = min(clip_duration, remaining)
            for platform in platforms:
                caption = (captions or [None] * len(platforms))[clip_index % max(len(captions or []), 1)]
                output = output_dir / f"{input_path.stem}_{platform}_{clip_index:03d}.mp4"
                result = self.create_vertical_cut(
                    input_path,
                    output,
                    platform=platform,
                    start=start,
                    duration=duration,
                    caption=caption,
                )
                results.append(result)
            start += duration
            clip_index += 1

        return results
