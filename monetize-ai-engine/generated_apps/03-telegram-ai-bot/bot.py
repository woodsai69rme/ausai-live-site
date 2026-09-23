"""
Monetized Telegram AI Script Generator Bot
Powered by OpenRouter Free API & Telegram Bot Framework.
"""

import os
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "REDACTED_API_KEY")

def generate_script(topic):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": "You are a viral YouTube Shorts script writer."},
            {"role": "user", "content": f"Write a 30-second script for topic: {topic}"}
        ]
    }
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()["choices"][0]["message"]["content"]
    return "Error generating script. Please check subscription."

if __name__ == "__main__":
    print("Telegram Monetized Bot Framework initialized.")
    print("Test Generation for topic 'Passive Income AI':")
    print(generate_script("Passive Income AI"))
