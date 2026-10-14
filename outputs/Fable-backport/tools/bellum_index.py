"""Index Bellum Gero's object Lua by the path strings it registers, not by file location.

Bellum registers some templates in folders that don't match their paths (for example
object/tangible/furniture/hoth/decorative_hoth_travel_advertisement.lua registers
object/tangible/tcg/series3/...). So the index key is the second argument of
ObjectTemplates:addTemplate(...) / addClientTemplate(...).

Reads Bellum's files as text only; runs none of its code.
Run: python -I tools/bellum_index.py   ->  work/bellum_index.json
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
H = os.path.normpath(os.path.join(HERE, '..', '..', '..'))  # tools -> Fable-backport -> outputs -> h
BELLUM = os.path.join(H, 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'bin', 'scripts')
OUT = os.path.join(HERE, '..', 'work', 'bellum_index.json')

RX_S = re.compile(r'addTemplate\(\s*([A-Za-z0-9_]+)\s*,\s*"([^"]+)"')
RX_C = re.compile(r'addClientTemplate\(\s*([A-Za-z0-9_]+)\s*,\s*"([^"]+)"')


def main():
    idx = {'server': {}, 'client': {}}
    n = 0
    for root, dirs, files in os.walk(os.path.join(BELLUM, 'object')):
        for fn in files:
            if not fn.endswith('.lua'):
                continue
            p = os.path.join(root, fn)
            with open(p, encoding='utf-8', errors='replace') as f:
                t = f.read()
            n += 1
            rel = os.path.relpath(p, BELLUM).replace(os.sep, '/')
            for name, path in RX_S.findall(t):
                idx['server'].setdefault(path, []).append({'file': rel, 'name': name})
            for name, path in RX_C.findall(t):
                idx['client'].setdefault(path, []).append({'file': rel, 'name': name})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(idx, f, indent=0, sort_keys=True)
    reloc = [(p, v[0]['file']) for p, v in idx['server'].items() if v[0]['file'] != p[:-4] + '.lua']
    print(f'bellum lua files {n}; server paths {len(idx["server"])}; client paths {len(idx["client"])}')
    print(f'relocated server registrations: {len(reloc)}')
    for p, f in sorted(reloc)[:20]:
        print('  ', p, '<-', f)
    return 0


if __name__ == '__main__':
    sys.exit(main())
