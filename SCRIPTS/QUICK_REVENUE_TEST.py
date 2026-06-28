#!/usr/bin/env python3
"""
Quick Revenue Test - Generate sample content and revenue tracking
Uses local Ollama models if available
"""
import json
from datetime import datetime
from pathlib import Path

# Create revenue tracking entry
ledger_path = Path("C:/Users/karma/REVENUE_LEDGER.jsonl")
ledger_path.parent.mkdir(exist_ok=True)

# Sample content to generate
content_samples = {
    "affiliate_review": f"""# AI Trading Software Review

**Generated:** {datetime.now().isoformat()}

## Why AI Trading Tools Are Essential in 2025

Using artificial intelligence for trading has become mainstream. These tools:
- Analyze 1000s of assets in seconds
- Execute trades at optimal timing
- Learn from market patterns
- Work 24/7 without fatigue

**Recommended Tools:**
1. TradingAI.tech - Advanced signal analysis
2. AlphaMatrix Pro - Institutional-grade algorithms
3. AutoTrader AI - Hands-free trading automation

*[Your affiliate links here]*
""",

    "seo_article": f"""# Best AI Tools for Making Money Online 2025

## Complete Guide to AI-Powered Income Generation

In 2025, AI tools can generate substantial passive income through:
- Content automation
- Trading bots
- SaaS products
- Digital marketing

Start with free models from OpenRouter to avoid costs.
Scale to paid models once revenue validates the approach.
""",

    "social_media": """🚀 Unlock AI Trading Potential!
📈 Generate passive income with automated signals
🔓 No coding required - plug & play solutions
🎯 Start with $0 using free OpenRouter models
#AITrading #PassiveIncome #Crypto #Affiliate""",
}

# Write content to files
output_dir = Path("C:/Users/karma/revenue_content")
output_dir.mkdir(exist_ok=True)

for name, content in content_samples.items():
    file_path = output_dir / f"{name}.md"
    file_path.write_text(content, encoding='utf-8')
    print(f"[OK] Generated {file_path.name}")

    # Append to ledger
    ledger_entry = {
        "ts": datetime.utcnow().isoformat(),
        "event": "creative_published",
        "source": "QuickRevenueTest",
        "id": f"quick_{name}",
        "amount_usd": None,
        "meta": {"type": name, "ready_for": "deployment"}
    }
    with open(ledger_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ledger_entry) + '\n')

print(f"\n💰 Content saved to {output_dir}")
print(f"📊 Ledger updated at {ledger_path}")
print("\nNext: Configure OPENROUTER_API_KEY and run UNLIMITED_OPENROUTER_SYSTEM.py")