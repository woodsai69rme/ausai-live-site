"""
Autonomous Browser Agent powered by Playwright and OpenRouter Free AI Models.
Executes web navigation, page analysis, screenshot captures, and automated interactions.
"""

import asyncio
import os
import sys
import json
import requests
from playwright.async_api import async_playwright

API_KEY = os.environ.get("OPENROUTER_API_KEY", "REDACTED_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class AutonomousBrowserAgent:
    def __init__(self, target_url="http://localhost:3188", model="openrouter/free"):
        self.target_url = target_url
        self.model = model

    def query_ai_decision(self, prompt, context_text=""):
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "http://localhost:3188",
            "X-Title": "AutoBrowser Agent",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an autonomous browser agent. Analyze page state and return concise actionable steps or summary."},
                {"role": "user", "content": f"Task Prompt: {prompt}\nPage Context:\n{context_text[:1500]}"}
            ],
            "max_tokens": 500
        }

        try:
            res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                data = res.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "No AI response")
            return f"API Error HTTP {res.status_code}: {res.text[:200]}"
        except Exception as e:
            return f"Exception: {e}"

    async def run_session(self, task_instruction="Analyze landing page structure and verify primary monetization call to action"):
        print(f"==================================================")
        print(f"🤖 Launching Autonomous Browser Agent")
        print(f"   Target URL: {self.target_url}")
        print(f"   AI Model: {self.model}")
        print(f"==================================================")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                print(f"🌐 Navigating to {self.target_url}...")
                await page.goto(self.target_url, timeout=5000, wait_until="domcontentloaded")
            except Exception as nav_err:
                print(f"⚠️ Target URL unavailable. Opening local file directly...")
                await page.close()
                page = await context.new_page()
                index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html"))
                file_url = f"file:///{index_path.replace('\\', '/')}"
                await page.goto(file_url, wait_until="domcontentloaded")

            title = await page.title()
            content_text = await page.evaluate("document.body.innerText")
            
            print(f"✅ Page Loaded successfully! Title: '{title}'")
            
            screenshot_path = os.path.join(os.path.dirname(__file__), "agent_screenshot.png")
            await page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved to {screenshot_path}")
            
            print("🧠 Asking AI model to evaluate page state and monetization readiness...")
            ai_analysis = self.query_ai_decision(task_instruction, content_text)
            print(f"\n💡 AI Analysis & Action Plan:\n{ai_analysis}\n")
            
            await browser.close()
            return {
                "title": title,
                "screenshot": screenshot_path,
                "ai_analysis": ai_analysis
            }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3188"
    agent = AutonomousBrowserAgent(target_url=target)
    asyncio.run(agent.run_session())
