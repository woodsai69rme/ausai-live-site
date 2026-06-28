# Australian Compliance Checklist — AusAI Tech

> **Status:** ⏳ Not started — complete BEFORE sending your first invoice.
> **Time:** 2-3 hours total (mostly waiting for ABN confirmation).
> **Cost:** $0 (ABN is free). Optional: $200-400 for accountant consultation.

---

## ⚠️ Why This Matters (Do Not Skip)

| If you don't... | What happens |
|---|---|
| Register an ABN before invoicing | Client must withhold **47%** of your payment for tax |
| Charge GST once over $75k turnover | ATO fines + back-dated GST liability |
| Put correct info on invoices | Invoice may be invalid; client can refuse payment |
| Set aside tax money | Surprise $5k-15k tax bill at EOFY |
| Track business vs personal expenses | Accounting nightmare; missed deductions |

**This checklist gets you legally operational in one session.**

---

## ✅ Phase 1: ABN Registration (Free, 15 min online)

**Before you do anything else.** You cannot legally invoice Australian businesses without an ABN.

- [ ] Go to **abr.gov.au** → "Apply for an ABN"
- [ ] Have your **TFN (Tax File Number)** ready — it's required for the application
- [ ] Select **Sole Trader** (recommended at your revenue level — see §Business Structure below)
- [ ] Complete the online form (15 min):
  - Business name: `AusAI Tech` (or your chosen name)
  - Activity: `AI Automation & Security Consulting`
  - Start date: today's date
- [ ] Receive ABN immediately (usually instant, sometimes up to 20 min)
- [ ] **Record your ABN:** `_______________` (11 digits)
- [ ] Save the ABN registration confirmation PDF
- [ ] **Mark ABN as registered in your Ops Dashboard:** Open `AUSAI_OPS_DASHBOARD.html` in your browser, and the alert banner at the top will turn green automatically once you run `localStorage.setItem('ausai_abn_registered', 'true')` in the browser console (F12 → Console → paste → Enter). This is optional but satisfying.

> **GST note:** On the ABN form, you will be asked if you want to register for GST.
> - If projected turnover < $75k/year → **select "No"** for now
> - You can register later once you approach the threshold
> - If you register voluntarily, you MUST charge 10% GST on every invoice from that point

---

## ✅ Phase 2: Business Structure Decision

| Factor | Sole Trader (recommended) | Company (Pty Ltd) |
|---|---|---|
| **Setup cost** | Free | ~$500-800 (ASIC fee + setup) |
| **Annual cost** | $0 | ~$250-400 (ASIC + accounting) |
| **Complexity** | Simple — income in personal tax return | Complex — separate tax return, director duties |
| **Liability** | Unlimited (personal assets at risk) | Limited (with exceptions) |
| **Tax rate** | Personal marginal rates (0-45%) | Flat 25% |
| **Break-even** | Always better below ~$120k/year | Better above ~$150k/year + asset protection needs |

**Verdict for AusAI Tech:** Start as **Sole Trader**. Revisit company structure once you consistently exceed $10k/month and want asset protection.

- [ ] Decision made: Sole Trader ✅
- [ ] Decision revisited: Set calendar reminder for **2026-12-31** to reassess

---

## ✅ Phase 3: Business Bank Account (Strongly Recommended)

Not legally required for sole traders, but essential for clean bookkeeping.

- [ ] Open a **separate business transaction account**
- [ ] Recommended options (no monthly fee):
  - **ING Business Optimiser** — no fees, good interest
  - **Up Bank** — no fees, good app
  - **NAB Business Everyday** — $0 fee if deposit conditions met
  - **CommBank Business Transaction** — widely accepted
- [ ] Use this account for ALL business income and expenses
- [ ] Never mix personal and business transactions

> **Why:** At tax time, your accountant (or you) needs to identify every business transaction. A separate account makes this trivial. Mixed accounts = hours of reconciliation.

---

## ✅ Phase 4: Invoicing Requirements (Legal Checklist)

Every invoice you send must include these items to be valid:

### All invoices (GST-registered or not):
- [ ] The words **"Tax Invoice"** (if GST-registered) or **"Invoice"**
- [ ] Your **business name** (AusAI Tech)
- [ ] Your **ABN** (11 digits)
- [ ] **Date of issue**
- [ ] **Description of services** (clear, specific)
- [ ] **Price** (per item and total)
- [ ] **Sequential invoice number** (INV-001, INV-002, etc.)

### Additional requirement for invoices over $1,000:
- [ ] **Buyer's identity** (name) or **buyer's ABN**

### If GST-registered (only once you hit $75k/year):
- [ ] GST amount shown separately (10% of subtotal)
- [ ] Statement: "Price includes GST" OR show GST as a separate line

**Your `Invoice_Template.html` already includes all mandatory fields.** Just replace the placeholders.

---

## ✅ Phase 5: GST Threshold Monitoring

| Scenario | Action |
|---|---|
| Current turnover < $75k/year | No GST registration needed; do not charge GST |
| Projected to hit $75k in next 12 months | Register for GST within 21 days of realising |
| Already registered | Charge 10% GST on every invoice; lodge BAS quarterly |

- [ ] Current annual turnover estimate: `$________`
- [ ] GST registration status: ☐ Not registered | ☐ Registered voluntarily | ☐ Mandatory
- [ ] If/when registered: Set quarterly BAS reminder (Feb, May, Aug, Nov)

> **BAS (Business Activity Statement):** If GST-registered, you lodge a BAS every quarter reporting GST collected and GST paid on business purchases. You can do this yourself via myGov/ATO portal or pay an accountant ~$200/quarter.

---

## ✅ Phase 6: Tax Planning (Critical)

As a sole trader, there is no "company" paying tax for you. **You must plan for it yourself.**

### Income Tax Set-Aside Rule

| Annual Income | Marginal Tax Rate | Recommended Set-Aside |
|---|---|---|
| $0 – $18,200 | 0% | 0% |
| $18,201 – $45,000 | 16% | 15-20% of revenue |
| $45,001 – $135,000 | 30% | 25-30% of revenue |
| $135,001 – $190,000 | 37% | 32-37% of revenue |
| $190,001+ | 45% | 40-45% of revenue |

- [ ] Set aside **25-30% of every payment** into a separate "tax" savings account
- [ ] Do not touch this money until tax time
- [ ] If you hit PAYG instalments (ATO will notify you), pay quarterly instead

### Deductible Expenses (Track These)

Keep receipts for everything business-related:
- [ ] Computer / laptop (used for work)
- [ ] Software subscriptions (ComfyUI nodes, hosting, domain, Stripe fees)
- [ ] Internet (portion used for business)
- [ ] Home office (portion of rent/utilities if WFH)
- [ ] Training / courses
- [ ] Travel to client meetings
- [ ] Accountant fees
- [ ] Bank fees

> **Tip:** Use a simple spreadsheet or the ATO myDeductions app to snap photos of receipts. At EOFY, this saves hours.

---

## ✅ Phase 7: Superannuation

As a sole trader, **nobody pays super for you.** You must do it yourself.

- [ ] Set up a self-managed super contribution schedule
- [ ] Minimum recommended: **10% of net profit** into super
- [ ] These contributions are tax-deductible (claim them on your tax return)
- [ ] Popular funds: AustralianSuper, Hostplus, Sunsuper

> **Note:** This is for long-term planning. If cash flow is tight in months 1-3, you can defer. But build the habit early.

---

## ✅ Phase 8: Insurance (Recommended)

| Type | Cost | Why |
|---|---|---|
| **Professional Indemnity** | $500-1,500/year | Covers you if a client claims your advice/work caused them loss |
| **Public Liability** | $300-600/year | Covers injury/damage to third parties |
| **Cyber Liability** | $400-800/year | Covers data breaches, hacking incidents (relevant for security audits) |

- [ ] Decision: ☐ Get PI insurance before first client | ☐ Defer until revenue stable
- [ ] If deferring: Set calendar reminder for **2026-09-30** to reassess

> **Why PI matters for you:** You sell "security audits." If a client gets hacked AFTER your audit (even if you found different vulnerabilities), they might blame you. PI insurance covers legal defense and settlements.

---

## ✅ Phase 9: Record Keeping

The ATO requires you to keep business records for **5 years**.

- [ ] All invoices issued (PDF copies)
- [ ] All receipts for expenses
- [ ] Bank statements (business account)
- [ ] Contracts / proposals accepted
- [ ] GST records (if registered)

**Digital is fine.** Scanned PDFs or photos are acceptable. No need for paper files.

---

## Quick-Reference: Before First Invoice Checklist

- [ ] ABN registered and recorded
- [ ] Business bank account opened
- [ ] Invoice template updated with real ABN, business name, bank details
- [ ] Invoice number sequence started (INV-001)
- [ ] Tax set-aside account opened (or labelled savings bucket)
- [ ] 25-30% of first payment mentally allocated to tax
- [ ] Professional Indemnity insurance decision made
- [ ] Receipt-tracking system ready (spreadsheet or app)

**Time to complete:** 2-3 hours of active work + waiting for ABN/email confirmations.

---

## When to See an Accountant

| Trigger | Why |
|---|---|
| Revenue exceeds $5k/month consistently | Tax planning becomes worth the $300-500 fee |
| Considering company structure | Accountant + lawyer consultation (~$800) |
| GST registration required | BAS lodgement; accountant ~$200/quarter saves headaches |
| First EOFY approaching | Accountant ensures you claim all deductions correctly |

> **Cost:** Solo trader tax return = $200-400. Worth every dollar for peace of mind.

---

*Disclaimer: This checklist is for guidance only. Australian tax laws change. For advice specific to your situation, consult a registered tax agent or visit ato.gov.au.*
