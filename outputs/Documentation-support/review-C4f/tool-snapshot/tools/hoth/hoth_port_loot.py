"""Hoth reward loot slice: port the Bellum Gero Hoth loot our client can show into the dev tree, and hook it to Hoth's
creatures (owner, 14 Oct: "port Bellum's Hoth reward loot as the next Hoth slice").

Inside Debian, as swgemu (writes LF files in /opt/swg/Core3-dev only):
    python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth/hoth_port_loot.py [--dry-run]

Source: Bellum Gero (github.com/Miphstoe/BellumGero-Live) at 1f4438a1, AGPL-3.0, pinned in work/research.
Inputs: tools/hoth/data/hoth_loot_inventory.json (hoth_loot_inventory.py, Windows) and hoth_loot_core3.json
(hoth_loot_core3_check.py, WSL). An item is ported when every template it needs has a client object, and Core3-dev
registers it already or Bellum supplies it. Of 163 Bellum items that is 25: 7 Hoth decorations and 18 vehicle deeds.
The rest need client objects that only Bellum's private archive has (listed in hoth-port-log.md).
What it writes:
  - loot/items/hoth/<item>.lua (Bellum's, unchanged) + a section in loot/items.lua;
  - loot/groups/hoth/{hoth_decor_common,hoth_decor_rare,hoth_vehicle_deeds}.lua: Bellum's groups cut to the ported
    items, equal weights totalling 10,000,000 + a section in loot/groups.lua;
  - the two vehicle deeds Core3-dev lacks (Organa speeder, Sith speeder: their control devices and vehicles exist):
    server templates under object/custom_content/tangible/deed/vehicle_deed/, shared templates in that folder's
    objects.lua, includes in its serverobjects.lua;
  - drops on Hoth's creatures (our design; Bellum gave these groups to its bosses elsewhere): TIERS below.
Re-running is safe: files are rewritten from the source and registrations and drops are added only once.
"""
import json, re, sys
from pathlib import Path

SRC = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/work/research/Miphstoe_BellumGero-Live/MMOCoreORB/bin/scripts')
DST = Path('/opt/swg/Core3-dev/MMOCoreORB/bin/scripts')
DATA = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth/data')
REV = '1f4438a1'
DRY = '--dry-run' in sys.argv
GROUP_TOTAL = 10000000

# Drops (lootChance out of 10,000,000). Ordinary Hoth life (level 62-90) may drop a common decoration; sergeants and
# named beasts (85-115) a rare one; the named beasts (98-115) also a vehicle deed.
COMMON = ['hoth_tauntaun', 'hoth_ice_mynock', 'hoth_scavenger', 'hoth_tauntaun_bull', 'hoth_imperial_salvage_tech',
          'hoth_probe_droid', 'hoth_scavenger_raider', 'hoth_greater_ice_mynock', 'hoth_snowtrooper',
          'hoth_rebel_snow_soldier', 'hoth_wampa']
BOSSES = ['hoth_elder_wampa', 'hoth_mynock_broodmother', 'hoth_wampa_frostfang', 'hoth_wampa_icemaw',
          'hoth_wampa_snowblind', 'hoth_wampa_matriarch', 'hoth_wampa_patriarch']
ELITE = ['hoth_rebel_snow_sergeant', 'hoth_snowtrooper_sergeant'] + BOSSES
TIERS = [('hoth_decor_common', COMMON, 300000),   # 3%
         ('hoth_decor_rare', ELITE, 500000),      # 5%
         ('hoth_vehicle_deeds', BOSSES, 200000)]  # 2%


def notice(rel, changes):
    return (f'-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision {REV}, AGPL-3.0),\n'
            f'-- MMOCoreORB/bin/scripts/{rel}. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).\n'
            + ''.join(f'-- {c}\n' for c in changes) + '\n')


def write(path, text):
    if DRY:
        print(f'would write {path.relative_to(DST)} ({len(text)} bytes)')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')
    print(f'wrote {path.relative_to(DST)}')


def append_once(path, marker, addition):
    """Append once, keeping the file's own line endings (some Core3 files, e.g. custom_content's, are CRLF)."""
    raw = path.read_bytes().decode('utf-8')
    crlf = '\r\n' in raw
    text = raw.replace('\r\n', '\n')
    if marker in text:
        print(f'already in {path.relative_to(DST)}: {marker.strip()[:60]}')
        return
    text = text.rstrip('\n') + '\n' + addition
    if DRY:
        print(f'would append to {path.relative_to(DST)}: {marker.strip()[:60]}')
        return
    path.write_bytes((text.replace('\n', '\r\n') if crlf else text).encode('utf-8'))
    print(f'appended to {path.relative_to(DST)}: {marker.strip()[:60]}')


def closure(templates, t, seen=None):
    seen = set() if seen is None else seen
    if t not in seen:
        seen.add(t)
        for r in templates[t]['refs']:
            closure(templates, r, seen)
    return seen


def ported_items(inv, core3):
    T, C = inv['templates'], core3['templates']
    items, new_templates = [], set()
    for name, it in sorted(inv['items'].items()):
        need = closure(T, it['template'])
        if not all(T[x]['client_shared'] for x in need):
            continue
        missing = [x for x in need if not (C[x]['core3_lua'] and C[x]['core3_shared'])]
        if all(T[x]['bellum_lua'] and T[x]['bellum_shared'] for x in missing):
            items.append(name)
            new_templates.update(missing)
    return items, sorted(new_templates)


def block_end(text, start):
    depth, i = 0, start
    while True:
        depth += {'{': 1, '}': -1}.get(text[i], 0)
        i += 1
        if depth == 0:
            return i


def add_drop(text, group, chance):
    """Add {groups = {{group, 10000000}}, lootChance = chance} to the mobile's lootGroups unless the group is there."""
    if f'group = "{group}"' in text:
        return text, False
    m = re.search(r'lootGroups\s*=\s*\{', text)
    open_at = m.end() - 1
    close_at = block_end(text, open_at)
    body = text[open_at + 1:close_at - 1]
    entries, i = [], 0
    while True:
        j = body.find('{', i)
        if j < 0:
            break
        k = block_end(body, j)
        entries.append(body[j:k])
        i = k
    entries.append('{\n\t\t\tgroups = {\n\t\t\t\t{group = "%s", chance = %d}\n\t\t\t},\n\t\t\tlootChance = %d\n\t\t}'
                   % (group, GROUP_TOTAL, chance))
    new = '{' + ','.join('\n\t\t' + e for e in entries) + '\n\t}'
    return text[:open_at] + new + text[close_at:], True


def main():
    inv = json.loads((DATA / 'hoth_loot_inventory.json').read_text())
    core3 = json.loads((DATA / 'hoth_loot_core3.json').read_text())
    items, new_templates = ported_items(inv, core3)
    print(f'{len(items)} items to port; {len(new_templates)} templates Core3-dev lacks: {new_templates}')

    # 1. templates Core3-dev lacks (the two deeds), Core3 style under custom_content
    for t in new_templates:
        folder, name = t[:-4].rsplit('/', 1)
        assert folder == 'object/tangible/deed/vehicle_deed', t  # the only case this slice needs
        cc = DST / 'object' / 'custom_content' / 'tangible' / 'deed' / 'vehicle_deed'
        b = inv['templates'][t]
        body = (SRC / b['bellum_lua']).read_text(encoding='utf-8')
        write(cc / f'{name}.lua', notice(b['bellum_lua'], ['Unchanged; placed under custom_content like the other later-era vehicle deeds.']) + body.lstrip())
        shared = f'shared_{name}'
        var = f'object_tangible_deed_vehicle_deed_{shared}'
        append_once(cc / 'objects.lua', f'{var} = ',
                    f'\n--*****************************************\n'
                    f'-- Hoth loot slice, 14 Oct 2026 (from Bellum Gero, AGPL-3.0)\n\n'
                    f'{var} = SharedTangibleObjectTemplate:new {{\n'
                    f'\tclientTemplateFileName = "{folder}/{shared}.iff"\n}}\n'
                    f'ObjectTemplates:addClientTemplate({var}, "{folder}/{shared}.iff")\n')
        append_once(cc / 'serverobjects.lua', f'vehicle_deed/{name}.lua"',
                    f'includeFile("custom_content/tangible/deed/vehicle_deed/{name}.lua") -- Hoth loot slice (Bellum Gero)\n')

    # 2. loot items
    for name in items:
        rel = f'loot/items/bellum/hoth/{name}.lua'
        write(DST / 'loot' / 'items' / 'hoth' / f'{name}.lua', notice(rel, ['Unchanged.']) + (SRC / rel).read_text(encoding='utf-8').lstrip())
    append_once(DST / 'loot' / 'items.lua', '--hoth sub-folder',
                '\n--hoth sub-folder (Hoth reward loot from Bellum Gero, AGPL-3.0; 14 Oct 2026)\n'
                + ''.join(f'includeFile("items/hoth/{n}.lua")\n' for n in items))

    # 3. loot groups, cut to the ported items, equal weights
    group_names = []
    for g, entries in sorted(inv['groups'].items()):
        keep = [e['name'] for e in entries if e['kind'] == 'itemTemplate' and e['name'] in items]
        if not keep:
            continue
        group_names.append(g)
        w = GROUP_TOTAL // len(keep)
        weights = [w] * len(keep)
        weights[-1] += GROUP_TOTAL - w * len(keep)
        rel = f'loot/groups/bellum/hoth/{g}.lua'
        lines = ''.join(f'\t\t{{itemTemplate = "{n}", weight = {x}}},\n' for n, x in zip(keep, weights)).rstrip(',\n') + '\n'
        write(DST / 'loot' / 'groups' / 'hoth' / f'{g}.lua',
              notice(rel, [f'Cut to the {len(keep)} of {len(entries)} items whose objects our client has; equal weights.'])
              + f'{g} = {{\n\tdescription = "",\n\tminimumLevel = 0,\n\tmaximumLevel = 0,\n\tlootItems = {{\n{lines}\t}}\n}}\n\n'
              + f'addLootGroupTemplate("{g}", {g})\n')
    append_once(DST / 'loot' / 'groups.lua', '--hoth sub-folder',
                '\n--hoth sub-folder (Hoth reward loot from Bellum Gero, AGPL-3.0; 14 Oct 2026)\n'
                + ''.join(f'includeFile("groups/hoth/{g}.lua")\n' for g in group_names))

    # 4. drops on Hoth's creatures: each mobile read once, every tier applied, written once
    drops = {}
    for group, mobs, chance in TIERS:
        assert group in group_names, group
        for mob in mobs:
            drops.setdefault(mob, []).append((group, chance))
    for mob, wanted in drops.items():
        path = DST / 'mobile' / 'hoth' / f'{mob}.lua'
        text = path.read_text(encoding='utf-8')
        added = []
        for group, chance in wanted:
            text, ok = add_drop(text, group, chance)
            if ok:
                added.append(f'{group} ({chance / 100000:g}%)')
        if not added:
            print(f'already has its drops: {mob}')
            continue
        # one comment line under the port notice at the top of the file
        lines = text.split('\n')
        first_code = next(i for i, l in enumerate(lines) if not l.startswith('--'))
        lines.insert(first_code, f'-- Hoth loot slice (14 Oct 2026): drops {", ".join(added)}.')
        write(path, '\n'.join(lines))
        if DRY and mob in ('hoth_wampa_patriarch', 'hoth_tauntaun'):
            print('\n'.join(lines[:5]))
            m = re.search(r'lootGroups\s*=\s*\{', '\n'.join(lines))
            body = '\n'.join(lines)
            print(body[m.start():block_end(body, m.end() - 1)])


if __name__ == '__main__':
    main()
