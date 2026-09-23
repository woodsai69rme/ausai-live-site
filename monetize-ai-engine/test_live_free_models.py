import requests
import json

API_KEY = "REDACTED_API_KEY"
URL = "https://openrouter.ai/api/v1/chat/completions"

models_to_test = [
    "openrouter/free",
    "openai/gpt-oss-20b:free",
    "inclusionai/ling-3.0-flash:free",
    "cohere/north-mini-code:free",
    "nvidia/nemotron-3-nano-30b-a3b:free"
]

print("=== Testing Live Active Free Models ===")
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "http://localhost:3188",
    "X-Title": "AutoMonetize AI Test",
    "Content-Type": "application/json"
}

for model in models_to_test:
    print(f"\nTesting Model: {model}")
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Invent a 1-sentence monetizable SaaS app idea targeting developer productivity."}
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=15)
        data = response.json() if response.content else {}
        if response.status_code == 200 and "choices" in data and len(data["choices"]) > 0:
            msg = data["choices"][0].get("message", {})
            content = msg.get("content", "")
            actual_model = data.get("model", model)
            print(f"✅ SUCCESS [200] (Actual Model: {actual_model})")
            print(f"Output: {content.strip()}")
        else:
            err_msg = data.get("error", {}).get("message", response.text[:150])
            print(f"❌ FAILED [{response.status_code}]: {err_msg}")
    except Exception as e:
        print(f"⚠️ ERROR: {e}")
