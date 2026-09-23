"""Stage + commit the retry + wrapper + smoke-test batch.

Files:
- run_nightly.bat (NEW)
- run_morning_digest.bat (NEW)
- install_scheduler.bat (rewrite: single-quote /tr + drop parens-in-echo)
- opt_d_alerts.py (retry logic + safer coercion clamps + status_code sentinels + effective field)
- opt_d_config.json (retry_attempts=3, retry_backoff_seconds=5.0)
- _smoke_retry.py (NEW unit-test suite)
"""
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
     'SLEEP_TRIPLE/run_nightly.bat',
     'SLEEP_TRIPLE/run_morning_digest.bat',
     'SLEEP_TRIPLE/install_scheduler.bat',
     'SLEEP_TRIPLE/opt_d_alerts.py',
     'SLEEP_TRIPLE/opt_d_config.json',
     'SLEEP_TRIPLE/_smoke_retry.py'])

run(['git', '-C', REPO, 'status', '--short'])

r = run(['git', '-C', REPO, 'commit', '-m',
         'feat(opt_d): per-channel retry with sentinel, wrapper batters, _smoke_retry.py'],
        ok_rc=(0, 1))  # rc=1 if nothing to commit
if r.returncode == 1:
    print('(nothing new to commit)')
    sys.exit(0)

print('--- last 4 commits ---')
run(['git', '-C', REPO, 'log', '--oneline', '-4'])

print('\n--- attempting push (rc=128 acceptable if PAT missing) ---')
p = run(['git', '-C', REPO, 'push', 'origin', 'master'], ok_rc=(0, 128))
if p.returncode == 128:
    print('!! push blocked (no PAT on shell). Commit is local-only.')
