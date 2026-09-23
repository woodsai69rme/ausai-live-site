#!/usr/bin/env python3
"""v3.3.0 SHIP recovery — end-to-end pipeline as a single Python script.

Replaces shell heredoc chains with a single process tree to avoid bash quoting
fragility. All file edits are bytes-level. Every phase is idempotent so the
script can be re-run safely.

Phases (each short-circuits when already applied):
  1. Patch .git/hooks/pre-commit (dashboards.js -> dashboards.mjs, line-anchored)
  2. Insert GITHUB_TAG_NOTES.md v3.3 routing-milestone section (before ## Migration)
  3. Append macOS Cmd+H caveat to DASHBOARD_ARCHITECTURE.md ## v3.x limitations
  4. node --check syntax verification on shared module + smoke test
  5. Smoke regression (node tools/test_dashboards.js) — expect 16/16 cats / 75+ OKs
  6. verify_dashboard.py on 3 HTML files (dashboards.mjs is covered by Phase 4) — expect 3 VALID
  7. git add source/test files
  8. git commit -F tmp/commit_E08_msg.txt (E08 source-tree commit)
  9. git add doc files; git commit -F tmp/commit_docs_msg.txt (docs commit; skipped if no diff)
 10. git tag -f -a dashboard-system-v3.3.0 -F tmp/v3_3_tag.txt (atomic force-update; peels to ^{commit})
 11. SSH push (3 retries x 15s back-off; non-fatal on failure — local tag preserved)
"""
import os
import re
import subprocess
import sys
import time

ROOT = r'C:\Users\karma'
os.chdir(ROOT)

# -- Paths (relative to repo root) -----------------------------------------
HOOK_REL = '.git/hooks/pre-commit'
GH_TAG_REL = 'GITHUB_TAG_NOTES.md'
ARCH_REL = 'DASHBOARD_ARCHITECTURE.md'
V33_PAYLOAD_REL = 'tmp/v3_3_tag_notes_diff_crlf.md'
COMMIT_E08_REL = 'tmp/commit_E08_msg.txt'
COMMIT_DOCS_REL = 'tmp/commit_docs_msg.txt'
TAG_MSG_REL = 'tmp/v3_3_tag.txt'
SMOKE_REL = 'tools/test_dashboards.js'
DASHBOARDS_REL = 'dashboards.mjs'
VERIFY_REL = 'COMPLETED_PROJECTS/mobile_backup/verify_dashboard.py'
SOURCE_FILES = [DASHBOARDS_REL, 'tools/test_dashboards.js']
DOC_FILES = ['CHANGELOG.md', ARCH_REL, GH_TAG_REL]
# Phase 6 verifies only the 3 HTML dashboard hosts. The .mjs shared module IS
# syntax-checked by Phase 4 (node --check) above, so avoid double-checking.
HTML_VERIFY_TARGETS = [
    'UNIFIED_MASTER_DASHBOARD.html',
    'AI_TOOLS_DASHBOARD.html',
    'AUSAI_OPS_DASHBOARD.html',
]

# -- Helpers ---------------------------------------------------------------
def banner(phase, msg):
    print(f"\n=== {phase}: {msg} ===", flush=True)


def run(cmd, check=True, allow_codes=(0,)):
    """subprocess.run wrapper. check=True means rc must be in allow_codes."""
    print(f"  $ {' '.join(cmd) if isinstance(cmd, list) else cmd}", flush=True)
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.stdout:
        print(p.stdout.rstrip(), flush=True)
    if p.stderr:
        print(f"  (stderr): {p.stderr.rstrip()}", flush=True)
    if check and p.returncode not in allow_codes:
        raise SystemExit(f"FATAL: command failed rc={p.returncode}: {cmd}")
    return p


# -- Phase 1: hook patch ---------------------------------------------------
def phase1_hook():
    banner("Phase 1", "PATCH pre-commit hook (dashboards.js -> dashboards.mjs)")
    with open(HOOK_REL, 'rb') as f:
        data = f.read()
    if b'dashboards.js' not in data:
        print("  hook already clean (no dashboards.js references)", flush=True)
        return
    # Line-anchored replace to avoid mangling log/comment text.
    new_data = data.replace(
        b'for target in dashboards.js',
        b'for target in dashboards.mjs',
    )
    if new_data == data:
        # Anchor not on a single line — fall back to non-replace and warn.
        print("  WARN: line-anchored match missed; leaving hook untouched", flush=True)
        return
    with open(HOOK_REL, 'wb') as f:
        f.write(new_data)
    print(f"  hook patched: {len(data)} -> {len(new_data)} bytes", flush=True)
    print("  post-patch greps:", flush=True)
    subprocess.run(['grep', '-nE', r'dashboards\.(js|mjs)', HOOK_REL])


# -- Phase 2: GITHUB_TAG_NOTES v3.3 routing-milestone section ----------------
def phase2_gh_tag():
    banner("Phase 2", "INSERT GITHUB_TAG_NOTES.md v3.3 routing-milestone section")
    with open(GH_TAG_REL, 'rb') as f:
        data = f.read()
    if b'Spotlight v3.3 enhancements' in data:
        print("  v3.3 section ALREADY APPLIED, skipping", flush=True)
        return
    mig_anchor = b'## Migration from v2.5.0'
    idx = data.find(mig_anchor)
    if idx == -1:
        raise SystemExit("FATAL: ## Migration anchor not found in GITHUB_TAG_NOTES.md")
    if not os.path.exists(V33_PAYLOAD_REL):
        raise SystemExit(f"FATAL: payload missing: {V33_PAYLOAD_REL}")
    with open(V33_PAYLOAD_REL, 'rb') as f:
        payload = f.read()
    new_data = data[:idx] + payload + data[idx:]
    with open(GH_TAG_REL, 'wb') as f:
        f.write(new_data)
    print(f"  inserted: {len(payload)} bytes before ## Migration; "
          f"file {len(data)} -> {len(new_data)} bytes", flush=True)


# -- Phase 3: macOS Cmd+H caveat under ARCHITECTURE.md ----------------------
MACOS_CAVEAT = (
    b'\r\n- **macOS Cmd+H caveat (v3.3):**\r\n'
    b'  The Ctrl/Cmd+H binding (added in v3.3 for Spotlight history dropdown)\r\n'
    b'  conflicts with macOS `Hide Window` (Cmd+H at the OS level). On macOS the\r\n'
    b'  browser-level handler fires after the OS-level hijack, so the modal does\r\n'
    b'  NOT close on Cmd+H. Users must use Esc or click the backdrop to dismiss.\r\n'
    b'  Track under "Outstanding" below.\r\n'
)


def phase3_arch_caveat():
    banner("Phase 3", "APPEND macOS Cmd+H caveat to DASHBOARD_ARCHITECTURE.md")
    with open(ARCH_REL, 'rb') as f:
        data = f.read()
    if b'macOS Cmd+H caveat' in data:
        print("  caveat ALREADY PRESENT, skipping", flush=True)
        return
    # ## v3.x limitations is the LAST section in DASHBOARD_ARCHITECTURE.md
    # (verified: byte ~29414, file ends shortly after). So appending at file end
    # lands the caveat correctly under v3.x limitations (not under ## Outstanding).
    new_data = data + MACOS_CAVEAT
    with open(ARCH_REL, 'wb') as f:
        f.write(new_data)
    print(f"  appended caveat: {len(data)} -> {len(new_data)} bytes", flush=True)


# -- Phase 4: node --check --------------------------------------------------
def phase4_node_check():
    banner("Phase 4", "node --check (syntax verification)")
    for f in [DASHBOARDS_REL, SMOKE_REL]:
        p = subprocess.run(['node', '--check', f], capture_output=True, text=True)
        if p.returncode != 0:
            print(f"  {(p.stderr or p.stdout or '').strip()}", flush=True)
            raise SystemExit(f"FATAL: node --check {f} failed rc={p.returncode}")
        print(f"  {f} SYNTAX OK", flush=True)


# -- Phase 5: smoke regression ---------------------------------------------
def phase5_smoke():
    banner("Phase 5", "SMOKE regression (node tools/test_dashboards.js)")
    p = subprocess.run(['node', SMOKE_REL], capture_output=True, text=True)
    output = (p.stdout or '') + (p.stderr or '')
    lines = output.splitlines()
    tail = '\n'.join(lines[-60:]) if len(lines) > 60 else output
    print(tail.rstrip(), flush=True)
    if p.returncode != 0:
        raise SystemExit(f"FATAL: smoke regression FAILED rc={p.returncode}")
    if 'FAIL' in output.upper():
        raise SystemExit("FATAL: smoke regression emitted FAIL line")
    ok_lines = sum(1 for ln in lines if ln.lstrip().lower().startswith('ok '))
    total_cats = 0
    passed_cats = 0
    for ln in lines:
        m = re.match(r'\s*(\d+)/(\d+)\s+test categories passed', ln)
        if m:
            passed_cats = int(m.group(1))
            total_cats = int(m.group(2))
            break
    print(f"  smoke OK: exit={p.returncode}, ok_prefix_lines={ok_lines}, "
          f"summary={passed_cats}/{total_cats} cats passed", flush=True)
    if total_cats == 0 or passed_cats != total_cats:
        raise SystemExit(
            f"FATAL: smoke summary line missing or partial "
            f"(passed={passed_cats}, total={total_cats})"
        )


# -- Phase 6: verify_dashboard.py ------------------------------------------
def phase6_verify():
    banner("Phase 6", "verify_dashboard.py on 3 HTML files")
    valid_count = 0
    for target in HTML_VERIFY_TARGETS:
        p = subprocess.run(['python', VERIFY_REL, target], capture_output=True, text=True)
        output = (p.stdout or '') + (p.stderr or '')
        last_line = output.strip().splitlines()[-1] if output.strip() else '(no output)'
        print(f"  {target}: {last_line}", flush=True)
        if 'VALID' in last_line.upper() and p.returncode == 0:
            valid_count += 1
    if valid_count < 3:
        raise SystemExit(f"FATAL: verify returned {valid_count} VALIDs (want 3)")
    print(f"  verify OK: {valid_count}/3 HTML files VALID", flush=True)


# -- Phase 7: git add source/test -------------------------------------------
def phase7_add_source():
    banner("Phase 7", "git add source/test files (dashboards.mjs + test_dashboards.js)")
    run(['git', 'add'] + SOURCE_FILES)
    p = run(['git', 'status', '--short'], check=False)
    print(f"  staged output:\n{p.stdout}", flush=True)


# -- Phase 8: E08 commit -----------------------------------------------------
def phase8_commit_e08():
    banner("Phase 8", "git commit -F tmp/commit_E08_msg.txt")
    if not os.path.exists(COMMIT_E08_REL) or os.path.getsize(COMMIT_E08_REL) == 0:
        raise SystemExit(f"FATAL: {COMMIT_E08_REL} missing or empty")
    p = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
    if p.returncode == 0:
        raise SystemExit("FATAL: no staged source/test changes — nothing to commit")
    run(['git', 'commit', '-F', COMMIT_E08_REL])
    sha = run(['git', 'rev-parse', 'HEAD']).stdout.strip()
    print(f"  E08 commit SHA: {sha}", flush=True)
    return sha


# -- Phase 9: docs commit (skipped if no staged diff) ------------------------
def phase9_commit_docs():
    banner("Phase 9", "git add doc files + git commit -F tmp/commit_docs_msg.txt")
    run(['git', 'add'] + DOC_FILES)
    p = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
    if p.returncode == 0:
        sha = run(['git', 'rev-parse', 'HEAD']).stdout.strip()
        print(f"  no staged doc changes; reusing HEAD={sha}", flush=True)
        return sha
    if not os.path.exists(COMMIT_DOCS_REL) or os.path.getsize(COMMIT_DOCS_REL) == 0:
        raise SystemExit(f"FATAL: {COMMIT_DOCS_REL} missing or empty")
    run(['git', 'commit', '-F', COMMIT_DOCS_REL])
    sha = run(['git', 'rev-parse', 'HEAD']).stdout.strip()
    print(f"  docs commit SHA: {sha}", flush=True)
    return sha


# -- Phase 10: annotated tag ------------------------------------------------
def phase10_tag(docs_sha):
    banner("Phase 10", "git tag -f -a dashboard-system-v3.3.0 (atomic force-update)")
    if not os.path.exists(TAG_MSG_REL) or os.path.getsize(TAG_MSG_REL) == 0:
        raise SystemExit(f"FATAL: {TAG_MSG_REL} missing or empty")
    # Atomic force-update: `git tag -f -a` re-creates the tag overwriting any
    # prior annotated tag of the same name in-place. No transient state where
    # the tag is missing (defends against concurrent observers probing the tag).
    run(['git', 'tag', '-f', '-a', 'dashboard-system-v3.3.0', '-F', TAG_MSG_REL, docs_sha])
    # IMPORTANT: peel to ^{commit} (the underlying commit SHA), NOT ^{tag}
    # (the tag-object SHA). Verified empirically: ^{tag} returns tag-object,
    # ^{commit}/^{} returns commit; tag SHA can never equal commit SHA so the
    # invariant MUST compare commit-SHAs.
    tag_sha = run(['git', 'rev-parse', '--verify', 'dashboard-system-v3.3.0^{commit}']).stdout.strip()
    head_sha = run(['git', 'rev-parse', 'HEAD']).stdout.strip()
    print(f"  tag SHA:    {tag_sha}", flush=True)
    print(f"  HEAD SHA:   {head_sha}", flush=True)
    print(f"  docs SHA:   {docs_sha}", flush=True)
    # HARD ABORT if tag SHA does NOT match HEAD SHA — required invariant for
    # release ships (was a soft WARN historically, promoted here).
    if tag_sha != head_sha:
        raise SystemExit(
            f"FATAL: tag SHA {tag_sha} != HEAD SHA {head_sha} after creation; "
            f"expected exact match"
        )
    print("  tag SHA == HEAD SHA OK", flush=True)
    return tag_sha


# -- Phase 11: SSH push with retries ----------------------------------------
def phase11_push(docs_sha):
    banner("Phase 11", "SSH push (3 retries x 15s back-off)")
    for attempt in range(1, 4):
        print(f"  attempt {attempt}/3...", flush=True)
        p = subprocess.run(
            ['git', 'push', 'origin', 'master', '--follow-tags'],
            capture_output=True, text=True,
        )
        out = (p.stdout or '') + (p.stderr or '')
        print(f"  rc={p.returncode}", flush=True)
        if out.strip():
            print(f"  output: {out.strip()}", flush=True)
        if p.returncode == 0 or 'Everything up-to-date' in out:
            print("  push OK", flush=True)
            return
        if attempt < 3:
            print(f"  retrying in 15s...", flush=True)
            time.sleep(15)
    print("  push FAILED after 3 attempts. Local tag preserved — manual push later.", flush=True)


def main():
    banner("v3.3.0 SHIP", "recovery pipeline starting")
    phase1_hook()
    phase2_gh_tag()
    phase3_arch_caveat()
    phase4_node_check()
    phase5_smoke()
    phase6_verify()
    phase7_add_source()
    e08_sha = phase8_commit_e08()
    docs_sha = phase9_commit_docs()
    phase10_tag(docs_sha)
    phase11_push(docs_sha)
    banner("v3.3.0 SHIP", "COMPLETE")


if __name__ == '__main__':
    try:
        main()
    except SystemExit as e:
        print(f"\n  EXIT: {e}", flush=True)
        sys.exit(1)
