# 💰 PASSIVE INCOME PLAN — AusAI Tech

**Purpose:** Build revenue streams that don't require your hourly presence.  
**Goal:** A$2,000–A$5,000/mo passive by Month 6, layered on top of consulting.  
**Strategy:** Productize what you already build for clients.

> **Why now?** Consulting caps at ~A$15k/mo solo. Adding passive products pushes you past the time-for-money ceiling without hiring. Start building assets from Day 1.

---

## 📋 TABLE OF CONTENTS

1. [The 4 Passive Income Lanes](#1-the-4-passive-income-lanes)
2. [Lane 1: n8n Workflow Template Pack](#2-lane-1-n8n-workflow-template-pack)
3. [Lane 2: AI Automation Audit-as-a-Product](#3-lane-2-ai-automation-audit-as-a-product)
4. [Lane 3: ComfyUI Media Workflow Packs](#4-lane-3-comfyui-media-workflow-packs)
5. [Lane 4: Digital Asset Store (Gumroad/Payhip)](#5-lane-4-digital-asset-store-gumroadpayhip)
6. [Revenue Timeline](#6-revenue-timeline)
7. [Marketing Without Time Cost](#7-marketing-without-time-cost)
8. [Tax & Legal](#8-tax--legal)

---

## 1. THE 4 PASSIVE INCOME LANES

| Lane | Product | Price | Effort to Build | Passive Revenue/Mo |
|---|---|---|---|---|
| 1 | n8n Workflow Template Pack | A$47–A$97 | 8-12 hrs | A$500–A$2,000 |
| 2 | AI Automation Audit-as-Product | A$97–A$197 | 20-30 hrs | A$1,000–A$3,000 |
| 3 | ComfyUI Media Workflow Packs | A$27–A$67 | 4-6 hrs | A$200–A$800 |
| 4 | Digital Asset Store | A$7–A$47 each | 2-4 hrs/item | A$300–A$1,000 |

**Stack them.** Don't pick one — build Lane 1 first (fastest to ship), then Lane 2 (highest margin), then 3-4 as you accumulate assets.

---

## 2. LANE 1: n8n WORKFLOW TEMPLATE PACK

### Product

**"10 Plug-and-Play n8n Workflows for Small Business"**

Price: **A$67** (one-time)  
Format: JSON files + setup video + PDF documentation  
Platform: Gumroad (gumroad.com — free to list, 10% fee)

### The 10 Workflows

| # | Workflow | Business Function |
|---|---|---|
| 1 | Lead Capture → CRM → Slack Alert → Email Sequence | Sales |
| 2 | Invoice Created → Payment Tracking → Overdue Alert | Finance |
| 3 | Form Submission → Google Sheets → Weekly Summary Email | Operations |
| 4 | Calendar Booking → Client Onboarding Email + Task Created | Admin |
| 5 | E-commerce Order → Inventory Update → Low-Stock Alert | Inventory |
| 6 | Social Media Post → Cross-Platform Repost + Analytics | Marketing |
| 7 | Customer Support Ticket → Auto-Reply → Escalation If Unresolved | Support |
| 8 | New Client → Contract Generated → Welcome Email → Project Created | Onboarding |
| 9 | Website Uptime Monitor → Alert If Down → Incident Log | IT |
| 10 | Monthly Report: Pull Data from 3 Sources → PDF → Email | Reporting |

### What's Included per Workflow

```
📁 Workflow_Name/
  ├── workflow.json              (n8n import-ready)
  ├── setup_guide.md             (step-by-step with screenshots)
  ├── credentials_required.txt   (API keys needed)
  ├── custom_nodes.txt           (if any — keep minimal)
  └── demo_video.mp4             (2-3 min silent walkthrough)
```

### Shipping Checklist

- [ ] Build all 10 workflows in your n8n instance
- [ ] Test each with real data (use test accounts)
- [ ] Record 2-3 min silent walkthrough per workflow (OBS or Loom free)
- [ ] Write setup guide with screenshots (use Greenshot or Snipping Tool)
- [ ] Create Gumroad product page (title, description, 3 preview images, trailer video)
- [ ] Set price at A$67
- [ ] Write 3 "free sample" workflows as lead magnets (email-gated)

### Marketing

- **Reddit:** Post free sample workflows in r/n8n, r/automation, r/zapier
- **n8n Forum:** Share workflows, link to full pack in signature
- **YouTube:** 3-min "How to automate X with n8n" videos → link in description
- **SEO:** "n8n workflow templates" + "free n8n workflows" keywords

### Revenue Math

- **Conservative:** 20 sales/mo × A$67 = A$1,340/mo
- **Optimistic:** 50 sales/mo × A$67 = A$3,350/mo
- **After Gumroad fee (10%):** A$1,206–A$3,015/mo

---

## 3. LANE 2: AI AUTOMATION AUDIT-AS-A-PRODUCT

### Product

**"AI Automation Opportunity Scanner"** — An automated tool that scans a business and generates an audit report.

Price: **A$147** (one-time per business scan)  
Format: Web app (simple HTML/JS) or Gumroad-delivered system  
Platform: Your own landing page + Stripe

### How It Works (Automated — You're Not on the Call)

1. **Client fills form** → Industry, team size, tools used, pain points
2. **AI analysis engine** → Runs their inputs through a GPT-4 prompt chain:
   - Step 1: Identify tool stack gaps
   - Step 2: Map manual processes to automation candidates
   - Step 3: Calculate time/cost savings per opportunity
   - Step 4: Generate prioritized recommendation list
3. **PDF report generated** → Emailed to client within 5 minutes
4. **Upsell CTA** → "Want me to build these? Book a call" (optional human follow-up)

### Tech Stack

- **Frontend:** Simple HTML form (hosted on GitHub Pages)
- **Processing:** n8n webhook → OpenAI API → PDF generation → Email
- **PDF Generation:** WeasyPrint (Python) or Google Docs template → PDF
- **Payment:** Stripe Payment Link (A$147)

### What the Report Includes

```
📄 AI Automation Opportunity Report for {Business Name}

1. Tool Stack Audit
   - Current tools assessed
   - Integration gaps identified
   - Security red flags flagged

2. Top 5 Automation Opportunities (ranked by ROI)
   #1: {Process} — Save {X} hrs/week — Cost ~A${Y} to build
   #2: ...
   
3. Recommended Tech Stack
   - Tools to add/remove
   - Estimated monthly tool cost

4. Implementation Roadmap
   - Phase 1 (Week 1-2): Quick wins
   - Phase 2 (Week 3-4): Core automations
   - Phase 3 (Month 2): Advanced AI integration

5. DIY Resources (optional — builds trust, some will still hire you)
   - Links to relevant Zapier/Make templates
   - YouTube tutorials for simple automations
```

### Revenue Math

- **Conservative:** 10 scans/mo × A$147 = A$1,470/mo
- **Optimistic:** 25 scans/mo × A$147 = A$3,675/mo
- **Costs:** OpenAI API ~A$0.50/scan + hosting A$0 = near-zero marginal cost
- **Net margin:** ~96% (Stripe ~3% + OpenAI API ~A$0.50/scan)

---

## 4. LANE 3: COMFYUI MEDIA WORKFLOW PACKS

### Product

**"AI Music Video Studio — 5 ComfyUI Workflows"**

Price: A$47 (one-time)  
Format: ComfyUI workflow JSON files + prompt libraries + tutorial video  
Platform: Gumroad

### The 5 Workflows

| # | Workflow | Use Case |
|---|---|---|
| 1 | Style Transfer Music Video | Apply art style to video synced to BPM |
| 2 | AI Lip-Sync Performance | Animate a character singing to audio |
| 3 | Abstract Visualizer | Generate reactive visuals from audio spectrum |
| 4 | Batch Image-to-Video | Convert image sequence to video with transitions |
| 5 | Text-to-Video Story | Generate video segments from lyrics/story prompts |

### What's Included per Workflow

```
📁 ComfyUI_Workflow_Name/
  ├── workflow.json                (drag-and-drop import)
  ├── model_requirements.txt       (which models to download)
  ├── prompt_library.txt           (10+ tested prompts)
  ├── settings_guide.md            (VRAM budget, recommended settings for RTX 4060 8GB)
  └── output_preview.mp4           (30-sec sample output)
```

> **Existing assets:** Your `C:\Users\karma\ComfyUI\workflow_templates\workflow_recipes.md` already documents workflows. Repackage them.

### Revenue Math

- **Conservative:** 10 sales/mo × A$47 = A$470/mo
- **Optimistic:** 25 sales/mo × A$47 = A$1,175/mo
- **Niche advantage:** Few competitors in ComfyUI template space (2026)

---

## 5. LANE 4: DIGITAL ASSET STORE (GUMROAD/PAYHIP)

### Products (Low-Effort, Quick-to-Ship)

| Product | Price | Build Time | Monthly Potential |
|---|---|---|---|
| **Email Template Pack** (20 AI agency email templates) | A$17 | 2 hrs | A$100–A$300 |
| **Cold DM Script Pack** (LinkedIn + Reddit + Email outreach) | A$12 | 1 hr | A$50–A$150 |
| **Automation ROI Calculator Spreadsheet** (Google Sheets) | A$7 | 1 hr | A$30–A$100 |
| **Client Onboarding Checklist PDF** (editable) | A$9 | 1 hr | A$40–A$100 |
| **AI Tool Comparison Cheat Sheet** (1-page PDF) | A$5 | 30 min | A$20–A$50 |
| **Scope of Work Template Pack** (5 templates) | A$22 | 2 hrs | A$100–A$200 |
| **Proposal Template Pack** (3 proposal formats) | A$27 | 2 hrs | A$100–A$250 |

**Total from Lane 4:** A$440–A$1,150/mo (with all 7 products live)

### Bundle Strategy

Create a "Complete AI Agency Toolkit" bundle: All 7 products for A$67 (vs A$99 individually). Higher perceived value, higher conversion.

---

## 6. REVENUE TIMELINE

| Month | Lanes Live | Conservative | Optimistic |
|---|---|---|---|
| **Month 1** | Lane 1 (n8n pack) shipping | A$200 | A$500 |
| **Month 2** | Lane 1-2 + 2-3 digital assets | A$500 | A$1,500 |
| **Month 3** | Lane 1-3 + 5 digital assets | A$1,000 | A$3,000 |
| **Month 4** | All 4 lanes + bundle | A$1,500 | A$4,000 |
| **Month 6** | All lanes + SEO traction | A$2,000 | A$5,000+ |

**Stack with consulting:** A$5k consulting + A$2k passive = A$7k/mo without hiring.

---

## 7. MARKETING WITHOUT TIME COST

### Set-and-Forget Channels

| Channel | Effort | Setup Time | Ongoing Time |
|---|---|---|---|
| **Gumroad discovery** (people search Gumroad) | Zero — built-in | 30 min to list | 0 hrs/week |
| **SEO on Gumroad product pages** | Write once | 1 hr/page | 0 hrs/week |
| **Reddit signature links** | Add once to profile | 2 min | 0 hrs/week |
| **GitHub README links** | Add to your repos | 5 min | 0 hrs/week |
| **Email signature** | Add once | 2 min | 0 hrs/week |
| **YouTube video descriptions** | Add to existing videos | 10 min | 0 hrs/week |
| **n8n/Make community forum signatures** | Add once | 5 min | 0 hrs/week |
| **Twitter/X bio link** | Add once | 1 min | 0 hrs/week |

> **Rule:** No marketing activity should require daily attention. Set once, earn forever.

### The "Free Sample" Funnel

```
Free workflow/sample (email-gated)
        ↓
   Email sequence (3 emails: value → use case → buy CTA)
        ↓
   Paid product (A$47–A$147)
        ↓
   Upsell: "Want me to build custom? Book a call" (A$1,000+)
```

---

## 8. TAX & LEGAL

### Australian Sole Trader Notes

- **Income:** Gumroad/Stripe income is business income — declare on your tax return.
- **GST:** Register for GST when turnover exceeds A$75,000. Gumroad/Payhip sales count.
- **Digital products:** No physical goods = no shipping complications. VAT/GST handled by Gumroad (marketplace facilitator rules).
- **Expenses you can deduct:**
  - Gumroad fees (10%)
  - Stripe processing fees
  - OpenAI API costs
  - Domain + hosting
  - Software subscriptions used to build products
- **ABN:** Use your existing sole trader ABN.

### Gumroad-Specific

- Gumroad collects and remits VAT/GST for you (marketplace facilitator)
- 10% fee on each sale
- Payouts: Weekly (or instant for 3% extra)
- Tax form: Gumroad asks for W-8BEN (non-US person) — fill it once

### Licensing

Include a simple license in each product:

```
LICENSE.txt:
This product is licensed to the individual purchaser only.
Do not redistribute, resell, or share the files.
You may use the workflows/templates for unlimited client projects.
```

---

## 🔗 CROSS-REFERENCES

- `AUTOMATION_TEMPLATE_PACK.md` — Reusable n8n blueprints to package
- `TECH_STACK_DECISION_TREE.md` — Framework to include in audit reports
- `AI_AUTOMATION_AUDIT_CHECKLIST.md` — Basis for the automated audit
- `TAX_TIME_CHECKLIST.md` — Track passive income for EOFY
- `MASTER_MONEY_PLAN.md` — Primary revenue targets
- `UPWORK_LAUNCH_GUIDE.md` — Active income channel while passive builds
- `C:\Users\karma\ComfyUI\workflow_templates\workflow_recipes.md` — Source for Lane 3

---

> **Last updated:** 2026-06-28 — Round 12  
> **Action:** Start Lane 1 TODAY. Build 1 workflow/day for 10 days. Ship by Day 14.
