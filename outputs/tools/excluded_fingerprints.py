"""Fingerprints of excluded source material, and a check against them (Claude, 15 Oct 2026). On Windows:

    python -I excluded_fingerprints.py make <folder> [<folder> ...]   # writes h/work/excluded-fingerprints/*.jsonl.gz
    python -I excluded_fingerprints.py check [<tree> ...]             # default: every file git tracks in h

The owner (15 Oct) had the SWG-Source clones in work/research (excluded by AGENTS.md, never used) moved to the Recycle
Bin. Before that, `make` records each file's relative path, size and SHA-256, plus the clone's origin and commit, so the
project keeps "what not to reference" without keeping the code. `check` hashes our files and reports any that is
byte-identical to an excluded one (it cannot see rewritten or partial copies: provenance records cover those).
The fingerprint files stay local (work/ is gitignored): they list the excluded repositories' structure.
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

H = Path(__file__).resolve().parents[2]
STORE = H / 'work' / 'excluded-fingerprints'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def origin(folder):
    def git(*args):
        r = subprocess.run(['git', '-c', 'safe.directory=*', '-C', str(folder)] + list(args), capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    return {'remote': git('remote', 'get-url', 'origin'), 'commit': git('rev-parse', 'HEAD')}


def make(folders):
    STORE.mkdir(parents=True, exist_ok=True)
    for folder in map(Path, folders):
        out = STORE / (folder.name + '.jsonl.gz')
        count = size = 0
        with gzip.open(out, 'wt', encoding='utf-8') as f:
            f.write(json.dumps({'source': folder.name, 'origin': origin(folder), 'made': '2026-10-15'}) + '\n')
            for root, dirs, files in os.walk(folder):
                dirs[:] = [d for d in dirs if d != '.git']
                for name in files:
                    p = Path(root) / name
                    try:
                        n = p.stat().st_size
                        f.write(json.dumps({'path': p.relative_to(folder).as_posix(), 'size': n, 'sha256': sha256(p)}) + '\n')
                    except OSError as e:
                        f.write(json.dumps({'path': p.relative_to(folder).as_posix(), 'error': type(e).__name__}) + '\n')
                        continue
                    count += 1
                    size += n
        print(f'{folder.name}: {count} files, {size / 1e6:.1f} MB -> {out}')


def load():
    known = {}
    for path in sorted(STORE.glob('*.jsonl.gz')):
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            source = json.loads(f.readline())['source']
            for line in f:
                row = json.loads(line)
                if row.get('sha256') and row.get('size', 0) > 64:   # tiny files (empty, one-liners) match by chance
                    known[row['sha256']] = (source, row['path'])
    return known


def check(trees):
    known = load()
    if not known:
        print('no fingerprints in', STORE)
        return 2
    if trees:
        files = [p for t in trees for p in Path(t).rglob('*') if p.is_file() and '.git' not in p.parts]
    else:
        names = subprocess.run(['git', '-C', str(H), 'ls-files', '-z'], capture_output=True, check=True).stdout.decode().split('\0')
        files = [H / n for n in names if n]
    hits = []
    for p in files:
        try:
            digest = sha256(p)
        except OSError:
            continue
        if digest in known:
            hits.append((p, known[digest]))
    print(f'{len(files)} files checked against {len(known)} excluded fingerprints: {len(hits)} identical')
    for p, (source, original) in hits[:50]:
        print(f'  {p}  ==  {source}/{original}')
    return 1 if hits else 0


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == 'make':
        make(sys.argv[2:])
        return 0
    if len(sys.argv) >= 2 and sys.argv[1] == 'check':
        return check(sys.argv[2:])
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
