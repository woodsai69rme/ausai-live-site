# 📆 POST-LAUNCH OPERATIONS — Week 2-4 Daily Playbook

**Engages:** the moment your 4 sites are publicly live (Steps 0-4 complete per `EXECUTION_SCRATCHPAD.md`).

**Purpose:** convert the *setup* mental model of `MASTER_MONEY_PLAN.md` into a *sustainable rhythm* mental model. Distinct from MMP — MMP is **Day-1 deploy and 4-hour boot**. This doc is **Days 8-30 daily execution**.

**Owner:** solo operator. **Wall-clock budget:** 90 min/day. **Daily recovery:** 30 min morning + 60 min afternoon.

---

## 🧠 Mental model: the 3 rhythms

| Rhythm | Time | Cadence | Why |
|---|---|---|---|
| **Pulse** (revenue + leads review) | 5 min | Every morning | Catch problems before they compound |
| **Outreach** (post + DM + comment) | 60-90 min | Every afternoon | Top-of-funnel; 7 posts/week non-negotiable |
| **Receipt** (deliver + invoice) | as needed | Per project | Top-of-revenue; spec'd in `First_Client_Onboarding.md` |

If a day only fits one rhythm, do **Pulse**. If two fit, **Pulse + Outreach**. Skip Receipt only if no active project (then you're in trouble anyway).

---

## 🌅 Morning Pulse (5 min, every day)

Open **`Revenue_Dashboard_Static.html`** in your browser. Check 4 things, in this order:

1. **Did Stripe receive anything overnight?** → If yes, send kickoff DM per `First_Client_Onboarding.md` within 1 hour
2. **Did Calendly get a booking overnight?** → If yes, send kickoff DM within 1 hour (same template)
3. **Any Fiverr unread messages?** → Reply within 12 hours (Fiverr penalizes slow responders)
4. **Any Reddit/LinkedIn DM replies?** → Reply within 12 hours

**No notifications?** That is normal for Days 1-7. Do not panic-pivot.

**Rule:** if Pulse takes more than 5 minutes, you're reading social media — close it. Notifications check is binary: is there anything new? Done.

---

## 🌇 Afternoon Outreach (60-90 min, every day)

The single biggest revenue lever after deploy. Spec'd by source:

### Day-type rotation (which platform gets focus)

| Day of week | Primary outreach | Secondary |
|---|---|---|
| **Monday** | Reddit (highest-ROI for the slow ramp) | LinkedIn DMs |
| **Tuesday** | LinkedIn (5 DMs from `LINKEDIN_DM_SEND_LIST.md`) | Twitter thread reply-raft |
| **Wednesday** | Reddit (different subreddit per week — see `SOCIAL_MEDIA_LAUNCH_POSTS.md`) | Hacker News (if you're feeling bold) |
| **Thursday** | Fiverr (1 gig iteration from `FIVERR_QUICK_START.md` notes) | Twitter standalone |
| **Friday** | **🚨 No outreach.** Use for **Receipt** rhythm + weekly revenue review | — |
| **Saturday** | Twitter/X (1 thread) | Reddit karma-building comments |
| **Sunday** | Weekly revenue review (30 min, see § below) | Queue 5 social posts for next week |

### Daily tactical checklist

- [ ] **1 cold DM / cold comment / cold post** — write it, send it, log it
- [ ] **1 reply to a competitor's post / a subreddit thread / a LinkedIn post** — adds visibility + karma
- [ ] **1 portfolio feature in social bio** — keep top 3 platforms' pinned-post pointed at your portfolio

**Don't:**
- ❌ Spend all 90 min on a single Reddit thread
- ❌ DM cold prospects (cold-DM penalty in most platforms is now severe)
- ❌ Post same content to multiple platforms raw — see "content repurposing" in `AUSAI_TECH_SOCIAL_MEDIA_GUIDE.md`

---

## 📥 Receipt rhythm (per project, when active)

If you have an active client (per `First_Client_Onboarding.md` kickoff already happened):

| Time | Activity |
|---|---|
| Daily (if mid-build) | 90 min focused work on their deliverable |
| Mon + Thu evening | Send them a status update (single Slack/Discord message, ≤6 lines) |
| On milestone hit | Send SOW-stipulated deliverable + invoice 50% |

If you have ≥3 active clients simultaneously: you've hit the consulting-cap ceiling. Decide: hire subcontractors? Raise rates? Both? — **do not** say yes to a 4th until you've raised rates.

---

## 📊 Weekly revenue review (Friday or Sunday, 30 min)

Open **`Revenue_Dashboard_Static.html`** + your Stripe Dashboard + Fiverr earnings tab. Compute:

### The 3 weekly numbers (write them down)

| Number | Where | Why |
|---|---|---|
| **Actual cash received this week** | Stripe + Fiverr + bank deposits | Ground truth |
| **Pipeline (pending invoices)** | `Revenue_Dashboard_Static.html` (Pending status) | Next-30-day forecast |
| **Hours worked this week** | Toggl export (or rough estimate) | $X / hour audit |

### The 1 weekly decision (just one, not 5)

Every Friday answer ONE of these questions (cycle through, one per week):

| Week | Question |
|---|---|
| Week 2 | **Is my messaging converting?** — count DMs/posts sent vs replies |
| Week 3 | **Is my pricing right?** — count 5+ Fiverr orders → if yes, raise 25% |
| Week 4 | **Am I delivering on time?** — if any client delivery slipped >1 day, identify the cause |

Don't try to answer all 3 every week. Decision fatigue kills solo operators.

### The 1% rule

If you earned A$1 this week → it's +A$1 above baseline → celebrate.

If you earned A$0 → check whether you did the **Pulse + Outreach** rhythms. If yes → pipeline will fill Week 2-3. If no → you stopped posting. Resume tomorrow.

---

## 🚨 Anti-pattern watch (the 6 ways solo operators burn out in Week 3)

| Pattern | Symptom | Fix |
|---|---|---|
| **Full-time grind** | Working 8h/day on client work for 2 clients | Cap at 5h/day client work; rest is sales/marketing |
| **Marketing slump** | Skipping afternoon Outreach "for a few days" | Restored via: set phone alarm at 14:00 labeled "Outreach" |
| **Trinket-trap** | Buying a new domain, new course, new plugin | Triage: did it make you $0 this week? Don't buy |
| **Multi-project parallelism** | 4 active clients all half-built | Finish one before starting another |
| **Comparison trap** | Spending 30 min/day reading competitor Twitter | 1x/week max; logged in `competitor_watch.md` |
| **Cash-flow anxiety** | Checking Stripe every 4 hours | Restrict Pulse to morning only |

If you see 2+ of these in yourself, take a half-day off. The rhythm resumes Monday.

---

## 📦 Tooling (post-launch stable state)

These run on day 2 onward. Set up once, use forever.

| Purpose | Tool | Why this one |
|---|---|---|
| Revenue tracking | **`Revenue_Dashboard_Static.html`** (in repo) | Master plan numbers vs actuals, single file |
| Project management | **`PROJECT_MANAGEMENT_SOP.md`** | Phase-by-phase delivery checklist + status templates |
| Scope defense | **`SCOPE_CREEP_DEFENSE.md`** | Boundary-setting scripts for every scenario |
| Crisis response | **`CRISIS_COMMS_PLAYBOOK.md`** | Pre-baked templates for when projects go wrong |
| Customer comms (≤3 clients) | Slack/Discord free tier | Real-time; clients request their own workspaces |
| Time tracking | Toggl free tier (1 user) | Hourly billing backup if disputes arise |
| Tax prep | Wave (free for sole traders) + **`TAX_TIME_CHECKLIST.md`** | Issue invoices, quarterly summaries, EOFY prep |
| Pricing strategy | **`PRICING_PSYCHOLOGY_GUIDE.md`** | When to raise, how to handle objections, bundling |
| Portfolio updates | Edit `ausai_live/portfolio/` directly + redeploy | No CMS needed at <10 case studies |
| Inbox triage | Gmail + 1 rule: "Anything from a paying client = Priority" | Don't let Fiverr spam bury real revenue signals |

**Don't add** (yet): ticketing systems, project-management tools, contract-management SaaS, legal-tech, complex CRMs. They're all distractions until you have ≥3 paying clients for 3 months.

---

## 🔁 Week 4 → Month 2 transition

When Week 4 ends having shipped ≥1 client + collected ≥A$500 cash + posted every day on at least 1 channel:

- ✅ You're past the "cold start valley"
- → Move to: **first subcontractor evaluation** (you've verified the playbook works)
- → OR: **raise rates 25%** (your portfolio now has 1+ shipped case)
- → OR: **ship a passive product** (template pack / course / n8n bundle) per `MASTER_MONEY_PLAN.md` §3

**Two of these three are right for your business.** Pick the one that matches your personality:
- Subcontractor = you want scale
- Raise rates = you want margin
- Passive product = you want optionality

Don't try to do all three simultaneously.

---

## ✅ Definition of done — post-launch operations

By end of Week 4:

- [ ] **30 days of Pulse + Outreach rhythm** unbroken (max 3 missed days allowed)
- [ ] **At least 1 paying client** past onboarding → final delivery
- [ ] **A$500-1500 cash in bank** (target = ~A$1,700 if linear on `MASTER_MONEY_PLAN.md` A$5K / 30-day conservative path; lower end = below-target outreach intensity; upper end = full pipeline conversion)
- [ ] **Testimonial from 1 client** added to `ausai_live/portfolio/`
- [ ] **ONE retier decision** (raise rates / hire sub-contractor / ship a product) made and committed to

By end of Week 8 (target per `MASTER_MONEY_PLAN.md` § aggressive path):

- [ ] **A$10,000/mo run-rate** on track (or honest assessment of why not — and pivot recommitted)

---

**Last rule:** if this doc ever feels overwhelming, open `Revenue_Dashboard_Static.html` and look at the **Days remaining** card. That's your only real clock.

> **Reality:** the second month is the hardest. Things work but slowly. Stick to the rhythm and don't measure yourself against founders making $10k MRR in month 2 — they've been at it since year 1.
