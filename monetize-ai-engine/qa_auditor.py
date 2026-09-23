"""
Deep QA & Security Auditor for AutoMonetize AI
Performs static analysis on HTML/CSS/JS/Python source code for security, performance, mobile readiness, and payment compliance.
"""

import os
import sys
import json
import re

def audit_codebase(code_dict):
    """
    code_dict = {'html': '...', 'css': '...', 'js': '...', 'py': '...'}
    """
    html = code_dict.get('html', '')
    css = code_dict.get('css', '')
    js = code_dict.get('js', '')
    py = code_dict.get('py', '')

    findings = []
    score = 100

    # 1. Security Check: Leaked Secrets
    secret_patterns = [
        (r'sk_live_[0-9a-zA-Z]{24,}', 'CRITICAL: Live Stripe Secret Key found in code. Move to environment variables.'),
        (r'ghp_[0-9a-zA-Z]{36}', 'CRITICAL: GitHub Personal Access Token leaked in source code.'),
        (r'sk-or-v1-[0-9a-f]{64}', 'WARNING: Hardcoded OpenRouter API key found. Use server environment variable in production.')
    ]
    for pattern, msg in secret_patterns:
        if re.search(pattern, html + js + py):
            findings.append({"severity": "HIGH", "category": "Security", "message": msg})
            score -= 20

    # 2. Security Check: Insecure Links
    if re.search(r'target=["\']_blank["\'](?![^>]*rel=["\'][^"\']*noopener)', html):
        findings.append({"severity": "MEDIUM", "category": "Security", "message": 'Links with target="_blank" should include rel="noopener noreferrer" to prevent tab-nabbing.'})
        score -= 5

    # 3. Mobile & Viewport Check
    if '<meta name="viewport"' not in html:
        findings.append({"severity": "HIGH", "category": "Mobile", "message": 'Missing viewport meta tag (<meta name="viewport" content="width=device-width, initial-scale=1.0">).'})
        score -= 15

    # 4. Monetization & Checkout Check
    if not any(keyword in (html + js).lower() for keyword in ['stripe', 'gumroad', 'checkout', 'subscribe', 'buy']):
        findings.append({"severity": "MEDIUM", "category": "Monetization", "message": 'No payment gateway (Stripe/Gumroad) trigger detected in frontend code.'})
        score -= 10

    # 5. CSS & Styling Check
    if not css and '<style>' not in html:
        findings.append({"severity": "MEDIUM", "category": "Design", "message": 'No CSS styling detected. Ensure styles are embedded.'})
        score -= 10

    # 6. JavaScript Error Handling
    if 'try {' not in js and 'try:' not in py:
        findings.append({"severity": "LOW", "category": "Reliability", "message": 'Limited error handling (try/catch) detected in client/server code.'})
        score -= 5

    score = max(20, min(100, score))
    grade = "A+" if score >= 95 else "A" if score >= 85 else "B" if score >= 70 else "C"

    return {
        "score": score,
        "grade": grade,
        "status": "PASSED" if score >= 75 else "NEEDS_IMPROVEMENT",
        "total_checks": 6,
        "findings_count": len(findings),
        "findings": findings,
        "recommendations": [
            "Keep API keys in backend environment variables (.env)",
            "Ensure all CTA buttons trigger a valid Stripe/Gumroad checkout session",
            "Enable gzip/brotli compression and dark mode CSS variables in production"
        ]
    }

if __name__ == "__main__":
    sample_code = {
        "html": '<!DOCTYPE html><html><head><title>App</title><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body><button onclick="checkout()">Subscribe ($19/mo)</button></body></html>',
        "css": "body { background: #000; color: #fff; }",
        "js": "function checkout() { alert('Stripe'); }",
        "py": "import os"
    }
    report = audit_codebase(sample_code)
    print(json.dumps(report, indent=2))
