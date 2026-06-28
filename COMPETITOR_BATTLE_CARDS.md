# Competitor Battle Cards — AusAI Tech

> **Purpose:** Know exactly how to handle "Why you vs. [competitor type]?" objections. Use these during discovery calls, LinkedIn DMs, and proposals.
> **When to use:** Discovery call Phase 4 objections, LinkedIn outreach when prospect says "we already have someone," proposal follow-ups.
> **Prerequisite:** `Discovery_Call_Script.md` (basic objection handling), `SERVICE_TIER_ONEPAGER.html` (pricing context)

---

## Battle Card 1: Big Agencies (Accenture, Deloitte, McKinsey Digital, Local Agencies)

**Their play:**
- Brand-name safety ("Nobody got fired for hiring Deloitte")
- Large teams (impressive on paper — but you get the B-team)
- Process-heavy (6-week discovery before any work starts)
- $50k-500k minimum engagements

**Your kill points (say these):**
> "Agencies are great for Fortune 500 transformation. For a focused automation project, you're paying for their overhead — junior consultants doing the work while partners bill at $500/hr for oversight. You get me from day one — the person who actually builds your system."

> "Big agencies run 6-week discovery phases before writing a line of code. I'll have your first automation working within 5 days. If it doesn't deliver, you haven't committed to a $50k retainer."

**Landmine to plant:**
> "Ask your agency contact: who specifically would be writing the automation code? What's their seniority? If they can't name the person, you're getting whoever's on the bench."

**When you'll lose:** Compliance-heavy industries (banking, defence) where vendor certification matters. Accept this and move on.

**Positioning:** *Speed + direct expertise. No account managers, no junior teams, no overhead.*

---

## Battle Card 2: Freelance Marketplaces (Fiverr, Upwork, Freelancer.com)

**Their play:**
- Price anchoring ($50-200 vs your $497-1,497)
- "Good enough" quality
- Fast turnaround (perceived — often false)

**Your kill points (say these):**
> "I regularly review Fiverr AI builds in this space. The pattern I see: they work for 2 weeks, then break when the API changes or the edge case hits. There's no error handling, no documentation, no warranty. You pay twice — once for the build, once for someone else to fix it."

> "On Fiverr, you're buying a deliverable. With me, you're buying an outcome. If it breaks in 30 days, I fix it. If the scope needs an adjustment, we talk. A Fiverr freelancer ghosts you after the 5-star review."

> "A Fiverr gig at $200 for 'AI chatbot' is someone copy-pasting a ChatGPT wrapper. The $1,497 I charge includes API security, prompt injection hardening, error fallbacks, and a 30-day warranty. You're not comparing the same thing."

**Landmine to plant:**
> "Before hiring on Fiverr, ask them: 'What happens when the API returns a 429 rate-limit error? What's your retry strategy?' If they can't answer, they're copy-pasting templates."

**When you'll lose:** Pure price shoppers with no quality requirements. Let them go — they'll be back after the Fiverr build fails.

**Positioning:** *Outcome vs. deliverable. Warranty. You're buying insurance, not just code.*

---

## Battle Card 3: In-House / DIY

**Their play:**
- "We'll just have our IT guy / intern / CTO do it"
- "We'll use ChatGPT and figure it out"
- Pride in self-sufficiency

**Your kill points (say these):**
> "Your CTO's time is worth $150+/hour. If they spend 40 hours learning n8n, debugging API auth, and handling edge cases, that's $6,000 of their time — and they're not working on your actual product. I'll deliver in 1/4 the time at 1/4 the cost of their opportunity cost."

> "DIY with ChatGPT gets you 70% of the way. It's the last 30% — error handling, edge cases, monitoring, security — that takes 90% of the time. That 30% is exactly what I do."

> "The question isn't 'can you build it.' It's 'should your most valuable people spend their time building it?' Every week your CTO spends on automation is a week your product roadmap slips."

**Landmine to plant:**
> "Try building just one workflow yourself — the simplest one. Track every hour, every dead end, every 'works in testing but not in production' bug. Then compare that to my 5-day timeline with warranty."

**When you'll lose:** Companies with genuinely capable in-house automation talent. If the CTO built their last automation in n8n and it works, they don't need you. Move on.

**Positioning:** *Opportunity cost. Speed. The last 30% is where the real work lives.*

---

## Battle Card 4: No-Code Platform Direct Sales (Zapier/Make/n8n Themselves)

**Their play:**
- "We can do it ourselves with Zapier"
- "n8n is free / open source"
- "The platform has AI now, we don't need a consultant"

**Your kill points (say these):**
> "Zapier and Make are powerful — I use them daily. But the platform sells you the hammer, not the house. You still need to: design the architecture, handle error states, set up monitoring, write the fallback logic, and secure the API keys. That's what I bring."

> "n8n is free and powerful. It's also unopinionated. Give 10 people n8n and the same problem, and you'll get 10 different solutions — and 8 of them will break in production. I bring battle-tested patterns."

> "The platform's AI features help you build faster. They don't tell you what to build. They don't know YOUR business, YOUR edge cases, or YOUR compliance requirements. I do."

**Landmine to plant:**
> "Open a free Zapier account and try building one real workflow — not a demo, something production-grade with error handling and Slack alerts when things fail. See how many hours it takes. Then compare to my timeline."

**When you'll lose:** Trivial, single-step automations ("New Gmail → Slack message"). Don't compete on those.

**Positioning:** *Architecture + patterns + production hardening. You don't need the tool — you need the system.*

---

## Battle Card 5: Other Solo AI Consultants

**Their play:**
- Same positioning as you
- Possibly cheaper
- Possibly more experience / better portfolio

**Your kill points (say these):**
> "Good — you're already looking for this. Here's what matters: ask any consultant what happens on Day 31. Do you get a warranty? A retainer option? A documented handoff? Most solo consultants deliver the project and disappear. I stay through Day 30 and beyond."

> "I specialise in the intersection of AI automation AND security. Most AI consultants can build the chatbot. Few can also audit it for prompt injection, harden the API layer, and document the security posture. That's my background."

**Landmine to plant:**
> "Before hiring any automation consultant, ask: 'Show me a past project's error-handling code.' If they can't — or if there's no error handling — you're buying a fragile system."

**When you'll lose:** More established consultants with 10+ case studies. That's okay — build your portfolio.

**Positioning:** *Security + automation double threat. Post-delivery commitment. Australian-focused (local timezone, local compliance).*

---

## Kill Criteria — When to Walk Away

Not every deal is worth winning. Disqualify fast:

| Deal Type | Walk Away If... |
|---|---|
| **Price-war** | Prospect is shopping 5+ vendors and focuses only on price. They'll treat you as a commodity. |
| **Unrealistic timeline** | "Need it by Friday" for a 2-week build. They'll blame you when the rushed deliverable breaks. |
| **Vague scope** | "Just make everything better." Guaranteed scope creep. Require a defined SOW or walk. |
| **Payment drama** | They negotiate the 50% upfront, ask for net-60 terms, or mention "previous contractor issues with payment." |
| **Ethics risk** | They ask you to scrape competitors, fake reviews, or automate spam. Hard no. |
| **Bad-mouthing previous providers** | If they trash-talk 3 past freelancers, you'll be number 4. |
| **No decision authority** | The person on the call can't say yes. They're a filter, not a buyer. Ask to speak to the decision maker. |

**Rule:** A bad client costs you 3× the revenue in time, stress, and opportunity cost. Say no early and often.

---

## Quick-Reference: One-Liner Responses

| They say... | You say... |
|---|---|
| "You're more expensive than Fiverr" | "Fiverr sells a deliverable. I sell an outcome with a warranty. Different product." |
| "Our CTO can build this" | "They can. Should they? At $150/hr, 40 hours of their time costs more than my entire engagement." |
| "Why not just use Zapier?" | "Zapier is the tool. I'm the architect. You need both." |
| "We work with a big agency already" | "Great — I can handle the focused execution work they're too expensive for." |
| "Another consultant quoted half that" | "Ask them what happens on Day 31. If the answer isn't '30-day warranty and retainer option,' you're comparing different services." |
| "Can you match their price?" | "I can scope down the engagement to match your budget. I can't match prices on the same scope without cutting quality." |

---

## Positioning Summary Card

**AusAI Tech = 3 things no one else has together:**

1. **AI Automation expertise** (n8n, Zapier, custom Python, ComfyUI, OpenRouter)
2. **Security-first approach** (every build includes API hardening, prompt injection checks, key rotation)
3. **Australian solo consultant** (local timezone, local compliance knowledge, no agency overhead)

**This is your moat:** Most AI consultants can't do security. Most security consultants can't build automation. Most agencies are slow and expensive. You sit at the intersection.

---

*Use these battle cards during the "Objection Handling" section of your discovery calls (`Discovery_Call_Script.md` Phase 4). Don't memorise them — keep this doc open during calls.*
