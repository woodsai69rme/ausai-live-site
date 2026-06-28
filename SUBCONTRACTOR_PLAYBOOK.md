# Subcontractor Playbook — AusAI Tech

> **Purpose:** How to find, vet, brief, pay, and manage subcontractors when you hit the solo consultant capacity ceiling (3+ concurrent clients). This is how you scale without burning out.
> **When to use:** When you have 3+ active builds and can't take on more without sacrificing quality.
> **Prerequisite:** `PROJECT_MANAGEMENT_SOP.md` (multi-client ceiling), `COMPLIANCE_CHECKLIST.md` (ABN requirements)

---

## The Subcontractor Philosophy

You're not building an agency. You're extending your capacity for overflow work. The goal is to find 2-3 reliable specialists who can take a build brief and deliver with minimal hand-holding.

**Rule 1:** Subcontract the BUILD, not the relationship. You own the client. The sub owns the code.
**Rule 2:** Pay fixed-price per project, not hourly. Aligns incentives — they want to finish, not bill more hours.
**Rule 3:** Every sub engagement is a trial. 2 projects minimum before you trust them with a client-facing role.

---

## Where to Find Subcontractors

| Channel | Best For | Quality Signal |
|---|---|---|
| **GitHub** (n8n contributors, automation repos) | n8n specialists | Code quality visible in their repos |
| **Upwork** (filter: 90%+ success, 10+ projects) | General automation | Review history, portfolio, test project |
| **Fiverr Pro** (verified only) | Quick tasks, overflow | Pro badge = platform-vetted |
| **n8n Community Forum** | n8n specialists | Active contributors, deep expertise |
| **Twitter/LinkedIn** (#n8n, #automation tags) | Specialists | Portfolio visible in their posts |
| **Referral from other consultants** | Highest quality | Warm intro beats all |

---

## The Vet Process (3 Steps, 45 Minutes Total)

### Step 1: Portfolio Review (15 min)

- [ ] 3+ visible projects they can show (screenshots, links, or descriptions)
- [ ] At least 1 project similar to what you'd brief them on
- [ ] Evidence of error handling (not just "happy path" builds)
- [ ] Evidence of documentation (they document what they build)
- [ ] **Red flag:** Can't show any portfolio → move on

### Step 2: Paid Test Project (15 min to brief)

**Give them a small, self-contained task from your backlog.** A$100-300 fixed price. 2-3 hours of work.

Example: "Build an n8n workflow that monitors {URL} for changes and sends a Slack alert when something changes. Include error handling and basic documentation."

**Evaluate:**
- [ ] Delivered on time?
- [ ] Included error handling?
- [ ] Included documentation?
- [ ] Asked clarifying questions before building? (GOOD — they're thoughtful)
- [ ] Code quality: clean, commented, modular?
- [ ] Communication: responsive, clear, professional?

### Step 3: Debrief Call (15 min)

- Walk through their test project together
- Ask: "What would you have done differently with more time?"
- Ask: "What's your availability? Typical turnaround on a 10-hour project?"
- Ask: "What's your rate for fixed-price projects?"
- Discuss: communication preferences (Slack? Email? Async?), timezone, availability

---

## The Brief Template (Send for Every Project)

```
PROJECT BRIEF — {Project Name}
Client industry: {brief — no identifying details}
Problem: {1-sentence description}
Desired outcome: {1-sentence result}

TOOLS:
- Workflow platform: {n8n / Make / Python}
- Integrations: {list of APIs/systems involved}
- AI/LLM: {OpenRouter model if applicable}
- Hosting: {Railway / Vercel / client's infra}

SCOPE:
- {Deliverable 1}
- {Deliverable 2}
- {Deliverable 3}

NOT IN SCOPE:
- {Exclusions — be specific}

REQUIREMENTS:
- Error handling: retry logic, Slack alert on failure
- Documentation: README with setup, troubleshooting, credentials
- Testing: provide test data or describe test scenarios
- Security: API keys via environment variables, input sanitisation

TIMELINE:
- Brief accepted by: {date}
- First draft for review: {date}
- Final delivery: {date}

BUDGET:
- Fixed price: A${amount}
- Payment: 50% on delivery of working draft, 50% on final delivery
- Revisions: 1 round included, additional at A${rate}/hour

FILES:
- Reference documents attached: {links}
- Existing code/templates: {if applicable}
```

---

## Pricing Your Subs

| Project Size | Your Client Price | Pay Sub | Your Margin |
|---|---|---|---|
| Small (5-10 hrs) | A$500-1,000 | A$300-600 | 40% |
| Medium (10-20 hrs) | A$1,000-2,000 | A$600-1,200 | 40% |
| Large (20-40 hrs) | A$2,000-4,000 | A$1,200-2,400 | 40% |
| Build (standard) | A$1,497 | A$800-1,000 | 33-47% |

**Rule:** Your margin should be 30-50%. You're paid for client management, quality assurance, and relationship ownership. The sub is paid for building.

---

## Managing Subcontractors

### Communication

- [ ] Async-first (Slack or email). Avoid real-time unless urgent.
- [ ] Daily check-in during active build (1 Slack message: "Progress: {X}%. Blockers: {none/X}.")
- [ ] Weekly video call (15 min) for complex projects

### Quality Assurance (Before Client Delivery)

- [ ] **Code review:** Check for error handling, security, documentation
- [ ] **Run the workflow yourself:** At least 3 test runs with different inputs
- [ ] **Edge case testing:** Empty input, large payload, API timeout, special characters
- [ ] **Security review:** Apply the checklist from `AI_AUTOMATION_AUDIT_CHECKLIST.md`
- [ ] **Documentation review:** Is the README client-ready?

### Payment

- [ ] **Never pay 100% upfront.** 50% on draft, 50% on final.
- [ ] Pay within 7 days of acceptance (fast payment builds loyalty)
- [ ] Use PayPal, Wise, or bank transfer
- [ ] If they quote an ABN on their invoice: no withholding required. If they don't quote an ABN, you must withhold 47% (ATO PAYG withholding trigger: no ABN on invoice, regardless of whether they actually have one). Verify with your accountant.

---

## Subcontractor Agreement (Key Clauses)

Every sub should agree to (in writing, even if just email):

1. **IP assignment:** All work product is owned by you (AusAI Tech) upon payment
2. **Confidentiality:** No discussing clients publicly, no portfolio use without permission
3. **Non-solicitation:** Cannot approach your clients directly for 12 months
4. **Independent contractor:** They're not your employee — no benefits, no super, no insurance
5. **Delivery standard:** Must include documentation, error handling, and pass your QA

**Template:** Adapt `RETAINER_AGREEMENT.html` (change "retainer" to "project" and "monthly" to "fixed price")

---

## When to Fire a Sub

| Signal | Action |
|---|---|
| Missed 2 deadlines without proactive communication | Fire immediately |
| Delivered work that fails your QA 2× | Fire after second failure |
| Client complains about quality you missed | Your fault for not QA-ing. Fix the sub or fire. |
| Communicated directly with your client without permission | Fire immediately — this is a trust breach |
| Raised rates mid-project | Finish this project, don't re-hire |
| Ghosted for >48 hours during active build | Send 1 warning. Second time = fire. |

---

## Scaling Targets

| Month | Active Clients | Subs Needed | Your Role |
|---|---|---|---|
| Month 1-2 | 1-2 | 0 | Do everything yourself |
| Month 3-4 | 3-4 | 1 (overflow) | Client-facing + QA |
| Month 5-6 | 4-6 | 1-2 | Client-facing + QA + biz dev |
| Month 7-12 | 6-10 | 2-3 | High-level strategy + client relationships |

---

## Related Documents

- `PROJECT_MANAGEMENT_SOP.md` — The phases your sub will work within
- `AI_AUTOMATION_AUDIT_CHECKLIST.md` — Security review applied to sub work
- `TECH_STACK_DECISION_TREE.md` — Tool selection you'll brief the sub on
- `AUTOMATION_TEMPLATE_PACK.md` — Templates you'll give subs to speed them up
- `COMPLIANCE_CHECKLIST.md` — ABN/payment rules for Australian subs

---

*The solo ceiling is real. At 3 concurrent clients, you choose: raise prices, subcontract, or burn out. Subcontracting is how you scale beyond yourself without building an agency.*
