# Disposable-Clone Rewrite Ref Scope — 2026-08-24

## Decision status

**Scope defined for approval; no rewrite or remote mutation performed.** This document converts the rewrite-readiness checklist into an exact ref policy for the current repository. The policy applies only to a future fresh/disposable clone after encrypted archive verification and provider credential containment. Free-tier accounts and no-cost keys remain security-sensitive and do not bypass containment or approval gates.

The current source repository remains untouched. The protected evidence ref and all current archive objects must remain available in the encrypted forensic archive; they must not be replaced by a rewritten ref in this worktree.

## Current read-only inventory

Observed locally from `C:/Users/karma`:

| Ref family | Exact current scope | Count | Current state |
|---|---|---:|---|
| Local branches | `refs/heads/master`, `refs/heads/backup-pre-rewrite` | 2 | `master` is active; `backup-pre-rewrite` is protected evidence |
| Tags | Every current `refs/tags/*` ref | 262 | All are in the local tag namespace and require review/recreation in the clean repo |
| Remote-tracking branches | Every leaf `refs/remotes/origin/*`, excluding symbolic `refs/remotes/origin/HEAD` | 178 | Local cache of origin branches; not itself a push target |
| Remote-tracking symbolic ref | `refs/remotes/origin/HEAD -> refs/remotes/origin/main` | 1 | Recreate after the clean remote is established |
| Remote | `origin` = `git@github.com:woodsai69rme/ausai-live-site.git` | 1 | Authoritative enumeration was not available because SSH returned `Permission denied (publickey)` |

Observed object IDs are evidence metadata, not authorization to update a remote. Re-enumerate the authoritative remote refs during the approved maintenance window.

## Recommended exact scrub scope

### 1. Active local branch to publish

Scrub and publish exactly:

```text
refs/heads/master
```

The rewritten active repository should expose one canonical branch named `master` unless the maintainer approves a different default branch. Do not rewrite the current `master` in place; produce it in a fresh clone and validate it first.

### 2. Protected local evidence branch

Do **not** carry this ref into the rewritten active repository:

```text
refs/heads/backup-pre-rewrite
```

Preserve it unchanged only inside the verified encrypted forensic archive. Its current object ID is recorded in `SECURITY/REWRITE_READINESS_2026-08-24.md`. This is a preserve-only evidence boundary, not a clean-repository ref. If an active repository must retain a branch with this name, create a separately scrubbed branch in the disposable clone; never move or overwrite the original evidence ref.

This exclusion is intentional: importing the original `backup-pre-rewrite` into an active clone would keep an unsanitized reachable history and defeat an all-ref clean scan.

### 3. Tags

Scrub the complete tag namespace:

```text
refs/tags/*
```

The current local baseline is all 262 tag refs. No tag is exempt based only on its name, date, version format, or apparent release status. After filtering:

- Recreate only the approved tag names at their rewritten target commits.
- Review annotated tag messages and tagger metadata.
- Treat existing tag signatures as invalid after rewriting; re-sign only with an approved signing key.
- Do not preserve original tag refs in the active clean repository. Keep original tag objects only in the encrypted archive.

The exact names must be materialized from the pre-rewrite inventory and compared one-for-one with the approved keep/recreate list before any remote update. A tag count alone is not sufficient approval evidence.

### 4. Remote branches on `origin`

The authoritative remote scrub target is:

```text
origin:refs/heads/*
```

That means every branch currently published on the GitHub repository, including branches that are not present in the local cache. Do not scrub only `master`, only the default branch, or only the 178 locally cached leaf refs.

The 178 current local tracking leaves are the baseline evidence set:

```text
refs/remotes/origin/*    # leaf refs only; origin/HEAD is symbolic metadata
```

They are not remote refs and must not be force-pushed as if they were. Before any remote operation, an authorized read-only `git ls-remote --heads origin` must produce the authoritative branch list. Since that enumeration currently failed with SSH public-key authorization, the remote branch name list remains **pending operator access**. Any branch found remotely but absent from the local cache must be added to the approved scrub set, not ignored.

After the clean remote is established, recreate the symbolic default pointer only after the maintainer confirms the default branch:

```text
refs/remotes/origin/HEAD -> refs/remotes/origin/main
```

The symbolic pointer is metadata, not an independent branch history.

### 5. Remote tags on `origin`

The authoritative remote tag scrub target is:

```text
origin:refs/tags/*
```

Enumerate this independently with `git ls-remote --tags origin`. Exclude only peeled display lines ending in `^{};` they are not independent tag refs. The current local count of 262 is a baseline, not proof that the remote has exactly the same tags. Any remote-only tag must be included in the scrub/recreate decision.

## Ref families that must be checked and not silently omitted

Before filtering, produce an all-ref inventory and fail closed if any unexpected namespace exists:

```bash
git for-each-ref --format='%(refname) %(objectname) %(symref)' > refs-all-before.txt
```

The approved active rewrite set is:

```text
refs/heads/master
refs/tags/*
origin:refs/heads/*       # authoritative remote set, fetched/read separately
origin:refs/tags/*        # authoritative remote set, fetched/read separately
```

The preserve-only set is:

```text
refs/heads/backup-pre-rewrite  # encrypted archive only; never active output
```

Any `refs/replace/*`, `refs/notes/*`, `refs/stash`, pull-request refs, Gerrit/change refs, alternate object databases, linked-worktree refs, or other namespace discovered by the inventory requires explicit disposition before the rewrite. It must not be silently dropped or assumed clean. Reflogs, unreachable/dangling objects, and original Git metadata remain forensic evidence in the encrypted archive even though they are not active publish refs.

## Required pre-rewrite comparison files

In the disposable clone and private operator log, retain these files outside Git:

```text
refs-all-before.txt
local-branches-before.txt
tags-before.txt
remote-tracking-before.txt
remote-heads-authoritative-before.txt
remote-tags-authoritative-before.txt
approved-keep-and-recreate-list.txt
approved-excluded-evidence-refs.txt
```

The approved list must contain full refnames, not abbreviated names. Compare names and object IDs before filtering; compare names, rewritten object IDs, and scan results afterward. Do not include credential values in these files.

## Post-rewrite ref acceptance criteria

The clean disposable clone is acceptable only when:

- `refs/heads/master` exists and is the approved rewritten default branch.
- `refs/heads/backup-pre-rewrite` is absent from the active clean clone.
- Every retained tag is explicitly approved and points to a rewritten object; no original tag ref remains active.
- Every authoritative `origin:refs/heads/*` branch is represented by an approved rewritten branch or an explicitly documented retirement decision.
- Every authoritative `origin:refs/tags/*` tag is represented by an approved rewritten tag or an explicitly documented retirement decision.
- No unexpected ref namespace exists.
- The all-ref secret scan and known-path/pattern checks pass across every retained ref.
- `git fsck --full --no-reflogs` reports no unexpected missing objects.
- The original encrypted archive remains immutable and independently restorable.

Remote deletion, force-update, branch protection changes, default-branch changes, and clone repair require separate repository-admin approval. None is authorized by this document.

## Current verification and blockers

- Local enumeration confirmed: 2 local branches, 262 tags, 178 remote-tracking leaf refs, and one symbolic `origin/HEAD` pointer.
- `origin` authoritative enumeration was attempted read-only and failed with `Permission denied (publickey)`; no remote state changed.
- Current local `HEAD` and `backup-pre-rewrite` remain unchanged.
- The exact remote branch/tag list cannot be certified until authorized read-only remote access is available.
- Provider rotation/revocation, encrypted archive restore verification, `git-filter-repo` installation, and repository-admin approval remain prerequisites.

## Related documents

- `SECURITY/REWRITE_READINESS_2026-08-24.md`
- `SECURITY/FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md`
- `SECURITY/EXTERNAL_ACTION_HANDOFF_2026-08-24.md`
- `SECURITY/ROTATION_CHECKLIST.md`
- `SECURITY/AUDIT_REMEDIATION_STATUS_2026-08-23.md`
