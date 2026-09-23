# Credential Rotation Checklist

Status: preparation only. No provider credential has been revoked or replaced by this document.

This workspace contains archived credential-shaped material. Treat every matching value as compromised until the owning provider confirms rotation or revocation. Free-tier or no-cost account status does not reduce the risk: bearer keys, OAuth secrets, SSH keys, and webhook URLs can still grant access, consume quotas, alter data, or impersonate the owner.

## Provider Workstreams

### GitHub

- [ ] Review GitHub account security and active personal access tokens.
- [ ] Revoke any token represented in `.git-credentials`, archived configs, session exports, or generated documentation.
- [ ] Review deploy keys, SSH keys, GitHub App tokens, and OAuth authorizations.
- [ ] Create replacement credentials with the smallest required scopes and an expiry.
- [ ] Verify a read-only repository operation with the replacement credential.
- [ ] Record token type, owner, scope, rotation time, and verification result without recording the value.

### Google

- [ ] Review Google Cloud API keys and OAuth client secrets associated with archived configuration files.
- [ ] Restrict replacement keys by API and application where possible.
- [ ] Rotate OAuth client secrets and invalidate affected sessions if required.
- [ ] Review Cloud audit logs from the earliest commit containing the material.
- [ ] Verify a harmless read-only API call using the replacement configuration.
- [ ] Record project, credential type, rotation time, and verification result without recording the value.

### OpenAI-Compatible Providers

- [ ] Identify the owning provider for every OpenAI-shaped key before revocation.
- [ ] Revoke the old key at the owning provider, including OpenRouter or other compatible gateways when applicable.
- [ ] Review usage and billing logs for unexpected activity.
- [ ] Create replacement keys outside the repository with provider-specific limits.
- [ ] Verify the application using a low-cost or read-only model/catalog request.
- [ ] Record provider, account/project, rotation time, and verification result without recording the value.

### SSH and Git Credentials

- [ ] Treat every tracked private key and credential helper file as compromised.
- [ ] Remove affected keys from authorized keys, deploy keys, CI secrets, and local agents.
- [ ] Generate replacement keys using a modern algorithm and a unique purpose.
- [ ] Update the local credential manager outside the repository.
- [ ] Verify access with the replacement key, then remove the old key from provider settings.
- [ ] Record key fingerprint and rotation time, never the private key material.

### Webhooks and Messaging

- [ ] Rotate any Discord, Slack, or equivalent webhook URL found by the scan.
- [ ] Review delivery logs and delete or disable the old webhook.
- [ ] Store the replacement URL only in the provider secret store or a local environment file outside Git.
- [ ] Send a harmless test message only after confirming the destination and retention policy.
- [ ] Record channel identity, rotation time, and verification result without recording the URL.

## Before History Scrubbing

- [ ] Complete provider rotation or revocation for every finding class.
- [ ] Confirm an encrypted, access-controlled forensic archive exists outside the active repository.
- [ ] Confirm the archive can be restored and its checksum is recorded.
- [ ] Confirm all local worktree changes are committed or separately exported; current worktree changes must not be included accidentally.
- [ ] Enumerate all local branches, tags, remote-tracking refs, and external clones.
- [ ] Agree on the exact paths and inline values to scrub.
- [ ] Agree on a maintenance window and remote force-update approval.
- [ ] Prepare a fresh clone destination for post-rewrite validation.

## Validation After Scrubbing

- [ ] Run `git fsck --full --no-reflogs`.
- [ ] Run the full scanner against the rewritten refs and working tree.
- [ ] Search all refs, not just `HEAD`, for the known file paths and replacement patterns.
- [ ] Verify the replacement credentials work without reintroducing secrets into Git.
- [ ] Notify every clone owner that old clones must be recloned or repaired.
- [ ] Keep the original encrypted archive immutable and access-controlled.

## Current Local Boundary

- Protected local ref: `backup-pre-rewrite`.
- Current branch: `master`.
- The worktree contains unrelated and active changes; no history rewrite is authorized from this state.
- The repository has many remote-tracking branches, so a remote scrub requires an explicit ref policy rather than rewriting only `master`.
