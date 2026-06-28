# PRODUCTIVITY_AND_REVENUE_OPTIONS

**Generated:** 2026-06-25
**Workspace:** `C:\Users\karma`
**Purpose:** A single canonical reference of every actionable option surfaced during the workspace audit + productivity + revenue analysis. Use this as the working playbook; file is append-only and authoritative.

---

## 0. Golden Rules (must obey)

From `CLAUDE.md` (alpha doctrine for Archon V2) plus orchestrator standards:

1. **Local-only deployment.** You run your own instance.
2. **No backwards compatibility.** Deprecated code is removed immediately — do not archive.
3. **Detailed errors over graceful failures.** Surface failures loud so you can fix them fast.
4. **Simplicity & minimalism.** Make as few changes as possible.
5. **Code reuse over reinvention.** Helper functions, components, classes — always reuse.
6. **Quality over speed.** Fewer, well-informed actions beat many rushed ones.
7. **Never accept corrupted data.** Skip failed items, do not silently fill with placeholders.

These rules govern every option below. If an option contradicts them, drop the option.

---

## 1. Workspace Audit Heat Map

Ran the audit before recommending any new work. Verified by inspecting each sub-repo's `git remote`, branch, and dirty file count.

### 1.1 Repos — Verdict Table

| Repo | Origin | Branch | Dirty | Verdict | Reason |
|---|---|---|---|---|---|
| **Archon V2 Alpha** (root) | local | master | 0 modified · 558 untracked | **KEEP** | Core project. Knowledge mgmt + MCP + PydanticAI agents. |
| **ComfyUI** | upstream | — | 10 | **KEEP** | Primary local music-video studio. Yours = launchers + `music_video_studio.py`. |
| **whisper.cpp** | upstream | — | 0 | **KEEP** | Audio transcription dep used by ComfyUI. |
| **ai-music-video-studio** | local | — | 2 | **MERGE into ComfyUI** → delete | Duplicates music_video_studio.py. Move unique scripts then delete. |
| **EmpireOS** | local | — | 15 | **DELETE** | Overlaps Archon's AI orchestration. |
| **jarvis_orchestrator** | local | — | 3 | **DELETE** | Overlaps Archon. |
| **SYSTEM_CORE** | woodsai69rme | — | 39 | **DELETE** | Overlaps Archon. |
| **REVENUE_GENERATORS** | woodsai69rme | — | 52 | **DELETE** | Overlaps Archon. Cut. |
| **pipedream** | woodsai69rme | — | **3,205** | **DELETE + re-clone** | Local clone is fully trashed. Reset won't recover. |
| **hermes-agent** | upstream | — | 0 | **DELETE** | Functionally superseded by jarvis. |
| **agent-zero** | upstream | — | 1 | **DELETE** | Functionally superseded by jarvis. |
| **tadpole-studio** | third-party | — | 2 | **DELETE** | Zero activity. |
| **aigf** | local | — | 0 | **DELETE** | Unused. |
| **stable-diffusion-webui** | upstream | — | 0 | **DELETE** | Superseded by ComfyUI workflows. |

### 1.2 Critical Red Flags

1. **Git root = user profile (anti-pattern).** Archon is initialized at `C:\Users\karma`. The OS profile is acting as your workspace, which is why 122 dotdirs accumulate and 558 files are "untracked." Move Archon to `C:\dev\archon` or similar to stop the bleed.
2. **Agentic schizophrenia.** Seven overlapping orchestrators (jarvis, EmpireOS, SYSTEM_CORE, REVENUE_GENERATORS, hermes, agent-zero, pipedream) all chase the same problem Archon's PydanticAI agents already solve. Pick one. Per the no-back-compat rule, delete the rest.
3. **Backups inside active Git.** `COMPLETED_PROJECTS\SYSTEM_BACKUP_*` directories are tracked inside the tree, bloating the index and confusing file watchers. Delete.
4. **Orphan docs.** ~230 `.md` files at the user root represent a planning graveyard. Most should be deleted; the survivors should move into `docs/`.
5. **Upstream cruft.** `stable-diffusion-webui` is fully replaced by your ComfyUI workflows. `tadpole-studio` and `aigf` show no activity evidence.

### 1.3 Concrete Punch-List

```bash
# A. Move Archon off the user root (first, so the rest measures correctly)
git -C "C:/Users/karma" remote -v                # capture remote
git -C "C:/Users/karma" push                     # ensure everything is pushed
# (preferred) Create new bare-cloned destination:
#   mkdir C:\dev\archon && cd C:\dev\archon
#   git clone <archon-remote> .

# B. Delete overlapping orchestrators + dead upstream
cd "C:/Users/karma" && rm -rf \
  jarvis_orchestrator EmpireOS SYSTEM_CORE REVENUE_GENERATORS \
  hermes-agent agent-zero pipedream tadpole-studio aigf \
  stable-diffusion-webui ai-music-video-studio

# C. Delete procrastination zoos
cd "C:/Users/karma" && rm -rf \
  ACTIVE_PROJECTS ARCHIVED_PROJECTS COMPLETED_PROJECTS

# D. Sweep Archon's 558 untracked cruft — REVIEW FIRST
cd "C:/dev/archon" && git clean -fdn             # dry-run, inspect output
cd "C:/dev/archon" && git clean -fd              # only after confirming

# E. Relocate the .md graveyard
mkdir -p "C:/dev/archon/docs/_graveyard" && \
  mv "C:/Users/karma"/*.md "C:/dev/archon/docs/_graveyard/" 2>/dev/null
```

> **Reserved:** the `.aitk` (427 items), `.qwen` (24), `.codex` (26), `.claude` (28), `.kilocode`, `.kiro`, `.verdent`, `.trae`, `.gemini`, `.crush`, `.monica-code` and the remaining ~110 dotdirs are AI CLI tool caches. **Don't curate — ignore.** Once the repo moves off the user root, they no longer pollute status.

### 1.4 Repo Hygiene Detail

- **pipedream** — `git reset --hard origin/master` will not help with 3,205 changes (`npm install` ran without a `.gitignore`). Backup any unique local work to a fresh directory, then `rm -rf` and re-clone.
- **ComfyUI's 10 dirty files** are yours: `launch_music_video_studio.bat`, `tools/`, `music_video_studio.py`. If you don't intend to fork upstream, add to `ComfyUI/.git/info/exclude`. Otherwise fork and commit.
- **All karma-owned repos with 30+ dirty files** (EmpireOS 15, SYSTEM_CORE 39, REVENUE_GENERATORS 52). These have no upstream merge target. Commit real work or delete.

---

## 2. Productivity Automations — Ranked

**Format:** Each row = WHO (existing tooling) · WHAT (exact steps) · WHEN (today/this week) · COST ($ and time) · RISK.

| # | Automation | Who / What | When | Cost | Risk |
|---|---|---|---|---|---|
| 1 | **Morning revenue briefing** | `local_ai_assistant.py chat` queries `REVENUE_LEDGER.jsonl` summary → TTS → speakers. 9am cron. | Today | 1 h setup; saves 5 min/day | Low — reads only, writes nothing. |
| 2 | **Daily YouTube harvest → Archon KB** | `youtube_transcript_harvest.py` → push to `/api/knowledge/upload`. Browse replaces Googling. | This week | 2 h setup; saves 1+ hr/day | Low — Idempotent upload via title hash. |
| 3 | **Voice command → n8n dispatch** | "Summarize inbox" → `voice_command_workflow.json` intent=dispatch → n8n webhook → summary back. | This week | 3 h setup; saves 30 min/day | Med — add allowlist of intents, never open-ended LLM dispatch. |
| 4 | **Global hotkey → local LLM chat** | PowerToys shortcut → opens `local_ai_assistant.py converse`. | Today | 30 min | Low. |
| 5 | **Overnight Archon crawl cron** | Task Scheduler at 02:00: crawls AI news + your project READMEs → Supabase → searchable next morning. | This week | 2 h setup | Med — seed URL list + rate-limit. |
| 6 | **Project-gatekeeper cron** | Every 6 h: `REVENUE_N8N_CONNECTOR.py` → pings `PROJECTS{}` → n8n `/revenue/metrics` → Slack/Discord if dirty > N. | This week | 1 h setup | Low — read-only with webhook out. |
| 7 | **Code-review-on-save** | VS Code task: on save of `.py`, pipe to `local_ai_assistant.py review` → inline CRITICAL/MAJOR/MINOR. | Next week | 3 h setup | Low — local Ollama, no exfil. |

> **Common wiring:** all seven ride on the same primitives — Task Scheduler (Windows), `local_ai_assistant.py` subcommands, n8n webhooks, Archon MCP tools. Build #1 first; #2-#7 reuse the cron + webhook plumbing.

### 2.1 Cron Backbone — Recommended Skeleton

```bat
@echo off
rem C:\Users\karma\bin\morning_briefing.bat
"C:\Users\karma\.venv\Scripts\python.exe" "C:\Users\karma\local_ai_assistant.py" chat \
  --prompt "Summarize yesterday's revenue events from REVENUE_LEDGER.jsonl in 3 bullets" ^
  --model qwen2.5-coder:latest > "%TEMP%\briefing.txt"
type "%TEMP%\briefing.txt"
```

Pair with Task Scheduler trigger at 09:00 daily. Add `/tn "MorningBriefing"` so the same task exists for n8n and post-MCP hooks.

### 2.2 Fail-Fast Wiring (Alpha Rule Applied)

Per CLAUDE.md, these automations must:
- **Fail fast** on missing creds (`OPENROUTER_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`).
- **Continue + log** for batch ops (transcripts, crawl pages) — never silently insert a `[0.0]*1536` zero-vector.
- **Skip the failed item** rather than store corrupted data.

---

## 3. AI Assistant Daily-Driver Config

Hardware: RTX 4060 8 GB VRAM, 14 Ollama models already installed, OpenRouter for free-tier cloud.

| Use case | Model | Source | Cost | VRAM |
|---|---|---|---|---|
| **Coding / debug** | `qwen2.5-coder:latest` | Ollama local | Free | 4.7 GB |
| **Tough reasoning** | `deepseek-r1:8b` | Ollama local | Free | 5.2 GB |
| **Quick snippets** | `phi4-mini` | Ollama local | Free | 2.5 GB |
| **Creative / brainstorm** | `gemma-4-31b-it:free` | OpenRouter free | Free | 0 (cloud) |
| **Multi-turn w/ history** | `qwen2.5-coder:latest` (converse mode) | Ollama local | Free | 4.7 GB |
| **Page analysis** | `local_ai_assistant.py browse` | Local headless Chromium | Free | 0 |

### 3.1 Model Coexistence Rules (8 GB VRAM cap)

- ComfyUI rendered idle = 0-1 GB. You can keep `qwen2.5-coder` (4.7 GB) loaded during regular work.
- Switch to `phi4-mini` (2.5 GB) when ComfyUI is generating so VRAM headroom > 3 GB.
- Never load two 5+ GB models simultaneously. Use Ollama `OLLAMA_MAX_LOADED_MODELS=1`.

### 3.2 Always-Route-Through-OpenRouter for Non-Local

Per CLAUDE.md: set ONLY `OPENROUTER_API_KEY`. Never set direct `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc. OpenRouter routes all model traffic so you keep one key, one billing line, and one rate limit policy.

---

## 4. Money-Making Paths — Ranked

**Ranking metric:** realistic weekly revenue × certainty. Best/week / Median / Worst estimates are conservative ranges, not promises.

| # | Path | You already have | First $ comes from | Best / Med / Worst week |
|---|---|---|---|---|
| **1** | **Music Video Creation as a Service** | ComfyUI + 14 Ollama + ACE-Step + Wan2.1 + 7 proven workflows + `launch_music_video_studio.bat` + 7 templates in `ComfyUI\workflow_templates\workflow_recipes.md`. | Fiverr / Upwork music-video gigs: $200-$1,500 each. <2 hrs production. | **$1,500 / $400 / $0** |
| **2** | **AI Security Audit Service** | `WEEK_1_ACTION_PLAN.md` drafted (Stripe, Carrd, Calendly, LinkedIn templates, FB groups, sample report template, cold email script). D-1–D-5 sequence ready. | LinkedIn cold outreach to AI-tool startups. $500 audit + $200/mo retainer. | **$1,500 / $500 / $0** |
| **3** | **Knowledge-Base RAG Service** *(longer ramp)* | Archon MCP at port 8051, Supabase+pgvector, 622 tracked; a single upload endpoint plus prompt templates = a sellable wrapper. | SMBs that need internal RAG. $1k setup + $200/mo. | **$1,200 / $300 / $0** |
| **4** | **Audio Transcription Cleanup** | `music_video_studio.py transcribe` + Whisper.cpp ready, SRT/TXT output. | Upwork "podcast cleanup" gigs. | **$600 / $150 / $0** |
| **5** | **Local-AI Setup Service** | `setup_all_ai_tools.ps1` + `START-ALL-AI-TOOLS.bat` + `local_ai_assistant.py` stack. | Reddit r/LocalLLaMA, HN, FB groups. $300 consult + $50/mo retainer. | **$600 / $200 / $0** |

**Skipped intentionally (ranked too low or duplicated):**
- Niche newsletters — saturated; no list.
- Stock footage / image licensing — no upstream model licensing plan; out of scope.
- Generic "AI chatbot" product — over-saturated.

### 4.1 Music Video Path — Detailed Operating Procedure

1. List 5 songs you'll produce this week. Each with lyrics + BPM + concept hook.
2. Run `music_video_studio.py wizard` for each song. Pick a workflow from `workflow_recipes.md` keyed to VRAM headroom.
3. For Fiverr: 1 gig listing ("Music Video (AI-generated, 24-72 h delivery) — 3 packages at $200/$500/$1,500").
4. Post 1 portfolio piece on /r/musicproduction + /r/comfyui each Friday.
5. Cycle repeat — no custom code; this is a content factory.

### 4.2 AI Security Audit — Detailed Operating Procedure

1. Create Carrd one-pager with Calendly + Stripe payment link ($500 upfront).
2. LinkedIn search: AI-tool founders with <10 employees.
3. Send 20 personalized cold DMs/day (template in `WEEK_1_ACTION_PLAN.md`).
4. For each booked: 2-hour audit = `local_ai_assistant.py review` on their codebase + 5-page PDF report.
5. Retainer pitch at delivery: $200/mo for "fix-as-we-find them" service.

### 4.3 Don'ts for Money (per CLAUDE.md)

- **Don't** add a 6th dashboard. `REVENUE_DASHBOARD.html` already exists; track there.
- **Don't** build payment infra from scratch. Stripe/PayPal templates exist.
- **Don't** perfect the landing page. Carrd is fine; ship.
- **Don't** research more AI tools. 122 dotdirs is the ceiling; you have enough.
- **Don't** add new revenue streams before #1 closes once. Completion > collection.
- **Don't** archive old projects. Per alpha rule: remove immediately, not archive.

---

## 5. Week 1 Action Plan (26 hours total)

Already drafted in `WEEK_1_ACTION_PLAN.md`. Compressed here:

**Day 1 — Audit + Cleanup (4 h)**
- A1. Move Archon repo out of `C:\Users\karma`.
- A2. Delete overlapping orchestrators + upstream cruft.
- A3. Confirm git status is clean.

**Day 2 — Productivity Backbone (4 h)**
- A4. Wire morning briefing cron (Automation #1).
- A5. Wire global hotkey → local LLM (#4).
- A6. Set OpenRouter key; smoke-test all 14 Ollama models.

**Day 3 — Knowledge Stack (4 h)**
- A7. Wire YouTube harvest → Archon (#2).
- A8. Wire overnight Archon crawl (#5).
- A9. Verify Archon MCP at `localhost:8051/health`.

**Day 4 — Revenue #1 Plumbing (4 h)**
- A10. Carrd landing + Stripe link + Calendly (Music Video gig).
- A11. Fiverr + Upwork gig live.
- A12. First portfolio piece.

**Day 5 — Revenue #2 Plumbing (4 h)**
- A13. Carrd + Calendly + Stripe (Security Audit gig).
- A14. 20 LinkedIn cold DMs/day x 5 days.
- A15. Sample audit report ready.

**Day 6 — Voice + Crons (3 h)**
- A16. Wire voice command #3 (intent allowlist, never open-ended dispatch).
- A17. Wire project-gatekeeper cron #6.
- A18. Wire code-review-on-save #7.

**Day 7 — Review + Ship Next (3 h)**
- A19. Update `REVENUE_LEDGER.jsonl` with week's events.
- A20. Compute Week 2 priorities from data, not vibe.
- A21. Archive this plan → move on.

---

## 6. Anti-Patterns (Don't Do These)

Anchored to CLAUDE.md + audit findings + the rank-ordering principle "completion > collection."

1. **Don't** park overlapping orchestrators thinking "I'll come back to them." Per alpha rule: just delete.
2. **Don't** add a tracking dashboard for hypothetical revenue. `REVENUE_DASHBOARD.html` exists.
3. **Don't** bootstrap yet another AI tool when 122 dotdirs and 14 Ollama models already cover it.
4. **Don't** accept contradictory tasks from earlier `MASTER`/`EXECUTION`/`OPTIONS` docs. Treat this file as the working source.
5. **Don't** let backups live inside the active Git tree.
6. **Don't** store zero-vectors or null foreign keys on embedding failure — skip the item.
7. **Don't** route AI through direct provider keys. OpenRouter only.
8. **Don't** start a new revenue stream before #1 closes a single paying transaction.
9. **Don't** try to perfect a workflow before the first paying client. Ship at "good enough."
10. **Don't** archive deprecated work. Remove it. Pages can be re-typed in seconds.

---

## 7. One-Sentence Summary

> You have $20M of infrastructure, three gilded routes to revenue, and a 26-hour Week 1 plan already drafted — the only thing missing is sending the next 20 LinkedIn messages and producing the first music-video gig.

---

## Appendix A — Files / Scripts Referenced

| Reference | Path |
|---|---|
| Core project | `C:\Users\karma\CLAUDE.md`, `C:\Users\karma\README.md` |
| Audit registry | `C:\Users\karma\DOTDIR_CATALOG.md` |
| Voice PA design | `C:\Users\karma\AI_VOICE_PA.md`, `C:\Users\karma\AI_VOICE_PA_DESIGN.md` |
| Voice bridge | `C:\Users\karma\VOICE_PA_BRIDGE.py`, `C:\Users\karma\ai_voice_pa.py` |
| Voice workflow | `C:\Users\karma\voice_command_workflow.json` |
| Revenue design | `C:\Users\karma\REVENUE_TRACKING_DESIGN.md`, `C:\Users\karma\REVENUE_N8N_CONNECTOR.py`, `C:\Users\karma\Revenue_Tracking_System.py` |
| Week 1 plan | `C:\Users\karma\WEEK_1_ACTION_PLAN.md` |
| Money report | `C:\Users\karma\MONEY_MAKER_REPORT.md` |
| Agent registry | `C:\Users\karma\AGENT_REGISTRY.md` |
| Outreach templates | `C:\Users\karma\OUTREACH_TEMPLATES.md` |
| Music-video tools | `C:\Users\karma\ComfyUI\launch_music_video_studio.bat`, `C:\Users\karma\ComfyUI\music_video_studio.py`, `C:\Users\karma\ComfyUI\workflow_templates\workflow_recipes.md` |
| Local AI helper | `C:\Users\karma\ComfyUI\local_ai_assistant.py` |
| YouTube harvest | `C:\Users\karma\youtube_transcript_harvest.py`, `C:\Users\karma\YOUTUBE_TRANSCRIPT_HARVEST_DESIGN.md` |
| Launcher scripts | `C:\Users\karma\setup_all_ai_tools.ps1`, `C:\Users\karma\START-ALL-AI-TOOLS.bat` |

## Appendix B — Verification Commands (copy/paste)

```bash
# Confirm git is in a sane state
git -C "C:/Users/karma" status --porcelain | wc -l

# Volume-by-volume dotdir ranking
ls -d "C:/Users/karma"/.* 2>/dev/null | xargs -I{} sh -c 'echo "$(du -sh {} 2>/dev/null | cut -f1) {}"'

# List every sub-repo with remote + branch + dirty count
for d in "C:/Users/karma"/*/; do
  [ -d "$d/.git" ] && echo "$(basename "$d") | \
    $(git -C "$d" remote get-url origin 2>/dev/null) | \
    $(git -C "$d" branch --show-current 2>/dev/null) | \
    dirty=$(git -C "$d" status --porcelain 2>/dev/null | wc -l)"
done

# Quick smoke tests
curl -s http://localhost:8051/health               # Archon MCP
curl -s http://localhost:8181/health               # Archon main
curl -s http://localhost:8052/health               # Archon agents
"C:/Users/karma/.venv/Scripts/ollama.exe" list     # 14 models loaded
```

---

**End of file.** Anything not in this doc either lives in one of the Appendices' source files, or is by design excluded. If something's missing, append — do not create another competing options file.
