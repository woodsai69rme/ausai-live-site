# Credential Incident Response

This workspace contains preserved project and machine artifacts. A credential-shaped value in Git history must be treated as compromised even when the related service appears unused.

## Immediate containment

1. Do not paste the value into chat, issues, logs, or a new commit.
2. Rotate or revoke the credential at its provider:
   - GitHub personal access tokens and deploy keys
   - Google API keys and OAuth client secrets
   - OpenAI-compatible provider keys
   - SSH keys and webhook URLs
3. Check provider audit logs for use since the first commit containing the value.
4. Record the provider, credential type, rotation timestamp, and affected repository in the incident record. Do not record the secret itself.
5. Update local environment stores outside Git, then verify the application with a harmless authenticated read-only request.

## Preserve without re-exposing

The Golden Rules require preserving projects and historical evidence. Preserve the original repository/archive as an encrypted, access-controlled offline copy. Do not keep active credentials in that copy unless the archive is specifically required for forensic purposes and is encrypted.

The active working tree should contain only placeholders such as `.env.example`. Existing tracked secret-shaped files remain an incident until they are rotated and removed from the active history.

## History scrubbing

History rewriting is destructive to commit IDs and must be coordinated with every clone and remote. After rotation and an encrypted archive is verified:

```bash
# Review first; do not run until the archive and rotation are confirmed.
git filter-repo --sensitive-data-removal --invert-paths --path <known-secret-file>
# For inline values, use a reviewed replacements file with git filter-repo.
git filter-repo --replace-text <reviewed-replacements-file>
git fsck --full --no-reflogs
```

Then force-update the remote only through an approved maintenance window. Every clone must be recloned or explicitly repaired; old clones can reintroduce the secret.

## Local checks

The normal changed-file scanner is fail-closed. It rejects paths outside the repository, reports missing or unreadable files, scans duplicate inputs once, and emits only path/line/pattern metadata.

```bash
# Human-readable changed-file scan
python SECURITY/secret_scan.py --paths-file changed-files.txt

# Machine-readable result for CI tooling
python SECURITY/secret_scan.py --json --paths-file changed-files.txt

# Documentation and workflow guardrail validation
python SECURITY/validate_security_docs.py
```

Run the dependency-free scanner against newly changed files in normal CI:

```bash
python SECURITY/secret_scan.py --paths-file changed-files.txt
```

Run the full tracked-file audit when investigating the archive:

```bash
python SECURITY/secret_scan.py --tracked-only
```

The full audit is expected to report historical findings until the rotation and scrub are complete. The scanner intentionally prints only path, line, and pattern class, never the matched value.

## CI policy

- Pull requests fail when a changed file contains a high-confidence credential pattern.
- Credentials belong in provider secrets or local environment stores, never in source files.
- Examples must use placeholders and must not resemble usable tokens.
- Action workflows should use least-privilege permissions and pinned, reviewed action versions.
