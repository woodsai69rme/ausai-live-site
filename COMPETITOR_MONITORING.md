# 📡 COMPETITOR MONITORING — AusAI Tech

**Purpose:** Track competitor pricing, positioning, and changes monthly so you're never caught off guard.  
**Time:** 15 min/month.  
**Output:** A running spreadsheet of who's charging what and how they're positioning.

> **Why this matters:** When a prospect says "X charges half that," you need facts, not guesses. When a competitor enters your niche, you need to know before they take your leads.

---

## 📋 TABLE OF CONTENTS

1. [Competitor Categories](#1-competitor-categories)
2. [What to Track](#2-what-to-track)
3. [Tracking Spreadsheet Template](#3-tracking-spreadsheet-template)
4. [Monthly Monitoring Routine](#4-monthly-monitoring-routine)
5. [Automated Monitoring (n8n Recipe)](#5-automated-monitoring-n8n-recipe)
6. [Competitive Intelligence Uses](#6-competitive-intelligence-uses)

---

## 1. COMPETITOR CATEGORIES

### Category A: Direct Competitors (same offer, same market)

| Type | Examples | Threat Level |
|---|---|---|
| Solo AI automation consultants (AU) | Other freelancers on Upwork/Fiverr targeting AU businesses | High |
| Small automation agencies (AU) | 2-5 person shops offering "AI automation for SMBs" | Medium-High |
| Generalist IT consultants who "also do automation" | Local IT support companies adding Zapier to their services | Medium |

### Category B: Platform Competitors (sell tools, not services)

| Type | Examples | Threat Level |
|---|---|---|
| No-code platforms pitching "no developer needed" | Zapier, Make, n8n marketing pages | Medium |
| AI tool vendors pitching "AI in 5 minutes" | ChatGPT, Claude, Copilot marketing | Low-Medium |

### Category C: Alternative Competitors (solve the same problem differently)

| Type | Examples | Threat Level |
|---|---|---|
| Virtual assistants / offshore ops teams | Philippines-based VAs doing manual data entry for A$8/hr | Medium |
| Enterprise RPA (Robotic Process Automation) | UiPath, Automation Anywhere (for larger companies) | Low |

---

## 2. WHAT TO TRACK

### Per Competitor

| Data Point | Why It Matters | How to Find It |
|---|---|---|
| **Service pricing** (audit, build, retainer) | Know if you're under/over-priced | Their website, Upwork profile, Fiverr gig |
| **Positioning/messaging** | How they frame value. What pain points they target. | Homepage headline, LinkedIn bio, ad copy |
| **Tech stack** | Tools they use. Differentiators. | Portfolio, case studies, LinkedIn posts |
| **Content frequency** | Are they active on LinkedIn/YouTube/Reddit? | Manual check |
| **Client logos/testimonials** | Who's hiring them? What industries? | Website, LinkedIn, Clutch/Google reviews |
| **New services/products** | Are they expanding? Into your niche? | Website updates, Product Hunt launches |
| **Pricing changes** | Price increases or decreases | Re-check monthly |

---

## 3. TRACKING SPREADSHEET TEMPLATE

### Google Sheets Structure

```
Sheet: Competitor Tracking
Columns:
A: Competitor Name
B: Category (A/B/C)
C: Website URL
D: Audit Price
E: Build Price (typical)
F: Retainer Price
G: Positioning (1-sentence)
H: Tech Stack
I: LinkedIn URL
J: Content cadence (posts/week)
K: Key differentiator
L: Last checked (date)
M: Notes/changes since last check

Sheet: Pricing History
Columns:
A: Competitor
B: Date
C: Service
D: Old Price
E: New Price
F: Change Reason (if known)
```

### Initial Data (Fill This In)

Spend 2-3 hours on Day 1 populating this. Then 15 min/month to maintain.

**Where to find competitors:**
- Upwork search: "AI automation" + "Australia" filter
- Fiverr search: "automation" + sort by rating
- Google: "AI automation consultant Australia"
- LinkedIn search: "AI automation" + your city
- Reddit: r/automation, r/zapier — look for people promoting services
- Your own discovery calls: prospects will name-drop competitors

---

## 4. MONTHLY MONITORING ROUTINE

### First Monday of Each Month (15 min)

1. **Open tracking spreadsheet**
2. **Check top 5 competitors' websites** for new services, pricing changes, new clients
3. **Check their LinkedIn** — any new posts? New positioning?
4. **Spot-check Upwork/Fiverr** — any new competitors? Price changes?
5. **Update spreadsheet** with any changes
6. **Flag any threats:**
   - Competitor lowered prices significantly → Monitor. Don't race to bottom.
   - Competitor entered your specific niche → Differentiate harder.
   - Competitor launched a product that competes with your service → Consider bundling.

### Quarterly Deep-Dive (30 min)

1. **Re-score all competitors** on threat level
2. **Review your positioning** vs. the market — need to refresh?
3. **Check for new entrants** (Google the same queries fresh)
4. **Update `COMPETITOR_BATTLE_CARDS.md`** if new competitors emerged

---

## 5. AUTOMATED MONITORING (N8N RECIPE)

Set up once, runs automatically:

```
Trigger: Cron node (1st Monday of month, 9 AM)
  ↓
HTTP Request: Scrape top 5 competitor websites (or use Visualping/ChangeTower free tier)
  ↓
HTTP Request: Google Alerts RSS for "[competitor name] automation"
  ↓
Filter: Any changes detected?
  ↓ YES → Slack/Email: "Competitor {name} updated {page}. Check it: {url}"
  ↓ NO  → Log: "No changes detected for {month}"
```

> **Free tools that do this for you:**
> - **Visualping** (visualping.io) — monitors web page changes. Free: 2 pages, daily checks.
> - **Google Alerts** (google.com/alerts) — email when competitor is mentioned. Set up for each competitor name + "automation."
> - **Feedly** (feedly.com) — RSS feed of competitor blogs.

---

## 6. COMPETITIVE INTELLIGENCE USES

### In Discovery Calls

- "X charges A$300 for audits. Why are you A$497?"  
  → "My audit includes a 10-point security scan and a tech stack recommendation report they don't offer. Here's the difference."

- "I could just use Zapier myself."  
  → "Absolutely. If you have 5-10 hours to learn and maintain it. Most of my clients tried that first — they came to me when the workflows broke at 2 AM."

### In Your Marketing

- **Price anchoring:** "Most automation consultants charge A$150-200/hr. I charge A$85-150 because I work fixed-price — you know the cost upfront."
- **Differentiation:** "Unlike no-code platforms that lock you into monthly fees, I build you a self-hosted n8n instance you own forever."

### In Pricing Decisions

- If ALL competitors raised prices → you can too
- If a new entrant is undercutting → don't match. Differentiate on quality, speed, or niche.
- If you're the most expensive → own it. "Premium automation for businesses that want it done right the first time."

---

## 🔗 CROSS-REFERENCES

- `COMPETITOR_BATTLE_CARDS.md` — Objection handlers using this intel
- `PRICING_PSYCHOLOGY_GUIDE.md` — How to price relative to competitors
- `Discovery_Call_Script.md` — Where you'll use competitor intel (Phase 4 objections)
- `AUTOMATION_TEMPLATE_PACK.md` — n8n workflow for automated monitoring

---

> **Last updated:** 2026-06-28 — Round 13  
> **Action:** Set up Google Alerts for your top 3 competitors today (2 minutes each).
