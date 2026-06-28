# Deployment Quick Start — AusAI Tech (5-Minute Go-Live)

> **Purpose:** Single condensed page with the remaining manual actions. Open this when you're ready to go live. Complete in one session.
> **Time:** ~35 min total (7 min deploy + ~28 min platform wiring).
> **Prerequisite:** All docs built. You're at the final go-live step.

---

## ⚡ The 4-Step Go-Live Sequence

### Step 0: Push to GitHub (5 clicks, 2 min)

1. Open `https://github.com/woodsai69rme/ausai-live-site`
2. Click **Add file → Create new file**
3. Name: `.github/workflows/pages.yml`
4. Paste the 38-line YAML from `C:/Users/karma/ausai_live/.github/workflows/pages.yml`
5. Commit directly to `main` branch

✅ Done. Workflow file is now on GitHub.

---

### Step 1: Enable GitHub Pages (4 clicks, 1 min + 60 sec wait)

1. Open `https://github.com/woodsai69rme/ausai-live-site/settings/pages`
2. Under **Source**, select **GitHub Actions** → Save
3. Wait ~60 seconds for deploy to complete

✅ Done. Your site is live at:
- `https://woodsai69rme.github.io/ausai-live-site/` (landing)
- `.../sales/checkout.html` (Stripe)
- `.../book.html` (booking)
- `.../portfolio/` (gallery)

---

### Step 2: Wire Stripe (12 min)

1. Sign up at `dashboard.stripe.com/register`
2. Create 4 products in Stripe (see `STRIPE_SETUP_GUIDE.md`):
   - AI Audit (A$497)
   - AI Build (A$1,497)
   - AI Partner (A$2,497/mo)
   - Custom Project (variable)
3. Copy each Payment Link URL
4. In `ausai_live/sales/checkout.html`, replace 4 `REPLACE_WITH_YOUR_LINK_*` placeholders
5. On GitHub, open the file → Edit (pencil icon) → paste your updated HTML with real Stripe URLs → Commit directly to main

---

### Step 3: Wire Calendly (5 min)

1. Sign up at `calendly.com/signup`
2. Create 3 event types:
   - AI Audit (30 min, free)
   - Build Kickoff (60 min, paid)
   - Strategy Deep-Dive (90 min, paid)
3. In `ausai_live/book.html`, replace `YOUR_USERNAME` (3 occurrences)
4. Set availability Mon-Fri 9-17
5. Re-commit the updated file

---

### Step 4 (Optional): Custom Domain (15 min)

Buy `ausai-tech.com` (~A$10/yr, Namecheap) or `ausai.com.au` (~A$15/yr if you have an ABN).
Then: GitHub repo Settings → Pages → Custom domain → enter domain → Save.

---

## 🎯 Pre-Go-Live Checklist (Tick These)

### Infrastructure
- [ ] Step 0: pages.yml pushed to GitHub
- [ ] Step 1: GitHub Pages enabled
- [ ] Site loads at the GitHub Pages URL (wait 60s, refresh)

### Money
- [ ] Stripe account created
- [ ] 4 Payment Links replaced in checkout.html
- [ ] Checkout page loads: `.../sales/checkout.html`

### Booking
- [ ] Calendly account created
- [ ] 3 event types created
- [ ] Booking page loads with YOUR calendar: `.../book.html`

### Compliance (do before first invoice)
- [ ] ABN registered at abr.gov.au
- [ ] Business bank account opened
- [ ] Tax set-aside account created (25-30%)
- [ ] Invoice template updated with real ABN

> **Full compliance guide:** See `COMPLIANCE_CHECKLIST.md` for ABN, GST, tax, insurance, and record-keeping requirements.

### First Outreach
- [ ] 5 LinkedIn DMs sent (from `LINKEDIN_DM_TEMPLATES.md`)
- [ ] 1 Reddit post live (from `SOCIAL_MEDIA_LAUNCH_POSTS.md`)
- [ ] Fiverr gig content copy-pasted (from `FIVERR_GIG_CONTENT.md`)

---

## What To Open Next

| After Go-Live, Open... | When |
|---|---|
| `AUSAI_OPS_DASHBOARD.html` | Every morning (your command centre) |
| `LINKEDIN_DM_TEMPLATES.md` | Daily outreach |
| `Revenue_Dashboard_Static.html` | Log first payment |
| `Discovery_Call_Script.md` | Before first sales call |
| `First_Client_Onboarding.md` | When first booking lands |
| `COMPLIANCE_CHECKLIST.md` | Before first invoice |

---

*Everything is built. Everything is staged. ~35 minutes separates you from a live AI consultancy. Execute steps 0-3 and you're open for business.*
