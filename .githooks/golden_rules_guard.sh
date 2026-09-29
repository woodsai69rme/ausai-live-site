#!/bin/sh
# .githooks/golden_rules_guard.sh -- Golden Rules hard enforcement (Stage 0)
# Added: 2026-09-24. Called at the TOP of .githooks/pre-commit, BEFORE the
# Windows .bat shim and BEFORE the paired-ack bypass hatches -- so it runs on
# EVERY shell path (sh directly, and cmd.exe via pre-commit.bat delegation,
# which inherits the call) and cannot be skipped by PRECOMMIT_BYPASS.
#
# Enforces (Golden Rules v1.1, .claude/GOLDEN_RULES.md):
#   Rule #1/#2/#5 (nothing obsolete / projects permanent / backups critical):
#     - HARD BLOCK: any staged change that removes a file from the WORKING
#       TREE (`git rm <file>`, shell `rm` of a tracked file, ...).
#       Detection: staged status D + file ABSENT on disk at commit time.
#     - ALLOWED with an informational note: index-only untracks
#       (`git rm --cached <file>`; staged D + file still present on disk).
#       Untracking deletes nothing from disk -- Rule-compliant.
#     - Renames/moves (R) flow through: rename sources are paired by git and
#       never appear in the D filter; moving is not deleting.
#     - This block has NO bypass env var (intentional hard rule).
#   Rule #8 (personal files are sacred -- operator directive 2026-07-13):
#     - HARD BLOCK: any staged change (A/M/D/R/C) under Documents, Downloads
#       (incl. ARCHIVE_OLD), Pictures, Videos, Music, Desktop, OneDrive.
#       Read/review only. No bypass env var.
#   Fail closed: unexpected guard errors refuse the commit (exit 2).
#
# Exit codes: 0 = pass, 1 = hard block, 2 = guard failure (fail closed).
# Additive coexistence per Rule #7: existing Stage A (syntax) + Stage B
# (smoke) logic is untouched and continues to run after this guard.

# --- 0. Resolve paths --------------------------------------------------------
script_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
cd "$repo_root" 2>/dev/null || exit 2

GUARD_TAG="[golden-rules]"

# Tree-ish to diff against: HEAD, or the empty tree for the initial commit.
TREEISH="HEAD"
if ! git rev-parse --verify --quiet HEAD >/dev/null 2>&1; then
    TREEISH="$(git hash-object -t tree /dev/null 2>/dev/null)" || exit 2
    [ -n "$TREEISH" ] || exit 2
fi

# --- 1. Guard: no deletions from the working tree (Rules #1/#2/#5) -----------
# Staged "D" + file absent on disk  => the commit deletes it. BLOCK.
# Staged "D" + file still on disk   => index-only untrack (rm --cached). OK.
DEL_LINES="$(git diff-index --cached --name-status --diff-filter=D "$TREEISH" 2>/dev/null)"
git_rc=$?
if [ "$git_rc" -ne 0 ]; then
    echo "$GUARD_TAG FAIL: could not read the git index (fail closed)." >&2
    exit 2
fi

BLOCKED_DELETIONS=""
UNTRACK_COUNT=0
if [ -n "$DEL_LINES" ]; then
    printf '%s\n' "$DEL_LINES" | grep '^D' | cut -f2- | while IFS= read -r del_path; do
        if [ -e "$del_path" ]; then
            echo "$GUARD_TAG OK: index-only untrack (file stays on disk): $del_path"
        else
            echo "__BLOCKED__ $del_path"
        fi
    done > "$repo_root/.git/golden_rules_guard.$$" 2>/dev/null || : 
    if [ -f "$repo_root/.git/golden_rules_guard.$$" ]; then
        BLOCKED_DELETIONS="$(grep '^__BLOCKED__ ' "$repo_root/.git/golden_rules_guard.$$" | sed 's/^__BLOCKED__ //')"
        UNTRACK_COUNT="$(grep -c -v '^__BLOCKED__ ' "$repo_root/.git/golden_rules_guard.$$" 2>/dev/null)"
        rm -f "$repo_root/.git/golden_rules_guard.$$"
    fi
fi

if [ -n "$BLOCKED_DELETIONS" ]; then
    echo "$GUARD_TAG FAIL: Golden Rules #1/#2/#5 -- commits may not delete files from disk." >&2
    echo "$GUARD_TAG       The following staged changes REMOVE files from the working tree:" >&2
    printf '%s\n' "$BLOCKED_DELETIONS" | sed 's/^/  - /' >&2
    echo "$GUARD_TAG       'Nothing is obsolete; all projects are permanent; all backups are critical.'" >&2
    echo "$GUARD_TAG       Allowed alternative: 'git rm --cached <path>' untracks WITHOUT deleting" >&2
    echo "$GUARD_TAG       from disk. This deletion block has NO bypass env var (by design)." >&2
    exit 1
fi

if [ "${UNTRACK_COUNT:-0}" -gt 0 ] 2>/dev/null; then
    echo "$GUARD_TAG NOTE: $UNTRACK_COUNT index-only untrack(s) staged -- files remain on disk (Rule-compliant)."
fi

# --- 2. Guard: protected personal folders (Rule #8) ---------------------------
# READ/REVIEW ONLY. Whole-line match catches A/M/D plus both rename endpoints.
PROTECTED_CHANGES="$(git diff-index --cached --name-status "$TREEISH" 2>/dev/null \
    | grep -E '(^|[^[:alnum:]])(Documents|Downloads|Pictures|Videos|Music|Desktop|OneDrive)/' || true)"

if [ -n "$PROTECTED_CHANGES" ]; then
    echo "$GUARD_TAG FAIL: Golden Rule #8 -- personal folders are SACRED (read/review only)." >&2
    echo "$GUARD_TAG       Staged changes touch protected paths:" >&2
    printf '%s\n' "$PROTECTED_CHANGES" | sed 's/^/  - /' >&2
    echo "$GUARD_TAG       Never modify/delete/move/archive: Documents, Downloads (incl." >&2
    echo "$GUARD_TAG       ARCHIVE_OLD), Pictures, Videos, Music, Desktop, OneDrive." >&2
    echo "$GUARD_TAG       Operator directive 2026-07-13 -- permanent until revoked in writing." >&2
    echo "$GUARD_TAG       Unstage with: git restore --staged '<path>'" >&2
    echo "$GUARD_TAG       This block has NO bypass env var (intentional, permanent directive)." >&2
    exit 1
fi

exit 0
