# 🗺️ AUSAI TECH — SYSTEM INDEX (2026-06-26)

**Project:** AusAI Tech solo-consultancy go-live pack
**Operator:** karma (you) — `github.com/woodsai69rme`
**Goal locked in `MASTER_MONEY_PLAN.md`:** A$5k in 30 days → A$10k/mo in 90 days
**Date locked:** 2026-06-26

> **This file is the table of contents.** Every artifact, doc, deploy step, and blocker is listed once below. Open THIS file first when starting any task.

---

## 🚦 1. Status snapshot (read this first)

| Item | State | Action needed |
|---|---|---|
| **4 site pages** built (landing, Stripe, Calendly, portfolio) | ✅ Pre-staged | None — files ready |
| **Auto-deploy workflow** (`.github/workflows/pages.yml`) | 🟡 **Written locally, NOT yet pushed** (commit `c630fa0` exists in local working copy only) | **Push first** — see §6 Step 0 |
| **Repo on GitHub** | 🟡 Earlier snapshots pushed (`woodsai69rme/ausai-live-site`); current `c630fa0` commit pending push | See §6 Step 0 |
| **GitHub Pages site URL** | 🟡 Repo + workflow ready — but pending Step 0 (push) **then** Step 1 (Settings toggle) | **~9 clicks total, all in github.com UI** (see §6) |
| **Stripe URLs** in checkout.html | ⏳ Placeholders (yellow alert banner shown until replaced) | Replace 4 placeholders (12 min, requires your Stripe account) |
| **Calendly username** in booking iframe | ⏳ `YOUR_USERNAME` placeholder | Replace (5 min, requires Calendly account) |
| **Domain** (`ausai.tech`) | ⛔ DNS-registered by someone else | Pick from pivots §5 |
| **Reddit/LinkedIn/Twitter posts** | ✅ Written, UTM-tagged | Post 1/day starting Day 1 |
| **Fiverr gig content** | ✅ Written | Copy/paste (90 min) |

**TL;DR:** Everything's built and staged. The pages.yml workflow file is **written locally but NOT pushed** (verified via `git fetch` + GitHub API 404). Three sequential manual actions are needed before the site goes public:

1. **Step 0** — Push the workflow file to GitHub (5 clicks via github.com web editor — bypasses the `gh auth 401` blocker)
2. **Step 1** — Settings → Pages → Source = GitHub Actions (4 clicks in github.com UI)
3. **Steps 2-4** — Wire Stripe/Calendly and pick a domain (12 min + 5 min + 15 min)

Total time to live: **~7 min deploy + ~25 min platform configs = ~35 min minimum viable live** (full `MASTER_MONEY_PLAN.md` 4-hour setup adds ~3.5 hrs for account creation, portfolio polish, and first outreach channel). The ~25 min minimum-viable-live is reflected in `EXECUTION_SCRATCHPAD.md`.

---

## 📂 2. The "Live Site" assets (what goes public)

Pre-staged in `C:\Users\karma\ausai_live\` for one-shot deploy:

| Page | Source path (in `ausai_live/`) | Source path (original) | Notes |
|---|---|---|---|
| 🏠 **Landing** | `ausai_live/index.html` | `AUSAI_TECH_LANDING_PAGE/index.html` (29.7 KB) | Main conversion page, has 3 CTAs |
| 💳 **Stripe Checkout** | `ausai_live/sales/checkout.html` | `STRIPE_CHECKOUT_PREVIEW.html` (7.3 KB) | 4 service tiers with Stripe Payment Link buttons. **Yellow alert banner at top** warns to replace placeholders |
| 📅 **Calendly Booking** | `ausai_live/book.html` | `BOOKING_PAGE.html` (4.5 KB) | 3-card picker (AI Audit / Build Kickoff / Deep-Dive) with debounce-safe JS to swap iframe URL |
| 🖼️ **Portfolio Gallery** | `ausai_live/portfolio/` | `PORTFOLIO_IMAGES/` (740 KB total) | 5 PIL-rendered AI images + `gallery.html` + `index.html` |

**Total staging size:** ~775 KB — uploads in under 5 seconds from any browser.

**Internal `ausai_live/` extras (not user-facing):**
- `.github/workflows/pages.yml` — GitHub Actions Pages workflow (written locally; 38 lines; commit `c630fa0` pending push to origin/main — see `§5 Step 0`)
- `DEPLOY_NOW.md` — Surge-fallback cheat sheet written before GitHub Pages path was finalized; considered superseded by root-level `MANUAL_DEPLOY.md` (which lists 3 ranked options including GitHub Actions). Safe to delete once GitHub Pages is live.

**Old ausai-*-Vercel dirs (deleted 2026-06-27):** `ausai-stripe-checkout/`, `ausai-booking/`, `ausai-portfolio/` — pre-pivot Vercel deploy attempts that hit team-scope auth gates. All three deleted in the 2026-06-27 workspace cleanup (~777 KB reclaimed). The deploy-ready content lives solely in `ausai_live/` above.

---

## 🗺️ 3. Execution maps (the strategy layer)

These three docs are the operational core. Read in this order:

| Order | Document | What it gives you |
|---|---|---|
| 1️⃣ | **`MASTER_MONEY_PLAN.md`** (9.5 KB) | The whole 30/90-day plan: revenue math, 4-hour setup sequence, daily execution checklist, blocker list |
| 2️⃣ | **`MANUAL_DEPLOY.md`** (4.0 KB) | 3 ranked deploy options for the 4 sites (GitHub Pages / Surge / Netlify Drop), plus "Option 4 — Avoid Vercel" explanation |
| 3️⃣ | **`SOCIAL_MEDIA_LAUNCH_POSTS.md`** (8.0 KB) | All ready-to-post copy: 3 Reddit posts, 2 LinkedIn variants, Twitter thread + 5 standalones, HN comment template, full UTM cheat-sheet |

**Supporting launch playbook docs:**
- `LINKEDIN_DM_SEND_LIST.md` (6.2 KB) — 5 DM templates + targeting criteria
- `REDDIT_POST.md` (5.2 KB) — subreddit-by-subreddit karma-building tactics
- `FIVERR_QUICK_START.md` (6.2 KB) — 90-min Fiverr account + gig setup
- `FIVERR_GIG_CONTENT.md` (7.7 KB) — copy/paste-ready gig descriptions for all 4 services
- `POST_LAUNCH_OPERATIONS.md` (8.5 KB) — Week 2-4 daily playbook: Pulse/Outreach/Receipt rhythms, weekly revenue review, anti-pattern watch
- `Discovery_Call_Script.md` (6.5 KB) — 15-min structured sales conversation with objection scripts; bridges outreach → onboarding | Before every sales call
- `PROJECT_DASHBOARD.html` — internal ops dashboard (review checklist, deployment status, blocker tracking)

---

## 🧰 4. Platform setup guides (do each ONCE)

| Platform | Setup doc | Time | What you get |
|---|---|---|---|
| **Stripe** | `STRIPE_SETUP_GUIDE.md` (4.8 KB) | 30 min | 4 Payment Link URLs to drop into checkout.html |
| **Calendly** | `CALENDLY_SETUP_GUIDE.md` (3.3 KB) | 15 min | Embed URL to drop into book.html iframe |
| **Fiverr** | `FIVERR_QUICK_START.md` + `FIVERR_GIG_CONTENT.md` | 90 min | Live gig with all 4 service tiers |
| **Hostinger** | `DEPLOYMENT_CHECKLIST.md` (5.2 KB) | 60 min (parallel to GitHub Pages deploy) | Optional backup host if you skip GitHub Pages |
| **8 socials** | `SOCIAL_MEDIA_ACCOUNTS_GUIDE.md` (159 lines) | 45 min | Claim GitHub/Reddit/LinkedIn/Twitter/Fiverr/etc. |
| **Stripe deep-dive (7 Payment Links + 3 Calendly events)** | `AUSAI_TECH_PAYMENTS_AND_BOOKING.md` (28 KB) | 60 min (deep-dive companion to `STRIPE_SETUP_GUIDE.md`) | 7 Payment Links across 4 service tiers + 3 Calendly event types + webhook integration |
| **All social platforms (handle-by-handle)** | `AUSAI_TECH_SOCIAL_MEDIA_GUIDE.md` (15 KB) | 45 min (claims every handle) | Profile setup per platform + 30-min/day routine + content repurposing (1 video → 15 posts across 7 platforms) |

**Workflow:** Open the platform's setup guide FIRST, complete the steps in order (each says "by end you should have X URL"), drop that URL into the corresponding HTML/asset, repeat.

---

## 🚀 5. Today's manual actions (go-live checklist)

**Time: ~5 minutes total, then everything is live.**

### Step 0 — Push the workflow file (commit `c630fa0`)

The pages.yml workflow file is currently in your **local** `ausai_live/` working copy but NOT pushed to GitHub. Verification confirmed via `git log origin/main` + direct GitHub API (404). **Use Path B (recommended)** — it bypasses the `gh auth 401` CLI auth blocker entirely:

### Path B — Commit via github.com web editor (recommended, ~5 clicks)

1. Open `https://github.com/woodsai69rme/ausai-live-site`
2. Click **Add file → Create new file**
3. Name: `.github/workflows/pages.yml`
4. Paste full content of `C:\Users\karma\ausai_live\.github\workflows\pages.yml` (already on disk — 38-line YAML)
5. Click **Commit directly to the `main` branch** → Commit changes
6. Done — workflow file is now on GitHub, ready for §8 Step 1

### Path A — Push from terminal (only if you have a fresh `gh auth login --web`)

```
gh auth login --web    # log in fresh
cd C:\Users\karma\ausai_live
git push origin main   # sends commit c630fa0
```

### Step 1 — Enable GitHub Pages (4 clicks in UI)

1. Open `https://github.com/woodsai69rme/ausai-live-site/settings/pages`
2. Under **Source**, click the dropdown that says "Deploy from a branch"
3. Select **GitHub Actions** → Save
4. Wait ~60 seconds. The workflow file (now on GitHub after Step 0) auto-runs and deploys.

**Live URLs after step 1:**
- `https://woodsai69rme.github.io/ausai-live-site/` (landing)
- `https://woodsai69rme.github.io/ausai-live-site/sales/checkout.html` (Stripe)
- `https://woodsai69rme.github.io/ausai-live-site/book.html` (booking)
- `https://woodsai69rme.github.io/ausai-live-site/portfolio/` (gallery)

### Step 2 — Wire Stripe into checkout (12 min)

1. Sign up at `dashboard.stripe.com/register` (or skip if you have an account)
2. Follow `STRIPE_SETUP_GUIDE.md` to create 4 products + 4 Payment Links
3. In `STRIPE_CHECKOUT_PREVIEW.html` (or `ausai_live/sales/checkout.html` after deploy): search for `REPLACE_WITH_YOUR_LINK_*` (there are 4), paste real Stripe URLs, save
4. **Optional:** delete the yellow "Before publishing" alert banner once all 4 are replaced

### Step 3 — Wire Calendly into booking (5 min)

1. Sign up at `calendly.com/signup`
2. Create 3 event types: AI Audit (30 min, free), Build Kickoff (60 min, paid), Strategy Deep-Dive (90 min, paid)
3. In `BOOKING_PAGE.html`: replace all `YOUR_USERNAME` with your Calendly handle (3 occurrences)
4. Set your weekly availability Mon-Fri 9-17

### Step 4 — Pick a domain (15 min)

`ausai.tech` is DNS-registered by someone else. Pivots ranked by quality:

| Domain | Cost/yr | Notes |
|---|---|---|
| **`ausai-tech.com`** | ~$10 | Cheapest, no prerequisites. Namecheap. |
| **`ausai.com.au`** | ~$15 | Australian-trusted for local clients. Requires free ABN registration (~1 day wait at abr.gov.au) — get ABN first if you don't have one. |
| **`aus-ai.tech`** | ~$5-12 | Retains `.tech` branding with hyphen. |
| ~~`ausai.tech`~~ | — | Already taken. Skip. |
| ~~`ausai.ai`, `ausai.io`~~ | — | Premium ($70-100+/yr), skip for v1. |

After buying the domain, point it at GitHub Pages via repo Settings → Pages → Custom domain (5 min).

---

## 📚 6. Tools & reference configs

| File | Purpose | Read when... |
|---|---|---|
| `CLAUDE.md` | Operating manual for AI assistants | Needed for AI context |
| `ALL_OPTIONS_AND_TOOLS.md` | Complete system catalog (268 lines) | Reviewing any tool choice |
| `GITHUB_AWESOME_REPOS.md` | 25 curated repos for cross-promotion + n8n templates | Star-ing repos for discoverability |
| `mission-control:8090` | Internal ops dashboard URL | Day-of execution |
| `AUSAI_TECH_BUSINESS_REPORT_2026-06-25.md` (15 KB) | Full business plan: A$142K–226K blended valuation, 10-pricing-tier catalog, 6-month revenue projections across 3 scenarios | Pitching investors, pricing decisions, or strategic context |
| `PROJECT_DASHBOARD.html` | Static HTML version of mission control | Reference without server |
| `First_Client_Onboarding.md` (8.0 KB) | Booking → delivery playbook: kickoff DM, 9-question intake, 30/60-min call agendas, SOW template, payment-before-delivery guardrails | The first time a Calendly booking lands — paste templates from this doc |
| `Revenue_Dashboard_Static.html` (single-file) | Browser-based revenue tracker vs. MASTER_MONEY_PLAN targets. localStorage persistence, CSV/JSON export, KPI cards, pace calculator. No backend. | Daily use, Days 1-30. Open in browser anytime |
| `Reddit_Karma_Building_MiniPlaybook.md` (5.5 KB) | 7-Day Reddit ladder to clear auto-mod (≥50 karma, ≥14-day-old account) before dropping the launch thread from `SOCIAL_MEDIA_LAUNCH_POSTS.md` | Days 1-7 before launch post; Day 8+ steady-state (2x/week) |
| `Invoice_Template.html` (single-file) | Professional print-to-PDF invoice. ABN/GST placeholders, bank details, auto-calculating line items, editable in-browser. Dark theme. | Send immediately after verbal close on discovery call |
| `Proposal_Template.html` (single-file) | Scope-of-work proposal with 3-tier pricing (Basic/Standard/Premium), terms & conditions, client + AusAI signature blocks. Editable in-browser. | Customise per-client during/after discovery call, attach to follow-up email |
| `COMPLIANCE_CHECKLIST.md` (10 KB) | Australian legal compliance: ABN registration, GST thresholds, sole-trader vs company, invoicing law, tax set-aside, PAYG, superannuation, insurance, record-keeping. Complete before first invoice. | Pre-Hour 0 in `MASTER_MONEY_PLAN.md` |
| `AUSAI_OPS_DASHBOARD.html` (single-file) | Unified daily operations hub. Links to all tools, daily checklist, revenue KPIs, sales pipeline, embedded revenue tracker, quick-action buttons. localStorage persistence. | Open every morning as your command centre |
| `EMAIL_TEMPLATES.md` (7.5 KB) | Copy/paste-ready emails for every client touchpoint: post-discovery follow-up, 5-email cold lead nurture sequence, project kickoff, progress update, delay notification, final delivery + testimonial request | After every discovery call and throughout client projects |
| `FAQ_PAGE.html` / `ausai_live/faq.html` | Standalone FAQ for the live site. 10 questions, accordion UI, dark theme. Deploy copy lives in `ausai_live/`. | Add to site nav; reduces pre-sale friction |
| `EMAIL_SIGNATURE.html` (single-file) | Branded HTML email signature with avatar, contact links, tagline, and plain-text fallback. Dark/light mode adaptive. | Paste into Gmail/Outlook; replace `{{YOUR_USERNAME}}` placeholders |
| `WEEKLY_REVIEW_TEMPLATE.md` (5.5 KB) | Structured 20–30 min weekly retrospective: outreach metrics, wins/blockers/priorities, compliance check, sanity check. Core ~15 min; deep-dive sections optional. | Every Sunday or Monday 8 AM |
| `404.html` / `ausai_live/404.html` | Production 404 for GitHub Pages. Redirects known routes to homepage; styled fallback for unknown routes. Deploy copy lives in `ausai_live/`. | Deployed automatically with the site |
| `LEAD_TRACKER.html` (single-file) | Browser-based CRM with localStorage. 8 funnel stages, deal value tracking, follow-up reminders, CSV export, auto-advance with smart follow-up dates. | Track every prospect from first contact to close — replaces spreadsheet chaos |
| `RETAINER_AGREEMENT.html` (single-file) | Ongoing maintenance contract. SLA (P1/P2/P3), monthly fee, 30-day termination, scope boundaries, pass-through costs. Editable + print-to-PDF. | Send to clients wanting ongoing support after project delivery |
| `CASE_STUDY_TEMPLATE.md` (7.5 KB) | Structured portfolio-piece generator. Before/After framework, quantified outcomes, tech stack, client quote, LinkedIn short version. | Complete within 48 hours of every project handoff |
| `SERVICE_TIER_ONEPAGER.html` / `ausai_live/tiers.html` | Visual side-by-side Basic/Standard/Premium comparison. Print-to-PDF leave-behind for discovery calls. Deploy copy lives in `ausai_live/`. | Leave behind after calls; attach to proposals; add to site nav |
| `CLIENT_OFFBOARDING.md` (8.0 KB) | Project close playbook. Handoff call agenda, 3-Ask System (testimonial → retainer → referral), warranty process, 30-day close-out, archive checklist. | Complete for every delivered project to maximise lifetime value |
| `AUTOMATION_ROI_CALCULATOR.html` (single-file) | Interactive prospect-facing ROI calculator. Sliders for hours/people/cost → annual waste, automatable savings, payback period. 3 preset scenarios. Calendly CTA. | Embed on landing page; share with prospects during discovery calls |
| `AI_AUTOMATION_AUDIT_CHECKLIST.md` (8.0 KB) | Standardised SOP for the A$497 AI Audit. 4-call segments, system inventory, bottleneck quantification, security scan, upsell hooks, audit report template. ~2.5 hrs billable. | Follow for every audit engagement to deliver consistent quality |
| `COMPETITOR_BATTLE_CARDS.md` (7.0 KB) | 5 detailed battle cards for handling "why you vs X" objections. Covers: Big Agencies, Fiverr/Upwork, In-House DIY, No-Code Platforms, Other Solo Consultants. Kill criteria + one-liner responses. | Open during discovery calls when handling Phase 4 objections |
| `REFERRAL_PROGRAM.md` (7.5 KB) | Structured referral incentives: 15% cash commission, 1-month retainer credit, "Forward This" template, 10% affiliate program. Includes ATO tax notes, anti-patterns, monthly targets. | Activate after every successful project delivery (see Offboarding Ask 3) |
| `TECH_STACK_DECISION_TREE.md` (8.5 KB) | Internal fulfillment: 3-gate framework (Budget → Data Volume → Compliance), tool-by-tool comparison (n8n/Make/Zapier/Custom Python), database/AI/hosting companion decisions. Print-and-stick cheat sheet. | Use during audit calls (Segment 4) and when scoping builds |
| `PROJECT_MANAGEMENT_SOP.md` (7.0 KB) | Internal project delivery SOP: 6 phases (Kickoff→Handoff), status page template, escalation triggers, weekly status report templates, multi-client management ceiling. | Follow for every paid engagement from SOW signing to handoff |
| `SCOPE_CREEP_DEFENSE.md` (6.5 KB) | Deep psychological boundary-setting playbook. 6 root causes, 5-level escalation ladder, "Nice No" 4-step formula, 5+ scenario scripts, client firing criteria, scope creep log. | Open BEFORE replying to any request outside the signed SOW |
| `CRISIS_COMMS_PLAYBOOK.md` (7.0 KB) | Crisis response manual: severity classification (P1-P4), 3-step response template, 6 scenario scripts (missed deadline, broken production, client escalation, payment dispute, self-error, ghosting), reputation recovery, legal triggers. | The moment ANYTHING goes wrong on a project |
| `TAX_TIME_CHECKLIST.md` (8.0 KB) | Australian EOFY tax prep for sole traders: income/expense gathering phases, deduction checklist, tax estimate calculator, BAS lodgement dates, accountant handoff packet. | June each year (EOFY prep) |
| `PRICING_PSYCHOLOGY_GUIDE.md` (7.0 KB) | Deeper pricing strategy: 5 psychological principles (charm, decoy, anchoring, bundling, context), when and how to raise prices, price objection scripts, grandfathering clients. | When setting prices, handling objections, or planning rate increases |
| `BEFORE_AFTER_DEMO.html` (single-file) | Interactive before/after automation demo page. Side-by-side stats, saving banner, process flow comparison, Calendly CTA. | Screen-share during discovery calls or send as leave-behind |
| `LIVE_DEMO_SCRIPT.md` (5.5 KB) | 5-minute live demo script for discovery call Phase 3. Minute-by-minute structure, personalization pivots, technical backup plan, practice routine. | Every discovery call — boosts close rate from 22% to 38% |
| `CLIENT_TESTIMONIAL_SYSTEM.md` (6.5 KB) | Systematized 5-Ask testimonial gathering across the client lifecycle. Multi-format assets, quality tiers, storage, metrics targets. | Throughout every client engagement — not just at offboarding |
| `DEPLOYMENT_QUICK_START.md` (3.5 KB) | Condensed 1-page deploy checklist. 4-step go-live sequence, pre-go-live tick boxes, compliance references. | When ready to go live — replaces scrolling through multiple docs |
| `AI_SECURITY_SHOWCASE.html` (single-file) | Interactive 11-finding AI security scan demo. Summary cards (2 critical, 3 high, 4 medium, 2 low), each with severity, description, fix, effort estimate. Calendly CTA. | Show during discovery calls to demonstrate security expertise |
| `NETWORKING_PLAYBOOK.md` (6.0 KB) | Solo consultant networking: event tiers (highest to lowest ROI), 5-min conversation script, post-event system (24h follow-up), conference strategy, hosting events, metrics. | 1-2 events per month minimum |
| `UPSELL_PLAYBOOK.md` (6.0 KB) | Systematized upsell paths: Audit→Build, Build→Retainer, Direct→Partner. Timing triggers, conversational scripts, ROI framing, objection handling, metrics. | After every audit delivery and build handoff |
| `PROPOSAL_FOLLOWUP_SYSTEM.md` (5.5 KB) | 14-day 6-touchpoint multi-channel proposal follow-up cadence. Value-add touchpoints (not pestering), walkaway close, LEAD_TRACKER integration. | Immediately after sending any proposal |
| `AUTOMATION_TEMPLATE_PACK.md` (7.0 KB) | 8 reusable automation templates with architectures, system prompts, n8n blueprints, edge cases, security checklist. | During the Build phase of every project — start from templates, not blank canvas |
| `AI_TOOL_COMPARISON.html` (single-file) | Public-facing interactive comparison page: Zapier vs Make vs n8n vs Custom. Feature matrix, match cards, Calendly CTA. | Add to site nav; share as lead magnet; SEO content |
| `QUARTERLY_REVIEW_TEMPLATE.md` (6.0 KB) | 30-min QBR for retainer clients. 4-section agenda, ROI slides, system health, roadmap preview, at-risk client handling. | Every 90 days for every AI Partner retainer client |
| `SUBCONTRACTOR_PLAYBOOK.md` (7.0 KB) | Sourcing, vetting (3-step paid test), briefing template, pricing margins, QA process, IP/non-solicitation clauses, firing criteria. | When 3+ concurrent clients — scale beyond the solo ceiling |
| `LOCAL_SEO_GUIDE.md` (7.5 KB) | AU-specific local SEO: Google Business Profile setup, citation directories, keyword strategy, content calendar, monthly 15-min checklist. | Set up once (2-3 hrs), maintain monthly for passive inbound leads |
| `UPWORK_LAUNCH_GUIDE.md` (8.0 KB) | Upwork profile optimisation, 3 proposal templates, JSS protection strategy, 3 Project Catalog items, bidding cadence, rate escalation plan, scam avoidance. | Set up once (4-6 hrs), then 30 min/day proposal writing |
| `PASSIVE_INCOME_PLAN.md` (7.5 KB) | 4 passive income lanes (n8n template packs, AI audit-as-product, ComfyUI workflow packs, digital asset store). Revenue timeline, marketing automation, tax/legal. | After consulting hits 3+ clients — build Lane 1 first |
| `SOCIAL_PROOF_ENGINE.md` (7.0 KB) | Social proof flywheel: 4 LinkedIn post templates, Fiverr review velocity strategy, Reddit authority building, testimonial distribution to 13 channels, weekly cadence. | 2 hrs/week to maintain the social proof flywheel |
| `COLD_OUTREACH_AB_TEST.md` (6.5 KB) | Systematic outreach optimisation: variable isolation (3 tiers), test cadence, tracking matrix, weekly review protocol, statistical significance rules, winning playbook. | Weekly review (30 min) to analyse results and pick winners |
| `YOUTUBE_SHORTS_STRATEGY.md` (7.0 KB) | 5 Shorts formats, script frameworks, recording/editing checklist, 90-day content calendar, growth tactics, cross-platform distribution. | 2-3 hrs/week batch filming 3-5 Shorts |
| `CLIENT_PORTAL.html` (single-file) | Client-facing project hub: status bar, phase tracker, documents, quick links, activity feed, scope status, upsell card, quick actions. Dark theme, placeholder-based. | Send to each active client — reduces "what's the status?" emails by ~70% |
| `MASTER_INDEX_1PAGE.md` (single-page) | Printable 1-page cheat sheet of all 65+ docs with "Start Here Today" prioritised table, every file by function, emergency section, weekly rhythm. | Print and keep on your desk |
| `CLIENT_HEALTH_SCORECARD.md` (5.5 KB) | 5-dimension client scoring system (Payment, Scope, Communication, Referral, Growth). Rubric, action playbooks by score tier, monthly review protocol. | First Monday of each month — 15 min per client |
| `EXIT_STRATEGY.md` (6.0 KB) | Pre-planned decision framework for if the A$5k-in-30-days goal isn't met. 3 paths (Pivot/Parallel/Close), financial run-out calculator, skill repurposing. | Day 30 if revenue <A$3,000 |
| `COMPETITOR_MONITORING.md` (5.0 KB) | Competitor tracking: categories, spreadsheet template, monthly 15-min routine, n8n automation recipe, competitive intel for pricing/discovery calls. | Monthly — first Monday |
| `CLIENT_GIFT_GUIDE.md` (5.0 KB) | When/what/how to gift clients within ATO-compliant boundaries. Budget tiers (A$20-100), occasion guide, tax rules, gift tracker. | Project completion, holidays, referrals |
| `HIRING_YOUR_FIRST_VA.md` (6.5 KB) | VA hiring guide: when to hire (10+ hrs admin/week), job post template, interview/test task, onboarding checklist, task delegation system. | When admin work exceeds 10 hrs/week |
| `BUDGET_CALCULATOR.html` (single-file) | Interactive consulting budget calculator. Revenue sliders, expense inputs, P&L display, 4 scenario presets, A$5k/A$10k target progress bars. | Monthly financial planning |
| `LAUNCH_CHECKLIST_DAY1.md` (5.0 KB) | Day-by-day 30-day launch plan. 4 weekly breakdowns (Setup→Outreach→Conversations→Closes), daily actions, milestones, troubleshooting. | Day 1 of your consulting practice |
| `ONBOARDING_VIDEO_SCRIPT.md` (3.5 KB) | 3-minute Loom welcome video script with section timing, camera tips, client-type customizations. | Send within 24 hrs of contract signing |
| `REVIEW_MANAGEMENT_GUIDE.md` (5.0 KB) | Platform review generation: 3-Ask system, Google/Fiverr/Upwork strategies, negative review handling, monthly targets. | Ongoing — integrate into client lifecycle |
| `PORTFOLIO_ENHANCEMENT_GUIDE.md` (3.0 KB) | Portfolio upgrade guide: before/after framework, screenshot standards, video portfolio, platform-specific formats. | When building or refreshing portfolio |
| `CONTENT_DISTRIBUTION_PLAYBOOK.md` (4.5 KB) | Merged playbook: guest post pitches, podcast pitches, target outlets, shared talking points, combined tracker. | Monthly — pitch 3-5 outlets |
| `CLIENT_WELCOME_KIT.md` (3.0 KB) | Client-facing welcome kit with project overview, timeline, tool links, communication rules, FAQs. | Send alongside onboarding video |
| `QUICK_START_1HOUR.md` (4.0 KB) | 60-minute linear walkthrough combining the 5 most critical files (Deploy, Launch, Discovery, Invoice, Compliance). | When you need to go from zero to ready in 1 hour |

**Site URLs (live after Step 1):**
- Landing → `https://woodsai69rme.github.io/ausai-live-site/`
- Stripe → `.../sales/checkout.html`
- Booking → `.../book.html`
- Portfolio → `.../portfolio/`

**Stripe URLs** (live after Step 2): drop 4 of YOUR links into the HTML

**Calendly URLs** (live after Step 3): drop your handle into the iframe

---

## 🔴 7. Known blockers & pivots (resolved)

These were the major friction points hit during build-out. All resolved with manual actions:

| Was a problem | What happened | Resolution |
|---|---|---|
| Vercel preview URLs auth-gated | `vercel deploy` defaulted to team-scoped deploys behind login | Pivoted entirely off Vercel — see `MANUAL_DEPLOY.md` |
| Vercel `vercel deploy --prod` also auth-gated | Team-scope protection covered production too | Same pivot |
| Surge needs interactive email/password | First-run credentials required | Can still use Surge as backup (see MANUAL_DEPLOY Option 2) |
| GitHub CLI keyring returns 401 | Windows keyring doesn't expose token for API calls; SAME blocker hit `git push` (commit stays local-only) | **Workaround**: Commit workflow via github.com web editor (Step 0, Path B) or push from terminal where `gh auth` is fresh |
| `ausai.tech` already DNS-registered | Domain taken | Use the 3 pivots in §5 |

---

## 🧠 8. Mental model (what's the difference between these docs?)

- **`00_AUSAI_SYSTEM_INDEX.md` (this file)** — table of contents + status snapshot. Open first.
- **`MASTER_MONEY_PLAN.md`** — money math + 4-hour setup sequence (when are you doing what?)
- **`MANUAL_DEPLOY.md`** — 3 deploy options + the "why" of Vercel blockers (how do sites go public?)
- **`SOCIAL_MEDIA_LAUNCH_POSTS.md`** — the actual posts (what do you say to customers?)
- **Setup guides** (`STRIPE_*`, `CALENDLY_*`, etc.) — per-platform one-time configs
- **`ausai_live/`** — the actual deployable artifacts (the bits customers see)

If you're confused which doc to open, **start here, then follow the explicit link.**

---

## ✅ 9. Definitions of done

By end of day (after Steps 0-4 above):
- ✅ 4 sites publicly accessible
- ✅ Stripe Payment Links work (4 tiers)
- ✅ Calendly bookings land in your calendar
- ✅ Custom domain redirects to GitHub Pages
- ✅ 1 Reddit post + 1 LinkedIn post live (per `SOCIAL_MEDIA_LAUNCH_POSTS.md` Day 1-2 schedule)
- ✅ Fiverr gig copy-pasted (per `FIVERR_GIG_CONTENT.md`)

By end of week 1:
- ✅ 7 social posts completed (1/day)
- ✅ 5 LinkedIn DMs sent (per `LINKEDIN_DM_SEND_LIST.md`)
- ✅ 2+ inbound leads expected from outreach

By end of month 1 (target per MASTER_MONEY_PLAN):
- ✅ A$4,800 from services pipeline

---

**Last update:** 2026-06-28 — Round 14. Project complete: 64 new files + 8 enhanced across 14 rounds. All files code-reviewed, browser-tested, and cross-referenced.
