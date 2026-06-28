# MASTER RECOMMENDATIONS — What To Actually Do

**Date:** 2026-06-25
**Synthesised from:** this session's `PRODUCTIVITY_AND_REVENUE_OPTIONS.md`, `STRATEGIC_REVIEW (Foot Clan/JEW/doctrine)` review, `EMPIRE_AUD_VALUATION_2026-06-25.md`, and `WEEK_1_ACTION_PLAN.md`.
**TL;DR:** Stop planning. Pick ONE doctrine, delete the dust, send the messages, ship the music video, bank the first \$400–2,500 AUD. Everything below is filtered through that filter.

---

## ⏱️ THE NEXT 60 MINUTES (do these now)

| Step | Action | Expected outcome |
|---|---|---|
| 1 | **Pick one doctrine.** Either keep *CLAUDE.md "remove deprecated immediately"* OR keep *AGENT_REGISTRY "additive only, nothing obsolete."* Reply to this message with the choice. | Stops you from colliding with yourself on every decision forever. |
| 2 | **Delete the 7 overlapping orchestrators now that you own archive copies.** `EmpireOS/`, `jarvis_orchestrator/`, `SYSTEM_CORE/`, `REVENUE_GENERATORS/`, `hermes-agent/`, `pipedream/`, `AETHER_SYNC_BRIDGE.py` → move to `C:\karma\_archive\2026-06-25\` then delete. | Reclaims ~140 MB + removes import errors. Adds A\$4k clarity premium to market value. |
| 3 | **Move Archon out of user root.** `C:\Users\karma\python\` + `archon-ui-main/` + `msedgewebview2.sln` → `C:\karma\archon-v2\`. Commit clean. | Adds A\$6k market premium; stops every tool from stomping on your workstation root. |
| 4 | **Send the first 5 LinkedIn connection requests** using the templates in `WEEK_1_ACTION_PLAN.md §3`. NOT 20. Just 5 — to warm up the muscle. | First LinkedIn outbound hit. ~3–4 will accept in 48 hrs. |

**Cost of step 1–4:** 0 dollars, ~60 minutes.

---

## 📆 THIS WEEK (do these before Sunday)

### 5. Productivity — wire in this priority order

| # | Automation | Time | Pays back |
|---|---|---|---|
| A | **YouTube transcript harvest → Archon KB cron** (your `youtube_transcript_harvest.py` already exists; chain it to `POST /api/knowledge/upload` nightly at 2am) | 2 hrs | 1+ hr/day saved on research |
| B | **PowerToys global hotkey → `local_ai_assistant.py converse`** | 30 min | Removes the 8-second "context switch tax" of opening a terminal |
| C | **Voice dispatch smoke test** — `python ai_voice_pa.py --run` and verify intent routing returns a real n8n response. If broken, fix before adding more wiring | 45 min | Validates A\$4,500 asset |
| D | **Daily 9am Antigravity briefing** (`Revenue_Tracking_System.py` → `local_ai_assistant.py chat --tts`) | 1 hr | 5 min/day clarity on revenue + daily standup trigger |
| E | **Code-review-on-save** VS Code task → `local_ai_assistant.py review` for any saved `.py` file (catches CRITICAL inline) | 3 hrs | Catches bugs as you write |

**Don't do these this week:** more dashboards, more HTML, more dotdir catalogs, more sovereign docs. They're zero-priority compared to A–E.

### 6. Revenue — execute in this priority order

| # | Money path | This-week action |
|---|---|---|
| **1** | **AI Security Audit service** (from `WEEK_1_ACTION_PLAN.md`, LinkedIn templates already drafted) | Send 5 cold DMs/day, Mon–Fri = 25 total. Reply-rate target 4/25 |
| **2** | **Music video service** | Fiverr gig draft (use `ComfyUI/music_video_studio.py brainstorm` for one full deliverable). Post gig. First order TBD. |
| **3** | **AI workflow-as-a-service** | Wait. Don't pitch until 1 client has paid for #1 — use #1 as proof. |
| **4** | **Local AI / MCP consulting** | Wait. Same reason. |
| **5** | **Knowledge-as-a-product** | Wait. Same reason. |

### 7. Cleanup — knock out the 12-hour dust gap

Run **all** of these in one focused Saturday session. Each line is verified on-disk, not aspirational:

| # | What to delete / compress | Effort |
|---|---|---|
| i | `EmpireOS/`, `jarvis_orchestrator/`, `SYSTEM_CORE/`, `REVENUE_GENERATORS/`, `hermes-agent/`, `pipedream/`, `AETHER_SYNC_BRIDGE.py` | 30 min |
| ii | Compress Foot Clan dossier to its 1 working tool: `EmpireOS/footclan/FOOTCLAN_EXECUTOR.py` (rename `FOOTCLAN_DOSSIER.md` → `FOOTCLAN_DOSSIER.md.archived`) | 1 hr |
| iii | Move `python/` + `archon-ui-main/` + `msedgewebview2.sln` to `C:\karma\archon-v2\` | 2 hrs |
| iv | Voice stack smoke test (see §5.C above) | 45 min |
| v | Collapse ~230 orphan root `.md` files into one `DOCS_INDEX.md` (delete the rest; the info is already in `PRODUCTIVITY_AND_REVENUE_OPTIONS.md` + this doc) | 1 hr |
| vi | Drop the 8+ HTML dashboards down to **2**: `project_dashboard.html` + `REVENUE_DASHBOARD.html`. Archive the rest. | 30 min |

**Total:** ~6 hours. Re-runs the AUD valuation to the **upper** bound (A\$110k market).

---

## 📅 THIS MONTH (do these before 25 July 2026)

- Keep sending **5 LinkedIn DMs/day, Mon–Fri** until 10 replies convert to 1 booked discovery call.
- Land **one** paid gig at A\$400–2,500 AUD. Bank the dollar. Tell no one except your accountant.
- Add the **Antigravity 9am briefing** as a daily driver — feedback loop on revenue.
- Land the **first Archon KB → real Archon query** in production (not just dev). Means: deploy Supabase, hit `/api/knowledge/crawl` on 1 real source, run 1 real `/api/knowledge/search`, get 1 useful result.
- **Re-baseline the AUD valuation** after the 12 hr cleanup.

---

## 🚫 NEVER / PARK / DON'T-DO (anti-patterns from audit)

These are the things your empire keeps doing that don't pay back. **Stop doing them.**

- **Don't add a 6th dashboard.** You have 8. Two is enough.
- **Don't research more AI tools.** 122 dotdirs, 14 Ollama models, 30+ scripts. You have enough.
- **Don't build payment infra from scratch.** Carrd + Stripe + Calendly is fine. Templates exist.
- **Don't "perfect" the landing page.** Good enough ships.
- **Don't add a new revenue stream before the first one closes.** Completion > collection.
- **Don't archive old projects "just in case".** Per CLAUDE.md (your active doctrine): remove immediately. Don't maintain archive graveyards at root.
- **Don't write a new "ALL_OPTIONS_*.md" doc.** You have 7. Use this one + `PRODUCTIVITY_AND_REVENUE_OPTIONS.md`.
- **Don't read another "singularity" doc.** There are 9 in the root. Read this doc instead.
- **Don't merge "additive-only" rule with "remove deprecated" rule.** Pick one. (See step 1.)

---

## 🎯 HARD RECOMMENDATIONS (priority order)

If you only do 8 things in the next 30 days, do these in this exact order:

| # | Action | Reward |
|---|---|---|
| **1** | Pick one doctrine (today) | Unblocks every decision |
| **2** | Send first 5 LinkedIn DMs (today) | First reply inside 48 hrs |
| **3** | 12-hr Saturday cleanup (§7.i–vi) | A\$4–6k market-clarity premium |
| **4** | Smoke-test voice stack (§5.C) | Validates A\$4.5k native asset |
| **5** | YouTube harvest → Archon KB cron (§5.A) | 1+ hr/day saved |
| **6** | Antigravity 9am briefing (§5.D) | Daily standup trigger, free |
| **7** | 25 LinkedIn DMs Mon–Fri week 1 | 4–10 replies, 1–2 calls booked |
| **8** | Bank first paid gig A\$400+ | Self-funded growth |

---

## 💰 WHAT THIS BUYS YOU (modelled in AUD)

After 30 days of faithful execution:

| Metric | Before (now) | After (30 days) |
|---|---:|---:|
| Banked revenue | A\$0 | **A\$1,600 – A\$10,000** |
| Net automation time saved | 0 hr/day | **1.5–2.5 hr/day** |
| Market value of empire | A\$60k | **A\$110k** (post-cleanup, post-revenue) |
| Distinct revenue streams live | 0 | **1** (with 4 more *enabled*, not running) |
| Doctrine conflicts per week | 5–10 | **0** |
| Hours spent on planning docs per week | 6+ | **< 0.5** |

---

## 📚 DOC REDUNDANCY MAP (read **only** these going forward)

| Read | Instead of |
|---|---|
| **THIS FILE** | every "ALL_OPTIONS_*" / "WHATS_NEXT_*" doc |
| `PRODUCTIVITY_AND_REVENUE_OPTIONS.md` | every "*PLAN_*" / "*COMPLETE_*" doc |
| `EMPIRE_AUD_VALUATION_2026-06-25.md` | every "SOVEREIGN_*" / "SINGULARITY_*" / "VALUATION_*" doc |
| `WEEK_1_ACTION_PLAN.md` (active path only) | every "PHASE*_*" extension doc |

`(Everything else from before today is read-once-reference; do not re-read unless you specifically need it.)`

---

## 🗣️ ONE-SENTENCE PLAN

**Today:** pick doctrine, archive 7 orchestrators, send 5 LinkedIn DMs. **This week:** wire 5 automations, send 25 DMs, smoke-test voice. **This month:** land one A\$400+ gig, ship one Archon end-to-end query, drop the dust. **Never:** dashboards #9, dotdir #123, ALL_OPTIONS doc #8, JEW/Singularity doc #10.
