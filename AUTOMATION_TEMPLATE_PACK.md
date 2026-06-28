# Automation Template Pack — AusAI Tech

> **Purpose:** Reusable automation blueprints, code snippets, and system prompts. Speed up every build by starting from battle-tested templates instead of blank canvases.
> **When to use:** During the Build phase of every project. Open this before you start building — you likely have a template for it.
> **Prerequisite:** `TECH_STACK_DECISION_TREE.md` (tool selection), `AI_AUTOMATION_AUDIT_CHECKLIST.md` (security checks)

---

## Template Inventory

| # | Template | Category | Complexity | Reuse Frequency |
|---|---|---|---|---|
| 1 | AI Customer Support Pipeline | CRM / Support | Medium | High |
| 2 | Lead Scoring + Slack Alert | CRM / Sales | Low | High |
| 3 | Invoice Generator + Follow-up | Finance / Ops | Medium | High |
| 4 | Data Enrichment (Clearbit-style) | Data / Enrichment | Medium | Medium |
| 5 | Social Media Post Scheduler | Marketing | Low | Medium |
| 6 | Competitor Price Monitor + Alert | E-commerce | Medium | Medium |
| 7 | Automated Weekly Report Generator | Reporting | Low | High |
| 8 | Form → Database → Dashboard | Data / Ops | Low | Very High |

---

## Template 1: AI Customer Support Pipeline

**Tools:** n8n + OpenRouter (Claude 3.5 Haiku) + Slack + Email
**Build time:** 4-6 hours
**Reuse frequency:** Very high (every chatbot/support build starts here)

### Architecture
```
Email/Slack message → n8n webhook → AI classification node → 
├─ 80% auto-resolved (AI drafts reply, sends) 
└─ 20% escalated → Slack alert to human with AI draft + context
```

### System Prompt (OpenRouter node)
```
You are a customer support AI for {CLIENT_NAME}. 
Tone: {professional/friendly/casual — client preference}.
Knowledge base: {paste FAQ / docs}.

Rules:
1. If the question is in the FAQ, answer directly.
2. If you're unsure or the question is complex, escalate with: "I'll have a team member get back to you within {X} hours."
3. Never make up information. Never promise refunds or legal outcomes.
4. Always include the original email subject in your response.
5. If the customer is angry, acknowledge their frustration and escalate.
```

### n8n Workflow Blueprint
```
1. Webhook (receive email/json)
2. Extract: subject, body, sender, timestamp
3. Code node: sanitize input (strip HTML, trim, max 2000 chars)
4. HTTP Request → OpenRouter (system prompt + user message)
5. IF node: check AI response for escalation keywords
6a. (No escalation): Email node → reply to sender with AI response
6b. (Escalation): Slack node → alert channel with full context
7. Database node → log interaction (Supabase)
8. Error trigger: if any node fails → Slack alert
```

### Edge Cases to Handle
- Empty email body → reply "Could you provide more detail?"
- API rate limit → retry 3× with 30s backoff, then escalate
- Non-English email → detect language, respond in same language
- Attachment → acknowledge receipt, escalate for human review

---

## Template 2: Lead Scoring + Slack Alert

**Tools:** n8n + Slack
**Build time:** 1-2 hours
**Reuse frequency:** Very high

### Architecture
```
Form submission → n8n webhook → score calculation → 
├─ High score → Slack alert + auto-DM draft
├─ Medium → CRM entry + nurture tag
└─ Low → CRM entry only
```

### Scoring Criteria (Customize per client)
```
Budget indication: "budget > $X" = +3 points
Timeline urgency: "within 30 days" = +2 points
Decision authority: "I'm the {CEO/founder/owner}" = +2 points
Specific use case named: +1 point
Referred by existing client: +3 points
Downloaded pricing page: +1 point
```

### Slack Alert Template
```
🚨 HIGH-VALUE LEAD: {Name} — {Company}
Score: {X}/10
Budget: {budget signal}
Timeline: {urgency signal}
Source: {form/page}
Action: Auto-drafted DM below ↓
---
Hi {Name}, saw you're interested in {topic}. {Personalized line}. Worth a 15-min call? {Calendly link}
```

---

## Template 3: Invoice Generator + Follow-up

**Tools:** n8n + Stripe + Email
**Build time:** 2-3 hours
**Reuse frequency:** High

### Architecture
```
Trigger (manual or scheduled) → Generate invoice in Stripe → 
Send email with payment link → Schedule follow-ups →
Day 3 reminder → Day 7 overdue notice → Day 14 final notice
```

### Email Sequence
- **Day 0:** Invoice email with Stripe Payment Link
- **Day 3:** Friendly reminder: "Just a heads-up — let me know if any questions."
- **Day 7:** Overdue notice: "Now past due — can we resolve this week?"
- **Day 14:** Final: "Last attempt — I'll need to pause work if unresolved."

---

## Template 4: Data Enrichment

**Tools:** n8n + OpenRouter + Supabase
**Build time:** 3-4 hours
**Reuse frequency:** Medium

### Architecture
```
CSV/API input → n8n → batch process (50 rows at a time) →
For each row: AI enriches (company size, industry, LinkedIn URL, contact guess) →
Write to Supabase → Export enriched CSV
```

### Enrichment Prompt
```
Given this company name and website:
Company: {name}
Website: {url}

Return JSON with:
- Industry category
- Estimated company size (1-10 / 11-50 / 51-200 / 201+)
- HQ location (city, country)
- Likely tech stack (from website signals)
- Public email domain pattern (e.g., firstname@company.com)

If uncertain, mark field as null.
```

---

## Template 5: Social Media Post Scheduler

**Tools:** n8n + Buffer API (or direct platform APIs) + Google Sheets
**Build time:** 1-2 hours
**Reuse frequency:** Medium

### Architecture
```
Google Sheet (content calendar) → n8n reads daily →
Posts to: LinkedIn / Twitter / Buffer queue →
Logs post URL + engagement stats back to sheet
```

---

## Template 6: Competitor Price Monitor

**Tools:** n8n + HTTP Request + Slack
**Build time:** 3-4 hours
**Reuse frequency:** Medium

### Architecture
```
Scheduled daily → HTTP Request (scrape competitor pricing pages — check target's robots.txt and ToS first) →
Parse prices → Compare to last known → 
If price changed (or new competitor): Slack alert →
Log to database for historical tracking
```

---

## Template 7: Automated Weekly Report Generator

**Tools:** n8n + OpenRouter + Google Docs/Email
**Build time:** 1-2 hours
**Reuse frequency:** Very high

### Architecture
```
Weekly trigger → Pull data from sources (Stripe, database, analytics) →
AI summarizes → Generate formatted email/PDF → Send to stakeholders
```

### Report Prompt
```
Generate a weekly summary from this data:
- Revenue this week: ${X}
- New customers: {Y}
- Support tickets: {Z} ({auto-resolved}% auto-resolved)
- System uptime: {U}%
- Top 3 issues this week

Format: executive summary (3 bullet points) + detailed breakdown + recommendations.
```

---

## Template 8: Form → Database → Dashboard

**Tools:** n8n + Supabase + simple HTML dashboard
**Build time:** 2-3 hours
**Reuse frequency:** Very high

### Architecture
```
Web form → n8n webhook → validate + sanitize → insert Supabase →
(Optional) AI enrichment → HTML dashboard (read-only API) →
Client views real-time dashboard
```

---

## Security Checklist (Apply to Every Template)

Before deploying any template to production:

- [ ] API keys use environment variables, not hardcoded
- [ ] Input sanitization on all user-facing inputs
- [ ] Rate limiting on AI API calls
- [ ] Error webhook → Slack alert on failure
- [ ] No customer data in error logs
- [ ] Database connections use read-only where possible
- [ ] Prompt injection hardening on AI nodes
- [ ] Tested with edge cases (empty input, special chars, large payloads)

---

## Template Storage

Keep reusable templates in:
```
C:/Users/karma/templates/n8n/     — n8n workflow JSON exports
C:/Users/karma/templates/prompts/ — system prompts and AI node configs
C:/Users/karma/templates/code/    — Python snippets and custom nodes
```

---

## Related Documents

- `TECH_STACK_DECISION_TREE.md` — Which tool for which template
- `AI_AUTOMATION_AUDIT_CHECKLIST.md` — Security checks applied to every template
- `PROJECT_MANAGEMENT_SOP.md` — Build phase where templates are used

---

*Don't build from scratch. Every project reuses 60-80% of a previous project's architecture. This pack is your library. Add to it after every build.*
