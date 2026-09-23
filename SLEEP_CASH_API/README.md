# YouTube Transcript Extractor API

> **Lane 4 of the SLEEP_CASH_SYSTEM** — API-as-a-Service micro-SaaS
> **Revenue:** A$19/month subscription via Stripe
> **Cost to run:** A$0 (Vercel free tier)

## Quick Start

```bash
# Local development
pip install -r requirements.txt
python youtube_transcript_api_service.py
# → API runs on http://localhost:8000

# View auto-generated docs
open http://localhost:8000/docs
```

## API Endpoints

| Endpoint | Method | Description | Auth |
|---|---|---|---|
| `/` | GET | Health check + API info | None |
| `/healthz` | GET | Simple health check | None |
| `/api/v1/transcript` | GET | Extract transcript from YouTube video | Free tier (IP-limited) or X-API-Key |
| `/webhook/stripe` | POST | Stripe webhook for subscription activation | Stripe signature (production) |
| `/docs` | GET | Swagger UI documentation | None |

## Usage Examples

### Free tier (no API key)
```bash
curl "http://localhost:8000/api/v1/transcript?video_id=dQw4w9WgXcQ"
```

### JSON format (default)
```bash
curl "http://localhost:8000/api/v1/transcript?video_id=dQw4w9WgXcQ&format=json"
```

### Plain text format
```bash
curl "http://localhost:8000/api/v1/transcript?video_id=dQw4w9WgXcQ&format=text"
```

### SRT subtitle format
```bash
curl "http://localhost:8000/api/v1/transcript?video_id=dQw4w9WgXcQ&format=srt"
```

### Pro tier (with API key)
```bash
curl -H "X-API-Key: ytx_user_1234567890" \
     "http://localhost:8000/api/v1/transcript?video_id=dQw4w9WgXcQ"
```

## Deploy to Vercel

1. Create a `vercel.json`:
```json
{
  "version": 2,
  "builds": [{"src": "youtube_transcript_api_service.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "youtube_transcript_api_service.py"}]
}
```

2. Deploy:
```bash
npm i -g vercel
vercel
```

3. Set environment variables in Vercel dashboard:
   - `KV_URL` or `REDIS_URL` — required for production replay protection and API-key persistence.
   - `STRIPE_WEBHOOK_SECRET` — required for signed webhook verification.

   Do not rely on `/tmp` or an `API_KEYS_FILE` for production persistence: Vercel
   serverless instances are ephemeral and may not share local files between
   invocations. Use the Redis/KV-backed store instead.

## Stripe Setup

1. Create a Stripe account (stripe.com/au — instant, no approval)
2. Create a Payment Link for A$19/mo subscription
3. Set webhook URL to `https://your-app.vercel.app/webhook/stripe`
4. Add webhook events: `checkout.session.completed`, `customer.subscription.deleted`
5. Set `STRIPE_WEBHOOK_SECRET` to the signing secret shown by Stripe.

The webhook rejects requests with HTTP 503 when verification is not configured.
For local-only unsigned JSON tests, set both `APP_ENV=development` (or
`NODE_ENV=test`) and `STRIPE_WEBHOOK_ALLOW_UNSIGNED=true`; never enable
unsigned mode on a public or production deployment. Signed webhooks do not
require this compatibility flag.

Webhook event IDs are claimed atomically for 72 hours using the Redis-backed
cache. Configure `KV_URL` or `REDIS_URL` in production; production webhooks
fail closed with HTTP 503 if shared replay-protection storage is unavailable.
This prevents duplicate Stripe deliveries from activating or deactivating
subscriptions twice. The processing claim is renewed while a handler runs;
failed processing releases the claim so Stripe can retry. A duplicate that
arrives while processing receives HTTP 409 and remains retryable.

## Rate Limits

| Tier | Limit | Auth |
|---|---|---|
| Free | 5 requests / 24 hours | IP-based |
| Pro | Unlimited | X-API-Key header |

## Revenue Projection

| Month | Subscribers | Revenue |
|---|---|---|
| Month 1 | 0-2 | A$0-38 |
| Month 3 | 5-15 | A$95-285 |
| Month 6 | 20-50 | A$380-950 |
| Month 12 | 50-200 | A$950-3800 |

## Marketing

1. List on RapidAPI marketplace
2. List on PublicAPIs.org
3. Post on Reddit: r/webdev, r/SideProject, r/learnpython
4. Post on Product Hunt
5. Add to GitHub README portfolio
