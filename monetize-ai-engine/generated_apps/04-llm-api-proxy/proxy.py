"""
High-Availability LLM API Rate Limiting Proxy & Monetization Middleware
Routes requests to OpenRouter free models, counts token credits, and enforces paid API keys.
"""

from fastapi import FastAPI, HTTPException, Header
import requests
import os

app = FastAPI(title="LLM API Proxy Middleware")

VALID_API_KEYS = {
    "sk-client-tier1": {"credits": 500, "plan": "Pro ($29/mo)"},
    "sk-client-tier2": {"credits": 5000, "plan": "Enterprise ($199/mo)"}
}

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "REDACTED_API_KEY")

@app.post("/v1/chat/completions")
def proxy_completion(payload: dict, x_api_key: str = Header(None)):
    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key. Upgrade your plan at https://your-monetized-proxy.com")

    client = VALID_API_KEYS[x_api_key]
    if client["credits"] <= 0:
        raise HTTPException(status_code=402, detail="Credit limit reached. Please top up your subscription.")

    # Deduct 1 credit
    client["credits"] -= 1

    # Proxy to OpenRouter Free Auto-Router
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    
    payload["model"] = "openrouter/free"
    res = requests.post(url, headers=headers, json=payload)
    return res.json()
