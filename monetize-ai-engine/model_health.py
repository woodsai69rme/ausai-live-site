"""
Live OpenRouter Free Model Health & Latency Prober - August 2026 Edition
Probes OpenRouter free models to measure HTTP status, latency (ms), and active status.
"""

import os
import sys
import json
import time
import requests

API_KEY = os.environ.get("OPENROUTER_API_KEY", "REDACTED_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

FREE_MODELS = [
    "openrouter/free",
    "nvidia/nemotron-3-ultra-550b:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-nano-30b:free",
    "openai/gpt-oss-20b:free",
    "dots3-note:free"
]

def check_model_health():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    report = []
    for model_id in FREE_MODELS:
        start_time = time.time()
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 10
        }
        try:
            res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=8)
            latency = round((time.time() - start_time) * 1000, 2)
            if res.status_code == 200:
                report.append({
                    "model": model_id,
                    "status": "ONLINE",
                    "latency_ms": latency,
                    "code": 200
                })
            else:
                report.append({
                    "model": model_id,
                    "status": "DEGRADED",
                    "latency_ms": latency,
                    "code": res.status_code
                })
        except Exception as e:
            report.append({
                "model": model_id,
                "status": "OFFLINE",
                "latency_ms": 0,
                "error": str(e)
            })

    return {"timestamp": time.time(), "models": report}

if __name__ == "__main__":
    result = check_model_health()
    print(json.dumps(result, indent=2))
