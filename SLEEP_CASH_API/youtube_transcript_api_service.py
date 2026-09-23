#!/usr/bin/env python3
"""
youtube_transcript_api_service.py — YouTube Transcript Extractor API.

Lane 4 of the SLEEP_CASH_SYSTEM. A micro-SaaS API endpoint that extracts
transcripts from any YouTube video. Designed for deployment on Vercel,
Cloudflare Workers, or local uvicorn.

Revenue model:
  - Free tier: 5 requests/day (IP-based rate limit)
  - Pro tier: A$19/mo via Stripe (unlimited requests)
  - API key passed via X-API-Key header for paid tier

Tech:
  - FastAPI + youtube-transcript-api
  - Dual storage backend: Redis (Vercel KV) when KV_URL is set, in-memory fallback otherwise
  - Stripe billing handled externally (Stripe Payment Link → webhook activates key)

Usage:
  Local:  python youtube_transcript_api_service.py
  Prod:   uvicorn youtube_transcript_api_service:app --host 0.0.0.0 --port 8000

Endpoints:
  GET  /                  — Health check + API info
  GET  /api/v1/transcript?video_id=XXX  — Extract transcript
  GET  /api/v1/transcript?video_id=XXX&format=json  — Structured JSON
  GET  /docs              — Auto-generated Swagger docs
"""

from __future__ import annotations

import json
import os
import secrets
import threading
import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

# youtube-transcript-api is installed (v1.2.2)
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, CouldNotRetrieveTranscript

# Proxy support for cloud deployments (Webshare, Bright Data, etc.)
WEBSHARE_PROXY_URL = os.environ.get("WEBSHARE_PROXY_URL", "").strip()

# KV store abstraction (Redis when Vercel KV is connected, in-memory fallback otherwise)
from kv_store import rate_limiter, api_key_store, cache

# Whisper fallback (Stage 3)
from whisper_fallback import transcribe_audio as whisper_transcribe

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FREE_TIER_DAILY_LIMIT = 5
RATE_LIMIT_WINDOW_HOURS = 24
STRIPE_PAYMENT_LINK = os.environ.get(
    "STRIPE_PAYMENT_LINK",
    "https://buy.stripe.com/REPLACE_WITH_YOUR_LINK_yt_transcript_pro",
)
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
STRIPE_WEBHOOK_ALLOW_UNSIGNED = os.environ.get(
    "STRIPE_WEBHOOK_ALLOW_UNSIGNED", ""
).strip().lower() in {"1", "true", "yes", "on"}
def _environment_values() -> set[str]:
    """Read all configured environment labels at decision time."""
    return {
        value.strip().lower()
        for value in (os.environ.get("APP_ENV", ""), os.environ.get("NODE_ENV", ""))
        if value.strip()
    }


_ENV_VALUES = _environment_values()
STRIPE_WEBHOOK_IS_DEVELOPMENT = bool(_ENV_VALUES) and _ENV_VALUES.issubset(
    {"dev", "development", "test", "testing", "local"}
)
STRIPE_WEBHOOK_EVENT_TTL_SECONDS = 72 * 3600
STRIPE_WEBHOOK_PROCESSING_TTL_SECONDS = 300

# ---------------------------------------------------------------------------
# Transcript extraction
# ---------------------------------------------------------------------------
_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _harvest_fallback_segments(video_id: str, language: str) -> list[dict]:
    """Fallback chain: invidious → piped → yt-dlp → whisper (via youtube_transcript_harvest)."""
    import sys

    root = _WORKSPACE_ROOT
    if root not in sys.path:
        sys.path.insert(0, root)
    from youtube_transcript_harvest import fetch_captions_real, load_harvest_config  # noqa: WPS433

    cfg = load_harvest_config()
    proxy = WEBSHARE_PROXY_URL or os.environ.get("YOUTUBE_HTTP_PROXY") or ""
    if proxy:
        cfg["http_proxy"] = proxy

    status, payload, _method = fetch_captions_real(video_id, language, cfg)
    if status != "ok":
        raise HTTPException(
            status_code=404,
            detail=f"All transcript methods failed ({status}): {payload if isinstance(payload, str) else payload}",
        )

    lines = payload if isinstance(payload, list) else [str(payload)]
    t = 0.0
    segments: list[dict] = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        segments.append({"text": text, "start": t, "duration": max(2.0, len(text.split()) * 0.35)})
        t += segments[-1]["duration"]
    return segments


def extract_transcript(video_id: str, languages: list[str] = None) -> list[dict]:
    """
    Extract transcript from a YouTube video.
    Returns list of {text, start, duration} dicts.
    Uses the v1.2.x API: YouTubeTranscriptApi.fetch() returns FetchedTranscript
    with .snippets (each having .text, .start, .duration).
    """
    if languages is None:
        languages = ["en", "en-US", "en-GB", "en-AU"]

    ytt_api = YouTubeTranscriptApi()
    try:
        fetched = ytt_api.fetch(video_id, languages=languages)
        # FetchedTranscript has .snippets — each FetchedTranscriptSnippet has .text, .start, .duration
        return [
            {"text": s.text, "start": s.start, "duration": s.duration}
            for s in fetched.snippets
        ]
    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="Transcripts are disabled for this video.")
    except NoTranscriptFound:
        # Try to list available transcripts
        try:
            available = ytt_api.list(video_id)
            langs = [t.language for t in available]
            raise HTTPException(
                status_code=404,
                detail=f"No transcript found in requested languages. Available: {', '.join(langs)}"
            )
        except Exception:
            raise HTTPException(status_code=404, detail="No transcript found for this video.")
    except VideoUnavailable:
        raise HTTPException(status_code=404, detail="Video is unavailable (private, deleted, or region-locked).")
    except CouldNotRetrieveTranscript:
        return _harvest_fallback_segments(video_id, languages[0])
    except Exception as e:
        err = str(e).lower()
        if "ip" in err and "block" in err:
            return _harvest_fallback_segments(video_id, languages[0])

        # Stage 3: Whisper fallback for any other unexpected errors
        try:
            print(f"Stage 1&2 failed, attempting Whisper fallback: {e}")
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            return whisper_transcribe(video_url, model="base.en", device="cpu", compute_type="int8")
        except Exception as whisper_err:
            raise HTTPException(status_code=500, detail=f"Transcript extraction failed (all stages): {str(e)} -> Whisper: {str(whisper_err)}")

def format_transcript_plain(segments: list[dict]) -> str:
    """Format transcript segments as plain text."""
    return "\n".join(seg["text"] for seg in segments)

def format_transcript_srt(segments: list[dict]) -> str:
    """Format transcript segments as SRT subtitles."""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = seg["start"]
        duration = seg.get("duration", 2.0)
        end = start + duration

        def to_srt_time(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        lines.append(str(i))
        lines.append(f"{to_srt_time(start)} --> {to_srt_time(end)}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines)


def compress_transcript(segments: list[dict], max_segment_chars: int = 500) -> list[dict]:
    """
    Compress adjacent short transcript segments into natural punctuation boundaries.
    Useful for long transcripts to reduce token usage and improve readability.
    """
    if not segments:
        return segments

    # First, merge adjacent segments that are very short and likely part of the same sentence
    merged = []
    current = dict(segments[0])

    for seg in segments[1:]:
        # If current segment is short and doesn't end with punctuation, merge with next
        if (len(current["text"]) < 100 and
            not current["text"].rstrip().endswith((".", "!", "?", "。", "！", "？")) and
            current["start"] + current["duration"] >= seg["start"] - 0.5):
            # Merge with next segment
            current["text"] = current["text"].rstrip() + " " + seg["text"].lstrip()
            current["duration"] = seg["start"] + seg["duration"] - current["start"]
        else:
            merged.append(current)
            current = dict(seg)
    merged.append(current)

    # Now split overly long segments at natural punctuation boundaries
    result = []
    for seg in merged:
        text = seg["text"].strip()
        if len(text) <= max_segment_chars:
            result.append(seg)
            continue

        # Split at punctuation boundaries
        import re
        # Split on sentence endings, keeping the punctuation
        parts = re.split(r'(?<=[.!?。！？])\s+', text)

        if len(parts) <= 1:
            # No natural split points, just keep as-is
            result.append(seg)
            continue

        # Distribute time proportionally across parts
        total_chars = sum(len(p) for p in parts)
        current_start = seg["start"]

        for part in parts:
            part = part.strip()
            if not part:
                continue
            part_duration = seg["duration"] * (len(part) / total_chars)
            result.append({
                "text": part,
                "start": current_start,
                "duration": part_duration
            })
            current_start += part_duration

    return result

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="YouTube Transcript Extractor API",
    description="Extract transcripts from any YouTube video. Free tier: 5 requests/day. Pro: A$19/mo.",
    version="1.0.0",
    contact={"name": "AusAI Tech", "url": "https://github.com/woodsai69rme"},
)

# CORS — allow browser-based API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check + API info."""
    return {
        "service": "YouTube Transcript Extractor API",
        "version": "1.0.0",
        "free_tier_limit": f"{FREE_TIER_DAILY_LIMIT} requests/24h",
        "pro_pricing": "A$19/month (unlimited)",
        "upgrade_url": STRIPE_PAYMENT_LINK,
        "endpoints": {
            "extract": "/api/v1/transcript?video_id=VIDEO_ID",
            "ingest_archon": "POST /api/v1/ingest/archon?video_id=VIDEO_ID (Pro key)",
            "pricing": "/pricing",
            "docs": "/docs",
            "health": "/healthz",
        },
        "usage": "Pass X-API-Key header or ?api_key= URL param for paid tier. Free tier is IP-rate-limited.",
    }


@app.get("/pricing", response_class=HTMLResponse)
async def pricing():
    """Public pricing page with Stripe checkout link."""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>YouTube Transcript API — A$19/mo Pro</title>
<style>
  body{{font-family:system-ui,sans-serif;background:#0a0e27;color:#f5f5fa;margin:0;padding:40px 20px}}
  .wrap{{max-width:720px;margin:0 auto}}
  h1{{font-size:2rem;margin:0 0 8px}}
  .sub{{color:#a0a5b4;margin-bottom:32px}}
  .card{{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:14px;padding:28px;margin-bottom:20px}}
  .price{{font-size:2.5rem;font-weight:700;color:#3cc8e6}}
  ul{{padding-left:20px;color:#c8cad4}}
  a.btn{{display:inline-block;background:#3cc8e6;color:#0a0e27;font-weight:700;padding:14px 28px;border-radius:10px;text-decoration:none;margin-top:16px}}
  code{{background:#000;padding:2px 6px;border-radius:4px}}
</style></head><body><div class="wrap">
<h1>YouTube Transcript API</h1>
<p class="sub">Extract transcripts from any YouTube video. Free: 5 requests/day. Pro: unlimited.</p>
<div class="card"><div class="price">A$19<span style="font-size:1rem;font-weight:400">/month</span></div>
<ul><li>Unlimited API requests</li><li>JSON, plain text, and SRT formats</li><li>API key via email after checkout</li><li>Swagger docs at <code>/docs</code></li></ul>
<a class="btn" href="{STRIPE_PAYMENT_LINK}">Subscribe — A$19/mo</a></div>
<p class="sub">Free tier: <code>GET /api/v1/transcript?video_id=VIDEO_ID</code> — no key required.</p>
</div></body></html>"""

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/v1/transcript")
def get_transcript(
    request: Request,
    video_id: str = Query(..., min_length=11, max_length=11, description="YouTube video ID (11 characters)"),
    format: str = Query("json", pattern="^(json|text|srt)$", description="Output format: json, text, or srt"),
    lang: str = Query("en", description="Preferred language code (e.g., en, es, fr)"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Extract transcript from a YouTube video.

    **Free tier:** 5 requests per 24 hours (IP-based). No API key needed.
    **Pro tier:** Unlimited requests. Pass X-API-Key header or ?api_key= URL param.

    **Formats:**
    - `json` (default): Array of {text, start, duration} segments
    - `text`: Plain text transcript
    - `srt`: SRT subtitle format
    """
    # Check API key for pro tier (header or URL param)
    api_key = x_api_key or request.query_params.get("api_key")
    is_pro = api_key_store.is_valid(api_key) if api_key else False

    # Rate limit only free tier
    if not is_pro:
        client_ip = request.client.host if request.client else "unknown"
        allowed, remaining = rate_limiter.check(client_ip, FREE_TIER_DAILY_LIMIT, RATE_LIMIT_WINDOW_HOURS)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Free tier limit: {FREE_TIER_DAILY_LIMIT} requests/24h. Upgrade to Pro for unlimited access.",
                    "upgrade_url": STRIPE_PAYMENT_LINK,
                    "reset_in_hours": RATE_LIMIT_WINDOW_HOURS,
                },
            )

    # Extract transcript — always include requested lang plus English fallbacks
    languages = [lang] + [l for l in ["en", "en-US", "en-GB", "en-AU"] if l != lang]

    # Check cache for 24h transcript result (segments only)
    cache_key = f"transcript:{video_id}:{lang}"
    cached = cache.get(cache_key)
    if cached is not None and isinstance(cached, list):
        segments = cached
    else:
        segments = extract_transcript(video_id, languages=languages)
        cache.set(cache_key, segments, ttl_seconds=24 * 3600)

    # Compress long transcripts (Pro tier only, free tier gets raw)
    if is_pro and len(segments) > 100:
        segments = compress_transcript(segments, max_segment_chars=500)

    # Format output
    if format == "text":
        content = format_transcript_plain(segments)
        return PlainTextResponse(content, media_type="text/plain")
    elif format == "srt":
        content = format_transcript_srt(segments)
        return PlainTextResponse(content, media_type="text/plain")
    else:
        return JSONResponse({
            "video_id": video_id,
            "language": lang,
            "segment_count": len(segments),
            "total_duration_seconds": sum(seg.get("duration", 0) for seg in segments),
            "transcript": segments,
        })

# ---------------------------------------------------------------------------
# Optional Archon ingest (push transcript into local knowledge base)
# ---------------------------------------------------------------------------
ARCHON_URL = os.environ.get("ARCHON_URL", "http://localhost:8181")
ARCHON_API_KEY = os.environ.get("ARCHON_VOICE_API_KEY", "local-voice-assistant")


@app.post("/api/v1/ingest/archon")
def ingest_transcript_to_archon(
    request: Request,
    video_id: str = Query(..., min_length=11, max_length=11, description="YouTube video ID"),
    lang: str = Query("en", description="Preferred language code"),
    title: str = Query("", description="Optional title hint for Archon upload filename"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Extract a transcript and upload it to the local Archon knowledge base.

    Requires Archon running on ARCHON_URL (default http://localhost:8181).
    Pro tier API key required. Pass X-API-Key header or ?api_key= URL param.
    """
    # Check API key for pro tier (header or URL param)
    api_key = x_api_key or request.query_params.get("api_key")
    is_pro = api_key_store.is_valid(api_key) if api_key else False
    if not is_pro:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Archon ingest requires Pro API key",
                "upgrade_url": STRIPE_PAYMENT_LINK,
            },
        )

    languages = [lang] + [l for l in ["en", "en-US", "en-GB", "en-AU"] if l != lang]
    segments = extract_transcript(video_id, languages=languages)
    body = format_transcript_plain(segments)
    safe_title = (title or video_id).strip().replace("/", "-").replace("\\", "-")[:80]
    filename = f"{safe_title}_{video_id}.txt"

    try:
        import requests
    except ImportError:
        raise HTTPException(status_code=500, detail="requests package not installed")

    try:
        r = requests.post(
            f"{ARCHON_URL}/api/documents/upload",
            files={"file": (filename, body.encode("utf-8"), "text/plain")},
            data={
                "knowledge_type": "technical",
                "tags": json.dumps(["youtube-harvest", "api-ingest"]),
            },
            headers={"X-API-Key": ARCHON_API_KEY},
            timeout=120,
        )
    except requests.exceptions.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Archon upload failed: {exc}")

    if not r.ok:
        raise HTTPException(status_code=502, detail=f"Archon returned {r.status_code}: {r.text[:300]}")

    payload = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    return {
        "success": True,
        "video_id": video_id,
        "archon_url": ARCHON_URL,
        "filename": filename,
        "segment_count": len(segments),
        "progress_id": payload.get("progressId"),
    }


def _generate_api_key() -> str:
    """Generate a cryptographically random API key for a new Pro customer.

    Existing keys remain valid; this only controls keys issued by future
    successful checkout webhooks.
    """
    return f"ytx_{secrets.token_hex(32)}"


def _webhook_event_cache_key(event_id: str) -> str:
    """Return the namespaced cache key used for webhook deduplication."""
    return f"stripe:webhook:event:{event_id}"


def _is_production_environment() -> bool:
    """Return whether any configured environment value is production."""
    return bool(_environment_values().intersection({"prod", "production"}))


def _is_development_environment() -> bool:
    """Return whether all configured environment values are local/test values."""
    values = _environment_values()
    if values:
        return values.issubset({"dev", "development", "test", "testing", "local"})
    return STRIPE_WEBHOOK_IS_DEVELOPMENT


def _start_webhook_lease_renewal(
    cache_key: str,
    claim: dict,
) -> tuple[threading.Event, threading.Event]:
    """Renew a webhook processing claim until the handler finishes.

    The renewal runs in a daemon thread because webhook business operations
    are synchronous. The second event is set if the owner can no longer renew
    its claim; callers should stop before beginning a new side effect when it
    is set. Conditional cache updates ensure a stale worker cannot renew a
    newer worker's claim.
    """
    stop_event = threading.Event()
    lease_lost = threading.Event()
    interval = max(1, STRIPE_WEBHOOK_PROCESSING_TTL_SECONDS // 3)

    def _renew() -> None:
        while not stop_event.wait(interval):
            try:
                renewed = cache.set_if_value(
                    cache_key,
                    claim,
                    claim,
                    STRIPE_WEBHOOK_PROCESSING_TTL_SECONDS,
                )
            except Exception:
                renewed = False
            if not renewed:
                lease_lost.set()
                return

    threading.Thread(target=_renew, name="stripe-webhook-lease", daemon=True).start()
    return stop_event, lease_lost


def _require_webhook_lease(lease_lost: threading.Event) -> None:
    """Abort before a new side effect if this worker lost its claim."""
    if lease_lost.is_set():
        raise HTTPException(
            status_code=409,
            detail="Stripe webhook processing lease is no longer owned",
        )


def _complete_webhook_claim(
    cache_key: str,
    claim: dict,
    lease_lost: threading.Event,
) -> None:
    """Commit completion only while this worker still owns the claim."""
    _require_webhook_lease(lease_lost)
    completed = cache.set_if_value(
        cache_key,
        claim,
        {"status": "completed"},
        STRIPE_WEBHOOK_EVENT_TTL_SECONDS,
    )
    if not completed:
        raise HTTPException(
            status_code=409,
            detail="Stripe webhook processing lease is no longer owned",
        )


# ---------------------------------------------------------------------------
# Stripe webhook (for activating API keys after payment)
# ---------------------------------------------------------------------------
@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Stripe webhook endpoint. Called when a subscription is activated or cancelled.

    Signed Stripe webhooks are required by default. Unsigned JSON is accepted
    only when STRIPE_WEBHOOK_ALLOW_UNSIGNED is explicitly enabled for local
    development/testing and STRIPE_WEBHOOK_SECRET is absent.
    """
    raw_body = await request.body()
    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Invalid webhook event")

    event_id: Optional[str] = None
    if STRIPE_WEBHOOK_SECRET:
        try:
            import stripe
            sig = request.headers.get("Stripe-Signature", "")
            event = stripe.Webhook.construct_event(raw_body, sig, STRIPE_WEBHOOK_SECRET)
            event_type = event["type"]
            data = event["data"]["object"]
            event_id = event.get("id")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Stripe signature verification failed",
            )
        if not event_id:
            raise HTTPException(status_code=400, detail="Stripe event ID is missing")
    elif STRIPE_WEBHOOK_ALLOW_UNSIGNED and _is_development_environment() and not _is_production_environment():
        # Explicit local-development compatibility mode. Never enable this in
        # a public or production deployment. Fixtures without an ID are not
        # deduplicated because each request receives a unique development ID.
        event_type = body.get("type", "")
        data = body.get("data", {}).get("object", {})
        event_id = body.get("id") or f"dev_{secrets.token_hex(16)}"
    else:
        raise HTTPException(
            status_code=503,
            detail="Stripe webhook verification is not configured",
        )

    if _is_production_environment() and not cache.is_durable():
        raise HTTPException(
            status_code=503,
            detail="Webhook replay protection storage is not configured",
        )

    cache_key = _webhook_event_cache_key(event_id)
    claim = {"status": "processing", "owner": secrets.token_hex(16)}
    if not cache.set_if_absent(
        cache_key,
        claim,
        STRIPE_WEBHOOK_PROCESSING_TTL_SECONDS,
    ):
        cached_event = cache.get(cache_key)
        if isinstance(cached_event, dict) and cached_event.get("status") == "completed":
            return {"status": "ignored", "reason": "duplicate", "event_id": event_id}
        raise HTTPException(
            status_code=409,
            detail="Stripe webhook event is already being processed",
        )

    lease_stop, lease_lost = _start_webhook_lease_renewal(cache_key, claim)
    try:
        _require_webhook_lease(lease_lost)
        if event_type == "checkout.session.completed":
            # New subscription — generate API key
            customer_email = data.get("customer_details", {}).get("email", "")
            api_key = api_key_store.get_key_by_event_id(event_id)
            if api_key is not None:
                _complete_webhook_claim(cache_key, claim, lease_lost)
                return {"status": "already_processed", "api_key": api_key}
            if api_key_store.has_event_id(event_id):
                _complete_webhook_claim(cache_key, claim, lease_lost)
                return {"status": "already_processed"}

            api_key = _generate_api_key()
            _require_webhook_lease(lease_lost)
            api_key_store.add_key(
                api_key,
                customer_email,
                data.get("customer", ""),
                stripe_event_id=event_id,
            )
            _require_webhook_lease(lease_lost)
            _complete_webhook_claim(cache_key, claim, lease_lost)
            return {"status": "activated", "api_key": api_key}

        if event_type == "customer.subscription.deleted":
            # Subscription cancelled — deactivate key
            _require_webhook_lease(lease_lost)
            customer_id = data.get("customer", "")
            api_key_store.deactivate_by_customer(customer_id)
            _require_webhook_lease(lease_lost)
            _complete_webhook_claim(cache_key, claim, lease_lost)
            return {"status": "deactivated"}

        _complete_webhook_claim(cache_key, claim, lease_lost)
        return {"status": "ignored", "event_type": event_type}
    except Exception:
        # Allow Stripe to retry if business processing fails after the claim,
        # but never remove a newer retry's claim.
        cache.delete_if_value(cache_key, claim)
        raise
    finally:
        lease_stop.set()

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
