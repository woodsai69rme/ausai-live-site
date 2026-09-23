"""Stage + commit opt_d_alerts fixes + opt_d_config.json tier thresholds."""
import subprocess, sys, os

REPO = r'C:\Users\karma'

def run(args, ok_rc=(0,)):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(f'$ {" ".join(args)}')
    print(f'rc={r.returncode}')
    if r.stdout.strip(): print(r.stdout.rstrip())
    if r.stderr.strip(): print('STDERR:', r.stderr.rstrip())
    if r.returncode not in ok_rc:
        print(f'  !! not in allowed rc set {ok_rc}')
        sys.exit(2)
    return r

# Stage relevant files only
run(['git', '-C', REPO, 'add', '-f',
     'SLEEP_TRIPLE/opt_d_alerts.py',
     'SLEEP_TRIPLE/opt_d_config.json'])

# Confirm staged set
run(['git', '-C', REPO, 'status', '--short'])

# Commit
r = run(['git', '-C', REPO, 'commit', '-m',
         'fix(opt_d): dry-run semantics + config tier thresholds + rate-limit debounce + Discord dedupe'])
print('--- commit done; showing last 3 commits ---')
run(['git', '-C', REPO, 'log', '--oneline', '-3'])

print('\n--- now attempting push (may fail without PAT) ---')
p = run(['git', '-C', REPO, 'push', 'origin', 'master'], ok_rc=(0, 128))
if p.returncode == 128:
    print('\n!! push blocked (no PAT on this shell). Commit is local-only.')
