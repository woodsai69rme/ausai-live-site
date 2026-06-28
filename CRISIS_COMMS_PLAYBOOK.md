# Crisis Communications Playbook — AusAI Tech

> **Purpose:** What to do (and say) when projects go wrong. Pre-baked scripts for every failure mode so you don't freeze when it counts.
> **When to use:** The moment something breaks — missed deadline, broken deliverable, client escalation, payment dispute.
> **Prerequisite:** `PROJECT_MANAGEMENT_SOP.md` (escalation triggers), `SCOPE_CREEP_DEFENSE.md` (boundary setting), `First_Client_Onboarding.md` (SOW reference)

---

## The Golden Rule of Crisis Comms

**The client should hear about the problem from YOU, not discover it themselves.**

The difference between a "professional who handled it well" and a "freelancer who ghosted" is the 30 minutes after you realise something's wrong. Communicate early, communicate fully, communicate the fix.

---

## Severity Classification

| Level | Example | Response Window | Tone |
|---|---|---|---|
| **P1 — Critical** | Deliverable doesn't work in production, client losing money, data breach | **1 hour** (acknowledge), **4 hours** (fix) | Urgent, transparent, solution-focused |
| **P2 — Major** | Missed milestone by >2 days, feature broken but not blocking business | **4 hours** (acknowledge), **24 hours** (fix) | Proactive, apologetic, timeline-clear |
| **P3 — Minor** | Cosmetic bug, documentation error, minor delay (<2 days) | **24 hours** (acknowledge), **48 hours** (fix) | Casual, solution-oriented |
| **P4 — Admin** | Invoice question, contract clarification, access issue | **24 hours** | Helpful, straightforward |

---

## Crisis Response Template (Use for EVERY Crisis)

```
1. ACKNOWLEDGE — Within the response window, send a message that says:
   - What you've noticed
   - That you're working on it
   - When they'll hear from you next

2. DIAGNOSE — Fix the problem. Don't send another message until you have:
   - Root cause identified
   - Fix in progress or completed
   - Prevention plan

3. RESOLVE — Send the final update:
   - What happened (honest, no blame-shifting)
   - What you did to fix it
   - What you're doing to prevent recurrence
   - What this means for the client (timeline impact, if any)
```

---

## Scenario 1: Missed Deadline

**P2 — Major.** Most common solo consultant crisis.

### Acknowledge (send BEFORE the deadline)

> **Subject:** {Project Name} — timeline update
>
> Hi {NAME},
>
> I want to be upfront: I won't hit the {date} milestone for {deliverable}. I underestimated {specific reason — be honest}.
>
> New delivery date: {date}. I've added {buffer} to ensure this one holds.
>
> No additional cost — this is on me for misestimating.
>
> I'll send a progress update by {date} confirming we're on track.
>
> Best,
> Karma

**Why this works:**
- Sent BEFORE the deadline (shows you're watching)
- Takes ownership (no excuses)
- Gives a specific new date (not "soon")
- Removes cost concern immediately

### What NOT to send

> ❌ "Running a bit behind, should have it soon." (vague, no ownership, no new date)
> ❌ "The API changed and I had to redo everything." (blame-shifting; client doesn't care why, they care when)
> ❌ *Saying nothing and hoping they don't notice.* (They'll notice. It's always worse.)

---

## Scenario 2: Broken Deliverable in Production

**P1 — Critical.** The system you built is failing and the client is losing money/reputation.

### Acknowledge (within 1 hour)

> **Subject:** URGENT — {System Name} issue
>
> Hi {NAME},
>
> I've identified an issue with {system} — {brief description of what's happening}. I'm actively working on a fix right now.
>
> **Current impact:** {what's affected, what's NOT affected}
> **Estimated fix time:** {timeframe}
> **Workaround in meantime:** {temporary fix if available}
>
> I'll update you by {time} or sooner if I have a fix.
>
> Karma

### Resolve (after fix)

> **Subject:** RESOLVED — {System Name} back to normal
>
> Hi {NAME},
>
> The issue is resolved. Here's what happened:
>
> **Root cause:** {1-sentence explanation}
> **Fix applied:** {what you did}
> **Prevention:** {what you're changing so this doesn't recur}
> **Timeline impact:** {none / +X days}
>
> I've documented this in the project README. If you see any issues in the next 24 hours, ping me immediately.
>
> Best,
> Karma

---

## Scenario 3: Client Escalation (Angry Email/Call)

**P1-P2.** The client is unhappy and has escalated. They may threaten to cancel or dispute payment.

### De-escalation Formula

```
1. DON'T DEFEND — First response: acknowledge their frustration (no "but...")
2. VALIDATE — "I understand why you'd feel that way."
3. INVESTIGATE — "Let me look into this and get back to you with specific answers."
4. PROPOSE — "Here's what I can do to make this right."
5. FOLLOW THROUGH — Do exactly what you said, by when you said.
```

### Response Template

> **Subject:** Re: {their subject}
>
> Hi {NAME},
>
> I hear you — and I understand why you're frustrated. {Restate their concern in your own words to show you read it.}
>
> I want to resolve this properly. Let me:
> 1. Investigate {specific issue} — I'll get back to you by {time today}
> 2. Send you a specific plan to fix this
>
> Is there anything else you want me to look at while I'm digging in?
>
> Karma

**After investigation:**

> **Subject:** Follow-up: {issue} — plan to resolve
>
> Hi {NAME},
>
> I've looked into {issue}. Here's what I found and what I'm going to do:
>
> **What happened:** {1-2 sentence honest explanation}
> **What I'm doing:** {specific fix, with timeline}
> **What this means for you:** {impact on timeline/cost — be explicit}
>
> If this resolution works for you, I'll start immediately. If you'd prefer a different approach, let me know and we'll figure it out.
>
> Karma

---

## Scenario 4: Payment Dispute

**P1.** Client refuses to pay or has stopped payment.

### If the client raises a legitimate quality concern:

> "I want you to be happy with what you paid for. Let's get on a 15-minute call — you walk me through exactly what's not working, and I'll either fix it or adjust the invoice. Fair?"

This demonstrates good faith. Have the call. If the issue is real, fix it. If it's scope creep disguised as a quality complaint, reference the SOW.

### If the client is clearly in the wrong (ghosting, refusing to pay for delivered work):

**Step 1 — Friendly reminder (Day 8):**
> "Hi {NAME}, just a heads-up — invoice {INV-XXX} was due on {date}. Let me know if you need anything from me to process it."

**Step 2 — Direct (Day 14):**
> "Hi {NAME}, invoice {INV-XXX} for A${amount} is now 14 days past due. Per our SOW (Section 5), late payment interest may apply. Can we resolve this this week?"

**Step 3 — Final (Day 30):**
> "Hi {NAME}, this is my final attempt to resolve invoice {INV-XXX}, now 30 days past due. If I don't hear from you by {date + 5 days}, I'll need to pursue formal recovery. I'd much rather resolve this directly — can we talk?"

**After Day 35:** If no resolution, consult a lawyer or small claims tribunal. Record all communications. Reference the signed SOW. For amounts under A$5,000, the Australian small claims process is relatively accessible for sole traders.

---

## Scenario 5: You Made a Mistake (Self-Inflicted)

**P1-P3.** You pushed wrong code, deleted data, misconfigured something.

### The Honest Confession

> **Subject:** I made an error — {brief description}
>
> Hi {NAME},
>
> I need to own something: {honest description of what you did wrong}.
>
> Here's the impact: {what it means for them — be specific}
>
> Here's what I'm doing: {immediate fix + prevention}
>
> I take full responsibility. This shouldn't have happened, and I've already changed {process/tool/check} so it doesn't happen again.
>
> Let me know if you have questions. I'll update you when the fix is live.
>
> Karma

**Why this works:**
- Owning mistakes builds more trust than hiding them
- Clients respect honesty more than perfection
- A freelancer who admits errors is rare — it differentiates you

---

## Scenario 6: Client Ghosting During Active Project

**P2.** Client stops responding mid-project. You can't proceed without their input.

> **Subject:** Checking in — need your input to continue
>
> Hi {NAME},
>
> I'm at a pause point on {project} — I need your feedback on {specific item} before I can continue.
>
> No rush at all, just wanted to flag: the timeline will shift by however long the pause is. Happy to resume whenever you're ready.
>
> If you'd prefer to put this on hold for a bit, just say the word and I'll park it. Otherwise, ping me when you have 5 minutes and we'll pick up where we left off.
>
> Karma

**If no response in 7 days:**
> "Hi {NAME}, I'm going to pause formal work on {project} until I hear from you. No invoice for the paused period — we'll pick up the remaining scope whenever you're ready. Just reply when the timing works."

---

## Reputation Recovery (When It Goes Public)

If a client posts a negative review or public complaint:

1. **Do NOT respond publicly in detail.** One reply: "Hi {NAME}, I've reached out privately to resolve this. Check your email/DMs." This shows you're responsive without airing details.
2. **Resolve privately.** Follow the de-escalation formula.
3. **After resolution, ask:** "If you're satisfied with how we resolved this, would you consider updating your review? No pressure either way."
4. **Learn.** Every crisis is a process failure. Update your checklist so it doesn't repeat.

---

## Legal Trigger Points

Stop communicating and consult a lawyer at:

| Trigger | Why |
|---|---|
| Client threatens legal action | Any further communication is discoverable |
| Client demands full refund AND threatens to sue | Escalated beyond your ability to resolve informally |
| Data breach involving customer data | For entities covered by the Privacy Act (generally >$3M annual turnover): mandatory OAIC notification within 30 days. For smaller clients: still best practice to notify but not legally required. Check your client's obligations. |
| You receive a letter of demand | Don't ignore it. Lawyer up. |

**Prevention:** Professional Indemnity insurance (see `COMPLIANCE_CHECKLIST.md` Phase 8) covers legal costs in many of these scenarios.

---

## Post-Crisis Retrospective (Do This Every Time)

After any crisis, take 10 minutes to document:

```
CRISIS LOG — {Date}
- What happened: {1 sentence}
- Severity: P1/P2/P3/P4
- Root cause: {why it happened}
- Time to acknowledge: {minutes}
- Time to resolve: {hours}
- Client outcome: {resolved / escalated / lost}
- Process change: {what you'll do differently}
```

**Patterns to watch for:**
- 2+ P1 crises in a month → you're overcommitted or your testing process is broken
- Same root cause twice → your prevention plan failed
- All crises happen with one client → they're the problem, not you

---

## Quick-Reference: What To Do First

```
🚨 CRISIS DETECTED

1. DON'T PANIC. Open this doc.
2. CLASSIFY: P1/P2/P3/P4
3. ACKNOWLEDGE within the response window (use template)
4. DIAGNOSE: find root cause BEFORE sending update #2
5. RESOLVE: send fix + timeline impact
6. RETRO: log it, learn from it
7. Don't over-apologise. One sincere apology is enough. After that, focus on the solution.
```

---

## Related Documents

- `PROJECT_MANAGEMENT_SOP.md` — Escalation triggers, status communication, delay notification template
- `SCOPE_CREEP_DEFENSE.md` — When scope creep is the root cause
- `First_Client_Onboarding.md` — SOW reference for payment disputes
- `COMPLIANCE_CHECKLIST.md` — Insurance for legal protection
- `EMAIL_TEMPLATES.md` — Delay notification and general client communication templates

---

*Every solo consultant has crises. The difference between those who survive them and those who don't is 100% communication speed. The client doesn't need you to be perfect. They need you to be honest.*
