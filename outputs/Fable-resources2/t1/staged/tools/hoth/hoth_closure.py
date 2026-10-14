"""Hoth step 1: which client files Hoth needs, and which our client (stock TREs + MTG archives) has.

    python -I tools/hoth/hoth_closure.py [seed ...]      default seeds: terrain/hoth.trn snapshot/hoth.ws

Starts from the seeds and follows every asset reference (object templates, appearances, meshes, shaders,
textures, terrain shader and flora families), resolving each path in the client's real load order
(a higher searchTree number wins). Read-only.

    --login FILE   use FILE as swgemu_login.cfg, e.g. the session file Play SWG Test Galaxy.cmd writes.

14 Oct 2026: the load order now comes from client_load_order.py, which reads the config the way the client does
([SharedFile] only). Bellum's walk_tres() counted searchTree lines in any section, so this tool once reported the
MTG archives as loaded when the client ignored them.

It reuses the TRE and IFF readers from Bellum Gero's planet tools (AGPL-3.0, pinned in
work/research/Miphstoe_BellumGero-Live, read before use: standard library, no writes, no network), loaded the
same way Bellum's own dep_closure.py loads them. Writes Documentation-support/hoth/hoth-closure.tsv and prints a
summary.
"""
import os, sys
from collections import Counter

H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
BELLUM = os.path.join(H, 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'tools', 'newplanets')
CLIENT = os.path.join(H, 'outputs', 'SWG-client')
OUT = os.path.join(H, 'outputs', 'Documentation-support', 'hoth')
sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))
from swgfmt.fmt_tools import read_tre, _inflate  # noqa: E402  (ours; was Bellum's tre_inventory)
# refs(): Bellum's asset-reference scanner (iff_tool.py); our readers have no equivalent yet, so it stays.
exec(open(os.path.join(BELLUM, 'iff_tool.py'), encoding='utf-8').read().split('if __name__')[0])

LEAVES = ('.dds', '.tga', '.wav', '.mp3', '.snd')


def main(seeds, login=None):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from client_load_order import load_order
    trees, ignored, _ = load_order(login)
    if ignored:
        print(f'# {len(ignored)} searchTree lines ignored by the client (not in [SharedFile])', file=sys.stderr)
    winners = {}  # internal path -> (tre, entry); later (higher priority) wins
    for tre in [os.path.join(CLIENT, name) for _, name in reversed(trees) if os.path.exists(os.path.join(CLIENT, name))]:
        try:
            for entry in read_tre(tre):
                winners[entry['name'].lower()] = (tre, entry)
        except Exception as exc:
            print(f'# skipped {os.path.basename(tre)}: {exc}', file=sys.stderr)

    def data(path):
        tre, entry = winners[path]
        with open(tre, 'rb') as stream:
            stream.seek(entry['offset'])
            blob = stream.read(entry['comp_size'] if entry['comp'] else entry['size'])
        return _inflate(blob, entry['comp'], entry['size'])

    seen, queue, rows, parent = set(), [s.lower() for s in seeds], [], {}
    while queue:
        path = queue.pop()
        if path in seen:
            continue
        seen.add(path)
        hit = winners.get(path)
        if hit is None:
            rows.append((path, '-', 'missing', parent.get(path, '')))
            continue
        tre = os.path.basename(hit[0])
        rows.append((path, tre, 'mtg' if tre.lower().startswith('mtg_') else 'stock', parent.get(path, '')))
        if path.endswith(LEAVES):
            continue
        for ref in refs(data(path)):
            if ref not in seen:
                parent.setdefault(ref, path)
                queue.append(ref)

    rows.sort()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'hoth-closure.tsv'), 'w', encoding='utf-8', newline='\n') as out:
        out.write('path\twinning_tre\tsource\tfirst_referenced_by\n')
        for row in rows:
            out.write('\t'.join(row) + '\n')
    count = Counter(r[2] for r in rows)
    print(f'{len(rows)} files reached from {", ".join(seeds)}: ' + ', '.join(f'{k} {v}' for k, v in sorted(count.items())))
    kinds = Counter(r[0].split('/')[0] for r in rows if r[2] == 'missing')
    print('missing by folder: ' + (', '.join(f'{k} {v}' for k, v in kinds.most_common()) or 'none'))
    for row in [r for r in rows if r[2] == 'missing'][:40]:
        print(f'  MISSING {row[0]}  (from {row[3]})')
    by_tre = Counter(r[1] for r in rows if r[2] == 'mtg')
    print('supplied by MTG archives: ' + ', '.join(f'{k} {v}' for k, v in by_tre.most_common()))


if __name__ == '__main__':
    args = sys.argv[1:]
    login = None
    if args[:1] == ['--login']:
        login, args = args[1], args[2:]
    main(args or ['terrain/hoth.trn', 'snapshot/hoth.ws'], login)
