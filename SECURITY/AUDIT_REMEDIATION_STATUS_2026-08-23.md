# Repository Audit and Remediation Status

Date: 2026-08-23
Status: repository-side remediation complete; external credential and remote-history actions remain pending
Owner: workspace maintainer

## Executive Summary

This workspace is a preserved ecosystem snapshot rather than a single clean application repository. It contains active projects, generated dashboards, archived projects, runtime logs, local tool state, backups, and machine-local artifacts under one Git root.

The audit and remediation work followed these Golden Rules:

- Nothing is obsolete.
- All projects remain permanent.
- All AI tools remain essential.
- Add, integrate, connect, and document.
- Enhance; do not reduce.
- Personal folders are read-only.
- Never commit secrets.
- Append-only records remain append-only.

The audit found a serious credential-history incident and repository-boundary problems. Local remediation has now been completed for CI hardening, runtime status semantics, changed-file secret scanning, security documentation, Graphify restoration, and test drift. No credential was printed, revoked, replaced, deleted, or reused. No Git history was rewritten and no remote was updated.

## Scope and Repository Shape

The repository root is the user workspace. It is not a conventional application boundary.

Previously measured inventory:

- 18,670 tracked files.
- 4,220 ignored-but-tracked paths.
- 76 tracked files larger than 10 MiB.
- Many archived and generated artifacts mixed with active source.
- 179 remote-tracking branches were present during the remediation pass.
- The working tree contained hundreds of pre-existing changes; the latest measured count was 688 porcelain entries.

Preservation and source hygiene are separate concerns. Keeping an archive does not require treating every machine artifact as active source, but no archive material was deleted during this work.

## Original Findings

### Critical: credential-shaped material in tracked history

The audit found tracked files containing high-confidence credential-shaped material, including:

- GitHub tokens and Git credential-helper files.
- Google API-key-shaped and OAuth-related material.
- OpenAI-compatible provider keys.
- SSH private-key material.
- Discord or messaging webhook-shaped URLs.
- Historical environment files, generated documentation, session exports, and backup configurations.

Affected material was not printed or copied into new documentation. Every matching value must be treated as compromised until the owning provider confirms revocation or rotation.

### High: unhealthy repository boundary

The Git root includes active source and machine/archive state. This increases the risk of accidental commits, makes full scans expensive, and complicates CI scope and history rewriting.

### High: previously non-blocking CI checks

The audit identified workflows where lint, type, frontend, or test failures could be reported without making the workflow fail. Those checks were changed to be blocking in the current remediation set.

### High: broad automation permissions

Comment-triggered Claude workflows had broad mutation permissions and mutable action references. The workflows were hardened locally, but repository policy and branch protection still require maintainer review.

### Medium/High: optimistic runtime status

SLEEP_TRIPLE could report an overall successful run when ComfyUI was offline or a dependency was degraded. Discord alert delivery also failed when `DISCORD_WEBHOOK_URL` was absent. Runtime status propagation was corrected so degraded dependencies are visible and nonzero to schedulers.

### Medium: data and test drift

The Full Stack catalog had moved from the older 107-video/92-item snapshot to the validated 115-video/99-item snapshot while two tests still asserted the old values. The tests were updated to the current validated snapshot.

## Remediation Implemented

### CI and workflow hardening

Changed workflows:

- `.github/workflows/ci.yml`
- `.github/workflows/claude-fix.yml`
- `.github/workflows/claude-review.yml`
- `.github/workflows/sleep-cash-preflight.yml`
- `.github/workflows/verify-dashboards.yml`

Implemented controls:

- Workflow-level `contents: read` defaults where applicable.
- Removed unnecessary OIDC permission use from Claude workflows.
- Kept write permissions limited to the Claude fix job that explicitly needs them.
- Pinned GitHub Actions to reviewed immutable commit SHAs with version comments.
- Made lint, formatting, type, frontend, and test checks blocking.
- Added a changed-file secret-scan job to CI.
- Added robust changed-file fallback logic for pull requests, pushes, and first-push edge cases.
- Preserved preflight diagnostics and summaries while making strict failure enforce a red job.

Validation:

- Workflow YAML parsing passed for all `.github/workflows/*.yml` files.
- No mutable `uses: ...@vN` action tags remain in the checked workflows.
- Scoped `git diff --check` passed for workflows and security documentation.

### Secret-scanning guardrail

Added `SECURITY/secret_scan.py`.

Behavior:

- Scans repository-relative paths, changed-file lists, direct paths, or tracked files.
- Reads files incrementally to avoid exhausting memory on generated/archive files.
- Reports only path, line, and pattern class.
- Never prints matched credential values.
- Detects private-key headers, GitHub token classes, OpenAI-shaped keys, Google key-shaped values, Slack tokens, and Discord webhooks.
- Ignores the scanner's own source file to avoid matching its documented regular expressions.

Normal CI usage:

```bash
python SECURITY/secret_scan.py --paths-file changed-files.txt
```

Full archive audit:

```bash
python SECURITY/secret_scan.py --tracked-only
```

The full tracked-file audit remains an incident audit and is expected to fail until provider rotation and history scrubbing are complete. On this workspace it is also expensive enough to exceed the local command window.

### Security runbooks

Added or maintained:

- `SECURITY/INCIDENT_RESPONSE.md`
- `SECURITY/ROTATION_CHECKLIST.md`

They document provider workstreams for GitHub, Google, OpenAI-compatible providers, SSH/Git credentials, and messaging webhooks. They also specify archive preservation, rotation evidence, history-scrubbing prerequisites, post-rewrite validation, and the prohibition on recording secret values.

### Enhanced security validation

Added:

- `SECURITY/validate_security_docs.py`: read-only validator for canonical documentation, repository references, workflow YAML, immutable action SHAs, and security-document scan results.
- `tests/test_security_controls.py`: regression coverage for credential detection, explicit placeholders, repository-boundary rejection, missing-file failures, and documentation validation.

The scanner was hardened to:

- Reject paths resolving outside the Git worktree, including traversal and symlink escapes.
- Report missing and unreadable files instead of silently skipping them.
- Normalize and deduplicate inputs.
- Remove only explicit placeholder syntax before matching, preserving detection when generic words such as `example` appear beside a real credential.
- Emit JSON for machine-readable CI consumers.

CI now runs the documentation/workflow validator after the changed-file scan.

### SLEEP_TRIPLE status semantics

Changed runtime modules:

- `SLEEP_TRIPLE/opt_a_digital_factory.py`
- `SLEEP_TRIPLE/opt_b_faceless_shorts.py`
- `SLEEP_TRIPLE/opt_c_crypto_yield.py`
- `SLEEP_TRIPLE/opt_d_alerts.py`
- `SLEEP_TRIPLE/opt_e_pod.py`
- `SLEEP_TRIPLE/opt_f_discovery.py`
- `SLEEP_TRIPLE/sleep_orchestrator.py`
- `SLEEP_TRIPLE/autonomous_master.py`

Implemented behavior:

- `degraded` is an explicit execution status.
- Offline ComfyUI produces a preserved prompt artifact but reports `degraded`.
- `SLEEP_TRIPLE/opt_e_pod.py` returns exit code `10` for degraded output.
- `sleep_orchestrator.py` accumulates degraded state across modules instead of checking only the last module.
- A degraded orchestrator run returns exit code `10`, not a clean zero.
- `autonomous_master.py` records a degraded final status when preflight or orchestration is unhealthy.
- Degraded output cannot be mistaken for a clean idempotent `ok` run.
- Tests and documentation describe the disabled-by-default POD lane accurately.
- Append-only audit and revenue records were not rewritten or compacted.

### Full Stack catalog test drift

Updated:

- `tests/test_full_stackyt_dashboard_browser.py`
- `tests/test_full_stackyt_freebuff.py`

The tests now match the validated local package snapshot:

- 115 catalog videos.
- 99 named catalog items.
- 99 execution records.

No production catalog generation logic was changed for this correction.

### Drive/RAG self-test portability

`TOOLS/drive_backup_rag/drive_backup_rag.py` had a Windows legacy-console failure in its self-test diagnostic because it printed the non-ASCII approximation character `≈`. The diagnostic now uses the ASCII-safe `~=` form. The exact Drive/RAG self-test passes 22/22 checks, including live Ollama reachability and the installed `nomic-embed-text` model; the full repository test suite passes.

### Graphify restoration and scoped graphs

The preserved Graphify source was used locally from:

- `.graphify/repos/Graphify-Labs/graphify`

The full workspace root graph update was attempted but exceeded the local time budget because the root contains the entire archive. No incomplete root graph was accepted.

Successful scoped code-only graphs:

| Scope | Output | Result |
|---|---|---|
| `SECURITY` | `SECURITY/graphify-out/` | 143 nodes, 155 edges, 12 communities |
| `SLEEP_TRIPLE` | `SLEEP_TRIPLE/graphify-out/` | 710 nodes, 1009 edges, 60 communities |
| `tests` | `tests/graphify-out/` | 713 nodes, 855 edges, 50 communities |
| `TOOLS/drive_backup_rag` | `TOOLS/drive_backup_rag/graphify-out/` | 55 nodes, 159 edges, 11 communities |

The graphs and reports are local generated artifacts. They were not used to delete or classify any project as obsolete. Graph queries confirmed the relationships between credential rotation, history scrubbing, ComfyUI health, degraded status, and orchestrator control flow.

## Verification Evidence

Completed checks:

```text
python -m pytest -q
........................................................................ [100%]
```

The full repository test suite passed after correcting the Full Stack snapshot expectations.

Additional passing checks:

- `python -m pytest -q SLEEP_TRIPLE/test_preflight.py SLEEP_TRIPLE/test_opt_e_pod.py`
- `python -m pytest -q tests/test_security_controls.py SLEEP_TRIPLE/test_preflight.py SLEEP_TRIPLE/test_opt_e_pod.py` — 43 passed.
- `python -m compileall -q SECURITY SLEEP_TRIPLE tests/test_security_controls.py`
- `python SECURITY/validate_security_docs.py` — 9 documents and 5 workflows checked.
- `python SECURITY/secret_scan.py` against the seven canonical security/index documents.
- All workflow YAML parsing and immutable SHA checks.
- Scoped Graphify `update --no-cluster` and `cluster-only --no-viz --no-label` for SECURITY, SLEEP_TRIPLE, and tests.
- Full `python -m pytest -q` — passed.

Not fully passing by design:

- Full tracked-history secret scan: known historical findings remain and the archive-scale scan can exceed the local execution window.
- Full root Graphify update: exceeded the local execution window; scoped graphs succeeded.
- Mypy was previously not completed within the local time budget during the earlier active-code pass; the repository-wide pytest and targeted quality checks were completed.

## Git and Archive Boundary

Protected local reference:

```text
backup-pre-rewrite
```

The current branch was `master`, and the protected reference existed before the latest remediation pass. A history rewrite was not safe because:

- The worktree contained unrelated and active modifications.
- The workspace had hundreds of changed paths.
- Many local and remote-tracking branches existed.
- The exact set of refs and external clones requiring coordination was not established.
- Provider rotation had not been completed.
- The encrypted forensic archive and checksum handoff were not verified in this session.

Read-only `git fsck --full --no-reflogs` completed but reported many dangling blobs/commits/tags and temporary pack garbage. No pruning or garbage collection was performed because the workspace is an archive and the objects may be recoverable evidence.

## Active-Code Enhancements Reviewed

The audit also reviewed and verified the active `AI_INFLUENCER_STUDIO` enhancement set that was present in the worktree:

- `adapters/automation.py`: added Postiz and Mixpost scheduling adapters with hosted-media validation for Postiz.
- `adapters/tts.py`: added the optional local Kokoro ONNX backend with explicit model/voice-file configuration and WAV/MP3 handling.
- `config.py`: added persisted Kokoro model and voices paths and corrected fresh-install environment-key loading.
- `model_registry.py`: added explicitly enabled OpenAI-compatible extra-provider catalogs and shared catalog parsing while preserving OpenRouter as the always-on hosted provider.
- `music_video_researcher.py`: added LLM-backed clip-fit judging with a deterministic token-overlap fallback.
- Documentation and focused tests were updated for the new configuration, provider catalog, and runtime behavior.
- The earlier refresh tuple regression was fixed so previous-snapshot catalog persistence continues to work.
- Kokoro documentation was corrected so it does not claim voice cloning that the adapter does not implement.

The AI Influencer Studio suite, lint checks, compilation, and targeted lockstep tests were included in the verification work. Mypy was not claimed as passed when the local execution window expired.

## External Actions Still Required

These actions require provider access, repository-admin access, or explicit coordinated approval:

1. Rotate or revoke all affected GitHub, Google, OpenAI-compatible, SSH, and webhook credentials.
2. Review provider audit and billing logs from the earliest exposure date.
3. Create replacement credentials outside the repository with least privilege and expiry.
4. Verify replacement credentials with harmless read-only requests.
5. Create and checksum an encrypted offline forensic archive using `SECURITY/FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md`, then verify a separate restore.
6. Freeze unrelated worktree changes or export them separately using the documented staged/unstaged/untracked/ignored-file procedure.
7. Define the complete ref policy for branches, tags, remote-tracking refs, and external clones.
8. Perform a reviewed `git filter-repo` rewrite in a maintenance window.
9. Validate the rewritten clone with `git fsck`, full secret scanning, and all required tests.
10. Coordinate remote force-updates and require recloning or repair of every old clone.
11. Review and narrow GitHub token scopes; the local GitHub CLI reported an invalid environment token and a separate keyring login with broad scopes. No credential was used.
12. Install and verify `git-filter-repo` inside the approved disposable rewrite clone; it is unavailable in the current shell.

## Operating Rules Going Forward

- Keep active secrets in provider secret stores or local environment files outside Git.
- Run changed-file scanning on every pull request.
- Run the full archive scan only as an explicit incident-audit job.
- Treat `degraded` as operationally meaningful and non-successful.
- Keep append-only JSONL records append-only.
- Refresh scoped Graphify outputs after code changes.
- Do not rewrite or prune archive history without a verified backup and ref policy.
- Keep this report factual; update status fields only when evidence changes.

## Related Documents

- `DOCS_INDEX.md`
- `SECURITY/INCIDENT_RESPONSE.md`
- `SECURITY/ROTATION_CHECKLIST.md`
- `SECURITY/EXTERNAL_ACTION_HANDOFF_2026-08-24.md`
- `SECURITY/DOCUMENTATION_MANIFEST_2026-08-24.md`
- `SECURITY/REWRITE_READINESS_2026-08-24.md`
- `SECURITY/FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md`
- `SECURITY/REWRITE_REF_SCOPE_2026-08-24.md`
- `SECURITY/secret_scan.py`
- `SECURITY/validate_security_docs.py`
- `tests/test_security_controls.py`
- `SECURITY/graphify-out/GRAPH_REPORT.md`
- `SLEEP_TRIPLE/graphify-out/GRAPH_REPORT.md`
- `tests/graphify-out/GRAPH_REPORT.md`
- `SLEEP_TRIPLE/README.md`
- `SLEEP_TRIPLE/DOCUMENTATION.md`
- `AGENTS.md` for the canonical workspace rules and preserved session context

## Change Record

- 2026-08-23: Documented the repository audit, security findings, CI hardening, SLEEP status corrections, Graphify restoration, test drift correction, verification evidence, and external blockers.
- 2026-08-23: Enhanced the scanner with fail-closed path handling and JSON output; added security documentation/workflow validation and regression tests. Refreshed SECURITY and tests Graphify scopes.
- 2026-08-24: Revalidated the current worktree, reran the full test suite, refreshed scoped Graphify code-only graphs and reports, and confirmed the tracked-history scan still exceeds the local audit window. Append-only SLEEP JSONL records and unrelated worktree changes were preserved.
- 2026-08-24: Added `SECURITY/EXTERNAL_ACTION_HANDOFF_2026-08-24.md` documenting the read-only GitHub/tooling boundary, current ref counts, and approval gates for provider rotation and history scrubbing; the initial SECURITY Graphify report contained 89 nodes, 105 edges, and 9 communities.
- 2026-08-24: Added `SECURITY/DOCUMENTATION_MANIFEST_2026-08-24.md` to map the complete remediation, runtime, Graphify, validation, archive, and approval-gated evidence set; the canonical validator then covered 7 documents.
- 2026-08-24: Added `SECURITY/REWRITE_READINESS_2026-08-24.md` with the current ref inventory, disposable-clone procedure, approval gates, post-rewrite checks, and explicit non-actions; the validator now covers 8 canonical documents.
- 2026-08-24: Refreshed the SECURITY Graphify scope after the readiness documentation; the report contained 112 nodes, 126 edges, and 11 communities at that point.
- 2026-08-24: Added and linked the forensic archive/export plan, then refreshed SECURITY Graphify; the report contained 128 nodes, 141 edges, and 12 communities at that point.
- 2026-08-24: Added `SECURITY/REWRITE_REF_SCOPE_2026-08-24.md` with the exact local and authoritative remote scrub namespaces, then refreshed SECURITY Graphify; the current report contains 143 nodes, 155 edges, and 12 communities.
- 2026-08-24: Recorded the maintainer's free-account clarification without weakening controls; free-tier keys remain bearer credentials and still require provider-specific rotation/revocation before any scrub.
- 2026-08-24: Fixed a Windows `charmap` portability failure in `TOOLS/drive_backup_rag/drive_backup_rag.py` by replacing a non-ASCII self-test diagnostic; the RAG self-test now passes 22/22 checks and the full pytest suite is green.
- 2026-08-24: Added `SECURITY/FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md` with a non-destructive GPG-encrypted forensic archive, restore-verification, and complete dirty-worktree export procedure; no archive was created in this documentation-only pass.
- 2026-08-24: Added `SECURITY/REWRITE_REF_SCOPE_2026-08-24.md`, defining `refs/heads/master`, all `refs/tags/*`, and authoritative `origin:refs/heads/*`/`origin:refs/tags/*` as the active scrub namespaces while preserving `backup-pre-rewrite` only in encrypted evidence; remote enumeration remains blocked by SSH authorization.
