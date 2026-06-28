# AusAI Tech — Stripe Payments & Calendly Booking Integration Guide

**Date:** 25 June 2026  
**Domain:** ausai.tech

---

## Part 1: Stripe Payment Links (No-Code Setup)

### Step 1: Create Stripe Account

1. Go to https://dashboard.stripe.com/register
2. Enter: AusAI Tech, email (hello@ausaitech.com), Australia
3. Verify email
4. Complete business details:
   - Business type: Individual / Sole proprietor
   - Industry: Technology / Software
   - Website: ausai.tech
   - Description: "AI automation services including workflow design, AI media production, and security auditing"
5. Connect bank account for payouts (Australian bank account required)

### Step 2: Create Payment Links

Navigate to **Stripe Dashboard → Payment Links → New**

#### Payment Link 1: AI Music Video — Basic ($150 AUD)

| Field | Value |
|---|---|
| **Product name** | AI Music Video — Basic |
| **Description** | 1-minute AI-generated music video using ComfyUI + Wan 2.1. Includes 1 revision. 72-hour delivery. |
| **Price** | A$150.00 |
| **Quantity** | 1 |
| **After payment** | Redirect to: https://ausai.tech/thank-you (create simple thank you page) |

#### Payment Link 2: AI Music Video — Standard ($300 AUD)

| Field | Value |
|---|---|
| **Product name** | AI Music Video — Standard |
| **Description** | 2-minute AI-generated music video with custom style matching. Includes 2 revisions. 1080p output. 72-hour delivery. |
| **Price** | A$300.00 |
| **Quantity** | 1 |

#### Payment Link 3: AI Music Video — Premium ($500 AUD)

| Field | Value |
|---|---|
| **Product name** | AI Music Video — Premium |
| **Description** | 3-minute AI-generated music video with character consistency, scene transitions, and beat-matched effects. 3 revisions. 4K output. 96-hour delivery. |
| **Price** | A$500.00 |
| **Quantity** | 1 |

#### Payment Link 4: ComfyUI Workflow — Basic ($200 AUD)

| Field | Value |
|---|---|
| **Product name** | ComfyUI Workflow — Basic |
| **Description** | Custom ComfyUI workflow for AI art or video. 1 style, fully documented, 48-hour delivery. |
| **Price** | A$200.00 |

#### Payment Link 5: ComfyUI Workflow — Standard ($400 AUD)

| Field | Value |
|---|---|
| **Product name** | ComfyUI Workflow — Standard |
| **Description** | Complex ComfyUI workflow with 3 style variations, optimisation for your GPU, full documentation. 72-hour delivery. |
| **Price** | A$400.00 |

#### Payment Link 6: AI Security Audit — Basic ($1,500 AUD)

| Field | Value |
|---|---|
| **Product name** | AI Security Audit — Basic |
| **Description** | Security review of your AI system. Prompt injection testing, data leakage check, API key exposure scan. Written report + 30-min debrief. 5-day delivery. |
| **Price** | A$1,500.00 |

#### Payment Link 7: Strategy Session ($200 AUD)

| Field | Value |
|---|---|
| **Product name** | AI Strategy Session |
| **Description** | 1-hour video call. We review your business, identify AI opportunities, and create a prioritised action plan. Includes session recording + written summary. |
| **Price** | A$200.00 |

### Step 3: Embed Payment Links on Landing Page

Replace placeholder links in the landing page with your actual Stripe payment links:

```html
<!-- In the pricing section, replace href="#contact" with: -->
<a href="https://buy.stripe.com/YOUR_BASIC_LINK" class="pricing-btn">Get Started</a>
<a href="https://buy.stripe.com/YOUR_PROFESSIONAL_LINK" class="pricing-btn primary">Book Consultation</a>
<a href="https://buy.stripe.com/YOUR_ENTERPRISE_LINK" class="pricing-btn">Contact Us</a>
```

### Step 4: Configure Stripe Settings

**In Stripe Dashboard → Settings:**

1. **Currency:** AUD (default)
2. **Receipts:** Enable "Send receipts to customers"
3. **Email notifications:** Enable payment confirmations
4. **Webhooks (optional):** Set up webhook endpoint if you want to trigger workflows on payment
   - URL: `https://your-n8n.com/webhook/stripe-payment`
   - Events: `checkout.session.completed`, `payment_intent.succeeded`

### Stripe Fee Summary

| Transaction | Amount | Stripe Fee (2.7% + $0.30) | You Receive |
|---|---|---|---|
| Music Video Basic | $150 | $4.35 | $145.65 |
| Music Video Standard | $300 | $8.40 | $291.60 |
| Music Video Premium | $500 | $13.80 | $486.20 |
| ComfyUI Basic | $200 | $5.70 | $194.30 |
| Security Audit | $1,500 | $40.80 | $1,459.20 |
| Strategy Session | $200 | $5.70 | $194.30 |

---

## Part 2: Calendly Booking System (Free Tier)

### Step 1: Create Calendly Account

1. Go to https://calendly.com/signup
2. Sign up with email (hello@ausaitech.com)
3. Connect Google Calendar (avoids double-booking)
4. Set timezone: Australia/Melbourne (or your timezone)

### Step 2: Create Event Types

#### Event 1: Free Discovery Call

| Field | Value |
|---|---|
| **Name** | Free Discovery Call |
| **Duration** | 15 minutes |
| **Description** | "Quick 15-minute call to discuss your AI needs. No sales pitch — just honest advice about what AI can do for your business." |
| **Availability** | Weekdays 9 AM – 5 PM |
| **Buffer** | 15 min before/after |
| **Limit** | 4 per day |
| **Questions** | Name, Email, Company name, What AI problem are you trying to solve? (dropdown: Workflow automation / AI media / Security / Other) |

#### Event 2: Strategy Session ($200 AUD)

| Field | Value |
|---|---|
| **Name** | AI Strategy Session |
| **Duration** | 60 minutes |
| **Description** | "1-hour deep-dive into your business. We'll identify AI opportunities, estimate ROI, and create a prioritised action plan. Includes session recording + written summary." |
| **Price** | A$200 (Calendly Payments or Stripe Payment Link) |
| **Availability** | Weekdays 10 AM – 4 PM |
| **Buffer** | 30 min before/after |
| **Limit** | 2 per day |
| **Questions** | Name, Email, Company, Industry, Current tools, Budget range (dropdown) |

#### Event 3: Project Follow-up

| Field | Value |
|---|---|
| **Name** | Project Follow-up |
| **Duration** | 30 minutes |
| **Description** | "Follow-up call for existing clients. Review progress, discuss next steps, or troubleshoot issues." |
| **Availability** | Weekdays 9 AM – 5 PM |
| **Limit** | 6 per day |

### Step 3: Embed Calendly on Landing Page

**Option A: Inline embed (recommended)**

Paste this before the closing `</body>` tag, and add a `<div id="calendly-container"></div>` where you want it to appear:

```html
<!-- Calendly inline widget begin -->
<link href="https://assets.calendly.com/assets/external/widget.css" rel="stylesheet" />
<script src="https://assets.calendly.com/assets/external/widget.js" type="text/javascript"></script>
<script>
  Calendly.initInlineWidget({
    url: 'https://calendly.com/ausaitech/discovery-call?hide_event_type_details=1&hide_gdpr_banner=1',
    parentElement: document.getElementById('calendly-container'),
    prefill: {},
    utm: {}
  });
</script>
<!-- Calendly inline widget end -->
```

**Option B: Popup widget (floating button)**

Add before `</body>`:

```html
<!-- Calendly badge widget begin -->
<link href="https://assets.calendly.com/assets/external/widget.css" rel="stylesheet" />
<script src="https://assets.calendly.com/assets/external/widget.js" type="text/javascript"></script>
<script>
  Calendly.initBadgeWidget({
    url: 'https://calendly.com/ausaitech/discovery-call',
    text: 'Book a Call',
    color: '#3b82f6',
    textColor: '#ffffff'
  });
</script>
<!-- Calendly badge widget end -->
```

### Step 4: Calendly Integrations

| Integration | Purpose | Setup |
|---|---|---|
| **Google Calendar** | Sync availability | Calendly → Integrations → Google Calendar |
| **Stripe** | Collect payment for paid events | Calendly → Integrations → Stripe (or use Payment Link in description) |
| **Zapier/n8n** | Trigger workflows on booking | Calendly → Integrations → Webhook |
| **Email notifications** | Reminders to you and client | Calendly → Notifications → Enable |

---

## Part 3: Integration Flow

```
Client visits ausai.tech
  ├─→ Sees pricing → Clicks "Book Consultation"
  │   ├─→ Option A: Calendly popup (free call) → Books → Calendar invite sent
  │   ├─→ Option B: Stripe payment link → Pays → Redirected to Calendly to book time
  │   └─→ Option C: Email (hello@ausaitech.com) → You reply with Calendly link
  │
  ├─→ Sees services → Clicks "Get Started"
  │   ├─→ Stripe payment link → Pays → Receipt email → You notified
  │   └─→ You deliver → Request revision → Done
  │
  └─→ Booked via Calendly → Shows up in Google Calendar → You prepare → Call
```

---

## Part 4: Email Templates

### Welcome Email (Auto-send after Fiverr order)

```
Subject: Thanks for your order! Here's what happens next 🚀

Hi [Name],

Thanks for choosing AusAI Tech! I'm excited to work on your [service].

Here's what happens next:
1. I'll review your requirements (check email in 2 hours)
2. I'll send a brief confirmation with timeline
3. I'll start working and send progress updates
4. You'll receive your deliverable by [date]

If you have any questions, reply to this email or book a quick call: [Calendly link]

Looking forward to it!

[Your name]
AusAI Tech
ausaitech.com
```

### Proposal Email (For direct clients)

```
Subject: AusAI Tech Proposal — [Project Name]

Hi [Name],

Great chatting with you! As discussed, here's my proposal for [project name]:

**Scope:** [Brief description]
**Timeline:** [X weeks]
**Investment:** A$[amount] (50% upfront, 50% on delivery)
**Deliverables:** [List]

**What's included:**
- [Item 1]
- [Item 2]
- [Item 3]

**Payment:** Click here to pay the deposit: [Stripe payment link]

Ready to proceed? Just reply "Yes" and I'll get started.

[Your name]
AusAI Tech
```

---

## Part 5: Quick Start Checklist

| # | Task | Time | Status |
|---|---|---|---|
| 1 | Create Stripe account | 15 min | ☐ |
| 2 | Verify Stripe identity | 10 min | ☐ |
| 3 | Create 7 payment links | 30 min | ☐ |
| 4 | Create Calendly account | 10 min | ☐ |
| 5 | Create 3 event types | 20 min | ☐ |
| 6 | Connect Google Calendar | 5 min | ☐ |
| 7 | Update landing page with links | 15 min | ☐ |
| 8 | Set up email notifications | 10 min | ☐ |
| 9 | Test payment flow end-to-end | 15 min | ☐ |
| 10 | Test booking flow end-to-end | 10 min | ☐ |
| **Total** | | **~2.5 hours** | |

---

*Integration guide generated 25 June 2026. Complete all steps before going live.*
