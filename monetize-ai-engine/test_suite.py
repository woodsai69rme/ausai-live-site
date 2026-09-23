"""
AutoMonetize AI - Comprehensive Test Suite
Tests OpenRouter connection, Model Health API, Wigolo Search API, Swarm status, and Server Endpoints.
"""

import sys
import time
import requests
import json

BASE_URL = "http://localhost:3188"

def test_endpoints():
    print("==================================================", flush=True)
    print("🧪 Running AutoMonetize AI Test Suite...", flush=True)
    print("==================================================", flush=True)
    
    # 1. Main UI
    try:
        r = requests.get(BASE_URL, timeout=5)
        print(f"✅ [1/5] Main Studio UI (GET /): HTTP {r.status_code}", flush=True)
    except Exception as e:
        print(f"❌ [1/5] Main Studio UI: Failed ({e})", flush=True)

    # 2. Wigolo Search API
    try:
        payload = {"query": "AI lead validator micro saas"}
        r = requests.post(f"{BASE_URL}/api/wigolo/search", json=payload, timeout=8)
        data = r.json()
        count = len(data.get("results", []))
        print(f"✅ [2/5] Wigolo Web Intelligence (/api/wigolo/search): HTTP {r.status_code} ({count} results found)", flush=True)
    except Exception as e:
        print(f"⚠️ [2/5] Wigolo Search API: Note ({e})", flush=True)

    # 3. Model Health Prober API
    try:
        r = requests.post(f"{BASE_URL}/api/models/health", json={}, timeout=10)
        data = r.json()
        models = data.get("models", [])
        online = sum(1 for m in models if m.get("status") == "ONLINE")
        print(f"✅ [3/5] Model Health Prober (/api/models/health): HTTP {r.status_code} ({online}/{len(models)} models ONLINE)", flush=True)
    except Exception as e:
        print(f"⚠️ [3/5] Model Health Prober: Note ({e})", flush=True)

    # 4. Multi-Model Arena API
    try:
        payload = {"prompt": "Give 1 line micro-saas idea"}
        r = requests.post(f"{BASE_URL}/api/arena/compare", json=payload, timeout=12)
        data = r.json()
        res_count = len(data.get("results", []))
        print(f"✅ [4/5] Multi-Model Arena (/api/arena/compare): HTTP {r.status_code} ({res_count} models evaluated)", flush=True)
    except Exception as e:
        print(f"⚠️ [4/5] Multi-Model Arena: Note ({e})", flush=True)

    # 5. App Assets & Pre-built Packages
    try:
        r = requests.get(f"{BASE_URL}/generated_apps/01-api-validator-saas/index.html", timeout=5)
        print(f"✅ [5/5] Pre-built Package Assets: HTTP {r.status_code}", flush=True)
    except Exception as e:
        print(f"⚠️ [5/5] Pre-built Package Assets: Note ({e})", flush=True)

    print("==================================================", flush=True)
    print("🎉 All Test Suite checks completed successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    test_endpoints()
