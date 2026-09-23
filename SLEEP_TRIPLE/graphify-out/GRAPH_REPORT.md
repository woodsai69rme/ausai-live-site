# Graph Report - SLEEP_TRIPLE  (2026-08-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 710 nodes · 1009 edges · 60 communities (54 shown, 6 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `373cdf5f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- opt_d_alerts.py
- SLEEP_TRIPLE — System Reference
- preflight.py
- opt_f_discovery.py
- ZoneInfo
- main
- OptEPodTests
- profile_all_setup.py
- load_config
- crypto_monitor.py
- sleep_orchestrator.py
- 🎬 YOUTUBE OAUTH SETUP FOR SLEEP_TRIPLE (Lane B)
- YouTube Transcript API - Micro-SaaS
- opt_a_digital_factory.py
- opt_b_faceless_shorts.py
- SLEEP_TRIPLE — Three Aud-Earning Systems That Run While You Sleep
- autonomous_master.py
- Free AI Toolkit - Complete Reference
- Lane B — Faceless YouTube Shorts + Affiliate (ZERO-COST Playbook)
- free_ai_toolkit.py
- 🎉 FREE AI TOOLKIT - COMPLETE & OPERATIONAL
- Crypto Monitor — Tier 1 Price Alert System
- Handler
- _doc_drift_check.py
- youtube_cli_oauth.py
- IsPlaceholderTests
- vercel.json
- REVENUE_SUMMARY.md
- gumroad_upload.py
- auto_upload.js
- read_json
- _commit_alerts.py
- _commit_alerts2.py
- _commit_docs.py
- _commit_retry.py
- config.py

## God Nodes (most connected - your core abstractions)
1. `load_config()` - 20 edges
2. `main()` - 16 edges
3. `SLEEP_TRIPLE — System Reference` - 16 edges
4. `main()` - 15 edges
5. `main()` - 13 edges
6. `OptEPodTests` - 13 edges
7. `🎬 YOUTUBE OAUTH SETUP FOR SLEEP_TRIPLE (Lane B)` - 13 edges
8. `Lane B — Faceless YouTube Shorts + Affiliate (ZERO-COST Playbook)` - 12 edges
9. `main()` - 11 edges
10. `IsPlaceholderTests` - 11 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `emit()`  [INFERRED]
  SLEEP_TRIPLE/opt_e_pod.py → SLEEP_TRIPLE/sleep_orchestrator.py
- `main()` --calls--> `append_ledger_event()`  [EXTRACTED]
  SLEEP_TRIPLE/opt_d_alerts.py → SLEEP_TRIPLE/_ledger_writer.py
- `main()` --calls--> `append_ledger_event()`  [EXTRACTED]
  SLEEP_TRIPLE/opt_e_pod.py → SLEEP_TRIPLE/_ledger_writer.py
- `load_config()` --calls--> `load_config()`  [EXTRACTED]
  SLEEP_TRIPLE/opt_a_digital_factory.py → SLEEP_TRIPLE/env_bridge.py
- `load_config()` --calls--> `load_config()`  [EXTRACTED]
  SLEEP_TRIPLE/opt_b_faceless_shorts.py → SLEEP_TRIPLE/env_bridge.py

## Import Cycles
- None detected.

## Communities (60 total, 6 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.06
Nodes (38): BackgroundTasks, BaseModel, check_rate_limit(), CheckoutResponse, create_checkout(), CreateCheckoutRequest, extract_video_id(), format_transcript() (+30 more)

### Community 1 - "opt_d_alerts.py"
Cohesion: 0.07
Nodes (40): append_audit(), build_discord_payload(), build_ntfy_payload(), build_payload(), build_pushover_payload(), build_slack_payload(), build_telegram_payload(), detect_actionable_spreads() (+32 more)

### Community 2 - "SLEEP_TRIPLE — System Reference"
Cohesion: 0.04
Nodes (45): 10. Architecture Decisions Recap, 11. Known Limitations & Pending Followups, 12. Quick Reference Commands, 13. Failure-Mode Reference Table, 14.1 Ledger Writer Canonicalization, 14.2 UTF-8 BOM Bug Fixes, 14.3 Schema Mismatch in opt_c Ledger Wiring, 14.4 HTTP Smoke Promotion to Section 11 (+37 more)

### Community 3 - "preflight.py"
Cohesion: 0.11
Nodes (32): cmd_open_missing(), cmd_status(), cmd_template(), cmd_youtube_oauth(), main(), Print .env template lines for missing keys only., Delegate to youtube_cli_oauth.py (InstalledAppFlow browser login)., credential_report() (+24 more)

### Community 4 - "opt_f_discovery.py"
Cohesion: 0.10
Nodes (34): ai_analyze(), analyze_opportunity(), append_audit(), emit_lane_recommendations(), estimate_scores(), generate_build_plan(), is_rule_8(), iso_now() (+26 more)

### Community 5 - "ZoneInfo"
Cohesion: 0.11
Nodes (29): main(), append_audit(), comfyui_reachable(), generate_comfyui_image(), generate_design_prompt(), http_get_json(), http_post_json(), is_rule_8() (+21 more)

### Community 6 - "main"
Cohesion: 0.09
Nodes (11): FormatOutputTests, LaneStatusTests, main(), MainExitCodeTests, _lane_status must reduce findings to [OK] / [NEEDS_CONFIG] / [OFFLINE] / [BLOCKE, Pure helpers must produce stable output., main() exit codes — runs against real on-disk configs., --verbose appends 'Per-Lane detail (verbose)' block after the summary. (+3 more)

### Community 7 - "OptEPodTests"
Cohesion: 0.08
Nodes (15): main(), OptEPodTests, Dry-run main() should return 0 and emit a design to outbox (fast: every Ollama/C, Dry-run mode should write a design file to outbox/e_pod/.          The earlier b, Dry-run should append audit rows to SLEEP_TRIPLE_AUDIT.jsonl.          Mocks sel, --dry-run and --run together should be refused., Invalid --publish choice should be refused by argparse., Run all tests and report summary. (+7 more)

### Community 8 - "profile_all_setup.py"
Cohesion: 0.20
Nodes (24): audit(), cmd_init(), cmd_open(), cmd_open_all(), cmd_open_google(), cmd_self_test(), cmd_set(), cmd_status() (+16 more)

### Community 9 - "load_config"
Cohesion: 0.14
Nodes (21): load_config(), Load a lane config JSON file with optional .env overlay., detect_set_channels(), main(), append_audit(), check_idempotent(), emit(), in_sleep_window() (+13 more)

### Community 10 - "crypto_monitor.py"
Cohesion: 0.19
Nodes (21): cmd_once(), cmd_test_alert(), _deep_merge(), _load_config(), _log_entry(), main(), notify(), _now_iso() (+13 more)

### Community 11 - "sleep_orchestrator.py"
Cohesion: 0.17
Nodes (20): append_ledger_event(), Append a 'signal_emitted' row to REVENUE_LEDGER.jsonl via     Append-RevenueEven, append_audit(), binance_fetch(), coinspot_fetch(), _derive_aud_per_usd(), https_get_json(), independentreserve_fetch() (+12 more)

### Community 12 - "🎬 YOUTUBE OAUTH SETUP FOR SLEEP_TRIPLE (Lane B)"
Cohesion: 0.10
Nodes (20): 🔧 AUTOMATED SETUP SCRIPT, Complete guide to get YouTube API credentials for Shorts upload, 📁 FILE LOCATION FOR SLEEP_TRIPLE, 🔐 OAUTH FLOW (First Real Run), `opt_b_config.json` (already updated by setup script), ▶️ RUN THE SETUP, `sleep_config.json` - Enable Lane B, **Step 1: Create Google Cloud Project** (+12 more)

### Community 13 - "YouTube Transcript API - Micro-SaaS"
Cohesion: 0.11
Nodes (18): 1. Install Dependencies, 2. Configure Environment, 3. Set Up Stripe, 4. Run Locally, 5. Deploy to Vercel, API Usage, Check Usage, Create Checkout Session (Pro Upgrade) (+10 more)

### Community 14 - "opt_a_digital_factory.py"
Cohesion: 0.19
Nodes (18): append_audit(), assert_rule_8_path(), generate_prompts(), gumroad_publish_stub(), is_rule_8(), load_config(), load_orchestrator_config(), main() (+10 more)

### Community 15 - "opt_b_faceless_shorts.py"
Cohesion: 0.16
Nodes (18): append_audit(), comfyui_health(), harvest_topics(), inject_affiliate_links(), is_rule_8(), load_config(), load_master(), main() (+10 more)

### Community 16 - "SLEEP_TRIPLE — Three Aud-Earning Systems That Run While You Sleep"
Cohesion: 0.11
Nodes (18): Bug closeouts (7 bugs in the ledger pipeline), Design Decisions, Files, New files, Option A — AI Digital Product Factory (`opt_a_digital_factory.py`), Option B — Faceless YouTube Shorts + Affiliate Funnel (`opt_b_faceless_shorts.py`), Option C — Crypto Yield Automation (`opt_c_crypto_yield.py`), Push status (+10 more)

### Community 17 - "autonomous_master.py"
Cohesion: 0.20
Nodes (17): append_audit(), get_last_run_summary(), is_rule_8(), load_config(), main(), Path, Run preflight and return (rc, summary)., Run the nightly orchestrator and return (rc, summary). (+9 more)

### Community 18 - "Free AI Toolkit - Complete Reference"
Cohesion: 0.11
Nodes (17): 🌐 Browser Automation (Built-in Hermes Tools), Cloud (nemotron-nano-12b-v2-vl:free - Zero VRAM), 🖥️ Computer Use (Desktop Automation), 📁 Files Created, Free AI Toolkit - Complete Reference, Local (minicpm-v:latest - 5.5 GB), 📦 Local Models (Sequential - ONE at a time), ☁️ OpenRouter Free Models (Parallel - ZERO VRAM) (+9 more)

### Community 19 - "Lane B — Faceless YouTube Shorts + Affiliate (ZERO-COST Playbook)"
Cohesion: 0.11
Nodes (17): 0. The real blocker (do this first), 1. Niche (Module: Strategy / Niche Decision Matrix), 2. Packaging (Module: Packaging — titles/thumbnails), 30-day $0 plan, 3. Scripting (Module: Scripting — AI workflows, hooks, retention), 4. Production (Module: Production), 5. Analytics (Module: Analytics — CTR, AVD, retention), 6. Monetization (Module: Sponsors + beyond AdSense) (+9 more)

### Community 20 - "free_ai_toolkit.py"
Cohesion: 0.14
Nodes (16): browser_automation_example(), computer_use(), computer_use_example(), demo_4_parallel_models(), demo_sequential_pipeline(), Wrapper for computer_use tool (would be called via Hermes)., Example browser automation workflow., Example computer use workflow. (+8 more)

### Community 21 - "🎉 FREE AI TOOLKIT - COMPLETE & OPERATIONAL"
Cohesion: 0.12
Nodes (16): 1. Browser Automation (Built-in Hermes Tools) ✅, 2. Computer Use (Desktop Automation via cua-driver) ✅, 3. Vision Models ✅, 4. Local Ollama Models (Sequential - ONE at a time) ✅, 5. OpenRouter Free Models (Parallel - ZERO VRAM) ✅, 📁 Files Created in `C:\Users\karma\SLEEP_TRIPLE\`, 🎉 FREE AI TOOLKIT - COMPLETE & OPERATIONAL, ⚡ Pro Tips (+8 more)

### Community 22 - "Crypto Monitor — Tier 1 Price Alert System"
Cohesion: 0.13
Nodes (14): Config, Crypto Monitor — Tier 1 Price Alert System, Discord Webhook Setup, Extending, Files, Option A: Windows Task Scheduler (recommended for your setup), Option B: Background process, Option C: Terminal with nohup (MSYS) (+6 more)

### Community 23 - "Handler"
Cohesion: 0.23
Nodes (9): BaseHTTPRequestHandler, Handler, main(), Path, SLEEP_TRIPLE audit log; always project-local so the dashboard ships portable., REVENUE ledger; prefer project-local, fall back to historical global path., Resolve the path on every request (handles late-created log files).         `res, _resolve_audit() (+1 more)

### Community 24 - "_doc_drift_check.py"
Cohesion: 0.26
Nodes (11): _count_unstripped_live(), _git_log_sleep_commits_with_subjects(), _hash_exists(), main(), Return ``(hash, subject)`` tuples parsed from §9 commit-history table     rows., Verify a short hash resolves to a real commit in the repo., How many entries would ``git log`` return WITHOUT the DOC_UPDATE_RE     strip? U, Skip entries at the head of ``rows`` whose subject matches     ``DOC_UPDATE_RE`` (+3 more)

### Community 25 - "youtube_cli_oauth.py"
Cohesion: 0.38
Nodes (11): cmd_guide(), cmd_status(), _ensure_deps(), _load_credentials(), main(), _optional_patch_opt_b(), Path, Upsert YOUTUBE_OAUTH_CREDENTIALS_PATH in workspace .env (no other keys touched). (+3 more)

### Community 27 - "vercel.json"
Cohesion: 0.22
Nodes (8): Run 094422e2 @ 2026-08-23T13:55:01.8456959Z, Run 0aef87c5 @ 2026-06-28T22:51:38.4246629Z, Run 28a5dcff @ 2026-07-12T13:55:01.1253146Z, Run 34962700 @ 2026-07-26T13:55:01.3961575Z, Run 668e4fe2 @ 2026-08-16T13:55:01.4086006Z, Run c68d91ea @ 2026-08-02T13:55:01.4671717Z, Run e433f268 @ 2026-07-19T13:55:01.7391234Z, Run f0c9c122 @ 2026-08-09T13:55:15.6463490Z

### Community 28 - "REVENUE_SUMMARY.md"
Cohesion: 0.25
Nodes (7): maxDuration, buildCommand, framework, functions, api/index.py, outputDirectory, rewrites

### Community 29 - "gumroad_upload.py"
Cohesion: 0.43
Nodes (6): append_audit(), gumroad_create_product(), load_config(), main(), Path, Create a product on Gumroad via API.

### Community 30 - "auto_upload.js"
Cohesion: 0.40
Nodes (3): fs, https, path

### Community 31 - "read_json"
Cohesion: 0.67
Nodes (3): main(), Path, read_json()

## Knowledge Gaps
- **156 isolated node(s):** `fs`, `path`, `https`, `Settings`, `buildCommand` (+151 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_config()` connect `load_config` to `opt_d_alerts.py`, `preflight.py`, `opt_f_discovery.py`, `ZoneInfo`, `sleep_orchestrator.py`, `opt_a_digital_factory.py`, `opt_b_faceless_shorts.py`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `IsPlaceholderTests` connect `IsPlaceholderTests` to `main`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `ZoneInfo` (e.g. with `main()` and `main()`) actually correct?**
  _`ZoneInfo` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `main()` (e.g. with `emit()` and `ZoneInfo`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `fs`, `path`, `https` to the rest of the system?**
  _156 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06290471785383904 - nodes in this community are weakly interconnected._
- **Should `opt_d_alerts.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06845513413506013 - nodes in this community are weakly interconnected._