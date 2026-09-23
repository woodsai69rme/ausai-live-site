# SLEEP_CASH_GO_LIVE_CHECKLIST — What YOU Need To Do

> **Generated:** 2026-06-30
> **Purpose:** Everything I built is ready. These are the accounts and API keys you need to create manually to go live.

---

## What I Built (Done — No Action Needed From You)

| File | What It Does | Status |
|---|---|---|
| `SLEEP_TRIPLE/opt_e_pod.py` | Print-on-Demand module (Lane 3) — generates AI designs, publishes to Printful/Shopify | ✅ Built, dry-run tested |
| `SLEEP_TRIPLE/opt_e_config.json` | POD config with pricing, niches, placeholders | ✅ Built |
| `SLEEP_TRIPLE/sleep_orchestrator.py` | Updated to run 4 modules (added opt_e + --skip-e flag) | ✅ Updated, tested |
| `SLEEP_TRIPLE/sleep_config.json` | Added option "e" for POD | ✅ Updated, validated |
| `SLEEP_TRIPLE/opt_a_config.json` | Added gumroad_api_key placeholder, enabled ComfyUI covers | ✅ Updated, validated |
| `SLEEP_TRIPLE/opt_b_config.json` | Added YouTube OAuth path + TTS config (kept safe defaults) | ✅ Updated, validated |
| `SLEEP_CASH_API/youtube_transcript_api_service.py` | FastAPI micro-SaaS API (Lane 4) — YouTube transcript extractor | ✅ Built, syntax validated |
| `SLEEP_CASH_API/requirements.txt` | Python dependencies for the API | ✅ Built |
| `SLEEP_CASH_API/README.md` | API documentation + deployment guide | ✅ Built |
| `FREEBUFF_SESSIONS_REVIEW.md` | Full review of all 41 freebuff sessions | ✅ Written |
| `SLEEP_CASH_SYSTEM.md` | Master plan for 5-lane autonomous income system | ✅ Written |
| `OUTSTANDING_WORK_PLAN.md` | Plan to finish all incomplete session work | ✅ Written |

---

## What YOU Need To Do (Manual Actions)

### 🔴 P0 — Lane 1: Gumroad Go-Live (15 minutes)

| Step | Action | Where | What to put in config |
|---|---|---|---|
| 1 | Go to gumroad.com → Sign up (60 seconds, no approval) | Browser | — |
| 2 | Settings → Applications → Create API key | Browser | Copy the key |
| 3 | Edit `SLEEP_TRIPLE/opt_a_config.json` | File | Replace `REPLACE_WITH_GUMROAD_API_KEY` with your real key |
| 4 | Fill Gumroad W-8BEN form (one-time, non-US person) | Browser | — |
| 5 | Test: `python SLEEP_TRIPLE/opt_a_digital_factory.py --run --publish staged` | Terminal | Should publish a draft to Gumroad |
| 6 | Go live: Update Windows Task Scheduler to use `--run --publish published` | Terminal | `schtasks /change /tn SLEEP_TRIPLE\Nightly /tr "python sleep_orchestrator.py --run --force-window --publish published"` |

### 🔴 P0 — Lane 2: YouTube + TTS Go-Live (30 minutes)

| Step | Action | Where | What to put in config |
|---|---|---|---|
| 1 | Create a YouTube channel (google.com → YouTube → Create channel) | Browser | — |
| 2 | Go to Google Cloud Console → Enable YouTube Data API v3 | Browser | — |
| 3 | Create OAuth 2.0 credentials → Download JSON file | Browser | Save to e.g. `C:\Users\karma\SLEEP_TRIPLE\youtube_oauth.json` |
| 4 | Edit `SLEEP_TRIPLE/opt_b_config.json`: set `youtube_upload_dry_run` to `false` | File | Change `true` → `false` |
| 5 | Edit `SLEEP_TRIPLE/opt_b_config.json`: set `youtube_oauth_credentials_path` to your JSON path | File | Replace `REPLACE_WITH_YOUTUBE_OAUTH_JSON_PATH` |
| 6 | Install Coqui TTS: `pip install TTS` | Terminal | — |
| 7 | Edit `SLEEP_TRIPLE/opt_b_config.json`: set `voiceover_provider` to `"coqui"` and `coqui_installed` to `true` | File | — |
| 8 | Test: `python SLEEP_TRIPLE/opt_b_faceless_shorts.py --run --publish` | Terminal | Should upload first short |
| 9 | Sign up for affiliate programs (instant approval): Kraken, Binance, Hostinger, Crypto.com, Ledger, Persona | Browser | URLs already in config |

### 🟠 P1 — Lane 4: API SaaS Deploy (2 hours)

| Step | Action | Where |
|---|---|---|
| 1 | `cd SLEEP_CASH_API && pip install -r requirements.txt` | Terminal |
| 2 | Test locally: `python youtube_transcript_api_service.py` | Terminal |
| 3 | Open http://localhost:8000/docs to verify API works | Browser |
| 4 | ✅ **DONE** — Deployed to Vercel: https://yt-transcript-api-ebon.vercel.app | Terminal |
| 5 | Create Stripe account (stripe.com/au — instant) | Browser |
| 6 | Create a A$19/mo subscription Payment Link in Stripe | Browser |
| 7 | Set Stripe webhook URL to `https://your-app.vercel.app/webhook/stripe` | Browser |
| 8 | List API on RapidAPI, PublicAPIs.org | Browser |
| 9 | Post on Reddit (r/webdev, r/SideProject) | Browser |

### 🟡 P2 — Lane 3: Print-on-Demand Go-Live (1 hour)

| Step | Action | Where | What to put in config |
|---|---|---|---|
| 1 | Sign up Shopify (3-day free trial) | Browser | — |
| 2 | Sign up Printful, connect to Shopify | Browser | — |
| 3 | Get Printful API key from Settings → API | Browser | Copy key |
| 4 | Get Shopify Admin API token | Browser | Copy token |
| 5 | Edit `SLEEP_TRIPLE/opt_e_config.json` | File | Replace `REPLACE_WITH_SHOPIFY_URL`, `REPLACE_WITH_SHOPIFY_ADMIN_TOKEN`, `REPLACE_WITH_PRINTFUL_API_KEY` |
| 6 | Test: `python SLEEP_TRIPLE/opt_e_pod.py --run --publish staged` | Terminal | — |

### 🟢 P3 — Lane 5: Crypto Yield (Month 2, after revenue confirmed)

| Step | Action |
|---|---|
| 1 | `pip install freqtrade` |
| 2 | Configure for Kraken (AU-accessible) |
| 3 | Run backtest + 2-week dry-run |
| 4 | If profitable: deposit A$500, set `max_capital_aud: 500` in `opt_c_config.json` |
| 5 | Set `snapshot_only: false` in `opt_c_config.json` |

### ⚙️ — Alerting Setup (5 minutes)

| Step | Action |
|---|---|
| 1 | Create Discord webhook: Server Settings → Integrations → Webhooks → New Webhook → Copy URL |
| 2 | Set environment variable: `setx DISCORD_WEBHOOK_URL "your_webhook_url"` |
| 3 | Test: `python SLEEP_TRIPLE/_live_send_test.py --channel discord` |

### 📦 — GitHub Push (5 minutes, needs PAT)

| Step | Action |
|---|---|
| 1 | Go to github.com → Settings → Developer settings → Personal access tokens → Generate new token |
| 2 | `git remote set-url origin https://YOUR_TOKEN@github.com/woodsai69rme/ausai-live-site.git` |
| 3 | `git push origin master` |

### 🇦🇺 — Australian Compliance (before first dollar earned)

| Step | Action | Time | Cost |
|---|---|---|---|
| 1 | Register ABN at abr.gov.au | 15 min | Free |
| 2 | Open business bank account (ING, Up, NAB) | 30 min | Free |
| 3 | Set up tax set-aside (25-30% of every payment) | 10 min | Free |
| 4 | Do NOT register for GST yet (threshold: A$75k/yr) | — | — |

---

## Revenue Timeline After Go-Live

| Timeframe | If you complete P0 only | If you complete P0 + P1 | If you complete all |
|---|---|---|---|
| Week 1 | First Gumroad product live, first YouTube short uploaded | + API deployed, listed on directories | + Shopify store live |
| Month 1 | A$5-20 (affiliate clicks) | + A$0-38 (first API subscribers) | + A$0 (POD takes time) |
| Month 3 | A$50-150 | + A$95-285 | + A$10 (first POD sales) |
| Month 6 | A$220-550 | + A$380-950 | + A$25 |
| Month 12 | A$700-2000 | + A$950-3800 | + A$51 |

---

*End of SLEEP_CASH_GO_LIVE_CHECKLIST.md*
