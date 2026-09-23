# History Rewrite Readiness — 2026-08-24

## State

Preparation only. No credentials were revoked, no history was rewritten, no remote ref was changed, and no archive object was pruned.

This working tree is not a rewrite boundary. It contains active source, generated output, archived material, append-only logs, and unrelated changes. The rewrite must happen in a fresh disposable clone after provider containment and archive verification.

## Current read-only inventory

- Repository root: `C:/Users/karma`
- Current branch: `master`
- Current `HEAD`: `373cdf5f18334697357390cffb378747e9e05957`
- Protected local ref: `backup-pre-rewrite` at `f2b0680f3e3bb836b5a3693cc43f692c827eab5b`
- Local branches: 2
- Tags: 262
- Remote-tracking refs: 179
- Origin: SSH GitHub remote for `woodsai69rme/ausai-live-site.git`
- `git-filter-repo`: unavailable in the current shell

The exact credential findings remain intentionally omitted. Use the scanner's path/line/pattern output and provider incident records as the source of truth.

## Approval gates before execution

All items below must be explicitly confirmed by the maintainer before any irreversible command:

- [ ] Every affected provider credential has been rotated or revoked.
- [ ] Provider audit and billing logs have been reviewed from the earliest exposure date.
- [ ] Replacement credentials work through harmless read-only checks and are stored outside Git.
- [ ] An encrypted, access-controlled forensic archive exists outside this repository.
- [ ] The archive has a recorded checksum and has been restored successfully to a separate location.
- [ ] Current worktree changes have been exported or committed under an agreed policy.
- [ ] The rewrite policy covers every required local branch, tag, remote-tracking ref, and known external clone.
- [ ] Repository-admin approval exists for the maintenance window and remote force-update.
- [ ] A fresh clone destination with sufficient free disk is available.
- [ ] `git-filter-repo` is installed and its version is recorded in the execution log.

## Disposable-clone procedure

Run these steps only in a newly created disposable directory after the gates above are complete. Do not run them in `C:/Users/karma`.

```bash
# Clone the approved source into a new disposable directory.
git clone --no-local <approved-source-url> <fresh-rewrite-directory>
cd <fresh-rewrite-directory>

# Record the ref inventory before changing anything.
git show-ref > refs-before.txt
git count-objects -v

# Install/verify git-filter-repo before this stage, then review its help.
git filter-repo --version
git filter-repo --help

# Apply only the maintainer-approved path/value rules.
# Keep the reviewed replacements file outside the repository if it contains
# sensitive source values, and never commit it.
git filter-repo --sensitive-data-removal --replace-text <reviewed-replacements-file>

# Validate all retained refs before any remote update.
git fsck --full --no-reflogs
git show-ref > refs-after.txt
python SECURITY/secret_scan.py --tracked-only
python -m pytest -q
python SECURITY/validate_security_docs.py
```

The exact `git filter-repo` path and replacement rules are intentionally not generated automatically. They must be reviewed against the provider incident inventory so that archive preservation and active-repository cleanup are not conflated.

## Post-rewrite checks

- [ ] No known secret-bearing paths or replacement patterns remain in every approved ref.
- [ ] The working tree contains placeholders only.
- [ ] `git fsck --full --no-reflogs` has no unexpected missing objects.
- [ ] Full tests and security validation pass in the fresh clone.
- [ ] The ref inventory matches the approved rewrite policy.
- [ ] The rewritten clone is archived before remote mutation.
- [ ] Every clone owner has a reclone or repair instruction.
- [ ] The remote force-update is performed only during the approved window.
- [ ] Old credentials remain revoked after the remote update.

## Explicit non-actions in this session

- No provider API or GitHub admin action was performed.
- No credential value was printed or tested.
- No `git filter-repo`, force-push, reset, checkout, prune, or garbage collection was run.
- No append-only SLEEP_TRIPLE JSONL record was normalized or rewritten.

## Related documents

- `SECURITY/EXTERNAL_ACTION_HANDOFF_2026-08-24.md`
- `SECURITY/ROTATION_CHECKLIST.md`
- `SECURITY/INCIDENT_RESPONSE.md`
- `SECURITY/DOCUMENTATION_MANIFEST_2026-08-24.md`
- `SECURITY/FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md`
- `SECURITY/REWRITE_REF_SCOPE_2026-08-24.md`
- `SECURITY/AUDIT_REMEDIATION_STATUS_2026-08-23.md`
