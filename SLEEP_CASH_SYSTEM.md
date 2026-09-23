# SLEEP_CASH_SYSTEM — Autonomous Income System for Australia

> **Generated:** 2026-06-30
> **Operator:** Karma (Australia, RTX 4060 8GB, 64GB RAM, Windows 11)
> **Goal:** Build a system that runs 24/7, generates real AUD, needs zero human approvals per transaction, and operates autonomously while you sleep
> **Design constraints:** Zero approvals · Real cash · Automatic · Australia-based · Agent-driven

---

## Executive Summary

This document defines a **5-lane autonomous income system** that layers on top of the existing `SLEEP_TRIPLE` infrastructure. Each lane was selected because it meets ALL four constraints: runs automatically, generates real money (not credits/virtual), requires no per-transaction human approval, and is legally operable from Australia.

**Target:** A$500/mo by Month 2 → A$2,000/mo by Month 6 → A$5,000/mo by Month 12

**Capital required:** A$0 to start (Lanes 1-3) · A$500+ optional for Lane 5 (crypto)

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    SLEEP_CASH_SYSTEM                          │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  LANE 1     │  │  LANE 2     │  │  LANE 3             │  │
│  │  AI Digital │  │  Faceless   │  │  Print-on-Demand    │  │
│  │  Products   │  │  YouTube    │  │  (AI Design +       │  │
│  │  (Gumroad)  │  │  + Affiliate│  │   Shopify+Printful) │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                    │              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  LANE 4     │  │  LANE 5     │  │  ORCHESTRATOR       │  │
│  │  API-as-a-  │  │  Crypto     │  │  (n8n + SLEEP_      │  │
│  │  Service    │  │  Yield +    │  │   TRIPLE scheduler) │  │
│  │  (Micro-    │  │  Arbitrage  │  │                     │  │
│  │   SaaS)     │  │  (Freqtrade)│  │  Runs 23:00-07:00   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  REVENUE DASHBOARD (port 3144)                        │   │
│  │  Real-time AUD revenue tracking + alert fanout        │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## Lane 1: AI Digital Product Factory (EXISTING — GO LIVE)

> **Status:** Code exists in `SLEEP_TRIPLE/opt_a_digital_factory.py` · Dry-run only · Needs Gumroad API key
> **Zero approvals:** Gumroad instant shop (60-second signup, no review process)
> **Capital:** A$0

### How It Works (Autonomous Loop)

```
23:00 → Orchestrator triggers opt_a
     → Ollama (qwen2.5-coder) generates prompt pack / code snippets / design assets
     → ComfyUI generates cover art (if enabled)
     → Product staged as Gumroad draft (via Gumroad API)
     → Audit row written to SLEEP_TRIPLE_AUDIT.jsonl
     → Revenue event written to REVENUE_LEDGER.jsonl
07:00 → Morning digest sent to Discord/Telegram with overnight production summary
```

### Products to Generate (Nightly Rotation)

| Day | Product Type | Price | Content |
|---|---|---|---|
| Mon | AI Prompt Pack (50 prompts) | A$17 | Niche-specific (rotating: marketing, coding, design, business) |
| Tue | Code Snippet Library | A$27 | Language-specific (Python, JavaScript, TypeScript, Go) |
| Wed | Design Asset Pack | A$12 | ComfyUI-generated patterns, textures, backgrounds |
| Thu | AI Prompt Pack (different niche) | A$17 | |
| Fri | Code Snippet Library (different lang) | A$27 | |
| Sat | Design Asset Pack | A$12 | |
| Sun | Bundle (all week's products) | A$47 | |

### Go-Live Checklist

- [ ] Create Gumroad account (gumroad.com — 60 seconds, no approval)
- [ ] Get Gumroad API key from Settings → Applications
- [ ] Add API key to `opt_a_config.json`
- [ ] Set `enable_comfy_cover: true` (ComfyUI is installed at `C:\Users\karma\ComfyUI`)
- [ ] First test: `python opt_a_digital_factory.py --run --publish staged` (publishes as draft)
- [ ] Review draft quality, refine generation prompts
- [ ] First live: `python opt_a_digital_factory.py --run --publish published`
- [ ] Update schtasks: `python sleep_orchestrator.py --run --force-window --publish published`
- [ ] Fill Gumroad W-8BEN (non-US person form, one-time)

### Revenue Projection

| Month | Products/mo | Sales rate | Avg price | Revenue |
|---|---|---|---|---|
| Month 1 | 7 | 2% | A$20 | A$2.80 |
| Month 3 | 7 | 5% | A$20 | A$7.00 |
| Month 6 | 30 (backlog) | 3% | A$20 | A$18.00 |

> **Honest note:** Gumroad organic discovery is slow. This lane compounds over time as your product library grows. It's the lowest-effort lane but also the slowest to scale. Marketing (Reddit, Twitter, YouTube descriptions) accelerates it.

---

## Lane 2: Faceless YouTube Shorts + Affiliate (EXISTING — GO LIVE)

> **Status:** Code exists in `SLEEP_TRIPLE/opt_b_faceless_shorts.py` · Dry-run only · Needs YouTube OAuth + TTS
> **Zero approvals:** Instant-approval affiliate programs (Binance, Kraken, Hostinger, Crypto.com, Ledger, Persona)
> **Capital:** A$0

### How It Works (Autonomous Loop)

```
23:05 → Orchestrator triggers opt_b
     → Ollama generates 30-sec script from trending topics
     → TTS generates voiceover (Coqui TTS local = free, or ElevenLabs free tier)
     → ComfyUI generates background visuals
     → FFmpeg composites video (voiceover + visuals + captions)
     → YouTube Data API v3 uploads as Short
     → Affiliate links injected into description
     → Audit row + revenue event written
```

### Affiliate Programs (Zero Approval, Australian-Accessible)

| Program | Commission | Cookie Duration | Signup |
|---|---|---|---|
| Binance | 20-40% of trading fees | Lifetime | instant |
| Kraken | 20% of trading fees | Lifetime | instant |
| Hostinger | 60% per sale | 30 days | instant |
| Crypto.com | 50% of trading fees | Lifetime | instant |
| Ledger | 10% per sale | 30 days | instant |
| Persona | $5 per verified identity | 30 days | instant |

### Niche Strategy (High CPM + Affiliate Fit)

**Niche: AI/Crypto/Automation tutorials** — matches your existing knowledge, has high-value affiliate programs, and targets the exact audience that buys digital products (Lane 1 cross-sell).

### Content Rotation (Weekly)

| Day | Topic | Affiliate Link |
|---|---|---|
| Mon | "3 AI tools that replace $5k/mo SaaS" | Hostinger |
| Tue | "How to stake crypto in Australia 2026" | Kraken/Binance |
| Wed | "I automated my entire income with AI" | Hostinger |
| Thu | "Hardware wallet vs exchange: which is safer?" | Ledger |
| Fri | "Build a faceless YouTube channel with AI" | Hostinger |
| Sat | "Crypto yield farming for beginners" | Crypto.com |
| Sun | "AI identity verification explained" | Persona |

### Go-Live Checklist

- [ ] Create YouTube channel (google.com → YouTube → Create channel)
- [ ] Enable YouTube Data API v3 in Google Cloud Console
- [ ] Download OAuth 2.0 credentials (JSON)
- [ ] Add credentials path to `opt_b_config.json`
- [ ] Set `youtube_upload_dry_run: false`
- [ ] Configure TTS: install Coqui TTS (`pip install TTS`) OR sign up ElevenLabs free tier
- [ ] Set voiceover provider in config (`coqui` or `elevenlabs`)
- [ ] Add affiliate program URLs to config (already partially done)
- [ ] First test: `python opt_b_faceless_shorts.py --run --publish` (uploads first short)
- [ ] Review first short quality, refine script generation prompts
- [ ] Update schtasks to include `--publish` flag

### Revenue Projection

| Month | Shorts/mo | Subscribers | Ad Revenue | Affiliate | Total |
|---|---|---|---|---|---|
| Month 1 | 7 | 0-50 | A$0 | A$5-20 | A$5-20 |
| Month 3 | 30 | 200-500 | A$0 | A$50-150 | A$50-150 |
| Month 6 | 30 | 1000+ | A$20-50 | A$200-500 | A$220-550 |
| Month 12 | 30 | 5000+ | A$200-500 | A$500-1500 | A$700-2000 |

> **Note:** YouTube Partner Program requires 1000 subs + 4000 watch hours. Affiliate commissions start from day 1 — no approval needed. The first 3 months are purely affiliate-driven.

---

## Lane 3: Print-on-Demand with AI Design (NEW — BUILD)

> **Status:** Not built · Needs Shopify + Printful + AI design pipeline
> **Zero approvals:** Shopify (instant) + Printful (instant) + AI design (local ComfyUI)
> **Capital:** A$0 (Shopify has free trial; Printful is free to connect)

### How It Works (Autonomous Loop)

```
23:10 → Orchestrator triggers POD module
     → ComfyUI generates design (trending topic → AI art prompt → PNG)
     → Design uploaded to Printful as product mockup
     → Product published to Shopify store
     → Printful auto-fulfills orders (print + pack + ship)
     → Shopify notifies on sale
     → Revenue event written to ledger
```

### Tech Stack

| Component | Tool | Cost |
|---|---|---|
| Storefront | Shopify (basic plan) | A$45/mo after 3-day trial |
| Fulfillment | Printful | A$0 (per-item cost deducted from sale) |
| Design generation | ComfyUI (local) | A$0 |
| Product niches | AI-generated from trending topics | A$0 |
| Payment | Shopify Payments (Stripe-powered) | Built into Shopify |

### Product Niches (AI-Friendly, High Margin)

| Niche | Product | Printful Cost | Sell Price | Margin |
|---|---|---|---|---|
| AI/Crypto humor | T-shirt | A$18 | A$35 | A$17 |
| Developer memes | Hoodie | A$35 | A$65 | A$30 |
| AI art gallery | Poster (A3) | A$12 | A$29 | A$17 |
| Crypto lifestyle | Mug | A$10 | A$25 | A$15 |
| Productivity quotes | Phone case | A$12 | A$30 | A$18 |

### Build Plan (Week 1-2)

| Day | Action | Time |
|---|---|---|
| 1 | Sign up Shopify (3-day free trial) | 15 min |
| 2 | Sign up Printful, connect to Shopify | 30 min |
| 3 | Build ComfyUI design pipeline (text → AI art → PNG with transparency) | 2 hrs |
| 4 | Write Python module `opt_e_pod.py` (design gen → Printful API → Shopify publish) | 4 hrs |
| 5 | Configure Printful product templates (T-shirt, hoodie, poster, mug, phone case) | 2 hrs |
| 6 | Test: generate 5 designs, publish to Printful, sync to Shopify | 2 hrs |
| 7 | Set up Shopify Payments (requires ABN) | 30 min |
| 8-14 | Integrate into SLEEP_TRIPLE orchestrator (runs after opt_b) | 4 hrs |

### Revenue Projection

| Month | Products/mo | Sales rate | Avg margin | Revenue |
|---|---|---|---|---|
| Month 1 | 7 | 0% | A$17 | A$0 |
| Month 3 | 30 | 2% | A$17 | A$10 |
| Month 6 | 30 | 5% | A$17 | A$25 |
| Month 12 | 60 | 5% | A$17 | A$51 |

> **Honest note:** POD is the slowest lane. Organic Shopify traffic is near-zero without marketing. This lane becomes viable only when combined with Lane 2 (YouTube Shorts driving traffic to store) or paid ads.

---

## Lane 4: API-as-a-Service Micro-SaaS (NEW — BUILD)

> **Status:** Not built · Highest revenue potential but requires coding
> **Zero approvals:** Stripe (instant) + Vercel/Render free tier (instant)
> **Capital:** A$0

### Concept

Build small API endpoints that solve specific problems, charge per-call or per-month via Stripe. Run on free-tier cloud (Vercel/Render/Cloudflare Workers). Market via GitHub, Product Hunt, and API directories.

### API Product Ideas (Ranked by Effort vs Revenue)

| API | Purpose | Pricing | Effort | Monthly Potential |
|---|---|---|---|---|
| AI Prompt Optimizer | Takes a prompt, returns optimized version | A$0.01/call or A$29/mo | 4 hrs | A$200-1000 |
| YouTube Transcript Extractor | Extracts transcript from any YouTube video | A$0.005/call or A$19/mo | 2 hrs | A$100-500 |
| Crypto Spread Scanner (AU) | Real-time stablecoin spreads across AU exchanges | A$49/mo | 6 hrs | A$200-1000 |
| ComfyUI Workflow Validator | Validates ComfyUI workflow JSON + estimates VRAM | A$0.02/call or A$15/mo | 3 hrs | A$50-300 |
| n8n Workflow Generator | Natural language → n8n workflow JSON | A$0.05/call or A$39/mo | 8 hrs | A$500-2000 |

### Tech Stack

| Component | Tool | Cost |
|---|---|---|
| Hosting | Vercel (free tier: 100GB bandwidth) or Cloudflare Workers | A$0 |
| AI backend | OpenRouter (free models available) or local Ollama proxy | A$0 |
| Payment | Stripe Payment Links + Stripe Billing (subscriptions) | 1.75% + A$0.30 per AU transaction |
| API docs | README.md + Swagger/OpenAPI spec | A$0 |
| Domain | Namecheap (.com ~A$12/yr) | A$12/yr |

### Build Plan (Week 3-4 — after Lanes 1-2 are live)

| Day | Action | Time |
|---|---|---|
| 1 | Pick ONE API (recommend: YouTube Transcript Extractor — lowest effort) | — |
| 2 | Build the endpoint (FastAPI or Express, deploy to Vercel) | 3 hrs |
| 3 | Add Stripe payment link (A$19/mo subscription) | 1 hr |
| 4 | Write API docs + README | 2 hrs |
| 5 | List on RapidAPI, PublicAPIs.org, API directories | 2 hrs |
| 6 | Post on Reddit (r/webdev, r/SideProject), Product Hunt | 1 hr |
| 7 | Monitor usage, iterate | ongoing |

### Revenue Projection

| Month | Subscribers | Avg price | Revenue |
|---|---|---|---|
| Month 1 | 0-2 | A$19 | A$0-38 |
| Month 3 | 5-15 | A$19 | A$95-285 |
| Month 6 | 20-50 | A$25 | A$500-1250 |
| Month 12 | 50-200 | A$30 | A$1500-6000 |

> **This is the highest-revenue lane long-term.** API services compound: every new subscriber is recurring revenue with near-zero marginal cost.

---

## Lane 5: Crypto Yield + Arbitrage (EXISTING — GO LIVE WITH CAPITAL)

> **Status:** Code exists in `SLEEP_TRIPLE/opt_c_crypto_yield.py` · Observation-only · $0 capital
> **Zero approvals:** Public exchange APIs (CoinSpot, Kraken, Independent Reserve) — no approval for read; trading requires exchange account (instant signup for AU residents)
> **Capital:** A$500+ recommended (user decision)

### How It Works

```
23:15 → Orchestrator triggers opt_c
     → Scans CoinSpot, Kraken, Independent Reserve public tickers
     → Calculates USDC/AUD and USDT/AUD spreads
     → If spread > 50 bps AND capital available: emit signal
     → With --execute flag: places buy on low exchange, sell on high
     → Audit row + revenue event written
```

### Two Modes

| Mode | Behavior | Risk | Approval |
|---|---|---|---|
| **Observation (current)** | Logs spreads, writes $0 signal events | Zero | None needed |
| **Execution (opt-in)** | Places real trades when spread exceeds threshold | Capital at risk | Exchange account (instant AU signup) |

### Upgraded: Freqtrade Integration

The existing `opt_c` module does manual spread calculation. For serious crypto yield, integrate [Freqtrade](https://github.com/freqtrade/freqtrade) — the industry-standard open-source trading bot:

| Feature | Freqtrade provides |
|---|---|
| Strategy backtesting | Test strategies on historical data before risking capital |
| Machine learning | FreqAI module for ML-driven strategy adjustment |
| Telegram monitoring | Real-time trade notifications on your phone |
| Dry-run mode | Paper trade with real market data, zero risk |
| Multi-exchange | Binance, Kraken, Coinbase, KuCoin support |

### Build Plan (Month 2 — after Lanes 1-2 revenue confirmed)

| Step | Action | Time |
|---|---|---|
| 1 | Install Freqtrade: `pip install freqtrade` | 10 min |
| 2 | Configure for Kraken (AU-accessible, good liquidity) | 30 min |
| 3 | Run backtest with stablecoin pair strategy on 90 days of data | 1 hr |
| 4 | Run dry-run for 2 weeks (paper trade, monitor performance) | 2 weeks |
| 5 | If dry-run profitable: deposit A$500, switch to live | 30 min |
| 6 | Set Telegram bot for trade notifications | 15 min |
| 7 | Integrate into SLEEP_TRIPLE scheduler (runs 23:15-23:45) | 1 hr |

### Revenue Projection (Honest — Crypto Is Risky)

| Mode | Strategy | Monthly Range | Risk |
|---|---|---|---|
| Dry-run | Paper trading | A$0 (virtual) | None |
| Live (conservative) | Stablecoin arbitrage, A$500 capital | A$5-30 | Low (stablecoin spreads are small) |
| Live (moderate) | Grid trading on BTC/AUD, A$2000 capital | A$50-200 | Medium (crypto volatility) |

> **WARNING:** Crypto trading can lose money. Never invest more than you can afford to lose. Start with A$500 and dry-run for 2 weeks minimum. The ATO treats crypto gains as CGT events — track every disposal.

---

## Orchestrator Integration

All 5 lanes integrate into the existing SLEEP_TRIPLE sequential orchestrator:

### Updated Nightly Schedule

```
23:00 → opt_a_digital_factory.py --run --publish published
23:05 → opt_b_faceless_shorts.py --run --publish
23:10 → opt_e_pod.py --run --publish              (NEW — Lane 3)
23:15 → opt_c_crypto_yield.py --run --execute      (if capital > 0)
23:45 → Freqtrade dry-run cycle (if installed)      (NEW — Lane 5)
00:00 → opt_d_alerts.py --run --trigger morning_digest
07:00 → Morning digest to Discord/Telegram
```

### New Config File: `opt_e_config.json` (Lane 3 — POD)

```json
{
  "shopify_store_url": "YOUR_SHOPIFY_URL",
  "printful_api_key": "YOUR_PRINTFUL_KEY",
  "comfyui_url": "http://127.0.0.1:8188",
  "product_niches": ["ai_humor", "crypto_lifestyle", "dev_memes", "ai_art", "productivity"],
  "products_per_night": 1,
  "publish_mode": "draft_only",
  "enable_comfy_design": true
}
```

---

## GitHub Awesome Lists — Tools & Resources Deep Dive

### Core Awesome Lists (Actively Maintained)

| List | URL | Key Tools |
|---|---|---|
| **awesome-ai-agents** | `e2b-dev/awesome-ai-agents` | AutoGPT, BabyAGI, GPT-Engineer, CrewAI, OpenHands |
| **awesome-automation** | `croqaz/awesome-automation` | n8n, Activepieces, Airflow, Huginn |
| **awesome-browser-automation** | `angrykoala/awesome-browser-automation` | Playwright, Puppeteer, Selenium, Skyvern, Browser-Use |
| **awesome-crypto-trading-bots** | `botcrypto-io/awesome-crypto-trading-bots` | Freqtrade, Hummingbot, OctoBot, Jesse, Superalgos |
| **MakeMoneyWithAI** | `garylab/MakeMoneyWithAI` | Curated list of AI money-making tools by revenue stream |

### Recommended Tools by Lane

#### Lane 1-2 (Content Generation)

| Tool | Repo | Purpose | Why |
|---|---|---|---|
| **MoneyPrinterTurbo** | `FujiwaraChoki/MoneyPrinterTurbo` | Automated short-form video creation | Takes a prompt → script → stock footage → TTS → HD video. Designed for TikTok/Shorts/Reels. Could replace opt_b's manual pipeline. |
| **Ollama** | `ollama/ollama` | Local LLM inference | Already installed. Powers script generation, product text, prompt packs. Free. |
| **ComfyUI** | `comfyanonymous/ComfyUI` | Local image/video generation | Already installed at `C:\Users\karma\ComfyUI`. Powers cover art, design assets, POD designs. |

#### Lane 3 (Print-on-Demand)

| Tool | Service | Purpose |
|---|---|---|
| **Printful API** | printful.com | Auto-fulfillment (print, pack, ship) |
| **Shopify API** | shopify.com | Storefront + payment processing |
| **Gelato** | gelato.com | Alternative to Printful (global print network) |

#### Lane 4 (API-as-a-Service)

| Tool | Repo/Service | Purpose |
|---|---|---|
| **Vercel** | vercel.com | Free-tier serverless API hosting |
| **Cloudflare Workers** | cloudflare.com | Free-tier edge compute (100k requests/day) |
| **FastAPI** | `tiangolo/fastapi` | Python API framework (fast, auto-docs) |
| **Stripe** | stripe.com/au | AU payment processing (1.75% + A$0.30) |

#### Lane 5 (Crypto)

| Tool | Repo | Stars | Purpose |
|---|---|---|---|
| **Freqtrade** | `freqtrade/freqtrade` | ~30k | Leading open-source crypto trading bot |
| **Hummingbot** | `hummingbot/hummingbot` | ~15k | Market-making + DEX arbitrage |
| **CCXT** | `ccxt/ccxt` | ~32k | Unified crypto exchange API library (100+ exchanges) |
| **Jesse** | `jesse-ai/jesse` | ~6k | Modern Python trading framework |

#### Browser Automation (Cross-Lane)

| Tool | Repo | Purpose | Why |
|---|---|---|---|
| **Browser-Use** | `browser-use/browser-use` | AI-driven browser automation | State-of-the-art vision-to-action browser control. Can automate any web task: lead gen, competitor monitoring, auto-purchasing, form filling. |
| **Playwright** | `microsoft/playwright` | Reliable browser automation | Industry standard for headless web automation. The engine under many AI browser tools. |
| **Skyvern** | `Skyvern-AI/skyvern` | AI browser workflow automation | Specifically designed for dynamic web interfaces without custom selectors. |

### Autonomous Agent Frameworks (For Advanced Automation)

| Framework | Repo | Strength | Use Case |
|---|---|---|---|
| **CrewAI** | `crewai/crewai` | Multi-agent orchestration | Define Researcher → Writer → Publisher agents that work in a loop |
| **AutoGPT** | `Significant-Gravitas/AutoGPT` | Mature autonomous agent | Chain tasks: research → analyze → act → report |
| **OpenHands** | `All-Hands-AI/OpenHands` | Code-capable agent | Can write code, fix bugs, deploy services autonomously |
| **n8n** | `n8n-io/n8n` | Visual workflow automation | Connect APIs, databases, AI models without code. Self-hostable. Already in your stack. |

---

## Australian-Specific Considerations

### Payment Processing

| Processor | Fee (AU) | Setup | API Automation | Use For |
|---|---|---|---|---|
| **Stripe AU** | 1.75% + A$0.30 | Instant | Full API | SaaS subscriptions, one-time payments |
| **Gumroad** | 10% | Instant | API for product management | Digital products (handles GST/VAT) |
| **Shopify Payments** | 1.75% + A$0.30 | Needs ABN | Full API | Physical products (POD) |
| **PayID/PayTo** | Free | Bank account | Limited API | Bank-to-bank (no card fees) |
| **Crypto** | Network fee | Exchange account | Full API | Borderless, no chargebacks |

### Tax & Legal

| Obligation | Threshold | Action |
|---|---|---|
| **Declare income** | Any amount | Report on tax return as business income |
| **ABN** | Before invoicing AU businesses | Register at abr.gov.au (free, instant) |
| **GST registration** | A$75,000/yr turnover | Don't register yet. Revisit at A$6k/mo. |
| **CGT on crypto** | Every disposal | Track every crypto-to-fiat AND crypto-to-crypto trade |
| **ATO data matching** | All platforms | ATO receives earnings data from Gumroad, Stripe, YouTube, crypto exchanges |
| **Sole trader** | Until ~A$120k/yr | Simplest structure. No company setup needed yet. |

### Australia Timing Advantage (YouTube)

| Upload time (AEST) | Captures |
|---|---|
| 8 PM AEST | US morning (high traffic) |
| 6 AM AEST | US evening (high traffic) |
| 2 PM AEST | EU morning + Asia evening |

> **SLEEP_TRIPLE runs at 23:00 AEST** — uploads hit US afternoon + EU evening. This is NOT optimal for US peak traffic. Consider adding a second upload window at 06:00 AEST for US evening coverage.

---

## Revenue Summary by Lane

| Lane | Month 1 | Month 3 | Month 6 | Month 12 | Capital | Effort |
|---|---|---|---|---|---|---|
| 1 (Gumroad) | A$3 | A$7 | A$18 | A$50 | A$0 | Low (existing) |
| 2 (YouTube+Aff) | A$10 | A$100 | A$385 | A$1350 | A$0 | Medium (existing) |
| 3 (POD) | A$0 | A$10 | A$25 | A$51 | A$0/A$45 | Medium (new) |
| 4 (API SaaS) | A$20 | A$190 | A$875 | A$3750 | A$0 | High (new) |
| 5 (Crypto) | A$0 | A$15 | A$100 | A$200 | A$500+ | Medium (existing) |
| **TOTAL** | **A$33** | **A$322** | **A$1403** | **A$5401** | **A$500** | — |

> **Honest assessment:** These are conservative projections. Lane 4 (API SaaS) has the highest ceiling but requires the most work. Lanes 1-2 are fastest to go live because the code already exists. The critical path is: **go live with Lanes 1-2 on Day 1-3, then build Lane 4 in Weeks 3-4.**

---

## Implementation Priority

| Priority | Lane | First Action | Time to Revenue |
|---|---|---|---|
| 🔴 P0 | Lane 1 (Gumroad) | Create Gumroad account + add API key | Day 3 |
| 🔴 P0 | Lane 2 (YouTube) | Create channel + OAuth + TTS config | Day 3 |
| 🟠 P1 | Lane 4 (API SaaS) | Build first API endpoint (YouTube Transcript) | Week 4 |
| 🟡 P2 | Lane 3 (POD) | Sign up Shopify + Printful | Week 2 |
| 🟢 P3 | Lane 5 (Crypto) | Install Freqtrade + dry-run 2 weeks | Month 2 |

---

## Monitoring & Alerting

The existing `opt_d_alerts.py` provides multi-channel webhook alerting. Configure:

| Alert | Trigger | Channel | Content |
|---|---|---|---|
| Morning digest | 07:00 daily | Discord | Overnight production summary + revenue total |
| Actionable spread | opt_c spread > 100 bps | Telegram | Crypto arbitrage opportunity detected |
| Audit failure | Any module status=failed | Discord | System error with stack trace |
| Weekly rollup | Sun 23:55 | Discord | Week's revenue breakdown by lane |

### Alert Setup Checklist

- [ ] Create Discord webhook (Server Settings → Integrations → Webhooks)
- [ ] Set `DISCORD_WEBHOOK_URL` environment variable
- [ ] Create Telegram bot via @BotFather
- [ ] Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` environment variables
- [ ] Test: `python _live_send_test.py --channel discord`
- [ ] Test: `python _live_send_test.py --channel telegram`

---

## What This System Does NOT Do

- **Does not guarantee income.** These are revenue *opportunities*, not guarantees. Market conditions, product quality, and platform algorithms all affect results.
- **Does not avoid tax.** All income is declared to the ATO. The "zero approvals" constraint refers to platform onboarding, not tax compliance.
- **Does not run without monitoring.** The system runs autonomously, but you should check the morning digest daily and review weekly rollups.
- **Does not replace active income.** This is a supplement, not a replacement. Active consulting (MASTER_MONEY_PLAN.md) generates faster revenue.
- **Does not work without initial setup.** Each lane requires a one-time setup (account creation, API keys, config). After setup, it runs autonomously.

---

## Cross-References

| Document | Relevance |
|---|---|
| `SLEEP_TRIPLE/DOCUMENTATION.md` | Full technical reference for existing 4-module system |
| `SLEEP_TRIPLE/README.md` | How-to-run guide |
| `PASSIVE_INCOME_PLAN.md` | 4-lane passive income strategy (Lanes 1-4 complement this plan) |
| `MASTER_MONEY_PLAN.md` | Active income strategy (consulting/Fiverr) — runs in parallel |
| `FOOTCLAN_TO_REVENUE.md` | Footclan PR review service → A$300/mo pilot plan |
| `REAL_MONEY_PLAN_2026-06-25.md` | Conservative financial projections |
| 🔧 Reference Docs (NEW 2026-07-09) | [`REFERENCE_DOCS_INDEX.md`](REFERENCE_DOCS_INDEX.md) — hardware-shopping list, Sunshine+Moonlight setup, yt-dlp/transcript/ComfyUI video deep-dive, awesome-youtube repos catalogue |
| `FREEBUFF_SESSIONS_REVIEW.md` | History of all freebuff sessions that led to this plan |
| `OUTSTANDING_WORK_PLAN.md` | Plan to finish all incomplete session work |
| `COMPLIANCE_CHECKLIST.md` | Australian compliance (ABN, GST, invoicing) |
| `TAX_TIME_CHECKLIST.md` | EOFY tax preparation |

---

*End of SLEEP_CASH_SYSTEM.md*

> **Next action:** Go live with Lane 1 (Gumroad) and Lane 2 (YouTube) today. Both modules already exist in SLEEP_TRIPLE — they just need accounts created and config updated. Everything else can wait.
