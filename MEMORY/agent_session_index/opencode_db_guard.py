r"""
OpenCode DB weekly guard.
  1. Soft-archive top-level sessions idle > 60 days (+ orphan subs)
  2. Hard-purge archived sessions archived > 7 days ago (grace period)
  3. VACUUM when no opencode process is running
  4. Delete stale opencode.db backup/pre_clean files older than 30 days
Log: MEMORY\agent_session_index\opencode_db_guard.log
"""
import sqlite3, os, glob, json, datetime, subprocess, sys

DB = r"C:\Users\karma\.local\share\opencode\opencode.db"
OUT = r"C:\Users\karma\MEMORY\agent_session_index"
LOG = os.path.join(OUT, "opencode_db_guard.log")
CONFIG = os.path.join(OUT, "opencode_db_guard.config.json")
IDLE_DAYS = 60
GRACE_DAYS = 7

if os.path.exists(CONFIG):
    try:
        with open(CONFIG, encoding="utf-8") as f:
            _cfg = json.load(f)
        IDLE_DAYS = int(_cfg.get("idle_days", IDLE_DAYS))
        GRACE_DAYS = int(_cfg.get("grace_days", GRACE_DAYS))
    except Exception as e:
        print(f"WARN: bad config, using defaults: {e}")

def log(msg):
    line = f"{datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')} {msg}"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)

def opencode_running():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq OpenCode.exe"],
                             capture_output=True, text=True).stdout
        return "OpenCode.exe" in out
    except Exception:
        return False

def main():
    if not os.path.exists(DB):
        log("FATAL: db missing"); sys.exit(1)
    now_ms = datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000
    idle_ms = (now_ms - IDLE_DAYS * 86400 * 1000)
    grace_ms = (now_ms - GRACE_DAYS * 86400 * 1000)
    c = sqlite3.connect(DB, timeout=60)
    c.execute("PRAGMA busy_timeout=60000")

    # 1) archive idle top-level sessions
    idle = [r[0] for r in c.execute(
        "SELECT id FROM session WHERE time_archived IS NULL AND parent_id IS NULL AND time_updated < ?", (idle_ms,))]
    for sid in idle:
        c.execute("UPDATE session SET time_archived=? WHERE id=?", (int(now_ms), sid))
    # orphan subs of archived
    for sid in [r[0] for r in c.execute(
            "SELECT id FROM session WHERE time_archived IS NULL AND parent_id IS NOT NULL "
            "AND parent_id IN (SELECT id FROM session WHERE time_archived IS NOT NULL)")]:
        c.execute("UPDATE session SET time_archived=? WHERE id=?", (int(now_ms), sid))
    c.commit()
    if idle:
        log(f"archived_idle={len(idle)}")

    # 2) purge archived past grace (skip newly archived)
    arch = [r[0] for r in c.execute(
        "SELECT id FROM session WHERE time_archived IS NOT NULL AND time_archived < ?", (grace_ms,))]
    purged = 0
    if arch:
        ph = ",".join("?" * len(arch))
        # backup rows that have messages before purge (once, best-effort)
        nm = c.execute(f"SELECT COUNT(*) FROM message WHERE session_id IN ({ph})", arch).fetchone()[0]
        if nm:
            bak = os.path.join(OUT, f"guard_purge_backup_{datetime.datetime.now():%Y%m%d}.json.gz")
            if not os.path.exists(bak):
                import gzip
                msgs = c.execute(f"SELECT * FROM message WHERE session_id IN ({ph})", arch).fetchall()
                parts = c.execute(
                    f"SELECT p.* FROM part p JOIN message m ON p.message_id=m.id WHERE m.session_id IN ({ph})", arch).fetchall()
                with gzip.open(bak, "wt", encoding="utf-8") as f:
                    json.dump({"messages": [list(x) for x in msgs], "parts": [list(x) for x in parts]}, f, default=str)
                log(f"backup={os.path.basename(bak)} msgs={len(msgs)}")
        r = c.execute(f"DELETE FROM event WHERE aggregate_id IN ({ph})", arch).rowcount
        r += c.execute(f"DELETE FROM event_sequence WHERE aggregate_id IN ({ph})", arch).rowcount
        r += c.execute(f"DELETE FROM message WHERE session_id IN ({ph})", arch).rowcount
        r += c.execute(f"DELETE FROM part WHERE session_id IN ({ph})", arch).rowcount
        r += c.execute("DELETE FROM part WHERE message_id NOT IN (SELECT id FROM message)").rowcount
        r += c.execute(f"DELETE FROM session_message WHERE session_id IN ({ph})", arch).rowcount
        r += c.execute(f"DELETE FROM todo WHERE session_id IN ({ph})", arch).rowcount
        c.commit()
        purged = r
        log(f"purged_rows={r} from {len(arch)} archived sessions")

    # integrity
    ic = c.execute("PRAGMA integrity_check").fetchone()[0]
    if ic != "ok":
        log(f"FATAL integrity={ic}"); sys.exit(2)
    size_mb = os.path.getsize(DB) // 1024 // 1024
    c.close()

    # 3) VACUUM only when opencode not running
    if opencode_running():
        log(f"skip_vacuum (opencode running) db={size_mb}MB")
    else:
        c = sqlite3.connect(DB, timeout=60)
        c.execute("VACUUM"); c.commit(); c.close()
        log(f"vacuum done db {size_mb}MB -> {os.path.getsize(DB)//1024//1024}MB")

    # 4) stale backups older than 30 days
    removed = 0
    for fp in glob.glob(os.path.join(os.path.dirname(DB), "*.pre_clean*")) + \
              glob.glob(os.path.join(os.path.dirname(DB), "*.db.bak*")):
        if os.path.getmtime(fp) < datetime.datetime.now().timestamp() - 30 * 86400:
            os.remove(fp); removed += 1
    if removed:
        log(f"removed_stale_backups={removed}")
    log("done")

if __name__ == "__main__":
    main()
