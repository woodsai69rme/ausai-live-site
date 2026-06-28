# Referral Program — AusAI Tech

> **Purpose:** Turn happy clients into a self-sustaining lead pipeline. Structured incentives for warm introductions.
> **When to activate:** After every successful project delivery (see `CLIENT_OFFBOARDING.md` Phase 3, Ask 3).
> **Prerequisite:** `CLIENT_OFFBOARDING.md`, `EMAIL_TEMPLATES.md`

---

## Why Referrals Are Your Best Channel

| Channel | Close Rate | Cost Per Lead | Time to Close |
|---|---|---|---|
| **Warm referral** | **50-70%** | ~A$75-225 (commission) | 5-14 days |
| LinkedIn cold DM | 3-8% | A$0 (time only) | 14-30 days |
| Fiverr marketplace | 5-15% | 15-20% platform fee | 1-7 days |
| Content / SEO | 1-3% | A$0 + 6-month build | 30-90 days |

**The math:** 1 warm referral is worth ~10 cold DMs. Your highest-leverage activity after delivering a great project is asking for referrals.

---

## Program Structure

### Option A — Cash Commission (Best for B2B clients)

**Payout:** 15% of the referred client's first engagement fee.

| Referred Client's Purchase | Referrer Earns | Paid When |
|---|---|---|
| AI Audit (A$497) | A$75 | Referred client pays invoice |
| AI Build (A$1,497) | A$225 | Referred client pays 50% deposit |
| AI Partner (A$2,497/mo) | A$375 | Referred client pays first month |
| Custom project (>$3,000) | 10% (capped at A$500) | Referred client pays final invoice |

**Payment method:** Bank transfer or PayPal. Send within 7 days of referred client's payment clearing.

**Tracking:** Track in `LEAD_TRACKER.html` → set Source to "Referral — {Referrer Name}" and add referral commission note.

**Tax note (Australia):** If you pay more than A$75 in a financial year to any individual, keep a record. If they're earning referral income regularly, they may need to declare it. You don't need to withhold tax on referral commissions to individuals (it's not employment income), but if you're paying another business with an ABN, ask for their ABN or you may need to withhold 47%. **Verify all tax treatment with your accountant before paying commissions.**

---

### Option B — Service Credit (Best for clients who'll re-buy)

**Credit:** 1 free month of AI Partner retainer (A$2,497 value) for every successful referral that closes at A$1,497+.

**Why this works:**
- Locks them into ongoing engagement
- Costs you service time, not cash
- Higher perceived value than A$225 cash

**When to offer:** If the client is on (or considering) the AI Partner retainer.

**Tracking:** Track as a credit note. Apply on the next retainer invoice. Expiry: 12 months from issue.

---

### Option C — The "Forward This" (Zero Friction)

The lightest ask. For clients who are happy but not raving. No money changes hands.

**The template (give this to the client):**

> Hi {Client Name},
>
> If you know anyone dealing with {the problem you solved}, I'd be grateful if you forwarded this:
>
> --
> Subject: Quick intro — AI automation consultant
>
> Hi {Prospect},
>
> Karma at AusAI Tech recently built {brief description of what you built} for us. Saved us {X hours / Y dollars}. Straightforward process, no surprises.
>
> He's taking on new projects. Here's his link: {your Calendly link}
>
> No pressure — just thought it might be useful.
>
> Best,
> {Client Name}
> --
>
> No need to write anything yourself — feel free to forward that or tweak it however you like. Appreciate you either way.

**When to use:** When the client says yes to a testimonial but doesn't have someone specific in mind. Plant the seed for when they do.

---

### Option D — Affiliate Program (For Content Creators, Other Consultants)

For non-clients who want to refer business (other freelancers, consultants, agency owners who don't do AI).

**Payout:** 10% of first engagement (capped at A$300).

**Rules:**
- Must use a unique referral link or code (track via Calendly UTM or simple `?ref=NAME` in your booking link)
- Paid only on closed, paid engagements
- Not stackable with other discounts

**Set-up (manual, 10 minutes):**
1. Create a unique Calendly booking link with UTM: `https://calendly.com/{your-username}/ai-audit?utm_source=referral&utm_medium=affiliate&utm_campaign={partner-name}`
2. Share the link with the partner
3. When a booking lands with that UTM, note it in `LEAD_TRACKER.html`
4. Pay commission within 7 days of the referred client's payment

---

## When to Ask for Referrals

The "3-Ask System" (from `CLIENT_OFFBOARDING.md` Phase 3):

1. **Testimonial** — soft ask during handoff call
2. **Retainer** — medium ask during handoff call
3. **Referral** — hard ask ONLY if Ask 1 or 2 was positive

**Timing formula:**
- **Immediately after deliverable praise:** "That's fantastic to hear. Who else do you know who's dealing with similar challenges? I'd love to help them too."
- **Day 14 check-in:** "Quick check-in — changed anything about the system? Also, wanted to mention: I'm taking on 2 new clients this month. If anyone comes to mind, I pay a 15% referral fee."
- **Day 30 warranty close:** Final check-in — natural moment to ask.

---

## Referral DM Template (for you to send to past clients)

> Subject: Quick thought — client opening this month
>
> Hi {NAME},
>
> Hope {project outcome} is still running smoothly.
>
> Quick one: I'm opening up 2 client slots for {month}. Before I post publicly, wanted to check — anyone in your network who might be dealing with {similar pain point}?
>
> I pay a 15% referral commission on any engagement that closes. All you need to do is forward them my Calendly link.
>
> If nobody comes to mind, no worries at all. Just figured I'd ask you first.
>
> Best,
> Karma
> AusAI Tech

---

## Anti-Patterns (Don't Do This)

| Don't | Why | Do Instead |
|---|---|---|
| Ask for referrals before delivering value | You haven't earned it | Wait until the client has seen results |
| Make it awkward or high-pressure | Damages the relationship | Keep it casual — "no worries at all" is always in the script |
| Offer referral fees as a substitute for doing great work | Referrals come from results, not bribes | Lead with the outcome, mention the commission as a bonus |
| Spam past clients monthly asking for referrals | You'll get unsubscribed | 2-3 gentle asks per year max |
| Promise commissions you can't track | Damages trust | Track every referral in `LEAD_TRACKER.html` and pay within 7 days |

---

## Referral Tracking (in LEAD_TRACKER.html)

For each referred lead, record:
- **Source:** "Referral — {Referrer Name}"
- **Referrer contact:** Email or phone
- **Commission type:** Cash (15%) / Credit (1 mo retainer) / Warm intro (no commission)
- **Commission amount:** A$X
- **Paid date:** (when referred client's payment clears)
- **Status:** Pending / Paid / Credit Applied

---

## Monthly Referral Targets

| Month | Referrals Asked | Referrals Received | Referrals Closed | Revenue from Referrals |
|---|---|---|---|---|
| Month 1 | 2-3 | 1-2 | 0-1 | A$0-500 |
| Month 2 | 5-8 | 2-4 | 1-2 | A$500-1,500 |
| Month 3 | 8-12 | 3-6 | 2-3 | A$1,500-3,000 |
| Month 6+ | Ongoing | 5-10/mo | 3-5/mo | A$3,000-7,500/mo |

**The goal:** By month 6, referrals should be 30-40% of your pipeline. At that point, you can reduce cold outreach — referrals convert higher and close faster.

---

## Related Documents

- `CLIENT_OFFBOARDING.md` — The 3-Ask System (where referrals live in the client lifecycle)
- `EMAIL_TEMPLATES.md` — Referral ask email template
- `LEAD_TRACKER.html` — Track every referral and commission
- `CASE_STUDY_TEMPLATE.md` — Completed case studies are referral fuel
- `COMPLIANCE_CHECKLIST.md` — Tax implications of paying commissions

---

*Referrals aren't a program. They're a habit. Ask every happy client, every time. One yes per month compounds into a self-sustaining pipeline.*
