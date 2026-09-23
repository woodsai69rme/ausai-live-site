"""Stage + commit DOCUMENTATION.md."""
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
     'SLEEP_TRIPLE/DOCUMENTATION.md'])

run(['git', '-C', REPO, 'status', '--short'])

r = run(['git', '-C', REPO, 'commit', '-m',
         'docs(SLEEP_TRIPLE): comprehensive system reference covering all 4 options + scheduler + helpers'])
print('--- last 4 commits ---')
run(['git', '-C', REPO, 'log', '--oneline', '-4'])
print()
print('DONE: documentation committed locally.')
