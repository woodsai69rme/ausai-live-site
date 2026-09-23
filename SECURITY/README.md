# Security Documentation

This directory contains the repository security controls and the current audit record. It does not contain active credentials.

## Start Here

| Need | Document or command |
|---|---|
| Current complete status | `AUDIT_REMEDIATION_STATUS_2026-08-23.md` |
| Full audit + Golden Rules (2026-09-17) | `FULL_AUDIT_AND_GOLDEN_RULES_2026-09-17.md` |
| Approval-gated external handoff | `EXTERNAL_ACTION_HANDOFF_2026-08-24.md` |
| Complete documentation manifest | `DOCUMENTATION_MANIFEST_2026-08-24.md` |
| Clean-clone rewrite readiness | `REWRITE_READINESS_2026-08-24.md` |
| Encrypted forensic archive/export plan | `FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md` |
| Exact disposable-clone ref scope | `REWRITE_REF_SCOPE_2026-08-24.md` |
| Respond to exposed credential material | `INCIDENT_RESPONSE.md` |
| Track provider rotation and rewrite prerequisites | `ROTATION_CHECKLIST.md` |
| Scan changed files | `python SECURITY/secret_scan.py --paths-file changed-files.txt` |
| Scan selected files | `python SECURITY/secret_scan.py path/to/file1 path/to/file2` |
| Run the explicit tracked-file incident audit | `python SECURITY/secret_scan.py --tracked-only` |
| Review security relationships | `graphify-out/GRAPH_REPORT.md` |
| Validate docs and workflow guardrails | `python SECURITY/validate_security_docs.py` |
| Get machine-readable scan output | `python SECURITY/secret_scan.py --json path/to/file` |

## Control Boundaries

- The scanner reports path, line, and pattern class only. It never prints matched values.
- Scanner paths are normalized to the Git worktree and symlink/path traversal outside the repository fails closed.
- Missing or unreadable paths fail closed instead of being silently skipped.
- Explicit placeholder syntax is removed before matching; generic words such as `example` do not suppress a real credential-shaped value.
- Duplicate input paths are scanned once.
- CI scans changed files and fails on high-confidence credential patterns.
- Historical findings remain an incident until provider rotation and coordinated history scrubbing are complete.
- The permanent archive is preserved; preservation does not make exposed credentials safe.
- Active credentials belong in provider secret stores or local environment files outside Git.
- History rewriting requires an encrypted archive, provider rotation, a complete ref policy, and coordinated approval.

## Validation Contract

Run the complete local guardrail check:

```bash
python SECURITY/validate_security_docs.py
python SECURITY/validate_security_docs.py --json
```

The validator checks that the canonical security documents exist, repository references resolve, workflow YAML parses, all external workflow actions use 40-character commit SHAs, and the security documents contain no high-confidence credential patterns. It currently covers 9 canonical documents and 5 workflows.

The command is safe and read-only. It does not contact providers, mutate credentials, rewrite history, or modify append-only runtime records.

## Current Status

Repository-side work is complete and tested. External work remains pending:

- Provider credential rotation/revocation.
- Provider audit-log review.
- Encrypted archive verification.
- Coordinated Git-history rewrite.
- Remote force-update and clone repair.

The latest read-only provider/admin boundary is recorded in `EXTERNAL_ACTION_HANDOFF_2026-08-24.md`. The clean-clone procedure is recorded in `REWRITE_READINESS_2026-08-24.md`. See the master status report for evidence and the exact boundary of work performed.

## Related Operational Evidence

- `SECURITY/graphify-out/GRAPH_REPORT.md` covers the 143-node security/remediation relationship graph (155 edges, 12 communities), including the forensic archive/export and exact ref-scope plans.
- `SECURITY/DOCUMENTATION_MANIFEST_2026-08-24.md` maps the complete remediation documentation set.
- `SECURITY/REWRITE_READINESS_2026-08-24.md` records the disposable-clone procedure and current tool prerequisite.
- `SECURITY/FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md` records the non-destructive encrypted archive, restore verification, and dirty-worktree export procedure.
- `SECURITY/REWRITE_REF_SCOPE_2026-08-24.md` defines the exact local branch, tag, remote-tracking baseline, and authoritative remote namespaces for a future scrub.
- `TOOLS/drive_backup_rag/drive_backup_rag.py` contains the ASCII-safe Drive/RAG self-test used by the full suite.
- `SLEEP_TRIPLE/graphify-out/GRAPH_REPORT.md` covers degraded dependency and orchestrator relationships.
- `TOOLS/drive_backup_rag/graphify-out/GRAPH_REPORT.md` covers the 55-node Drive/RAG control graph.
- `SLEEP_TRIPLE/SLEEP_TRIPLE_AUDIT.jsonl` is append-only runtime evidence.
- `.github/workflows/ci.yml` contains the blocking changed-file scan.
- `.github/workflows/claude-fix.yml` and `.github/workflows/claude-review.yml` contain the hardened automation permissions and immutable action references.
