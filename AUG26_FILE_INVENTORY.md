# 📦 aug26 Playlist Project — Complete File Inventory

*Snapshot: 2026-08-21 05:14 · Workspace: `C:\Users\karma\` · All sizes current (post-recovery)*

Companion to `AUG26_PLAYLIST_PROJECT.md` (master documentation) and
`AUG26_INCIDENT_REPORT.md` (2026-08-21 data-loss incident + recovery).

---

## 1. Deliverables (what to open)

| File | Size | Role |
|---|---|---|
| `AUG26_PLAYLIST_GUIDE.md` | 155 KB | **The guide** — stats, categories, top-15 viewed, tools catalog, full video-by-video review of all 421, 5 learning paths |
| `AUG26_PLAYLIST_DASHBOARD.html` | 292 KB | Self-contained dashboard — thumbnails, search, filter, sort, click-through |
| `AUG26_WATCHLIST_TRACKER.html` | 275 KB | Interactive tracker — watched/notes (localStorage), status filter chips, export/import progress |
| `AUG26_PRIORITY_PAGE.html` | 154 KB | Shareable, self-contained page ranking all 421 videos by watch-priority (search + category/status/min-priority filters) |
| `AUG26_ACTION_PLAYBOOK.md` | 10 KB | Transcript-grounded playbook (AI video-gen + music monetization, 30-day plan) |
| `AUG26_PLAYBOOK_VERIFICATION.md` | 6 KB | Claim-by-claim playbook verification (17/18 confirmed) |
| `AUG26_TREND_ANALYSIS.html` + `.md` | 25 KB + 3 KB | 5 SVG charts: weekly volume, category mix over time, weekday distribution |
| `AUG26_CHANNEL_DIGEST.md` | 29 KB | Per-channel digest — 47 channels with ≥2 videos, focus + top 3 each |
| `AUG26_PROGRESS_REPORT.md` | <1 KB | Watched-progress report (populates after tracker export) |
| `AUG26_WATCH_THIS_WEEK.md` | 5 KB | Top-10 unwatched by priority score + 7-day flow + full top-25 |
| `AUG26_UNAVAILABLE_REPORT.md` | 4 KB | The 12 non-OK videos: why each is unavailable, patterns, archive.org result, maintenance tips |
| `AUG26_FREE_TOOLS.md` | 25 KB | **Everything FREE mined from all 421 videos** — free coding stack, free agents, free video/audio gen, free courses, 188 free GitHub repos, paid→free alternative map, top-20 free videos |
| `aug26_watchlist.csv` | 174 KB | 421-row watchlist CSV (UTF-8 BOM): #, original position, id, title, channel, length, views, likes, date, category, tools, url, summary |
| `aug26_watchlist_verification.md` | <1 KB | Availability results: 409 OK / 10 EMBED_DISABLED / 1 PRIVATE / 1 REMOVED |
| `aug26_embedding_disabled.csv` + `.md` | 4 KB + 2 KB | The 10 live-but-unembeddable videos (outreach list) |
| `aug26_duplicates.md` | 4 KB | Duplicate cleanup report (49 positions removed, per-video table) |
| `aug26_pivot_summary.md` | 4 KB | Pivot tables by category / duration / channel |
| `aug26_pivot_by_category.csv` · `aug26_pivot_by_channel.csv` · `aug26_pivot_category_channel.csv` | 1–11 KB | Pivot CSV exports |
| `AUG26_UNAVAILABLE_LOG.md` | 3 KB | Watcher log: weekly status of the 12 watched videos (appended) |
| `AUG26_UNAVAILABLE_ALERT.md` | — | Written only when an unavailable video's status changes |
| `AUG26_REFRESH_HISTORY.md` | <1 KB | Persistent record of every batch run (PASS/FAIL + videos + verification counts) |
| `refresh_status.json` | <1 KB | Machine-readable latest run status (success/failed + stats) — written by `record_refresh.py` |
| `REFRESH_STATUS_ALERT.md` | — | Written by the startup check when the last refresh failed or is stale; removed when healthy |
| `aug26_tracker_progress.json` | — | **REAL** watched/notes export from the tracker (feeds the progress report) |
| `aug26_tracker_progress.demo.json` | <1 KB | Demo seed used only when the real export is absent (clearly labeled DEMO in the report) |
| `priority_config.json` | <1 KB | Tune priority scoring: weights, category interests, recency half-life, max-views |
| `MEMORY/` | 7 docs + `chatgpt_chats/` | **Canonical memory layer** — golden rules, background/projects, free AI tools, computer-use/Foot Clan, session index, system status (always backed up + RAG-indexed) · `chatgpt_chats/` = 4,101 one-per-chat files (4,501 RAG chunks) |
| `build_chatgpt_chat_index.py` | — | Rebuild `MEMORY/chatgpt_chats/` from `CHATGPT_DEEP_INDEX.json` (4,101 conversations) |
| `sync_drive_after_connect.py` | — | Watches for the rclone `gdrive:` token, then auto-syncs the mirror to Drive + writes `SYNC_DRIVE_STATUS.md` |
| `MEMORY_QUERY.bat` | — | Launcher: query the RAG memory, re-ingest, backup, Drive connect |
| `CONNECT_GOOGLE_DRIVE.bat` | — | One-time rclone `gdrive:` browser OAuth + first Drive sync |
| `TOOLS/drive_backup_rag/config.json` | — | Backup+ RAG config: 76 include sources, `rclone_remote=gdrive`, answer timeout 300s |
| `BACKUPS/drive_rag/drive_rag.sqlite` | 6.3 GB | **The RAG DB** — ~1.84M chunks (SQLite FTS5 + Ollama embeddings): workspace 24,093 · session archives 21,919 · codingsesh 64,896 · docs archive ~1.7M |
| `BACKUPS/GOOGLE_DRIVE_MIRROR/` | 446 MB | Drive mirror — 76 sources / 17,479 files (memory + docs + 4,101 ChatGPT chats) |
| `BACKUPS/GOOGLE_DRIVE_MIRROR/warroom_backup_20260822_*.zip` | 158 MB | Zip pack for manual Drive upload (regenerate after adding chats: `backup --method export_zip`) |

## 2. Documentation

| File | Size | Role |
|---|---|---|
| `AUG26_PLAYLIST_PROJECT.md` | 21 KB | **Master documentation** — overview, deliverables, data, scripts, refresh procedure, verification, duplicates, caveats, memory layer + free-tools section (§10) |
| `AUG26_INCIDENT_REPORT.md` | 7 KB | 2026-08-21 data-loss incident: root cause, timeline, damage, recovery, prevention |
| `AUG26_FILE_INVENTORY.md` | this file | Complete file inventory |
| `MEMORY/README.md` + `05_MEMORY_SYSTEM_STATUS.md` | 2 KB + 3 KB | Memory-layer usage + system status (what's indexed, how to query, limits) |
| `DRIVE_BACKUP_RAG.md` | 10 KB | Drive backup + RAG docs — updated 2026-08-22 with the memory layer (§0) + reconnect flow |
| `MEMORY_SYSTEM.md` | 5 KB | **Memory-system master doc** — what it is, quick start, RAG coverage, backups, maintenance |

## 3. Canonical data files (source of truth)

| File | Size | Contents |
|---|---|---|
| `playlist_details.json` | 990 KB | Raw fetched metadata per video: title, channel, duration, views, likes, upload date, full description (419/421 fetched; 2 unavailable kept as placeholders) |
| `playlist_analysis.json` | 306 KB | **The generator input** — per-video summary, category, tools, github links (421 videos) |
| `playlist_dedup_map.json` | 46 KB | Duplicate traceability: kept position + removed positions per video (49 total) |
| `full_playlist_flat.txt` | 43 KB | Deduplicated flat playlist — 421 rows × 5 fields (index, videoId, duration, channel, title) |
| `full_playlist_flat_raw462.txt` | 47 KB | Raw 462-position flat (pre-dedupe; for re-diffing against YouTube) |
| `watchlist_verification.json` | 124 KB | Per-video availability status (OK / EMBED_DISABLED / PRIVATE / REMOVED) |
| `playlist_data.json` | 134 KB | 462 basic entries (id, title, duration, channel, views) — the **recovery seed** for `recover_flat.py` |
| `playlist_raw.json` | 2.4 MB | Raw InnerTube page dump (unused by the pipeline; archival) |
| `playlist_videos.json` | 28 KB | Original 100-video parse (superseded) |
| `aug26_playlist_summary.md` | 16 KB | Pre-session summary of the first 100 videos (superseded by the guide) |

## 4. Pipeline scripts (regeneration)

### Fetch & assembly
| Script | Role |
|---|---|
| `fetch_playlist_details.py` | Fetch full metadata (incremental, resumable, checkpoint every 25; `FETCH_WORKERS` env, default 1) |
| `retry_playlist_details.py` / `retry_few.py` | Retry failed fetches (android client bypasses bot checks) |
| `recover_flat.py` | Rebuild the 462-row raw flat from `playlist_data.json` (disaster recovery) |
| `finalize_playlist.py` | Merge fetched details into `playlist_details.json` |
| `fix_indexes.py` | Rebuild indexes 1–421 deterministically from the flat |
| `refresh_titles.py` | Apply creator title renames |
| `diff_playlist.py` | Diff a fresh fetch: adds/removes/renames/order/coverage |
| `dedupe_playlist.py` | Dedupe raw→unique, renumber, write flat + details + dedup map |

### Analysis & generation
| Script | Output |
|---|---|
| `summarize_playlist.py` | `playlist_analysis.json` |
| `build_playlist_guide.py` | `AUG26_PLAYLIST_GUIDE.md` |
| `build_playlist_dashboard.py` | `AUG26_PLAYLIST_DASHBOARD.html` |
| `build_watchlist_tracker.py` | `AUG26_WATCHLIST_TRACKER.html` |
| `build_action_playbook.py` | `AUG26_ACTION_PLAYBOOK.md` |
| `fetch_transcripts.py` | Auto-captions → `transcripts/` |
| `verify_playbook.py` | `AUG26_PLAYBOOK_VERIFICATION.md` |
| `build_trend_analysis.py` | `AUG26_TREND_ANALYSIS.html` + `.md` |
| `build_channel_digest.py` | `AUG26_CHANNEL_DIGEST.md` |
| `build_pivot_summary.py` | `aug26_pivot_summary.md` + 3 CSVs |
| `export_watchlist_csv.py` | `aug26_watchlist.csv` + `aug26_duplicates.md` |
| `verify_watchlist_oembed.py` | `watchlist_verification.json` + `aug26_watchlist_verification.md` |
| `verify_watchlist.py` | yt-dlp fallback verifier (`VERIFY_SLICE`/`VERIFY_WORKERS`) |
| `check_unavailable.py` | Watcher → `AUG26_UNAVAILABLE_ALERT.md` + log |
| `export_embedding_disabled.py` | `aug26_embedding_disabled.csv` + `.md` |
| `build_progress_report.py` | `AUG26_PROGRESS_REPORT.md` (from tracker export; **priority-scored** suggestions via `priority_config.json`; prefers the real export over the demo seed) |
| `build_weekly_and_unavailable.py` | `AUG26_WATCH_THIS_WEEK.md` + `AUG26_UNAVAILABLE_REPORT.md` |
| `build_free_tools.py` | `AUG26_FREE_TOOLS.md` — free-tool extraction from all 421 videos |
| `fetch_transcripts2.py` | Transcripts for the Grok wave + music deep-dive videos (into `transcripts/`) |
| `build_priority_page.py` | `AUG26_PRIORITY_PAGE.html` — shareable priority-ranked page (all 421 videos) |
| `record_refresh.py` | Append to `AUG26_REFRESH_HISTORY.md` + write `refresh_status.json` — called by the batch on success and failure |
| `check_refresh_status.py` | Startup check: alert when the last refresh failed/stale; writes/clears `REFRESH_STATUS_ALERT.md`, exit 0/1 |
| `STARTUP_REFRESH_CHECK.bat` | Runs `check_refresh_status.py` at logon (logs to `refresh_logs/startup_check.log`); **installed in the Windows Startup folder** |

### Full Stack comparisons
| Script | Output |
|---|---|
| `fullstack_playlist_compare.py` | `FULLSTACK_PLAYLIST_COMPARISON.md` |
| `build_fullstack_deep_dive.py` | `FULLSTACK_DEEP_DIVE.md` |
| `build_watchlist_catalog_gaps.py` | `FULLSTACK_WATCHLIST_GAPS.md` |

### Safety tooling
| Script | Role |
|---|---|
| `backup_playlist_data.py` | Timestamped backup of 5 canonical files → `data_backups/` (keep 7) |
| `check_data_integrity.py` | ≥400 videos + non-truncated flat; on failure restores + exits 1 |

### Automation
| File | Role |
|---|---|
| `refresh_aug26_playlist.bat` | Weekly batch: 10 fail-safe steps, logs to `refresh_logs/`, scheduled task `aug26_playlist_weekly_refresh` (Sun 03:00) — also copies the priority page into the suite's `public/` so the dashboard tab auto-updates |
| `START_QUAD_VISION_SUITE.bat` (etc.) | Unrelated to this project |

## 5. Backups & logs

| Path | Contents |
|---|---|
| `data_backups/aug26_20260821_*/` | 8 timestamped fail-safe backups of the 5 canonical files — newest 7 kept automatically |
| `refresh_logs/aug26_refresh_*.log` | 8 run logs from the 2026-08-21 batch tests + the 08-22 memory-layer full run — the 04:35 log documents the incident; later logs show clean runs |
| `AUG26_REFRESH_HISTORY.md` | 4 PASS rows (2026-08-20 ×2, 2026-08-21 ×2) — every weekly run appends here |

## 6. Transcripts (`transcripts/`, 36 files)

| Files | Role |
|---|---|
| 14 playlist-index-prefixed files (e.g. `6_8HutJ9W5pTg.txt`, `285_d_wEd-fZcdg.txt`) | Auto-captions of the top video-gen + music monetization videos — grounding for the playbook |
| 8 `grok_*.txt` files | Transcripts of the **Grok Bot wave** videos (Aug 2026) — grounding for playbook Part 3 |
| 3 `music_*.txt` files | Music deep-dive transcripts (Mozart AI, A Studio, AI influencer economics) |
| 3 `*_ID.txt` + `test_*.txt` + misc | Test artifacts from transcript-harvesting tooling |

## 7. Full Stack catalog ecosystem (related)

| File | Role |
|---|---|
| `full_stackyt_tool_catalog.json` | 115 videos / 99 tools (+8 added this session) |
| `FULL_STACKYT_EXECUTION_PACK.json` + `.md` | 99 Backlog records (regenerated) |
| `FULL_STACKYT_CHANGELOG.md` | Catalog changelog incl. the +8 additions |
| `validate_full_stackyt_package.py` | Package validator — **PASS** (115/99/99) |
| `full_stackyt_query.py` | CLI query tool |
| `FULLSTACK_PLAYLIST_COMPARISON.md` / `FULLSTACK_DEEP_DIVE.md` / `FULLSTACK_WATCHLIST_GAPS.md` | This project's Full Stack analysis (see §1) |
