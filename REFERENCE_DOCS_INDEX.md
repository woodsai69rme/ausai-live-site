# 🗂️ REFERENCE_DOCS_INDEX.md — reading-order guide for the workspace reference docs

> **Generated:** 2026-07-09
> **Purpose:** Single-page navigation index for the 4 reference docs that accumulated this session. Picks the right doc for your question.
> **Not** a knowledge base — just navigation. Each reference doc is its own self-contained deep dive.

---

## 📚 THE FOUR REFERENCE DOCS — at a glance

| Doc | Read time | Primary verb | What shape |
|---|---|---|---|
| [`YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md`](YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md) | ~25 min | **Building** | Deep dive into specific repos at the code-level. "What's the SOTA WAY?" |
| [`AWESOME_YOUTUBE_REPOS_2026.md`](AWESOME_YOUTUBE_REPOS_2026.md) | ~10 min | **Discovering** | Catalog of curated GitHub awesome-list-of-lists. "What's been BUILT BY OTHERS?" |
| [AWESOME_AGENTS_BROWSER_COMPUTER_USE_2026.md](AWESOME_AGENTS_BROWSER_COMPUTER_USE_2026.md) | ~15 min | **Discovering** | Awesome lists + projects for AI agents, skills, browser-use, computer-use |
| Local mirror: `github_repos/awesome_agents_lists/` | ~5 min | **Browsing offline** | Shallow clones of 11 awesome lists + 3 engines; see `INDEX.md` + `README.md` |
| [`HARDWARE_SHOPPING_LIST_2026.md`](HARDWARE_SHOPPING_LIST_2026.md) | ~15 min | **Buying** | Tier-anchored shopping list for USB-C / TB / display / peripheral hardware. "What PRODUCT matches my ports?" |
| [`SUNSHINE_MOONLIGHT_SETUP.md`](SUNSHINE_MOONLIGHT_SETUP.md) | ~10 min | **Installing** | Step-by-step guide for cable-free remote-desktop. "How DO I set this up?" |

---

## 🎯 WHICH DOC WHEN — pick by intent

| If you're asking... | Open |
|---|---|
| "What can I run today? Show me all installed AI + IT tools" | `AI_AND_IT_TOOLKIT.md` (Tier 1 first) OR `python tool_kit.py list --tier t1` |
| "I want the full AI army war room (voice + browser + computer + skills)" | `OPEN_WAR_ROOM_CONTROL.bat` · `WAR_ROOM_CONTROL.md` · `WAR_ROOM_CONTROL_DASHBOARD.html` |
| "All free models / APIs / tools / resources" | `FREE_RESOURCES_MASTER.md` · `OPEN_FREE_RESOURCES.bat` · War Room **Free Resources** tab |
| "Session docs for free + War Room + Drive RAG" | `SESSION_DOCUMENTATION_2026-07-16_c.md` (X: + `_DOCS_ARCHIVE`) · `FREE_RESOURCES_WAR_ROOM_DRIVE_RAG_DOCUMENTATION_2026-07-16.md` |
| "I just want to see the daily-driver tools in a clean browser dashboard" | open `AI_AND_IT_TOOLKIT.html` |
| "What's the best Python library for YouTube transcript harvesting?" | `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` §2 |
| "Is there a curated list of YouTube AI tools?" | `AWESOME_YOUTUBE_REPOS_2026.md` §3 row #4 + §4 pick #2 |
| "Where are local clones of agent/browser/computer-use awesome lists?" | `github_repos/awesome_agents_lists/INDEX.md` · research: `AWESOME_AGENTS_BROWSER_COMPUTER_USE_2026.md` |
| "Best browser agent / computer-use stack for OpenRouter?" | Agency: `AI_AGENCY/` · research: `AWESOME_AGENTS_BROWSER_COMPUTER_USE_2026.md` · clones: `awesome_agents_lists/` |
| "What hub should I buy for my laptop's USB-C ports?" | `HARDWARE_SHOPPING_LIST_2026.md` Step 0 first, then §-tier tables |
| "How do I install Sunshine + Moonlight?" | `SUNSHINE_MOONLIGHT_SETUP.md` Step 1-5 |
| "What's the most current AI content-factory pipeline?" | `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` §3 |
| "What's the best ComfyUI video workflow?" | `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` §4 |
| "What's a hardware-KVM switch box?" | `HARDWARE_SHOPPING_LIST_2026.md` §M |
| "Best front-end alternative to YouTube (privacy)? " | `AWESOME_YOUTUBE_REPOS_2026.md` §1 (Big Three) |
| "What is `yt-dlp` and why do I need deno alongside it?" | `AWESOME_YOUTUBE_REPOS_2026.md` §2 |
| "Any community list of people-tracking-style analytics or growth hacks for YouTube?" | `AWESOME_YOUTUBE_REPOS_2026.md` §5 (warning: mostly SEO-marketing junk) |
| "Can I use my laptop on a phone/tablet as a 2nd display?" | `HARDWARE_SHOPPING_LIST_2026.md` §K (Phone-as-display) |
| "Will my OnePlus/Oppo work with this Android tool I'm building?" | (not in current 4 — falls back to `COMPLETED_PROJECTS/mobile_backup/MOBILE_TOOLS_INDEX.md`) |

---

## 🔗 CROSS-REFERENCE TABLE — by topic

| Topic | YOUTUBE-RESEARCH | AWESOME-YOUTUBE | HARDWARE-SHOPPING | SUNSHINE-MOONLIGHT |
|---|---|---|---|---|
| **Python transcript libs** | §2 ✓ | — | — | — |
| **Whisper / faster-whisper** | §2.3 ✓ | — | — | — |
| **`yt-dlp` flag recipe** | §2.4 ✓ | §2 ✓ (status) | — | — |
| **AI content-factory pipelines** | §3 ✓ | §3 row #4 ✓ | — | — |
| **ComfyUI video trends** | §4 ✓ | §3 row #7 + §4 pick #1 ✓ | — | — |
| **Voice cloning** | §5 ✓ | — | — | — |
| **Privacy front-ends (FreeTube/etc)** | — | §1 ✓ | — | — |
| **USB-C / TB dock SKU table** | — | — | §-tier 1/2/3 ✓ | — |
| **DisplayLink adapters** | — | — | §E (USB-A fallback) ✓ | — |
| **Hardware KVM switch box** | — | — | §M ✓ | — |
| **Phone-as-display** | — | — | §K ✓ | — |
| **Sunshine/Moonlight install** | — | — | — | ✓ |
| **Sunshine vs Parsec vs VNC** | — | — | — | (Tier-2C table) |

---

## 📐 SUGGESTED READING ORDER — first-time readers

If you're seeing these for the first time and want to build mental model:

1. **`YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md`** — establish what tools exist (the individual repos layer).
2. **`AWESOME_YOUTUBE_REPOS_2026.md`** — see how the community has organized them.
3. **`HARDWARE_SHOPPING_LIST_2026.md`** — if you're going to use any of these tools on physical hardware.
4. **`SUNSHINE_MOONLIGHT_SETUP.md`** — once you decide to commit to a cable-free setup.

OR in reverse: if your question starts HARDWARE-side (e.g., "I need to plug displays into this laptop"), start at HARDWARE-SHOPPING first, then read the others as relevant.

---

## 🪢 RELATIONSHIP TO WORKSPACE INDEX INFRASTRUCTURE

This doc is from inside the workspace, where the surrounding indexing is:

- `WORKSPACE_INDEX.md` — master ecosystem index (18 systems + cross-refs)
- `GRAND_SUMMARY.md` — one-page printable summary
- `MASTER_INDEX_1PAGE.md` — AusAI Tech consulting business index
- `CHANGELOG.md` — complete fleet history
- `ALL_TOOLS_QUICK_REFERENCE.md` — `START-ALL-AI-TOOLS.bat` menu quick-ref card

These higher-level indexes already point AT this file via the "Reference docs:" line. This file is the leaf for reference-doc navigation.

---

*End of navigation index. Each section is a one-question lookup. If a topic doesn't fit any of the 4 reference docs, the source-of-truth is `WORKSPACE_INDEX.md` then `CHANGELOG.md`.*
