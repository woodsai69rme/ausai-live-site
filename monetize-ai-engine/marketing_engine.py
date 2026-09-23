"""
Go-to-Market Marketing & Launch Campaign Engine for AutoMonetize AI
Generates cold email sequences, viral X/Twitter threads, Product Hunt launch kits, and programmatic SEO plans.
"""

import os
import sys
import json
import requests

API_KEY = os.environ.get("OPENROUTER_API_KEY", "REDACTED_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def generate_marketing_campaign(app_name="AutoForm Lead Validator", target_audience="B2B Founders & Marketing Agencies"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a world-class SaaS growth marketer. Generate a complete high-converting Go-to-Market marketing campaign for:
App Name: {app_name}
Target Audience: {target_audience}

Return JSON with exact keys:
1. "cold_email": {{
    "subject": "3 click-worthy subject lines (separated by /)",
    "body": "100-word personalized cold email focusing on pain point, solution, and low-friction CTA",
    "followup_1": "50-word quick bump follow-up email",
    "followup_2": "breakup email with value add"
   }}
2. "viral_x_thread": [
    "Tweet 1 (Hook with number & result)",
    "Tweet 2 (The problem with current solutions)",
    "Tweet 3 (How our tool fixes it)",
    "Tweet 4 (Behind the scenes / tech breakdown)",
    "Tweet 5 (CTA + Launch discount code)"
   ]
3. "product_hunt_kit": {{
    "tagline": "60-character punchy tagline",
    "maker_comment": "First comment explaining why you built it and offering a special promo",
    "day_1_checklist": ["Step 1", "Step 2", "Step 3", "Step 4"]
   }}
4. "seo_keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4", "keyword 5", "keyword 6"],
5. "affiliate_pitch": "50-word DM pitch offering 40% recurring lifetime commission to niche creators."
"""

    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": "You are an elite SaaS marketing director. Output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1200
    }

    try:
        res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        if res.status_code == 200:
            content = res.json()["choices"][0]["message"]["content"]
            # Clean possible markdown formatting
            clean_str = content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_str)
        else:
            return {"error": f"OpenRouter returned HTTP {res.status_code}"}
    except Exception as e:
        # Fallback structured template if offline
        return {
            "cold_email": {
                "subject": f"Quick question about your lead validation / {app_name} for your team / Fixing form drop-offs",
                "body": f"Hey {{firstName}},\n\nSaw you're running growth for {{company}}. Most teams lose 15-20% of inbound leads due to disposable emails and fake form inputs.\n\nWe built {app_name} to validate emails in real-time before they hit your CRM—saving ad spend and protecting domain reputation.\n\nMind if I send over a 2-minute sandbox link?\n\nBest,\nKarma",
                "followup_1": "Hey {{firstName}}, just bumping this in case it got buried under your inbox. Happy to set up a free trial for {{company}} if interested!",
                "followup_2": "Hey {{firstName}}, assuming this isn't a priority right now. If you ever need to clean fake signups, here's a free test API key. Cheers!"
            },
            "viral_x_thread": [
                f"🧵 1/5 I spent the last 48 hours building {app_name} to solve a $10,000/mo problem for indie hackers. Here's what happened:",
                "2/5 The problem: 24% of all web form signups are fake or throwaway disposable emails. You're paying for CRM contacts that will never convert.",
                f"3/5 Enter {app_name}: A lightweight 2-line JavaScript snippet that verifies domains, MX records, and spam lists in 45ms.",
                "4/5 Built completely with OpenRouter free models and FastAPI. Total hosting cost: $0/mo.",
                f"5/5 We are live! Check out the interactive demo and get 50% off lifetime access: https://buy.stripe.com/demo"
            ],
            "product_hunt_kit": {
                "tagline": f"Real-time lead verification & monetization utility for modern SaaS",
                "maker_comment": f"Hey Product Hunt! 👋 I built {app_name} because I was tired of bloated $199/mo enterprise tools. Today we're giving all PH hunters lifetime access for $29. Would love your feedback!",
                "day_1_checklist": [
                    "Post at 12:01 AM PST to maximize 24h voting window",
                    "Comment on all incoming questions within 5 minutes",
                    "Share link in IndieHackers, Reddit r/SideProject, and X",
                    "Send email blast to existing waitlist with direct PH link"
                ]
            },
            "seo_keywords": [
                f"best {app_name.lower()} alternative",
                "real time email validation api",
                "stop fake form signups shopify",
                "disposable email blocker javascript",
                "cheap lead validation tool 2026",
                "stripe automated micro saas template"
            ],
            "affiliate_pitch": f"Hey! Love your content on SaaS tools. We just launched {app_name} and are offering 40% recurring monthly commission for creators. Would love to send you a VIP access link!"
        }

if __name__ == "__main__":
    camp = generate_marketing_campaign()
    print(json.dumps(camp, indent=2))
