# Client Offboarding — AusAI Tech

> **Purpose:** Close every project professionally, maximise testimonial capture, and plant the seed for referrals and retainers. Complete within 48 hours of final delivery.
> **Prerequisite:** `First_Client_Onboarding.md` (mirror structure), `EMAIL_TEMPLATES.md` (delivery + testimonial request templates)

---

## Phase 1 — Pre-Offboarding (Delivery Day)

Before the handoff call, confirm:

- [ ] Final invoice sent and marked PAID in `Invoice_Template.html`
- [ ] Revenue logged in `Revenue_Dashboard_Static.html`
- [ ] All deliverables documented (README, credentials, architecture diagram)
- [ ] 30-day warranty period start date noted in calendar
- [ ] `CASE_STUDY_TEMPLATE.md` opened and ready to fill during call

---

## Phase 2 — Handoff Call (30–45 min)

### Agenda

| Time | Topic | Notes |
|---|---|---|
| 0:00–5:00 | **Warm open** — "How has the first week with the system been?" | Listen for unexpected wins or issues |
| 5:00–15:00 | **Live demo** — Walk through the delivered system end-to-end | Screen-share, record if client permits |
| 15:00–25:00 | **Documentation review** — Share credentials doc, README, architecture diagram | Send via email after call |
| 25:00–35:00 | **Training** — Show client how to make minor changes (prompt edits, filter tweaks) | Record as Loom if possible |
| 35:00–40:00 | **Q&A** — Address any concerns before sign-off | Note issues for warranty tracking |
| 40:00–45:00 | **Next steps** — Warranty, retainer offer, testimonial ask (see Phase 3) | This is the revenue extension moment |

### Handoff Call Script (Key Lines)

**Opening:**
> "Today is about making sure you feel completely confident using what we built. There are no stupid questions — this is your system now."

**During training:**
> "I'm going to show you the 3 things you can change yourself without breaking anything. Everything else, just ping me."

**Transition to close:**
> "Before we wrap, I want to make sure you're set for the next 30 days and beyond."

---

## Phase 3 — The Three Ask System (End of Handoff Call)

The offboarding call is your highest-leverage moment. You have delivered value and the client is (hopefully) happy. Make three asks in this exact order:

### Ask 1 — The Testimonial (soft)

> "If you've found this useful, would you be open to a quick sentence I could use on my site? Something like what you'd tell a friend who was considering working with me. No pressure — if you're not comfortable yet, we can revisit in two weeks."

**If yes:**
- Open `EMAIL_TEMPLATES.md` → "Final Delivery + Testimonial Request"
- Send the follow-up email with a testimonial guide (3 questions to answer)
- Set a reminder for 14 days if they need time

**If no / "let me think about it":**
> "Totally understand. I'll send you a super short email in two weeks — just reply with whatever feels natural, even if it's just 'Karma built us an automation that saved 10 hours a week.' One sentence is gold for me."

### Ask 2 — The Retainer (medium)

> "A lot of clients find that after the build, they want someone keeping an eye on things — monthly tuning, new feature ideas, making sure nothing breaks when APIs update. I offer a monthly retainer for that. Would it make sense to chat about what that might look like for you?"

**If yes:**
- Book a 20-min "retainer scoping" call for next week
- Open `RETAINER_AGREEMENT.html` and customise during the call
- Send the customised agreement within 2 hours of the call while momentum is high
- The retainer is your path from project revenue to predictable monthly income

**If no / "not right now":**
> "No worries at all. I'll check in around day 25 of the warranty period — by then you'll have a feel for whether the system needs ongoing attention."

### Ask 3 — The Referral (hard — only if Ask 1 or 2 was positive)

> "Last thing — do you know anyone else who might be dealing with [the problem you solved]? I'm not doing any paid ads right now, so word-of-mouth is basically how I find my next clients. I'd be happy to offer them the same audit rate I gave you, or even a quick free 15-min call."

**If they name someone:**
- Ask for an intro email (warm intro beats cold outreach 10×)
- Offer to draft the intro email for them to forward
- Add the referred person to `LEAD_TRACKER.html` immediately with source "Referral — [Client Name]"

**If they don't name anyone:**
> "No pressure at all. If someone comes up in the next month or two, here's a link they can use to book directly with me: [Calendly link]."

---

## Phase 4 — Post-Call Actions (Within 2 Hours)

- [ ] **Send handoff email** with all documentation attached
- [ ] **Send testimonial request email** (if not collected live)
- [ ] **Log project as "Delivered"** in `LEAD_TRACKER.html`
- [ ] **Complete `CASE_STUDY_TEMPLATE.md`** while memory is fresh
- [ ] **Set calendar reminders:**
  - Day 7: "Check in — any issues?"
  - Day 14: "Testimonial follow-up (if not received)"
  - Day 25: "Retainer soft pitch (if not already sold)"
  - Day 30: "Warranty expires — final check-in"
- [ ] **Update `Revenue_Dashboard_Static.html`** with final payment
- [ ] **Archive project files** in `C:/Users/karma/deliverables/YYYY-MM-client-name/`

---

## Phase 5 — Warranty Period (Days 1–30)

**Your commitment:** Bug fixes and minor adjustments at no charge.

**What is covered:** (mirrors `First_Client_Onboarding.md` §4 Warranty)
- Defects in delivered code
- Integration failures caused by API changes (if the API was working at delivery)
- Broken workflows due to environment changes

**What is NOT covered:**
- New feature requests (these require a Change Order per `First_Client_Onboarding.md`)
- Changes to third-party platforms that break integrations (e.g., Instagram API policy change)
- Client-caused configuration changes

**Process:**
1. Client reports issue via email/Slack
2. You acknowledge within SLA (24h for non-urgent, 4h for urgent)
3. Fix and deploy
4. Update `LEAD_TRACKER.html` notes with issue + resolution

---

## Phase 6 — The 30-Day Close-Out

On day 30, send a final check-in:

> **Subject:** 30-day check-in — how's everything running?
>
> Hi {{NAME}},
>
> The 30-day warranty period for [project name] closes today. Wanted to check in:
>
> 1. Is everything running smoothly?
> 2. Any questions since the handoff?
> 3. If you haven't had a chance yet, I'd still love a brief testimonial — even one sentence helps enormously: [link to Google Form or just reply]
>
> If you ever need changes, extensions, or a new project, just reply to this email. I'm here.
>
> Best,  
> Karma — AusAI Tech

---

## Offboarding Checklist (Print & Tick)

### Delivery Day
- [ ] Final invoice paid
- [ ] Revenue logged
- [ ] All docs prepared (README, credentials, architecture)
- [ ] Handoff call scheduled

### Handoff Call
- [ ] Demo completed
- [ ] Training delivered
- [ ] Q&A resolved
- [ ] **Ask 1:** Testimonial requested
- [ ] **Ask 2:** Retainer offered
- [ ] **Ask 3:** Referral asked (if appropriate)

### Post-Call (2 hours)
- [ ] Handoff email sent
- [ ] Testimonial follow-up scheduled
- [ ] Case study template started
- [ ] Lead tracker updated
- [ ] Calendar reminders set (Day 7, 14, 25, 30)

### Warranty Period
- [ ] Day 7 check-in sent
- [ ] Day 14 testimonial nudge (if needed)
- [ ] Day 25 retainer soft pitch (if not sold)
- [ ] Day 30 final check-in sent
- [ ] Warranty officially closed

### Project Close
- [ ] Case study completed and filed
- [ ] Testimonial received and saved
- [ ] Referral lead added to tracker (if any)
- [ ] Project files archived
- [ ] Client marked "Closed — Delivered" in tracker

---

## Key Metrics to Track

| Metric | Target | Why |
|---|---|---|
| Testimonial ask rate | 100% of projects | Social proof compounds |
| Testimonial conversion | 60%+ | Not everyone will, but most will if asked well |
| Retainer conversion | 30%+ of eligible projects | Turns one-off revenue into recurring |
| Referral ask rate | 80%+ of happy clients | Warm intros are the cheapest acquisition |
| Referral conversion | 20%+ referred leads close | Much higher than cold outreach |

---

## Related Documents

- `First_Client_Onboarding.md` — Mirror structure for project start
- `EMAIL_TEMPLATES.md` — Delivery, testimonial request, and delay notification templates
- `RETAINER_AGREEMENT.html` — For clients who say yes to ongoing support
- `CASE_STUDY_TEMPLATE.md` — Fill this within 48 hours of handoff
- `LEAD_TRACKER.html` — Update client stage and add any referrals
- `Revenue_Dashboard_Static.html` — Log final payment

---

*Professional offboarding is where average consultants lose future revenue. Great consultants turn every delivery into three things: a testimonial, a retainer conversation, and a referral. Do all three.*
