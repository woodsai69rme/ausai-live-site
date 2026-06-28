# 💰 MASTER MONEY PLAN — AusAI Tech Go-Live (Final)

**Date locked:** 2026-06-26
**Owner:** solo operator (you)
**Goal:** A$5,000 in next 30 days · A$10,000/mo within 90 days

---

## 🎯 One-page summary

You have already built everything. The remaining work is **manual execution** of pre-written guides.

| Asset | Status | Time to use it |
|---|---|---|
| Landing page (`AUSAI_TECH_LANDING_PAGE/index.html`) | ✅ Ready | Deploy → 12 min |
| Portfolio gallery (5 images + HTML) | ✅ Ready | Deploy → 5 min |
| Fiverr gig content (`FIVERR_GIG_CONTENT.md`) | ✅ Ready | Copy → 90 min |
| Fiverr checklist (`FIVERR_QUICK_START.md`) | ✅ Ready | Execute → 90 min |
| Stripe checkout preview (`STRIPE_CHECKOUT_PREVIEW.html`) | ✅ Ready | Edit 4 links → 12 min |
| Booking page (`BOOKING_PAGE.html`) | ✅ Ready | Add Calendly URL → 5 min |
| 5 GitHub portfolio repos | ✅ Pushed | Pin → 5 min |
| Reddit launch posts (`SOCIAL_MEDIA_LAUNCH_POSTS.md`) | ✅ Ready | Post 1/day → 5 min/day |
| LinkedIn/ Twitter launch posts | ✅ Ready | Same |

**Total time to first sale:** ~4 hours of full setup (Hour 1 accounts + Hour 2 money infra + Hour 3 deploy + Hour 4 first outreach) + first 5 days of consistent posting. The *minimum-viable-live* slice (deploy + Stripe + Calendly wiring, no accounts yet, no first outreach) is ~35 min and lives in `EXECUTION_SCRATCHPAD.md`. The 4-hour figure covers the full operational chain.

---

## 🚀 4-Hour Setup Sequence (do in this order)

### Pre-Hour 0: Australian Compliance (do BEFORE first invoice)

**Time:** 2-3 hours | **Cost:** $0 | **Critical:** Without this, you legally cannot invoice Australian businesses.

| Step | Action | Time |
|---|---|---|
| 0a | **Register ABN** at abr.gov.au (free, instant) — required before invoicing any Australian business | 15 min |
| 0b | **Open business bank account** (ING, Up, NAB — no monthly fee options) | 30 min application + 1-3 business days approval |
| 0c | **Set up tax set-aside system** — transfer 25-30% of every payment into a separate "tax" savings account immediately on receipt | 10 min |
| 0d | **Decision:** Sole Trader vs Company → start as **Sole Trader** (free, simple, correct until you exceed ~$120k/year) | 10 min |
| 0e | **GST:** Do not register yet (threshold is $75,000/year). Revisit when you approach $6k/month consistently. | 5 min |

> **Full compliance guide:** See `COMPLIANCE_CHECKLIST.md` for ABN, GST thresholds, invoicing law, tax obligations, insurance, and record-keeping requirements.

---

### Hour 1: Accounts (parallel)

- [ ] **Stripe** → `dashboard.stripe.com/register` (5 min)
  - Activate account, verify identity
  - Create 4 products (chatbot, n8n bundle, site, hourly)
  - Copy 4 Payment Link URLs

- [ ] **Calendly** → `calendly.com/signup` (3 min)
  - Create 3 event types (AI Audit 30 min free, Build Kickoff 60 min, Deep-Dive 90 min)
  - Copy the inline embed URL
  - Set availability Mon-Fri 9-17 → reusable link

- [ ] **Fiverr** → `fiverr.com/join` (5 min, doesn't matter — guides automate this)
  - Just get to the "Create a Gig" screen
  - All content already pre-written in `FIVERR_GIG_CONTENT.md`

- [ ] **GitHub** → verify at `github.com/woodsai69rme` (1 min)
  - Should already be set up. Confirm profile README shows.

### Hour 2: Money infrastructure (parallel)

- [ ] **Stripe checkout** — open `STRIPE_CHECKOUT_PREVIEW.html`, replace 4 `REPLACE_WITH_YOUR_LINK_*` with real Stripe URLs, save as `checkout.html`
  - Upload to `public_html/sales/checkout.html` on Hostinger

- [ ] **Booking page** — open `BOOKING_PAGE.html`, replace iframe placeholder with Calendly embed code, save as `book.html`
  - Upload to `public_html/book.html` on Hostinger

- [ ] **Link from landing page** — edit `AUSAI_TECH_LANDING_PAGE/index.html` CTAs to point to `/sales/checkout.html` and `/book.html`

### Hour 3: Deploy to your platform of choice (90-second manually-enabled path)

Your folder is **pre-staged** at `C:\Users\karma\ausai_live\` with all 4 pages ready:

```
ausai_live\
├── index.html              (Landing)
├── sales\checkout.html     (Stripe tiers)
├── book.html               (Calendly 3-card)
└── portfolio\              (5-image gallery + index.html)
```

**Pick one of these 3 paths** (full steps in `MANUAL_DEPLOY.md`):

| Platform | Effort | Public URLs (after deploy — names = whatever you choose in the 90-sec step) |
|---|---|---|
| 🥇 **GitHub Pages** (click-flow) | 90 sec UI clicks | `https://woodsai69rme.github.io/<your-repo-name>/` (+ `/sales/checkout.html`, `/book.html`, `/portfolio/`) |
| 🥈 **Surge.sh** (terminal) | 30 sec, email + password | `https://<domain-you-choose>.surge.sh/` (+ `/sales/checkout.html`, `/book.html`, `/portfolio/`) |
| 🥉 **Netlify Drop** (drag-drop) | 10 sec, browser | `https://<random-hash>.netlify.app/` (+ `/sales/checkout.html`, `/book.html`, `/portfolio/`) |

> ⚠️ **What I couldn't do from CLI:** Autonomous deploy hit two terminal blockers — (a) `gh auth` keyring returns 401 Bad credentials when retrieving the token for API calls, even though `gh auth status` shows logged in; (b) Vercel team-scope protection covers all deployment types. Manual UI deploy via GitHub.com / surge / Netlify sidesteps both. See `MANUAL_DEPLOY.md` for the 4-click GitHub Pages path (recommended; takes 90 seconds in your browser).

### Hour 4: First outreach

- [ ] **Reddit r/automation** → copy Day 1 post verbatim from SOCIAL_MEDIA_LAUNCH_POSTS.md
- [ ] **LinkedIn Version A** → post on your personal profile
- [ ] **Twitter thread** → schedule 7 tweets via Buffer (free tier)
- [ ] **Send 5 DMs** from `LINKEDIN_DM_SEND_LIST.md`

---

## 📊 Money math

### Conservative path (Month 1)

| Source | Rate | Volume | Revenue |
|---|---|---|---|
| Fiverr AI Chatbot | $500/job | 2 jobs | **$1,000** |
| Fiverr n8n Bundle | $1,200/job | 1 job | **$1,200** |
| Stripe direct (mixed) | $250-500 each | 4 sales | **$1,800** |
| Consulting hours | $80/hr | 10 hrs | **$800** |
| **Month 1 total** | | | **$4,800** |

### Aggressive path (Month 2-3) with reputation + reviews

| Source | Rate | Volume | Revenue |
|---|---|---|---|
| Fiverr (with 5★ reviews) | $600/job avg | 6 jobs | **$3,600** |
| Stripe direct | $500 avg | 8 sales | **$4,000** |
| Recurring hosting mgmt | $200/mo/client | 5 clients | **$1,000** |
| Monthly consulting retainer | $500/mo | 3 clients | **$1,500** |
| **Month 3 total** | | | **$10,100** |

### Full-time target (Months 4-12)

- White-label n8n deployments to agencies: $3,000 × 4 = **$12,000/mo**
- AI consulting retainers: $1,500/mo × 5 = **$7,500/mo**
- Course sales (eventual): $200 × 50 = **$10,000/mo**
- **Target by month 12: $30,000/mo**

---

## 🗓️ Daily execution checklist (week 1)

**Each morning (15 min):**

- [ ] Check Stripe for new payment
- [ ] Check Calendly for new bookings
- [ ] Respond to Fiverr messages
- [ ] Send 2 LinkedIn DMs (use templates in `LINKEDIN_DM_SEND_LIST.md`)

**Each afternoon (30 min):**

- [ ] Send 1 Reddit comment on AI thread (build karma)
- [ ] Post 1 Twitter engagement
- [ ] Update portfolio if new project complete

**Once per week:**

- [ ] Friday: review revenue, ship any pending deliverable
- [ ] Sunday: queue 5 social posts for next week

---

## 🔴 Blocker checklist (must-fix before first sale)

- [ ] **Windows pagefile → 16-32 GB** (5 min, requires reboot)
  - Property of My Computer → Advanced → Performance → Advanced → Virtual Memory → Change
  - Uncheck auto-manage → Custom size → Initial 16384, Max 32768 → Set → OK → **Restart Windows**
  - Without this: ComfyUI crashes on model load → can't generate portfolio AI art on demand
- [ ] **Buy 1 custom domain** (~$12/yr): `ausai.tech` is taken — pivot to **`ausai-tech.com`** (~$10/yr, Namecheap) or **`ausai.com.au`** (~$15/yr if you have an ABN; register one at `abr.gov.au` first if not). .io and .ai are premium ($70-$100/yr) — skip.
- [ ] **OpenRouter API key** (free tier signup): `openrouter.ai`
- [ ] **Stripe payouts configured** (bank/PayPal): required before first $100 withdrawal

---

## 🟠 Current limitations & workarounds

| Limitation | Workaround |
|---|---|
| ComfyUI crashes (pagefile) | Use PIL-generated portfolio images (already done — 5 ready) |
| No GitHub stars on your 3 repos | Open `GITHUB_AWESOME_REPOS.md` Section 9 — repo lists to star |
| Stripe URLs are placeholders | Manual replace when Stripe ready (12 min) |
| Hostinger account not active | Use **GitHub Pages / Surge / Netlify Drop** for instant deploy (~90 sec) — see `MANUAL_DEPLOY.md` |
| No time for course creation | Defer to month 3 — start with services |

---

## 📂 File index (everything you have)

### Marketing assets (ready to deploy)
- `AUSAI_TECH_LANDING_PAGE/index.html` — main landing
- `STRIPE_CHECKOUT_PREVIEW.html` — service tiers with Stripe buttons
- `BOOKING_PAGE.html` — Calendly embed page
- `DASHBOARD_MISSION_CONTROL.html` — internal ops dashboard
- `PORTFOLIO_IMAGES/01-05-*.png` + `gallery.html` — 5 portfolio images

### Strategy & guides (ready to read)
- `FIVERR_QUICK_START.md` (157 lines) — 90-min Fiverr setup
- `FIVERR_GIG_CONTENT.md` (233 lines) — copy-paste gig descriptions
- `STRIPE_SETUP_GUIDE.md` (170 lines) — payment links walkthrough
- `CALENDLY_SETUP_GUIDE.md` (132 lines) — booking page walkthrough
- `SOCIAL_MEDIA_ACCOUNTS_GUIDE.md` (159 lines) — claim 8 platforms
- `SOCIAL_MEDIA_LAUNCH_POSTS.md` (this folder) — ready-to-post copy
- `LINKEDIN_DM_SEND_LIST.md` (195 lines) — 5 DM templates
- `REDDIT_POST.md` (185 lines) — subreddit launch posts
- `DEPLOYMENT_CHECKLIST.md` (186 lines) — Hostinger deploy steps
- `TODAY_EXECUTION_CHECKLIST.md` (193 lines) — day-1 action plan

### Portfolio / GitHub (live)
- `github.com/woodsai69rme/comfyui-workflow-recipes` (8 files)
- `github.com/woodsai69rme/n8n-templates` (14+ files, 5 imported + ATTRIBUTION)
- `github.com/woodsai69rme/ai-security-checklist` (3 files)
- `github.com/woodsai69rme/woodsai69rme` — profile README ✅ PUSHED

### Discovery / research
- `ALL_OPTIONS_AND_TOOLS.md` (268 lines) — complete system catalog
- `GITHUB_AWESOME_REPOS.md` (164 lines) — 25 curated repos, monetization roadmap

### Reference / config
- `CLAUDE.md` — operating manual for AI assistants
- `mission-control:8090` — internal dashboard

### Delivery & operations (built Rounds 7-9)
- `PROJECT_MANAGEMENT_SOP.md` — Phase-by-phase delivery checklist
- `SCOPE_CREEP_DEFENSE.md` — Boundary-setting psychological playbook
- `CRISIS_COMMS_PLAYBOOK.md` — Pre-baked crisis response templates
- `TAX_TIME_CHECKLIST.md` — EOFY tax preparation (sole trader)
- `PRICING_PSYCHOLOGY_GUIDE.md` — Deeper pricing strategy and objection handling

---

## ✅ End-state goal (90 days from now)

By **2026-09-26**, target:

- ✅ $30,000/mo recurring + project revenue
- ✅ 10+ Fiverr 5★ reviews
- ✅ 5 retainer clients
- ✅ 1k subscribers on LinkedIn
- ✅ Hosted portfolio (GitHub Pages / Surge / Netlify Drop per `MANUAL_DEPLOY.md`) + Stripe active
- ✅ Fully automated n8n lead-to-delivery pipeline

---

**Last step:** go execute Hour 1 of the setup sequence above. Everything else is already done.
