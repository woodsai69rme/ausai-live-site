import os
for root, dirs, files in os.walk(r'C:\Users\karma'):
    # skip system/large dirs
    skip = {'Program Files', 'Windows', 'System32', '.git', 'node_modules', '.cache',
            '.abacusai', '.agent', '.claude', '.aider-desk', '.uv', '.bun', '.npm',
            '.azure', '.aws', '.chrome', '.chromium', '.dotnet', '.emacs', '.eslint',
            '.firefox', '.flutter', '.gitconfig', '.java', '.npm', '.oracle',
            '.p2', '.ripgrep', '.rustup', '.ssh', '.subversion', '.vim', '.vscode',
            '.webpack', '.wget', '.yarn', '.conda', '.docker', '.kube', '.terraform',
            'AppData', 'Library', 'Local', 'Roaming'}
    dirs[:] = [d for d in dirs if d not in skip and not d.startswith('.')]
    for f in files:
        fl = f.lower()
        if '17092026185324' in fl or 'woodato' in fl or 'woodato' in root.lower():
            print(os.path.join(root, f))
print('SEARCH DONE')
