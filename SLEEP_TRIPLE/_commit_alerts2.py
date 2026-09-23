"""Stage + commit the alert-hardening batch (fanout + morning-digest + live-send-test)."""
import subprocess, sys

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

run(['git', '-C', REPO, 'add', '-f',
     'SLEEP_TRIPLE/compute_next_boundary.py',
     'SLEEP_TRIPLE/opt_d_alerts.py',
     'SLEEP_TRIPLE/opt_d_config.json',
     'SLEEP_TRIPLE/install_scheduler.bat',
     'SLEEP_TRIPLE/uninstall_scheduler.bat',
     'SLEEP_TRIPLE/_live_send_test.py'])

run(['git', '-C', REPO, 'status', '--short'])

r = run(['git', '-C', REPO, 'commit', '-m',
         'feat(opt_d): multi-channel fanout + morning-digest auto-fire + live-send helper'])
print('--- last 4 commits ---')
run(['git', '-C', REPO, 'log', '--oneline', '-4'])

print('\n--- attempting push (may fail rc=128 without PAT) ---')
p = run(['git', '-C', REPO, 'push', 'origin', 'master'], ok_rc=(0, 128))
if p.returncode == 128:
    print('\n!! push blocked (no PAT on shell). Commit is local-only.')
