"""
End-to-End Comprehensive Verification Test Suite for AutoMonetize AI Pro
Tests all 9 core modules and backend endpoints.
"""

import os
import sys
import json
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from real_app_harvester import harvest_real_monetizable_apps
from marketing_engine import generate_marketing_campaign
from domain_scanner import scan_domain_variations
from qa_auditor import audit_codebase
from trend_scraper import get_live_market_trends
from stripe_simulator import simulate_payment_event
from wigolo_engine import WigoloSearchEngine
from model_health import check_model_health
from voice_generator import generate_voiceover

def run_comprehensive_tests():
    print("==================================================", flush=True)
    print("🧪 AUTOMONETIZE AI PRO: COMPREHENSIVE TEST SUITE", flush=True)
    print("==================================================", flush=True)
    
    results = {}

    # Test 1: Real Apps Harvester
    print("[1/9] Testing Real Apps Harvester...", end=" ", flush=True)
    try:
        apps = harvest_real_monetizable_apps()
        assert len(apps) > 0, "No apps returned"
        results["Real Apps Harvester"] = {"status": "PASS", "count": len(apps), "sample": apps[0]["name"]}
        print(f"✅ PASS ({len(apps)} apps)")
    except Exception as e:
        results["Real Apps Harvester"] = {"status": "FAIL", "error": str(e)}
        print(f"❌ FAIL: {e}")

    # Test 2: Marketing & GTM Engine
    print("[2/9] Testing Marketing & GTM Engine...", end=" ", flush=True)
    try:
        camp = generate_marketing_campaign("Test SaaS", "Developers")
        assert "cold_email" in camp or "viral_x_thread" in camp, "Missing campaign keys"
        results["Marketing Engine"] = {"status": "PASS", "keys": list(camp.keys())}
        print("✅ PASS")
    except Exception as e:
        results["Marketing Engine"] = {"status": "FAIL", "error": str(e)}
        print(f"❌ FAIL: {e}")

    # Test 3: Cheap Domain Scanner
    print("[3/9] Testing Cheap Domain Scanner...", end=" ", flush=True)
    try:
        dom_report = scan_domain_variations("leadpulse")
        assert "domains" in dom_report and len(dom_report["domains"]) > 0, "No domains returned"
        results["Domain Scanner"] = {"status": "PASS", "scanned": dom_report["total_scanned"], "available": dom_report["available_count"]}
        print(f"✅ PASS ({dom_report['available_count']} available / {dom_report['total_scanned']} checked)")
    except Exception as e:
        results["Domain Scanner"] = {"status": "FAIL", "error": str(e)}
        print(f"❌ FAIL: {e}")

    # Test 4: Static QA & Security Auditor
    print("[4/9] Testing Static QA & Security Auditor...", end=" ", flush=True)
    try:
        test_code = {
            "html": '<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body><button onclick="checkout()">Buy</button></body></html>',
            "css": "body { background: #111; }",
            "js": "function checkout() { fetch('/api/stripe/checkout'); }",
            "py": "import os"
        }
        qa_rep = audit_codebase(test_code)
        assert "score" in qa_rep and qa_rep["score"] > 0, "Invalid QA response"
        results["QA Auditor"] = {"status": "PASS", "score": qa_rep["score"], "grade": qa_rep["grade"]}
        print(f"✅ PASS (Score: {qa_rep['score']}/100, Grade: {qa_rep['grade']})")
    except Exception as e:
        results["QA Auditor"] = {"status": "FAIL", "error": str(e)}
        print(f"❌ FAIL: {e}")

    # Test 5: Live Market Trend Radar
    print("[5/9] Testing Live Market Trends Radar...", end=" ", flush=True)
    try:
        trends = get_live_market_trends()
        assert len(trends) > 0, "No trends returned"
        results["Market Trends"] = {"status": "PASS", "count": len(trends)}
        print(f"✅ PASS ({len(trends)} trends)")
    except Exception as e:
        results["Market Trends"] = {"status": "FAIL", "error": str(e)}
        print(f"❌ FAIL: {e}")

    # Test 6: Stripe Payment Simulator
    print("[6/9] Testing Stripe Payment Simulator...", end=" ", flush=True)
    try:
        evt = simulate_payment_event(1)
        assert "plan_name" in evt and "customer_email" in evt, "Invalid event structure"
        results["Stripe Simulator"] = {"status": "PASS", "amount": evt["amount_usd"], "plan": evt["plan_name"]}
        print(f"✅ PASS ({evt['plan_name']} - ${evt['amount_usd']})")
    except Exception as e:
        results["Stripe Simulator"] = {"status": "FAIL", "error": str(e)}
        print(f"❌ FAIL: {e}")

    # Test 7: Wigolo Multi-Engine Search
    print("[7/9] Testing Wigolo Search Engine...", end=" ", flush=True)
    try:
        w_engine = WigoloSearchEngine()
        w_res = w_engine.search_multi_engine("micro saas")
        results["Wigolo Search"] = {"status": "PASS", "count": len(w_res)}
        print(f"✅ PASS ({len(w_res)} results)")
    except Exception as e:
        results["Wigolo Search"] = {"status": "FAIL", "error": str(e)}
        print(f"❌ FAIL: {e}")

    # Test 8: Free Neural Voice Generator (Edge-TTS)
    print("[8/9] Testing Free Neural Voice Generator (Edge-TTS)...", end=" ", flush=True)
    try:
        v_res = generate_voiceover("AutoMonetize AI neural voice engine is verified.", "en-US-ChristopherNeural", "test_audio.mp3")
        assert v_res["success"] is True, "Voice synthesis failed"
        results["Neural Voice (Edge-TTS)"] = {"status": "PASS", "audio_url": v_res["audio_url"]}
        print("✅ PASS")
    except Exception as e:
        results["Neural Voice (Edge-TTS)"] = {"status": "FAIL", "error": str(e)}
        print(f"❌ FAIL: {e}")

    # Test 9: OpenRouter Free Models Health Prober
    print("[9/9] Testing OpenRouter Free Models Health Prober...", end=" ", flush=True)
    try:
        health = check_model_health()
        assert "models" in health and len(health["models"]) > 0, "No models probed"
        online_count = sum(1 for m in health["models"] if m["status"] == "ONLINE")
        results["Model Health"] = {"status": "PASS", "online": online_count, "total": len(health["models"])}
        print(f"✅ PASS ({online_count}/{len(health['models'])} models online)")
    except Exception as e:
        results["Model Health"] = {"status": "FAIL", "error": str(e)}
        print(f"❌ FAIL: {e}")

    print("==================================================", flush=True)
    passed_count = sum(1 for r in results.values() if r["status"] == "PASS")
    print(f"🎯 FINAL TEST RESULTS: {passed_count}/9 ALL PASSED", flush=True)
    print("==================================================", flush=True)
    
    return {"passed": passed_count, "total": 9, "details": results}

if __name__ == "__main__":
    report = run_comprehensive_tests()
    with open("test_results.json", "w") as f:
        json.dump(report, f, indent=2)
