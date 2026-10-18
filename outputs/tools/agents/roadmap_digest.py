"""Staleness check and stamp for Agent/notes/roadmap-digest.md (Claude, 15 Oct).

The digest is a lookup of SWG-roadmap.md and SWG-handoff.md written by a Haiku agent from Agent/notes/roadmap-digest-prompt.md.
  python -I tools/agents/roadmap_digest.py check   exit 0 = fresh, exit 1 = STALE (names which source changed), exit 2 = no stamp
  python -I tools/agents/roadmap_digest.py snap    BEFORE starting the Haiku agent: remember the sizes and hashes of both sources
  python -I tools/agents/roadmap_digest.py stamp   rewrite the 'Stamp:' line with the sizes and hashes from the snap (what the agent read);
                                                   without a snap it uses the current files
The board is compared without its Log section (it changes every few minutes).
Run from the outputs folder or anywhere (paths are resolved from this file).
"""
import hashlib
import json
import re
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parents[2]
DIGEST = OUT / 'Agent' / 'notes' / 'roadmap-digest.md'
SNAP = OUT.parent / 'work' / 'roadmap-digest-snap.json'  # work/ is git-ignored
SOURCES = {'roadmap': OUT / 'SWG-roadmap.md', 'board': OUT / 'SWG-handoff.md'}


def current():
    """Sizes and hashes of the sources. The board's Log (everything from '## Log' on) changes every few minutes and is left out:
    the digest only summarizes the lock, questions, task rows and instructions above it."""
    out = {}
    for k, p in SOURCES.items():
        data = p.read_bytes()
        if k == 'board':
            data = data.split(b'\n## Log', 1)[0]
        out[k] = (len(data), hashlib.sha256(data).hexdigest()[:12])
    return out


def stamp_line():
    cur = {k: tuple(v) for k, v in json.loads(SNAP.read_text(encoding='utf-8')).items()} if SNAP.exists() else current()
    parts = '; '.join(f'{k} {size} bytes sha {h}' for k, (size, h) in cur.items())
    return f'Stamp: generated {time.strftime("%d %b %Y %H:%M")} from {parts}'


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if cmd == 'snap':
        SNAP.write_text(json.dumps(current()), encoding='utf-8')
        print('snapshot saved:', {k: v[0] for k, v in current().items()})
        return
    text = DIGEST.read_text(encoding='utf-8')
    if cmd == 'stamp':
        line = stamp_line()
        new, n = re.subn(r'^Stamp:.*$', lambda _: line, text, count=1, flags=re.M)
        if not n:
            sys.exit('no "Stamp:" line in the digest')
        DIGEST.write_text(new, encoding='utf-8')
        SNAP.unlink(missing_ok=True)
        print(line)
        return
    m = re.search(r'^Stamp: .*$', text, flags=re.M)
    found = dict(re.findall(r'(roadmap|board) \d+ bytes sha ([0-9a-f]{12})', m.group(0))) if m else {}
    if not found:
        print('NO STAMP: run "stamp" after the digest was generated')
        sys.exit(2)
    stale = [k for k, (size, h) in current().items() if found.get(k) != h]
    if stale:
        print('STALE: ' + ', '.join(stale) + ' changed since the digest was written')
        sys.exit(1)
    print('fresh')


if __name__ == '__main__':
    main()
