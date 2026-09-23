# Music Video Researcher — AI Influencer Studio

> **Module:** `ai_influencer_studio.music_video_researcher`  
> **CLI:** `aisocial music-video ...`  
> **Web Dashboard:** `http://localhost:8000/music-video`  
> **Status:** Implemented and tested  
> **Date:** 2026-07-17

---

## What it does

The Music Video Researcher helps operators research free video-generation options, analyze YouTube music-video trends, scan local audio libraries and reusable assets, and create reusable-clip-aware plans for every song.

### Capabilities

| Capability | Description |
|---|---|
| **Generator research** | Catalog of free/fremium local + cloud video generators with per-model VRAM thresholds |
| **YouTube trend analysis** | Best-effort trend fetching via jina.ai (no API key) |
| **Audio library scan** | Discover `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg` files |
| **Asset reuse scan** | Collect stock videos, images, character refs, and reference videos |
| **Style analysis** | Extract common visual elements, color palettes, and camera patterns from previous videos |
| **Song planning** | Generate 8-scene plans with camera moves, transitions, and reusable-clip suggestions |
| **Master plan** | Aggregate all song plans into a single JSON master plan |

---

## CLI usage

### Research free video generators

```bash
aisocial music-video research --generators --vram 16
```

### Research YouTube trends

```bash
aisocial music-video research --trends --max-results 10
```

### Create a character/style bible template

```bash
aisocial music-video style-bible-template --output assets/style-bible.json
```

Attach it to a plan:

```bash
aisocial music-video plan \
  --style-bible assets/style-bible.json \
  --song '{"name":"My Song","audio":"tracks/my_song.mp3"}'
```

The bible is optional and is persisted in the plan for reproducibility. It never executes a render by itself. Style-bible fields are appended to the SongPlan data model so existing positional constructors remain compatible.

### Create a song plan

```bash
aisocial music-video plan \
  --song '{"name":"My Song","audio":"tracks/my_song.mp3","genre":"pop","mood":"upbeat","duration":180.0}' \
  --character-ref assets/hero.png \
  --generation-mode full
```

### Create and save a master plan

```bash
aisocial music-video master-plan \
  --song '{"name":"My Song","audio":"tracks/my_song.mp3"}' \
  --output plans/master.json
```

### Execute a saved plan

```bash
aisocial music-video execute --plan plans/master.json --song-index 0 --generation-mode clip_only
```

### Repurpose a finished video

```bash
# Single vertical clip
aisocial repurpose --input video.mp4 --platform tiktok --caption "Hello world"

# Batch clips for multiple platforms
aisocial repurpose --input video.mp4 --multi --platforms tiktok,instagram,youtube --clip-duration 15
```

---

## Python API

```python
from pathlib import Path
from ai_influencer_studio.music_video_researcher import MusicVideoResearchEngine

engine = MusicVideoResearchEngine(data_dir=Path("./data"))

# Research generators for your VRAM budget
generators = engine.research_generators(vram_gb=16)

# Scan reusable assets
engine.scan_reusable_assets(Path("./ComfyUI"))

# Create a plan for one song
plan = engine.create_song_plan(
    song_name="My Song",
    audio_path="tracks/my_song.mp3",
    genre="pop",
    mood="upbeat",
    duration=180.0,
)

# Save master plan
engine.save_master_plan(Path("plans/master.json"))
```

---

## Data model

### `SongPlan`

| Field | Type | Description |
|---|---|---|
| `song_name` | `str` | Song title |
| `audio_path` | `str` | Path to audio file |
| `genre` | `str` | Music genre |
| `mood` | `str` | Visual mood |
| `bpm` | `float \| None` | Beats per minute (reserved) |
| `duration` | `float` | Song duration in seconds |
| `character_ref` | `str \| None` | Locked character reference image path |
| `generation_mode` | `str` | `full`, `clip_only`, or `assembly_only` |
| `scenes` | `list[dict]` | 8-scene breakdown |
| `reusable_clips` | `list[str]` | Suggested reusable video clips |
| `character_refs` | `list[str]` | Suggested character reference images |
| `style_refs` | `list[str]` | Suggested style reference videos |
| `style_bible_path` | `str \| None` | Optional JSON character/style bible source |
| `style_bible` | `dict` | Persisted character/style continuity rules |

### Master plan JSON

```json
{
  "created": "2026-07-17T...Z",
  "style_analysis": {...},
  "reusable_assets": {"video_clips": 5, "images": 12, ...},
  "generator_recommendations": [...],
  "songs": [...]
}
```

---

## Generator catalog

| ID | Name | Type | Min VRAM |
|---|---|---|---|
| `wan21` | Wan 2.1 | Local | 16 GB |
| `ltx2` | LTX Video 2.x | Local | 24 GB |
| `stable_video_diffusion` | Stable Video Diffusion | Local | 8 GB |
| `animate_diff` | AnimateDiff (SDXL) | Local | 8 GB |
| `kling` | Kling AI | Cloud free tier | — |
| `luma` | Luma Dream Machine | Cloud free tier | — |
| `pika` | Pika Labs | Cloud free tier | — |

---

## Testing

```bash
cd AI_INFLUENCER_STUDIO
python -m pytest tests/test_music_video_researcher.py -v
```

---

## Known limitations

- **YouTube trends** use jina.ai public scraping; for production, replace with YouTube Data API v3.
- **Generator catalog** is static; real-time pricing/availability are not fetched.

---

## Web Dashboard

Start the web server:

```bash
aisocial web
# or
python -m ai_influencer_studio.web.app
```

Then open `http://localhost:8000/music-video`.

### Pages

| Page | Path | Purpose |
|---|---|---|
| Research | `/music-video` → Research card | Research free video generators and YouTube trends |
| Plan | `/music-video` → Plan card | Create a master plan for a song |
| Execute | `/music-video` → Execute card | Run a saved plan through the ComfyUI pipeline |

### Execute form UX

- Plans are loaded from `/api/music-video/plans` into a dropdown.
- The **Run ComfyUI Pipeline** button is disabled until a plan is selected.
- Click **Refresh Plans** to reload the dropdown.

---

## HTTP API

### `POST /api/music-video/research`

Research free video generators and YouTube trends.

**Form fields:**

| Field | Type | Default | Description |
|---|---|---|---|
| `vram` | int | 8 | Minimum VRAM in GB |
| `max_results` | int | 10 | Maximum number of trend results |

**Response:**

```json
{
  "generators": [{"id": "wan21", "name": "Wan 2.1"}],
  "trends": [{"video_id": "abc123", "title": "Trend"}]
}
```

### `POST /api/music-video/plan`

Create and save a master music video plan for one song.

**Form fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `song_name` | str | yes | Song title |
| `audio_path` | str | yes | Path to audio file |
| `genre` | str | no | Music genre |
| `mood` | str | no | Visual mood |
| `duration` | float | no | Song duration in seconds (default 180) |
| `character_ref` | str | no | Path to character reference image |
| `generation_mode` | str | no | `full`, `clip_only`, or `assembly_only` (default `full`) |

**Response:**

```json
{
  "plan": {"songs": [...]},
  "path": "/path/to/Song_Name_music_video_plan.json"
}
```

### `GET /api/music-video/plans`

List saved master plans in the configured data directory.

**Response:**

```json
{
  "plans": [
    {"name": "Song_Name_music_video_plan.json", "path": "...", "songs": 1, "created": "..."}
  ]
}
```

### `POST /api/music-video/execute`

Execute a saved song plan through the ComfyUI orchestrator.

**Form fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `plan` | str | yes | Filename in data directory or full path |
| `song_index` | int | no | Index of song to execute (default 0) |
| `generation_mode` | str | no | Override plan generation mode |

**Validation:**

- Plan file must exist.
- Plan must contain a non-empty `songs` list.
- Selected song must be a dict with a non-empty `audio_path`.
- Referenced `audio_path` file must exist on disk.

**Response:**

```json
{"returncode": 0, "output_dir": "..."}
```

### `POST /api/music-video/analyze-audio`

Analyze an audio file and return duration and BPM.

**Form fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `audio_path` | str | yes | Path to audio file |

**Response:**

```json
{"duration": 210.5, "bpm": 128.0, "source": "librosa"}
```

### `DELETE /api/music-video/plans/{plan_name}`

Delete a saved master plan.

**Response:**

```json
{"deleted": "Song_Name_music_video_plan.json"}
```

### `POST /api/music-video/plans/{plan_name}/rename`

Rename a saved master plan.

**Form fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `new_name` | str | yes | New filename ending in `.json` |

**Response:**

```json
{"renamed": {"from": "old.json", "to": "new.json"}}
```

### `WS /ws/music-video/execute`

Execute a saved song plan with real-time progress streaming.

**Message (client → server):**

```json
{"plan": "Song_Name_music_video_plan.json", "song_index": 0, "generation_mode": "full"}
```

**Messages (server → client):**

```json
{"type": "status", "message": "started"}
{"type": "stdout", "line": "transcribing..."}
{"type": "stderr", "line": "..."}
{"type": "done", "returncode": 0}
{"type": "error", "message": "..."}
```

---

### `POST /api/video/repurpose`

Create a vertical repurposed clip from an existing video.

**Form fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `input_path` | str | yes | Path to source video |
| `platform` | str | no | `tiktok`, `instagram`, or `youtube` (default `tiktok`) |
| `start` | float | no | Start time in seconds (default 0) |
| `duration` | float | no | Clip duration in seconds (default full video) |
| `caption` | str | no | Caption to burn into the clip |

### `POST /api/video/repurpose/multi`

Generate repurposed clips for multiple platforms.

**Form fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `input_path` | str | yes | Path to source video |
| `platforms` | str | yes | Comma-separated platform list |
| `clip_duration` | float | no | Duration of each segment (default 15) |

### `POST /api/scheduler/{scheduler}/push`

Push a payload to an external scheduler. `{scheduler}` can be `n8n`, `postiz`, or `mixpost`.

**Request body:** JSON payload to forward to the scheduler.

**Response:**

```json
{"status": 200, "body": "ok"}
```

---

## Scheduler integrations

The studio can push finished videos to external schedulers:

| Scheduler | Config keys | Method |
|---|---|---|
| n8n | `n8n_webhook_url` | `AutomationAdapter.push_to_n8n` |
| Postiz | `postiz_api_url`, `postiz_api_key` | `AutomationAdapter.push_to_postiz` |
| Mixpost | `mixpost_api_url`, `mixpost_api_key` | `AutomationAdapter.push_to_mixpost` |

---

## Next steps

1. Replace jina.ai scraping with YouTube Data API v3.
2. Auto-detect BPM and duration from audio files.
3. Add real-time progress updates via WebSocket for long ComfyUI renders.
4. Add native ComfyUI orchestrator support for `--character-ref` and clip-first flags.
