# 🎯 First Client Onboarding — Booking → Delivery Playbook

**When this kicks in:** the moment a Calendly notification arrives for the first `AI Audit` (free), `Build Kickoff` (paid), or `Strategy Deep-Dive` (paid) booking.

**Why this exists:** MASTER_MONEY_PLAN.md covers the funnel setup (Stripe URLs live, Calendly bookable, etc.). It does **not** cover what to do in the 18 hours between "someone booked" and "first invoice paid." That's this doc — the operational hinge.

**⚠️ Prerequisite:** This playbook is **usable only after** `EXECUTION_SCRATCHPAD.md` **Steps 0-3 are complete** — meaning the GitHub Pages site is live, Stripe Payment Links are real URLs (not `REPLACE_WITH_YOUR_LINK_*` placeholders), and the Calendly iframe handle is real (not `YOUR_USERNAME`). If you try to onboard before those are wired, you'll have a working kickoff DM but no way to invoice.

**Owner:** solo operator. Total wall-clock per client: 90 minutes spread across 3 days.

---

## ⏱️ T+0 (within 1 hour of booking notification)

The Calendly email arrives. Don't reply immediately — wait 30 min so you don't seem desperate — then send the **kickoff DM** template below. Mark it "Day 0" in your tracking.

### Kickoff DM template (paste verbatim, personalize `{{}}`)

> **Subject:** Re: {{Calendly event type}} — quick confirmation
>
> Hi {{first name}},
>
> Got your booking through — thanks for reaching out. To make our session maximally useful, can you drop a 2-3 sentence reply on:
>
> 1. **The headline outcome you want** (e.g., "clients self-serve answers without me"; "stop missing lead forms at 2am"; "predict next quarter's revenue within ±15%")
> 2. **Any constraint I'm missing** (budget ceiling, hard deadline, internal politics, "we tried X already")
> 3. **What "success" looks like** by Day 30 after we ship
>
> I'll have a draft plan + 3 clarifying questions ready when we meet. Don't prep anything — show up with the rough ideas above and I'll bring the structure.
>
> Calendar invite is attached. {{Phone/Zoom URL — pick based on event type}}
>
> — karma

**Why this works:**
- Sells *outcomes*, not *tech*
- Shifts prep burden from you (operator) onto them (client) — surfaces constraints before you quote
- Adds credibility (you "have a draft plan") without overpromising

---

## 📝 T+1 to T+2 (within 24h) — send the **intake form**

After they reply, send this doc. **Send as Google Form OR as a static `.md` they fill out and email back** — your call. (Google Form is faster; markdown is more impressive to sophisticated clients.)

### Intake form (the 9 questions you actually need)

```
1. Business in one sentence (what you sell, who buys it)
2. Monthly revenue range (rough — under $5k / $5-25k / $25k+)
3. Current "AI" or automation tools in use (chatbot? Zapier? Email sequences? None?)
4. The single pain point you'd most want to fix (one sentence)
5. Who internally will own this after delivery? (Name + role)
6. Approximate budget for this project: ($ / range / "let's discuss after the call")
7. Hard deadline / event driving this (if any)
8. Tools you absolutely need kept off-limits (security, compliance, vendor lock-in)
9. Can you share access to the relevant account TODAY? (Yes / Need to ask / Not yet)
```

**Why these 9:**
- Q1-3 size the engagement
- Q4-Q6 identify the bottleneck and your budget
- Q7-Q9 flag blockers you'd otherwise discover mid-project

---

## ☎️ T+3 (kickoff call day) — the 30-min agenda

When the **AI Audit** (free, 30 min) or **Build Kickoff** (paid, 60 min) call starts, follow this agenda exactly. Don't improvise.

**Suggested copy-paste intro** (saves you 2 min of stalling):

> "Thanks for making time. Structure for today: 20 min of me asking you questions, 5 min for your questions back, last 5 min I summarize what comes next and rough pricing. Sounds fair?"

### Agenda (AI Audit — 30 min free)

| Time | You do | They do |
|---|---|---|
| 0-2 min | Send the agenda (script above) | Agree |
| 2-7 min | Q1-Q4 from intake form (re-ask live, fill any gaps) | Answer |
| 7-15 min | **Diagnose & demo** — sketch the bottleneck on a shared whiteboard (Zoom / Google Docs) | React |
| 15-20 min | **Quick-win proposal** — "Given X, I can fix in 1 week by doing Y. Time estimate: $Z. Want me to send a formal SOW?" | Ask clarifying Qs |
| 20-25 min | Q&A from them | Ask |
| 25-28 min | **Decision prompt:** "Want me to send the SOW now, or want 24 hours to think?" | Decide |
| 28-30 min | Send SOW link + scheduling URL for follow-up | Book next call |

**Post-call (within 1 hour):**

- If they said "send SOW" → skip to **§ SOW template** below and email it within 1 hour
- If they said "let me think" → drop a 24h no-pressure follow-up drafted earlier:

> Subject: Following up — {{project tagline}}
>
> Hi {{first name}}, no pressure either way. If we're a fit I'll have a 30-day plan to you by Friday. If we're not, you keep the AI Audit notes from today — no invoice. Reasonable?

### Agenda (Build Kickoff — 60 min paid)

Same agenda as above **plus** this segment added at minute 35:

| 35-50 min | **Architecture sketch** — draw the system: which tools (n8n / ComfyUI / Supabase / OpenRouter), what data flows, what's automated vs human-in-loop | React, push back |
| 50-55 min | **Risk callout** — "Here are 3 things that will probably go wrong. Here's how I'd prevent each." | Ask Qs |
| 55-60 min | Send SOW + invoice link | Digest |

---

## 📜 SOW template (Statement of Work)

Send within 1 hour of "send SOW" commitment. Use this template — copy/paste:

```
STATEMENT OF WORK — {{project name}}
Date: {{YYYY-MM-DD}}
Operator: karma (AusAI Tech — github.com/woodsai69rme)
Client: {{company name}}

1. OUTCOME
   {{one-sentence outcome they'll see shipped}}

2. SCOPE (deliverables)
   - [ ] {{deliverable 1}}
   - [ ] {{deliverable 2}}
   - [ ] {{deliverable 3}}

3. NOT IN SCOPE (out of scope — brought up = paid hourly via Change Order)
   - {{exclusion 1}}
   - {{exclusion 2}}
   - **Integration limits:** This scope includes integrations with {specific systems only}. Any additional API, platform, or system integration requires a formal Change Order.
   - **Iteration limits:** This engagement includes {N} rounds of refinement/revision. Additional optimization cycles are billed at {rate}/hour or quoted as a separate Change Order.
   - **Data responsibility:** Client is responsible for providing clean, formatted data and access credentials before kickoff. Data cleaning, formatting, or extraction beyond basic import is out of scope.
   - **Model drift / post-delivery changes:** AI models may drift or require updates over time. This SOW covers delivery of a working system as specified. Ongoing monitoring, retraining, or model updates are available via a separate monthly retainer (quoted separately, typically A$500-2,000/month depending on scope).

4. TIMELINE
   Kickoff: Day 0 (today)
   Milestone 1: Day {{N}} — {{milestone}}
   Milestone 2: Day {{N}} — {{milestone}}
   Final delivery: Day {{N}}
   Warranty: 14 days post-delivery for bug fixes (no new features)

5. FEES
   Total: ${{amount}}
   Payment schedule: 50% upfront / 50% on Milestone 1 delivery
   Invoice due: Net 7 days
   Late-payment interest: at the rate prescribed by your jurisdiction's commercial law (NSW example: 1.0%/month per the *Building and Construction Industry Security of Payment Act 1999*; verify for your state/country before signing).

6. ACCEPTANCE
   You accept when: {{single measurable criterion}}
   You reject when: {{dispute-resolution mechanism — recommend "30-min resolution call"}}

7. IP & OWNERSHIP
   All deliverables, code, configs transfer to {{client}} upon final payment.
   By signing, {{client}} grants karma (AusAI Tech) a non-exclusive, perpetual, royalty-free license to use anonymized versions of these deliverables as portfolio material (no company name, no proprietary data, no client-identifying details). Public case studies require a separate written addendum.

SIGNED: karma ({{date}})        SIGNED: {{client contact}} ({{date}})
```

**Why this template works:**
- Section 1 is *one* sentence (anti-scope-creep)
- Section 3 explicitly names what counts as additional billable work
- 50/50 split protects you from "did all the work, then they ghosted"
- Section 6's acceptance criterion is **measurable** (not "looks good")
- Section 7 anonymized-portfolio clause = future marketing asset

---

## 🔄 Change Orders

If the client asks for work outside the original SOW during the project:

> "Happy to help with {new request}. This falls outside the original scope we agreed to in the SOW Section 3. I can quote it separately — estimated {time} at {rate}. Want me to send a Change Order proposal?"

**Process:**
1. Acknowledge the request within 24 hours
2. Quote the additional work using `Proposal_Template.html` (change title to "Change Order — {Project Name}")
3. Require payment (or agreement) before starting the additional work
4. Update the project timeline if the Change Order affects delivery

**Rule:** Never absorb scope creep silently. Every addition is a new quote. The SOW's explicit "NOT IN SCOPE" clauses make this conversation easy — you simply point to Section 3.

---

## 💳 Payment infrastructure (the unsentimental part)

**For Build Kickoff (paid, 60 min) and Deep-Dive (paid, 90 min):**

After they reply "yes send SOW":

1. **Send Stripe Payment Link invoice** (per `STRIPE_SETUP_GUIDE.md`) for 50% upfront = `Total × 0.5`
2. Mark it 7-day due
3. **DO NOT** start work until payment clears
4. Once paid → Stripe sends them a receipt automatically → you wire them confirmation + kickoff-confirmed DM

> **Hard rule:** Never start work without 50% upfront, even for friends. The minute you do is the minute the project becomes "volunteer work."

**For AI Audit (free, 30 min):** No payment needed. They booked it, you delivered, no invoice.

---

## 🧰 Tools to have open during onboarding

| Stage | Tool | URL |
|---|---|---|
| Booking notification | Gmail | (Cal ms you set up will land here) |
| Kickoff DM | Gmail (drafts) | (or whatever you reply from) |
| Stripe invoice | Stripe Dashboard | `https://dashboard.stripe.com/payment-links` |
| SOW hosting | Google Docs | (or `ausai-tech.com/sow/{{client}}` if you're fancy) |
| Whiteboard | Zoom + Excalidraw / Google Docs |
| Client communication | Slack / Discord / WhatsApp — agree Day 0 |
| Time tracking | Toggl free tier → bill hourly if scope creep |

**Status page** (set up Day 0): `https://statuspage.com` (free) or a single `ausai-tech.com/clients/{{clientname}}` static page so they always know where the project is.

---

## 🚨 When it goes wrong (your 3 most-likely first-deliverable failure modes)

| Scenario | Why it happens | Pre-baked response |
|---|---|---|
| Client ghosts after kickoff DM | You didn't get their reply in 24h | Send a 48h follow-up: "Hi {{name}}, closing out — feel free to ping me when ready." If no reply in 7d, mark dormant. |
| Scope explodes mid-project | You didn't write Section 3 of the SOW | "Per SOW Section 3, that's out of scope. Happy to quote it as a ${{X}} add-on. Want me to?" |
| Payment late 14+ days | No late fee clause | First reminder at Day 8: "Friendly heads-up — invoice {{num}} was due Day 7." Day 14: "Per SOW Section 5, late fee applies. Let me know if we need to discuss terms." |

---

## ✅ Definitions of done — onboarding

By end of Week 1 after first booking:

- [ ] Client has SOW in writing
- [ ] 50% upfront invoice paid via Stripe
- [ ] Slack/Discord channel created
- [ ] Shared workspace (Drive / Notion) created
- [ ] Kickoff call happened (you've followed the 30-min agenda above)
- [ ] Status page (or check-in cadence) agreed

By end of project (Day 14-30):
- [ ] Milestone 1 invoice sent + paid
- [ ] Final delivery shipped
- [ ] Final 50% invoice paid
- [ ] Testimonial requested via DM (template at end)
- [ ] Project added to portfolio gallery (`ausai_live/portfolio/`)

---

## 💬 Testimonial DM template (send Day 32 = 2 days post-delivery)

> Subject: Quick favor? 2-min testimonial
>
> Hi {{first name}}, hope the new {{deliverable}} is paying dividends. Quick favor: a 2-line testimonial I can put on my portfolio? Anything goes — even "worked with karma, fast turnaround." Real > polished.
>
> If you'd rather not, no worries — drop me a thumbs-up emoji and we're square.
>
> — karma

**Conversion to testimonial ~40%** based on prior freelancer data. If they say yes, paste it into `ausai_live/portfolio/` testimonial carousel after explicit written permission.

---

**End of playbook.** Now: **don't write any of this in advance** — paste from this doc when the moment arrives. Customization is in `{{}}` placeholders only.

> **Reality:** the **first** client will be messy. The **third** onward will be smooth because you've executed this playbook 2x. By client 10 you'll stop reading this doc entirely.
