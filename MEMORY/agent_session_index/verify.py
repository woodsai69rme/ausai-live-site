import json, os, glob
print("=== Unified index summary ===")
idx = json.load(open(r"C:\Users\karma\MEMORY\agent_session_index\unified_ai_sessions_index.json", encoding="utf-8"))
print(f"Total records: {len(idx)}")
by_tool = {}
for r in idx:
    t = r.get("tool","?")
    by_tool[t] = by_tool.get(t,0)+1
for t,n in sorted(by_tool.items()):
    print(f"  {t}: {n}")

print("\n=== Kilo sessions export integrity ===")
out = r"C:\Users\karma\MEMORY\kilo_sessions"
for d in sorted(glob.glob(os.path.join(out, "ses_*"))):
    sj = os.path.join(d, "session.json")
    sm = os.path.join(d, "session.md")
    ok = "OK" if os.path.exists(sj) and os.path.exists(sm) else "MISSING"
    print(f"  {os.path.basename(d)[:32]:32s} json={os.path.getsize(sj) if os.path.exists(sj) else 0:>8,} md={os.path.getsize(sm) if os.path.exists(sm) else 0:>8,}  {ok}")
full = os.path.join(out, "kilo_sessions_full.json")
idx_md = os.path.join(out, "KILO_SESSIONS_INDEX.md")
print(f"  kilo_sessions_full.json: {os.path.getsize(full):,} bytes")
print(f"  KILO_SESSIONS_INDEX.md:  {os.path.getsize(idx_md):,} bytes")
