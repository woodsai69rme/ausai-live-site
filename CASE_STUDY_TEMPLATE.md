# Case Study Template — AusAI Tech

> **Purpose:** Turn every delivered project into a compelling portfolio piece that attracts the next client. Complete this template within 48 hours of project handoff while details are fresh.
> **Output:** A 1-page case study suitable for the portfolio gallery, LinkedIn post, and proposal attachment.

---

## Metadata

| Field | Value |
|---|---|
| **Client** | `{{CLIENT_NAME}}` (anonymised if NDA prevents naming — e.g., "Australian E-commerce Retailer") |
| **Industry** | `{{INDUSTRY}}` (e.g., E-commerce, SaaS, Healthcare, Professional Services) |
| **Service Tier** | `{{TIER}}` (Basic / Standard / Premium) |
| **Project Dates** | `{{START_DATE}}` → `{{END_DATE}}` |
| **AusAI Operator** | Karma — AusAI Tech |
| **Case Study ID** | `{{CS-YYYY-NNN}}` (e.g., CS-2026-001) |
| **Client Approved for Public Use?** | ☐ Yes ☐ Anonymised only ☐ Internal use only |

---

## 1. The Problem (Before)

> **Rule:** Lead with the client's pain, not your solution. The reader should nod and think "that sounds like us."

**In 1-2 sentences, what was broken?**
```
{{CLIENT_NAME}} was spending X hours per week on [manual process].
This caused [specific pain: missed leads, slow response times, data errors, compliance risk, etc.].
```

**Quantify the pain (get this from the client during discovery):**
- Time lost per week: `{{HOURS}}` hours
- Cost of inaction (estimate): A$`{{ANNUAL_COST}}`/year
- Risk or opportunity cost: `{{RISK_DESCRIPTION}}`

**Why previous solutions failed (if any):**
```
They had tried {{PREVIOUS_ATTEMPT}} but it {{WHY_IT_FAILED}}.
```

---

## 2. The Solution (What AusAI Built)

> **Rule:** Describe the solution in business terms first, then technical terms. Most readers are not technical.

### 2.1 Business Summary
```
We built a {{SYSTEM_TYPE}} that {{WHAT_IT_DOES}}.
This replaced their {{OLD_PROCESS}} with {{NEW_PROCESS}},
saving them {{HOURS_SAVED}} hours per week.
```

### 2.2 Technical Stack

| Layer | Technology |
|---|---|
| **AI Model** | `{{MODEL}}` (e.g., GPT-4 via OpenRouter, Claude 3.5 Sonnet) |
| **Orchestration** | `{{PLATFORM}}` (e.g., n8n, custom FastAPI, Make/Zapier) |
| **Data Store** | `{{DATABASE}}` (e.g., Supabase PostgreSQL, Airtable, Notion) |
| **Frontend** | `{{UI}}` (e.g., Next.js, Streamlit, none — API-only) |
| **Hosting** | `{{HOST}}` (e.g., GitHub Pages, Vercel, self-hosted) |
| **Integrations** | `{{INTEGRATIONS}}` (e.g., Slack, Stripe, Calendly, email) |

### 2.3 Key Features Delivered

- [ ] `{{FEATURE_1}}`
- [ ] `{{FEATURE_2}}`
- [ ] `{{FEATURE_3}}`

---

## 3. The Results (After)

> **Rule:** Numbers beat adjectives. Every claim needs a number or a time period.

### 3.1 Quantified Outcomes

| Metric | Before | After | Improvement |
|---|---|---|---|
| Time spent on task | `{{BEFORE_TIME}}` | `{{AFTER_TIME}}` | `{{TIME_SAVED}}` |
| Response time | `{{BEFORE_RESPONSE}}` | `{{AFTER_RESPONSE}}` | `{{RESPONSE_IMPROVEMENT}}` |
| Error rate | `{{BEFORE_ERROR}}` | `{{AFTER_ERROR}}` | `{{ERROR_IMPROVEMENT}}` |
| Cost per action | `{{BEFORE_COST}}` | `{{AFTER_COST}}` | `{{COST_IMPROVEMENT}}` |
| Revenue/profit impact | — | — | A$`{{REVENUE_IMPACT}}` (if known) |

### 3.2 Qualitative Outcomes

> **Client quote (get permission):**
> ```
> "{{CLIENT_QUOTE}}"
> ```
> — `{{CLIENT_NAME}}`, `{{CLIENT_TITLE}}`

> **Your observation:**
> ```
> {{OPERATOR_OBSERVATION}}
> ```

---

## 4. The Process (How We Worked)

> **Rule:** Show your working method. Prospects buy process confidence, not just outcomes.

### 4.1 Timeline

| Week | Milestone |
|---|---|
| Week 1 | Discovery call + intake questionnaire + SOW signed |
| Week 2 | Architecture design + client approval |
| Week 3 | Build + internal testing |
| Week 4 | Client UAT + revisions + final delivery |

*(Adjust to actual project length.)*

### 4.2 Communication Rhythm

- **Kickoff:** 30-min video call (`First_Client_Onboarding.md`)
- **Mid-project:** 2 progress updates via email (`EMAIL_TEMPLATES.md`)
- **Delivery:** Handoff call + recorded walkthrough
- **Post-delivery:** 30-day check-in (`CLIENT_OFFBOARDING.md`)

---

## 5. Portfolio Conversion Checklist

After completing this template, do the following within 24 hours:

- [ ] **Anonymise if needed** — replace real names with "Australian [Industry] Company"
- [ ] **Export a visual** — screenshot the system dashboard or output (with client permission)
- [ ] **Write the short version** — 3-sentence summary for the portfolio gallery
- [ ] **Write the LinkedIn post** — 150-200 words with before/after hook (`SOCIAL_MEDIA_LAUNCH_POSTS.md`)
- [ ] **Add to `LEAD_TRACKER.html`** — mark client stage as "Closed Won — Delivered"
- [ ] **Request testimonial** — use the testimonial request email from `EMAIL_TEMPLATES.md`
- [ ] **Update revenue dashboard** — log final payment in `Revenue_Dashboard_Static.html`

---

## 6. Example (Filled Sample)

> **Client:** Australian E-commerce Retailer (anonymised)
> **Industry:** E-commerce
> **Tier:** Standard (A$1,200)

### The Problem
The retailer was manually processing 200+ customer enquiries per week via email and Instagram DMs. Response time averaged 6 hours. They missed 15-20% of after-hours enquiries entirely. Annual cost of lost sales estimated at A$18,000.

### The Solution
We built an AI-powered customer support agent integrated with their Shopify store and Instagram Business account. The agent answers FAQs, checks order status, and escalates complex issues to a human — 24/7.

**Stack:** GPT-4 via OpenRouter → n8n workflow → Supabase (order lookup) → Instagram Graph API

### The Results

| Metric | Before | After |
|---|---|---|
| Response time | 6 hours | 45 seconds |
| After-hours coverage | 0% | 100% |
| Enquiries handled without human | 30% | 78% |
| Weekly hours saved | — | 12 hours |

> *"We went from drowning in DMs to actually having weekends back. The AI handles 80% of our routine questions instantly."*
> — Operations Manager

### Portfolio Short Version
"AI customer support agent for an Australian e-commerce retailer. Cut response time from 6 hours to 45 seconds and recovered 12 staff hours per week. Built with GPT-4, n8n, and Supabase."

---

**File this completed case study in:** `C:/Users/karma/case_studies/CS-YYYY-NNN.md`

*For the portfolio gallery page, use the short version + one screenshot. For LinkedIn, use the full narrative with the quote. For proposals, attach the full case study as proof of capability.*
