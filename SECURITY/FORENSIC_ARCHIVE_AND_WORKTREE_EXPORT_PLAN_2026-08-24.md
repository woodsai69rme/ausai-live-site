# Forensic Archive and Worktree Export Plan — 2026-08-24

## Purpose and boundary

This plan prepares a recoverable forensic snapshot of the current dirty workspace **without rewriting Git history**. It separates three things that must not be conflated:

1. **Forensic preservation:** an encrypted copy of Git metadata, all approved refs, current worktree bytes, and audit metadata.
2. **Worktree export:** a reproducible export of staged changes, unstaged changes, untracked files, and ignored files.
3. **Future remediation:** credential rotation and any history rewrite, which are separate approval-gated operations and are not performed here.

The current root is `C:/Users/karma`, on branch `master`, with protected ref `backup-pre-rewrite`, 262 tags, and 179 remote-tracking refs. It contains active source, generated material, archives, local tool state, and append-only runtime logs. Therefore, this plan must be run from a **new destination outside the repository**, never by staging, resetting, cleaning, pruning, or rewriting this worktree.

## Non-actions

The operator must not run any of the following as part of archive preparation:

- `git reset`, `git clean`, `git checkout`, `git restore`, or `git stash`.
- `git filter-repo`, `git filter-branch`, or any history rewrite.
- `git gc`, `git prune`, reflog expiration, or object deletion.
- `git push`, force-push, remote ref deletion, or provider API calls.
- A plain `git archive` as the only export; it omits dirty and untracked worktree state.
- A recursive archive of the entire parent directory; the file list must come from Git and remain repository-bound.

No credential values belong in this document, the manifest, command history, or verification report. The archive is encrypted evidence; encryption does not make exposed credentials safe, so provider rotation remains required.

## Required operator inputs and prerequisites

Before execution, record these values in a private operator log, not in Git:

- `CASE_ROOT`: a dedicated destination outside `C:/Users/karma`, preferably an access-controlled encrypted external volume.
- `CASE_ID`: an immutable case identifier and UTC timestamp.
- Archive custodian and authorized restore operator.
- Retention period and destruction policy, if any.
- GPG key/passphrase custody procedure. Never put a passphrase in a command line, environment variable, repository file, or chat.

Read-only prerequisites:

- GNU GPG is available (`gpg 2.4.9` was present in the last local check).
- GNU tar and `sha256sum` are available, or an equivalent approved archiver is documented.
- Sufficient free space exists for the worktree snapshot, Git metadata snapshot, bundle, restore test, and encrypted output.
- The destination is not inside the repository and is not a Git worktree.
- The operator has a second restore location with enough free space.

If any prerequisite is unknown, stop and record `blocked`; do not improvise with a plaintext archive or an in-place export.

## Artifact layout

Use a case directory outside the repository, for example `<CASE_ROOT>/<CASE_ID>/`:

```text
<CASE_ID>/
  payload/                         # plaintext staging area; access-controlled
    evidence/
      repository.all-refs.bundle
      git-directory.tar
      worktree.snapshot.tar
      tracked-staged.patch
      tracked-unstaged.patch
    metadata/
      case.json
      refs-before.txt
      status-before.porcelain
      file-list.z
      count-objects.txt
      fsck-before.txt
      sha256sums.txt
  forensic-payload.tar.gpg          # encrypted deliverable
  forensic-payload.tar.gpg.sha256   # checksum of encrypted deliverable
  restore-test/                     # disposable verification target
  verification.txt                  # no secret values
```

The plaintext `payload/` must remain outside the repository and have restricted filesystem permissions throughout preparation. Do not upload it or copy it to a cloud service. Whether it is retained after successful verification is an explicit retention decision; never remove it automatically against the permanent-preservation rule.

## Phase 1 — Freeze and capture read-only state

1. Stop writers that may change the worktree during capture, including scheduled jobs and editors that auto-generate files. Do not alter append-only logs.
2. Open a fresh shell at the repository root and set a case destination outside it:

```bash
ROOT="$(git rev-parse --show-toplevel)"
CASE_ROOT="<CASE_ROOT>"
CASE_ID="<CASE_ID>"
CASE="$CASE_ROOT/$CASE_ID"
PAYLOAD="$CASE/payload"
mkdir -p "$PAYLOAD/evidence" "$PAYLOAD/metadata" "$CASE/restore-test"
test "$(realpath "$CASE")" != "$(realpath "$ROOT")" \
  || { printf '%s\n' 'refusing destination inside repository' >&2; exit 1; }
```

3. Capture the exact repository and worktree boundary. These commands read Git state and write only to `CASE`:

```bash
printf '%s\n' "$ROOT" > "$PAYLOAD/metadata/root.txt"
git rev-parse --show-toplevel >> "$PAYLOAD/metadata/root.txt"
git rev-parse HEAD > "$PAYLOAD/metadata/head.txt"
git branch --show-current > "$PAYLOAD/metadata/branch.txt"
git show-ref > "$PAYLOAD/metadata/refs-before.txt"
git status --porcelain=v1 --untracked-files=all > "$PAYLOAD/metadata/status-before.porcelain"
git ls-files --cached --others --ignored --exclude-standard -z > "$PAYLOAD/metadata/file-list.z"
git count-objects -v > "$PAYLOAD/metadata/count-objects.txt"
git fsck --full --no-reflogs > "$PAYLOAD/metadata/fsck-before.txt" 2>&1 || true
```

`fsck` output is evidence, not a cleanup request. Preserve dangling-object findings exactly and do not run garbage collection.

4. Record the external ref inventory explicitly:

```bash
git branch --all --verbose --no-abbrev > "$PAYLOAD/metadata/branches.txt"
git tag --list --format='%(refname:short) %(objectname)' > "$PAYLOAD/metadata/tags.txt"
git for-each-ref --format='%(refname) %(objectname)' > "$PAYLOAD/metadata/all-refs.txt"
```

5. Capture separate tracked-change patches. Both are needed to reconstruct index and worktree state; neither changes the source tree:

```bash
git diff --binary > "$PAYLOAD/evidence/tracked-unstaged.patch"
git diff --cached --binary > "$PAYLOAD/evidence/tracked-staged.patch"
```

## Phase 2 — Export all worktree bytes and Git evidence

Use the Git-produced NUL-delimited file list so filenames are not parsed through whitespace or shell expansion. This includes cached/tracked files plus untracked and ignored files known to Git; tar preserves file contents, modes, and symlinks:

```bash
tar -C "$ROOT" --format=pax --null \
  --files-from="$PAYLOAD/metadata/file-list.z" \
  -cpf "$PAYLOAD/evidence/worktree.snapshot.tar"
```

Create a ref bundle for independent ref verification. The bundle does not replace the raw Git-directory capture because dangling objects and reflogs are forensic evidence too:

```bash
git bundle create "$PAYLOAD/evidence/repository.all-refs.bundle" --all
git bundle verify "$PAYLOAD/evidence/repository.all-refs.bundle" \
  > "$PAYLOAD/metadata/bundle-verify.txt"
```

Capture the raw Git directory without touching it. This preserves local objects, reflogs, index state, hooks, and repository metadata for authorized forensic restoration:

```bash
git_dir="$(git rev-parse --git-dir)"
tar -C "$ROOT" --format=pax -cpf "$PAYLOAD/evidence/git-directory.tar" "$git_dir"
```

If `git rev-parse --git-common-dir` points outside `git_dir`, stop and document that linked worktree/common-directory layout before adding the common directory to the approved evidence set. Never silently follow paths outside the repository boundary.

## Phase 3 — Build and encrypt the payload

Create a metadata record containing only non-secret facts: case ID, UTC timestamps, repository root label, HEAD, branch, tool versions, file-list hash, and the current ref counts. Then hash every plaintext payload file before encryption:

```bash
{
  printf '%s\n' "case_id=$CASE_ID"
  date -u +%Y-%m-%dT%H:%M:%SZ
  git --version
  gpg --version | sed -n '1p'
  tar --version | sed -n '1p'
  printf 'head='; git rev-parse HEAD
  printf 'branch='; git branch --show-current
  printf 'local_branches='; git branch --format='%(refname:short)' | wc -l
  printf 'tags='; git tag | wc -l
  printf 'remote_tracking='; git for-each-ref refs/remotes --format='%(refname)' | wc -l
} > "$PAYLOAD/metadata/case.txt"

(
  cd "$PAYLOAD"
  find . -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 sha256sum
) > "$PAYLOAD/metadata/sha256sums.txt"
```

Stream the payload directly into GPG so no second unencrypted tarball is created. GPG must prompt through approved pinentry; do not supply a passphrase inline:

```bash
tar -C "$PAYLOAD" --format=pax -cpf - . \
  | gpg --symmetric --cipher-algo AES256 --s2k-digest-algo SHA512 \
      --output "$CASE/forensic-payload.tar.gpg"
sha256sum "$CASE/forensic-payload.tar.gpg" \
  > "$CASE/forensic-payload.tar.gpg.sha256"
```

For higher-assurance custody, an authorized GPG signing key may create a detached signature in addition to the SHA-256 checksum. Record only the signer key fingerprint and verification result; never place private-key material in the repository or payload.

## Phase 4 — Restore verification

Restoration must use a separate empty directory, never the source worktree and never the payload directory:

```bash
RESTORE="$CASE/restore-test/restored-payload"
mkdir -p "$RESTORE"
gpg --decrypt "$CASE/forensic-payload.tar.gpg" \
  | tar -C "$RESTORE" -xpf -

(
  cd "$RESTORE"
  sha256sum -c metadata/sha256sums.txt
)
git bundle verify "$RESTORE/evidence/repository.all-refs.bundle"
```

The restore is successful only if all of the following are true:

- GPG decrypts the entire stream without an integrity/MDC error.
- Every recorded payload checksum passes.
- `git bundle verify` passes.
- `metadata/refs-before.txt`, `status-before.porcelain`, `file-list.z`, `count-objects.txt`, and `fsck-before.txt` are present and byte-identical to the originals.
- The worktree snapshot can be listed and extracted without path traversal outside the restore directory.
- `git-directory.tar` can be restored into a second disposable location for forensic inspection without opening or modifying the source worktree.
- The encrypted archive checksum matches `forensic-payload.tar.gpg.sha256`.

Write only pass/fail results, timestamps, tool versions, destination labels, and hashes to `verification.txt`. Do not copy scanner matches or credential values into the verification report.

## Phase 5 — Prove the source worktree was not changed

After all capture and restore steps, rerun the read-only state capture into a temporary file outside the repository and compare it with the initial evidence:

```bash
git status --porcelain=v1 --untracked-files=all > "$CASE/status-after.porcelain"
sha256sum "$PAYLOAD/metadata/status-before.porcelain" "$CASE/status-after.porcelain"

git rev-parse HEAD
# Must equal metadata/head.txt.
git show-ref > "$CASE/refs-after.txt"
# Must be byte-identical to metadata/refs-before.txt.
```

If status, HEAD, refs, or the protected `backup-pre-rewrite` ref differ, mark the case failed and investigate. Do not repair by resetting or checking out; preserve both observations.

## Worktree reconstruction test (optional, fresh clone only)

To prove the export is usable without touching this repository, use a separately approved disposable clone/directory:

```bash
git clone --no-local <approved-source-url> <fresh-test-clone>
cd <fresh-test-clone>
git apply --cached <CASE>/restore-test/restored-payload/evidence/tracked-staged.patch
git apply <CASE>/restore-test/restored-payload/evidence/tracked-unstaged.patch
# Extract worktree.snapshot.tar only into a controlled staging directory,
# then compare untracked/ignored paths and hashes before copying them into
# the fresh test clone.
git status --porcelain=v1 --untracked-files=all --ignored
```

The reconstruction test is evidence only. It must not be run in `C:/Users/karma`, and it must not be used to rewrite refs or push a remote.

## Acceptance record

Mark the plan complete only when the private operator record contains:

- [ ] Destination confirmed outside the repository and access-controlled.
- [ ] Process freeze window recorded.
- [ ] Initial HEAD, branch, all refs, status, file list, object count, and fsck output captured.
- [ ] Staged and unstaged patches captured.
- [ ] Full Git directory, all-ref bundle, and Git-listed worktree snapshot exported.
- [ ] Payload SHA-256 manifest created without secret values.
- [ ] GPG encryption completed with operator-controlled passphrase/key custody.
- [ ] Encrypted archive checksum recorded.
- [ ] Separate restore completed and all checksums passed.
- [ ] Bundle verification passed.
- [ ] Source HEAD, refs, status, and protected ref unchanged.
- [ ] Custodian, retention, and restore location recorded outside Git.
- [ ] No credential rotation, history rewrite, pruning, force-push, or remote mutation performed.

## Current blockers and next handoff

This document prepares the archive and export procedure; it does not claim that an archive has already been created. The last tool inventory found GPG and tar available, but `age`, `7z`, and `git-filter-repo` unavailable. An operator must supply the external destination and encryption custody decision before execution.

After a verified archive exists, the next approval-gated steps are provider credential rotation/revocation, complete ref-policy definition, and any history rewrite in a fresh disposable clone. Preserve this archive even if active history is later scrubbed.

## Related documents

- `SECURITY/REWRITE_READINESS_2026-08-24.md`
- `SECURITY/EXTERNAL_ACTION_HANDOFF_2026-08-24.md`
- `SECURITY/ROTATION_CHECKLIST.md`
- `SECURITY/INCIDENT_RESPONSE.md`
- `SECURITY/DOCUMENTATION_MANIFEST_2026-08-24.md`
- `SECURITY/AUDIT_REMEDIATION_STATUS_2026-08-23.md`
