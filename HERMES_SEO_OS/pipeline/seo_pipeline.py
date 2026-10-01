#!/usr/bin/env python3
"""
Hermes SEO OS pipeline — Julian Goldie–style SEO agent swarm (local-first).

Stages:
  keyword → outline → article → SEO pack → internal links → social → YouTube
  → outreach → publish plan → index checklist → QA

Usage:
  python HERMES_SEO_OS/pipeline/seo_pipeline.py --keyword "n8n consultant Australia"
  python HERMES_SEO_OS/pipeline/seo_pipeline.py --from-bank 0
  python HERMES_SEO_OS/pipeline/seo_pipeline.py --keyword "AI chatbot" --dry-run
  python HERMES_SEO_OS/pipeline/seo_pipeline.py --list-outbox
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path(r"C:\Users\karma")
sys.path.insert(0, str(WORKSPACE / "TOOLS"))

CONFIG_PATH = ROOT / "config.json"
MEMORY = ROOT / "memory"
OUTBOX = ROOT / "outbox"
BRAND_PATH = MEMORY / "BRAND_VOICE.md"
BANK_PATH = MEMORY / "KEYWORD_BANK.json"


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_brand() -> str:
    return BRAND_PATH.read_text(encoding="utf-8") if BRAND_PATH.is_file() else "AusAI Tech"


def load_bank() -> dict[str, Any]:
    if BANK_PATH.is_file():
        return json.loads(BANK_PATH.read_text(encoding="utf-8"))
    return {"seed_keywords": []}


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s[:80].strip("-") or "post"


def llm(prompt: str, system: str, cfg: dict[str, Any], max_chars: int = 12000) -> str:
    """Ollama primary → OpenRouter free fallback via core_llm if available."""
    model = cfg.get("llm", {}).get("ollama_model", "qwen2.5-coder:latest")
    try:
        from core_llm import chat as llm_chat

        return llm_chat(prompt[:max_chars], system=system[:4000], model=model)
    except Exception:
        pass

    # Direct Ollama
    import urllib.request

    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system[:4000]},
                {"role": "user", "content": prompt[:max_chars]},
            ],
            "stream": False,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return (data.get("message") or {}).get("content") or data.get("response") or ""
    except Exception as exc:
        return f"[LLM unavailable: {exc}]\n\nDraft placeholder for: {prompt[:200]}"


def stage_dir(keyword: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    d = OUTBOX / f"{stamp}__{slugify(keyword)}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def run_pipeline(keyword: str, cfg: dict[str, Any], dry_run: bool = False) -> Path:
    brand = load_brand()
    out = stage_dir(keyword)
    meta = {
        "keyword": keyword,
        "started": datetime.now().isoformat(timespec="seconds"),
        "brand": cfg.get("brand"),
        "site_url": cfg.get("site_url"),
        "dry_run": dry_run,
        "stages": [],
    }

    def mark(name: str, ok: bool = True, note: str = "") -> None:
        meta["stages"].append({"name": name, "ok": ok, "note": note, "ts": time.time()})
        print(f"  [{'OK' if ok else '!!'}] {name}" + (f" — {note}" if note else ""))

    print(f"\n=== Hermes SEO OS pipeline ===")
    print(f"Keyword: {keyword}")
    print(f"Outbox:  {out}")
    if dry_run:
        write(out / "00_dry_run.txt", f"Dry-run for: {keyword}\nNo LLM calls.")
        write(out / "manifest.json", json.dumps(meta, indent=2))
        mark("dry_run", True, "skipped LLM")
        return out

    # 1 Keyword scout
    sys_kw = "You are an Australian SEO keyword strategist. Return compact JSON only."
    prompt_kw = f"""Seed keyword: {keyword}

Expand into JSON:
{{
  "primary": "...",
  "long_tails": ["...", "...", "...", "...", "..."],
  "intent": "buyer|informational|comparison",
  "cluster": "...",
  "related_questions": ["...", "...", "..."]
}}
Focus on Australia / small business / AI automation where relevant."""
    raw_kw = llm(prompt_kw, sys_kw, cfg, max_chars=4000)
    write(out / "01_keywords.json", raw_kw)
    mark("keyword_scout")

    # 2 Outline
    sys_out = "You are an SEO content strategist. Produce a blog outline that can rank."
    prompt_out = f"""Keyword: {keyword}
Brand context:
{brand[:2500]}

Write a markdown outline with:
- Working title options (3)
- H1
- H2/H3 structure (8–12 sections)
- FAQ section (5 questions)
- CTA placement notes for AusAI Tech
Audience: Australian SMEs considering AI automation."""
    outline = llm(prompt_out, sys_out, cfg)
    write(out / "02_outline.md", outline)
    mark("serp_strategist")

    # 3–4 Content writer
    sys_w = (
        "You are a senior SEO copywriter for AusAI Tech (Australia). "
        "Write original, practical content. No fake statistics. Use AUD pricing only if from brand context. "
        "Markdown. Aim 1200+ words."
    )
    prompt_w = f"""Write a full blog post targeting: {keyword}

Use this outline:
{outline[:6000]}

Brand / offers / CTAs:
{brand[:3000]}

Rules:
- Natural keyword use (no stuffing)
- Australian spelling
- Include intro hook, practical steps, comparison table if relevant, FAQ, strong CTA
- Mention ausailive.vercel.app once as the site
- Do NOT invent client case-study numbers"""
    article = llm(prompt_w, sys_w, cfg, max_chars=14000)
    write(out / "03_article.md", article)
    mark("content_writer", note=f"{len(article.split())} words approx")

    # 5 SEO pack
    sys_seo = "Return JSON only for SEO metadata."
    prompt_seo = f"""From this article for keyword "{keyword}", produce JSON:
{{
  "title_tag": "max 60 chars",
  "meta_description": "max 155 chars",
  "slug": "url-slug",
  "h1": "...",
  "primary_keyword": "...",
  "secondary_keywords": ["..."],
  "faq": [{{"q":"...","a":"..."}}],
  "schema_types": ["Article","FAQPage"],
  "og_title": "...",
  "og_description": "..."
}}

Article excerpt:
{article[:5000]}"""
    seo_pack = llm(prompt_seo, sys_seo, cfg, max_chars=8000)
    write(out / "04_seo_pack.json", seo_pack)
    mark("seo_editor")

    # 6 Internal links
    links = f"""# Internal link map — {keyword}

## Site pages to link
- [AusAI home]({cfg.get('site_url')}/)
- [Services / checkout]({cfg.get('site_url')}/sales/checkout.html)
- [Book AI audit]({cfg.get('site_url')}/book.html)
- [FAQ]({cfg.get('site_url')}/faq.html)
- [Portfolio]({cfg.get('site_url')}/portfolio/)

## Anchor text ideas
1. AI automation consultant Australia
2. n8n automation bundle
3. custom AI chatbot setup
4. free AI audit

## Related future posts (cluster)
- Zapier vs Make vs n8n
- How to automate lead capture
- AI chatbot for small business

## Editor note
Add 3–5 contextual internal links inside `03_article.md` before publish.
"""
    write(out / "05_internal_links.md", links)
    mark("internal_linker")

    # 7 Social
    sys_soc = "You write high-conversion social posts. Australian tone. No fake metrics."
    prompt_soc = f"""Keyword: {keyword}
Create markdown with:
## LinkedIn (2 posts)
## Reddit (r/automation + r/smallbusiness style, value-first, not spammy)
## X / Twitter (3 tweets thread)
## Hook lines (5)

Article title/theme from:
{article[:2000]}
CTA: free AI audit or AusAI site."""
    social = llm(prompt_soc, sys_soc, cfg)
    write(out / "06_social.md", social)
    mark("social_clipper")

    # 8 YouTube
    sys_yt = "You write YouTube SEO scripts in Julian Goldie energy but truthful (no fake rank guarantees)."
    prompt_yt = f"""Keyword: {keyword}
Produce markdown:
## Shorts script (45–60 seconds, spoken)
## Long-form outline (8–12 min)
## Title options (5)
## Description (with CTA)
## Tags (12)
Theme: how AI agents / Hermes-style automation help SEO & business automation.
"""
    yt = llm(prompt_yt, sys_yt, cfg)
    write(out / "07_youtube.md", yt)
    mark("youtube_scripter")

    # 9 Outreach
    outreach = f"""# Backlink / outreach scout — {keyword}

## Target types
1. Australian small-business blogs accepting guest posts
2. n8n / automation community showcases
3. Local business directories & partner roundups
4. Podcast: AI / SMB Australia

## Pitch angle
- Practical automation (not tool spam)
- Free value: checklist or mini-workflow
- AusAI Tech as implementer, not "AI hype"

## Sample DM
Hi {{name}} — I put together a practical guide on {keyword} for AU small businesses
(no fluff). Happy to adapt it as a guest post or resource for your audience.
Site: {cfg.get('site_url')}

## Do not
- Mass spam
- Guarantee rankings
"""
    write(out / "08_outreach.md", outreach)
    mark("backlink_scout")

    # 10 Publish plan
    publish = f"""# Publish plan — {keyword}

## Mode: {cfg.get('publish', {}).get('mode', 'draft_outbox')}

### Checklist
- [ ] Human edit `03_article.md`
- [ ] Apply meta from `04_seo_pack.json`
- [ ] Add internal links from `05_internal_links.md`
- [ ] Add hero image (ComfyUI optional)
- [ ] Publish to site / CMS
- [ ] Submit URL in Google Search Console
- [ ] Share social pack (`06_social.md`)
- [ ] Schedule Shorts (`07_youtube.md`)

### Paths on this PC
- Draft folder: `{out}`
- Brand memory: `{BRAND_PATH}`
- Calendar: `{cfg.get('paths', {}).get('calendar')}`

### Optional Hermes CLI
```
cd hermes-agent
python hermes
# then: "Review and improve the article in {out / '03_article.md'}"
```
"""
    write(out / "09_publish.md", publish)
    mark("publisher")

    # 11 Index
    index_md = f"""# Indexing checklist — {keyword}

- [ ] Sitemap includes new URL
- [ ] robots.txt allows crawl
- [ ] Google Search Console → URL Inspection → Request indexing
- [ ] Bing Webmaster submit (optional)
- [ ] Internal links from 2 older pages
- [ ] Share on LinkedIn (crawl signal + traffic)
- [ ] Wait 3–14 days; check coverage

Target slug (edit after SEO pack):
`/{slugify(keyword)}`
"""
    write(out / "10_index.md", index_md)
    mark("indexer")

    # 12 QA
    sys_qa = "You are an E-E-A-T and SEO spam auditor. Be strict but practical."
    prompt_qa = f"""Audit this draft for:
- keyword stuffing
- thin content
- fake claims / invented stats
- missing CTA
- Australian relevance
- title/meta length issues if visible

Article:
{article[:7000]}

Return markdown: PASS/FAIL per section + top 5 edits.
"""
    qa = llm(prompt_qa, sys_qa, cfg)
    write(out / "11_qa.md", qa)
    mark("qa_auditor")

    # Master article bundle
    bundle = f"""---
keyword: {keyword}
generated: {meta['started']}
site: {cfg.get('site_url')}
status: draft
---

# {keyword.title()} — Draft Bundle

## Article
See `03_article.md`

## SEO
See `04_seo_pack.json`

## Social
See `06_social.md`

## Next human step
1. Edit article
2. Publish
3. Request indexing
"""
    write(out / "README.md", bundle)
    meta["finished"] = datetime.now().isoformat(timespec="seconds")
    meta["outbox"] = str(out)
    write(out / "manifest.json", json.dumps(meta, indent=2))
    print(f"\nDone → {out}")
    return out


def list_outbox() -> None:
    if not OUTBOX.is_dir():
        print("No outbox yet.")
        return
    rows = sorted([p for p in OUTBOX.iterdir() if p.is_dir()], reverse=True)
    if not rows:
        print("Outbox empty.")
        return
    print(f"{'Folder':<50} {'Has article':<12}")
    for p in rows[:30]:
        print(f"{p.name:<50} {'yes' if (p / '03_article.md').is_file() else 'no':<12}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes SEO OS pipeline")
    parser.add_argument("--keyword", "-k", help="Target keyword")
    parser.add_argument("--from-bank", type=int, help="Use seed keyword index from KEYWORD_BANK.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list-outbox", action="store_true")
    args = parser.parse_args()

    if args.list_outbox:
        list_outbox()
        return 0

    cfg = load_config()
    keyword = args.keyword
    if args.from_bank is not None:
        bank = load_bank()
        seeds = bank.get("seed_keywords") or []
        if args.from_bank < 0 or args.from_bank >= len(seeds):
            print(f"--from-bank out of range (0..{len(seeds)-1})")
            return 1
        keyword = seeds[args.from_bank]["kw"]
    if not keyword:
        print("Provide --keyword or --from-bank N")
        return 1

    run_pipeline(keyword, cfg, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
