import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import http.server
import socketserver
import webbrowser
import json
import subprocess
import requests
import time
import threading
import zipfile
import glob

from wigolo_engine import WigoloSearchEngine
from model_health import check_model_health
from trend_scraper import get_live_market_trends
from stripe_simulator import simulate_payment_event
from real_app_harvester import harvest_real_monetizable_apps
from marketing_engine import generate_marketing_campaign
from domain_scanner import scan_domain_variations
from qa_auditor import audit_codebase
from voice_generator import generate_voiceover, AVAILABLE_VOICES

import database

PORT = 3188
API_KEY = os.environ.get("OPENROUTER_API_KEY", "REDACTED_API_KEY")
wigolo_search = WigoloSearchEngine()

KNOWLEDGE_DOCS = [
    {
        "id": "doc-overview",
        "title": "⚡ AutoMonetize AI Pro Studio Architecture & Master Guide",
        "category": "Architecture & Specs",
        "filename": "DOCUMENTATION_AUTOMONETIZE_AI.md"
    },
    {
        "id": "doc-review",
        "title": "📋 Architectural Review & Strategic Advisory (August 2026)",
        "category": "Audit & Review",
        "filename": "AUTOMONETIZE_AI_PRO_REVIEW_AND_ADVISORY.md"
    },
    {
        "id": "doc-audio-video",
        "title": "🎙️ Trending Audio/Video Workflows: Kokoro-82M, F5-TTS, Wan 2.2 & n8n",
        "category": "Audio & Video AI",
        "filename": "RESEARCH_TRENDING_AUDIO_VIDEO_WORKFLOWS_2026.md"
    },
    {
        "id": "doc-awesome-lists",
        "title": "⭐ Awesome Lists & Community Monetization Trends 2026",
        "category": "Community Trends",
        "filename": "RESEARCH_AWESOME_LISTS_COMMUNITY_TRENDS_2026.md"
    },
    {
        "id": "doc-models-commerce",
        "title": "🧠 Free Frontier Models, Nemotron 3, Kimi K3 & Stripe Agentic Commerce",
        "category": "Model Intelligence",
        "filename": "RESEARCH_NEW_MODELS_AGENTIC_MONETIZATION_2026.md"
    },
    {
        "id": "doc-lumen",
        "title": "🚀 Lumen: 7-Agent Autonomous YouTube Channel Automation System",
        "category": "Autonomous Agents",
        "filename": "LUMEN_YOUTUBE_AUTOMATION_AGENT_GUIDE.md"
    }
]

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        elif self.path == '/api/trends/live':
            try:
                trends = get_live_market_trends()
                self.send_json_response(200, {"success": True, "trends": trends})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e), "trends": []})
                return
        elif self.path == '/api/apps/harvest':
            try:
                apps = harvest_real_monetizable_apps()
                self.send_json_response(200, {"success": True, "apps": apps})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e), "apps": []})
                return
        elif self.path == '/api/audio/voices':
            self.send_json_response(200, {"success": True, "voices": AVAILABLE_VOICES})
            return
        elif self.path == '/api/knowledge/docs':
            self.send_json_response(200, {"success": True, "docs": KNOWLEDGE_DOCS})
            return
        elif self.path == '/api/db/projects':
            try:
                projects = database.list_projects()
                self.send_json_response(200, {"success": True, "projects": projects})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e), "projects": []})
                return
        elif self.path == '/api/db/campaigns':
            try:
                campaigns = database.list_campaigns()
                self.send_json_response(200, {"success": True, "campaigns": campaigns})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e), "campaigns": []})
                return
        elif self.path == '/api/db/domains':
            try:
                domains = database.list_domain_watchlist()
                self.send_json_response(200, {"success": True, "domains": domains})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e), "domains": []})
                return
        super().do_GET()

    def do_POST(self):
        if self.path == '/api/audio/generate':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            text = data.get("text", "Discover, build, and monetize profitable software applications.")
            voice = data.get("voice", "en-US-ChristopherNeural")
            output_name = data.get("output_name", "audio_narration.mp3")
            
            try:
                audio_res = generate_voiceover(text, voice, output_name)
                self.send_json_response(200, audio_res)
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e)})
                return

        elif self.path == '/api/knowledge/read':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            doc_id = data.get("doc_id", "doc-overview")
            
            target_doc = next((d for d in KNOWLEDGE_DOCS if d["id"] == doc_id), None)
            if not target_doc:
                self.send_json_response(404, {"success": False, "error": "Document not found"})
                return
            
            # Look in current directory or parent directory
            fn = target_doc["filename"]
            p1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), fn)
            p2 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), fn)
            p3 = os.path.join("C:\\Users\\karma", fn)
            
            filepath = p1 if os.path.exists(p1) else (p2 if os.path.exists(p2) else p3)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                self.send_json_response(200, {"success": True, "doc": target_doc, "content": content})
            else:
                self.send_json_response(200, {"success": True, "doc": target_doc, "content": f"# {target_doc['title']}\n\n*Document loaded from vault index.*"})
            return

        elif self.path == '/api/db/save_project':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            
            try:
                pid = database.save_project(
                    title=data.get("title", "Untitled Micro-SaaS"),
                    niche=data.get("niche", "Developer Utility"),
                    pricing_model=data.get("pricing_model", "$19/mo"),
                    estimated_mrr=data.get("estimated_mrr", "$3,500/mo"),
                    html_code=data.get("html_code", ""),
                    css_code=data.get("css_code", ""),
                    js_code=data.get("js_code", ""),
                    qa_score=data.get("qa_score", 100),
                    notes=data.get("notes", "")
                )
                self.send_json_response(200, {"success": True, "project_id": pid})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e)})
                return

        elif self.path == '/api/db/delete_project':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            pid = data.get("id")
            
            try:
                database.delete_project(pid)
                self.send_json_response(200, {"success": True})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e)})
                return

        elif self.path == '/api/db/save_campaign':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            
            try:
                cid = database.save_campaign(
                    app_name=data.get("app_name", "App"),
                    target_audience=data.get("target_audience", "Audience"),
                    campaign_data=data.get("campaign", {})
                )
                self.send_json_response(200, {"success": True, "campaign_id": cid})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e)})
                return

        elif self.path == '/api/db/save_domain':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            
            try:
                database.save_domain_watchlist(
                    domain=data.get("domain", ""),
                    status=data.get("status", "AVAILABLE"),
                    price_estimate=data.get("price_estimate", "$0.99"),
                    category=data.get("category", "General")
                )
                self.send_json_response(200, {"success": True})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e)})
                return

        elif self.path == '/api/export/bundle_zip':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            
            title = data.get("title", "MyMonetizedApp")
            html = data.get("html", "<!DOCTYPE html><html><body><h1>Hello</h1></body></html>")
            css = data.get("css", "body { font-family: sans-serif; }")
            js = data.get("js", "console.log('App loaded');")
            marketing = data.get("marketing", {})
            stripe_link = data.get("stripe_link", "https://buy.stripe.com/demo")
            
            zip_filename = "app_bundle.zip"
            zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), zip_filename)
            
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.writestr("index.html", html)
                    zipf.writestr("style.css", css)
                    zipf.writestr("app.js", js)
                    zipf.writestr("stripe_config.json", json.dumps({"payment_link": stripe_link, "mode": "subscription"}, indent=2))
                    zipf.writestr("marketing_kit.json", json.dumps(marketing, indent=2))
                    
                    readme_content = f"""# {title} - Complete Production Package

Built and generated with AutoMonetize AI Pro Studio.

## Deployment Options:
1. **Netlify**: Drag and drop this folder directly into netlify.com/drop
2. **Vercel**: Run `npx vercel` inside this unzipped directory
3. **GitHub Pages**: Push files to `main` or `gh-pages` branch

## Monetization Configuration:
- Stripe Payment Link: {stripe_link}
- Pricing Mode: Subscription / Lifetime
"""
                    zipf.writestr("README.md", readme_content)
                    
                    # Include latest audio if exists
                    audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_narration.mp3")
                    if os.path.exists(audio_path):
                        zipf.write(audio_path, "audio_narration.mp3")
                
                self.send_json_response(200, {"success": True, "download_url": f"/{zip_filename}", "filename": zip_filename})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e)})
                return

        elif self.path == '/api/marketing/generate':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            app_name = data.get("app_name", "AI Lead Validator Micro-SaaS")
            target_audience = data.get("target_audience", "B2B Founders & Marketing Agencies")
            
            try:
                campaign = generate_marketing_campaign(app_name, target_audience)
                # Auto-save campaign to sqlite
                try: database.save_campaign(app_name, target_audience, campaign)
                except: pass
                self.send_json_response(200, {"success": True, "campaign": campaign})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e)})
                return

        elif self.path == '/api/domain/check':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            query = data.get("query", "autotool")
            
            try:
                report = scan_domain_variations(query)
                self.send_json_response(200, {"success": True, "report": report})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e)})
                return

        elif self.path == '/api/qa/audit':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            
            try:
                audit_result = audit_codebase(data)
                self.send_json_response(200, {"success": True, "audit": audit_result})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e)})
                return

        elif self.path == '/api/models/health':
            try:
                health_data = check_model_health()
                self.send_json_response(200, health_data)
                return
            except Exception as e:
                self.send_json_response(200, {"status": "error", "error": str(e)})
                return

        elif self.path == '/api/stripe/simulate':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            tier_idx = data.get("tier_idx", None)
            
            try:
                event = simulate_payment_event(tier_idx)
                self.send_json_response(200, {"success": True, "event": event})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e)})
                return

        elif self.path == '/api/swarm/run':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body)
            niche = data.get('niche', 'AI Automation Micro-SaaS')
            
            try:
                swarm_script = os.path.join(os.path.dirname(__file__), 'agent_swarm.py')
                result = subprocess.run([sys.executable, swarm_script, niche], capture_output=True, text=True, timeout=90)
                output_text = result.stdout if result.returncode == 0 else (result.stderr or result.stdout)
                
                self.send_json_response(200, {
                    "success": result.returncode == 0,
                    "output": output_text
                })
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "output": f"Swarm Execution Error: {str(e)}"})
                return

        elif self.path == '/api/wigolo/search':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body)
            query = data.get('query', 'monetizable AI app tools')
            
            try:
                results = wigolo_search.search_multi_engine(query)
                self.send_json_response(200, {"success": True, "query": query, "results": results})
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "error": str(e), "results": []})
                return

        elif self.path == '/api/run-browser-test':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            
            try:
                data = json.loads(body)
                target_url = data.get('target_url', 'http://localhost:3188')
                
                agent_script = os.path.join(os.path.dirname(__file__), 'browser_agent.py')
                result = subprocess.run([sys.executable, agent_script, target_url], capture_output=True, text=True, timeout=60)
                output_text = result.stdout if result.returncode == 0 else result.stderr
                
                self.send_json_response(200, {
                    "success": result.returncode == 0,
                    "output": output_text,
                    "screenshot": "/agent_screenshot.png"
                })
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "output": f"Error running browser test: {str(e)}"})
                return

        elif self.path == '/api/autopilot/trigger':
            try:
                cron_script = os.path.join(os.path.dirname(__file__), 'cron_engine.py')
                result = subprocess.run([sys.executable, cron_script], capture_output=True, text=True, timeout=120)
                output_text = result.stdout if result.returncode == 0 else (result.stderr or "Process returned non-zero exit code.")
                
                self.send_json_response(200, {
                    "success": result.returncode == 0,
                    "output": output_text
                })
                return
            except Exception as e:
                self.send_json_response(200, {"success": False, "output": f"Auto-Pilot Error: {str(e)}"})
                return

        elif self.path == '/api/arena/compare':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body)
            prompt = data.get('prompt', 'Invent a 1-sentence monetizable app idea.')
            
            models = ["openrouter/free", "nvidia/nemotron-3-ultra-550b:free", "google/gemma-4-31b-it:free"]
            results = []
            
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            for m in models:
                start_t = time.time()
                payload = {
                    "model": m,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150
                }
                try:
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=12)
                    elapsed = round((time.time() - start_t) * 1000, 2)
                    if res.status_code == 200:
                        res_json = res.json()
                        text = res_json.get("choices", [{}])[0].get("message", {}).get("content", "No output")
                        results.append({"model": m, "status": "SUCCESS", "latency_ms": elapsed, "output": text})
                    else:
                        results.append({"model": m, "status": f"HTTP {res.status_code}", "latency_ms": elapsed, "output": res.text[:150]})
                except Exception as ex:
                    results.append({"model": m, "status": "ERROR", "latency_ms": 0, "output": str(ex)})

            self.send_json_response(200, {"results": results})
            return

        super().do_POST()

    def send_json_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def open_browser_delayed():
    time.sleep(1)
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"==================================================", flush=True)
        print(f"  ⚡ AutoMonetize AI Studio Pro Live & Running", flush=True)
        print(f"  URL: http://localhost:{PORT}", flush=True)
        print(f"  Modules: Real Apps, Marketing, Domains, QA, Voice, Vault, DB", flush=True)
        print(f"==================================================", flush=True)
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except Exception as e:
            print(f"Server stopped: {e}", flush=True)

if __name__ == "__main__":
    run_server()
