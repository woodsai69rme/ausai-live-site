# Upsell Playbook — AusAI Tech

> **Purpose:** Systematized Audit→Build→Partner upsell path with timing triggers, conversation scripts, and pricing bridges. Every audit client is a build prospect — convert them systematically.
> **When to use:** After every AI Audit delivery. Before/after every Build handoff. At every quarterly review.
> **Prerequisite:** `AI_AUTOMATION_AUDIT_CHECKLIST.md`, `Discovery_Call_Script.md`, `PRICING_PSYCHOLOGY_GUIDE.md`

---

## The Upsell Philosophy

**Rule 1:** Don't upsell during the sale. Upsell after you've delivered value.
**Rule 2:** Every upsell must be justified by a SPECIFIC finding. Not "you might need more" — "Finding #3 shows X. Here's the fix."
**Rule 3:** The client should feel like they're making the smart business decision, not being sold to.

---

## Upsell Path 1: Audit → Build (A$497 → A$1,497)

**Timing:** Immediately during the audit deliverable call. This is your highest-conversion moment.

### The Bridge Script

**After presenting the audit findings:**

> "Of these {N} findings, the top 3 are costing you roughly A${total waste}/year. I can build the fix for Finding #1 — the {biggest bottleneck} — in about {X} days. The build is A$1,497 total. Since you've already completed the A$497 audit, your remaining investment is A$1,000. That covers deployment, documentation, and 30-day warranty."

**Why this works:**
- Frames the audit fee as a credit toward the build (perceived discount without discounting)
- Names ONE specific finding (not "fix everything" — too vague)
- Includes warranty (differentiator)
- The price is 3× the audit — already anchored from the decoy pricing structure

### If They Hesitate: The Scope-Back

> "If the full build is more than you want to commit to right now, I can scope it to just {core deliverable} for A${lower amount}. You get the core fix running, and we add the rest later when you've seen the value."

### If They Say Yes: The Transition

> "Perfect. I'll send the SOW now. Same terms as the audit — 50% to start, build within {X} days, 30-day warranty. You'll have the fix running by {date}."

**Then:** Send SOW from `Proposal_Template.html` within 1 hour. Update `LEAD_TRACKER.html` stage to "Proposal Sent — Upsell."

---

## Upsell Path 2: Build → Retainer (A$1,497 → A$2,497/mo)

**Timing:** During the Build handoff call (see `CLIENT_OFFBOARDING.md` Phase 3, Ask 2). Second window: Day 25 warranty check-in.

### The Bridge Script (Handoff Call)

> "A lot of clients find that after the build, the system needs ongoing tuning — API updates, new edge cases, feature ideas that come up once you're using it daily. I offer a monthly retainer for that. A$2,497/month covers up to 3 active workflows, monthly tuning, and priority support. If something breaks at 11 PM, you don't wait until Monday."

### The Bridge Script (Day 25 Check-In)

> "You've been running {system} for 25 days now. How many little things have come up that you'd want tuned? That's exactly what the retainer handles — ongoing attention without needing to scope and quote each change. Worth a 15-minute call to scope what that would look like for you?"

### The ROI Framing

**Before the upsell conversation, calculate:**

| Line | Amount |
|---|---|
| Annual cost without automation | A${their manual cost} |
| Annual cost WITH the build | A${reduced cost} |
| Annual savings from build | A${delta} |
| Retainer annual cost | A$29,964 |
| Net savings WITH retainer | A${delta - 29964} |

**If net savings is still positive:** "Even with the retainer, you're saving A${net}/year. And you get ongoing attention so the system never degrades."

---

## Upsell Path 3: Direct to Partner (A$0 → A$2,497/mo)

**For clients who skip Audit and Build entirely.** Use when a prospect clearly needs ongoing automation (multiple workflows, frequent changes, no internal team).

### The Script

> "For what you're describing — {multiple workflows across teams} — a one-off build won't serve you well. You need ongoing automation capacity. My AI Partner retainer at A$2,497/month covers up to 3 active workflows with monthly tuning, priority support, and quarterly strategy reviews. Think of it as having an automation engineer on retainer for 1/5 the cost of a full-time hire."

---

## Upsell Timing Triggers

| Trigger | What to Do |
|---|---|
| **Audit delivered** | Pitch Audit→Build within the deliverable call |
| **Build mid-project praise** | Plant the retainer seed: "This is the kind of thing a retainer covers ongoing." |
| **Build handoff** | Full retainer pitch (Ask 2 from offboarding) |
| **Warranty check-in (Day 7)** | Soft touch: "Everything running smoothly? Any features you wish it had?" |
| **Warranty check-in (Day 25)** | Retainer revisit: "Ready for that retainer conversation?" |
| **Client reports a bug** | "This is exactly what a retainer catches before you notice it." |
| **Client asks for a change** | "Happy to — this falls under retainer scope. Want to set that up?" |
| **Quarterly review** | Natural upsell to higher tier or additional workflows |

---

## Upsell Objection Handling

### "We can't afford the monthly commitment"

> "I understand. Two options: 1) We keep things ad-hoc — you ping me when you need changes, I quote each one. Typically that costs more over a year than the retainer. 2) We start with a lighter retainer at A${lower amount}/month covering 1 workflow with basic support. You can upgrade anytime."

### "We'll manage it ourselves"

> "Totally fair. I'll document everything so your team can handle it. One thing to watch: the #1 reason automations break isn't the code — it's API changes and edge cases that emerge after the first month. If you hit one of those and don't have time to debug it, I'm here."

### "Let's wait and see"

> "Smart — let the system prove itself. I'll check in at the end of the warranty period. By then you'll know exactly what needs ongoing attention."

---

## Upsell Metrics to Track

| Metric | Target |
|---|---|
| Audit→Build conversion | 40-50% |
| Build→Retainer conversion | 25-35% |
| Average time from audit to upsell close | 2-7 days |
| Revenue per client (with upsells) | 3-5× initial engagement |

**Goal:** Every A$497 audit client should be worth A$3,000-5,000 lifetime. Every A$1,497 build client should be worth A$10,000+ lifetime (build + 6-12 months retainer).

---

## Quick-Reference Upsell Scripts

```
AUDIT→BUILD:  "Finding #1 is costing you A$X/year. I can fix it in Y days for A$1,497."
BUILD→RETAINER: "Ongoing tuning + priority support — A$2,497/month. No more quoting every change."
DIRECT→PARTNER: "You need ongoing capacity, not a one-off build. A$2,497/month = automation engineer on retainer."
HESITATION: "Let's scope back to the core fix. Add the rest when you've seen value."
```

---

## Related Documents

- `AI_AUTOMATION_AUDIT_CHECKLIST.md` — The audit deliverable that triggers Upsell Path 1
- `CLIENT_OFFBOARDING.md` — Ask 2 (retainer pitch) during handoff
- `PRICING_PSYCHOLOGY_GUIDE.md` — Pricing anchoring and decoy effect
- `Proposal_Template.html` — SOW for upsold builds
- `RETAINER_AGREEMENT.html` — Contract for retainer upsells
- `LEAD_TRACKER.html` — Track upsell stages
- `QUARTERLY_REVIEW_TEMPLATE.md` — QBR upsell opportunity

---

*Upselling isn't selling. It's showing clients the next logical step based on what you've already proven. If the audit found real problems, the build is the obvious fix. If the build is delivering value, the retainer is the obvious protection.*
