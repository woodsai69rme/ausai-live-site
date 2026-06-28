# Project Management SOP — AusAI Tech (Internal)

> **Purpose:** Standardised, lightweight project management for solo consultant delivery. No bloated PM software — just a repeatable checklist you execute per project.
> **When to use:** Kickoff to handoff for every paid engagement (AI Build $1,497+ and custom projects).
> **Prerequisite:** `First_Client_Onboarding.md` (client is onboarded, SOW signed, 50% deposit paid).

---

## The Solo PM Philosophy

You're a team of one. You don't need Jira, Asana, or Monday.com. You need:

1. **One document** the client can see (shared status page)
2. **One calendar** with milestone dates
3. **One checklist** you tick through per project phase

That's it. Complexity is the enemy of delivery speed.

---

## Project Phases

| Phase | Duration | What Happens | Client Involvement |
|---|---|---|---|
| **0 — Kickoff** | Day 0-1 | SOW signed, deposit paid, intake complete, access granted | High (provide credentials, review intake) |
| **1 — Architecture** | Day 1-3 | System design, tool selection (use `TECH_STACK_DECISION_TREE.md`), architecture diagram | Low (review diagram, 1 call) |
| **2 — Build** | Day 3-10 | Core automation built, tested internally | None (heads-down work) |
| **3 — Client Review** | Day 10-12 | Demo to client, feedback gathered, 1 round of revisions | High (attend demo, provide feedback) |
| **4 — Polish** | Day 12-14 | Revisions applied, final testing, documentation written | Low (review documentation) |
| **5 — Handoff** | Day 14 | Delivery call, training, testimonial ask | High (attend handoff call) |
| **Post — Warranty** | Day 14-44 | 30-day bug-fix warranty, retainer pitch, case study | Medium (report bugs, respond to check-ins) |

**Total timeline:** 14 days to delivery (standard), 44 days including warranty.

---

## Phase 0 — Kickoff Checklist

- [ ] SOW signed by both parties
- [ ] 50% deposit received (Stripe confirmation)
- [ ] Client added to `LEAD_TRACKER.html` → stage "Active — Building"
- [ ] Intake form received and reviewed
- [ ] All system access credentials received:
  - [ ] Platform logins (WordPress, Shopify, CRM, etc.)
  - [ ] API keys (read-only where possible)
  - [ ] Database access (if needed)
  - [ ] Third-party tool logins
- [ ] Shared Slack/Discord channel created
- [ ] Google Drive / Notion workspace created
- [ ] Client status page URL created (simple HTML page or Notion doc)
- [ ] Milestone dates set in calendar (Days 3, 10, 12, 14)
- [ ] Kickoff DM sent: "All received — I'm building the architecture now. You'll see a diagram and tool list by Day 3."

---

## Phase 1 — Architecture Checklist

- [ ] System diagram drafted (draw.io, Excalidraw, or pen and paper)
- [ ] Tool stack selected (reference `TECH_STACK_DECISION_TREE.md`)
- [ ] Data flow mapped: sources → transformations → destinations
- [ ] Error handling strategy documented (retry logic, alerting, fallbacks)
- [ ] Architecture review call booked with client (15-20 min)
- [ ] Client approves architecture (written confirmation)
- [ ] Architecture doc added to shared workspace

**Status update template (send to client):**

> **Subject:** Architecture ready for review
>
> Hi {NAME},
>
> The system architecture is drafted. Here's what I'm building:
>
> - **Tools:** {n8n / Python / Make / etc.}
> - **Data flow:** {X → Y → Z}
> - **Error handling:** {retry strategy, alerting method}
> - **Timeline:** Build complete by Day 10, your review Day 10-12, handoff Day 14.
>
> Diagram attached. Any changes before I start building?
>
> Best,
> Karma

---

## Phase 2 — Build Checklist

This is your heads-down work. No client involvement unless you hit a blocker needing their input.

- [ ] Development environment ready (n8n instance, Python env, etc.)
- [ ] Core workflow built and tested with sample data
- [ ] Edge cases tested:
  - [ ] Empty input → graceful handling
  - [ ] Rate-limited API → retry with backoff
  - [ ] Malformed data → error logged, not crashed
  - [ ] Network timeout → fallback or queue
- [ ] Error notifications configured (Slack/email alert on failure)
- [ ] Monitoring set up (basic health check or uptime monitor)
- [ ] API keys rotated from test to production
- [ ] Security checklist completed (from `AI_AUTOMATION_AUDIT_CHECKLIST.md` §Security Scan)
- [ ] Documentation draft started (README, credentials, architecture diagram)
- [ ] Self-review: walk through the workflow as if you were the client

**Rule:** If you find yourself stuck for >30 minutes on any single issue, message the client with a specific question. Don't guess about their business logic.

---

## Phase 3 — Client Review Checklist

- [ ] Internal testing complete (you've run it end-to-end 3+ times without errors)
- [ ] Demo environment ready (separate from production, if applicable)
- [ ] Client demo call scheduled (30 min)
- [ ] **Demo agenda:**
  - 0-5 min: Show the happy path (it works!)
  - 5-15 min: Show edge cases (how it handles errors gracefully)
  - 15-25 min: Client Q&A and feedback
  - 25-30 min: Document requested changes, set expectations
- [ ] All feedback documented in writing (shared doc or email)
- [ ] Revisions scoped: which are in-scope (bug fixes, minor tweaks) vs out-of-scope (new features = Change Order)

**Revision scope guardrail:**

> "I've noted {N} items. Items 1-{X} are included. Items {X+1}-{N} are new features — I'll quote those as a Change Order. Sound fair?"

---

## Phase 4 — Polish Checklist

- [ ] All in-scope revisions applied
- [ ] Final round of testing (same edge cases as Phase 2)
- [ ] Documentation completed:
  - [ ] README.md (how to use, what to do if something breaks)
  - [ ] Credentials list (where keys live, how to rotate)
  - [ ] Architecture diagram (final version)
  - [ ] Troubleshooting guide (top 5 things that might go wrong + fixes)
- [ ] Client trained on basic operations:
  - [ ] How to monitor (check dashboard/logs)
  - [ ] How to make minor changes (prompt edits, filter tweaks)
  - [ ] What NOT to touch (core workflow logic)
- [ ] Final invoice prepared (remaining 50%)
- [ ] Handoff call scheduled

---

## Phase 5 — Handoff Checklist

Follow `CLIENT_OFFBOARDING.md` structure:
- [ ] Demo completed (live walkthrough)
- [ ] Training delivered (client can operate independently)
- [ ] All documentation sent via email
- [ ] Final invoice sent
- [ ] **Testimonial asked** (Ask 1)
- [ ] **Retainer pitched** (Ask 2)
- [ ] **Referral asked** (Ask 3, if appropriate)
- [ ] Warranty terms confirmed (30 days, bug fixes only)
- [ ] Calendar reminders set: Day 7, 14, 25, 30 check-ins

---

## Status Page Template

Every client gets a simple status page. Host as a shared Notion page, Google Doc, or static HTML.

```
PROJECT STATUS — {Project Name}
Last updated: {Date}

📊 OVERALL: 🟢 On Track / 🟡 At Risk / 🔴 Blocked

✅ COMPLETED:
- {Completed item 1}
- {Completed item 2}

🔄 IN PROGRESS:
- {Current item} — ETA {Date}

⏳ UP NEXT:
- {Next item} — starts {Date}

🚧 BLOCKERS:
- None / {Describe blocker and what you need from client}

📅 KEY DATES:
- Architecture review: {Date} ✅
- Build complete: {Date}
- Client review: {Date}
- Handoff: {Date}
- Warranty expires: {Date}
```

Update this once per phase (not daily). The client can check it anytime without pinging you.

---

## Escalation Triggers

If any of these happen, stop and reassess:

| Trigger | Response |
|---|---|
| **Client unresponsive for >48 hours** during Phase 0-3 | Send 1 nudge. If no response in 72h, pause work and send: "Pausing work until I hear back — no rush, just want to make sure we're aligned." |
| **Build milestone missed by >2 days** | Message client with revised timeline BEFORE the original deadline. Proactively own the delay. |
| **Client requests 3+ revision rounds** | Convert to Change Order. "We've done the agreed revision round. Additional changes are new scope — I'll quote them." |
| **Client contests invoice** | Stop all work. Resolve payment before continuing. Reference SOW §5. |
| **API key / credential expires mid-build** | Message client immediately. "Need a refreshed key for {service}. Can't continue without it." |
| **You realise the SOW underestimated by >50%** | Honest conversation: "I've hit complexity I didn't anticipate in scoping. Here's what changed. Here's what it means for timeline/cost. Options: A) scope back, B) budget increase, C) cancel with partial refund." |

---

## Tools Per Phase (Quick Reference)

| Phase | Tools Open |
|---|---|
| **0 — Kickoff** | `First_Client_Onboarding.md`, `LEAD_TRACKER.html`, `Invoice_Template.html` |
| **1 — Architecture** | `TECH_STACK_DECISION_TREE.md`, draw.io / Excalidraw |
| **2 — Build** | n8n / Python / Make, `AI_AUTOMATION_AUDIT_CHECKLIST.md` §Security |
| **3 — Review** | `Proposal_Template.html` (for change orders), `EMAIL_TEMPLATES.md` (status updates) |
| **4 — Polish** | Documentation templates, `CASE_STUDY_TEMPLATE.md` (start drafting) |
| **5 — Handoff** | `CLIENT_OFFBOARDING.md`, `Invoice_Template.html`, `RETAINER_AGREEMENT.html` |
| **Post — Warranty** | `LEAD_TRACKER.html`, `Revenue_Dashboard_Static.html`, `CASE_STUDY_TEMPLATE.md` |

---

## Status Report Templates

### Weekly Update (send every Friday during active build)

> **Subject:** {Project Name} — Week {N} update
>
> Hi {NAME},
>
> This week:
> - ✅ {completed item 1}
> - ✅ {completed item 2}
>
> Next week:
> - 🔄 {upcoming item 1} — targeting {Day}
> - 🔄 {upcoming item 2} — targeting {Day}
>
> On track for handoff {date}. No blockers from my side.
>
> Questions? Just reply.
>
> Best,
> Karma

### Delay Notification (send immediately when you're behind)

> **Subject:** {Project Name} — timeline adjustment
>
> Hi {NAME},
>
> I want to be upfront: I'm {X days} behind on the {milestone}. Here's why: {1-sentence reason — be honest}.
>
> New timeline: {revised date}. I'm adding {extra buffer} to make sure this doesn't happen again.
>
> No additional cost to you — this is on me.
>
> Let me know if this creates any issues on your side.
>
> Best,
> Karma

---

## Multi-Client Management (When You Have 2+ Active Projects)

**Rule of thumb:**
- 1 active project = full focus, no need for scheduling
- 2 active projects = alternate days (Mon/Wed/Fri = Client A, Tue/Thu = Client B)
- 3 active projects = you've hit the consulting-cap ceiling. Time-block: 9-12 Client A, 1-4 Client B, 5-6 Client C admin. Beyond this, quality suffers and clients notice.

**If you're at 3+ clients:** decide — hire subcontractors? Raise rates? Both? (per `POST_LAUNCH_OPERATIONS.md`). Do not accept a 4th until you've made this decision.

---

## Related Documents

- `First_Client_Onboarding.md` — Client intake to SOW signing (runs before this SOP)
- `CLIENT_OFFBOARDING.md` — Handoff to testimonial (runs after this SOP)
- `TECH_STACK_DECISION_TREE.md` — Tool selection during architecture phase
- `AI_AUTOMATION_AUDIT_CHECKLIST.md` — Security checks during build
- `EMAIL_TEMPLATES.md` — Status updates and delay notifications
- `LEAD_TRACKER.html` — Update client stage throughout
- `Proposal_Template.html` — Change orders during review
- `SCOPE_CREEP_DEFENSE.md` — Advanced boundary-setting when scope starts expanding

---

*Good project management for a solo consultant isn't about Gantt charts. It's about: 1) the client always knows what's happening, 2) you never miss a deadline without proactively communicating, and 3) the scope boundary is crystal clear from Day 0.*
