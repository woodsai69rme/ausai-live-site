# WEEK_1_QUICKWINS.md — 30-day Execution Calendar

> **Energy budget:** 1 hr/day of focused execution is worth 5x 5 hrs/day distracted. Plan as if energy is your hardest resource.
> **Money metric:** $A0 → $A1,600-10,000 in 30 days (master plan).
> **Time metric:** 1.5-2.5 hr/day saved (master plan).

---

## Week 0 — Foundation cleanup (today + next 48 hr)

| Day      | Block        | Action                                                                                                                            | Time   | Energy  |
|----------|--------------|-----------------------------------------------------------------------------------------------------------------------------------|--------|---------|
| **Today**| 09:00-09:30  | Fix REVENUE_LEDGER.jsonl: `echo '{"ts":"'$([DateTime]::Now.ToString("o"))'","event":"day_0_start","amount_aud":0,"note":""}' >> REVENUE_LEDGER.jsonl` | 5 min  | low     |
|          | 09:30-10:30  | Open LinkedIn → 8 search queries (runbook) → collect 25 names                                                              | 60 min | medium  |
|          | 10:30-11:00  | Read 5 profiles deeply → send 5 personalized DMs                                                                              | 30 min | high    |
| **Tue**  | 09:00-09:30  | Send remaining 20 DMs (5 per morning, 4 mornings, no spam)                                                                    | 90 min | high    |
|          | 17:00-17:15  | Send 5 more DMs after lunch-block clears                                                                                       | 15 min | medium  |
| **Wed-**| evening      | Re-read CLAUDE.md & AGENT_REGISTRY.md doctrine; pick ONE (recommendation: CLAUDE.md — no-legacy, remove deprecated)            | 30 min | high    |

---

## Week 1 — Setup & first automations (destructive ops require user greenlight)

| Day      | Block       | Action                                                                                                                          | Outcome                              |
|----------|-------------|---------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| **Mon**  | 08:00-08:15 | Run `tools\06_launch_all_automations.bat` → registers 3 Scheduled Tasks (AntigravityMorningBrief 09:00, ArchonDailyCrawl 02:00, ArchonYouTubeHarvest 06:00) | **WATCH:** confirm `schtasks /Query /TN "Antigravity*"` lists 3 tasks |
|          | 08:15-08:30 | Smoke-test: `python tools/01_morning_briefing.py --tts` (no Ollama needed for first run)                                       | **Watch:** briefing prints OK       |
| **Tue**  | 09:30 (auto)| AntigravityMorningBrief fires → review output in REVENUE_LEDGER.jsonl   | **Expect:** 1 briefing entry         |
| **Wed**  | 06:00 (auto)| ArchonYouTubeHarvest fires → check Archon /api/knowledge/items for new entries | **Expect:** new YouTube items    |
| **Thu**  | 02:00 (auto)| ArchonDailyCrawl fires → check progress in archon logs               | **Expect:** new crawled sources      |
| **Fri**  | 12:00-13:00 | **Run** `tools/07_archive_overlapping_orchestrators.bat /SILENT` (the 7 orchestrators → `_archive_2026-06-25/`)               | **Recoverable:** /UNDO if needed     |
|          | 13:00-13:30 | PowerToys hotkey assign for "open Antigravity matrix" via launcher   | Visible productivity gain            |

**Week 1 acceptance gates:**
- [ ] 25 DMs sent
- [ ] 3 Scheduled Tasks registered & fire 1× each without error
- [ ] /LIST → /SILENT → archive move performed (reversible via /UNDO)

**Week 1 expected FIRST replies:**
- 3-5 LinkedIn replies (12-20% rate target)
- 1-2 booked discovery calls
- **$0 banked yet**, but pipeline > $5k AUD potential

---

## Week 2 — Convert replies → first gig

| Day      | Block        | Action                                                                                                    | Risk gate          |
|----------|--------------|-----------------------------------------------------------------------------------------------------------|---------------------|
| **Mon**  | 09:00-09:30  | Reply to all open DMs from week 1 (within 4 hour window if possible)                                       | Don't over-pitch  |
| **Tue**  | 10:00-10:30  | Discovery call #1 (if booked) — use `GIG_PICK_MATRIX.md` to decide signage of estimate                   | Pricing rule: $400 floor |
| **Wed**  | 09:00-10:00  | Discovery call #2 (if booked). Prepare 1 specific deliverable for each (not generic "AI agent")            | **Don't** promise generic AI |
| **Thu**  | 13:00-14:00  | Send signed statement of work to whoever said "send me a quote" — Stripe/USDC payment first for any new client | **Cash upfront** |
| **Fri**  | 15:00-17:00  | First paid work: deliver 1 specific scoped deliverable (e.g., one Archon RAG query wired + 1 chat to client) | **DON'T** deliver unpaid pilot |

**Week 2 acceptance gates:**
- [ ] 1-2 closed gigs (each $A400-$A2,500)
- [ ] Payment in bank (use Stripe/LemonSqueezy/USDC)
- [ ] 1 written testimonial from first client

**Week 2 expected first revenue:** **$A1,500-$A4,000**

---

## Week 3 — Double down + second gig

| Day     | Block        | Action                                                                                                |
|---------|--------------|-------------------------------------------------------------------------------------------------------|
| **Mon** | 09:00-09:30  | Re-survey replies: conversions → ask each "anybody you know has this problem?" for warm intros           |
| **Tue** | 10:00-11:00  | Send 5 new DMs to intros from clients    |
| **Wed** | all day       | Hands-on delivery of second gig                                                                              |
| **Thu** | 14:00-15:00  | 5 more personalised DMs using testimonial from client #1                                               |
| **Fri** | 13:00-14:00  | Bull-pen plan: pick your second productised service (per `GIG_PICK_MATRIX.md`)                          |

**Week 3 acceptance gates:**
- [ ] 2 paid gigs delivered + testimonial each
- [ ] Pipeline > $10k AUD
- [ ] One productised service priced & landing page drafted

---

## Week 4 — Repeat & systemise

| Day     | Block        | Action                                                                                                |
|---------|--------------|-------------------------------------------------------------------------------------------------------|
|         | morning      | Booked DM backlog → pick top 3, send 3 more                                                      |
|         | afternoon    | Land page 1 productised service (notion, lemon squeezy, or simple Stripe link)                            |
|         | evening      | Re-score leads, archive / drop cold ones                                                              |

**Week 4 acceptance gates:**
- [ ] Revenue dashboard shows $A0 → $A1,600-$A10,000
- [ ] 1 productised service (or at least a Stripe link) live
- [ ] At least 1 client on retainer / monthly (> 1 gig)

---

## Energy rules (THIS is the differentiator)

1. **High-energy blocks** (mornings, after lunch energy peak) → DMs, discovery calls, delivery.
2. **Low-energy blocks** (end-of-day, weekends) → automate, monitor, plan. NOT new work.
3. **No more than 1 hr/day of planning.** > 1 hr/day = procrastination disguised as alignment.
4. **Daily ledger write.** Append `REVENUE_LEDGER.jsonl` EVEN for zero-revenue days. The data is more valuable than the dollars.
5. **Friday afternoon = cleanup only.** Never new code + new outreach. Cleanup = archive / prune / delete / pay taxes.

---

## What gets cut if energy drops

Cut in priority order (last cut first):
1. Friday cleanup
2. Productised service work
3. Pipeline expansion (more DMs)
4. Discovery calls
5. **LAST TO CUT:** Friday cleanup & DM-send (these are the actual money Motion)

If you can't do DM-send 4 mornings in a row in week 1, the plan is broken. Not the plan — your energy model.

---

## What gets cut if money appears faster than expected

Don't cut Week 2 until Week 3 baseline is built. The fastest route to 2nd gig is repeat-1st-gig motion, not new outreach.

---

## Tracking

| Where                                    | What                                      |
|------------------------------------------|-------------------------------------------|
| REVENUE_LEDGER.jsonl                     | Every money-in event, every meeting-booked |
| leads_2026-06-25.csv                     | All DM attempts, replies, scores, sent_dates |
| `tools/01_morning_briefing.py` daily output | Daily state of money ledger + scored leads |
| EMPIRE_AUD_VALUATION_2026-06-25.md        | Re-value empire at end of week 4 to see if z$ increase tracks  |
| EXECUTION_LOG_2026-06-25.md              | Living document of deviations from this plan |
