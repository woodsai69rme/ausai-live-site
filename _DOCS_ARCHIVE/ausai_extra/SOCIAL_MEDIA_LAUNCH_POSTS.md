# Social Media Launch Posts — Copy/Paste Ready

> **When to post:** Tuesday-Thursday 8-10 AM (your timezone) for max reach.
> **Pin them in order:** Reddit first (humility), then LinkedIn (B2B), then Twitter (broad).
>
> **🔗 UTM tracking rule:** Every URL you paste into a post = add `?utm_source={platform}&utm_medium=social&utm_campaign=launch-day-{n}&utm_content={post-title-slug}` so you can see exactly which channel converted. Append this to ALL calendar/Stripe/GitHub links in your actual posted copy.

---

## 1. Reddit Posts (3 subreddits — post in this order, 1 per day)

### r/automation (Day 1)

**Title:** I built 280+ free n8n workflow templates for AI agents — open source

**Body:**
```
Sharing a starter pack I put together for anyone using n8n + AI agents.

**What's inside:**
- 280+ workflow JSON files (importable directly into n8n)
- AI chat agent, web scraper, chart analyzer, paper summarizer, financial dashboard
- All MIT-licensed / attribution-required

**Stack:**
- OpenRouter for LLM routing (free tier available)
- Postgres + pgvector for RAG
- n8n as the automation glue

**GitHub:** [your repo link]

If you import one and end up customizing it, I'd love to see what you build.

---
*(This is the post. Read what got shared) *
```

### r/LocalLLaMA (Day 3)

**Title:** Open-source RT-4060 AI workstation — Ollama + ComfyUI + n8n setup guide

**Body:**
```
Took my RTX 4060 8GB + 32GB RAM and turned it into a local AI workstation that runs:

- SD 1.5 + Juggernaut-XL via ComfyUI (image generation)
- LLaMA 3.2 + Mistral + DeepSeek via Ollama (chat / agents)
- Whisper + librosa for audio/BPM analysis
- 280+ n8n workflows for automation

Everything is local, no cloud spend, fully reproducible.

Full setup guide in the repo: [link]

Question for the room: What's the best lightweight open model you've gotten running on 8GB VRAM?
```

### r/sideproject (Day 7)

**Title:** Built an AusAI consulting site in 3 days for $250 — here's the whole stack

**Body:**
```
Solo-built this in one weekend:

- 5-page responsive landing page (hosted on Hostinger)
- Stripe payment links for 3 service tiers
- Calendly embed for 30-min free audits
- Auto-generated portfolio images (PIL, no GPU needed)
- n8n workflow for lead → email → CRM

Total cost to deploy: ~$3/mo for hosting.

Tech: HTML + vanilla CSS + Python scripts. No frameworks.

Live: [link]
Repo: [link]

Happy to share the templates if anyone's planning a similar one-person consultancy.
```

---

## 2. LinkedIn Posts (Personal Profile — 2 versions)

### Version A: Story (Day 9)

```
After 25 years in IT, I finally built the thing I wished I'd had 10 years ago:

An AI consultancy that ships production systems this week, not next quarter.

Last 7 days I delivered:
→ A custom RAG chatbot for a law firm (5 docs, 4 days)
→ An n8n pipeline that scrapes & summarizes 30 YouTube channels (1 day)
→ A portfolio site + Stripe checkout for a freelance designer (3 days)

The stack:
• OpenRouter (routing AI spend across 50+ providers)
• n8n (280+ workflow templates, self-hosted)
• Ollama (local LLMs on RTX 4060)
• ComfyUI (image gen, SD 1.5 + Juggernaut-XL)
• PostgreSQL + pgvector (RAG memory)

The price:
$500 chatbot, $1,200 automation bundle, $250 landing site, $80/hr consulting.

The honest truth: I can deliver these faster and cheaper than agencies 5x my size because I skipped the project-manager layer.

30-min free audit calendar in comments. 👇
```

### Version B: Listicle (Day 14)

```
5 AI stack picks for solo consultants (with budget):

1️⃣ LLM model: OpenRouter — free tier, 50+ models, single API key
2️⃣ Automation: n8n — 280+ workflows on GitHub, self-host for ~$5/mo
3️⃣ Image gen: ComfyUI + SD 1.5 — local, free, RTX 4060 friendly
4️⃣ Local LLM: Ollama — 6GB for 7B models, no cloud round-trip
5️⃣ Vector DB: Postgres + pgvector — Supabase free tier covers most projects

Full setup guide + scripts: [link]

What would you add?
```

---

## 3. Twitter / X Posts (single tweet thread + 5 standalones)

### Thread (best for engagement, ~7 tweets)

**Tweet 1:**
```
I shipped 3 AI projects in 7 days for under $200/mo in tooling.

Here's the stack 👇
```

**Tweet 2:**
```
1. OpenRouter → ONE API key, routes to 50+ LLM providers
   Free tier covers ~90% of prototyping → $0
```

**Tweet 3:**
```
2. n8n (self-hosted) → open-source Zapier
   280+ ready-to-import workflows on GitHub
   Runs on a $5/mo VPS
```

**Tweet 4:**
```
3. ComfyUI + SD 1.5 → local AI images
   Free, runs on RTX 4060 8GB
   Skip Midjourney subscriptions entirely
```

**Tweet 5:**
```
4. Ollama → local LLMs for sensitive data
   LLaMA 3.2, Mistral, DeepSeek - 6-7GB RAM each
```

**Tweet 6:**
```
5. PostgreSQL + pgvector → RAG memory
   Free on Supabase, scales to 50k docs
```

**Tweet 7:**
```
Combined: ~$8/mo.

Hosted on Hostinger (existing plan), GitHub, Vercel free tier.

Full template repo: [link]
```

### Standalones (pick one/day)

- *"Hot take: solo consultants will replace agencies within 3 years. The math: zero project-manager layer + OpenRouter + n8n = ship in days, not months. I just did 3 projects in 7 days."*

- *"Free 30-min AI audit calendar is open this week. Drop a comment 'audit' and I'll DM you the link. Slots limited to 5 this week."*

- *"If you're still paying $50/mo for Midjourney you're leaving money on the table. ComfyUI + SD 1.5 runs locally on a $400 GPU. My workflow guide: [link]"*

- *"The most underrated AI tool of 2026: pgvector. Half the AI startups I audit are paying $300/mo for Pinecone. Postgres + pgvector does the same thing free on Supabase."*

- *"n8n just hit 143k stars on GitHub and most people haven't realized it's now the cheapest way to deploy AI agents at scale. 280+ workflows, all open-source."*

---

## 4. Hacker News Comment Templates (search for relevant threads)

When you see a post about AI/automation/n8n, drop one of these:

> Recently shipped 3 AI projects for under $200/mo total cost. The breakthrough for me was using OpenRouter as the LLM gateway — one API key routes to deepseek-r1 free, claude-sonnet paid, llama-3 local, all in the same workflow. Stack details + scripts here: [link]

---

### UTM Template Cheat-Sheet (paste-ready)

| Channel | utm_source | utm_medium | utm_campaign | utm_content |
|---|---|---|---|---|
| Reddit r/automation | reddit | forum | launch-day-1 | starter-pack |
| Reddit r/LocalLLaMA | reddit | forum | launch-day-3 | workstation |
| Reddit r/sideproject | reddit | forum | launch-day-7 | landing-page |
| LinkedIn (story) | linkedin | post | launch-day-2 | personal-story |
| LinkedIn (listicle) | linkedin | post | launch-day-9 | stack-listicle |
| Twitter thread | twitter | thread | launch-day-3 | ai-stack-thread |
| Twitter standalone | twitter | tweet | launch-day-{14-18} | {topic} |
| Hacker News | news | comment | launch-day-{n} | {thread-topic} |

**Example applied (use your real URL — see MANUAL_DEPLOY.md):**
`https://YOUR_DEPLOYED_URL/?utm_source=reddit&utm_medium=forum&utm_campaign=launch-day-1&utm_content=starter-pack`

After you deploy (90 sec via `MANUAL_DEPLOY.md`), paste your actual URL in place of `YOUR_DEPLOYED_URL` everywhere above. Every post = UTM-tagged. Then check your deploy analytics + Stripe for which channel drove the first sale.

## 5. Subreddit Engagement Schedule

| Day | Platform | Action |
|-----|----------|--------|
| Day 1 | Reddit r/automation | Post starter pack |
| Day 2 | LinkedIn | Version A story post |
| Day 3 | Twitter | Thread (7 tweets) |
| Day 4 | Reddit r/LocalLLaMA | Workstation post |
| Day 7 | Reddit r/sideproject | Landing page build post |
| Day 9 | LinkedIn | Version B listicle post |
| Day 14 | Twitter | 5 standalone tweets (1/day) |
| Ongoing | Hacker News | Reply 2×/week with comments on AI threads |

---

✓ **All posts ready. Copy any block verbatim — just replace [link] placeholders with your GitHub repo / Calendly / Hostinger URLs.**
