# Security and Remediation Documentation Manifest — 2026-08-24

## Purpose

This manifest is the cold-start map for the repository audit and remediation package. It records what is documented, where the evidence lives, which commands validate it, and which actions remain approval-gated. It contains no credential values.

## Golden Rules applied

- Nothing is obsolete.
- All projects remain permanent.
- All AI tools remain essential.
- Add, integrate, connect, and document.
- Enhance; do not reduce.
- Personal folders are read-only.
- Never commit secrets.
- Append-only records remain append-only.

## Documentation map

| Surface | Canonical artifact | Purpose | Current state |
|---|---|---|---|
| Cold-start navigation | `DOCS_INDEX.md` | Repository-wide pointer map and commands | Linked |
| Master audit | `SECURITY/AUDIT_REMEDIATION_STATUS_2026-08-23.md` | Findings, fixes, evidence, and blockers | Current through 2026-08-24 |
| Security index | `SECURITY/README.md` | Security controls and runbook entry point | Current |
| Incident response | `SECURITY/INCIDENT_RESPONSE.md` | Immediate containment and scrub procedure | Maintained |
| Rotation checklist | `SECURITY/ROTATION_CHECKLIST.md` | Provider-by-provider preparation and validation | Preparation only |
| External handoff | `SECURITY/EXTERNAL_ACTION_HANDOFF_2026-08-24.md` | Read-only provider/admin boundary and approval gates | Current |
| Rewrite readiness | `SECURITY/REWRITE_READINESS_2026-08-24.md` | Disposable-clone procedure, approvals, and tool prerequisites | Preparation only |
| Forensic archive/export | `SECURITY/FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md` | Encrypted evidence capture, restore verification, and dirty-worktree export | Plan prepared; not executed |
| Rewrite ref scope | `SECURITY/REWRITE_REF_SCOPE_2026-08-24.md` | Exact local/remote branch and tag selectors, exclusions, and authority gaps | Defined; approval-gated |
| Secret scanner | `SECURITY/secret_scan.py` | Fail-closed path and credential-pattern scanning | CI-integrated |
| Documentation validator | `SECURITY/validate_security_docs.py` | Link, workflow, action-pin, and security-doc checks | CI-integrated |
| Scanner regression tests | `tests/test_security_controls.py` | Boundary, placeholder, missing-file, and validator coverage | Passing |
| Drive/RAG self-test | `TOOLS/drive_backup_rag/drive_backup_rag.py` | Offline backup invariants, RAG health, Ollama reachability, and Windows-safe diagnostics | 22/22 passing |

## Remediation surfaces documented

### CI and workflows

The following workflows are covered by the master audit, validator, and immutable-action checks:

- `.github/workflows/ci.yml`
- `.github/workflows/claude-fix.yml`
- `.github/workflows/claude-review.yml`
- `.github/workflows/sleep-cash-preflight.yml`
- `.github/workflows/verify-dashboards.yml`

Documented controls include least-privilege permissions, reviewed immutable action SHAs, blocking quality checks, changed-file scanning, and robust changed-file selection.

### SLEEP_TRIPLE runtime

The master audit and SLEEP documentation cover:

- Lane modules A–F.
- Orchestration and autonomous-master status propagation.
- Offline ComfyUI behavior.
- Degraded exit code `10`.
- Idempotency protection.
- Append-only audit and revenue ledgers.
- Dashboard/runtime evidence.
- Disabled-by-default POD configuration.

Operational evidence remains in:

- `SLEEP_TRIPLE/SLEEP_TRIPLE_AUDIT.jsonl`
- `SLEEP_TRIPLE/REVENUE_LEDGER.jsonl`
- `SLEEP_TRIPLE/REVENUE_SUMMARY.md`
- `SLEEP_TRIPLE/dashboard.html`
- `SLEEP_TRIPLE/README.md`
- `SLEEP_TRIPLE/DOCUMENTATION.md`

Those runtime records are preserved and are not rewritten by documentation work.

### Active AI Influencer Studio

The master audit records the reviewed enhancement set:

- Postiz and Mixpost scheduling adapters.
- Optional local Kokoro ONNX TTS backend.
- Explicitly enabled OpenAI-compatible provider catalogs.
- LLM-backed clip-fit judging with deterministic fallback.
- Configuration, lockstep, compilation, and targeted test evidence.

The audit does not claim uncompleted mypy or external-provider verification as passed.

### Graphify evidence

Scoped local graphs and reports are maintained at:

- `SECURITY/graphify-out/GRAPH_REPORT.md`: **143 nodes, 155 edges, 12 communities**.
- `SLEEP_TRIPLE/graphify-out/GRAPH_REPORT.md`: **710 nodes, 1,009 edges, 60 communities**.
- `tests/graphify-out/GRAPH_REPORT.md`: **713 nodes, 855 edges, 50 communities**.
- `TOOLS/drive_backup_rag/graphify-out/GRAPH_REPORT.md`: **55 nodes, 159 edges, 11 communities**.

Graphify source is preserved at `.graphify/repos/Graphify-Labs/graphify`. The full repository graph is not treated as complete because the archive-scale root update exceeded the local execution window.

## Validation evidence

The current local validation contract is:

```bash
python SECURITY/validate_security_docs.py
python SECURITY/validate_security_docs.py --json
python SECURITY/secret_scan.py --paths-file changed-files.txt
python -m pytest -q
python -m compileall -q SECURITY SLEEP_TRIPLE tests/test_security_controls.py TOOLS/drive_backup_rag/drive_backup_rag.py
```

Latest verified results:

- Full pytest suite: passed, including the 22-check Drive/RAG self-test after the Windows console-encoding fix.
- Focused security/SLEEP suite: 43 passed.
- Security validator: 10 canonical docs and 5 workflows checked.
- Canonical security-document scan: passed.
- Python compilation: passed.
- Workflow YAML/action checks: 5 workflows, 0 mutable action refs.
- Scoped Graphify reports: present and metric-consistent; the RAG source scope is refreshed separately after the ASCII portability fix.

The explicit historical audit remains separate:

```bash
python SECURITY/secret_scan.py --tracked-only
```

It remains expected to find historical credential-shaped material and can exceed the local execution window. Its unresolved result is documented, not suppressed.

## Git and archive boundary

- Branch: `master`.
- Protected local ref: `backup-pre-rewrite`.
- Local branches: 2.
- Tags: 262.
- Remote-tracking refs: 179.
- The worktree includes active code, generated outputs, archived material, and append-only logs.
- Read-only `git fsck` reported dangling objects; no pruning or garbage collection was performed.

## Approval-gated actions

The following are not repository-side documentation tasks and remain untouched:

1. Provider credential rotation/revocation.
2. Provider audit and billing review.
3. Encrypted forensic archive creation and restore verification, following `SECURITY/FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md`.
4. Worktree freeze/export and complete ref policy definition, using the staged/unstaged/untracked/ignored-file procedure in that plan.
5. History rewrite in a fresh disposable clone.
6. Full all-ref post-rewrite scanning and testing.
7. Approved remote force-update and clone repair.

See `SECURITY/EXTERNAL_ACTION_HANDOFF_2026-08-24.md` for the exact handoff boundary, `SECURITY/REWRITE_READINESS_2026-08-24.md` for the disposable-clone execution checklist, `SECURITY/FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md` for the verified archive/export procedure, and `SECURITY/REWRITE_REF_SCOPE_2026-08-24.md` for the exact ref policy.

## Documentation maintenance rule

When evidence changes, update the master audit, this manifest, the security index, and `DOCS_INDEX.md` together. Never copy credential values into any of them. Keep runtime JSONL logs append-only and preserve the archive even when exposed material must later be scrubbed from active history.
