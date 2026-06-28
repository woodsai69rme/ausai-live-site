# LinkedIn Outreach Runbook — Australian Small Business AI Automation

> **Why manual, not automated?** LinkedIn aggressively blocks scripted search via CAPTCHA. The browser-use agent was blocked on every search engine. Manual pre-qualified search from your logged-in session is safer, faster, and ToS-clean.

---

## 30-minute workflow

**Phase 1 — Search & collect (10 min):**
Run these 8 queries in LinkedIn's People search bar. Copy 25 names into a scratch sheet.

### Search queries (paste into LinkedIn search)

| # | Query                                                                                  | Why this angle                          |
|---|----------------------------------------------------------------------------------------|------------------------------------------|
| 1 | `"overwhelmed" AND "looking for help"` + Australia, 11-50 employees, Marketing         | Marketing service owners in pain        |
| 2 | `"scaling" AND "hiring" AND "automation"` + Australia, 11-50 employees, Real Estate     | Real estate agencies growing             |
| 3 | `"spending too much time on" AND "bookkeeping"` + Australia, 1-10 employees, Accounting | Bookkeepers drowning                     |
| 4 | `"e-commerce" AND "team" AND "busy"` + Australia, E-commerce                          | E-com operators overflowing             |
| 5 | `"agency owner" AND "AI"` + Australia, Marketing & Advertising                         | Agencies already curious about AI        |
| 6 | `"founder" AND "solo" AND "automating" OR "AI"` + Australia, 1-10 employees          | Solo founders reaching for AI            |
| 7 | `"recruiting" AND "manual" AND "sourcing"` + Australia, 11-50 employees, Staffing      | Recruiters drowning in manual work       |
| 8 | `"tradie" OR "trade business"` + Australia, Construction                              | Tradies with $50k+ revenue, often need scheduling/quotes AI |

**Tip:** Use the People filter (not Companies). Set the Location to Australia > Sydney / Melbourne / Brisbane / Perth > 25-mile radius. Filter by Current company: tick the relevant industry box.

### Filter to qualified-only (collect to `c:\users\karma\leads_2026-06-25.csv` with the template below)

| Column              | What to capture                                                |
|---------------------|----------------------------------------------------------------|
| `name`              | Full name as on LinkedIn                                       |
| `profile_url`       | https://www.linkedin.com/in/<slug>/                            |
| `company`           | Company name                                                   |
| `role`              | Founder / Owner / Director / GM                                |
| `headline`          | First line of their LinkedIn headline (the pain-signal line)   |
| `recent_post`       | Title + URL of a recent post they made about the pain          |
| `trigger`           | one-sentence: WHY they're a fit for AI automation right now    |
| `dm_draft_index`    | 1-5 — picks one of the 5 templates in LINKEDIN_DM_TEMPLATES.md |
| `score`             | HOT (5) / WARM (3) / COLD (1) — see scoring matrix             |
| `sent_date`         | leave blank until you actually send                            |
| `reply`             | leave blank until they reply                                   |

**Qualification = score ≥ 3 (WARM).** Only send DM templates to WARM+HOT. Skip COLD.

### Scoring matrix

| Signal                                                       | HOT (+5)  | WARM (+3)  | COLD (+1)  |
|--------------------------------------------------------------|-----------|------------|------------|
| Posted about scaling / hiring / overwhelm / "looking for"   | yes       | mention only | none       |
| Industry = Marketing / Real Estate / Accounting / Recruit   | yes       | adjacent   | unrelated  |
| Solo or team 1-50                                            | yes       | 50-200     | 200+ (enterprise) |
| Australia-based                                             | yes       | NZ / Asia  | other      |
| Already posting about AI / tools / n8n / Make / Zapier      | yes       | aware      | unaware    |
| Recent activity (< 30 days)                                  | yes       | 30-90 days | > 90 days  |
| Examples:                                                    | 5+ matches = HOT | 3-4 matches = WARM | 2 or fewer = COLD |

---

**Phase 2 — Personalize & send (15 min):**

1. Open 5 profiles from Phase 1 (the WARM+/HOT rows).
2. For each, read their **last 3-5 posts** (~90 seconds each).
3. Open `LINKEDIN_DM_TEMPLATES.md`. Pick the template whose `dm_draft_index` you marked.
4. Fill in the `[BRACKETED]` placeholders using **something you read in their posts** — not generic praise. Referencing a specific post is the difference between "another bot" and "a real person who read what I wrote".
5. Send. (Do NOT use InMail credits — use free DMs to connections of connections.)

### DM template mapping

| If their trigger is...                                            | Use template index |
|-------------------------------------------------------------------|--------------------|
| Overwhelmed by manual ops / admin                                  | 1                  |
| Hiring pain / team scaling                                        | 2                  |
| Posting about AI / automation curiosity                           | 3                  |
| E-commerce / Shopify scaling                                      | 4                  |
| "Looking for help" with content / SEO / social                    | 5                  |

---

**Phase 3 — Track replies & convert (5 min/day after):**

1. Append every sent DM to `c:\users\karma\leads_2026-06-25.csv` with `sent_date` filled.
2. Every reply → bump `score` and assess using `GIG_PICK_MATRIX.md`.
3. **First reply, even a "thanks", triggers**: book a 20-min free discovery call on the same day. Reply window = 4 hours max.
4. Every booked call append to `REVENUE_LEDGER.jsonl` with `event: meeting_booked` (no amount yet).

---

## How to know it worked

- 25 personalized DMs sent in week 1
- 3-5 replies expected (12-20% reply rate on personalized DMs)
- 1-2 booked discovery calls
- 1 closed gig within 14 days = first $1,500-$4,000 AUD

## What NOT to do

- ❌ Don't send 50 DMs in 24 hours (LinkedIn rate-limit kills your account)
- ❌ Don't send the same template twice (read each profile; personalise)
- ❌ Don't pitch "AI" or "automation" in the opener — pitch **the specific outcome they posted about**
- ❌ Don't follow-up more than once. If no reply in 7 days, drop the lead.
- ❌ Don't add value-add preambles like "I love your work". Start with the pain you saw.
