"""Bellum Gero's Hoth reward loot: what each item needs and what we already have (owner, 14 Oct: port Bellum's Hoth
reward loot as the next Hoth slice).

Reads Bellum's loot groups and items (bin/scripts/loot/{groups,items}/bellum/hoth), then follows every server
template they name through Bellum's object Lua: loot schematic -> draft schematic -> crafted object, deed -> control
device + vehicle, and so on. For each template it records whether Bellum has its server Lua and whether the client
has its shared .iff (and which archive wins). The server loads the same archives as the client (stock, then MTG,
then local_planets.tre on the test galaxy), so the client check covers the server's shared templates too.
Core3-dev is checked separately inside WSL (hoth_loot_core3_check.py), because Windows can't read /opt/swg.

Run: python -I tools/hoth/hoth_loot_inventory.py   ->  tools/hoth/data/hoth_loot_inventory.json
Reads Bellum's files as text only; runs none of Bellum's code.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'owner_content'))
import swg_client_data as scd  # noqa: E402

BELLUM = r'C:\Users\Pengw\Documents\Codex\2026-10-13\h\work\research\Miphstoe_BellumGero-Live\MMOCoreORB\bin\scripts'
GROUPS = os.path.join(BELLUM, 'loot', 'groups', 'bellum', 'hoth')
ITEMS = os.path.join(BELLUM, 'loot', 'items', 'bellum', 'hoth')
OUT = os.path.join(HERE, 'data', 'hoth_loot_inventory.json')
REF = re.compile(r'"(object/[A-Za-z0-9_/]+\.iff)"')


def read(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def groups():
    out = {}
    for name in sorted(os.listdir(GROUPS)):
        text = read(os.path.join(GROUPS, name))
        entries = [{'kind': k, 'name': n, 'weight': int(w)} for k, n, w in
                   re.findall(r'(itemTemplate|groupTemplate) = "([^"]+)", weight = (\d+)', text)]
        out[name[:-4]] = entries
    return out


def items():
    out = {}
    for name in sorted(os.listdir(ITEMS)):
        text = read(os.path.join(ITEMS, name))
        m = re.search(r'directObjectTemplate = "([^"]+)"', text)
        out[name[:-4]] = {
            'template': m.group(1) if m else None,
            'custom_name': (re.search(r'customObjectName = "([^"]*)"', text) or [None, ''])[1],
            'crafting_values': 'craftingValues = {}' not in text,
        }
    return out


def shared(template):
    head, tail = template.rsplit('/', 1)
    return head + '/shared_' + tail


def client_archive(name):
    if scd._index is None:
        scd._build_index()
    hit = scd._index.get(name.lower())
    return os.path.basename(hit[0]) if hit else None


def bellum_index():
    """Bellum registers some templates in folders that don't match their paths (e.g. tcg objects under
    furniture/hoth), so index its object Lua by the registered path: server path -> file, shared path -> file."""
    server, client = {}, {}
    for root, _, files in os.walk(os.path.join(BELLUM, 'object')):
        for f in files:
            if f.endswith('.lua'):
                path = os.path.join(root, f)
                text = read(path)
                for p in re.findall(r'ObjectTemplates:addTemplate\(\s*\w+\s*,\s*"([^"]+)"', text):
                    server[p] = path
                for p in re.findall(r'ObjectTemplates:addClientTemplate\(\s*\w+\s*,\s*"([^"]+)"', text):
                    client[p] = path
    return server, client


def closure(roots):
    """Every server template reachable from the roots through Bellum's object Lua."""
    server, client = bellum_index()
    seen, todo = {}, list(roots)
    while todo:
        t = todo.pop()
        if t in seen:
            continue
        lua = server.get(t)
        refs = []
        if lua:
            # the object's own registration line names itself; keep the rest
            refs = sorted(set(r for r in REF.findall(read(lua)) if r != t))
        seen[t] = {
            'bellum_lua': os.path.relpath(lua, BELLUM).replace(os.sep, '/') if lua else None,
            'bellum_shared': os.path.relpath(client[shared(t)], BELLUM).replace(os.sep, '/') if shared(t) in client else None,
            'client_shared': client_archive(shared(t)),
            'refs': refs,
        }
        todo.extend(refs)
    return seen


def main():
    g, it = groups(), items()
    roots = sorted(set(v['template'] for v in it.values() if v['template']))
    templates = closure(roots)
    result = {'groups': g, 'items': it, 'templates': templates}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=1, sort_keys=True)
    missing_client = [t for t, v in templates.items() if not v['client_shared']]
    print(f'{len(g)} groups, {len(it)} items, {len(roots)} item templates, {len(templates)} templates in all')
    print(f'client shared .iff missing for {len(missing_client)}:')
    for t in sorted(missing_client):
        print('   ', t)
    by_archive = {}
    for v in templates.values():
        by_archive[v['client_shared']] = by_archive.get(v['client_shared'], 0) + 1
    print('winning archive:', dict(sorted(by_archive.items(), key=lambda kv: -kv[1])))
    print('->', OUT)


if __name__ == '__main__':
    main()
