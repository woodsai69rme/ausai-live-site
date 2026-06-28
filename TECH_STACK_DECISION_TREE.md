# Tech Stack Decision Tree — AusAI Tech (Internal Fulfillment)

> **Purpose:** Fast, consistent tool selection for every client engagement. No more "should I use Make or n8n for this?" — follow the tree.
> **When to use:** During audit calls (Segment 4 of `AI_AUTOMATION_AUDIT_CHECKLIST.md`) and when scoping builds in `Proposal_Template.html`.
> **Status:** Internal reference — NOT for clients.

---

## The Decision Framework

Every automation decision runs through **3 gates** in this order:

```
GATE 1: Budget          →  What can the client afford per month to RUN this?
GATE 2: Data Volume     →  How many operations per month?
GATE 3: Security/Compliance →  Any HIPAA, SOC2, data residency, or audit requirements?
```

Then the **final check**: Complexity (how many conditional branches? state machines? real-time needs?).

---

## Gate 1: Budget (Monthly Running Cost)

| Monthly Budget | Go-To Solution | Best For |
|---|---|---|
| **$0** (free tier only) | **n8n self-hosted** (local Docker or free-tier hosting) | Most builds. Handles 90% of automations. Note: free hosting tiers usually sleep after inactivity — use the $5/mo tier for always-on workflows. |
| **$0-30/mo** | **n8n self-hosted** (Railway Hobby $5/mo or equivalent) + OpenAI free-tier credits | AI-enhanced workflows on a tight budget |
| **$30-100/mo** | **n8n self-hosted** + OpenRouter API (pay-per-token) or **Make (Integromat) Starter** | When client wants managed hosting + more integrations |
| **$100-500/mo** | **Make Pro/Teams** ($16-29/mo) or **n8n Cloud** | Multi-user, higher limits, managed platform |
| **$500-2,000/mo** | **Custom Python** + Supabase + Vercel/Railway hosting | Fully bespoke, unlimited scale |
| **$2,000+/mo** | **Enterprise:** Custom infrastructure + dedicated monitoring | Compliance-heavy, SLA-backed |

**Default:** For 90% of AusAI clients, **n8n self-hosted on Railway ($0-5/mo)** is the right answer. Start there and upgrade only if Gate 2 or 3 forces it.

---

## Gate 2: Data Volume (Operations/Month)

Operations = webhook triggers + API calls + data transformations per month.

| Volume | Platform | Why |
|---|---|---|
| **< 5,000 ops/mo** | n8n self-hosted (free) | No limits on self-hosted n8n |
| **5,000 – 100,000 ops/mo** | n8n self-hosted (still free) | Scales fine on a $5/mo Railway instance |
| **100,000 – 1,000,000 ops/mo** | n8n Cloud Starter ($20/mo) OR self-hosted on $20/mo instance | Needs a bit more RAM, maybe a queue worker |
| **1M – 10M ops/mo** | **Custom Python** + queue (BullMQ / Celery) + Supabase | n8n's visual editor becomes a bottleneck at this scale |
| **10M+ ops/mo** | **Custom Python** + Kafka / Pulsar + dedicated infra | Enterprise scale. Rare for solo consultancy. |

**Default:** Most small-business automations run < 50,000 ops/mo. n8n self-hosted handles this trivially.

---

## Gate 3: Security & Compliance

| Requirement | Solution | Notes |
|---|---|---|
| **None** (standard AU small business) | Any platform | Default path |
| **Data must stay in Australia** | n8n self-hosted on AU region (Railway `ap-southeast-1` or Vercel) + Supabase AU region | Explicitly set hosting regions |
| **HIPAA / health data** | **Custom Python only.** n8n/Make/Zapier are NOT HIPAA compliant. Self-hosted n8n with BAA is legally grey. | Python + encrypted DB + audit logging |
| **SOC2 / enterprise audit** | Custom Python + AWS/GCP with compliance config | n8n's audit trail is weak for formal SOC2 |
| **Finance / PCI-DSS** | **Do not touch card data.** Integrate via Stripe/PayPal API only. Never store raw card numbers. | Liability: use established payment processors |
| **Government** | Depends on classification. Unclassified: n8n self-hosted. Protected: custom Python + gov-cloud (AWS/Azure Gov). | Check ISM controls before quoting |
| **GDPR (EU clients)** | n8n self-hosted in EU region OR n8n Cloud EU | Data residency; DPA may be needed |

**Default:** Most AusAI clients are standard AU small businesses with no special compliance needs. Don't over-engineer.

---

## Final Check: Complexity

| Signal | n8n / Make | Custom Python |
|---|---|---|
| **Linear workflows** (trigger → step → step → output) | ✅ | Overkill |
| **Conditional branching** (< 10 branches) | ✅ (visual nodes) | Overkill |
| **Simple API calls** (REST, webhook, polling) | ✅ | Overkill |
| **6+ conditional branches, nested logic** | ⚠️ Gets messy | ✅ Cleaner in code |
| **State machines** (multi-step with persistent state) | ❌ n8n's execution model is stateless | ✅ Persist state in DB |
| **Real-time / sub-second latency** | ❌ n8n adds 500ms-2s per node | ✅ Optimised for speed |
| **Streaming data** (WebSocket, Server-Sent Events) | ❌ n8n doesn't support SSE | ✅ Native in Python |
| **Custom ML model serving** | ❌ Limited to API calls | ✅ Run models directly |
| **Heavy data transformation** (> 10MB payloads) | ❌ n8n will choke | ✅ Pandas/NumPy |
| **Need version control (Git)** | ❌ n8n exports JSON; diffs are unreadable | ✅ Standard Git workflows |

---

## The Full Decision Matrix

```
START HERE
    │
    ├─ Is this a simple, linear automation with < 10 steps?
    │   ├─ YES → Budget under $100/mo? → n8n self-hosted ✅
    │   └─ Budget $100+/mo? → Make (Integromat) ✅
    │
    ├─ Does it need AI/LLM calls?
    │   ├─ Budget under $30/mo? → n8n + OpenRouter free models ✅
    │   ├─ Budget $30-200/mo? → n8n + OpenRouter paid models ✅
    │   └─ Budget $200+/mo OR needs custom fine-tuning? → Custom Python + OpenRouter API ✅
    │
    ├─ Any compliance requirements (HIPAA, SOC2, finance, government)?
    │   └─ Custom Python only ✅ (n8n/Make/Zapier are NOT compliant)
    │
    ├─ Is it a state machine, real-time, or streaming?
    │   └─ Custom Python ✅
    │
    ├─ Does it process > 1M operations/month?
    │   └─ Custom Python + queue + dedicated DB ✅
    │
    └─ None of the above? → n8n self-hosted ✅ (default)
```

---

## Tool-by-Tool Quick Reference

### n8n (self-hosted)

| Factor | Rating |
|---|---|
| **Cost** | Free (self-hosted on $0-5/mo Railway; Hobby $5/mo for always-on) |
| **Setup time** | 10 min (Railway template or Docker) |
| **Connectors** | 400+ nodes |
| **AI integration** | Native LangChain nodes, OpenRouter HTTP node |
| **Error handling** | Good — retry, error workflow, error output node |
| **Version control** | Poor — JSON export only |
| **Best for** | 90% of all builds. Bread-and-butter automations. |
| **Avoid for** | HIPAA, real-time, heavy state, streaming |

### Make (Integromat)

| Factor | Rating |
|---|---|
| **Cost** | Free (1,000 ops/mo) → $9/mo (10,000 ops) → $29/mo |
| **Setup time** | 5 min (cloud, no hosting) |
| **Connectors** | 1,500+ (more than n8n) |
| **AI integration** | OpenAI, Google AI modules |
| **Error handling** | Excellent — detailed execution logs, replay |
| **Version control** | Poor — no Git integration |
| **Best for** | Clients who want managed hosting, larger connector library |
| **Avoid for** | Budget-constrained, compliance-heavy |

### Zapier

| Factor | Rating |
|---|---|
| **Cost** | Free (100 tasks/mo) → $20/mo (750 tasks) → expensive at scale |
| **Setup time** | 3 min |
| **Connectors** | 6,000+ (most of any platform) |
| **AI integration** | Built-in ChatGPT, Claude actions |
| **Error handling** | Basic — "Zapier Error" emails, limited replay |
| **Version control** | None |
| **Best for** | Trivial single-step Zaps. "New Gmail → Slack." |
| **Avoid for** | Complex multi-step workflows, budget-constrained, security-sensitive |

### Custom Python

| Factor | Rating |
|---|---|
| **Cost** | $0 (code) + $5-50/mo hosting (Railway/Vercel) |
| **Setup time** | 2-8 hours per project (vs. 30 min in n8n) |
| **Connectors** | Unlimited (any Python library / API) |
| **AI integration** | Full control — any model, any provider, custom chains |
| **Error handling** | Full control — custom retry, dead-letter queues, Sentry |
| **Version control** | Git native — full history, branches, code review |
| **Best for** | Compliance, state machines, real-time, scale, complex logic |
| **Avoid for** | Simple linear workflows (waste of time) |

---

## Database / Storage Companion Decision

| If using... | Companion DB | Why |
|---|---|---|
| n8n self-hosted | **Supabase** (Postgres + pgvector) | Free tier, API-first, embeddings for AI |
| Make / Zapier | **Airtable** or **Google Sheets** | No-code friendly, client can edit |
| Custom Python | **Supabase** or **SQLite** (single-user) | Supabase for web apps, SQLite for scripts |
| Compliance-heavy | **Supabase dedicated** or **AWS RDS** | Encrypted, auditable, regional |

---

## AI Provider Decision

| Use Case | Provider | Model | Cost |
|---|---|---|---|
| **Chatbots** (customer support) | **OpenRouter** → Claude 3.5 Haiku | Fast, cheap, safe | ~$0.25/1M tokens |
| **Classification** (email routing, sentiment) | **OpenRouter** → GPT-4o-mini | Fastest, cheapest | ~$0.15/1M tokens |
| **Code generation** (automation scripts) | **OpenRouter** → Claude 3.5 Sonnet | Best coding model | ~$3/1M tokens |
| **Document analysis** (PDFs, contracts) | **OpenRouter** → Claude 3.5 Sonnet | Vision + long context | ~$3/1M tokens |
| **Creative / brainstorming** | **OpenRouter** → GPT-4o | Strong reasoning | ~$2.50/1M tokens |
| **Free tier builds** | **OpenRouter** → free models | Budget-constrained | $0 |

**Default:** Route everything through **OpenRouter**. One API key, all models, pay-per-token. No vendor lock-in.

---

## Hosting Decision

| Scenario | Platform | Cost |
|---|---|---|
| **n8n self-hosted** | **Railway** (template deploy) | $0-5/mo |
| **Custom Python API** | **Railway** or **Vercel** | $0-20/mo |
| **Static site** (landing, checkout) | **GitHub Pages** | Free |
| **Database** | **Supabase** | Free tier (500MB) → $25/mo |
| **Client wants managed everything** | **n8n Cloud** + **Airtable** | $20 + $20 = $40/mo |
| **Australian data residency** | Railway `ap-southeast-1` + Supabase AU | Same pricing |

---

## Quick Decision Cheat Sheet (Print This)

```
CLIENT SAYS:                           YOU CHOOSE:
───────────                            ──────────
"I have no budget"               →    n8n self-hosted + OpenRouter free models
"I need it fast"                 →    n8n self-hosted (5-day build)
"I need HIPAA compliance"        →    Custom Python (only option)
"We have 50,000 emails/day"      →    Custom Python + queue
"Just connect Gmail to Slack"   →    Zapier (don't over-engineer)
"I want to edit it myself"       →    n8n (visual editor) or Make
"I need a dashboard too"         →    n8n + Supabase + custom HTML dashboard
"We're an enterprise"            →    Custom Python + AWS + compliance
"I need AI in the workflow"      →    n8n + OpenRouter HTTP node
"My CTO will maintain it"        →    Custom Python (Git, CI/CD, familiar)
"I don't have a CTO"             →    n8n self-hosted (visual, documented)
```

---

## When to Break This Tree

This tree covers 95% of decisions. Break it when:

1. **Client has an existing vendor relationship** (e.g., "We already use Make Teams, build there") — build in their stack
2. **Novel use case** not covered by the matrix (e.g., hardware/IoT automation, on-premise air-gapped systems) — research fresh
3. **Client insists on a specific tool** you disagree with — advise once, then either build there or walk

---

## Related Documents

- `AI_AUTOMATION_AUDIT_CHECKLIST.md` — Segment 4 uses this tree for classifying automations
- `Discovery_Call_Script.md` — Phase 3 "here's how we fix it" references tool choices
- `Proposal_Template.html` — §2 Scope specifies the chosen tools
- `First_Client_Onboarding.md` — §Agenda references "which tools" in the architecture sketch
- `COMPETITOR_BATTLE_CARDS.md` — Battle Card 4 handles "why not just use Zapier directly"

---

*When in doubt: n8n self-hosted. Upgrade only when forced by compliance, scale, or complexity. Simple is fast. Fast is profitable.*
