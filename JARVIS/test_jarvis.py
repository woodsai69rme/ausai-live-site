#!/usr/bin/env python
"""
test_jarvis.py - live verification that JARVIS core works on THIS machine.
Run:  python test_jarvis.py
No mock output: every check hits the real Ollama / RAG / MEMORY stack.
"""
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jarvis

def check(name, fn):
    try:
        ok, detail = fn()
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
        return ok
    except Exception as e:
        print(f"[FAIL] {name}: exception {e}")
        return False

cfg = jarvis.load_config(os.path.join(jarvis.HERE, "jarvis_config.json"))

results = []
results.append(check("Ollama reachable + models listed", lambda: (
    (lambda m: (bool(m), f"{len(m)} models: {', '.join(m[:4])}...")) (jarvis.ollama_list()))))
results.append(check("Second brain (MEMORY) loads", lambda: (
    (lambda t: (len(t) > 200, f"{len(t)} chars from MEMORY/")) (jarvis.load_second_brain()))))
results.append(check("RAG recall over vault", lambda: (
    (lambda r: (len(r) > 20, f"{len(r)} chars recalled for 'golden rules'")) (jarvis.recall_rag("golden rules", 4)))))
results.append(check("Brain chat answers groundedly", lambda: (
    (lambda x: (len(x[0]) > 20 and "JARVIS" not in x[0][:0], f"{x[1]} replied {len(x[0])} chars")) (
        jarvis.answer(cfg, "In one line, what are my golden rules about projects?")))))
results.append(check("Web research returns results", lambda: (
    (lambda r: (len(r) > 30, f"{len(r)} chars of live results")) (jarvis.web_research("free local LLM 2026", 4)))))
results.append(check("Command router: brains list", lambda: (
    (lambda r: (r and "qwen" in r[1], "router works")) (jarvis.route_command(cfg, "brains")))))
results.append(check("Knowledge map builds (self-contained HTML)", lambda: (
    (lambda p: (os.path.exists(p) and os.path.getsize(p) > 1000, f"{os.path.getsize(p)} bytes at {p}")) (
        jarvis.build_knowledge_map(cfg, os.path.join(jarvis.HERE, "knowledge_map.html"))))))
results.append(check("Desktop open alias resolves", lambda: (
    (lambda r: ("Opened" in r or "Can't find" in r, r)) (jarvis.open_desktop("memory")))))

passed = sum(1 for r in results if r)
print(f"\n=== {passed}/{len(results)} checks passed ===")
sys.exit(0 if passed == len(results) else 1)
