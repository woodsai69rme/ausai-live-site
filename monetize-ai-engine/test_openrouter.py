import requests
import json
import os

API_KEY = "REDACTED_API_KEY"
URL = "https://openrouter.ai/api/v1/chat/completions"

models_to_test = [
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-r1:free",
    "qwen/qwen-2.5-coder-32b-instruct:free"
]

print("=== Testing OpenRouter Free Models ===")
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
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            print(f"SUCCESS [Status {response.status_code}]")
            print(f"Response: {content}")
        else:
            print(f"FAILED [Status {response.status_code}]: {response.text[:200]}")
    except Exception as e:
        print(f"ERROR: {e}")
