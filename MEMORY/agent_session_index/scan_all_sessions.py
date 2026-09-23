r"""
Unified AI chat session index scanner.

Scans every known AI coding-tool local store on this machine and produces:
  - unified_ai_sessions_index.json   (one record per session/file)
  - unified_ai_sessions_index.md     (human-readable report)

Output dir: C:\Users\karma\MEMORY\agent_session_index\
"""
import sqlite3, os, json, glob, datetime
from datetime import timezone

OUT_DIR = r"C:\Users\karma\MEMORY\agent_session_index"
os.makedirs(OUT_DIR, exist_ok=True)

def ts_ms(ms):
    if ms is None:
        return None
    try:
        ms = float(ms)
        if ms > 1e11:  # value is already in milliseconds (~1.7e12 for 2026)
            ms = ms / 1000
        return datetime.datetime.fromtimestamp(ms, tz=timezone.utc).isoformat()
    except Exception:
        return str(ms)

def is_unix_epoch(ts):
    try:
        t = float(ts)
        return t < 1e12
    except Exception:
        return False

def normalize_ts(ts):
    """Accept ms-epoch, s-epoch, ISO strings, None."""
    if ts is None or ts == "":
        return None
    if isinstance(ts, (int, float)):
        if is_unix_epoch(ts):
            ts = ts * 1000  # treat as seconds -> ms
        return ts_ms(ts)
    if isinstance(ts, str):
        try:
            t = float(ts)
            if is_unix_epoch(t):
                t = t * 1000
            return ts_ms(t)
        except Exception:
            try:
                dt = datetime.datetime.fromisoformat(ts)
                return dt.isoformat()
            except Exception:
                return ts
    return str(ts)

records = []

def add(tool, sid, title, created, updated, path, fmt, extra=None, bsize=None):
    records.append({
        "tool": tool,
        "session_id": sid,
        "title": (title or "")[:120],
        "created": normalize_ts(created),
        "updated": normalize_ts(updated),
        "path": path,
        "format": fmt,
        "bytes": bsize,
        "extra": extra or {}
    })

# ── 1. Kilo (sqlite) ──────────────────────────────────────────────
kilo_db = r"C:\Users\karma\.local\share\kilo\kilo.db"
kilo_diff = r"C:\Users\karma\.local\share\kilo\session_diff"
try:
    c = sqlite3.connect(kilo_db)
    rows = c.execute("SELECT id,title,time_created,time_updated,parent_id,directory,version,agent FROM session ORDER BY time_created").fetchall()
    for r in rows:
        sid, title, tc, tu, parent, directory, ver, agent = r
        df = os.path.join(kilo_diff, f"{sid}.json")
        bsz = os.path.getsize(df) if os.path.exists(df) else None
        nm = c.execute("SELECT COUNT(*) FROM message WHERE session_id=?", (sid,)).fetchone()[0]
        np_ = c.execute("SELECT COUNT(*) FROM part WHERE session_id=?", (sid,)).fetchone()[0]
        add("kilo", sid, title, tc, tu, directory, "kilo.db",
            extra={"parent": parent, "version": ver, "agent": agent, "messages": nm, "parts": np_, "diff_file": df},
            bsize=bsz)
    c.close()
except Exception as e:
    records.append({"tool": "kilo", "error": str(e), "path": kilo_db})

# ── 2. OpenCode (sqlite) ─�──────────────────────────────────────────
oc_db = r"C:\Users\karma\.local\share\opencode\opencode.db"
try:
    c = sqlite3.connect(oc_db)
    rows = c.execute("SELECT id,title,time_created,time_updated,parent_id,directory,version,agent FROM session ORDER BY time_created").fetchall()
    for r in rows:
        sid, title, tc, tu, parent, directory, ver, agent = r
        nm = c.execute("SELECT COUNT(*) FROM message WHERE session_id=?", (sid,)).fetchone()[0]
        add("opencode", sid, title, tc, tu, directory, "opencode.db",
            extra={"parent": parent, "version": ver, "agent": agent, "messages": nm},
            bsize=None)  # per-session size unknown; DB-total size is not per-session
    c.close()
except Exception as e:
    records.append({"tool": "opencode", "error": str(e), "path": oc_db})

# ── 3. Continue (JSON sessions) ─────────────────────────────────────
cont_dir = r"C:\Users\karma\.continue\sessions"
if os.path.isdir(cont_dir):
    for fp in glob.glob(os.path.join(cont_dir, "*.json")):
        try:
            d = json.load(open(fp, "r", encoding="utf-8", errors="ignore"))
            sid = d.get("id") or os.path.basename(fp)
            title = d.get("title") or d.get("name") or ""
            tc = d.get("createdAt") or d.get("created_at")
            tu = d.get("updatedAt") or d.get("updated_at") or tc
            msgs = d.get("messages") or d.get("history") or []
            add("continue", sid, title, tc, tu, fp, "continue.json",
                extra={"messages": len(msgs)}, bsize=os.path.getsize(fp))
        except Exception as e:
            records.append({"tool": "continue", "error": str(e), "path": fp})

# ── 4. Antigravity brains ───────────────────────────────────────────
ag_root = r"C:\Users\karma\.gemini\antigravity\brain"
if os.path.isdir(ag_root):
    for brain in glob.glob(os.path.join(ag_root, "*")):
        if not os.path.isdir(brain):
            continue
        bid = os.path.basename(brain)
        tf = os.path.join(brain, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(tf):
            n = 0
            with open(tf, "r", encoding="utf-8", errors="ignore") as f:
                for _ in f:
                    n += 1
            mt = os.path.getmtime(tf)
            add("antigravity", bid, f"AG brain {bid[:8]}", mt, mt, tf, "ag.jsonl",
                extra={"transcript_lines": n}, bsize=os.path.getsize(tf))
        else:
            mt = os.path.getmtime(brain)
            add("antigravity", bid, f"AG brain {bid[:8]}", mt, mt, brain, "ag.brain")

# ── 5. X:\SESSION_ARCHIVES session docs ─────────────────────────────
arch = r"X:\SESSION_ARCHIVES"
if os.path.isdir(arch):
    for pat in ("SESSION_DOCUMENTATION_*.md", "SESSION_FULL_HISTORY_*.md"):
        for fp in glob.glob(os.path.join(arch, pat)):
            st = os.stat(fp)
            add("session_archive", os.path.basename(fp), os.path.basename(fp),
                st.st_mtime, st.st_mtime, fp, "archive.md", bsize=st.st_size)

# ── 6. X:\codingsesh session summaries ──────────────────────────────
cs = r"X:\codingsesh"
if os.path.isdir(cs):
    for fp in glob.glob(os.path.join(cs, "session_*.txt")) + glob.glob(os.path.join(cs, "session_*.md")):
        st = os.stat(fp)
        add("codingsesh", os.path.basename(fp), os.path.basename(fp),
            st.st_mtime, st.st_mtime, fp, "codingsesh", bsize=st.st_size)
    for fp in glob.glob(os.path.join(cs, "*", "session_*.txt")) + glob.glob(os.path.join(cs, "*", "session_*.md")):
        st = os.stat(fp)
        add("codingsesh", os.path.basename(fp), os.path.basename(fp),
            st.st_mtime, st.st_mtime, fp, "codingsesh", bsize=st.st_size)

# ── 7. VS Code globalStorage agent tasks ────────────────────────────
tasks_root = r"C:\Users\karma\AppData\Roaming\Code\User\globalStorage"
agent_roots = {
    "claude-dev": os.path.join(tasks_root, "saoudrizwan.claude-dev", "tasks"),
    "roo-cline": os.path.join(tasks_root, "rooveterinaryinc.roo-cline", "tasks"),
    "kilocode": os.path.join(tasks_root, "kilocode.kilo-code", "tasks"),
    "debug-cline": os.path.join(tasks_root, "zhucan.debug-cline", "tasks"),
}
for agent_name, root in agent_roots.items():
    if not os.path.isdir(root):
        continue
    for task_dir in sorted(glob.glob(os.path.join(root, "*"))):
        if not os.path.isdir(task_dir):
            continue
        tid = os.path.basename(task_dir)
        meta = os.path.join(task_dir, "metadata.json")
        title = tid
        tc = tu = os.path.getmtime(task_dir)
        if os.path.exists(meta):
            try:
                d = json.load(open(meta, "r", encoding="utf-8", errors="ignore"))
                title = d.get("title") or d.get("name") or tid
                tc = d.get("createdAt") or d.get("created_at") or tc
                tu = d.get("updatedAt") or d.get("updated_at") or tc
            except Exception:
                pass
        add(f"vscode-{agent_name}", tid, title, tc, tu, task_dir, "vscode.task",
            extra={"metadata": meta}, bsize=None)

# ── 8. Cursor ai-tracking ───────────────────────────────────────────
cursor_db = r"C:\Users\karma\.cursor\ai-tracking\ai-code-tracking.db"
if os.path.isfile(cursor_db):
    try:
        c = sqlite3.connect(cursor_db)
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        add("cursor", "cursor.ai-tracking", "Cursor AI tracking DB",
            os.path.getmtime(cursor_db), os.path.getmtime(cursor_db), cursor_db,
            "cursor.db", extra={"tables": tables}, bsize=os.path.getsize(cursor_db))
        # try sessions table
        try:
            cnt = c.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            add("cursor", "cursor.sessions", f"Cursor sessions ({cnt})",
                None, None, cursor_db, "cursor.db", extra={"count": cnt})
        except Exception:
            pass
        c.close()
    except Exception as e:
        records.append({"tool": "cursor", "error": str(e), "path": cursor_db})

# ── 9. emptyWindowChatSessions ──────────────────────────────────────
ewcs = os.path.join(tasks_root, "emptyWindowChatSessions")
if os.path.isdir(ewcs):
    for fp in glob.glob(os.path.join(ewcs, "*.json")):
        try:
            d = json.load(open(fp, "r", encoding="utf-8", errors="ignore"))
            sid = d.get("id") or os.path.basename(fp)
            title = d.get("title") or f"Empty window chat {sid[:8]}"
            add("emptyWindowChat", sid, title, d.get("createdAt") or None,
                d.get("updatedAt") or None, fp, "ewcs.json",
                extra={"messages": len(d.get("messages",[]))}, bsize=os.path.getsize(fp))
        except Exception as e:
            records.append({"tool": "emptyWindowChat", "error": str(e), "path": fp})

# ── 10. ChatBox / AnythingLLM / LM Studio / CherryStudio ────────────
for tool, path in [("chatbox", os.path.expandvars(r"%APPDATA%\chatbox")),
                   ("anythingllm", os.path.expandvars(r"%APPDATA%\AnythingLLM")),
                   ("cherrystudio", os.path.expandvars(r"%APPDATA%\CherryStudio")),
                   ("lmstudio", os.path.expandvars(r"%APPDATA%\LM Studio"))]:
    if os.path.isdir(path):
        nfiles = sum(1 for _ in glob.iglob(os.path.join(path, "**", "*"), recursive=True))
        add(tool, tool, f"{tool} app data", os.path.getmtime(path), os.path.getmtime(path), path, "appdir",
            extra={"files_approx": nfiles})

# ── 11. grok transcripts in SESSION_ARCHIVES ────────────────────────
for fp in glob.glob(os.path.join(arch, "grok_transcript_*.jsonl")) if os.path.isdir(arch) else []:
    st = os.stat(fp)
    add("grok", os.path.basename(fp), os.path.basename(fp), st.st_mtime, st.st_mtime, fp, "grok.jsonl", bsize=st.st_size)

# ── 12. X:\codingsesh dashboards ────────────────────────────────────
for fp in glob.glob(os.path.join(cs, "*.html")) + glob.glob(os.path.join(cs, "*.json")) + glob.glob(os.path.join(cs, "*.md")) if os.path.isdir(cs) else []:
    st = os.stat(fp)
    add("codingsesh", os.path.basename(fp), os.path.basename(fp), st.st_mtime, st.st_mtime, fp, "codingsesh", bsize=st.st_size)

# ── 13. antigravity transcripts_export (per-brain md/jsonl) ─────────
if os.path.isdir(ag_root):
    for brain in glob.glob(os.path.join(ag_root, "*")):
        if not os.path.isdir(brain):
            continue
        bid = os.path.basename(brain)
        te = os.path.join(brain, "transcripts_export")
        if os.path.isdir(te):
            for fp in glob.glob(os.path.join(te, "*")):
                if os.path.isfile(fp):
                    st = os.stat(fp)
                    add("antigravity", f"{bid}:{os.path.basename(fp)}", f"AG {bid[:8]} trans",
                        st.st_mtime, st.st_mtime, fp, "ag.transcript", bsize=st.st_size)

# ── 14. Grok CLI session stores (~\.grok\sessions) ──────────────────
grok_root = r"C:\Users\karma\.grok\sessions"
if os.path.isdir(grok_root):
    for ch in glob.glob(os.path.join(grok_root, "**", "chat_history.jsonl"), recursive=True):
        sdir = os.path.dirname(ch)
        sid = os.path.basename(sdir)
        title = sid
        tc = tu = os.path.getmtime(ch)
        sj = os.path.join(sdir, "summary.json")
        if os.path.exists(sj):
            try:
                d = json.load(open(sj, "r", encoding="utf-8", errors="ignore"))
                title = d.get("title") or d.get("name") or title
                tc = d.get("createdAt") or d.get("created_at") or tc
                tu = d.get("updatedAt") or d.get("updated_at") or tc
            except Exception:
                pass
        try:
            nlines = sum(1 for _ in open(ch, "r", encoding="utf-8", errors="ignore"))
        except Exception:
            nlines = None
        add("grok-cli", sid, str(title), tc, tu, ch, "grok.chat.jsonl",
            extra={"dir": sdir, "chat_lines": nlines}, bsize=os.path.getsize(ch))

# ── 15. Cline CLI session stores (~\.cline\data\sessions) ───────────
cline_root = r"C:\Users\karma\.cline\data\sessions"
if os.path.isdir(cline_root):
    for meta_fp in glob.glob(os.path.join(cline_root, "*", "*.json")):
        if meta_fp.endswith(".messages.json"):
            continue
        sid = os.path.basename(meta_fp).replace(".json", "")
        title = sid
        tc = tu = os.path.getmtime(meta_fp)
        try:
            d = json.load(open(meta_fp, "r", encoding="utf-8", errors="ignore"))
            title = d.get("title") or d.get("name") or d.get("task") or title
            tc = d.get("createdAt") or d.get("created_at") or tc
            tu = d.get("updatedAt") or d.get("updated_at") or tc
        except Exception:
            pass
        msgs_fp = meta_fp.replace(".json", ".messages.json")
        bsz = os.path.getsize(msgs_fp) if os.path.exists(msgs_fp) else os.path.getsize(meta_fp)
        add("cline", sid, str(title)[:120], tc, tu, meta_fp, "cline.json", bsize=bsz)

# ── 16. Codex CLI rollouts (~\.codex\sessions) ──────────────────────
codex_root = r"C:\Users\karma\.codex\sessions"
if os.path.isdir(codex_root):
    for fp in glob.glob(os.path.join(codex_root, "**", "rollout-*.jsonl"), recursive=True):
        st = os.stat(fp)
        add("codex", os.path.basename(fp), os.path.basename(fp), st.st_mtime, st.st_mtime,
            fp, "codex.rollout.jsonl", bsize=st.st_size)

# ── 17. Claude Code CLI transcripts (~\.claude\projects) ────────────
claude_root = r"C:\Users\karma\.claude\projects"
if os.path.isdir(claude_root):
    for fp in glob.glob(os.path.join(claude_root, "**", "*.jsonl"), recursive=True):
        st = os.stat(fp)
        add("claude-code", os.path.basename(fp).replace(".jsonl", ""), os.path.basename(fp),
            st.st_mtime, st.st_mtime, fp, "claude.transcript.jsonl", bsize=st.st_size)

# ── 18. Qoder session logs (~\.qoder\logs\sessions) ─────────────────
qoder_root = r"C:\Users\karma\.qoder\logs\sessions"
if os.path.isdir(qoder_root):
    for fp in glob.glob(os.path.join(qoder_root, "**", "*.jsonl"), recursive=True):
        st = os.stat(fp)
        sid = os.path.basename(os.path.dirname(os.path.dirname(fp)))
        add("qoder", f"{sid}:{os.path.basename(fp)}", f"qoder segment {sid[:8]}",
            st.st_mtime, st.st_mtime, fp, "qoder.segment.jsonl", bsize=st.st_size)

# ── Write JSON (streamed) ───────────────────────────────────────────
json_path = os.path.join(OUT_DIR, "unified_ai_sessions_index.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)
print(f"JSON: {json_path} ({len(records)} records, {os.path.getsize(json_path):,} bytes)")

# ── Write Markdown report ────────────────────────────────────────────
md_path = os.path.join(OUT_DIR, "unified_ai_sessions_index.md")
by_tool = {}
for r in records:
    t = r.get("tool", "?")
    by_tool[t] = by_tool.get(t, 0) + 1
out = []
out.append("# Unified AI Chat Session Index")
out.append("")
out.append(f"Generated: {datetime.datetime.now(timezone.utc).isoformat()}")
out.append("")
out.append("## Summary by Tool")
out.append("")
out.append("| Tool | Sessions/Files |")
out.append("|------|----------------|")
for t in sorted(by_tool):
    out.append(f"| {t} | {by_tool[t]} |")
out.append("")
out.append(f"**Total records: {len(records)}**")
out.append("")
out.append("## All Sessions")
out.append("")
out.append("| Tool | Session ID | Title | Created (UTC) | Updated (UTC) | Bytes | Path |")
out.append("|------|-----------|-------|---------------|---------------|-------|------|")
for r in records:
    sid = (r.get("session_id","") or "")[:24]
    title = (r.get("title","") or "")[:45].replace("|","\\|")
    created = (r.get("created") or "")[:19].replace("T"," ")
    updated = (r.get("updated") or "")[:19].replace("T"," ")
    b = r.get("bytes")
    b = f"{b:,}" if b else ""
    path = (r.get("path","") or "")[:70].replace("|","\\|")
    out.append(f"| {r.get('tool','')} | {sid} | {title} | {created} | {updated} | {b} | {path} |")
out.append("")
out.append("## Detail Fields per Tool")
out.append("")
detail_cols = {"kilo":"id,title,agent,model,dir,version,msgs,parts,todos,ts","opencode":"id,title,agent,model,dir,version,msgs,ts","continue":"id,title,messages,ts","antigravity":"brain_id,transcript_lines,ts","session_archive":"filename,bytes,ts","codingsesh":"filename,bytes,ts","vscode-claude-dev":"task_id,metadata,ts"}
for t in sorted(by_tool):
    rows_t = [r for r in records if r.get("tool") == t]
    if not rows_t:
        continue
    sample = rows_t[0]
    keys = sorted(sample.keys())
    out.append(f"### {t}")
    out.append("Fields: " + ", ".join(keys))
    out.append("")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print(f"Markdown: {md_path}")

# Per-tool JSON splits
for t in sorted(by_tool):
    sub = [r for r in records if r.get("tool") == t]
    with open(os.path.join(OUT_DIR, f"unified_{t}.json"), "w", encoding="utf-8") as f:
        json.dump(sub, f, indent=2, ensure_ascii=False)
    print(f"  -> unified_{t}.json ({len(sub)} records)")
