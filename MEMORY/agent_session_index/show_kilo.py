import json
d = json.load(open(r"C:\Users\karma\MEMORY\agent_session_index\unified_kilo.json", encoding="utf-8"))
for r in d:
    print(r["session_id"][:12], "|", repr(r["created"]), "|", repr(r["updated"]), "|", r["title"][:40])
