# 🎬 YOUTUBE_TOOLS_SYSTEM_INDEX.md

> **Master index for YouTube Enhancement & Transcript Harvest system.** Covers 5 files — transcript harvester runtime, design doc, enhancements guide, quick start, and audit trail. Additive-only, public-transcript-only, Rule #8 fenced.

**Generated:** 2026-06-28
**Parent systems:** ComfyUI, AI Tools Dashboard

---

## 📁 FILE INVENTORY (5 files)

| File | Size | Purpose |
|---|---|---|
| `youtube_transcript_harvest.py` | ~3 KB | Python runtime: parses captions from YouTube video IDs, splits by sentence, pushes to Project Brain ingest |
| `YOUTUBE_TRANSCRIPT_HARVEST_DESIGN.md` | ~3 KB | Design doc: public-transcript-only harvest, audit trail, additive-only constraints |
| `YOUTUBE-ENHANCEMENTS.md` | ~4 KB | Enhancement guide: transcript harvesting, metadata enrichment, formatting tools |
| `QUICK_START_YOUTUBE_ENHANCEMENT_TOOLS.md` | ~2 KB | Quick start: setup and first harvest walkthrough |
| `youtube_transcript_harvest.md` | ~2 KB | Usage reference for the harvest tool |

### Related (in subdirectories)

| Location | Content |
|---|---|
| `04_DEVELOPMENT/` | `youtube_enhancement_tools` Python package |
| OpenClaw agents | `/steer` and `/side` commands for task redirection |

---

## 🏗️ ARCHITECTURE

```
User provides video IDs/URLs
          │
          ▼
youtube_transcript_harvest.py
          │
          ├─ Parse captions (public transcripts only)
          ├─ Split by sentence boundaries
          ├─ Push chunks → PROJECT_BRAIN_2_0/ingest.py
          ├─ Write audit trail → YOUTUBE_TRANSCRIPT_AUDIT.log
          │
          └─ REFUSE: local media (Videos/Music/Pictures/Recordings)
```

---

## 🔒 SECURITY BOUNDARIES

- **Public-transcript-only:** Never accesses private video data or local media libraries
- **Rule #8 fence:** Refuses Videos, Music, Pictures, Recordings folders
- **Additive-only:** Audit log grows monotonically. No transcript row is deleted.
- **No credentials stored:** No API keys in these files.

---

## 🔗 CROSS-REFERENCES

| System | Index |
|---|---|
| ComfyUI Music Video Studio | `ComfyUI/COMFYUI_SYSTEM_INDEX.md` |
| AI Tools Dashboard | `AI_TOOLS_DASHBOARD.html` |
| Workspace Master | `WORKSPACE_INDEX.md` |

---

*Designed under Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite.*
