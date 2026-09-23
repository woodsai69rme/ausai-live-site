# SSH Push Setup — First-Time Guide for `git push origin master`

## Goal

Wire Windows-side `ssh-agent` + `~/.ssh/config` so that, after you paste
`~/.ssh/id_ed25519.pub` into GitHub, `git push origin master` works from
Git Bash **without generating a new key**.

## What changed in this round

- `~/.ssh/config` was created with a `Host github.com` block pointing at the
  existing `~/.ssh/id_ed25519` key.
- This cheat sheet was rewritten around that existing key.
- No new key is needed; just register the existing public key on GitHub and
  load the private key into an SSH agent.

## Quick check — do you already have the key?

Open Git Bash and run:

```bash
ls -la ~/.ssh/id_ed25519*
```

You should see:

```
/c/Users/karma/.ssh/id_ed25519      # private key
/c/Users/karma/.ssh/id_ed25519.pub  # public key (this goes to GitHub)
```

If those files exist, skip to **Step 3**. If they do NOT exist, run this once
to create them (press `<Enter>` twice for no passphrase, or set one):

```bash
ssh-keygen -t ed25519 -C "karma@karmapc.local" -f ~/.ssh/id_ed25519
```

## Step 1 — Create/refresh `~/.ssh/config`

This file already exists after this round. Contents:

```text
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes
    # accept-new is supported by OpenSSH 7.6+. On older clients, remove this
    # line and run: ssh-keyscan github.com >> ~/.ssh/known_hosts
    StrictHostKeyChecking accept-new
```

If you ever need to recreate it manually:

```bash
# Ensure the SSH directory has the right permissions
mkdir -p ~/.ssh
chmod 700 ~/.ssh

cat > ~/.ssh/config << 'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes
    # accept-new is supported by OpenSSH 7.6+. On older clients, remove this
    # line and run: ssh-keyscan github.com >> ~/.ssh/known_hosts
    StrictHostKeyChecking accept-new
EOF

chmod 600 ~/.ssh/config
```

## Step 2 — Start ssh-agent and load the key

### Option A — Persistent Windows OpenSSH service (recommended)

This survives reboots once enabled.

1. Open **PowerShell as Administrator**.
2. Run:

```powershell
# Enable the service to start automatically
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent

# Load the existing key (you will be prompted for a passphrase if you set one)
ssh-add "$env:USERPROFILE\.ssh\id_ed25519"

# Verify
ssh-add -l
```

3. Close PowerShell; go back to Git Bash.

> **Note for Git Bash:** When the Windows `ssh-agent` service is running,
> Git Bash should see the same agent. If `ssh-add -l` fails with
> "Could not open a connection to your authentication agent", use Option B.

### Option B — Session-scoped agent in Git Bash (fallback)

Use this if Option A fails or you do not have admin rights.

```bash
# Start an ssh-agent for this shell session
eval "$(ssh-agent -s)"

# Load the key
ssh-add ~/.ssh/id_ed25519

# Verify
ssh-add -l
```

> This must be re-run every time you open a new Git Bash window, so Option A
> is preferred on Windows 11.

## Step 3 — Register the public key on GitHub

1. Copy your public key to the clipboard:

```bash
cat ~/.ssh/id_ed25519.pub
```

2. Open <https://github.com/settings/keys>.
3. Click **New SSH key**.
4. Fill in:
   - **Title**: `Karma Win11 — ausai-live-site`
   - **Key type**: Authentication Key
   - **Key**: paste the entire output from `cat ~/.ssh/id_ed25519.pub`
5. Click **Add SSH key**.

## Step 4 — Test

Wait ~10 seconds, then in Git Bash run:

```bash
ssh -T git@github.com
```

Expected output:

```
Hi woodsai69rme! You've successfully authenticated, but GitHub does not provide shell access.
```

Then:

```bash
cd /c/Users/karma
git push origin master
```

Expected: the local commits upload cleanly to `origin/master`.

## Step 5 — Make it survive reboots (PowerShell, run once)

If you used Option A, the service is already set to `Automatic`. After a
reboot, the agent starts, but the key is not loaded automatically. You can add
the key on login with this one-liner (PowerShell as Admin). If you set a
passphrase when creating the key, `ssh-add` will prompt for it:

```powershell
ssh-add "$env:USERPROFILE\.ssh\id_ed25519"
```

To avoid typing it after every reboot, create a small Scheduled Task or add
the command to your PowerShell profile:

```powershell
# Add to $PROFILE (create if missing)
New-Item -Path $PROFILE -ItemType File -Force
Add-Content -Path $PROFILE -Value 'ssh-add "$env:USERPROFILE\.ssh\id_ed25519" 2>$null'
```

> **Security note:** This keeps the key loaded in the Windows ssh-agent after
> you log in. Do not use this on a shared machine.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Permission denied (publickey)` | Key not registered on GitHub, or wrong key loaded | Re-copy `~/.ssh/id_ed25519.pub` to GitHub; run `ssh-add -l` to confirm the fingerprint matches |
| `Could not open a connection to your authentication agent` | ssh-agent not running | Start the Windows `ssh-agent` service (Option A) or run `eval "$(ssh-agent -s)"` (Option B) |
| `ssh-add: No such file or directory` | Key path is wrong | Verify `ls ~/.ssh/id_ed25519` |
| `ssh-add: identity file ... permissions are too open` | Private key permissions too permissive | Run `chmod 600 ~/.ssh/id_ed25519` |
| `git push` still asks for a password | Remote URL is HTTPS, not SSH | Run `git remote set-url origin git@github.com:woodsai69rme/ausai-live-site.git` |
| `Host key verification failed` | GitHub host key not accepted | Ensure `StrictHostKeyChecking accept-new` is in `~/.ssh/config`, or run `ssh-keyscan github.com >> ~/.ssh/known_hosts` |

## One-shot verification script

Save as `~/ssh_push_check.sh`, then run it after completing Steps 1–3:

```bash
#!/usr/bin/env bash
# Note: do NOT use set -e here; some commands are expected to fail until the
# public key is registered on GitHub.

echo "=== SSH config ==="
cat ~/.ssh/config

echo ""
echo "=== Loaded keys ==="
ssh-add -l 2>&1 || true

echo ""
echo "=== Git remote ==="
git -C /c/Users/karma remote -v

echo ""
echo "=== GitHub auth test ==="
ssh -T git@github.com 2>&1 || true

echo ""
echo "=== Push dry-run ==="
git -C /c/Users/karma push --dry-run origin master 2>&1 || true

if ssh-add -l >/dev/null 2>&1; then
    echo ""
    echo "PASS: ssh-agent is running and a key is loaded."
    echo "NEXT: Register ~/.ssh/id_ed25519.pub on GitHub if you have not already."
else
    echo ""
    echo "WARN: ssh-agent is not running or no key is loaded."
    echo "NEXT: Start ssh-agent and run ssh-add ~/.ssh/id_ed25519."
fi
```

Run it with:

```bash
bash ~/ssh_push_check.sh
```

## Once it works

- `git push origin master` should upload all local-only commits.
- Verify at <https://github.com/woodsai69rme/ausai-live-site/commits/master>.
