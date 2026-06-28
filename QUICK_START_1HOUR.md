# ⚡ 1-HOUR QUICK START — AusAI Tech

**Purpose:** Go from zero to ready-to-sell in ~60 minutes. This condenses the 5 most critical files into one linear walkthrough.

**You'll need:** A computer, 60 minutes, and ~A$30 for a domain.

> **Open your browser. Start the timer. Follow every step in order.**

---

## ⏱️ MINUTE 0–10: LEGAL FOUNDATION

### Apply for ABN (5 min)
1. Go to `abr.gov.au`
2. Click "Apply for an ABN" → Individual (sole trader)
3. You'll need your TFN. Approval is instant or within 24 hrs.
4. Save your ABN number. You'll need it for invoices.

### Open a business bank account (5 min)
1. ING or Up Bank — free, no monthly fees, open online in 10 min
2. Create a second "Tax Savings" account. Transfer 25% of every payment here.

> **Full legal checklist:** `COMPLIANCE_CHECKLIST.md` — complete before your first invoice.

---

## ⏱️ MINUTE 10–25: DEPLOY THE SITE

### Push + Enable GitHub Pages (5 min)
1. Open `https://github.com/woodsai69rme/ausai-live-site`
2. Click **Add file → Create new file**
3. Name: `.github/workflows/pages.yml`
4. Paste the content of `C:\Users\karma\ausai_live\.github\workflows\pages.yml`
5. Click **Commit directly to main**
6. Go to Settings → Pages → Source = **GitHub Actions** → Save
7. Wait 60 seconds. Your site is live.

### Test Your URLs
- Landing: `https://woodsai69rme.github.io/ausai-live-site/`
- Stripe: `.../sales/checkout.html`
- Booking: `.../book.html`
- Portfolio: `.../portfolio/`

### Buy a Domain (5 min)
1. Go to Namecheap, search `ausai-tech.com` (~A$10/yr)
2. Buy it. Point DNS to GitHub Pages (Settings → Pages → Custom domain).

> **Full deploy guide:** `DEPLOYMENT_QUICK_START.md`

---

## ⏱️ MINUTE 25–35: STRIPE + CALENDLY

### Stripe (5 min)
1. Sign up at `dashboard.stripe.com` (free)
2. Create 4 products at these price points:
   - **AI Audit:** A$497 (one-time)
   - **Build Kickoff:** A$997 (one-time)
   - **Full Build:** A$1,497 (one-time)
   - **AI Partner Retainer:** A$2,497 (monthly)
3. Create Payment Links for each
4. Open `ausai_live/sales/checkout.html` → find `REPLACE_WITH_YOUR_LINK_*` → paste your 4 links
5. Delete the yellow alert banner

### Calendly (5 min)
1. Sign up at `calendly.com` (free)
2. Create 3 event types:
   - **AI Audit:** 30 min, free
   - **Build Kickoff:** 60 min, paid
   - **Strategy Deep-Dive:** 90 min, paid
3. Open `ausai_live/book.html` → replace `YOUR_USERNAME` with your handle (×3)
4. Set availability: Mon-Fri 9-5 AEST

> **Full setup guides:** `STRIPE_SETUP_GUIDE.md` + `CALENDLY_SETUP_GUIDE.md`

---

## ⏱️ MINUTE 35–45: OUTREACH SETUP

### LinkedIn (5 min)
1. Update your LinkedIn headline:  
   `AI Automation Consultant | I build systems that save 15+ hrs/week | Zapier • Make • n8n`
2. Set up a Google Sheet for tracking prospects (or use `LEAD_TRACKER.html`)

### Write Your First 5 DMs (5 min)
Use this template from `LINKEDIN_OUTREACH_SCRIPTS.md`:

```
Hi {name},

I noticed {company} is {something_about_their_business}. 

I help businesses like yours eliminate repetitive manual work 
through AI automation — typically saving 15-20+ hrs/week.

Open to a 10-min chat to see if there's a fit? No pressure.

{Your Name}
```

> **Full scripts:** `LINKEDIN_OUTREACH_SCRIPTS.md` + `REDDIT_OUTREACH_SCRIPTS.md`

---

## ⏱️ MINUTE 45–55: YOUR FIRST DISCOVERY CALL PREP

### Read the Script (5 min — do this NOW)
Open `Discovery_Call_Script.md`. Read it once. You don't need to memorise it.

**The 5 phases:**
1. **Warm-up** (2 min) — Build rapport. "How did you find me?"
2. **Discovery** (5 min) — "Walk me through your current process."
3. **Diagnosis** (5 min) — "Here's what's costing you time."
4. **Solution** (5 min) — "Here's what I'd build. Timeline: X. Cost: A$Y."
5. **Close** (3 min) — "Want me to send a proposal?" (Then send from `Proposal_Template.html`.)

### Key Numbers to Remember
- Your audit: **A$497**
- Your build: **A$997–A$1,497**
- Your retainer: **A$2,497/mo**
- Average outcome: **15–20 hrs/week saved**
- Demo close rate: **38%** (use `BEFORE_AFTER_DEMO.html` on calls)

> **Objection handlers:** `COMPETITOR_BATTLE_CARDS.md`

---

## ⏱️ MINUTE 55–60: YOUR FIRST INVOICE

### Create an Invoice (3 min)
1. Open `Invoice_Template.html` in your browser
2. Fill in: Client name, service, amount, your ABN, bank details
3. Print → Save as PDF
4. Send to client

### Set Up Your Daily Command Centre (2 min)
- Bookmark `AUSAI_OPS_DASHBOARD.html` — open every morning
- Print `MASTER_INDEX_1PAGE.md` — stick on your wall

---

## ✅ DONE. WHAT NOW?

### Remainder of Day 1
- [ ] Send your first 5 LinkedIn DMs
- [ ] Post your first piece of content (LinkedIn or Reddit)
- [ ] Set up Fiverr gigs using `FIVERR_GIG_CONTENT.md`

### First Week
- [ ] Follow `LAUNCH_CHECKLIST_DAY1.md` for Days 2-7
- [ ] Track everything in `LEAD_TRACKER.html`
- [ ] When a call books → review `Discovery_Call_Script.md` 10 min before

### First Close
- [ ] Send proposal from `Proposal_Template.html`
- [ ] Start `PROPOSAL_FOLLOWUP_SYSTEM.md` if no reply in 48 hrs
- [ ] On close → send `Invoice_Template.html` → onboard with `First_Client_Onboarding.md`

---

## 🚨 STUCK?

| Symptom | Open This |
|---|---|
| No replies to DMs after 1 week | `COLD_OUTREACH_AB_TEST.md` — test new hooks |
| Discovery calls go well but no closes | `Discovery_Call_Script.md` — review Phase 4-5 |
| Got a client but don't know what to do first | `PROJECT_MANAGEMENT_SOP.md` |
| Client asking for more than agreed | `SCOPE_CREEP_DEFENSE.md` |
| Something went wrong with a client | `CRISIS_COMMS_PLAYBOOK.md` |
| 30 days in, <A$3,000 revenue | `EXIT_STRATEGY.md` |
| Need to know which file to open | `MASTER_INDEX_1PAGE.md` |

---

## 🔗 THE 5 CORE FILES (Print These)

1. `DEPLOYMENT_QUICK_START.md` — Go live in 35 min
2. `LAUNCH_CHECKLIST_DAY1.md` — Your first 30 days, day by day
3. `Discovery_Call_Script.md` — Every sales call, every time
4. `Invoice_Template.html` — Get paid
5. `COMPLIANCE_CHECKLIST.md` — Don't get sued by the ATO

---

> **You're ready.** The site is live. You have a script. You have templates.  
> **Now go send 5 DMs.** Everything else you can figure out as you go.

> **Last updated:** 2026-06-28 — Round 14 (consolidation)
