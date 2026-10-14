"""Hoth creatures slice: check every Bellum Gero Hoth mobile and lair against our dev scripts and the real client.

    python -I tools/hoth/hoth_mobile_check.py DEVLISTS [--login FILE]

DEVLISTS is a folder of name lists exported from the dev tree (object_templates.txt, weapon_groups.txt,
loot_groups.txt, commands.txt, creature_templates.txt, lair_templates.txt), made by a read-only grep in WSL.
--login is the client session file (Play SWG Test Galaxy.cmd's), so the client check uses the real load order.
Read-only: parses Bellum's Lua as text (nothing is executed) and prints one row per mobile, then the lairs.
"""
import os, re, sys

H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
BELLUM = os.path.join(H, 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'bin', 'scripts')
CLIENT = os.path.join(H, 'outputs', 'SWG-client')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client_load_order import load_order, read_tre  # noqa: E402


def names(folder, f):
    return set(open(os.path.join(folder, f), encoding='utf-8').read().split())


def lua_list(text, key):
    m = re.search(key + r'\s*=\s*\{', text)
    if not m:
        return []
    depth, i = 1, m.end()
    while depth and i < len(text):
        depth += {'{': 1, '}': -1}.get(text[i], 0)
        i += 1
    return re.findall(r'"([^"]+)"', text[m.end():i - 1])


def field(text, key):
    m = re.search(r'\b' + key + r'\s*=\s*("?)([^",\n]*)\1', text)
    return m.group(2).strip() if m else ''


def main(argv):
    login = None
    if '--login' in argv:
        i = argv.index('--login')
        login = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    dev = argv[0]
    objects, weapons, loot = names(dev, 'object_templates.txt'), names(dev, 'weapon_groups.txt'), names(dev, 'loot_groups.txt')
    commands, creatures, lairs = names(dev, 'commands.txt'), names(dev, 'creature_templates.txt'), names(dev, 'lair_templates.txt')
    trees, _, _ = load_order(login)
    client = set()
    for _, name in trees:
        path = os.path.join(CLIENT, name)
        if os.path.exists(path):
            client.update(e['name'].lower() for e in read_tre(path))
    bellum_objects = {}
    for d, _, fs in os.walk(os.path.join(BELLUM, 'object')):
        for f in fs:
            if f.endswith('.lua'):
                for iff in re.findall(r'addTemplate\(\s*\w+\s*,\s*"([^"]+)"', open(os.path.join(d, f), encoding='utf-8', errors='replace').read()):
                    bellum_objects[iff] = os.path.relpath(os.path.join(d, f), BELLUM).replace(os.sep, '/')

    def shared(iff):
        head, tail = iff.rsplit('/', 1)
        return f'{head}/shared_{tail}'.lower()

    print('mobile | level | body (server / client) | weapon | attacks missing | loot groups missing')
    for f in sorted(os.listdir(os.path.join(BELLUM, 'mobile', 'hoth'))):
        if not f.startswith('hoth_'):
            continue
        text = open(os.path.join(BELLUM, 'mobile', 'hoth', f), encoding='utf-8').read()
        name = f[:-4]
        bodies = []
        for iff in lua_list(text, 'templates'):
            server = 'ours' if iff in objects else ('Bellum ' + bellum_objects[iff] if iff in bellum_objects else 'MISSING')
            bodies.append(f"{iff.split('/')[-1]} ({server} / {'yes' if shared(iff) in client else 'NO'})")
        weapon = field(text, 'primaryWeapon')
        weapon_ok = weapon in ('unarmed', 'none', '') or weapon in weapons
        attacks = re.findall(r'\{"(\w+)"\s*,', text.split('primaryAttacks', 1)[-1])
        missing_attacks = [a for a in attacks if a.lower() not in commands]
        groups = re.findall(r'group\s*=\s*"([^"]+)"', text)
        missing_loot = sorted({g for g in groups if g not in loot})
        print(f"{name} | {field(text, 'level')} | {', '.join(bodies) or '?'} | {weapon}{'' if weapon_ok else ' (MISSING)'} | "
              f"{','.join(missing_attacks) or '-'} | {','.join(missing_loot) or '-'}"
              + (' | name already used in ours!' if name in creatures else ''))
    print()
    print('lair | mobiles (missing in Bellum Hoth set and ours) | building')
    for d, _, fs in os.walk(os.path.join(BELLUM, 'mobile', 'lair')):
        for f in sorted(fs):
            if 'hoth' not in f:
                continue
            text = open(os.path.join(d, f), encoding='utf-8').read()
            mobs = re.findall(r'\{\s*"(\w+)"\s*,', text.split('mobiles', 1)[-1].split('buildingsVeryEasy', 1)[0])
            hoth = {g[:-4] for g in os.listdir(os.path.join(BELLUM, 'mobile', 'hoth'))}
            missing = [m for m in mobs if m not in hoth and m not in creatures]
            buildings = sorted(set(re.findall(r'"(object/tangible/lair/[^"]+)"', text)))
            bstat = [f"{b.split('/')[-1]} ({'ours' if b in objects else 'MISSING'}/{'yes' if shared(b) in client else 'NO'})" for b in buildings]
            print(f"{f[:-4]} | {','.join(mobs)}{' MISSING ' + ','.join(missing) if missing else ''} | {', '.join(bstat) or '-'}"
                  + (' | name already used in ours!' if f[:-4] in lairs else ''))


if __name__ == '__main__':
    main(sys.argv[1:])
