# AI Automation Audit Checklist — AusAI Tech

> **Purpose:** Standardised, repeatable SOP for the A$497 AI Audit. Follow this for every engagement to deliver consistent quality in ~2.5 hours of billable time.
> **Deliverable:** PDF report with system inventory, process map, risk scorecard, prioritised roadmap.
> **Prerequisite:** `Discovery_Call_Script.md` (first contact), `First_Client_Onboarding.md` (intake form responses)

---

## Phase 0 — Pre-Audit Prep (15 min, day before call)

- [ ] **Read intake form:** Client's 9 answers from `First_Client_Onboarding.md` §Intake Form
- [ ] **Scan their tech stack:** Visit their website. Open DevTools → Network tab. Note: CMS (WordPress/Webflow/Shopify?), analytics (GA4? Hotjar?), chat widget (Intercom? Tidio?), payment processor, CDN.
- [ ] **Check APIs:** For each tool spotted, quickly check if it has a public API (google `{tool} api docs`). Note API availability in your audit spreadsheet.
- [ ] **Competitor check:** Search `{client industry} automation consultant` — note 2-3 competitors and their pricing for context during the call.
- [ ] **Prepare 3 quick wins:** Based on intake form + tech scan, prepare 3 low-effort, high-impact suggestions you can drop during the call to demonstrate value immediately.
- [ ] **Open audit template:** Have `Proposal_Template.html` (or a Google Doc version) open and pre-filled with client name, date, and intake answers.

---

## Phase 1 — The Audit Call (90 min)

### Segment 1: System Inventory (30 min)

**Goal:** Map every tool, every data flow, every manual step.

| # | Question | What You're Looking For |
|---|---|---|
| 1 | "Walk me through a typical customer journey — from first touch to delivery." | Where are the manual handoffs? |
| 2 | "Which tool does what? Let's list every piece of software you use." | Overlaps, gaps, orphaned tools |
| 3 | "What data moves between these tools — and how?" | Zapier? CSV export/import? Manual copy-paste? |
| 4 | "Which of these tools do you dread opening?" | Pain points; likely automation candidates |
| 5 | "If you could wave a magic wand and make ONE process fully automatic, which would it be?" | North star — this will anchor the roadmap |

**Output:** A list of 5-15 tools/systems, each marked: API available (Y/N), pain level (1-5), automation potential (High/Med/Low).

### Segment 2: Bottleneck Identification (25 min)

**Goal:** Quantify the cost of the top 3-5 bottlenecks.

| # | Question | What You're Looking For |
|---|---|---|
| 6 | "For {pain point #1}: How many hours per week does this eat? Whose time?" | Hours × people × hourly cost = annual waste |
| 7 | "What's the cost of getting this wrong? Late responses? Missed orders? Compliance risk?" | Hard dollar impact + soft risk |
| 8 | "When was the last time this broke? What happened?" | Urgency; failure cost |
| 9 | "If we fixed this tomorrow, what's the first thing you'd do with the freed-up time?" | Motivation; positions you as the enabler |
| 10 | "Has anyone tried to automate this before? What happened?" | Past failures = landmines to avoid |

**Output:** Top 3-5 bottlenecks with estimated annual waste (A$), automation difficulty (Easy/Moderate/Hard), and estimated build time.

### Segment 3: Security & Compliance Scan (20 min)

**Goal:** Identify red flags that position you as the security-aware consultant.

| Check | Red Flag If... | Why It Matters |
|---|---|---|
| **API keys in frontend code** | DevTools → Sources → search `api_key`, `secret`, `token` | Exposed keys = instant breach risk |
| **No HTTPS enforcement** | Check if `http://` redirects to `https://` | Data in transit unprotected |
| **Form endpoints exposed** | Check contact/checkout forms for CSP headers | Spam, injection risk |
| **Third-party script sprawl** | DevTools → Network → count unique 3rd-party domains | Each script = potential supply chain attack |
| **Customer data handling** | "Where do you store customer data? Who can access it?" | GDPR/Privacy Act compliance |
| **Backup frequency** | "When was your last backup? When was it last tested?" | Ransomware readiness |
| **Access control** | "Who has admin access? Any ex-employees still active?" | Insider threat; credential hygiene |
| **AI model safety** | "Any AI/LLM tools touching customer data? Any prompt injection concerns?" | AI-specific risk; compliance |
| **Hardcoded credentials** | "Any passwords or API keys in config files or GitHub repos?" | Common in small businesses |
| **Auto-update status** | "Are your plugins/CMS/themes on auto-update?" | Most breaches exploit unpatched CVEs |

**Output:** Risk scorecard (Critical/High/Medium/Low) for each category. 3-5 top risks with remediation estimates.

### Segment 4: Automation Opportunities Map (15 min)

**Goal:** Map every process to an automation tier.

For each process identified in Segments 1-2, classify:

| Automation Tier | Fits When... | Example | Typical Cost |
|---|---|---|---|
| **Tier 1: No-code** | Simple if/then, data moves between SaaS tools | Zapier: "New Typeform → Slack alert + Airtable row" | A$0-50/month |
| **Tier 2: Low-code** | Multi-step logic, conditional branching, API chaining | n8n: "Scrape competitor prices → compare → Slack DM if undercut" | A$0-30/month (self-hosted) |
| **Tier 3: AI-enhanced** | Needs reasoning, classification, generation, or unstructured data | OpenAI API: "Classify 500 support tickets → route to correct team" | A$0-200/month API costs |
| **Tier 4: Full custom** | Complex state machines, real-time, compliance-heavy | Custom Python + Supabase: "Predictive inventory ordering with supplier API integration" | A$1,500-5,000 build |

**Output:** A table with: Process name → Current pain (hrs/week) → Tier → Build estimate → Monthly running cost → Annual saving.

---

## Phase 2 — Post-Call Deliverable Assembly (45 min)

### Step 1: Fill the Audit Report Template (25 min)

Use this structure for every audit deliverable:

```
AUSAI TECH — AI AUTOMATION AUDIT
Client: {name} | Date: {date} | Auditor: karma

1. EXECUTIVE SUMMARY (½ page)
   - Top finding in 1 sentence
   - Annual savings opportunity: A$X
   - Payback period: Y months
   - Recommended next step

2. SYSTEM INVENTORY ({N} tools audited)
   [Table: Tool | Purpose | API? | Pain Score | Automation Fit]

3. TOP BOTTLENECKS (ranked by cost)
   [For each of 3-5: Description, Annual Cost, Fix, Build Time, Tier]

4. SECURITY SCORECARD
   [Traffic-light table: Check | Status | Risk | Remediation]
   🟢 = Good  🟡 = Needs attention  🔴 = Critical

5. PRIORITISED ROADMAP (90-day)
   [Table: Month | Initiative | Effort | Cost | Saving | ROI]
   Month 1 (Quick Wins): 2-3 Tier 1-2 automations
   Month 2 (Core Build): 1-2 Tier 3 automations
   Month 3 (Scale): Tier 4 + monitoring

6. INVESTMENT SUMMARY
   - Total recommended build: A$X
   - Annual savings: A$Y
   - ROI: Z%
   - Payback: W months

7. NEXT STEPS
   "Based on this audit, I recommend starting with..."
   → Links to booking page for Build Kickoff or Strategy Deep-Dive
```

### Step 2: Bake in the Upsell Hooks (10 min)

Every finding in the audit should map to a productized service:

| Audit Finding | Upsell Hook |
|---|---|
| "5+ manual data transfers between tools" | → "This is exactly what our A$1,497 AI Build solves. We'd connect {Tool A} ↔ {Tool B} with error handling, retry logic, and Slack alerts when something fails." |
| "Customer emails going unanswered >4 hours" | → "Our AI chatbot tier handles 80%+ of first-touch queries instantly. Build time: 5 days. Monthly cost: ~$30 in API fees." |
| "No backup. Last tested: never." | → "Our AI Partner retainer includes weekly verified backups, security patches, and uptime monitoring. A$2,497/month." |
| "Exposed API key in frontend code" | → "Critical. This needs fixing before anything else. We'll rotate all keys, implement server-side proxy, and audit all repos. 2 days. A$800." |
| "Team spending 15 hrs/week on data entry" | → "Automating this alone pays for the entire engagement in {X} months. Let's start here." |

### Step 3: Polish & Deliver (10 min)

- [ ] Convert to PDF (print from browser or use pandoc)
- [ ] Add client logo (if provided) to header
- [ ] Number pages (1 of 7, etc.)
- [ ] Email with subject: "AusAI Tech — AI Audit Report: {Client Name}"
- [ ] Body: 3-line summary + PDF attached + link to book Build Kickoff
- [ ] Template: `EMAIL_TEMPLATES.md` → "Post-Discovery Follow-Up"

---

## Phase 3 — Post-Delivery Follow-Up (within 48 hours)

- [ ] **Day 1:** Send audit PDF (per Phase 2, Step 3)
- [ ] **Day 2:** Follow-up call (15 min) — "Walk me through which finding surprised you most"
- [ ] **Day 3:** Send proposal for the top-priority automation (use `Proposal_Template.html`)
- [ ] **Day 5:** If no response, send 1 no-pressure follow-up (see `EMAIL_TEMPLATES.md` nurture sequence)
- [ ] **Day 14:** Final follow-up. If no response, move to dormant in `LEAD_TRACKER.html`.

---

## Audit Quality Standards

| Criterion | Minimum | Target |
|---|---|---|
| Tools inventoried | 5+ | 10+ |
| Bottlenecks quantified (A$) | 3+ | 5+ |
| Security checks completed | 7 of 10 | 10 of 10 |
| Upsell hooks baked in | 3 | 5+ |
| Delivered within 24h of call | ✅ | ✅ |
| Total consultant time | 2.5 hrs | 2.0 hrs |

---

## Quick-Reference: Tools to Have Open During Audit

| Tool | Purpose |
|---|---|
| Browser DevTools (F12) | Network tab, Sources tab, Console |
| Google Docs / Notion | Live notes during call |
| `Proposal_Template.html` | Pre-filled for instant SOW if client is ready |
| `Discovery_Call_Script.md` | Phase structure reference |
| `SERVICE_TIER_ONEPAGER.html` | Leave-behind after call |
| `LEAD_TRACKER.html` | Update after call |
| `COMPLIANCE_CHECKLIST.md` | If security findings involve compliance advice |

---

## Red Flags During Audit (When to Walk or Reprice)

| Red Flag | Response |
|---|---|
| Client won't share access to systems | "I can't audit what I can't see. The report will be surface-level only — A$250 for a light version." |
| "We're being sued / under investigation" | "I'm not a lawyer. I can do a technical audit but can't advise on legal exposure. You need a solicitor for that." |
| Client asks you to hack/access competitor systems | "That's illegal. I won't do it. Happy to audit your own systems though." |
| "Can you just copy what {competitor} has?" | "I build custom automation, not clones. I can analyse their approach and design something better for your specific needs." |
| 3+ reschedules before audit call | "Let's reconnect when your schedule settles. My calendar link is below." |

---

## Related Documents

- `Discovery_Call_Script.md` — First contact (runs before this audit)
- `First_Client_Onboarding.md` — Post-audit when client buys Build
- `Proposal_Template.html` — SOW for the recommended build
- `SERVICE_TIER_ONEPAGER.html` — Leave-behind pricing card
- `EMAIL_TEMPLATES.md` — Audit delivery email template
- `LEAD_TRACKER.html` — Move prospect from "Audit Delivered" → "Proposal Sent"
- `TECH_STACK_DECISION_TREE.md` — Use during Segment 4 to classify automations

---

*Every audit should produce at least 3 specific, dollar-quantified findings. If you can't find 3, you haven't looked deep enough. The audit is your single best conversion tool — make every one count.*
