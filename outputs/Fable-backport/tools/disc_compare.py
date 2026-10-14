"""Compare the disc copies hashed by disc_index.py --hash with the copies our client loads. Read-only.
Run: python -I tools/disc_compare.py
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import swg_iff  # noqa: E402
from swg_iff import scd  # noqa: E402

scd._build_index()
d = json.load(open(os.path.join(HERE, '..', 'work', 'disc_index.json'), encoding='utf-8'))
for p, by_archive in sorted(d['hashes'].items()):
    ours = scd.client_file(p)
    h = hashlib.sha256(ours).hexdigest() if ours else None
    hit = scd._index.get(p.lower())
    same = [a for a, v in by_archive.items() if v == h]
    print(f'{p}\n   client: {os.path.basename(hit[0]) if hit else None} {h[:16] if h else None}\n   disc:   '
          + ', '.join(f'{a} {v[:16]}' for a, v in by_archive.items())
          + f'\n   -> {"identical to " + ", ".join(same) if same else "differs"}')
