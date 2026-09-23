# 🧰 AI_AND_IT_TOOLKIT.md — Operator Self-Use Toolkit Index

> **Generated:** 2026-07-09
> **Audience:** Karma (single operator, daily use). Pragmatic tone, internal paths OK.
> **Source:** Comprehensive sweep across `C:\Users\karma\` + sub-projects (`ComfyUI/`, `python/` Archon, `SLEEP_CASH_API/`, `SLEEP_TRIPLE/`, `AI_ARMY/`, `REVENUE_GENERATORS/`, `COMPLETED_PROJECTS/mobile_backup/`).
> **Companion artifacts:** `AI_AND_IT_TOOLKIT.html` (interactive), `tool_kit.py` (CLI dispatcher).
> **Why this doc exists:** the workspace inventory has grown beyond what `ALL_TOOLS_QUICK_REFERENCE.md` + `AI_TOOLS_INVENTORY_INDEX.md` + `AUSAI_TOOLKIT_INDEX.md` separately cover. This toolkit *integrates* AI + IT tool inventory into one operator-focused cross-walk.

---

## 🏷️ TIER LEGEND

| Tag | Meaning | Update cadence |
|---|---|---|
| 🟢 **T1 — Daily driver** | Used ≥1×/week; book-marked; covers ~80% of typical work | every commit |
| 🟡 **T2 — Weekly** | Used ≥1×/month; meaningful but not always-top-of-mind | weekly |
| 🟠 **T3 — Monthly** | Used on-demand; situational tool | monthly review |
| ⚪ **T4 — Shelfware** | Installed/known but not actively used; cited for completeness | quarterly |

---

## 1. 🧠 LOCAL AI RUNTIMES (LoRA / Inference)

| Tool | Tier | Path / Port | Invocation | Notes |
|---|---|---|---|---|
| **Ollama** | 🟢 T1 | `C:\Users\karma\.ollama\` · API `http://localhost:11434` | `ollama pull <model>` · `ollama run <model> <prompt>` | v0.31.x · models: qwen2.5-coder:latest, deepseek-r1:8b, ornith:9b, llama3.2:3b, mistral:7b, hf.co/deepreinforce-ai/ornith-1.0-35b (CPU-heavy) |
| **ComfyUI** | 🟢 T1 | `C:\Users\karma\ComfyUI\` · API `http://localhost:8188` | `ComfyUI\launch_music_video_studio.bat` (21-option menu) | Local image/video/audio generation · RTX 4060 8GB · `tools/` for headless |
| **LM Studio** | 🟠 T3 | API `http://localhost:1234` | `start LM Studio` | Alt local LLM serving (OpenAI-compatible endpoint) |
| **llama.cpp / vLLM** | ⚪ T4 | (not installed) | n/a | Aspirational; use Ollama until proven better |

## 2. ☁️ CLOUD AI PROVIDERS

| Tool | Tier | API | Notes |
|---|---|---|---|
| **OpenRouter** | 🟢 T1 | `OPENROUTER_API_KEY` env · `https://openrouter.ai/api/v1/chat/completions` | Only AI provider per CLAUDE.md · routes to all models · free models file at `ComfyUI\config\openrouter_free_models.txt` |
| **Anthropic / OpenAI** | ⚪ T4 | (no direct key, per CLAUDE.md) | Use ONLY via OpenRouter |

## 3. 🦾 AGENT FRAMEWORKS (local + multi-agent)

| Tool | Tier | Path | Invocation | Notes |
|---|---|---|---|---|
| **AI Army / Foot Clan** | 🟢 T1 | `AI_ARMY\` · port `:8001` | `python AI_ARMY\server.py` | 9 API routes · 6 agents · revenue-generating |
| **Footclan Executor** | 🟡 T2 | `FOOTCLAN_EXECUTOR.py` | `python FOOTCLAN_EXECUTOR.py --task "..." --dry-run` | Squad-dispatch framework with audit log |
| **Voice PA ↔ Footclan bridge** | 🟠 T3 | `voice_pa_bridge.py` + `VOICE_PA_BRIDGE.md` | default `--dry-run` | Cross-system correlator by iso-minute prefix match · append-only bridge log |
| **Agent Registry** | 🟢 T1 | `AGENT_REGISTRY.md` | read-only | 2,793 agents across 16 domains · append-only · `AGENT_REGISTRY_AUDIT.md` for sanity |
| **Archon V2** | 🟡 T2 | `python\` · ports `:3737/:8181/:8051/:8052` | `START_ARCHON_STACK.bat` · `STOP_ARCHON_STACK.bat` | FastAPI + Socket.IO + MCP + Agents microservice stack · 4 services |
| **Project Brain 2.0** | 🟡 T2 | `PROJECT_BRAIN_2_0\` | `python ingest.py --watch` · `python ingest.py --since <iso>` · `--audit-offset` | SHA256-cycle dedupe · Phase A-H design corridor closed · append-only index |
| **AI Influencer Factory** | 🟡 T2 | `ai_influencer_factory.py` | `python ai_influencer_factory.py --run` | Ollama → Piper TTS → ComfyUI → n8n content pipeline |

## 4. 🧰 AI TOOLS / CLI (single-purpose)

| Tool | Tier | Path | Invocation | Notes |
|---|---|---|---|---|
| **Music Video Studio** | 🟢 T1 | `ComfyUI\tools\music_video_studio.py` | `python ... brainstorm --model ornith --lyrics poem.txt` (10+ subcommands incl. `transcribe` / `analyze-audio` / `wizard`) | Hybrid Ollama/OpenRouter dispatcher · `MVS_MODEL_ALIASES` + `is_openrouter_tag()` |
| **Local AI Assistant** | 🟢 T1 | `ComfyUI\tools\local_ai_assistant.py` | `chat`/`converse`/`browse`/`summarize`/`explain-error`/`plan`/`review`/`check` | Stdlib-only · Ollama aliases via `MODEL_ALIASES` |
| **Benchmark Coders** | 🟡 T2 | `benchmark_coders.py` | `python ... --sweep` · `--model TAG --prompt "..."` | Per-model timing/wordcount/charcount · JSONL history at `benchmark_coders_results.jsonl` |
| **AI Voice PA** | 🟡 T2 | `ai_voice_pa.py` | `python ai_voice_pa.py --run --stt cloud --i-have-credentials` (else `--dry-run`) | 5 intent enum · Rule #8 fence · append-only `voice_pa.actions.jsonl` |
| **YouTube Transcript Harvester** | 🟡 T2 | `youtube_transcript_harvest.py` | `--video URL --lang en --format srt --run` (else `--dry-run`) | Captions-only · Rule #8 fence rigid |
| **WAR_ROOM CLI dispatcher** | 🟢 T1 | `war_room.py` | `status`/`list`/`info`/`health`; doctor family: `snapshot-doctor` / `diff-doctor` / `trend-doctor` / `trend-compare` (RATE-based today-vs-past-week) / `launch-trend` | Operator CLI dispatcher for the HUD + workspace-health doctor family · 16 subcommands total · see `WAR_ROOM.md` runbook section |
| **MCP Host Connector** | 🟠 T3 | `MCP_HOST_CONNECTOR.ps1` | first concrete MCP adapter | Bridges MCP host to the family of MCP servers |

## 5. 🏭 CONTENT FACTORIES (5-lane revenue)

| Tool | Tier | Path | Invocation | Notes |
|---|---|---|---|---|
| **opt_a — Digital Products** | 🟡 T2 | `SLEEP_TRIPLE\opt_a_digital_factory.py` | `python ... --run --publish published` | Gumroad · Ollama(qwen2.5-coder) generators · requires user's Gumroad key |
| **opt_b — Faceless YouTube + Affiliate** | 🟡 T2 | `SLEEP_TRIPLE\opt_b_faceless_shorts.py` | `python ... --run --publish` | TTS → ComfyUI → FFmpeg composites → YouTube Data API v3 upload |
| **opt_c — Crypto Yield** | 🟡 T2 | `SLEEP_TRIPLE\opt_c_crypto_yield.py` | `python ... --run --execute` (else observation-only) | Coinspot/Kraken/IR public tickers · 50 bps threshold · capital-protection default |
| **opt_d — Alerts fanout** | 🟢 T1 | `SLEEP_TRIPLE\opt_d_alerts.py` | `python ... --trigger morning_digest --channel discord` (or telegram) | 8-hour audit window · 3-retry exponential backoff · morning digest |
| **opt_e — Print-on-Demand** | 🟠 T3 | `SLEEP_TRIPLE\opt_e_pod.py` | `python ... --run --publish mode` | ComfyUI design · Printful fulfillment · Shopify sync |
| **REVENUE_GENERATORS suite** | 🟠 T3 | `REVENUE_GENERATORS\` | `deploy_revenue` / `content_factory` / `saas_launcher` / `brain_crawler` / `singularity` / `self_healing` | 6 actions · dispatches through AI Army `:8001` · append-only ledger |

## 6. ⚙️ IT AUTOMATION

| Tool | Tier | Path | Invocation | Notes |
|---|---|---|---|---|
| **n8n Automation** | 🟡 T2 | `n8n-automation-stack\` · port `:5678` | `docker-compose up -d` | 91+ workflow templates · LUCA avatar generator · webhook rounds |
| **AI Self-Healing Daemon** | 🟠 T3 | `REVENUE_GENERATORS\SELF_HEALING_DAEMON.py` | standalone runner | Service health checks · `plan_heal` instead of `attempt_heal` |
| **MCP Federation** | 🟠 T3 | `MCP_FEDERATION_MERGER.ps1` + `MCP_REMOTE_QUERY.ps1` | `... --run` (else `--dry-run`) | Phase 1: query rows · Phase 2: chunk rows · closed 5-element outcome enum |
| **SLEEP_TRIPLE orchestrator** | 🟡 T2 | `SLEEP_TRIPLE\sleep_orchestrator.py` | `python ... --force-window` | 23:00-07:00 nightly + 07:00 morning digest + Sun weekly rollup · append-only audit log |
| **Task-scheduler installer** | 🟡 T2 | `install_monitor_scheduler.bat` | `--dry-run` · `--uninstall` · (no flag) installs both `SLEEP_CASH\Monitor` + `SLEEP_CASH\ProbeAll` | Auto-elevates via PowerShell UAC · digit-validates `MONITOR_INTERVAL` |

## 7. 🛠️ DEV INFRASTRUCTURE (operator plumbing)

| Tool | Tier | Path | Notes |
|---|---|---|---|
| **Python venvs** | 🟢 T1 | `python\.venv\` (Archon) · `SLEEP_CASH_API\` · per-project | `uv sync` standard · 3.12 + 3.13 mixed |
| **uv** | 🟢 T1 | `~/.local\bin\uv` | Dependency manager · fast resolver |
| **Node.js + Vite** | 🟡 T2 | `archon-ui-main\` · Vite proxy `:3737` → `:8181` | React + TypeScript + TailwindCSS frontend |
| **Docker / docker-compose** | 🟡 T2 | `n8n-automation-stack\` · Archon stack · multi-archon-compose | Compose orchestration under bare-Windows runners (`archon_orchestrator.py`) |
| **PowerShell** | 🟢 T1 | Windows-native | Required for UAC elevation of `.bat` installers |
| **pyenv** | 🟠 T3 | `~/.pyenv\` | Per-project Python version pick · currently 3.13 default |
| **npm / pnpm / bun** | 🟠 T3 | various | Bun at `~/.bun\` is fastest for Karma's local scripts |

## 8. 📱 MOBILE / HARDWARE (touches physical borders)

| Tool | Tier | Path | Invocation | Notes |
|---|---|---|---|---|
| **Recovery Suite** | 🟡 T2 | `COMPLETED_PROJECTS\mobile_backup\RECOVERY_SUITE.bat` (12-position) · top-level shim `C:\Users\karma\recovery.bat` | reaches from any cwd · dispatches Android unlock GUI + iPhone suite + Oppo specialist + 4 Flask reference apps | 15/15 PASS tests · broken-screen runbook |
| **Sunshine + Moonlight** | 🟡 T2 | `C:\Program Files\Sunshine\` (if installed) | See `SUNSHINE_MOONLIGHT_SETUP.md` | GPU-accelerated remote-desktop · documented, NOT auto-installed |
| **scrcpy** | ⚪ T4 | (uninstalled — `tools/scrcpy/` empty) | `choco install scrcpy adb` | Android screen-over-USB |
| **libimobiledevice** | ⚪ T4 | (uninstalled) | `choco install libimobiledevice` | iPhone plumbing for `iphone_recovery.py` |
| **adb (Android Debug Bridge)** | 🟢 T1 | `C:\Program Files\Google\Android\platform-toolsdb.exe` (or PATH) | `adb devices` · `adb install <apk>` · `adb shell` | Core daily-driver for ALL Android ops · USB + wireless (adb pair IP:PORT) |
| **fastboot** | 🟢 T1 | `C:\Program Files\Google\Android\platform-toolsastboot.exe` | `fastboot devices` · `fastboot flash <partition> <img>` · `fastboot oem unlock` | Companion to adb · bootloader unlock / recovery flash / EDL |
| **Android platform-tools (ZIP)** | 🟡 T2 | `C:\Program Files\Google\Android\platform-tools` | `winget install Google.PlatformTools` · or zip from developer.android.com | Bundle: adb + fastboot + mDNS responder · ~7 MB |
| **APKTool** | 🟡 T2 | `C:\Program Filespktoolpktool.jar` | `java -jar apktool.jar d -o out_dir foo.apk` | Reverse-engineer suspicious APKs (FB-evidence use) · smali + 9patch |
| **jadx (DEX decompiler)** | 🟡 T2 | `C:\Program Files\jadxin\jadx.exe` | `jadx -d out_dir foo.apk` · `jadx-gui foo.apk` | DEX/Java decompiler · inspect classes/methods · companion to apktool |
| **Frida** | 🟠 T3 | `AppData\Local\Programs\Frida` (or `pip install frida-tools`) | `frida -U -l script.js com.target.app` | Runtime API-hook · cross-platform · trace suspicious apps at runtime |
| **Magisk (root framework)** | 🟠 T3 | Phone-side install (F-Droid / GitHub) | `adb push magisk.apk /data/local/tmp` then install via Magisk Manager | Systemless root · MagiskHide + Zygisk; use `/data/local/tmp` NOT `/sdcard` (Android 11+ write-restricted) |
| **Android Studio** | 🟠 T3 | `C:\Program Files\Android\Android Studioin\studio64.exe` | `start "" "Android Studio"` | Full APK dev environment · emulator · profiler · ~5 GB |
| **libimobiledevice CLI** | 🟡 T2 | `C:\Program Files\libimobiledevicein` | `idevice_id -l` · `idevicesyslog` · `idevicebackup2 backup <dir>` | CLI surface for ALL iOS plumbing · pull logs / screenshots |
| **iMazing (iOS GUI)** | 🟠 T3 | `C:\Program Files\iMazing` | `start "" "iMazing.exe"` | GUI iPhone backup/transfer · encrypted backups · iTunes-replacement |
| **Windows Subsystem for Android (WSA)** | 🟠 T3 | Microsoft Store · Amazon Appstore (ProductId=9p3395vx91nr) | `start ms-windows-store://pdp/?ProductId=9p3395vx91nr` | DEPRECATED Sept 2024 (Microsoft); Amazon Appstore install path remains valid; adb localhost:58526 still works |
| **MTKClient (MediaTek flash)** | ⚪ T4 | `C:\Program Files\mtkclient\mtk.py` (clone github.com/bkerler/mtkclient + venv) | `cd "C:\Program Files\mtkclient" && .venv\Scripts\python.exe mtk.py` | Niche: bypass-auth + flash MediaTek chips · install-on-demand; never auto-installed |

## 9. 📊 DASHBOARDS & KNOWLEDGE BASE

| Tool | Tier | Path | Notes |
|---|---|---|---|
| **AI Tools Dashboard** | 🟢 T1 | `AI_TOOLS_DASHBOARD.html` | All tools in one HTML page · Open in browser |
| **Ultimate Empire V2** | 🟢 T1 | `ULTIMATE_AI_EMPIRE_ENHANCED_DASHBOARD_V2.html` | 6 Quick Tools tiles now (incl. Mobile Recovery) |
| **Revenue Dashboard (Live)** | 🟢 T1 | `http://localhost:3144` | SLA `SLEEP_TRIPLE\dashboard_server.py` |
| **Master Command Center** | 🟢 T1 | `UNIFIED_COMMAND_CENTER.html` · `master_dashboard_hub.html` | Top-level hub |
| **System Status Dashboard** | 🟡 T2 | `dashback26\system_status_dashboard.html` | Service health summary |
| **Bookmark Manager Pro** | 🟡 T2 | `BOOKMARK_MANAGER_PRO_INDEX.md` (16 stages) · `enhanced_dashboard.html` | 7,685 bookmarks · 17 categories · 100% test coverage |

## 10. 🧾 AUDIT FAMILY (workspace hygiene / evidence trail)

| Tool | Tier | Path | Notes |
|---|---|---|---|
| **REALITY_VS_CLAIM_AUDIT** | 🟡 T2 | `REALITY_VS_CLAIM_AUDIT.py` · `--dry-run` default | Cross-checks master-index headlines vs on-disk reality |
| **INDEX_DELTA_SCANNER** | 🟡 T2 | `INDEX_DELTA_SCANNER.py` | Top-level (1-deep) entry divergence |
| **INDEX_DELTA_RECURSIVE** | 🟡 T2 | `INDEX_DELTA_RECURSIVE.py` `--max-depth 2` | Where-inside the disk tree the divergence happens |
| **MASTER_INDEX_RECONCILER** | 🟡 T2 | `MASTER_INDEX_RECONCILER.py` `--run --emit-summary` | Aggregates 3 source logs into `MASTER_INDEX_RECONCILED.md` |
| **GAL_INTEGRITY_VERIFY** | 🟡 T2 | `GAL_INTEGRITY_VERIFY.py` `--header-only` (fast) | x:\AETHER_CORE_SYSTEM archives · 7-element status enum |
| **CROSS_TOOL_AGGREGATOR** | 🟡 T2 | `CROSS_TOOL_AGGREGATOR.py` `--run --emit-summary` | Top-of-family digest for the 5-log audit family |
| **DOTDIR_CATALOG_RUN** | 🟡 T2 | `DOTDIR_CATALOG_RUN.py` `--run --emit-summary` | 81+ workspace-hygiene names · emits `DOTDIR_CATALOG.md` |
| **append-only hygiene runner** | 🟠 T3 | `append_only_hygiene_runner.py` | 12-log closed list · size + ts monotonic check |
| **app backup-integrity verifier** | 🟠 T3 | `verify_backups.ps1` · `BACKUP_AUDIT_RUN.ps1` | Reads `BACKUP_MANIFEST.json` · 6-element status enum |
| **env-vs-example checker** | 🟠 T3 | `ENV_AUDIT_RUN.ps1` | 5-element `ENV_KEY_STATUS_ENUM` · Rule #8 fence rigid |

---

## 11. 🖥️ OS APPS (installed on this PC)

| Tool | Tier | Path / Source | Invocation | Notes |
|---|---|---|---|---|
| **Google Chrome** | 🟢 T1 | `C:\Program Files\Google\Chrome\Application` | `start "" chrome` | v149.0.7827.201 · primary browser |
| **Microsoft Edge** | 🟢 T1 | `C:\Program Files (x86)\Microsoft\Edge\Application` | `start "" msedge` | 5 entries in scan (Edge + WebView + updater) |
| **Mozilla Firefox** | 🟡 T2 | `C:\Program Files\Mozilla Firefox` | `start "" firefox` | Alt browser |
| **GitHub Desktop** | 🟢 T1 | `AppData\Local\GitHubDesktop` | `start "" "GitHub Desktop.exe"` | v3.5.3 · git GUI |
| **Docker Desktop** | 🟢 T1 | `C:\Program Files\Docker\Docker` | `start "" "Docker Desktop.exe"` | v4.81.0 · WSL2 |
| **Slack** | 🟡 T2 | AppX / `AppData\Local\slack` | `start "" slack` | Daily team comms |
| **Discord** | 🟡 T2 | AppX / `AppData\Local\Discord` | `start "" discord` | Voice + community |
| **Telegram Desktop** | 🟡 T2 | `AppData\Roaming\Telegram Desktop` | `start "" "Telegram.exe"` | E2E DMs |
| **Spotify** | 🟡 T2 | `AppData\Roaming\Spotify` | `start "" spotify` | Focus music |
| **VLC media player** | 🟡 T2 | `C:\Program Files\VideoLAN\VLC` | `start "" vlc <file>` | Universal codec |
| **HandBrake** | 🟠 T3 | `C:\Program Files\HandBrake` | `start "" "HandBrake.exe"` | FFmpeg UI |
| **OBS Studio** | 🟠 T3 | `C:\Program Files\obs-studio\bin\64bit` | `start "" obs64.exe` | Streaming + recording |
| **CapCut** | 🟠 T3 | `AppData\Local\CapCut` | `start "" "CapCut.exe"` | v8.8.0.3774 · short-form video |
| **DaVinci Resolve** | 🟠 T3 | `C:\Program Files\Blackmagic Design\DaVinci Resolve` | `start "" Resolve.exe` | Color grading + NLE |
| **Blackmagic RAW** | 🟠 T3 | (system codec) | n/a | Codec pack for .braw files |
| **Google Drive** | 🟡 T2 | `C:\Program Files\Google\Drive File Stream` | `start "" "GoogleDriveFS.exe"` | v127.0.1.0 · Drive sync |
| **Dropbox** | 🟡 T2 | `AppData\Roaming\Dropbox` | `start "" dropbox` | Client-side sync |
| **Foxit PDF Reader** | 🟡 T2 | `C:\Program Files (x86)\Foxit Software\Foxit PDF Reader` | `start "" "Foxit PDF Reader.exe"` | v2024.4.0.27683 |
| **CutePDF Writer** | 🟠 T3 | `C:\Program Files (x86)\CutePDF Writer` | print-to-printer → "CutePDF Writer" | v4.0 · printer-as-PDF |
| **Notepad++** | 🟡 T2 | `C:\Program Files\Notepad++` | `code-like` registry entry | 3 hits in scan incl. plugins |
| **7-Zip** | 🟡 T2 | `C:\Program Files\7-Zip` | `7zFM` (or `7z a archive.7z files\`) | Multi-format archiver |
| **WinRAR** | 🟡 T2 | `C:\Program Files\WinRAR` | `start "" "WinRAR.exe"` | 2 hits (x64 + x86) |
| **CPU-Z** | 🟠 T3 | `C:\Program Files\CPUID\CPU-Z` | `start "" "cpuz.exe"` | v2.15 · CPU/mobo/RAM info |
| **AIDA64 Extreme** | 🟠 T3 | `C:\Program Files (x86)\FinalWire\AIDA64 Extreme` | `start "" "aida64.exe"` | v7.50 · deeper sensor logging |
| **Deskflow** | 🟠 T3 | `C:\Program Files\Deskflow` | `start "" deskflow` | v1.23.0.0 · cross-machine K/M |
| **iCloud / Bonjour** | ⚪ T4 | `C:\Program Files (x86)\Bonjour` | (background service) | Apple networking helper |

## 12. ⚙️ SYSTEM (runtimes + utilities on this PC)

| Tool | Tier | Path / Source | Invocation | Notes |
|---|---|---|---|---|
| **Windows Terminal** | 🟢 T1 | Microsoft Store (AppX) | `wt` | Primary CLI host · tabs + panes |
| **Git** | 🟢 T1 | `C:\Program Files\Git` | `git <cmd>` | v2.48.1 · msys2 + POSIX utilities |
| **GitHub CLI (gh)** | 🟢 T1 | `(scan: HKLM 64)` | `gh <cmd>` | v2.75.0 · `gh auth login` |
| **Python (system)** | 🟢 T1 | `C:\Python313\python.exe` (or `py` launcher) | `python --version` | Companion to uv-managed venvs |
| **VS Code (system)** | 🟢 T1 | `AppData\Local\Programs\Microsoft VS Code` | `code .` | Companion to Antigravity |
| **Antigravity (Google IDE)** | 🟡 T2 | `AppData\Local\Programs\Antigravity IDE` | `start "" "Antigravity IDE.exe"` | Google's 2026 anti-gravity IDE |
| **Visual Studio 2022** | 🟡 T2 | `C:\Program Files\Microsoft Visual Studio\2022` | `devenv.exe` | Enterprise .NET/C++ |
| **Node.js (system)** | 🟡 T2 | `C:\Program Files\nodejs` | `node --version` | Project-local preferred via npm |
| **AWS CLI v2** | 🟡 T2 | `(scan: HKLM 64)` | `aws <cmd>` | v2.27.50 · SSO friendly |
| **Google Cloud SDK** | 🟡 T2 | `C:\Program Files (x86)\Google\Cloud SDK` | `gcloud <cmd>` | Includes gsutil + bq + kubectl |
| **Azure CLI** | 🟡 T2 | (winget install) | `az <cmd>` | `az login` first |
| **Java JDK** | 🟡 T2 | `C:\Program Files\Eclipse Adoptium` | `java -version` | JAVA_HOME for build tools |
| **.NET Runtime** | 🟡 T2 | `C:\Program Files\dotnet` | `dotnet --list-runtimes` | 10 entries in scan |
| **PowerToys** | 🟡 T2 | Microsoft Store (AppX) | `start "" PowerToys.exe` | FancyZones + PowerRename |
| **Everything (voidtools)** | 🟡 T2 | `C:\Program Files\Everything` | `Everything.exe -search <q>` | Instant filename search |
| **Rust toolchain** | 🟠 T3 | `C:\Users\karma\.cargo\bin` | `rustc --version` | Install via rustup-init.exe |
| **Go runtime** | 🟠 T3 | `C:\Program Files\Go\bin` | `go version` | 11 hits in scan |
| **Rufus (USB imager)** | 🟠 T3 | `C:\Program Files\Rufus` | `start "" Rufus.exe` | Bootable USB |

---

## 🔍 NAVIGATION

| Need | Open |
|---|---|
| **Visual filter / hover-card UI** | Open `AI_AND_IT_TOOLKIT.html` in the browser |
| **CLI: list/invoke/health** | `python tool_kit.py` (dispatcher with subcommands) |
| **Companion for THIS doc** (same data, presentation differs) | `AI_AND_IT_TOOLKIT.html` + `tool_kit.py` |
| **Sales-toolkit starter pack** (different audience) | `AUSAI_TOOLKIT_INDEX.md` — for client calls |
| **AI-runner catalog** (vendored / installed AI coding agents) | `AI_TOOLS_INVENTORY_INDEX.md` |
| **Giant fleet overview** | `WORKSPACE_INDEX.md` (18 systems) |
| **One-page printable cheat** | `GRAND_SUMMARY.md` |
| **Daily digest** | `DAILY_REFERENCE_DIGEST_2026-07-09.md` |

## 🔗 COMPANION ARTIFACTS

This doc is one of THREE co-generated shapes (all created 2026-07-09):

1. `AI_AND_IT_TOOLKIT.md` — **canonical source-of-truth** (this file)
2. `AI_AND_IT_TOOLKIT.html` — same data, HTML form with filter chips + hover cards
3. `tool_kit.py` — CLI dispatcher that can invoke any T1/T2 tool with bare command

All three are pointed at from `REFERENCE_DOCS_INDEX.md` (engineer-discoverable) + `WORKSPACE_INDEX.md` + `GRAND_SUMMARY.md` (START HERE row).

## 💡 DECISION GUIDE — which tool for which task?

| If you need to… | Pick | Tier |
|---|---|---|
| Run a local LLM | Ollama | T1 |
| Brainstorm lyrics/concept | Music Video Studio (OpenRouter free) | T1 |
| Whisper-transcribe audio | Music Video Studio `batch-transcribe` | T1 |
| Generate cover art | ComfyUI via launcher menu | T1 |
| Find any one of 2,793 agents | `grep -F "<id>" AGENT_REGISTRY.md` | T1 |
| Run an AI Army revenue action | `python AI_ARMY\server.py` then `:8001` | T1 |
| Cross-check disk vs index headlines | `python REALITY_VS_CLAIM_AUDIT.py --run --emit-summary` | T2 |
| Sched alerts about overnight state | `python opt_d_alerts.py --trigger morning_digest --channel discord` | T1 |
| Auto-edit a Markdown file | `str_replace` tool · no tool needed | n/a |

---

*Designed under Golden Rules: append, preserve, protect. Tier reassessments are updates; tool entries are append-only.*
