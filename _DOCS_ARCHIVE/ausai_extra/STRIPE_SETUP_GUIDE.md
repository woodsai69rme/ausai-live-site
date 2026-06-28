# Stripe Payment Links — Setup Guide

> Step-by-step instructions to create payment links for every service tier.

---

## Prerequisites

- Stripe account (free to create)
- Bank account for payouts (Australian)
- ABN (optional for now — Stripe allows sole traders)

---

## Step 1: Create Stripe Account

1. Go to **dashboard.stripe.com**
2. Click "Start now"
3. Enter email + password
4. Verify email
5. Complete onboarding:
   - Business type: "Individual / Sole proprietor"
   - Business name: "AusAI Tech"
   - ABN: (enter if you have one, or skip)
   - Personal details: name, DOB, address
   - Bank account: for payouts
6. Done — you're ready to create payment links

**Time:** 10 minutes

---

## Step 2: Create Payment Links

For each service tier, create a payment link:

### Link 1: AI Music Video — Basic (A$150)

1. Go to **Payments → Payment Links**
2. Click "New payment link"
3. Fill in:
   - Name: "AI Music Video — Basic"
   - Description: "1-minute AI-generated music video. 72h delivery, 1 revision, 1080p."
   - Amount: **15000** (Stripe uses cents, so 15000 = A$150)
   - Currency: **AUD**
4. Under "After payment":
   - Select "Show confirmation page"
   - Or redirect to: `https://ausai.tech/thank-you` (create this later)
5. Click "Create link"
6. Copy the payment link URL
7. Save it somewhere safe

### Link 2: AI Music Video — Standard (A$300)

1. Same steps as above
2. Name: "AI Music Video — Standard"
3. Description: "2-minute AI-generated music video. Custom style, 72h, 2 revisions, 1080p + ProRes."
4. Amount: **30000** (A$300)
5. Create link → copy URL

### Link 3: AI Music Video — Premium (A$500)

1. Name: "AI Music Video — Premium"
2. Description: "3-minute premium AI music video. Character consistency, effects, unlimited revisions, 96h."
3. Amount: **50000** (A$500)
4. Create link → copy URL

### Link 4: ComfyUI Workflow — Basic (A$200)

1. Name: "ComfyUI Workflow — Basic"
2. Description: "1-style custom ComfyUI workflow. 48h delivery, 7-day support."
3. Amount: **20000** (A$200)
4. Create link → copy URL

### Link 5: ComfyUI Workflow — Standard (A$400)

1. Name: "ComfyUI Workflow — Standard"
2. Description: "3-style ComfyUI pipeline. Full docs, 30-day support."
3. Amount: **40000** (A$400)
4. Create link → copy URL

### Link 6: ComfyUI Workflow — Enterprise (A$600)

1. Name: "ComfyUI Workflow — Enterprise"
2. Description: "Enterprise workflow suite. Unlimited styles, training, 90-day support."
3. Amount: **60000** (A$600)
4. Create link → copy URL

### Link 7: Security Audit (A$1,500)

1. Name: "AI Security Audit — Starter"
2. Description: "2-hour AI security review + 5-page PDF report. Prompt injection, data leakage, API security."
3. Amount: **150000** (A$1,500)
4. Create link → copy URL

### Link 8: AI Consulting Session (A$200)

1. Name: "AI Consulting — 1 Hour"
2. Description: "1-hour AI strategy session. Tool selection, ROI analysis, implementation roadmap."
4. Amount: **20000** (A$200)
5. Create link → copy URL

---

## Step 3: Update Landing Page Links

After creating payment links, update the landing page:

1. Open `AUSAI_TECH_LANDING_PAGE/index.html`
2. Find all `#contact` links
3. Replace with your Stripe payment link URLs

Example:
```html
<!-- Before -->
<a href="#contact" class="pricing-btn">Get Started</a>

<!-- After -->
<a href="https://buy.stripe.com/xxxxx" class="pricing-btn" target="_blank">Get Started</a>
```

---

## Step 4: Test Payment Flow

1. Click one of your payment links
2. Fill in test card: `4242 4242 4242 4242` (any future date, any CVC)
3. Complete checkout
4. Verify you receive email confirmation
5. Check Stripe dashboard — payment should appear

---

## Step 5: Add to Fiverr (If Applicable)

Fiverr handles payments internally — you don't use Stripe for Fiverr orders. But you CAN link to Stripe for:
- Direct clients (LinkedIn DMs)
- Website visitors (ausai.tech)
- Reddit/ social media referrals

---

## Payment Link Summary

| Service | Price | Stripe Link |
|---|---|---|
| Music Video — Basic | A$150 | [paste link] |
| Music Video — Standard | A$300 | [paste link] |
| Music Video — Premium | A$500 | [paste link] |
| ComfyUI — Basic | A$200 | [paste link] |
| ComfyUI — Standard | A$400 | [paste link] |
| ComfyUI — Enterprise | A$600 | [paste link] |
| Security Audit | A$1,500 | [paste link] |
| Consulting Session | A$200 | [paste link] |

**Time to set up all 8 links:** ~30 minutes
**Cost:** $0 (Stripe takes 1.75% + A$0.30 per transaction)

---

## Stripe Fees (Australia)

| Transaction Type | Fee |
|---|---|
| Domestic cards | 1.75% + A$0.30 |
| International cards | 2.9% + A$0.30 |
| AMEX | 2.9% + A$0.30 |
| Currency conversion | +1% |

**Example:** A$150 sale → Stripe takes A$2.93 → You receive A$147.07
