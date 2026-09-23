#!/usr/bin/env python3
"""
opt_f_discovery.py — Option F: AI Money-Making App Discovery Engine.

Searches, evaluates, and builds monetizable app/platform/solution ideas using
OpenRouter free models + local Ollama. Integrates with SLEEP_TRIPLE orchestrator.

Capabilities:
  - Scans GitHub awesome lists, Reddit, Product Hunt, Indie Hackers for trends
  - Uses free OpenRouter models to analyze market fit, build difficulty, revenue potential
  - Generates executable build plans with code scaffolding
  - Validates ideas against real market data (where possible)
  - Outputs ranked opportunities to SLEEP_TRIPLE lanes (A-E) for execution

Zero approvals: Uses only free/public APIs + local AI
Capital: A$0 (all discovery is free)
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "opt_f_config.json"
AUDIT_LOG = ROOT / "SLEEP_TRIPLE_AUDIT.jsonl"
OUTBOX = ROOT / "outbox" / "f_discovery"

EXEC_STATUS = ("started", "ok", "degraded", "skipped", "refused", "noop", "failed")
SOURCE_ENUM = ("github_awesome", "reddit", "producthunt", "indiehackers", "youtube", "manual")
OPPORTUNITY_TYPE = ("saas", "digital_product", "content", "api_service", "affiliate", "pod", "crypto_tool")

# OpenRouter free models for different analysis tasks
FREE_MODELS = {
    "creative": "google/gemma-4-26b-a4b-it:free",
    "reasoning": "qwen/qwen3-next-80b-a3b-instruct:free",
    "coding": "poolside/laguna-s-2.1:free",
    "fast": "liquid/lfm-2.5-1.2b-instruct:free",
    "analysis": "nvidia/nemotron-3-ultra-550b-a55b:free",
}

RULE_8_FOLDERS = frozenset(
    ["Documents", "Downloads", "Pictures", "Videos", "Music", "Desktop",
     "OneDrive", "ARCHIVE_OLD"]
)


def is_rule_8(p: Path) -> bool:
    return bool({seg.name for seg in p.resolve().parents} & RULE_8_FOLDERS)


def load_config() -> dict:
    from env_bridge import load_config as _load
    return _load(CONFIG_PATH)


def load_master() -> dict:
    return json.loads((ROOT / "sleep_config.json").read_text(encoding="utf-8"))


def iso_now() -> str:
    tz = ZoneInfo("Australia/Sydney")
    return datetime.now(tz).isoformat()


def today_iso() -> str:
    tz = ZoneInfo("Australia/Sydney")
    return datetime.now(tz).date().isoformat()


def append_audit(row: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


# ---------------------------------------------------------------------------
# OpenRouter API Integration (free models only)
# ---------------------------------------------------------------------------

def openrouter_chat(model: str, messages: list, temperature: float = 0.7, max_tokens: int = 4096) -> str | None:
    """Call OpenRouter free model. Returns response text or None on failure."""
    api_key = load_config().get("openrouter_api_key", "")
    if not api_key or api_key.startswith("REPLACE"):
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/karma/SLEEP_TRIPLE",
            "X-Title": "SLEEP_TRIPLE Discovery Engine",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[opt_f] OpenRouter error ({model}): {e}", file=sys.stderr)
        return None


def ollama_generate(model: str, prompt: str) -> str:
    """Fallback to local Ollama if OpenRouter unavailable."""
    try:
        import subprocess
        # Truncate prompt if too long to avoid timeout
        if len(prompt) > 4000:
            prompt = prompt[:4000] + "..."
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=45
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        return f"[OLLAMA ERROR: {e}]"
    return "[OLLAMA FAILED]"


def ai_analyze(model_key: str, prompt: str, fallback_model: str = "ornith:9b") -> str:
    """Try OpenRouter first, fall back to Ollama."""
    model = FREE_MODELS.get(model_key, FREE_MODELS["reasoning"])
    result = openrouter_chat(model, [{"role": "user", "content": prompt}])
    if result:
        return result
    print(f"[opt_f] Falling back to Ollama ({fallback_model})", file=sys.stderr)
    return ollama_generate(fallback_model, prompt)


# ---------------------------------------------------------------------------
# Source Scanners (free/public sources only)
def scan_github_awesome(limit: int = 20) -> list:
    """Scan awesome lists for trending money-making tools."""
    awesome_lists = [
        "https://raw.githubusercontent.com/e2b-dev/awesome-ai-agents/main/README.md",
        "https://raw.githubusercontent.com/garylab/MakeMoneyWithAI/main/README.md",
        "https://raw.githubusercontent.com/croqaz/awesome-automation/main/README.md",
        "https://raw.githubusercontent.com/angrykoala/awesome-browser-automation/main/README.md",
        "https://raw.githubusercontent.com/botcrypto-io/awesome-crypto-trading-bots/main/README.md",
    ]

    opportunities = []
    for url in awesome_lists:
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
            # Extract project names and descriptions from markdown
            lines = content.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                # Match markdown links: - [Name](url) - Description
                if line.startswith("- [") and "](" in line and ")" in line:
                    # Parse the markdown link
                    try:
                        name_part = line.split("](")[0][2:]  # Get name between [ and ]
                        url_part = line.split("](")[1].split(")")[0]  # Get URL
                        desc_part = line.split(")")[-1].strip()
                        if desc_part.startswith("- "):
                            desc_part = desc_part[2:]
                        # Filter for money-making relevant projects
                        keywords = ["ai", "automation", "saas", "bot", "agent", "crypto", "trading", "money", "income", "revenue", "monetiz", "business", "startup", "tool", "api", "workflow", "n8n", "comfyui", "llm", "model", "generate", "content", "video", "image", "design", "code", "dev", "productivity", "marketing", "sales", "affiliate", "passive", "side hustle"]
                        text = f"{name_part} {desc_part}".lower()
                        if any(kw in text for kw in keywords):
                            opportunities.append({
                                "source": "github_awesome",
                                "name": name_part[:80],
                                "description": desc_part[:300],
                                "url": url_part,
                                "discovered_at": iso_now(),
                            })
                    except Exception:
                        pass
        except Exception as e:
            print(f"[opt_f] Failed to scan {url}: {e}", file=sys.stderr)

    return opportunities[:limit]


def scan_reddit_sources(limit: int = 10) -> list:
    """Scan Reddit for side hustle / AI money-making discussions (public JSON)."""
    subreddits = ["sidehustle", "Entrepreneur", "IndieHackers", "SaaS", "AI_Agents"]
    opportunities = []

    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=25"
            req = urllib.request.Request(url, headers={"User-Agent": "SLEEP_TRIPLE/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for post in data.get("data", {}).get("children", []):
                pdata = post.get("data", {})
                title = pdata.get("title", "")
                if any(kw in title.lower() for kw in ["ai", "automation", "saas", "passive", "side hustle", "money", "revenue", "mrr", "arr"]):
                    opportunities.append({
                        "source": "reddit",
                        "name": title[:80],
                        "description": pdata.get("selftext", "")[:300],
                        "url": f"https://reddit.com{pdata.get('permalink', '')}",
                        "score": pdata.get("score", 0),
                        "discovered_at": iso_now(),
                    })
        except Exception as e:
            print(f"[opt_f] Reddit scan failed for r/{sub}: {e}", file=sys.stderr)

    return sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)[:limit]


def scan_producthunt(limit: int = 10) -> list:
    """Scan Product Hunt for new AI/SaaS launches (public RSS/JSON)."""
    # Using public RSS feed
    try:
        url = "https://www.producthunt.com/feed"
        with urllib.request.urlopen(url, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
        # Simple XML parsing for titles/links
        import re
        items = re.findall(r"<item>.*?</item>", content, re.DOTALL)
        opportunities = []
        for item in items[:limit]:
            title_match = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", item)
            link_match = re.search(r"<link>(.*?)</link>", item)
            desc_match = re.search(r"<description><!\[CDATA\[(.*?)\]\]></description>", item)
            if title_match:
                opportunities.append({
                    "source": "producthunt",
                    "name": title_match.group(1)[:80],
                    "description": (desc_match.group(1)[:300] if desc_match else ""),
                    "url": link_match.group(1) if link_match else "",
                    "discovered_at": iso_now(),
                })
        return opportunities
    except Exception as e:
        print(f"[opt_f] Product Hunt scan failed: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# AI-Powered Analysis & Scoring
# ---------------------------------------------------------------------------

def analyze_opportunity(opp: dict, model_key: str = "analysis") -> dict:
    """Use AI to score opportunity on multiple dimensions."""
    # Try AI analysis only if OpenRouter key is configured
    cfg = load_config()
    has_openrouter = cfg.get("openrouter_api_key", "").strip() and not cfg.get("openrouter_api_key", "").startswith("REPLACE")
    
    if has_openrouter:
        prompt = f"""Analyze this money-making opportunity and return ONLY valid JSON:

Opportunity: {opp.get('name', '')}
Description: {opp.get('description', '')}
Source: {opp.get('source', '')}
URL: {opp.get('url', '')}

Score 1-10 on each dimension (10 = best):
1. market_demand: Real paying customers exist?
2. build_difficulty: How hard to build MVP? (10 = trivial, 1 = very hard)
3. revenue_potential: Monthly revenue ceiling at scale?
4. time_to_first_dollar: Days to first $1?
5. competition: How saturated? (10 = blue ocean, 1 = red ocean)
6. maintenance: Ongoing effort after launch? (10 = set-and-forget, 1 = high maintenance)
7. fits_my_skills: Matches Python/AI/automation/ComfyUI/n8n stack? (10 = perfect)
8. zero_approval: No platform approval needed? (10 = fully permissionless)

Return ONLY this JSON (no markdown, no extra text):
{{
  "scores": {{"market_demand": N, "build_difficulty": N, "revenue_potential": N, "time_to_first_dollar": N, "competition": N, "maintenance": N, "fits_my_skills": N, "zero_approval": N}},
  "weighted_total": N,
  "recommended_lane": "A|B|C|D|E|NEW",
  "mvp_plan": "3-step plan",
  "risks": ["risk1", "risk2"],
  "why": "2-sentence rationale"
}}"""

        result = ai_analyze(model_key, prompt)
        try:
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                analysis = json.loads(result[start:end])
                if "weighted_total" not in analysis and "scores" in analysis:
                    weights = {"market_demand": 1.5, "build_difficulty": 1.2, "revenue_potential": 1.5, "time_to_first_dollar": 1.0, "competition": 0.8, "maintenance": 0.8, "fits_my_skills": 1.3, "zero_approval": 1.0}
                    total = sum(analysis["scores"].get(k, 0) * w for k, w in weights.items())
                    analysis["weighted_total"] = round(total, 1)
                opp["analysis"] = analysis
                opp["weighted_score"] = analysis.get("weighted_total", 0)
                return opp
        except Exception as e:
            print(f"[opt_f] Analysis parse failed: {e}", file=sys.stderr)
    
    # Heuristic scoring fallback (fast, no API calls)
    scores = estimate_scores(opp)
    opp["analysis"] = {"scores": scores, "weighted_total": sum(scores.values()) * 0.1, "recommended_lane": recommend_lane(scores), "mvp_plan": "", "risks": [], "why": "Heuristic scoring"}
    opp["weighted_score"] = opp["analysis"]["weighted_total"]
    return opp


def estimate_scores(opp: dict) -> dict:
    """Heuristic scoring based on keywords when AI unavailable."""
    text = f"{opp.get('name', '')} {opp.get('description', '')}".lower()
    scores = {
        "market_demand": 5,
        "build_difficulty": 5,
        "revenue_potential": 5,
        "time_to_first_dollar": 5,
        "competition": 5,
        "maintenance": 5,
        "fits_my_skills": 5,
        "zero_approval": 5,
    }
    # Boost for relevant keywords
    if any(kw in text for kw in ["ai", "llm", "agent", "automation"]):
        scores["fits_my_skills"] = 8
        scores["market_demand"] = 7
    if any(kw in text for kw in ["saas", "api", "micro-saas", "subscription"]):
        scores["revenue_potential"] = 7
        scores["build_difficulty"] = 6
    if any(kw in text for kw in ["crypto", "trading", "yield", "arbitrage"]):
        scores["revenue_potential"] = 8
        scores["competition"] = 4
    if any(kw in text for kw in ["content", "video", "youtube", "shorts", "tiktok"]):
        scores["zero_approval"] = 9
        scores["time_to_first_dollar"] = 6
    if any(kw in text for kw in ["digital product", "gumroad", "course", "template", "prompt"]):
        scores["zero_approval"] = 10
        scores["time_to_first_dollar"] = 7
        scores["build_difficulty"] = 7
    if any(kw in text for kw in ["print on demand", "pod", "shopify", "printful", "merch"]):
        scores["zero_approval"] = 8
        scores["maintenance"] = 6
    if any(kw in text for kw in ["n8n", "workflow", "automation", "no-code", "low-code"]):
        scores["fits_my_skills"] = 9
        scores["build_difficulty"] = 7
    return scores


def recommend_lane(scores: dict) -> str:
    """Recommend SLEEP_TRIPLE lane based on scores."""
    # Lane A: Digital products (Gumroad) - high zero_approval, quick first dollar
    if scores["zero_approval"] >= 8 and scores["time_to_first_dollar"] >= 6:
        return "A"
    # Lane B: Content/YouTube - high zero_approval, content focus
    if scores["zero_approval"] >= 8 and scores["fits_my_skills"] >= 7:
        return "B"
    # Lane C: Crypto - high revenue_potential, crypto keywords
    if scores["revenue_potential"] >= 7:
        return "C"
    # Lane D: API SaaS - high revenue, subscription model
    if scores["revenue_potential"] >= 7 and scores["build_difficulty"] >= 5:
        return "D"
    # Lane E: POD - zero_approval, maintenance
    if scores["zero_approval"] >= 7 and scores["maintenance"] >= 5:
        return "E"
    return "NEW"


def generate_build_plan(opp: dict) -> dict:
    """Generate executable build plan with code scaffolding."""
    prompt = f"""Create a concrete build plan for this opportunity. Return JSON only.

Opportunity: {opp.get('name', '')}
Description: {opp.get('description', '')}
Recommended Lane: {opp.get('analysis', {}).get('recommended_lane', 'NEW')}
My Stack: Python, FastAPI, n8n, ComfyUI, Ollama, OpenRouter free models, Gumroad, YouTube, Printful, Shopify, crypto APIs

Return ONLY JSON:
{{
  "mvp_steps": [
    {{"step": 1, "task": "specific task", "tool": "python|n8n|comfyui|api", "time_hours": N, "output": "what gets produced"}},
    {{"step": 2, "task": "...", "tool": "...", "time_hours": N, "output": "..."}}
  ],
  "code_scaffold": {{
    "files": [
      {{"path": "project/main.py", "content": "starter code..."}},
      {{"path": "project/requirements.txt", "content": "deps..."}}
    ]
  }},
  "deployment": "vercel|render|local|docker",
  "monetization": "gumroad|stripe|affiliate|printful|ads",
  "first_dollar_checklist": ["item1", "item2"],
  "estimated_mvp_hours": N
}}"""

    result = ai_analyze("coding", prompt)
    try:
        start = result.find("{")
        end = result.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(result[start:end])
    except Exception:
        pass
    return {"mvp_steps": [], "code_scaffold": {"files": []}, "deployment": "local", "monetization": "none", "first_dollar_checklist": [], "estimated_mvp_hours": 0}


# ---------------------------------------------------------------------------
# Main Discovery Pipeline
# ---------------------------------------------------------------------------

def run_discovery(sources: list, max_per_source: int, dry_run: bool) -> list:
    """Run full discovery pipeline: scan -> analyze -> rank -> plan."""
    all_opportunities = []

    # Scan sources
    if "github_awesome" in sources:
        print("[opt_f] Scanning GitHub awesome lists...")
        all_opportunities.extend(scan_github_awesome(max_per_source))

    if "reddit" in sources:
        print("[opt_f] Scanning Reddit...")
        all_opportunities.extend(scan_reddit_sources(max_per_source))

    if "producthunt" in sources:
        print("[opt_f] Scanning Product Hunt...")
        all_opportunities.extend(scan_producthunt(max_per_source))

    print(f"[opt_f] Found {len(all_opportunities)} raw opportunities")

    # Analyze each
    analyzed = []
    for i, opp in enumerate(all_opportunities):
        print(f"[opt_f] Analyzing {i+1}/{len(all_opportunities)}: {opp.get('name', '')[:50]}")
        analyzed.append(analyze_opportunity(opp))
        if not dry_run:
            # Generate build plan for top candidates
            if opp.get("weighted_score", 0) >= 60:
                opp["build_plan"] = generate_build_plan(opp)

    # Rank by weighted score
    analyzed.sort(key=lambda x: x.get("weighted_score", 0), reverse=True)
    return analyzed


def save_results(opportunities: list, dry_run: bool) -> Path:
    """Save discovery results to outbox."""
    OUTBOX.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTBOX / f"discovery_{stamp}.json"

    result = {
        "generated_at": iso_now(),
        "dry_run": dry_run,
        "total_found": len(opportunities),
        "top_10": opportunities[:10],
        "by_lane": {},
    }

    # Group by recommended lane
    for opp in opportunities:
        lane = opp.get("analysis", {}).get("recommended_lane", "NEW")
        result["by_lane"].setdefault(lane, []).append({
            "name": opp.get("name"),
            "score": opp.get("weighted_score"),
            "url": opp.get("url"),
            "mvp_hours": opp.get("build_plan", {}).get("estimated_mvp_hours", 0),
        })

    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return out_path


def emit_lane_recommendations(opportunities: list, dry_run: bool) -> None:
    """Print actionable lane recommendations."""
    print("\n" + "=" * 60)
    print("SLEEP_TRIPLE LANE RECOMMENDATIONS")
    print("=" * 60)

    by_lane = {}
    for opp in opportunities:
        lane = opp.get("analysis", {}).get("recommended_lane", "NEW")
        by_lane.setdefault(lane, []).append(opp)

    for lane, opps in sorted(by_lane.items()):
        print(f"\n🎯 LANE {lane} ({len(opps)} opportunities)")
        for opp in opps[:3]:  # Top 3 per lane
            score = opp.get("weighted_score", 0)
            name = opp.get("name", "")[:50]
            plan = opp.get("build_plan", {})
            mvp_h = plan.get("estimated_mvp_hours", 0)
            monetization = plan.get("monetization", "?")
            print(f"  [{score:.0f}] {name} → {mvp_h}h MVP → {monetization}")
            if plan.get("first_dollar_checklist"):
                print(f"      First $: {plan['first_dollar_checklist'][0]}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Option F — AI Money-Making Discovery Engine")
    ap.add_argument("--dry-run", action="store_true", help="Scan and analyze only, no build plans (default)")
    ap.add_argument("--run", action="store_true", help="Generate build plans for high-score opportunities")
    ap.add_argument("--sources", nargs="+", default=["github_awesome", "reddit", "producthunt"],
                    choices=["github_awesome", "reddit", "producthunt", "all"],
                    help="Sources to scan")
    ap.add_argument("--max-per-source", type=int, default=15, help="Max opportunities per source")
    ap.add_argument("--min-score", type=int, default=50, help="Minimum weighted score to generate build plan")
    args = ap.parse_args()

    if args.dry_run and args.run:
        print("REFUSED: --dry-run and --run together", file=sys.stderr)
        return 5

    if is_rule_8(ROOT):
        print(f"REFUSED: ROOT path {ROOT} violates Rule #8 fence", file=sys.stderr)
        return 2

    cfg = load_config()
    master = load_master()
    dry_run = not args.run
    tz = ZoneInfo(master.get("tz", "Australia/Sydney"))
    now_iso = datetime.now(tz).isoformat()
    today = today_iso()

    sources = args.sources
    if "all" in sources:
        sources = ["github_awesome", "reddit", "producthunt"]

    append_audit({
        "ts": now_iso, "module": "opt_f", "slug": "opt_f_discovery",
        "status": "started", "task": "discover", "date": today,
        "dry_run": dry_run, "sources": sources, "max_per_source": args.max_per_source,
    })

    opportunities = run_discovery(sources, args.max_per_source, dry_run)

    # Filter by min score for build plans
    if not dry_run:
        opportunities = [o for o in opportunities if o.get("weighted_score", 0) >= args.min_score]

    out_path = save_results(opportunities, dry_run)

    append_audit({
        "ts": now_iso, "module": "opt_f", "slug": "opt_f_discovery",
        "status": "ok", "task": "discover", "date": today,
        "dry_run": dry_run, "opportunities_found": len(opportunities),
        "top_score": opportunities[0].get("weighted_score", 0) if opportunities else 0,
        "output_file": str(out_path),
    })

    emit_lane_recommendations(opportunities, dry_run)
    print(f"\n[opt_f] Results saved to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())