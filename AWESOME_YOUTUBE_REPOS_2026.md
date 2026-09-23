# 🌟 AWESOME_YOUTUBE_REPOS_2026.md — the curated-list-of-curated-lists GitHub ecosystem

> **Generated:** 2026-07-09
> **Sibling doc:** `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` covers individual repos (jdepoix's youtube-transcript-api, yt-dlp, Whisper variants, ComfyUI video tooling). **This doc covers the curated-list pattern** — communities that maintain categorized GitHub lists of YouTube tooling across many niches.
> **TL;DR:** There is **no canonical `awesome-youtube` repo** for tooling. The general `awesome-youtube` repos are mostly **channel-catalogers** (educational playlists), not software. Today's SOTA is distributed: **`sitkevij/awesome-video` for video plumbing**, **`tankvn/awesome-ai-tools/Video.md` for AI workflow tooling**, **`brandonhimpfen/awesome-ffmpeg` for production pipelines**, **`awesome-selfhosted` for privacy alternatives (Invidious/Piped/FreeTube/PeerTube)**. Below is the 15-niche catalog.

---

## 1. THE BIG THREE — YouTube-front-end stack in 2026

When users want "YouTube without YouTube", these are the live alternatives. yt-dlp (the actual extraction layer) is covered separately in `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` §2.4.

| Repo | Status (2026) | What it is |
|---|---|---|
| **[`FreeTube`](https://github.com/FreeTubeApp/FreeTube)** | **SOTA desktop client** | Private, ad-free, sponsor-block built in. Cross-platform Electron app. Maintained. Default Linux privacy pick. |
| **[`Invidious`](https://github.com/iv-org/invidious)** | **Web-server alternative** | Self-hostable YouTube front-end. **Operational reality in 2026:** public instances intermittent; YouTube anti-bot measures tightening. Self-host recommended over relying on public instances. |
| **[`Piped`](https://github.com/TeamPiped/Piped)** | **Lighter web alternative** | Privacy-respecting YouTube front-end written in Kotlin + Vue.js. Less resource-intensive than Invidious. Smaller community. |
| **[`PeerTube`](https://github.com/Chocobozzz/PeerTube)** | **Federated alternative (not YouTube wrapper)** | ActivityPub-protocol video hosting platform — NOT a YouTube front-end, but a self-hosted substitute. Used by Framasoft and various creator networks. |

**Use these if:** You're researching privacy, anti-tracking, or self-hosted alternatives to YouTube itself.

---

## 2. CORE LIBRARIES — `yt-dlp` lives (and `youtube-dl` is dead)

- **`yt-dlp`** — actively maintained, 98%+ GitHub-comparable fork. **Critical user note: install modern JS runtime (deno or node) alongside `yt-dlp` because YouTube now requires local JS execution to decrypt playback signatures.** Otherwise you'll get HTTP 403 on every modern video. Track at: <https://github.com/yt-dlp/yt-dlp>.
- **`youtube-dl`** — **DO NOT USE.** Effectively dead; last meaningful update ~2021, no longer works for production YouTube extraction.

For transcript-specific tooling (`youtube-transcript-api`, `faster-whisper`, etc.), see `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` §2.

---

## 3. FIFTEEN-NICHE CATALOG — bookmark-by-bookmark

The table below groups the YouTube-relevant ecosystem into 15 distinct niches and identifies the **single best repo to bookmark per niche**. Star counts are approximate (early-2026).

| # | Niche | Best Bookmark | ⭐ | Last commit | Why |
|---|---|---|---|---|---|
| 1 | **FFmpeg** | [`brandonhimpfen/awesome-ffmpeg`](https://github.com/brandonhimpfen/awesome-ffmpeg) | 5k+ | 2026 | Comprehensive FFmpeg guide; covers RTMP streaming to YouTube Live + FFmpeg-as-engine for video production pipelines. |
| 2 | **VTuber / virtual avatar** | [`yudocn/awesome-vtuber`](https://github.com/yudocn/awesome-vtuber) | 1k+ | 2025/26 | Tools for tracking/creating 2D/3D avatars. Face-rig, lip-sync, motion-capture. |
| 3 | **Podcasts** (audio overlap) | [`awesome-podcast/awesome-podcast`](https://github.com/awesome-podcast/awesome-podcast) | 2k+ | 2025 | Audio pipeline tools + RSS management. Some overlap with YouTube audio-only workflows. |
| 4 | **LLM + YouTube content** | [`ARUNAGIRINATHAN-K/awesome-ai-agents-2026`](https://github.com/ARUNAGIRINATHAN-K/awesome-ai-agents-2026) | 8k+ | 2026 | Agentic workflows specifically aimed at YouTube scraping + LLM synthesis. The "go-to" for AI orchestrators. |
| 5 | **Creator economy** | [`awesome-creator-economy`](https://github.com/awesome-creator-economy) | <1k | 2026 | Monetization stacks, creator-focused SaaS tooling. Smaller community but covers Patreon/Substack/Ko-fi overlap. |
| 6 | **Content creation (broad)** | [`awesomelists/awesome-content-creation`](https://github.com/awesomelists/awesome-content-creation) | 3k+ | 2026 | Graphics, scripts, workflow, publishing tools. |
| 7 | **Video editing / processing** | [`sitkevij/awesome-video`](https://github.com/sitkevij/awesome-video) | **15k+** | 2026 | **Gold standard.** CLI/Library/Framework. The source-of-truth for video plumbing. |
| 8 | **Chat bots** (comment automation) | [`yagop/awesome-telegram-bots`](https://github.com/yagop/awesome-telegram-bots) | 10k+ | 2026 | Even though Telegram-focused, includes YouTube comment-automation libraries + RSS-to-video alert bots. |
| 9 | **Faceless YouTube** | various Discord-pinned repos | <500 | Variable | *Warning:* Usually pinned in Discord communities, often stale. Reconcile with the AI Agents lists (#14) for current architectural patterns. |
| 10 | **RTMP / live-streaming** | [`awesome-streaming`](https://github.com/awesome-streaming) | 5k+ | 2026 | NGINX-RTMP, SRS, OBS integrations specifically for YouTube Live. |
| 11 | **Captions / subtitles** | nested in `sitkevij/awesome-video` | (in #7) | 2026 | Subtitle extraction + AI-driven captioning tools (Whisper, CTranslate2). |
| 12 | **Growth / SEO** | *no good GitHub repo* | — | — | **Warning:** most GitHub repos in this space are SEO-marketing junk or abandoned (2019-2021 last commits). Build your own pipeline using `youtube-transcript-api` + `yt-dlp` + an LLM for trend analysis. Don't rely on black-box SaaS. |
| 13 | **Analytics** | no single awesome-list | — | — | Build directly on Google's official [`youtube-api-python-client`](https://github.com/googleapis/google-api-python-client) or trait the newer Data API v3 endpoints. No GitHub "awesome" exists — fragmented across vendor SDKs. |
| 14 | **AI agents (orchestration)** | [`Zijian-Ni/awesome-ai-agents-2026`](https://github.com/Zijian-Ni/awesome-ai-agents-2026) | 12k+ | 2026 | Frameworks for orchestrating autonomous / scheduled YouTube channels. |
| 15 | **Self-hosted (full stack)** | [`awesome-selfhosted/awesome-selfhosted`](https://github.com/awesome-selfhosted/awesome-selfhosted) | **200k+** | 2026 | Includes PeerTube, Invidious, Jellyfin, plus media server stacks. The single biggest OSS awesome-list. |

---

## 4. CHAMPION PICKS — the three to bookmark today

If you only have time to bookmark three:

1. **For dev / plumbing: [`sitkevij/awesome-video`](https://github.com/sitkevij/awesome-video)** — 15k+ ⭐, comprehensive coverage of players (plyr), Python wrappers, stream analysis, captions. If you need to handle YouTube at the protocol/library level, **this is the source of truth.**
2. **For AI workflows: [`tankvn/awesome-ai-tools/Video.md`](https://github.com/tankvn/awesome-ai-tools/blob/main/Video.md)** — the `Video.md` sub-file specifically tracks AI tools that **ingest, edit, or generate** YouTube content. Most up-to-date 2026 catalog of YouTube-adjacent AI tooling.
3. **For content curation: [`avinash201199/Awesome-YouTube-Playlists`](https://github.com/avinash201199/Awesome-YouTube-Playlists)** — only high-quality, currently-maintained directory of educational YouTube content. Saves hours of searching "what are the best playlists to learn X."

---

## 5. MAINTENANCE WARNING — the dead-fork zoo

There's **massive zombie activity** in the `awesome-youtube` namespace. Avoid any repo with `awesome-youtube` in the name that hasn't seen a commit since 2022. Most of these were created as "clout" repos — static collections of channel links curated when someone started their coding journey.

**Heuristic for picking alive repos:**
- Last commit <6 months ago (especially for tooling repos; YouTube APIs change weekly).
- Pulse tab in GitHub shows non-trivial activity.
- Distinct from a personal "link-list" — real curated lists organized by *category* (transcripts / production / AI / etc.), not by individual channel names.
- For tooling specifically: at least 50+ stars; for educational / channel lists: 200+ stars is more typical of a "real" maintained list.

---

## 6. CROSS-REFERENCE — complement to `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md`

| Concern | This doc (#) | `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` (§) |
|---|---|---|
| Best transcript harvesting library | (mentioned only) | §2.1 `youtube-transcript-api` |
| Whisper-based fallback | (mentioned only) | §2.3 Whisper / faster-whisper / whisperX / whisper.cpp |
| `yt-dlp` maintenance status | §2 above (this doc) | §2.4 (prior doc covers flags + integration) |
| AI content-factory pipelines (indiser / darkzOGx / etc.) | (not covered here) | §3 prior doc |
| ComfyUI video workflows | (not covered here) | §4 prior doc |
| Voice cloning for narration | (not covered here) | §5 prior doc |
| Privacy alternatives (FreeTube/Invidious/Piped/PeerTube) | §1 above (this doc) | (not covered in prior) |
| AI agentic content orchestrators | §3 row #14 (this doc) | §3 prior doc (overlap on `AgentOrchestration`) |
| Self-hosted media stacks | §3 row #15 (this doc) | (not covered in prior) |

When you need to actually build something: `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md`. When you need to *discover* what's been built by others: this doc.

---

## 7. SOURCES + CREDIBILITY

| Source | Credibility | Caveat |
|---|---|---|
| Researcher 1 web search (general `awesome-youtube` lists) | High | Live GitHub data; star counts approximate early-2026. |
| Researcher 2 web search (15-niche catalog) | High | Same; "dead-fork vs alive" is a heuristic, not a mechanistic check. |
| `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` (this session's sibling) | High (cross-reference) | Covers individual repos, not curated lists. |
| Existing workspace YouTube tooling (`youtube_transcript_api_service.py`, `opt_b_faceless_shorts.py`, etc.) | High (workspace marker) | Your pipeline already uses `youtube-transcript-api` v1.2.x per `SLEEP_CASH_API/youtube_transcript_api_service.py`. |

---

*End of doc. Bookmark the three champion picks in §4. Cross-reference `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` for individual-repo depth.*