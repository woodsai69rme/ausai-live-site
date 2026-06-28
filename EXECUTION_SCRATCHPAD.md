# ⚡ EXECUTION SCRATCHPAD — 3 manual steps to live

> **One-page action checklist.** Open browser in one window, this scratchpad on screen. ~25 min from "open this" to "live + booking + taking payments".

---

## ☑️ STEP 0 — push pages.yml via github.com (5 min)

> All in your browser — no terminal, no `gh auth`. Bypasses the known Windows-keyring 401 blocker.

- [ ] Open `https://github.com/woodsai69rme/ausai-live-site`
- [ ] **Add file → Create new file**
- [ ] Filename: `.github/workflows/pages.yml`
- [ ] Paste 38-line YAML content from `C:\Users\karma\ausai_live\.github\workflows\pages.yml`
- [ ] **Commit new file** → wait ~20 sec

## ☑️ STEP 1 — enable GitHub Pages (2 min)

- [ ] On github.com: **Settings → Pages → Source** radio group
- [ ] Select **GitHub Actions** → **Save**
- [ ] Wait ~60 sec → all 4 URLs below return HTTP 200

## ☑️ STEP 2 — wire 4 Stripe Payment Links (12 min)

- [ ] https://dashboard.stripe.com/register (or skip if account exists)
- [ ] Per `AUSAI_TECH_PAYMENTS_AND_BOOKING.md` Part 1: create 7 Payment Links
- [ ] Open `STRIPE_CHECKOUT_PREVIEW.html` (or `ausai_live/sales/checkout.html` after deploy)
- [ ] Search `REPLACE_WITH_YOUR_LINK_*` (4 hits) → paste real URLs
- [ ] Delete the yellow "Before publishing" alert banner once all 4 replaced

## ☑️ STEP 3 — wire Calendly (5 min)

- [ ] https://calendly.com/signup (use `hello@ausaitech.com`)
- [ ] Per `AUSAI_TECH_PAYMENTS_AND_BOOKING.md` Part 2 + `CALENDLY_SETUP_GUIDE.md`: create 3 event types (15 min free, 60 min paid, 30 min follow-up)
- [ ] Open `BOOKING_PAGE.html` → search `YOUR_USERNAME` (3 hits) → your handle
- [ ] Set availability **Mon–Fri 9–17**

---

## 🌐 Live URLs after Step 1 (paste into notes):

- 🏠 Landing → `https://woodsai69rme.github.io/ausai-live-site/`
- 💳 Stripe → `https://woodsai69rme.github.io/ausai-live-site/sales/checkout.html`
- 📅 Booking → `https://woodsai69rme.github.io/ausai-live-site/book.html`
- 🖼️ Portfolio → `https://woodsai69rme.github.io/ausai-live-site/portfolio/`

## ⏱️ Total: ~25 min → live + accepting bookings + taking payments

> **Next after live:** Send first Reddit post per `SOCIAL_MEDIA_LAUNCH_POSTS.md` §1 (r/automation Day 1 — starter pack thread; 5 min, paste-verbatim).
