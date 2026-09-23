"""Tool_Kit — operator self-use CLI dispatcher.

Companion to AI_AND_IT_TOOLKIT.md / .html. Subcommands:

    python tool_kit.py list                    # all tools (terse)
    python tool_kit.py list --category agents  # filter by category
    python tool_kit.py list --tier t1          # filter by tier (T1-T4)
    python tool_kit.py categories              # list categories + counts
    python tool_kit.py tiers                   # list tiers + counts
    python tool_kit.py search <substring>      # search name / path / invocation / notes
    python tool_kit.py info <name>             # full record for one tool
    python tool_kit.py run <name>              # print invocation only (dispatcher never executes)
    python tool_kit.py health                  # live TCP probes against local services

Stdlib-only (argparse, socket, sys, typing). No external deps.
Cross-platform; runs on Windows + Linux + macOS.

Designed under the user's Golden Rules: append, preserve, protect.
New rows are added in the REGISTRY dict below; existing rows are never removed.
"""

import argparse
import socket
import sys
from typing import Dict, List, Optional, Tuple

# Ensure stdout can print box-drawing / middle-dot / bullet chars on Windows
# cp1252. Otherwise `list` fails with UnicodeEncodeError on `·` / `→` glyphs.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Python 3.7+
except (AttributeError, ValueError):
    pass  # non-configurable stdout environments (e.g. pipes); let default apply.

# ============================================================
# TOOL REGISTRY — append-only; do not remove rows. To deprecate, set tier to t4.
# Paths shown below use Karma's local-machine Windows conventions; the
# dispatcher itself is cross-platform (slug-based lookup, not fs-based).
# ============================================================

REGISTRY: Dict[str, Dict] = {
    "ollama": {
        "category": "runtime", "tier": "t1",
        "name": "Ollama",
        "path": r"C:\Users\karma\.ollama\ · 127.0.0.1:11434",
        "invocation": "ollama pull <model>  ·  ollama run <model> <prompt>",
        "notes": "v0.31.x · models: qwen2.5-coder:latest, deepseek-r1:8b, ornith:9b, llama3.2:3b, mistral:7b",
        "health_url": "http://127.0.0.1:11434/api/tags",
    },
    "comfyui": {
        "category": "runtime", "tier": "t1",
        "name": "ComfyUI",
        "path": r"C:\Users\karma\ComfyUI\ · 127.0.0.1:8188",
        "invocation": r"C:\Users\karma\ComfyUI\launch_music_video_studio.bat",
        "notes": "Local image/video/audio generation · RTX 4060 8GB · 21-option launcher menu",
        "health_url": "http://127.0.0.1:8188/system_stats",
    },
    "openrouter": {
        "category": "cloud", "tier": "t1",
        "name": "OpenRouter",
        "path": "OPENROUTER_API_KEY env · https://openrouter.ai/api/v1/chat/completions",
        "invocation": "curl -H \"Authorization: Bearer $OPENROUTER_API_KEY\" https://openrouter.ai/api/v1/chat/completions",
        "notes": "Only AI provider per CLAUDE.md · routes to all models",
    },
    "ai-army": {
        "category": "agents", "tier": "t1",
        "name": "AI Army / Foot Clan",
        "path": r"C:\Users\karma\AI_ARMY\ · 127.0.0.1:8001",
        "invocation": r"python C:\Users\karma\AI_ARMY\server.py",
        "notes": "9 API routes · 6 agents · revenue-generating",
        "health_url": "http://127.0.0.1:8001/health",
    },
    "footclan-executor": {
        "category": "agents", "tier": "t2",
        "name": "Footclan Executor",
        "path": r"C:\Users\karma\FOOTCLAN_EXECUTOR.py",
        "invocation": r"python C:\Users\karma\FOOTCLAN_EXECUTOR.py --task \"...\" --dry-run",
        "notes": "Squad-dispatch framework with audit log",
    },
    "agent-registry": {
        "category": "agents", "tier": "t1",
        "name": "Agent Registry",
        "path": r"C:\Users\karma\AGENT_REGISTRY.md",
        "invocation": "grep -F \"<id>\" AGENT_REGISTRY.md",
        "notes": "2,793 agents across 16 domains · append-only",
    },
    "archon": {
        "category": "agents", "tier": "t2",
        "name": "Archon V2",
        "path": r"C:\Users\karma\python\ · 127.0.0.1:3737/:8181/:8051/:8052",
        "invocation": r"C:\Users\karma\START_ARCHON_STACK.bat",
        "notes": "FastAPI + Socket.IO + MCP + Agents microservice stack · 4 services",
        "health_url": "http://127.0.0.1:8181/health",
    },
    "project-brain": {
        "category": "agents", "tier": "t2",
        "name": "Project Brain 2.0",
        "path": r"C:\Users\karma\PROJECT_BRAIN_2_0",
        "invocation": "python PROJECT_BRAIN_2_0/ingest.py --watch --audit-offset",
        "notes": "SHA256-cycle dedupe · Phase A-H design corridor closed",
    },
    "ai-influencer": {
        "category": "agents", "tier": "t2",
        "name": "AI Influencer Factory",
        "path": r"C:\Users\karma\ai_influencer_factory.py",
        "invocation": "python ai_influencer_factory.py --run",
        "notes": "Ollama → Piper TTS → ComfyUI → n8n content pipeline",
    },
    "music-video-studio": {
        "category": "cli", "tier": "t1",
        "name": "Music Video Studio",
        "path": r"C:\Users\karma\ComfyUI\tools\music_video_studio.py",
        "invocation": "python ComfyUI/tools/music_video_studio.py brainstorm --model ornith --lyrics poem.txt",
        "notes": "10+ subcommands incl. transcribe / analyze-audio / wizard / list-free-models",
    },
    "local-ai-assistant": {
        "category": "cli", "tier": "t1",
        "name": "Local AI Assistant",
        "path": r"C:\Users\karma\ComfyUI\tools\local_ai_assistant.py",
        "invocation": "python ComfyUI/tools/local_ai_assistant.py chat",
        "notes": "Stdlib-only · 8 subcommands · Ollama aliases via MODEL_ALIASES",
    },
    "benchmark-coders": {
        "category": "cli", "tier": "t2",
        "name": "Benchmark Coders",
        "path": r"C:\Users\karma\benchmark_coders.py",
        "invocation": "python benchmark_coders.py --sweep",
        "notes": "Per-model timing/wordcount/charcount · JSONL history at benchmark_coders_results.jsonl",
    },
    "ai-voice-pa": {
        "category": "cli", "tier": "t2",
        "name": "AI Voice PA",
        "path": r"C:\Users\karma\ai_voice_pa.py",
        "invocation": "python ai_voice_pa.py --run --stt cloud --i-have-credentials",
        "notes": "5-intent enum · Rule #8 fence · append-only voice_pa.actions.jsonl",
    },
    "youtube-harvester": {
        "category": "cli", "tier": "t2",
        "name": "YouTube Transcript Harvester",
        "path": r"C:\Users\karma\youtube_transcript_harvest.py",
        "invocation": "python youtube_transcript_harvest.py --video URL --lang en --format srt --run",
        "notes": "Captions-only · Rule #8 fence rigid",
    },
    "opt-a": {
        "category": "factory", "tier": "t2",
        "name": "opt_a — Digital Products (Gumroad)",
        "path": r"C:\Users\karma\SLEEP_TRIPLE\opt_a_digital_factory.py",
        "invocation": "python SLEEP_TRIPLE/opt_a_digital_factory.py --run --publish published",
        "notes": "Ollama(qwen2.5-coder) generators · requires user's Gumroad key",
    },
    "opt-b": {
        "category": "factory", "tier": "t2",
        "name": "opt_b — Faceless YouTube + Affiliate",
        "path": r"C:\Users\karma\SLEEP_TRIPLE\opt_b_faceless_shorts.py",
        "invocation": "python SLEEP_TRIPLE/opt_b_faceless_shorts.py --run --publish",
        "notes": "TTS → ComfyUI → FFmpeg composites → YouTube Data API v3 upload",
    },
    "opt-c": {
        "category": "factory", "tier": "t2",
        "name": "opt_c — Crypto Yield",
        "path": r"C:\Users\karma\SLEEP_TRIPLE\opt_c_crypto_yield.py",
        "invocation": "python SLEEP_TRIPLE/opt_c_crypto_yield.py --run --execute",
        "notes": "Coinspot/Kraken/IR public tickers · 50 bps threshold · capital-protection default",
    },
    "opt-d": {
        "category": "factory", "tier": "t1",
        "name": "opt_d — Alerts fanout",
        "path": r"C:\Users\karma\SLEEP_TRIPLE\opt_d_alerts.py",
        "invocation": "python SLEEP_TRIPLE/opt_d_alerts.py --trigger morning_digest --channel discord",
        "notes": "8-hour audit window · 3-retry exponential backoff · morning digest",
    },
    "opt-e": {
        "category": "factory", "tier": "t3",
        "name": "opt_e — Print-on-Demand",
        "path": r"C:\Users\karma\SLEEP_TRIPLE\opt_e_pod.py",
        "invocation": "python SLEEP_TRIPLE/opt_e_pod.py --run --publish mode",
        "notes": "ComfyUI design · Printful fulfillment · Shopify sync",
    },
    "revenue-generators": {
        "category": "factory", "tier": "t3",
        "name": "REVENUE_GENERATORS suite",
        "path": r"C:\Users\karma\REVENUE_GENERATORS",
        "invocation": "dispatched via AI Army http://127.0.0.1:8001",
        "notes": "6 actions · deploy_revenue / content_factory / saas_launcher / brain_crawler / singularity / self_healing",
    },
    "n8n": {
        "category": "automation", "tier": "t2",
        "name": "n8n Automation",
        "path": r"C:\Users\karma\n8n-automation-stack · 127.0.0.1:5678",
        "invocation": "docker-compose -f n8n-automation-stack/docker-compose.yml up -d",
        "notes": "91+ workflow templates · LUCA avatar generator",
        "health_url": "http://127.0.0.1:5678/healthz",
    },
    "mcp-federation": {
        "category": "automation", "tier": "t3",
        "name": "MCP Federation merger",
        "path": r"C:\Users\karma\MCP_FEDERATION_MERGER.ps1",
        "invocation": "powershell MCP_FEDERATION_MERGER.ps1 --run",
        "notes": "Phase 1: query rows · Phase 2: chunk rows · closed 5-element outcome enum",
    },
    "sleep-orchestrator": {
        "category": "automation", "tier": "t2",
        "name": "SLEEP_TRIPLE orchestrator",
        "path": r"C:\Users\karma\SLEEP_TRIPLE\sleep_orchestrator.py",
        "invocation": "python SLEEP_TRIPLE/sleep_orchestrator.py --force-window",
        "notes": "23:00-07:00 nightly + 07:00 morning digest + Sun weekly rollup",
    },
    "recovery-suite": {
        "category": "mobile", "tier": "t2",
        "name": "Recovery Suite (12-position menu)",
        "path": r"C:\Users\karma\recovery.bat → COMPLETED_PROJECTS\mobile_backup\RECOVERY_SUITE.bat",
        "invocation": r"C:\Users\karma\recovery.bat",
        "notes": "Android unlock GUI + iPhone suite + Oppo specialist + 4 Flask reference apps · 15/15 PASS tests",
    },
    "sunshine-moonlight": {
        "category": "mobile", "tier": "t2",
        "name": "Sunshine + Moonlight",
        "path": r"C:\Program Files\Sunshine\ (if installed)",
        "invocation": "see SUNSHINE_MOONLIGHT_SETUP.md",
        "notes": "GPU-accelerated remote-desktop · documented, NOT auto-installed",
    },
    "ai-tools-dashboard": {
        "category": "dashboards", "tier": "t1",
        "name": "AI Tools Dashboard",
        "path": r"C:\Users\karma\AI_TOOLS_DASHBOARD.html",
        "invocation": "open AI_TOOLS_DASHBOARD.html  (or start \"\" AI_TOOLS_DASHBOARD.html)",
        "notes": "All tools in one HTML page",
    },
    "ultimate-empire": {
        "category": "dashboards", "tier": "t1",
        "name": "Ultimate Empire V2 Dashboard",
        "path": r"C:\Users\karma\ULTIMATE_AI_EMPIRE_ENHANCED_DASHBOARD_V2.html",
        "invocation": "open ULTIMATE_AI_EMPIRE_ENHANCED_DASHBOARD_V2.html",
        "notes": "6 Quick Tools tiles (incl. Mobile Recovery)",
    },
    "revenue-dashboard": {
        "category": "dashboards", "tier": "t1",
        "name": "Revenue Dashboard (Live)",
        "path": "127.0.0.1:3144 · SLEEP_TRIPLE/dashboard_server.py",
        "invocation": "open http://127.0.0.1:3144",
        "notes": "Real-time revenue tracking",
        "health_url": "http://127.0.0.1:3144/healthz",
    },
    "war-room": {
        "category": "dashboards", "tier": "t1",
        "name": "WAR_ROOM CLI dispatcher",
        "path": r"C:\Users\karma\war_room.py",
        "invocation": "python war_room.py status                   # operator HUD overview;  war_room.py doctor / trend-compare / launch-trend for cumulative health",
        "notes": "7 in-HTML-surfaces (status/action/recon/evidence/comms/reference/mobile) + 16 CLI subcommands incl. the cont.21 doctor family: snapshot-doctor (write point-in-time), diff-doctor (compare 2 snaps), trend-doctor / trend-compare (window aggregation / RATE-based today-vs-past-week), launch-trend (1-click wrapper). See WAR_ROOM.md runbook for examples. CLI has no HTTP /health endpoint; use `python war_room.py health` to probe the 5 local services.",
    },
    # Audit Family
    "reality-vs-claim": {
        "category": "audit", "tier": "t2",
        "name": "REALITY_VS_CLAIM_AUDIT",
        "path": r"C:\Users\karma\REALITY_VS_CLAIM_AUDIT.py",
        "invocation": "python REALITY_VS_CLAIM_AUDIT.py --run --emit-summary",
        "notes": "Cross-checks master-index headlines vs on-disk reality",
    },
    "index-delta": {
        "category": "audit", "tier": "t2",
        "name": "INDEX_DELTA_SCANNER",
        "path": r"C:\Users\karma\INDEX_DELTA_SCANNER.py",
        "invocation": "python INDEX_DELTA_SCANNER.py --run",
        "notes": "Top-level (1-deep) entry divergence",
    },
    "index-delta-recursive": {
        "category": "audit", "tier": "t2",
        "name": "INDEX_DELTA_RECURSIVE",
        "path": r"C:\Users\karma\INDEX_DELTA_RECURSIVE.py",
        "invocation": "python INDEX_DELTA_RECURSIVE.py --run --max-depth 2",
        "notes": "Where-inside the disk tree the divergence happens",
    },
    "master-reconciler": {
        "category": "audit", "tier": "t2",
        "name": "MASTER_INDEX_RECONCILER",
        "path": r"C:\Users\karma\MASTER_INDEX_RECONCILER.py",
        "invocation": "python MASTER_INDEX_RECONCILER.py --run --emit-summary",
        "notes": "Aggregates 3 source logs into MASTER_INDEX_RECONCILED.md",
    },
    "gal-integrity": {
        "category": "audit", "tier": "t2",
        "name": "GAL_INTEGRITY_VERIFY",
        "path": r"C:\Users\karma\GAL_INTEGRITY_VERIFY.py",
        "invocation": "python GAL_INTEGRITY_VERIFY.py --run  [--header-only]",
        "notes": "x:\\AETHER_CORE_SYSTEM archives · 7-element status enum",
    },
    "cross-aggregator": {
        "category": "audit", "tier": "t2",
        "name": "CROSS_TOOL_AGGREGATOR",
        "path": r"C:\Users\karma\CROSS_TOOL_AGGREGATOR.py",
        "invocation": "python CROSS_TOOL_AGGREGATOR.py --run --emit-summary",
        "notes": "Top-of-family digest for the 5-log audit family",
    },
    "dotdir-catalog": {
        "category": "audit", "tier": "t2",
        "name": "DOTDIR_CATALOG_RUN",
        "path": r"C:\Users\karma\DOTDIR_CATARUN.py",
        "invocation": "python DOTDIR_CATALOG_RUN.py --run --emit-summary",
        "notes": "81+ workspace-hygiene names · emits DOTDIR_CATALOG.md",
    },
    # ============================================================
    # Wave-2 extensions (2026-07-09) — closes gap with AI_AND_IT_TOOLKIT.{md,html}.
    # These 22 entries bring REGISTRY to parity with the operator-facing docs
    # (every tool advertised in either the Markdown or HTML dashboard is
    # resolvable via `python tool_kit.py info <slug>`).
    # ============================================================

    # --- runtime (2 new) ---
    "lm-studio": {
        "category": "runtime", "tier": "t3",
        "name": "LM Studio",
        "path": "http://localhost:1234  (OpenAI-compatible endpoint)",
        "invocation": "start LM Studio  # then use OpenAI-compatible chat",
        "notes": "Alt local LLM serving · install-on-demand",
        "health_url": "http://localhost:1234/v1/models",
    },
    "llama-cpp": {
        "category": "runtime", "tier": "t4",
        "name": "llama.cpp / vLLM",
        "path": "(not installed)",
        "invocation": "n/a",
        "notes": "Aspirational; use Ollama until proven better",
    },

    # --- cloud (1 new) ---
    "anthropic-openai": {
        "category": "cloud", "tier": "t4",
        "name": "Anthropic / OpenAI direct",
        "path": "(no direct key, per CLAUDE.md)",
        "invocation": "n/a — route via OpenRouter instead",
        "notes": "Direct provider keys deliberately not set; use OpenRouter for all AI",
    },

    # --- agents (1 new) ---
    "voice-pa-bridge": {
        "category": "agents", "tier": "t3",
        "name": "Voice PA ↔ Footclan bridge",
        "path": r"C:\Users\karma\voice_pa_bridge.py",
        "invocation": "python voice_pa_bridge.py --dry-run  (else --run)",
        "notes": "Cross-system correlator by iso-minute prefix match · append-only bridge log",
    },

    # --- cli (1 new) ---
    "mcp-host-connector": {
        "category": "cli", "tier": "t3",
        "name": "MCP Host Connector",
        "path": r"C:\Users\karma\MCP_HOST_CONNECTOR.ps1",
        "invocation": "powershell MCP_HOST_CONNECTOR.ps1",
        "notes": "First concrete MCP adapter · bridges MCP host to family of MCP servers",
    },

    # --- automation (2 new) ---
    "self-healing-daemon": {
        "category": "automation", "tier": "t3",
        "name": "AI Self-Healing Daemon",
        "path": r"C:\Users\karma\REVENUE_GENERATORS\SELF_HEALING_DAEMON.py",
        "invocation": "python SELF_HEALING_DAEMON.py  # standalone runner",
        "notes": "Service health checks · emits plan_heal (renamed from attempt_heal)",
    },
    "task-scheduler-installer": {
        "category": "automation", "tier": "t2",
        "name": "Task-scheduler installer",
        "path": r"C:\Users\karma\install_monitor_scheduler.bat",
        "invocation": "install_monitor_scheduler.bat  [--dry-run|--uninstall]",
        "notes": "Auto-elevates via PowerShell UAC · digit-validates MONITOR_INTERVAL · installs SLEEP_CASH\\Monitor + ProbeAll",
    },

    # --- dev (new category — 7 tools) ---
    "python-venvs": {
        "category": "dev", "tier": "t1",
        "name": "Python venvs (uv-managed)",
        "path": r"C:\Users\karma\python\.venv  · SLEEP_CASH_API  · per-project",
        "invocation": r"uv sync  (or: python -m venv .venv && uv pip install -r requirements.txt)",
        "notes": "3.12 + 3.13 mixed · uv is canonical operator action · `&&` requires PowerShell 7+ / bash; win-PS 5.x: split into 2 cmds",
    },
    "uv": {
        "category": "dev", "tier": "t1",
        "name": "uv (package manager)",
        "path": r"C:\Users\karma\.local\bin\uv",
        "invocation": "uv <cmd>  # e.g. uv sync / uv add / uv run",
        "notes": "Fast resolver · 10-100x faster than pip · drop-in for pip in pyproject.toml projects",
    },
    "node-vite": {
        "category": "dev", "tier": "t2",
        "name": "Node.js + Vite",
        "path": r"C:\Users\karma\archon-ui-main  · Vite proxy :3737 → :8181",
        "invocation": "npm run dev  (or: vite)",
        "notes": "React + TypeScript + TailwindCSS frontend",
        "health_url": "http://localhost:3737",
    },
    "docker": {
        "category": "dev", "tier": "t2",
        "name": "Docker / docker-compose",
        "path": r"C:\Users\karma\n8n-automation-stack  · Archon stack  · multi-archon-compose",
        "invocation": "docker compose -f <file> up -d",
        "notes": "Compose orchestration under bare-Windows runners (archon_orchestrator.py)",
    },
    "powershell": {
        "category": "dev", "tier": "t1",
        "name": "PowerShell",
        "path": "Windows-native (built-in)",
        "invocation": "powershell -NoProfile -Command \"...\"",
        "notes": "Required for UAC elevation of .bat installers · digit-validates env vars",
    },
    "pyenv": {
        "category": "dev", "tier": "t3",
        "name": "pyenv",
        "path": r"C:\Users\karma\.pyenv",
        "invocation": "pyenv shell 3.13  (or: pyenv local 3.12)",
        "notes": "Per-project Python version pick · currently 3.13 default",
    },
    "npm-bun": {
        "category": "dev", "tier": "t3",
        "name": "npm / pnpm / bun",
        "path": r"various · bun at C:\Users\karma\.bun",
        "invocation": "bun <cmd>  # fastest for Karma's local scripts",
        "notes": "Bun fastest for Karma's local scripts · use npm only when lockfile-required",
    },

    # --- mobile (2 new) ---
    "scrcpy": {
        "category": "mobile", "tier": "t4",
        "name": "scrcpy",
        "path": "(uninstalled — tools/scrcpy/ empty)",
        "invocation": "choco install scrcpy adb",
        "notes": "Android screen-over-USB · install when needed",
    },
    "libimobiledevice": {
        "category": "mobile", "tier": "t4",
        "name": "libimobiledevice",
        "path": "(uninstalled)",
        "invocation": "choco install libimobiledevice",
        "notes": "iPhone plumbing for iphone_recovery.py · install when needed",
    },

    # --- dashboards (3 new) ---
    "master-command-center": {
        "category": "dashboards", "tier": "t1",
        "name": "Master Command Center",
        "path": r"C:\Users\karma\UNIFIED_COMMAND_CENTER.html + master_dashboard_hub.html",
        "invocation": "open UNIFIED_COMMAND_CENTER.html",
        "notes": "Top-level hub · integrates all sub-dashboards",
    },
    "system-status-dashboard": {
        "category": "dashboards", "tier": "t2",
        "name": "System Status Dashboard",
        "path": r"C:\Users\karma\dashback26\system_status_dashboard.html",
        "invocation": "open system_status_dashboard.html",
        "notes": "Service health summary · 5-minute refresh",
    },
    "bookmark-manager": {
        "category": "dashboards", "tier": "t2",
        "name": "Bookmark Manager Pro",
        "path": r"C:\Users\karma\BOOKMARK_MANAGER_PRO_INDEX.md  (16 stages)  · enhanced_dashboard.html",
        "invocation": "open enhanced_dashboard.html",
        "notes": "7,685 bookmarks · 17 categories · 100% test coverage",
    },

    # --- audit (3 new) ---
    "append-only-hygiene-runner": {
        "category": "audit", "tier": "t3",
        "name": "append-only hygiene runner",
        "path": r"C:\Users\karma\append_only_hygiene_runner.py",
        "invocation": "python append_only_hygiene_runner.py --run",
        "notes": "12-log closed list · size + ts monotonic check",
    },
    "backup-audit-run": {
        "category": "audit", "tier": "t3",
        "name": "BACKUP_AUDIT_RUN",
        "path": r"C:\Users\karma\BACKUP_AUDIT_RUN.ps1",
        "invocation": "powershell BACKUP_AUDIT_RUN.ps1 -Run",
        "notes": "Reads BACKUP_MANIFEST.json · 6-element status enum",
    },
    "env-audit-run": {
        "category": "audit", "tier": "t3",
        "name": "ENV_AUDIT_RUN",
        "path": r"C:\Users\karma\ENV_AUDIT_RUN.ps1",
        "invocation": "powershell ENV_AUDIT_RUN.ps1 -Run",
        "notes": "5-element ENV_KEY_STATUS_ENUM · Rule #8 fence rigid",
    },
    # ============================================================
    # Wave-3 extensions (2026-07-09) — OS-installed apps on Karma's PC.
    # Discovery mode: scan_pc_apps.ps1 enumerated 453 unique entries
    # (Registry HKLM 64/32 + HKCU + AppX Store). Operators curated the
    # top ~44 apps that Karma actually uses into two new closed-list
    # categories: `system` (runtimes + system utilities) and
    # `os-apps` (user-facing apps).
    # ============================================================

    # --- system (runtimes + utilities; 18 new) ---
    "windows-terminal": {
        "category": "system", "tier": "t1",
        "name": "Windows Terminal",
        "path": "Microsoft Store (AppX)",
        "invocation": "wt",
        "notes": "Primary CLI host · tabs / panes / Quake mode",
    },
    "git": {
        "category": "system", "tier": "t1",
        "name": "Git",
        "path": r"C:\Program Files\Git",
        "invocation": "C:\Program Files\Git\bin\git.exe  (or: git <cmd> from any shell)",
        "notes": "v2.48.1 per PC scan · msys2 + POSIX utilities bundled",
    },
    "github-cli": {
        "category": "system", "tier": "t1",
        "name": "GitHub CLI (gh)",
        "path": "(scan: HKLM 64; install path TBD by `gh --version`)",
        "invocation": "gh <cmd>  # e.g. gh repo view; gh pr create",
        "notes": "v2.75.0 per PC scan · authenticated for github.com",
    },
    "aws-cli": {
        "category": "system", "tier": "t2",
        "name": "AWS CLI v2",
        "path": "(scan: HKLM 64; `aws --version` resolves)",
        "invocation": "aws <cmd>  # configure SSO first: aws sso login",
        "notes": "v2.27.50 · SSO + IAM Identity Center friendly",
    },
    "gcloud-sdk": {
        "category": "system", "tier": "t2",
        "name": "Google Cloud SDK",
        "path": r"C:\Program Files (x86)\Google\Cloud SDK",
        "invocation": "gcloud <cmd>  # gcloud init for first auth",
        "notes": "Includes gsutil + bq + kubectl",
    },
    "azure-cli": {
        "category": "system", "tier": "t2",
        "name": "Azure CLI",
        "path": "(install via `winget install Microsoft.AzureCLI`)",
        "invocation": "az <cmd>  # az login first",
        "notes": "Cross-platform · MSI install available",
    },
    "java-jdk": {
        "category": "system", "tier": "t2",
        "name": "Java JDK",
        "path": r"C:\Program Files\Eclipse Adoptium  (or C:\Program Files\Java)",
        "invocation": "java -version  # check JAVA_HOME",
        "notes": "Verify with `java -version`; JAVA_HOME for build tools",
    },
    "python-system": {
        "category": "system", "tier": "t1",
        "name": "Python (system install)",
        "path": r"C:\Python313 (or C:\Python312)  · C:\Users\karma\AppData\Local\Programs\Python",
        "invocation": "python --version  # py launcher for version switching",
        "notes": "Companion to uv-managed venvs · use uv for project-local Python",
    },
    "node-system": {
        "category": "system", "tier": "t2",
        "name": "Node.js (system install)",
        "path": r"C:\Program Files\nodejs (per scan)",
        "invocation": "node --version; npm --version",
        "notes": "Use Vue/React/etc via npx; project-local preferred via package.json",
    },
    "rust-toolchain": {
        "category": "system", "tier": "t3",
        "name": "Rust toolchain",
        "path": r"C:\Users\karma\.cargo\bin",
        "invocation": "rustc --version; cargo --version",
        "notes": "Install via rustup-init.exe",
    },
    "go-runtime": {
        "category": "system", "tier": "t3",
        "name": "Go runtime",
        "path": r"C:\Program Files\Go\bin (or custom)",
        "invocation": "go version",
        "notes": "11 hits in PC scan (likely Go + embedded tools)",
    },
    ".net-runtime": {
        "category": "system", "tier": "t2",
        "name": ".NET Runtime",
        "path": r"C:\Program Files\dotnet",
        "invocation": "dotnet --list-runtimes",
        "notes": "10 entries in PC scan (Desktop + ASP.NET + EF Core etc)",
    },
    "antigravity-ide": {
        "category": "system", "tier": "t2",
        "name": "Antigravity (Google IDE)",
        "path": r"C:\Users\karma\AppData\Local\Programs\Antigravity IDE",
        "invocation": "start \"\" \"Antigravity IDE.exe\"",
        "notes": "Google's 2026 'anti-gravity' IDE · v2.1.4 / v2.1.1 user install · notable Gemini integration",
    },
    "vs-code-system": {
        "category": "system", "tier": "t1",
        "name": "VS Code (system install)",
        "path": r"C:\Users\karma\AppData\Local\Programs\Microsoft VS Code",
        "invocation": "code .",
        "notes": "Companion to Antigravity · CLI `code` registered for shells",
    },
    "visual-studio": {
        "category": "system", "tier": "t2",
        "name": "Visual Studio 2022",
        "path": r"C:\Program Files\Microsoft Visual Studio\2022",
        "invocation": "start \"\" \"C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\Common7\\IDE\\devenv.exe\"",
        "notes": "If installed: enterprise-grade .NET/C++ IDE",
    },
    "windows-powertoys": {
        "category": "system", "tier": "t2",
        "name": "PowerToys",
        "path": "Microsoft Store (AppX)",
        "invocation": "start \"\" \"PowerToys.exe\"",
        "notes": "FancyZones + PowerRename + Keyboard Manager + AlwaysOnTop",
    },
    "everything-search": {
        "category": "system", "tier": "t2",
        "name": "Everything (voidtools)",
        "path": r"C:\Program Files\Everything",
        "invocation": "\"C:\\Program Files\\Everything\\Everything.exe\" -search <query>",
        "notes": "Instant filename search across NTFS · CLI -search mode is script-friendly",
    },
    "rufus": {
        "category": "system", "tier": "t3",
        "name": "Rufus (USB imager)",
        "path": r"C:\Program Files\Rufus",
        "invocation": "start \"\" \"C:\\Program Files\\Rufus\\rufus.exe\"",
        "notes": "Bootable USB for Linux/Windows · portable, no install",
    },

    # --- os-apps (user-facing apps; 26 new) ---
    "chrome": {
        "category": "os-apps", "tier": "t1",
        "name": "Google Chrome",
        "path": r"C:\Program Files\Google\Chrome\Application (per scan)",
        "invocation": "start \"\" \"chrome\"  (or: chrome.exe)",
        "notes": "v149.0.7827.201 per scan · primary browser",
    },
    "ms-edge": {
        "category": "os-apps", "tier": "t1",
        "name": "Microsoft Edge",
        "path": r"C:\Program Files (x86)\Microsoft\Edge\Application",
        "invocation": "start \"\" msedge",
        "notes": "5 hits in PC scan (Edge + WebView + update stacks) · built-in to Win 11",
    },
    "firefox": {
        "category": "os-apps", "tier": "t2",
        "name": "Mozilla Firefox",
        "path": r"C:\Program Files\Mozilla Firefox",
        "invocation": "start \"\" firefox",
        "notes": "Alt browser · 1 hit in PC scan",
    },
    "github-desktop": {
        "category": "os-apps", "tier": "t1",
        "name": "GitHub Desktop",
        "path": r"C:\Users\karma\AppData\Local\GitHubDesktop",
        "invocation": "start \"\" \"GitHub Desktop.exe\"",
        "notes": "v3.5.3 per scan · git GUI for non-CLI work",
    },
    "docker-desktop": {
        "category": "os-apps", "tier": "t1",
        "name": "Docker Desktop",
        "path": r"C:\Program Files\Docker\Docker",
        "invocation": "start \"\" \"Docker Desktop.exe\"",
        "notes": "v4.81.0 per scan · WSL2 backend · Docker Engine + Compose",
    },
    "slack": {
        "category": "os-apps", "tier": "t2",
        "name": "Slack",
        "path": r"C:\Users\karma\AppData\Local\slack (typical)",
        "invocation": "start \"\" slack",
        "notes": "Daily team comms",
    },
    "discord": {
        "category": "os-apps", "tier": "t2",
        "name": "Discord",
        "path": r"C:\Users\karma\AppData\Local\Discord (typical)",
        "invocation": "start \"\" discord",
        "notes": "Voice channels · community workspaces",
    },
    "telegram": {
        "category": "os-apps", "tier": "t2",
        "name": "Telegram Desktop",
        "path": r"C:\Users\karma\AppData\Roaming\Telegram Desktop",
        "invocation": "start \"\" \"Telegram.exe\"",
        "notes": "1 hit in PC scan · E2E DMs + channel reads",
    },
    "spotify": {
        "category": "os-apps", "tier": "t2",
        "name": "Spotify",
        "path": r"C:\Users\karma\AppData\Roaming\Spotify",
        "invocation": "start \"\" spotify",
        "notes": "Focus music · can run headless: `spotify --minimized`",
    },
    "vlc": {
        "category": "os-apps", "tier": "t2",
        "name": "VLC media player",
        "path": r"C:\Program Files\VideoLAN\VLC (per scan)",
        "invocation": "start \"\" vlc  (or: vlc <file>)",
        "notes": "1 hit in PC scan · universal codec playback",
    },
    "handbrake": {
        "category": "os-apps", "tier": "t3",
        "name": "HandBrake",
        "path": r"C:\Program Files\HandBrake",
        "invocation": "start \"\" \"HandBrake.exe\"",
        "notes": "Video transcoder · FFmpeg UI for video compression",
    },
    "obs-studio": {
        "category": "os-apps", "tier": "t3",
        "name": "OBS Studio",
        "path": r"C:\Program Files\obs-studio\bin\64bit",
        "invocation": "start \"\" \"C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe\"",
        "notes": "Streaming + recording · virtual camera",
    },
    "capcut": {
        "category": "os-apps", "tier": "t3",
        "name": "CapCut",
        "path": r"C:\Users\karma\AppData\Local\CapCut (per scan)",
        "invocation": "start \"\" \"CapCut.exe\"",
        "notes": "v8.8.0.3774 · Bytedance short-form video editor",
    },
    "davinci-resolve": {
        "category": "os-apps", "tier": "t3",
        "name": "DaVinci Resolve",
        "path": r"C:\Program Files\Blackmagic Design\DaVinci Resolve",
        "invocation": "start \"\" \"Resolve.exe\"",
        "notes": "Color grading + NLE · free tier very capable",
    },
    "blackmagic-raw": {
        "category": "os-apps", "tier": "t3",
        "name": "Blackmagic RAW",
        "path": "(codec pack; no UI)",
        "invocation": "n/a — system-wide BRAW codec installer",
        "notes": "Codec pack for .braw files via DaVinci Resolve / Premiere",
    },
    "cloud-drive-google": {
        "category": "os-apps", "tier": "t2",
        "name": "Google Drive for desktop",
        "path": r"C:\Program Files\Google\Drive File Stream (per scan)",
        "invocation": "start \"\" \"GoogleDriveFS.exe\"",
        "notes": "v127.0.1.0 per scan · Drive + Backup sync to G:\\My Drive",
    },
    "dropbox": {
        "category": "os-apps", "tier": "t2",
        "name": "Dropbox",
        "path": r"C:\Users\karma\AppData\Roaming\Dropbox (typical)",
        "invocation": "start \"\" dropbox",
        "notes": "1 hit in PC scan (Dropbox Redeem Launcher; client install path varies)",
    },
    "foxit-pdf": {
        "category": "os-apps", "tier": "t2",
        "name": "Foxit PDF Reader",
        "path": r"C:\Program Files (x86)\Foxit Software\Foxit PDF Reader (per scan)",
        "invocation": "start \"\" \"Foxit PDF Reader.exe\"",
        "notes": "v2024.4.0.27683 per scan · lighter than Adobe",
    },
    "cute-pdf-writer": {
        "category": "os-apps", "tier": "t3",
        "name": "CutePDF Writer",
        "path": r"C:\Program Files (x86)\CutePDF Writer (per scan)",
        "invocation": "print-to-printer → 'CutePDF Writer' virtual printer",
        "notes": "v4.0 per scan · printer-as-PDF · lightweight",
    },
    "notepad-plus-plus": {
        "category": "os-apps", "tier": "t2",
        "name": "Notepad++",
        "path": r"C:\Program Files\Notepad++",
        "invocation": "start \"\" notepad++  (or via right-click 'Edit with Notepad++')",
        "notes": "Lightweight code editor · 3 Notepad hits in PC scan incl N++ + plugins",
    },
    "7zip": {
        "category": "os-apps", "tier": "t2",
        "name": "7-Zip",
        "path": r"C:\Program Files\7-Zip",
        "invocation": "7zFM  (or: 7z a archive.7z <files>)",
        "notes": "File archiver · CLI 7z supports many formats · use 7z a archive.7z files/glob",
    },
    "winrar": {
        "category": "os-apps", "tier": "t2",
        "name": "WinRAR",
        "path": r"C:\Program Files\WinRAR",
        "invocation": "start \"\" \"WinRAR.exe\"",
        "notes": "RAR + ZIP · 2 hits in PC scan (x64 + x86)",
    },
    "cpu-z": {
        "category": "os-apps", "tier": "t3",
        "name": "CPU-Z",
        "path": r"C:\Program Files\CPUID\CPU-Z (per scan)",
        "invocation": "start \"\" \"cpuz.exe\"",
        "notes": "v2.15 per scan · HW info: CPU + mobo + RAM SPD",
    },
    "aida64-extreme": {
        "category": "os-apps", "tier": "t3",
        "name": "AIDA64 Extreme",
        "path": r"C:\Program Files (x86)\FinalWire\AIDA64 Extreme (per scan)",
        "invocation": "start \"\" \"aida64.exe\"",
        "notes": "v7.50 per scan · deeper HW + sensor logging than CPU-Z",
    },
    "deskflow": {
        "category": "os-apps", "tier": "t3",
        "name": "Deskflow",
        "path": r"C:\Program Files\Deskflow (per scan)",
        "invocation": "start \"\" deskflow",
        "notes": "v1.23.0.0 per scan · cross-machine keyboard/mouse sharing (Barrier fork)",
    },
    "icloud-bonjour": {
        "category": "os-apps", "tier": "t4",
        "name": "iCloud / Bonjour",
        "path": r"C:\Program Files (x86)\Bonjour (per scan)",
        "invocation": "(background service)",
        "notes": "Apple networking helper · required for iTunes / iPhone wiring",
    },

    # ============================================================
    # Wave-4 extensions (2026-07-09) — comprehensive phone/tablet tooling.
    # 12 new mobile entries (mobile category 4 -> 16 total).
    # Curation draws on Karma's 20+ yrs IT + active FB anti-scam work
    # (signature case: Brendan Foots). Builds out the APK/lib inspection
    # chain (apktool + jadx + frida + magisk) for analyzing user-submitted
    # scammer-evidence APKs, plus daily-driver transport (adb/fastboot).
    # ============================================================

    # --- mobile (12 new) ---
    "adb": {
        "category": "mobile", "tier": "t1",
        "name": "Android Debug Bridge (adb)",
        "path": r"C:\Program Files\Google\Android\platform-tools\adb.exe  (or system PATH)",
        "invocation": "adb devices  # list;  adb install <apk>;  adb shell  # enter phone shell",
        "notes": "Core daily-driver for ALL Android ops · ships inside platform-tools ZIP · USB + wireless (adb pair IP:PORT)",
    },
    "fastboot": {
        "category": "mobile", "tier": "t1",
        "name": "Fastboot (bootloader/flash)",
        "path": r"C:\Program Files\Google\Android\platform-tools\fastboot.exe  (or system PATH)",
        "invocation": "fastboot devices  # list flash-mode;  fastboot flash <partition> <img>;  fastboot oem unlock",
        "notes": "Companion to adb · comes with platform-tools · required for bootloader unlock / recovery flash / EDL",
    },
    "platform-tools": {
        "category": "mobile", "tier": "t2",
        "name": "Google Android platform-tools (ZIP)",
        "path": r"C:\Program Files\Google\Android\platform-tools  (or system PATH)",
        "invocation": "winget install Google.PlatformTools  # OR: zip from developer.android.com",
        "notes": "Bundle: adb + fastboot + mDNS responder · ~7 MB · reinstall once per major Android SDK bump",
    },
    "apktool": {
        "category": "mobile", "tier": "t2",
        "name": "APKTool (reverse-engineer APK)",
        "path": r"C:\Program Files\apktool\apktool.jar  (or system PATH)",
        "invocation": "java -jar apktool.jar d -o out_dir foo.apk  # decompile;  apktool b -o new.apk out_dir  # rebuild",
        "notes": "Reverse-engineer suspicious APKs · FB-evidence use: disassemble scammer-sent apps submitted as proof · supports smali + 9patch",
    },
    "jadx": {
        "category": "mobile", "tier": "t2",
        "name": "jadx (DEX/Java decompiler)",
        "path": r"C:\Program Files\jadx\bin\jadx.exe  (or system PATH)",
        "invocation": "jadx -d out_dir foo.apk  # decompile;  jadx-gui foo.apk  # GUI alternative",
        "notes": "Companion to apktool · inspect classes/methods/strings of suspicious APKs · supports Dalvik + Java 17 bytecode",
    },
    "frida": {
        "category": "mobile", "tier": "t3",
        "name": "Frida (runtime instrumentation)",
        "path": r"C:\Users\karma\AppData\Local\Programs\Frida  (or pip install frida-tools)",
        "invocation": "pip install frida-tools  # then: frida -U -l script.js com.target.app  # hook runtime",
        "notes": "Runtime API-hook tool · cross-platform (Android + iOS) · FB-evidence use: trace suspicious app at runtime to confirm behavior",
    },
    "magisk": {
        "category": "mobile", "tier": "t3",
        "name": "Magisk (root framework + Magisk Manager)",
        "path": "(phone-side install; Magisk Manager from F-Droid / GitHub releases)",
        "invocation": "adb push magisk.apk /data/local/tmp  # NOT /sdcard (Android 11+ write-restricted); then patch boot.img via Magisk Manager app",
        "notes": "Systemless root · MagiskHide + Zygisk · use-case: rooted-test scenarios, hidden env for analyzing malware",
    },
    "android-studio": {
        "category": "mobile", "tier": "t3",
        "name": "Android Studio (Google IDE)",
        "path": r"C:\Program Files\Android\Android Studio\bin\studio64.exe  (or system PATH)",
        "invocation": 'start "" "Android Studio"  # OR: studio64.exe --launcher-mode single',
        "notes": "Full APK dev environment · emulator · profiler · install-on-demand; ~5 GB",
    },
    "libimobile-cli": {
        "category": "mobile", "tier": "t2",
        "name": "libimobiledevice CLI (iPhone)",
        "path": r"C:\Program Files\libimobiledevice\bin  (or system PATH)",
        "invocation": "idevice_id -l  # list UDIDs;  idevicesyslog;  idevicebackup2 backup <dir>;  idevicescreenshot",
        "notes": "libimobiledevice Windows builds · CLI surface for ALL iOS plumbing · FB-evidence use: pull iOS logs / screenshots",
    },
    "imazing": {
        "category": "mobile", "tier": "t3",
        "name": "iMazing (iOS backup/transfer GUI)",
        "path": r"C:\Program Files\iMazing  (or typical install)",
        "invocation": 'start "" "iMazing.exe"',
        "notes": "GUI iPhone backup/transfer · easier than idevicebackup2 for non-cli · supports encrypted backups; useful when iTunes is misbehaving",
    },
    "wsa": {
        "category": "mobile", "tier": "t3",
        "name": "Windows Subsystem for Android (WSA)",
        "path": "Microsoft Store: Amazon Appstore app (ProductId=9p3395vx91nr; the only surviving WSA front door)",
        "invocation": 'start ms-windows-store://pdp/?ProductId=9p3395vx91nr  # Amazon Appstore install; WSA itself discontinued',
        "notes": "DEPRECATED: WSA itself was discontinued by Microsoft Sept 2024. Amazon Appstore install path remains valid (ProductId above); adb localhost:58526 still works for installed Amazon apps. For serious Android-on-PC use, BlueStacks / LDPlayer are the current operator-grade alternatives",
    },
    "mtk-client": {
        "category": "mobile", "tier": "t4",
        "name": "MTKClient (MediaTek flash utility)",
        "path": r"C:\Program Files\mtkclient\mtk.py  (git clone https://github.com/bkerler/mtkclient + venv; install-on-demand only)",
        "invocation": 'cd "C:\Program Files\mtkclient" && .venv\Scripts\python.exe mtk.py  # CLI modes: brom, payload, da',
        "notes": "Niche: bypass-auth + flash MediaTek chips · Karma-side: only if MTK device arrives for FB-evidence work; never auto-installed",
    },
}


# ============================================================
# Schema validation — runs at import time so bad entries crash early
# (not mid-subcommand when KeyError would surprise the user).
# Rule: every entry MUST have these keys + values drawn from closed lists.
# ============================================================

REQUIRED_KEYS = frozenset({"name", "category", "tier", "path", "invocation", "notes"})

def _validate_registry() -> None:
    """Assert REGISTRY schema at import time. Raises AssertionError on drift.

    References CATEGORIES + TIERS module-globals — caller MUST invoke this
    function AFTER those are defined (we call it at the bottom of the
    Display-helpers section below).
    """
    bad: List[str] = []
    for slug, entry in REGISTRY.items():
        missing = REQUIRED_KEYS - set(entry.keys())
        if missing:
            bad.append(f"  {slug}: missing keys {sorted(missing)}")
            continue
        if entry["category"] not in CATEGORIES:
            bad.append(f"  {slug}: category={entry['category']!r} not in closed-list {CATEGORIES}")
        if entry["tier"] not in TIERS:
            bad.append(f"  {slug}: tier={entry['tier']!r} not in closed-list {TIERS}")
    if bad:
        raise AssertionError("REGISTRY schema validation failed:\n" + "\n".join(bad))

# ============================================================
# Display helpers
# ============================================================

CATEGORIES = ["runtime", "cloud", "agents", "cli", "factory", "automation", "dev", "mobile", "dashboards", "audit", "os-apps", "system"]
TIERS = ["t1", "t2", "t3", "t4"]
TIER_LABELS = {"t1": "T1 Daily", "t2": "T2 Weekly", "t3": "T3 Monthly", "t4": "T4 Shelf"}

def tier_label(t: str) -> str:
    return TIER_LABELS.get(t, t.upper())

# Run schema validation NOW — CATEGORIES + TIERS are defined above; this is
# the earliest safe point. Will raise AssertionError on drift; exits the
# import if drift exists (loud failure per CLAUDE.md "fail fast and loud").
_validate_registry()

def _w(s: str, n: int) -> str:
    """Pad/truncate to n chars wide (terminal-table-friendly)."""
    return (s[: n - 1] + "…") if len(s) > n else s.ljust(n)

def print_table(tools: List[Tuple[str, Dict]]) -> None:
    """Print tools as a compact 4-col table: tier | name | path | invocation."""
    rows = []
    for key, t in tools:
        rows.append((tier_label(t["tier"]), t["name"], _w(t["path"], 50), _w(t["invocation"], 60)))
    # Header
    print(f"  {'TIER':<11} {'NAME':<38} {'PATH':<50} {'INVOCATION':<60}")
    print("  " + "-" * 159)
    for r in rows:
        print(f"  {r[0]:<11} {r[1]:<38} {r[2]:<50} {r[3]:<60}")
    print(f"\n  Total: {len(tools)} tools")


# ============================================================
# Subcommands
# ============================================================

def cmd_list(args: argparse.Namespace) -> int:
    """List tools; --category / --tier filters available."""
    filt_cat = args.category
    filt_tier = args.tier
    entries = list(REGISTRY.items())
    if filt_cat:
        if filt_cat not in CATEGORIES:
            print(f"[ERR] unknown category: {filt_cat}")
            print(f"      available: {', '.join(CATEGORIES)}")
            return 1
        entries = [e for e in entries if e[1]["category"] == filt_cat]
    if filt_tier:
        if filt_tier not in TIERS:
            print(f"[ERR] unknown tier: {filt_tier}  (use t1 / t2 / t3 / t4)")
            return 1
        entries = [e for e in entries if e[1]["tier"] == filt_tier]
    if not entries:
        print("[INFO] no tools match the filters")
        return 0
    # Sort by tier then name
    entries.sort(key=lambda kv: (TIERS.index(kv[1]["tier"]) if kv[1]["tier"] in TIERS else 99, kv[1]["name"]))
    print_table(entries)
    return 0

def cmd_categories(args: argparse.Namespace) -> int:
    """Print categories + tool counts; warn on out-of-list categories (schema drift)."""
    counts: Dict[str, int] = {c: 0 for c in CATEGORIES}
    dropped: List = []  # list of (slug, observed_category)
    for slug, t in REGISTRY.items():
        if t["category"] in counts:
            counts[t["category"]] += 1
        else:
            dropped.append((slug, t["category"]))
    # Build per-category name list ONCE (was O(N*K); now O(N) once).
    by_category: Dict[str, List[str]] = {c: [] for c in CATEGORIES}
    for slug, t in REGISTRY.items():
        if t["category"] in by_category:
            by_category[t["category"]].append(t["name"])
    print("  CATEGORY       COUNT  TOOLS")
    print("  " + "-" * 60)
    total = 0
    for c in CATEGORIES:
        n = counts[c]
        total += n
        print(f"  {c:<14} {n:<6} {', '.join(by_category[c])}")
    print(f"\n  Total: {total} tools across {len(CATEGORIES)} categories")
    if dropped:
        print(f"  [WARN] {len(dropped)} REGISTRY entries have OUT-OF-LIST categories:")
        for slug, cat in dropped:
            print(f"    {slug}: category={cat!r}")
        return 2  # loud exit so schema drift is visible (not silent)
    return 0

def cmd_tiers(args: argparse.Namespace) -> int:
    """Print tiers + tool counts; warn on out-of-list tiers (schema drift)."""
    counts: Dict[str, int] = {t: 0 for t in TIERS}
    dropped: List = []
    for slug, tool in REGISTRY.items():
        if tool["tier"] in counts:
            counts[tool["tier"]] += 1
        else:
            dropped.append((slug, tool["tier"]))
    print("  TIER         COUNT  EXAMPLES")
    print("  " + "-" * 60)
    examples: Dict[str, List[str]] = {t: [] for t in TIERS}
    for slug, tool in REGISTRY.items():
        if tool["tier"] in examples and len(examples[tool["tier"]]) < 4:
            examples[tool["tier"]].append(tool["name"])
    total = 0
    for t in TIERS:
        n = counts[t]
        total += n
        print(f"  {tier_label(t):<12} {n:<6} {', '.join(examples[t])}")
    print(f"\n  Total: {total} tools across {len(TIERS)} tiers")
    if dropped:
        print(f"  [WARN] {len(dropped)} REGISTRY entries have OUT-OF-LIST tiers:")
        for slug, tier in dropped:
            print(f"    {slug}: tier={tier!r}")
        return 2
    return 0

def cmd_search(args: argparse.Namespace) -> int:
    """Substring match across name / path / invocation / notes."""
    needle = args.needle.lower()
    matched = [(k, t) for k, t in REGISTRY.items() if needle in (t["name"] + t["path"] + t["invocation"] + t["notes"]).lower()]
    if not matched:
        print(f"[INFO] no matches for: {args.needle!r}")
        return 0
    print_table(matched)
    return 0

def cmd_info(args: argparse.Namespace) -> int:
    """Print full record for one tool (keyed by registry slug)."""
    key = args.name.lower()
    tool = REGISTRY.get(key)
    if not tool:
        # Try fuzzy match
        candidates = [(k, t) for k, t in REGISTRY.items() if key in k or key in t["name"].lower()]
        if not candidates:
            print(f"[ERR] tool not found: {args.name!r}")
            print(f"      try: python tool_kit.py search {args.name!r}")
            return 1
        if len(candidates) > 1:
            print(f"[ERR] ambiguous: {args.name!r} matches {len(candidates)} tools:")
            for k, t in candidates:
                print(f"        {k}  ({t['name']})")
            return 1
        key, tool = candidates[0]
    print(f"  Name       : {tool['name']}")
    print(f"  Slug       : {key}")
    print(f"  Category   : {tool['category']}")
    print(f"  Tier       : {tier_label(tool['tier'])}")
    print(f"  Path       : {tool['path']}")
    print(f"  Invocation : {tool['invocation']}")
    print(f"  Notes      : {tool['notes']}")
    if "health_url" in tool:
        print(f"  Health     : {tool['health_url']}")
    return 0

def cmd_run(args: argparse.Namespace) -> int:
    """Print invocation for one tool. Dispatcher never executes shell.

    The operator copies the printed invocation and runs it themselves.
    Effectful shell exec is deliberately out of scope for this dispatcher.
    `--run` is parsed for backward-compat (old scripts may still pass it) but
    behavior is identical with or without it.
    """
    key = args.name.lower()
    tool = REGISTRY.get(key)
    if not tool:
        candidates = [(k, t) for k, t in REGISTRY.items() if key in k or key in t["name"].lower()]
        if len(candidates) == 1:
            key, tool = candidates[0]
        elif len(candidates) > 1:
            print(f"[ERR] ambiguous: {args.name!r} matches {len(candidates)} tools:")
            for k, t in candidates:
                print(f"        {k}  ({t['name']})")
            return 1
        else:
            print(f"[ERR] tool not found: {args.name!r}")
            return 1
    print(f"  {tool['name']}  [{tier_label(tool['tier'])} / {tool['category']}]")
    print(f"  Path       : {tool['path']}")
    print(f"  Invocation : {tool['invocation']}")
    print(f"  Notes      : {tool['notes']}")
    print(f"  (Dispatcher does NOT execute shell — copy the invocation and run it manually.)")
    if args.run:
        print(f"  (--run acknowledged; behavior unchanged.)")
    return 0

def cmd_health(args: argparse.Namespace) -> int:
    """Probe each tool that has a health_url via TCP/HTTP. Print status."""
    print("\n  HEALTH PROBE — tools with health_url:\n")
    print(f"  {'NAME':<33} {'URL':<48} {'STATE':<10} {'LATENCY':<10}")
    print("  " + "-" * 101)
    for key, tool in REGISTRY.items():
        url = tool.get("health_url")
        if not url:
            continue
        # Quick TCP probe to host:port (cheap sanity)
        # Parse host:port from URL
        try:
            if "://" in url:
                scheme, rest = url.split("://", 1)
                host_port = rest.split("/", 1)[0]
                if ":" in host_port:
                    host, port = host_port.rsplit(":", 1)
                    port = int(port)
                else:
                    host, port = host_port, (443 if scheme == "https" else 80)
            else:
                continue
            t0 = _now_ms()
            sock = socket.create_connection((host, port), timeout=3.0)
            sock.close()
            latency = _now_ms() - t0
            state = "up"
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            state, latency = "down", "n/a"
        print(f"  {tool['name'][:33]:<33} {url[:48]:<48} {state:<10} {str(latency):<10}")
    return 0

def _now_ms() -> int:
    """Return current epoch milliseconds (cheap, no datetime import needed)."""
    import time
    return int(time.time() * 1000)


# ============================================================
# Argparse wiring
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tool_kit",
        description="AI + IT Toolkit CLI dispatcher — companion to AI_AND_IT_TOOLKIT.md",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_p = sub.add_parser("list", help="list tools (terse table)")
    sp_p.add_argument("--category", choices=CATEGORIES, help="filter by category")
    sp_p.add_argument("--tier", choices=TIERS, help="filter by tier (t1/t2/t3/t4)")
    sp_p.set_defaults(func=cmd_list)

    sp_cat = sub.add_parser("categories", help="list categories + counts")
    sp_cat.set_defaults(func=cmd_categories)

    sp_t = sub.add_parser("tiers", help="list tiers + counts")
    sp_t.set_defaults(func=cmd_tiers)

    sp_s = sub.add_parser("search", help="substring search across name/path/invocation/notes")
    sp_s.add_argument("needle", help="text to search (case-insensitive)")
    sp_s.set_defaults(func=cmd_search)

    sp_i = sub.add_parser("info", help="print full record for one tool")
    sp_i.add_argument("name", help="tool slug or partial name (e.g. 'ollama', 'comfyui', 'music')")
    sp_i.set_defaults(func=cmd_info)

    sp_r = sub.add_parser("run", help="print invocation for one tool (this dispatcher never executes shell)")
    sp_r.add_argument("name", help="tool slug or partial name")
    sp_r.add_argument("--run", action="store_true", help="acknowledge effectful execution (prints but does not exec)")
    sp_r.set_defaults(func=cmd_run)

    sp_h = sub.add_parser("health", help="TCP/HTTP probe for tools with health URLs")
    sp_h.set_defaults(func=cmd_health)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
