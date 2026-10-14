"""Second half of hoth_loot_inventory.py, run inside WSL: which of the Hoth loot templates Core3-dev already has.

Core3 registers templates by path string, and keeps later-era objects under object/custom_content/, so this indexes
every ObjectTemplates:addTemplate / addClientTemplate path in bin/scripts/object rather than looking for files.
For every template in tools/hoth/data/hoth_loot_inventory.json it records the Core3-dev file registering the server
template and the one defining the shared template (or null), plus whether the loot item and group names are taken.
Writes tools/hoth/data/hoth_loot_core3.json and prints a summary.

Run: wsl -d Debian -u swgemu -- python3 -I /mnt/c/.../tools/hoth/hoth_loot_core3_check.py
"""
import json, os, re

H = '/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth/data'
CORE3 = '/opt/swg/Core3-dev/MMOCoreORB/bin/scripts'


def read(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()
    except OSError:
        return ''


def index():
    server, client = {}, {}
    for root, _, files in os.walk(os.path.join(CORE3, 'object')):
        for f in files:
            if f.endswith('.lua'):
                path = os.path.join(root, f)
                rel = os.path.relpath(path, CORE3)
                text = read(path)
                for p in re.findall(r'ObjectTemplates:addTemplate\(\s*\w+\s*,\s*"([^"]+)"', text):
                    server[p] = rel
                for p in re.findall(r'ObjectTemplates:addClientTemplate\(\s*\w+\s*,\s*"([^"]+)"', text):
                    client[p] = rel
    return server, client


def main():
    inv = json.load(open(os.path.join(H, 'hoth_loot_inventory.json')))
    server, client = index()
    out = {'templates': {}, 'item_names_taken': [], 'group_names_taken': []}
    for t in sorted(inv['templates']):
        head, tail = t.rsplit('/', 1)
        out['templates'][t] = {'core3_lua': server.get(t), 'core3_shared': client.get(head + '/shared_' + tail)}
    names = set()
    for root, _, files in os.walk(os.path.join(CORE3, 'loot')):
        for f in files:
            if f.endswith('.lua'):
                names.update(re.findall(r'addLoot(?:Item|Group)Template\("([^"]+)"', read(os.path.join(root, f))))
    out['item_names_taken'] = sorted(n for n in inv['items'] if n in names)
    out['group_names_taken'] = sorted(n for n in inv['groups'] if n in names)
    with open(os.path.join(H, 'hoth_loot_core3.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, indent=1, sort_keys=True)
    v = out['templates'].values()
    print(f"{len(out['templates'])} templates: Core3-dev registers the server template for "
          f"{sum(bool(x['core3_lua']) for x in v)}, the shared template for {sum(bool(x['core3_shared']) for x in v)}")
    print('item names already taken:', out['item_names_taken'])
    print('group names already taken:', out['group_names_taken'])


if __name__ == '__main__':
    main()
