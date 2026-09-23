"""Music video research and planning engine.

The engine helps operators research free video generators, analyze YouTube
music-video trends, scan audio libraries, analyze previous videos for style,
and create reusable clip-based plans with consistent characters.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

from ai_influencer_studio.audio_analysis import analyze_audio
from ai_influencer_studio.youtube_client import YouTubeDataClient

# Catalog of free / freemium video generation options.
FREE_VIDEO_GENERATORS: dict[str, dict[str, Any]] = {
    "wan21": {
        "name": "Wan 2.1",
        "type": "local",
        "best_for": "8GB+ VRAM, open-source T2V/I2V",
        "pros": ["Open source", "Audio-driven video", "I2V support"],
        "cons": ["High VRAM for 14B", "Slow on 8GB"],
    },
    "ltx2": {
        "name": "LTX Video 2.x",
        "type": "local",
        "best_for": "High-end GPUs, 4K/50fps",
        "pros": ["4K 50FPS", "Sync audio gen"],
        "cons": ["Extreme VRAM needs"],
    },
    "stable_video_diffusion": {
        "name": "Stable Video Diffusion",
        "type": "local",
        "best_for": "8GB VRAM, short clips",
        "pros": ["Runs on 8GB", "ComfyUI native"],
        "cons": ["Short clips only", "Flickering"],
    },
    "animate_diff": {
        "name": "AnimateDiff (SDXL)",
        "type": "local",
        "best_for": "8GB VRAM, motion modules",
        "pros": ["Runs on 8GB", "Flexible prompts"],
        "cons": ["Short clips", "Temporal flicker"],
    },
    "kling": {
        "name": "Kling AI",
        "type": "cloud_free_tier",
        "best_for": "Best cloud quality, free daily credits",
        "pros": ["Excellent quality", "Free tier"],
        "cons": ["Cloud only", "Queue times"],
    },
    "luma": {
        "name": "Luma Dream Machine",
        "type": "cloud_free_tier",
        "best_for": "Fast 5s clips",
        "pros": ["Excellent quality", "Free tier"],
        "cons": ["5s only", "Cloud"],
    },
    "pika": {
        "name": "Pika Labs",
        "type": "cloud_free_tier",
        "best_for": "Quick 3s clips",
        "pros": ["Free tier", "Good motion"],
        "cons": ["Very short", "Watermark"],
    },
}


# Catalog of free / open music-generation options for feeding audio planning.
LOCAL_MUSIC_GENERATORS: dict[str, dict[str, Any]] = {
    "ace_step": {
        "name": "ACE-Step 1.5",
        "type": "local",
        "best_for": "Local Suno-style full-song generation",
        "pros": ["Open source", "Full-song output", "Runs local"],
        "cons": ["Needs a decent GPU", "Setup involved"],
    },
    "heartmula": {
        "name": "HeartMuLa",
        "type": "local",
        "best_for": "Open music foundation models",
        "pros": ["Open source", "Foundation-model quality"],
        "cons": ["Research-grade", "Weights large"],
    },
    "musicgen": {
        "name": "Meta MusicGen",
        "type": "local",
        "best_for": "Text-to-music + melody conditioning",
        "pros": ["Open source", "Melody conditioning"],
        "cons": ["Instrumental-leaning", "12GB+ VRAM for large"],
    },
    "suno": {
        "name": "Suno",
        "type": "cloud_free_tier",
        "best_for": "Best-in-class vocals + arrangement",
        "pros": ["Excellent quality", "Free tier"],
        "cons": ["Cloud only", "Usage caps"],
    },
    "udio": {
        "name": "Udio",
        "type": "cloud_free_tier",
        "best_for": "High-fidelity full tracks",
        "pros": ["Great quality", "Free tier"],
        "cons": ["Cloud only", "Usage caps"],
    },
}


@dataclass
class SongPlan:
    """Plan for a single music video."""

    song_name: str
    audio_path: str
    genre: str = ""
    mood: str = ""
    bpm: float | None = None
    duration: float = 0.0
    character_ref: str | None = None
    generation_mode: str = "full"  # full, clip_only, assembly_only
    scenes: list[dict[str, Any]] = field(default_factory=list)
    reusable_clips: list[str] = field(default_factory=list)
    character_refs: list[str] = field(default_factory=list)
    style_refs: list[str] = field(default_factory=list)
    # Appended after the original fields so positional SongPlan construction remains compatible.
    style_bible_path: str | None = None
    style_bible: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "song_name": self.song_name,
            "audio_path": self.audio_path,
            "genre": self.genre,
            "mood": self.mood,
            "bpm": self.bpm,
            "duration": self.duration,
            "character_ref": self.character_ref,
            "generation_mode": self.generation_mode,
            "style_bible_path": self.style_bible_path,
            "style_bible": self.style_bible,
            "scenes": self.scenes,
            "reusable_clips": self.reusable_clips,
            "character_refs": self.character_refs,
            "style_refs": self.style_refs,
        }


class MusicVideoResearchEngine:
    """Research and plan AI music videos."""

    def __init__(self, data_dir: Path, youtube_api_key: str | None = None) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.youtube_client = YouTubeDataClient(api_key=youtube_api_key)
        self.style_analysis: dict[str, Any] = {}
        self.reusable_assets: dict[str, list[str]] = {
            "video_clips": [],
            "images": [],
            "characters": [],
            "styles": [],
        }
        self.song_plans: list[SongPlan] = []

    def research_music_generators(self, vram_gb: int = 8) -> list[dict[str, Any]]:
        """Return music generators suitable for the given VRAM budget."""
        vram_thresholds = {
            "ace_step": 8,
            "heartmula": 8,
            "musicgen": 12,
        }
        suitable: list[dict[str, Any]] = []
        for key, gen in LOCAL_MUSIC_GENERATORS.items():
            if gen["type"] == "local":
                if vram_gb >= vram_thresholds.get(key, 8):
                    suitable.append({"id": key, **gen})
            else:
                suitable.append({"id": key, **gen})
        return suitable

    def research_generators(self, vram_gb: int = 8) -> list[dict[str, Any]]:
        """Return free video generators suitable for the given VRAM budget."""
        # Per-generator minimum VRAM recommendations.
        vram_thresholds = {
            "wan21": 16,
            "ltx2": 24,
            "stable_video_diffusion": 8,
            "animate_diff": 8,
        }
        suitable: list[dict[str, Any]] = []
        for key, gen in FREE_VIDEO_GENERATORS.items():
            if gen["type"] == "local":
                if vram_gb >= vram_thresholds.get(key, 8):
                    suitable.append({"id": key, **gen})
            else:
                suitable.append({"id": key, **gen})
        return suitable

    def fetch_youtube_trends(
        self,
        keywords: list[str] | None = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch trending music video metadata.

        Uses the YouTube Data API v3 when an API key is configured; otherwise
        falls back to best-effort jina.ai scraping.
        """
        if keywords is None:
            keywords = [
                "music video 2024 trends",
                "cinematic music video style",
                "dark aesthetic music video",
            ]
        return self.youtube_client.fetch_trends(keywords=keywords, max_results=max_results)

    def analyze_previous_videos(self, channel_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze previous music videos for style patterns."""
        style_analysis = {
            "common_visual_elements": list(dict.fromkeys(channel_data.get("common_elements", []))),
            "color_palettes": list(dict.fromkeys(channel_data.get("color_palette", []))),
            "camera_patterns": list(dict.fromkeys(channel_data.get("camera_style", []))),
            "videos": channel_data.get("videos", []),
        }
        self.style_analysis = style_analysis
        return style_analysis

    def scan_audio_library(self, audio_dir: Path) -> list[dict[str, Any]]:
        """Scan for audio files and return metadata."""
        audio_files: list[dict[str, Any]] = []
        for ext in (".mp3", ".wav", ".m4a", ".flac", ".ogg"):
            for f in audio_dir.rglob(f"*{ext}"):
                audio_files.append({
                    "name": f.stem,
                    "path": str(f),
                    "size_mb": round(f.stat().st_size / 1e6, 1),
                })
        return audio_files

    # Known character names recognised in asset filenames; used for continuity checks.
    KNOWN_CHARACTER_NAMES = ("chloe", "malik", "kaido", "sora", "zaya", "racer")

    # Filename hints used to classify flat staging directories (gdrive_upload_staging).
    CHARACTER_NAME_HINTS = (
        "chloe", "character", "design_sheet", "crew_card", "_card_", "_grid", "_grid_",
        "sprite", "turnaround", "_bible_", "_char_", "hero_", "avatar", "portrait_",
    )
    STYLE_NAME_HINTS = (
        "storyboard", "_reference", "_ref_", "style_bible", "style_sheet", "moodboard",
        "_styles_", "_style_", "workflow", "_sheet_", "_bible",
    )

    def scan_reusable_assets(self, root: Path) -> dict[str, list[str]]:
        """Scan directories for reusable clips, images, and character refs."""
        assets: dict[str, list[str]] = {
            "video_clips": [],
            "images": [],
            "characters": [],
            "styles": [],
        }

        stock_video = root / "input" / "stock_videos"
        stock_images = root / "input" / "stock_images"
        characters = root / "input" / "characters"
        references = root / "input" / "reference_videos"

        if stock_video.exists():
            for ext in (".mp4", ".mov", ".webm", ".avi"):
                assets["video_clips"].extend(str(p) for p in stock_video.rglob(f"*{ext}"))
        if stock_images.exists():
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                assets["images"].extend(str(p) for p in stock_images.rglob(f"*{ext}"))
        if characters.exists():
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                assets["characters"].extend(str(p) for p in characters.rglob(f"*{ext}"))
        if references.exists():
            for ext in (".mp4", ".mov", ".webm", ".avi"):
                assets["styles"].extend(str(p) for p in references.rglob(f"*{ext}"))

        for key in assets:
            assets[key] = list(dict.fromkeys(assets[key]))

        self.reusable_assets = assets
        return assets

    def scan_gdrive_staging(self, staging_root: Path) -> dict[str, list[str]]:
        """Classify a flat staging directory (e.g. gdrive_upload_staging/) into reusable assets.

        The gdrive staging folder is a flat pile of generated clips, character
        sheets, and storyboards. Unlike ``scan_reusable_assets`` (which expects
        the ``input/`` sub-folder layout), this scan walks one flat directory and
        buckets by extension + filename hints so plans can reuse what has
        already been generated or uploaded.
        """
        assets: dict[str, list[str]] = {
            "video_clips": [],
            "images": [],
            "characters": [],
            "styles": [],
        }
        if not staging_root.exists() or not staging_root.is_dir():
            return assets

        # The flat staging pile often contains sub-folder copies of the same
        # media (download(3)/, *_files/, review/). Dedupe by basename so a file
        # shipped in several places is listed once (first occurrence wins).
        seen_basenames: set[str] = set()
        for path in sorted(staging_root.rglob("*")):
            if not path.is_file():
                continue
            if path.name.lower() in seen_basenames:
                continue
            seen_basenames.add(path.name.lower())
            stem = path.stem.lower()
            ext = path.suffix.lower()
            if ext in (".mp4", ".mov", ".webm", ".avi"):
                assets["video_clips"].append(str(path))
                if any(hint in stem for hint in self.STYLE_NAME_HINTS):
                    assets["styles"].append(str(path))
            elif ext in (".png", ".jpg", ".jpeg", ".webp"):
                assets["images"].append(str(path))
                # Style hints win over character hints (e.g. storyboard grids
                # contain "grid" which is also a character hint).
                if any(hint in stem for hint in self.STYLE_NAME_HINTS):
                    assets["styles"].append(str(path))
                elif any(hint in stem for hint in self.CHARACTER_NAME_HINTS):
                    assets["characters"].append(str(path))

        for key in assets:
            assets[key] = list(dict.fromkeys(assets[key]))

        # Merge into the engine-level bucket (append-only; earlier scans win).
        for key in assets:
            merged = list(self.reusable_assets.get(key, []))
            for value in assets[key]:
                if value not in merged:
                    merged.append(value)
            self.reusable_assets[key] = merged
        return assets

    def create_song_plan(
        self,
        song_name: str,
        audio_path: str,
        genre: str = "",
        mood: str = "",
        duration: float = 180.0,
        character_ref: str | None = None,
        generation_mode: str = "full",
        style_bible_path: str | None = None,
    ) -> SongPlan:
        """Create a reusable-clip-aware plan for one song.

        When the audio file exists, its measured duration and BPM are preferred
        over the defaults so scenes align to the real track. Reusable clips are
        ranked by filename relevance to the song's genre/mood/name and the best
        fit is suggested per scene.
        """
        bpm: float | None = None
        if Path(audio_path).exists():
            try:
                analysis = analyze_audio(audio_path)
            except (OSError, ValueError, RuntimeError, FileNotFoundError):
                analysis = {}
            measured_duration = analysis.get("duration")
            measured_bpm = analysis.get("bpm")
            if isinstance(measured_duration, int | float) and measured_duration > 0:
                duration = float(measured_duration)
            if isinstance(measured_bpm, int | float) and measured_bpm > 0:
                bpm = float(measured_bpm)
        ranked_clips = self._rank_clips_for_song(self.reusable_assets["video_clips"], song_name, genre, mood)
        scenes: list[dict[str, Any]] = []
        scene_duration = duration / 8
        concepts = [
            "Opening atmosphere - establish mood and setting",
            "First verse - introduce visual narrative",
            "Pre-chorus - build tension visually",
            "Chorus 1 - main hook, highest energy",
            "Verse 2 - develop narrative",
            "Chorus 2 - variation, more intensity",
            "Bridge - contrast, shift perspective",
            "Final chorus + outro - climax and resolution",
        ]
        for i, concept in enumerate(concepts):
            start = i * scene_duration
            end = (i + 1) * scene_duration
            scenes.append({
                "scene_number": i + 1,
                "start_time": round(start, 2),
                "end_time": round(end, 2),
                "duration": round(scene_duration, 2),
                "concept": concept,
                "camera": self._camera_for_scene(i),
                "transition": self._transition_for_scene(i, len(concepts)),
                "suggested_clip": ranked_clips[i % len(ranked_clips)] if ranked_clips else "",
            })

        style_bible = self.load_style_bible(Path(style_bible_path)) if style_bible_path else {}
        character_data = style_bible.get("character", {})
        if not isinstance(character_data, Mapping):
            raise ValueError("Style bible character must be a JSON object")
        reference_path = character_data.get("reference_path")
        if reference_path is not None and not isinstance(reference_path, str):
            raise ValueError("Style bible character reference_path must be a string or null")
        plan = SongPlan(
            song_name=song_name,
            audio_path=audio_path,
            genre=genre,
            mood=mood,
            bpm=bpm,
            duration=duration,
            character_ref=character_ref or character_data.get("reference_path"),
            generation_mode=generation_mode,
            style_bible_path=style_bible_path,
            style_bible=style_bible,
            scenes=scenes,
            reusable_clips=ranked_clips[:10],
            character_refs=self.reusable_assets["characters"][:3],
            style_refs=self.reusable_assets["styles"][:5],
        )
        self.song_plans.append(plan)
        return plan

    @staticmethod
    def load_style_bible(path: Path) -> dict[str, Any]:
        """Load a JSON style bible; missing optional files fail clearly."""
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Style bible not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid style bible JSON: {path}") from exc
        if not isinstance(data, dict):
            raise ValueError("Style bible must be a JSON object")
        return data

    @staticmethod
    def create_style_bible_template(path: Path) -> Path:
        """Create a reusable character/style bible template without overwriting files."""
        if path.exists():
            raise FileExistsError(f"Style bible already exists: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        template = {
            "name": "My music-video universe",
            "character": {
                "name": "Main character",
                "reference_path": "assets/characters/main.png",
                "appearance": [],
                "wardrobe": [],
                "continuity_rules": [],
            },
            "visual_style": {
                "palette": [],
                "lighting": [],
                "camera_language": [],
                "locations": [],
                "texture": [],
            },
            "negative_rules": [],
        }
        path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")
        return path

    def create_master_plan(self) -> dict[str, Any]:
        """Aggregate all song plans into a master plan."""
        return {
            "created": datetime.now(UTC).isoformat(),
            "style_analysis": self.style_analysis,
            "reusable_assets": {k: len(v) for k, v in self.reusable_assets.items()},
            "generator_recommendations": self.research_generators(),
            "music_generator_recommendations": self.research_music_generators(),
            "continuity_warnings": self.check_character_continuity()["warnings"],
            "songs": [plan.to_dict() for plan in self.song_plans],
        }

    def save_master_plan(self, path: Path | None = None) -> Path:
        """Persist the master plan to disk."""
        if path is None:
            path = self.data_dir / "master_music_video_plan.json"
        path.write_text(json.dumps(self.create_master_plan(), indent=2), encoding="utf-8")
        return path

    def save_master_plan_with_name(self, name: str) -> Path:
        """Persist the master plan using a unique filename."""
        safe_name = Path(name).stem.replace(" ", "_")
        path = self.data_dir / f"{safe_name}_music_video_plan.json"
        path.write_text(json.dumps(self.create_master_plan(), indent=2), encoding="utf-8")
        return path

    @staticmethod
    def _clip_tokens(clip_path: str) -> set[str]:
        """Meaningful lowercase tokens from a clip filename (e.g. ``chloe-night-drive_001``)."""
        stem = Path(clip_path).stem.lower()
        tokens = re.split(r"[^a-z0-9]+", stem)
        return {token for token in tokens if len(token) >= 3}

    @classmethod
    def _rank_clips_for_song(
        cls,
        clips: list[str],
        song_name: str,
        genre: str,
        mood: str,
    ) -> list[str]:
        """Rank reusable clips by filename relevance to the song's genre/mood/name.

        The staging pool is shared across every track, so matching clip filename
        tokens (car, night, city, dance, ...) against the song's keywords picks a
        better first-pass set than arbitrary order. Exact token matches score 4;
        prefix/substring overlaps score 1. Ties keep their original scan order so
        plans are reproducible.
        """
        song_text = f"{song_name} {genre} {mood}"
        song_keywords = {
            token
            for token in re.split(r"[^a-z0-9]+", song_text.lower())
            if len(token) >= 3
        }
        if not song_keywords:
            return list(clips)
        scored: list[tuple[int, int, str]] = []
        for index, clip in enumerate(clips):
            tokens = cls._clip_tokens(clip)
            score = 0
            for token in tokens:
                if token in song_keywords:
                    score += 4
                elif any(token.startswith(keyword) or keyword.startswith(token) for keyword in song_keywords):
                    score += 1
            scored.append((score, index, clip))
        return [clip for _, _, clip in sorted(scored, key=lambda item: (-item[0], item[1]))]

    def _character_names_in(self, paths: list[str]) -> set[str]:
        """Character names referenced by asset paths (matched against known names)."""
        names: set[str] = set()
        for path in paths:
            stem = Path(path).stem.lower()
            for name in self.KNOWN_CHARACTER_NAMES:
                if name in stem:
                    names.add(name)
        return names

    def check_character_continuity(self, plan: SongPlan | None = None) -> dict[str, Any]:
        """Warn when a song mixes characters that no style bible approves.

        A single plan (or all song plans when ``plan`` is None) is checked:
        every distinct character referenced by the plan's character refs, the
        explicit ``character_ref``, and the style bible must either be the only
        character, or the exact set must appear in the bible's
        ``allowed_character_mixes``. Returns non-blocking warnings so plans are
        still produced and the operator can decide.
        """
        plans = [plan] if plan is not None else list(self.song_plans)
        warnings: list[str] = []
        for song in plans:
            characters = self._character_names_in(song.character_refs)
            if song.character_ref:
                characters |= self._character_names_in([song.character_ref])
            bible = song.style_bible if isinstance(song.style_bible, dict) else {}
            bible_character = bible.get("character")
            if isinstance(bible_character, dict):
                name = bible_character.get("name")
                if isinstance(name, str) and name:
                    characters.add(name.lower())
            allowed_pairs = {
                frozenset({str(part).lower() for part in pair if isinstance(part, str)})
                for pair in bible.get("allowed_character_mixes", [])
                if isinstance(pair, list) and len(pair) >= 2
            }
            if len(characters) > 1 and frozenset(characters) not in allowed_pairs:
                names = ", ".join(sorted(characters))
                warnings.append(
                    f"{song.song_name}: mixes characters ({names}) without an "
                    "allowed_character_mixes entry in the style bible"
                )
        return {"checked": len(plans), "warnings": warnings}

    def judge_clip_fit(
        self,
        song: SongPlan,
        scene_index: int,
        vision_model: str | None = None,
        api_key: str | None = None,
        openrouter_url: str = "https://openrouter.ai/api/v1",
    ) -> dict[str, Any]:
        """Score one scene's suggested clip fit, LLM-backed when possible.

        Clips are video files, so the judge scores the clip's filename/metadata
        against the scene concept (a text-to-text fit), optionally via an
        OpenRouter model. Without a key/model it never raises: it falls back to
        the same token-overlap heuristic ``_rank_clips_for_song`` uses and
        reports ``judge: "heuristic"``.
        """
        if scene_index < 0 or scene_index >= len(song.scenes):
            raise ValueError(f"scene_index {scene_index} out of range for {len(song.scenes)} scenes")
        scene = song.scenes[scene_index]
        clip = str(scene.get("suggested_clip", ""))
        concept = str(scene.get("concept", ""))

        song_keywords = {
            token
            for token in re.split(r"[^a-z0-9]+", f"{song.song_name} {song.genre} {song.mood}".lower())
            if len(token) >= 3
        }
        concept_keywords = {token for token in re.split(r"[^a-z0-9]+", concept.lower()) if len(token) >= 3}
        clip_tokens = self._clip_tokens(clip)
        matched = clip_tokens & (song_keywords | concept_keywords)
        heuristic_score = round(min(100.0, len(matched) * 20 + (12 if clip_tokens else 0)), 1)

        if api_key and vision_model:
            prompt = (
                "Score how well this reusable clip fits the scene of a music video. "
                f"Song: {song.song_name} ({song.genre}, {song.mood}).\n"
                f"Scene concept: {concept}\n"
                f"Clip filename: {Path(clip).name if clip else '(none)'}\n"
                "Reply with only a JSON object: {\"score\": 0-100 integer, \"reason\": short reason}"
            )
            try:
                response = requests.post(
                    f"{openrouter_url.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": vision_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 120,
                    },
                    timeout=30,
                    proxies={"http": None, "https": None},
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                parsed = _extract_json_object(content)
                llm_score = float(parsed.get("score", -1))
                if 0 <= llm_score <= 100:
                    return {
                        "scene": scene_index + 1,
                        "clip": clip,
                        "score": round(llm_score, 1),
                        "judge": "llm",
                        "model": vision_model,
                        "reasoning": str(parsed.get("reason", ""))[:500],
                    }
            except (requests.RequestException, KeyError, TypeError, ValueError, IndexError):
                pass  # Fall through to the heuristic rather than failing the plan.

        return {
            "scene": scene_index + 1,
            "clip": clip,
            "score": heuristic_score,
            "judge": "heuristic",
            "model": "token-overlap",
            "reasoning": (
                f"matched tokens: {', '.join(sorted(matched)) or 'none'}"
                if matched
                else "no token overlap with song keywords or scene concept"
            ),
        }

    @staticmethod
    def _camera_for_scene(index: int) -> str:
        cameras = [
            "Slow dolly in - establishing",
            "Static wide - observe",
            "Subtle handheld - tension",
            "Fast dolly + whip pan - energy",
            "Tracking shot - follow subject",
            "Crane up - reveal scale",
            "Static close-up - intimate",
            "Slow zoom out - resolution",
        ]
        return cameras[index % len(cameras)]

    @staticmethod
    def _transition_for_scene(index: int, total: int) -> str:
        if index == total - 1:
            return "Fade to black"
        transitions = [
            "Hard cut on beat",
            "Cross dissolve",
            "Whip pan transition",
            "Match cut",
            "Morph cut",
            "Glitch cut",
            "Fade through black",
        ]
        return transitions[index % len(transitions)]


def _extract_json_object(content: str) -> dict[str, Any]:
    """Pull the first JSON object out of a model reply, tolerating fences/prose."""
    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object in model reply")
    parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("model reply JSON is not an object")
    return parsed
