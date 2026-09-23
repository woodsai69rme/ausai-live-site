# SLEEP_CASH_SYSTEM — Master Index



> **Generated:** 2026-06-30

> **System Version:** 1.0

> **Operator:** Karma (Australia, RTX 4060 8GB, 64GB RAM)

> **Goal:** Autonomous 24/7 income generation with zero approvals, real AUD, runs while you sleep



---



## 🚀 Quick Start



```batch

REM Launch all services & tests:

LAUNCH_SLEEP_CASH.bat status        REM Check system status

LAUNCH_SLEEP_CASH.bat preflight     REM Per-Lane readiness (credentials + services)

LAUNCH_SLEEP_CASH.bat dry-run       REM Run SLEEP_TRIPLE dry-run

LAUNCH_SLEEP_CASH.bat api           REM Start YouTube Transcript API

LAUNCH_SLEEP_CASH.bat monitor       REM Poll live API health (set DISCORD_WEBHOOK_URL for alerts)

LAUNCH_SLEEP_CASH.bat monitor-probe-all  REM Single-shot multi-service probe (live API + ComfyUI + Ollama)

LAUNCH_SLEEP_CASH.bat install-monitor [opts]  REM Wrapper for install_monitor_scheduler.bat (--dry-run / --uninstall supported)

LAUNCH_SLEEP_CASH.bat test-all      REM Run all tests

LAUNCH_SLEEP_CASH.bat schedule      REM Install scheduled tasks (admin)

```



**Live URL:** https://yt-transcript-api-ebon.vercel.app (YouTube Transcript API)



---



## 📋 The 5-Lane System



| Lane | Name | Status | Capital | Revenue/mo (Month 6) |

|---|---|---|---|---|

| 🚦 **1** | AI Digital Products (Gumroad) | ✅ Code ready | A$0 | A$18 |

| 🚦 **2** | Faceless YouTube + Affiliate | ✅ Code ready | A$0 | A$385 |

| 🚦 **3** | Print-on-Demand (Shopify+Printful) | ✅ Code ready | A$0 | A$25 |

| 🚦 **4** | API-as-a-Service (YouTube Transcript) | ✅ **LIVE on Vercel** | A$0 | A$875 |

| 🚦 **5** | Crypto Yield (Freqtrade) | ✅ Code ready | A$500+ | A$100 |

| | | | **TOTAL** | **A$1,403** |



See `SLEEP_CASH_SYSTEM.md` for full plan with GitHub awesome list deep dive.



---



## 📚 Documentation Map



### Session Documentation

| Document | Purpose |

|---|---|

| `FREEBUFF_SESSIONS_REVIEW.md` | Complete review of all 41 freebuff sessions |

| `SESSION_COMPLETE_DOCUMENTATION.md` | Full session record (phases 1-6) |

| `OUTSTANDING_WORK_PLAN.md` | Plan to finish all incomplete session workstreams |

| `SLEEP_CASH_SYSTEM.md` | Master 5-lane autonomous income system plan |



### Action Plans

| Document | Purpose |

|---|---|

| `SLEEP_CASH_GO_LIVE_CHECKLIST.md` | Step-by-step manual actions for user |

| `README_SLEEP_CASH.md` | This file — master index |



### Code Files

| File | Purpose | Status |

|---|---|---|

| `LAUNCH_SLEEP_CASH.bat` | Unified Windows launcher | ✅ NEW |

| `SLEEP_TRIPLE/opt_e_pod.py` | Print-on-Demand module (Lane 3) | ✅ NEW |

| `SLEEP_TRIPLE/opt_e_config.json` | POD configuration | ✅ NEW |

| `SLEEP_TRIPLE/test_opt_e_pod.py` | POD module smoke tests | ✅ NEW |

| `SLEEP_TRIPLE/test_preflight.py` | Preflight placeholder / lane-status / exit-code unit tests (21 PASS) | ✅ NEW |

| `SLEEP_TRIPLE/preflight.py` | Per-Lane readiness checker (creds, services, live API) | ✅ NEW |

| `SLEEP_CASH_API/youtube_transcript_api_service.py` | FastAPI micro-SaaS (Lane 4) | ✅ **LIVE** on Vercel |

| `SLEEP_CASH_API/test_yt_transcript_api.py` | API smoke tests | ✅ NEW |

| `SLEEP_CASH_API/test_monitor.py` | Monitor probe / Discord-post / exit-code unit tests (14 PASS) | ✅ NEW |

| `SLEEP_CASH_API/monitor.py` | Live API health monitor (Discord webhook optional) | ✅ NEW |

| `SLEEP_CASH_API/requirements.txt` | Python dependencies | ✅ NEW |

| `SLEEP_CASH_API/README.md` | API documentation | ✅ NEW |

| `SLEEP_CASH_API/vercel.json` | Vercel deploy config | ✅ NEW |

| `.github/workflows/sleep-cash-preflight.yml` | GitHub Actions preflight CI gate (per-Lane summary in $GITHUB_STEP_SUMMARY) | ✅ NEW |

| `install_monitor_scheduler.bat` | Auto-elevating standalone scheduled-task installer (--uninstall / --dry-run, MONITOR_INTERVAL digit-validation; now installs BOTH `SLEEP_CASH\Monitor` AND `SLEEP_CASH\ProbeAll`) | ✅ NEW |



### Modified Files

| File | Change |

|---|---|

| `SLEEP_TRIPLE/sleep_orchestrator.py` | Added opt_e module + --skip-e flag |

| `SLEEP_TRIPLE/sleep_config.json` | Added option "e" |

| `SLEEP_TRIPLE/opt_a_config.json` | Added gumroad_api_key placeholder, enable_comfy_cover=true |

| `SLEEP_TRIPLE/opt_b_config.json` | Added YouTube OAuth path + edge-tts config |

| `LAUNCH_SLEEP_CASH.bat` | Added `preflight` and `monitor` commands + Usage header / menu updates |



---



## ✅ What's Live Now (No User Action Required)



- ✅ **YouTube Transcript API** — deployed to https://yt-transcript-api-ebon.vercel.app

- ✅ **Edge-TTS** — installed and tested with Australian English voice

- ✅ **POD Module** — tested dry-run, generates AI designs via Ollama

- ✅ **Orchestrator** — runs 4 SLEEP_TRIPLE modules sequentially

- ✅ **All test suites** — fully deterministic: 10 API tests + 10 POD tests passing, with mocks for YouTube, Ollama, and ComfyUI to isolate the test surface from external flake

- ✅ **6 signup pages** — opened and verified for user to create accounts

- ✅ **Pre-flight tool** — `python SLEEP_TRIPLE/preflight.py` (or `LAUNCH_SLEEP_CASH.bat preflight`) shows current per-Lane readiness, services, and credential placeholders

- ✅ **API monitor** — `python SLEEP_CASH_API/monitor.py` (or `LAUNCH_SLEEP_CASH.bat monitor`) polls /healthz; set `DISCORD_WEBHOOK_URL` to enable alert pings after N consecutive failures. See also: **Multi-service probe** below for single-shot aggregate checks.

- ✅ **Multi-service probe** — `python SLEEP_CASH_API/monitor.py --probe-all` does a single-shot aggregate health check across the live Vercel API + ComfyUI :8188 + Ollama :11434. Exits 1 if any target unreachable. Does not auto-Discord-post (single-shot slow service would spam the channel); see the **API monitor** above if you want Discord pings after `--discord-threshold` consecutive failures.

- ✅ **Scheduler dry-run** — `install_monitor_scheduler.bat --dry-run` prints the would-be `schtasks /create` invocations for BOTH `SLEEP_CASH\Monitor` AND `SLEEP_CASH\ProbeAll` without installing. Re-uses the same `:no_python`/`:no_monitor` guards as the install path, so the preview is honest (errors out cleanly if either is missing). Also reachable via `LAUNCH_SLEEP_CASH.bat install-monitor --dry-run` (delegates via `shift /1`, forwards args to the standalone bat).



## 🛫 Pre-flight Readiness (today)



```

Lane 1: [NEEDS_CONFIG]   AI Digital Products (Gumroad) — gumroad_api_key placeholder

Lane 2: [NEEDS_CONFIG]   Faceless YouTube + Affiliate — youtube_oauth_credentials_path placeholder

Lane 3: [BLOCKED]        Crypto Yield (Freqtrade observation) — observation-only by design

Lane 4: [OK]             API-as-a-Service (YouTube Transcript) — LIVE on Vercel

Lane 5: [NEEDS_CONFIG]   Print-on-Demand (Shopify + Printful) — 3 credential placeholders after account signup

```



Run `LAUNCH_SLEEP_CASH.bat preflight` any time to re-check. Lane 4 is the only Lane publishable today; Lanes 1/2/5 are code-ready and unblock the moment you paste your API keys into the corresponding `REPLACE_WITH_*` fields.



## ⏳ What YOU Need To Do



| # | Action | Time |

|---|---|---|

| 1 | Create Gumroad account + get API key | 15 min |

| 2 | Create YouTube channel + Google Cloud OAuth | 30 min |

| 3 | Set up Stripe for API billing | 20 min |

| 4 | Register ABN at abr.gov.au | 15 min |

| 5 | Sign up Shopify + Printful | 30 min |



See `SLEEP_CASH_GO_LIVE_CHECKLIST.md` for complete step-by-step instructions.



---



## 🧪 Testing



```bash

# Run all tests

LAUNCH_SLEEP_CASH.bat test-all



# Individual suites

python SLEEP_CASH_API/test_yt_transcript_api.py

python SLEEP_TRIPLE/test_opt_e_pod.py

python SLEEP_TRIPLE/_smoke_retry.py



# Per-Lane readiness (credentials, services, live API)

python SLEEP_TRIPLE/preflight.py



# Continuous API health monitor (Ctrl+C to stop)

python SLEEP_CASH_API/monitor.py

python SLEEP_CASH_API/monitor.py --interval 30

python SLEEP_CASH_API/monitor.py --once

MONITOR_INTERVAL=120 DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/... python SLEEP_CASH_API/monitor.py

```



**Single-shot / preview probes (no loop, no install):**



```bash

python SLEEP_CASH_API/monitor.py --probe-all

install_monitor_scheduler.bat --dry-run

```



---



## 🔒 CI / Pre-publish Gate



`tolerant preflight.py` is the standard CI gate. Run `--strict` before any

live publish or as a scheduled job; a non-zero exit means **do not publish**.



### GitHub Actions (or any CI)



```yaml

- name: SLEEP_CASH pre-flight gate

  run: python SLEEP_TRIPLE/preflight.py --strict

```



### Local pre-publish hook (batch)



```bat

REM Guard against publishing during a quiet Lane outage.

python SLEEP_TRIPLE\preflight.py --strict

if errorlevel 1 (

    echo [pre-publish] ABORT - fix Lane readiness before --run.

    exit /b 1

)

```



### JSON parsing example (jq)



```bash

python SLEEP_TRIPLE/preflight.py --json | jq '.lanes[] | select(.publishable == false) | {lane: .num, status, summary}'

```



### Exit codes



| Code | Meaning |

|---|---|

| 0 | All 5 Lanes `[OK]` (or `--strict` not set) |

| 1 | `--strict` set and at least one Lane is `[NEEDS_CONFIG]`, `[BLOCKED]`, or `[OFFLINE]` |



---



## 💰 Revenue Projections



| Month | Conservative | With Marketing |

|---|---|---|

| Month 1 | A$33 | A$200 |

| Month 3 | A$322 | A$1,500 |

| Month 6 | A$1,403 | A$3,500 |

| Month 12 | A$5,401 | A$10,000+ |



---



## 🔗 Live URLs



- **YouTube Transcript API:** https://yt-transcript-api-ebon.vercel.app

- **Swagger Docs:** https://yt-transcript-api-ebon.vercel.app/docs



---



## 📂 File Sizes (this session)



| File | Size |

|---|---|

| `FREEBUFF_SESSIONS_REVIEW.md` | 14.5 KB |

| `SLEEP_CASH_SYSTEM.md` | 27.2 KB |

| `OUTSTANDING_WORK_PLAN.md` | 10.7 KB |

| `SLEEP_CASH_GO_LIVE_CHECKLIST.md` | 6.8 KB |

| `SESSION_COMPLETE_DOCUMENTATION.md` | 16.0 KB |

| `README_SLEEP_CASH.md` | This file |

| `SLEEP_TRIPLE/opt_e_pod.py` | 15.0 KB |

| `SLEEP_TRIPLE/test_opt_e_pod.py` | 8 KB |

| `SLEEP_TRIPLE/preflight.py` | 5 KB |

| `SLEEP_CASH_API/youtube_transcript_api_service.py` | 12.4 KB |

| `SLEEP_CASH_API/test_yt_transcript_api.py` | 5 KB |

| `SLEEP_CASH_API/monitor.py` | 4 KB |

| `LAUNCH_SLEEP_CASH.bat` | 7 KB |



---



---



## Verbose preflight examples



Per-Lane detail (creds / services / vitals with [OK] / [FAIL] marks):



```bash

python SLEEP_TRIPLE/preflight.py --verbose

python SLEEP_TRIPLE/preflight.py --strict --verbose

LAUNCH_SLEEP_CASH.bat preflight --verbose

```

*End of README_SLEEP_CASH.md*

