"""Tests for ai_influencer_studio.music_video_researcher."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_influencer_studio.music_video_researcher import MusicVideoResearchEngine, SongPlan
from ai_influencer_studio.youtube_client import YouTubeDataClient


@pytest.fixture
def engine(tmp_path: Path) -> MusicVideoResearchEngine:
    return MusicVideoResearchEngine(data_dir=tmp_path)


def test_research_generators_returns_suitable_options(engine: MusicVideoResearchEngine) -> None:
    results = engine.research_generators(vram_gb=16)
    assert len(results) >= 4
    ids = {r["id"] for r in results}
    assert "wan21" in ids
    assert "kling" in ids


def test_research_generators_filters_by_vram(engine: MusicVideoResearchEngine) -> None:
    results = engine.research_generators(vram_gb=4)
    local_ids = {r["id"] for r in results if r["type"] == "local"}
    # High-VRAM local options should be excluded for 4GB.
    assert "wan21" not in local_ids
    assert "ltx2" not in local_ids
    # Cloud options are always included.
    cloud_ids = {r["id"] for r in results if r["type"] == "cloud_free_tier"}
    assert "kling" in cloud_ids


def test_research_music_generators_includes_cloud_and_local(engine: MusicVideoResearchEngine) -> None:
    results = engine.research_music_generators(vram_gb=16)
    ids = {r["id"] for r in results}
    assert "ace_step" in ids
    assert "musicgen" in ids
    assert "suno" in ids


def test_research_music_generators_filters_high_vram_local(engine: MusicVideoResearchEngine) -> None:
    results = engine.research_music_generators(vram_gb=4)
    local_ids = {r["id"] for r in results if r["type"] == "local"}
    assert local_ids == set()
    cloud_ids = {r["id"] for r in results if r["type"] == "cloud_free_tier"}
    assert "suno" in cloud_ids
    assert "udio" in cloud_ids


def test_analyze_previous_videos_extracts_style(engine: MusicVideoResearchEngine) -> None:
    channel_data = {
        "common_elements": ["neon", "rain", "cyberpunk"],
        "color_palette": ["teal", "magenta"],
        "camera_style": ["handheld", "dolly"],
        "videos": [{"title": "Test"}],
    }
    analysis = engine.analyze_previous_videos(channel_data)
    assert analysis["common_visual_elements"] == ["neon", "rain", "cyberpunk"]
    assert analysis["color_palettes"] == ["teal", "magenta"]
    assert analysis["camera_patterns"] == ["handheld", "dolly"]


def test_scan_audio_library_finds_audio_files(tmp_path: Path, engine: MusicVideoResearchEngine) -> None:
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    (audio_dir / "song1.mp3").write_bytes(b"x" * 1_000_000)
    (audio_dir / "song2.wav").write_bytes(b"y" * 2_000_000)

    results = engine.scan_audio_library(audio_dir)
    names = {r["name"] for r in results}
    assert names == {"song1", "song2"}
    assert all("path" in r and "size_mb" in r for r in results)


def test_scan_reusable_assets_collects_clips_and_characters(tmp_path: Path, engine: MusicVideoResearchEngine) -> None:
    (tmp_path / "input" / "stock_videos").mkdir(parents=True)
    (tmp_path / "input" / "characters").mkdir(parents=True)
    (tmp_path / "input" / "stock_videos" / "clip.mp4").write_text("video")
    (tmp_path / "input" / "characters" / "hero.png").write_text("image")

    assets = engine.scan_reusable_assets(tmp_path)
    assert any("clip.mp4" in p for p in assets["video_clips"])
    assert any("hero.png" in p for p in assets["characters"])


def test_scan_gdrive_staging_classifies_flat_dir(tmp_path: Path, engine: MusicVideoResearchEngine) -> None:
    (tmp_path / "clip_001.mp4").write_text("video")
    (tmp_path / "chloe-hero.jpg").write_text("image")
    (tmp_path / "Storyboard_2x2_grid.png").write_text("image")
    (tmp_path / "landscape.png").write_text("image")
    (tmp_path / "notes.txt").write_text("ignore")

    assets = engine.scan_gdrive_staging(tmp_path)
    assert any("clip_001.mp4" in p for p in assets["video_clips"])
    assert any("chloe-hero.jpg" in p for p in assets["characters"])
    assert any("Storyboard_2x2_grid.png" in p for p in assets["styles"])
    assert any("landscape.png" in p for p in assets["images"])
    assert not any("notes.txt" in p for p in assets["video_clips"] + assets["images"])
    # Merged into engine-level buckets.
    assert any("clip_001.mp4" in p for p in engine.reusable_assets["video_clips"])
    assert any("chloe-hero.jpg" in p for p in engine.reusable_assets["characters"])


def test_scan_gdrive_staging_dedupes_subfolder_copies(tmp_path: Path, engine: MusicVideoResearchEngine) -> None:
    (tmp_path / "clip_001.mp4").write_text("video")
    # Same basename copied into a sub-folder must be listed once.
    sub = tmp_path / "download(3)"
    sub.mkdir()
    (sub / "clip_001.mp4").write_text("video")

    assets = engine.scan_gdrive_staging(tmp_path)
    clips = [Path(p).name for p in assets["video_clips"]]
    assert clips.count("clip_001.mp4") == 1


def test_scan_gdrive_staging_missing_dir_returns_empty(engine: MusicVideoResearchEngine) -> None:
    assets = engine.scan_gdrive_staging(Path("/definitely/not/here"))
    assert all(assets[key] == [] for key in assets)


def test_scan_gdrive_staging_merges_with_existing_assets(tmp_path: Path, engine: MusicVideoResearchEngine) -> None:
    (tmp_path / "input" / "stock_videos").mkdir(parents=True)
    (tmp_path / "input" / "stock_videos" / "base.mp4").write_text("video")
    engine.scan_reusable_assets(tmp_path)

    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "wan_clip.mp4").write_text("video")
    engine.scan_gdrive_staging(staging)

    clips = engine.reusable_assets["video_clips"]
    assert any("base.mp4" in p for p in clips)
    assert any("wan_clip.mp4" in p for p in clips)


@patch("ai_influencer_studio.music_video_researcher.analyze_audio")
def test_create_song_plan_uses_measured_bpm_and_duration(
    mock_analyze: MagicMock, tmp_path: Path, engine: MusicVideoResearchEngine
) -> None:
    audio = tmp_path / "track.mp3"
    audio.write_bytes(b"audio")
    mock_analyze.return_value = {"duration": 210.5, "bpm": 128.0, "source": "librosa"}

    plan = engine.create_song_plan(
        song_name="Measured",
        audio_path=str(audio),
        genre="pop",
        mood="bright",
    )
    assert plan.duration == pytest.approx(210.5)
    assert plan.bpm == pytest.approx(128.0)
    assert len(plan.scenes) == 8
    assert plan.scenes[-1]["end_time"] == pytest.approx(210.5, abs=0.1)
    mock_analyze.assert_called_once_with(str(audio))


@patch("ai_influencer_studio.music_video_researcher.analyze_audio")
def test_create_song_plan_keeps_defaults_when_audio_missing(
    mock_analyze: MagicMock, engine: MusicVideoResearchEngine
) -> None:
    plan = engine.create_song_plan(
        song_name="NoAudio",
        audio_path="/tmp/does-not-exist.mp3",
        duration=120.0,
    )
    assert plan.duration == 120.0
    assert plan.bpm is None
    mock_analyze.assert_not_called()


@patch("ai_influencer_studio.music_video_researcher.analyze_audio")
def test_create_song_plan_falls_back_when_analysis_fails(
    mock_analyze: MagicMock, tmp_path: Path, engine: MusicVideoResearchEngine
) -> None:
    audio = tmp_path / "track.mp3"
    audio.write_bytes(b"audio")
    mock_analyze.side_effect = RuntimeError("decode failed")

    plan = engine.create_song_plan(
        song_name="BrokenAudio",
        audio_path=str(audio),
        duration=150.0,
    )
    assert plan.duration == 150.0
    assert plan.bpm is None


def test_rank_clips_prioritizes_matching_filenames(engine: MusicVideoResearchEngine) -> None:
    clips = [
        "/pool/dance_club_001.mp4",
        "/pool/chloe-night-drive.mp4",
        "/pool/wan_city_rain.mp4",
    ]
    ranked = engine._rank_clips_for_song(clips, "Midnight City", "synthwave", "night")
    assert ranked[0] == "/pool/chloe-night-drive.mp4"
    assert ranked[1] == "/pool/wan_city_rain.mp4"
    assert ranked[2] == "/pool/dance_club_001.mp4"


def test_create_song_plan_ranks_clips_and_assigns_scene_clips(tmp_path: Path, engine: MusicVideoResearchEngine) -> None:
    (tmp_path / "dance_club_001.mp4").write_text("video")
    (tmp_path / "night-drive.mp4").write_text("video")
    (tmp_path / "city_rain.mp4").write_text("video")
    engine.scan_gdrive_staging(tmp_path)

    plan = engine.create_song_plan("Night Dance", "/tmp/song.mp3", genre="pop", mood="club")
    assert plan.reusable_clips[0].endswith("dance_club_001.mp4")
    # Every scene suggests its best-fit reusable clip (cycled through the pool).
    assert plan.scenes[0]["suggested_clip"].endswith("dance_club_001.mp4")
    assert plan.scenes[-1]["suggested_clip"]


def test_character_continuity_warns_on_unapproved_mix(engine: MusicVideoResearchEngine) -> None:
    plan = engine.create_song_plan("Mix", "/tmp/a.mp3")
    plan.character_refs = ["/pool/chloe-hero.jpg", "/pool/malik-design.jpg"]
    result = engine.check_character_continuity(plan)
    assert len(result["warnings"]) == 1
    assert "chloe" in result["warnings"][0]
    assert "malik" in result["warnings"][0]


def test_character_continuity_ok_for_single_character(engine: MusicVideoResearchEngine) -> None:
    plan = engine.create_song_plan("Solo", "/tmp/a.mp3")
    plan.character_refs = ["/pool/chloe-hero.jpg"]
    result = engine.check_character_continuity(plan)
    assert result["warnings"] == []


def test_character_continuity_ok_with_bible_allowed_mix(engine: MusicVideoResearchEngine) -> None:
    plan = engine.create_song_plan("Duet", "/tmp/a.mp3")
    plan.character_refs = ["/pool/chloe-hero.jpg", "/pool/malik-design.jpg"]
    plan.style_bible = {"allowed_character_mixes": [["chloe", "malik"]]}
    result = engine.check_character_continuity(plan)
    assert result["warnings"] == []


def test_master_plan_includes_continuity_warnings(engine: MusicVideoResearchEngine) -> None:
    engine.create_song_plan("Mix", "/tmp/a.mp3")
    engine.song_plans[0].character_refs = ["/pool/chloe-hero.jpg", "/pool/kaido-sheet.png"]
    master = engine.create_master_plan()
    assert "continuity_warnings" in master
    assert len(master["continuity_warnings"]) == 1


def test_create_song_plan_builds_scenes(engine: MusicVideoResearchEngine) -> None:
    plan = engine.create_song_plan(
        song_name="Test Song",
        audio_path="/tmp/test.mp3",
        genre="pop",
        mood="upbeat",
        duration=160.0,
    )
    assert plan.song_name == "Test Song"
    assert len(plan.scenes) == 8
    assert plan.scenes[0]["start_time"] == 0
    assert plan.scenes[-1]["end_time"] == pytest.approx(160.0, abs=0.1)


def test_song_plan_new_fields_are_appended_for_positional_compatibility() -> None:
    from ai_influencer_studio.music_video_researcher import SongPlan

    plan = SongPlan("Song", "song.mp3", "pop", "bright", None, 120.0, None, "full", [], [], [], [])
    assert plan.scenes == []
    assert plan.style_bible_path is None
    assert plan.style_bible == {}


def test_style_bible_rejects_non_object_character(tmp_path: Path, engine: MusicVideoResearchEngine) -> None:
    bible_path = tmp_path / "invalid-character.json"
    bible_path.write_text(json.dumps({"character": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="character must be a JSON object"):
        engine.create_song_plan("Invalid", "/tmp/song.mp3", style_bible_path=str(bible_path))


def test_style_bible_rejects_non_string_reference_path(tmp_path: Path, engine: MusicVideoResearchEngine) -> None:
    bible_path = tmp_path / "invalid-reference.json"
    bible_path.write_text(json.dumps({"character": {"reference_path": 123}}), encoding="utf-8")
    with pytest.raises(ValueError, match="reference_path must be a string or null"):
        engine.create_song_plan("Invalid", "/tmp/song.mp3", style_bible_path=str(bible_path))


def test_style_bible_template_and_plan_loading(tmp_path: Path, engine: MusicVideoResearchEngine) -> None:
    bible_path = tmp_path / "style-bible.json"
    engine.create_style_bible_template(bible_path)
    data = json.loads(bible_path.read_text(encoding="utf-8"))
    data["character"]["reference_path"] = "/tmp/hero.png"
    bible_path.write_text(json.dumps(data), encoding="utf-8")
    plan = engine.create_song_plan("Styled", "/tmp/song.mp3", style_bible_path=str(bible_path))
    assert plan.style_bible_path == str(bible_path)
    assert plan.character_ref == "/tmp/hero.png"
    assert plan.style_bible["name"] == "My music-video universe"


def test_create_song_plan_with_character_ref_and_generation_mode(engine: MusicVideoResearchEngine) -> None:
    plan = engine.create_song_plan(
        song_name="Test Song",
        audio_path="/tmp/test.mp3",
        genre="pop",
        mood="upbeat",
        duration=160.0,
        character_ref="/tmp/hero.png",
        generation_mode="clip_only",
    )
    assert plan.character_ref == "/tmp/hero.png"
    assert plan.generation_mode == "clip_only"
    assert plan.to_dict()["character_ref"] == "/tmp/hero.png"
    assert plan.to_dict()["generation_mode"] == "clip_only"


def test_save_master_plan_persists_json(tmp_path: Path, engine: MusicVideoResearchEngine) -> None:
    engine.create_song_plan("Song A", "/tmp/a.mp3")
    engine.create_song_plan("Song B", "/tmp/b.mp3")
    path = engine.save_master_plan(tmp_path / "plan.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["songs"][0]["song_name"] == "Song A"
    assert data["songs"][1]["song_name"] == "Song B"
    assert "generator_recommendations" in data
    assert "music_generator_recommendations" in data
    assert any(g["id"] == "suno" for g in data["music_generator_recommendations"])


@patch("ai_influencer_studio.youtube_client.requests.get")
def test_fetch_youtube_trends_parses_video_ids(mock_get: MagicMock, engine: MusicVideoResearchEngine) -> None:
    mock_get.return_value.text = (
        'watch?v=abc123def45 "title":"Trending Music Video"'
        'watch?v=abc123def45 "title":"Trending Music Video"'
    )
    mock_get.return_value.raise_for_status = lambda: None
    trends = engine.fetch_youtube_trends(keywords=["test"], max_results=5)
    assert len(trends) == 1
    assert trends[0]["video_id"] == "abc123def45"
    assert "youtube.com" in trends[0]["url"]


def test_cli_music_video_research_generators(tmp_path: Path) -> None:
    from ai_influencer_studio.cli import main
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.cli.MusicVideoResearchEngine"
    ) as mock_engine:
        mock_config.from_file.return_value.data_dir = tmp_path
        mock_engine.return_value.research_generators.return_value = [
            {"id": "wan21", "name": "Wan 2.1"}
        ]
        main(["music-video", "research", "--generators", "--vram", "16"])
        mock_engine.assert_called_once()
        mock_engine.return_value.research_generators.assert_called_once_with(vram_gb=16)


@patch("ai_influencer_studio.cli.MusicVideoResearchEngine")
@patch("ai_influencer_studio.cli.StudioConfig")
def test_cli_music_video_research_trends(
    mock_config: MagicMock, mock_engine: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    from ai_influencer_studio.cli import main
    mock_config.from_file.return_value.data_dir = tmp_path
    mock_engine.return_value.fetch_youtube_trends.return_value = [
        {"video_id": "abc123", "title": "Trend"}
    ]
    main(["music-video", "research", "--trends", "--max-results", "3"])
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["trends"][0]["video_id"] == "abc123"
    mock_engine.return_value.fetch_youtube_trends.assert_called_once_with(max_results=3)


def test_cli_music_video_plan(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main
    song_json = json.dumps({"name": "Song A", "audio": "/tmp/a.mp3", "genre": "pop", "duration": 120.0})
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config:
        mock_config.from_file.return_value.data_dir = tmp_path
        main(["music-video", "plan", "--song", song_json])
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["plans"][0]["song_name"] == "Song A"
    assert len(output["plans"][0]["scenes"]) == 8


def test_cli_music_video_master_plan(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main
    song_json = json.dumps({"name": "Song B", "audio": "/tmp/b.mp3", "mood": "dark"})
    output_path = tmp_path / "master.json"
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config:
        mock_config.from_file.return_value.data_dir = tmp_path
        main(["music-video", "master-plan", "--song", song_json, "--output", str(output_path)])
    captured = capsys.readouterr()
    assert "Master plan saved to:" in captured.out
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["songs"][0]["song_name"] == "Song B"
    assert data["songs"][0]["mood"] == "dark"


def test_cli_music_video_plan_rejects_invalid_json(tmp_path: Path) -> None:
    from ai_influencer_studio.cli import main
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, pytest.raises(SystemExit):
        mock_config.from_file.return_value.data_dir = tmp_path
        main(["music-video", "plan", "--song", "not-json"])


def test_cli_music_video_plan_rejects_missing_keys(tmp_path: Path) -> None:
    from ai_influencer_studio.cli import main
    bad_json = json.dumps({"name": "Song A"})
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, pytest.raises(SystemExit):
        mock_config.from_file.return_value.data_dir = tmp_path
        main(["music-video", "plan", "--song", bad_json])


def test_cli_music_video_research_requires_flag(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config:
        mock_config.from_file.return_value.data_dir = tmp_path
        result = main(["music-video", "research"])
    assert result == 1
    captured = capsys.readouterr()
    assert "Use --generators and/or --trends" in captured.err


def test_cli_music_video_plan_scans_assets(tmp_path: Path) -> None:
    from ai_influencer_studio.cli import main
    from ai_influencer_studio.music_video_researcher import SongPlan

    song_json = json.dumps({"name": "Song A", "audio": "/tmp/a.mp3"})
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.cli.MusicVideoResearchEngine"
    ) as mock_engine:
        mock_config.from_file.return_value.data_dir = tmp_path
        mock_engine.return_value.create_song_plan.return_value = SongPlan(
            song_name="Song A", audio_path="/tmp/a.mp3"
        )
        main(["music-video", "plan", "--song", song_json, "--assets-root", str(tmp_path)])
        mock_engine.return_value.scan_reusable_assets.assert_called_once_with(tmp_path)


def test_cli_music_video_plan_scans_gdrive_staging(tmp_path: Path) -> None:
    from ai_influencer_studio.cli import main
    from ai_influencer_studio.music_video_researcher import SongPlan

    song_json = json.dumps({"name": "Song A", "audio": "/tmp/a.mp3"})
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.cli.MusicVideoResearchEngine"
    ) as mock_engine:
        mock_config.from_file.return_value.data_dir = tmp_path
        mock_engine.return_value.create_song_plan.return_value = SongPlan(
            song_name="Song A", audio_path="/tmp/a.mp3"
        )
        main(["music-video", "plan", "--song", song_json, "--staging-root", str(tmp_path)])
        mock_engine.return_value.scan_gdrive_staging.assert_called_once_with(tmp_path)


def test_cli_music_video_plan_scans_both_asset_roots(tmp_path: Path) -> None:
    from ai_influencer_studio.cli import main
    from ai_influencer_studio.music_video_researcher import SongPlan

    song_json = json.dumps({"name": "Song A", "audio": "/tmp/a.mp3"})
    assets_root = tmp_path / "assets"
    staging_root = tmp_path / "staging"
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.cli.MusicVideoResearchEngine"
    ) as mock_engine:
        mock_config.from_file.return_value.data_dir = tmp_path
        mock_engine.return_value.create_song_plan.return_value = SongPlan(
            song_name="Song A", audio_path="/tmp/a.mp3"
        )
        main([
            "music-video", "plan", "--song", song_json,
            "--assets-root", str(assets_root),
            "--staging-root", str(staging_root),
        ])
        mock_engine.return_value.scan_reusable_assets.assert_called_once_with(assets_root)
        mock_engine.return_value.scan_gdrive_staging.assert_called_once_with(staging_root)


def test_cli_music_video_plan_passes_character_ref_and_generation_mode(tmp_path: Path) -> None:
    from ai_influencer_studio.cli import main
    from ai_influencer_studio.music_video_researcher import SongPlan

    song_json = json.dumps({"name": "Song A", "audio": "/tmp/a.mp3"})
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.cli.MusicVideoResearchEngine"
    ) as mock_engine:
        mock_config.from_file.return_value.data_dir = tmp_path
        mock_engine.return_value.create_song_plan.return_value = SongPlan(
            song_name="Song A", audio_path="/tmp/a.mp3"
        )
        main([
            "music-video", "plan", "--song", song_json,
            "--character-ref", "/tmp/hero.png",
            "--generation-mode", "clip_only",
        ])
        mock_engine.return_value.create_song_plan.assert_called_once_with(
            song_name="Song A",
            audio_path="/tmp/a.mp3",
            genre="",
            mood="",
            duration=180.0,
            character_ref="/tmp/hero.png",
            generation_mode="clip_only",
        )


@patch("ai_influencer_studio.youtube_client.requests.get")
def test_youtube_client_channel_stats(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {
        "items": [
            {
                "id": "UC123",
                "snippet": {"title": "Test Channel"},
                "statistics": {"subscriberCount": "42", "viewCount": "100", "videoCount": "7"},
            }
        ]
    }
    mock_get.return_value.raise_for_status = lambda: None
    client = YouTubeDataClient(api_key="fake-key")
    stats = client.fetch_channel_stats("UC123")
    assert stats["title"] == "Test Channel"
    assert stats["subscribers"] == "42"
    assert stats["videos"] == "7"


@patch("ai_influencer_studio.youtube_client.requests.get")
def test_youtube_client_top_videos(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {
        "items": [
            {"id": {"videoId": "abc123"}, "snippet": {"title": "Most Viewed"}},
            {"id": {"videoId": "def456"}, "snippet": {"title": "Second"}},
        ]
    }
    mock_get.return_value.raise_for_status = lambda: None
    client = YouTubeDataClient(api_key="fake-key")
    videos = client.fetch_top_videos("UC123", max_results=2)
    assert len(videos) == 2
    assert videos[0]["video_id"] == "abc123"
    assert videos[0]["title"] == "Most Viewed"


def test_youtube_client_channel_stats_without_key() -> None:
    client = YouTubeDataClient(api_key="")
    assert client.fetch_channel_stats("UC123") == {}
    assert client.fetch_top_videos("UC123") == []


@patch("ai_influencer_studio.youtube_client.requests.get")
def test_youtube_client_channel_stats_unknown_channel(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {"items": []}
    mock_get.return_value.raise_for_status = lambda: None
    client = YouTubeDataClient(api_key="fake-key")
    assert client.fetch_channel_stats("UCnope") == {}


@patch("ai_influencer_studio.youtube_client.requests.get")
def test_cli_youtube_analytics(mock_get: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    def _side_effect(url, **kwargs):
        mock = MagicMock()
        mock.raise_for_status = lambda: None
        if "channels" in url:
            mock.json.return_value = {
                "items": [{"id": "UC1", "snippet": {"title": "Ch"}, "statistics": {"viewCount": "9"}}]
            }
        else:
            mock.json.return_value = {"items": [{"id": {"videoId": "v1"}, "snippet": {"title": "Top"}}]}
        return mock

    mock_get.side_effect = _side_effect
    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config:
        mock_config.from_file.return_value.data_dir = tmp_path
        mock_config.from_file.return_value.youtube_api_key = "fake-key"
        main(["youtube", "analytics", "--channel-id", "UC1"])
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["channel"]["title"] == "Ch"
    assert output["top_videos"][0]["video_id"] == "v1"


@patch("ai_influencer_studio.youtube_client.requests.get")
def test_youtube_client_api_path(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {
        "items": [
            {"id": {"videoId": "abc123"}, "snippet": {"title": "Test Video"}}
        ]
    }
    mock_get.return_value.raise_for_status = lambda: None
    client = YouTubeDataClient(api_key="fake-key")
    trends = client.fetch_trends(keywords=["test"], max_results=1)
    assert len(trends) == 1
    assert trends[0]["video_id"] == "abc123"
    assert trends[0]["title"] == "Test Video"


@patch("ai_influencer_studio.youtube_client.requests.get")
def test_youtube_client_scrape_fallback(mock_get: MagicMock) -> None:
    mock_get.return_value.text = 'watch?v=abc123def45 "title":"Fallback Video"'
    mock_get.return_value.raise_for_status = lambda: None
    client = YouTubeDataClient(api_key="")
    trends = client.fetch_trends(keywords=["test"], max_results=1)
    assert len(trends) == 1
    assert trends[0]["video_id"] == "abc123def45"


def test_engine_uses_youtube_api_key(tmp_path: Path) -> None:
    engine = MusicVideoResearchEngine(data_dir=tmp_path, youtube_api_key="secret")
    assert engine.youtube_client.api_key == "secret"


def test_cli_music_video_execute(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({"songs": [{"audio_path": str(tmp_path / "a.mp3")}]}), encoding="utf-8")
    (tmp_path / "a.mp3").write_text("audio")

    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.cli.VideoAdapter"
    ) as mock_adapter:
        mock_config.from_file.return_value.data_dir = tmp_path
        mock_adapter.return_value.execute_music_video_plan.return_value = {"returncode": 0}
        main(["music-video", "execute", "--plan", str(plan_path), "--song-index", "0"])
        mock_adapter.return_value.execute_music_video_plan.assert_called_once()


def test_cli_repurpose_single(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    input_path = tmp_path / "video.mp4"
    input_path.write_text("video")
    output_dir = tmp_path / "media" / "repurposed"

    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.cli.VideoRepurposer"
    ) as mock_repurposer_cls:
        mock_config.from_file.return_value.media_dir = tmp_path / "media"
        mock_repurposer = MagicMock()
        mock_repurposer.create_vertical_cut.return_value = {
            "input": str(input_path),
            "output": str(output_dir / "video_tiktok.mp4"),
            "platform": "tiktok",
        }
        mock_repurposer_cls.return_value = mock_repurposer

        main(["repurpose", "--input", str(input_path), "--platform", "tiktok", "--caption", "Hello"])

        mock_repurposer.create_vertical_cut.assert_called_once_with(
            str(input_path),
            output_dir / "video_tiktok.mp4",
            platform="tiktok",
            start=0.0,
            caption="Hello",
        )
        captured = capsys.readouterr()
        assert "tiktok" in captured.out


def test_cli_repurpose_multi(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from ai_influencer_studio.cli import main

    input_path = tmp_path / "video.mp4"
    input_path.write_text("video")
    output_dir = tmp_path / "media" / "repurposed"

    with patch("ai_influencer_studio.cli.StudioConfig") as mock_config, patch(
        "ai_influencer_studio.cli.VideoRepurposer"
    ) as mock_repurposer_cls:
        mock_config.from_file.return_value.media_dir = tmp_path / "media"
        mock_repurposer = MagicMock()
        mock_repurposer.create_multi_clips.return_value = [
            {"platform": "tiktok", "output": "clip1.mp4"},
            {"platform": "instagram", "output": "clip2.mp4"},
        ]
        mock_repurposer_cls.return_value = mock_repurposer

        main([
            "repurpose",
            "--input", str(input_path),
            "--multi",
            "--platforms", "tiktok,instagram",
            "--clip-duration", "15",
        ])

        mock_repurposer.create_multi_clips.assert_called_once_with(
            str(input_path),
            output_dir,
            platforms=["tiktok", "instagram"],
            clip_duration=15.0,
        )
        captured = capsys.readouterr()
        assert "clips" in captured.out


def _judge_plan() -> SongPlan:
    return SongPlan(
        song_name="Neon Nights",
        audio_path="song.mp3",
        genre="synthwave",
        mood="dreamy",
        scenes=[
            {
                "start_time": 0.0,
                "end_time": 15.0,
                "concept": "neon city street at night",
                "suggested_clip": "neon_city_street.mp4",
            },
            {
                "start_time": 15.0,
                "end_time": 30.0,
                "concept": "character walking through rain",
                "suggested_clip": "chloe_rain_walk.mp4",
            },
        ],
    )


def test_judge_clip_fit_heuristic_without_key(engine: MusicVideoResearchEngine) -> None:
    result = engine.judge_clip_fit(_judge_plan(), scene_index=0)
    assert result["scene"] == 1
    assert result["clip"] == "neon_city_street.mp4"
    assert result["judge"] == "heuristic"
    assert result["model"] == "token-overlap"
    assert 0 <= result["score"] <= 100


def test_judge_clip_fit_out_of_range(engine: MusicVideoResearchEngine) -> None:
    with pytest.raises(ValueError, match="out of range"):
        engine.judge_clip_fit(_judge_plan(), scene_index=5)


@patch("ai_influencer_studio.music_video_researcher.requests.post")
def test_judge_clip_fit_llm_parses_score(
    mock_post: MagicMock, engine: MusicVideoResearchEngine
) -> None:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "choices": [{"message": {"content": '{"score": 87, "reason": "city matches"}'}}]
    }
    mock_post.return_value = response

    result = engine.judge_clip_fit(
        _judge_plan(),
        scene_index=1,
        vision_model="openrouter/qwen-vl",
        api_key="sk-test",
    )
    assert result["judge"] == "llm"
    assert result["model"] == "openrouter/qwen-vl"
    assert result["score"] == pytest.approx(87.0)
    assert result["reasoning"] == "city matches"
    sent = mock_post.call_args.kwargs["json"]
    assert sent["model"] == "openrouter/qwen-vl"
    assert mock_post.call_args.kwargs["headers"] == {"Authorization": "Bearer sk-test"}


@patch("ai_influencer_studio.music_video_researcher.requests.post")
def test_judge_clip_fit_falls_back_on_malformed_llm(
    mock_post: MagicMock, engine: MusicVideoResearchEngine
) -> None:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "choices": [{"message": {"content": "not json at all"}}]
    }
    mock_post.return_value = response

    result = engine.judge_clip_fit(
        _judge_plan(),
        scene_index=0,
        vision_model="openrouter/qwen-vl",
        api_key="sk-test",
    )
    assert result["judge"] == "heuristic"
    assert result["model"] == "token-overlap"
