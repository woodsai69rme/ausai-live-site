import requests

API_KEY = "REDACTED_API_KEY"
URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "openrouter/free",
    "messages": [
        {"role": "user", "content": "Hello! Confirm API key functionality with a short 1-sentence greeting."}
    ],
    "max_tokens": 50
}

print(f"Testing key: {API_KEY[:10]}...{API_KEY[-5:]}")
res = requests.post(URL, headers=headers, json=payload, timeout=15)
print(f"Status Code: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    msg = data["choices"][0]["message"]["content"]
    model_used = data.get("model", "unknown")
    print(f"SUCCESS! Model used: {model_used}")
    print(f"Response: {msg.strip()}")
else:
    print(f"FAILED: {res.text}")
