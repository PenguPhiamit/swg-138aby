"""Owner's Legacy Era Armory -> structured catalogue, matched to real SWG crafters and items. (Claude, 14 Oct 2026.)

    python -I tools/owner_content/extract_armory.py

Input: Content-catalogue/owner-SWG-SW5E/legacy_era_armory.md (the owner's file, 14 Oct). Output: armory.json next to it.
Owner, 14 Oct: the books are a reference for new professions, mats and consumables; match everything to the correct
SWG profession style; making items useful comes later. So every item gets:
  - the real SWG crafter line for its kind (Weaponsmith Firearms / Melee / Munitions, Armorsmith, Tailor, Droid
    Engineer, Jedi, ...), read against the client's skills.iff and schematic_group.iff;
  - the real SWG item when one exists (names from string/en/weapon_name.stf and wearables_name.stf), with the skill
    box that grants its schematic where the client lists one;
  - whether it's crafted today (current era) or a found piece (older eras: loot, quest or Storyteller prop that a
    restoration mechanic could later revive, as the armory intends).
Left out: the SW5e numbers (dice, ranges in feet, AC, DCs). Kept as reference text only: the armory's notes.
"""
import collections, json, os, re, sys

H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
DIR = os.path.join(H, 'outputs', 'Content-catalogue', 'owner-SWG-SW5E')
SRC = os.path.join(DIR, 'legacy_era_armory.md')
OUT = os.path.join(DIR, 'armory.json')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swg_client_data as c  # noqa: E402

CURRENT = {'LGC', 'GAL'}
WS = 'Weaponsmith'
LINES = {  # subsection number -> (crafter line, kind)
    '6.1': (f'{WS}, Firearms line', 'pistol'), '6.2': (f'{WS}, Firearms line', 'pistol'),
    '6.3': (f'{WS}, Firearms line', 'carbine'), '6.4': (f'{WS}, Firearms line', 'rifle'),
    '6.5': (f'{WS}, Firearms line', 'rifle'), '6.6': (f'{WS} (heavy weapons are Commando-only to use)', 'heavy'),
    '6.7': (f'{WS}, Firearms line', 'slugthrower'), '6.8': (f'{WS}, Firearms line', 'bow'),
    '6.9': (f'{WS}, Firearms line', 'specialty'), '6.10': (f'{WS}, Munitions line', 'munition'),
    '6.11': ('not player-crafted (ancient or Force relic: loot, quest or Storyteller prop)', 'relic'),
    '7.1': (f'{WS}, Melee line', 'blade'), '7.2': (f'{WS}, Melee line', 'polearm/axe'),
    '7.3': (f'{WS}, Melee line', 'staff/baton'), '7.4': (f'{WS}, Melee line', 'cultural melee'),
    '7.5': ('Jedi, Lightsaber line (Jedi build their own sabers in pre-CU)', 'lightsaber'),
    '7.6': ('not player-crafted (ancient Jedi/Sith relic)', 'relic'),
    '7.7': ('not player-crafted (Yuuzhan Vong living weapon; Bio-Engineer only if a living-gear mechanic is built)', 'relic'),
    '8.1': ('Tailor', 'clothing'), '8.2': ('Armorsmith, Personal Armor line', 'light armor'),
    '8.3': ('Armorsmith, Personal Armor line', 'medium armor'), '8.4': ('Armorsmith, Personal Armor line', 'heavy armor'),
    '8.5': ('new (pre-CU has no jetpacks, exoframes or sealed suits)', 'powered gear'),
    '8.6': ('new (pre-CU has no personal shields; nearest is the Armorsmith Deflectors line, which makes armor components)', 'shield'),
    '8.7': ('Armorsmith (helmets come with armor sets) or Tailor (masks)', 'helmet'),
    '8.8': ('not player-crafted (ancient or precursor armor)', 'relic'),
    '8.9': ('new for beasts (pre-CU pets wear no armor); droid plating by Droid Engineer (real droid defensive modules)', 'plating'),
    '9.1': ('real equivalents: Artisan weapon powerups (item_powerup_weapon_*) and Weaponsmith components', 'weapon mod'),
    '9.2': ('real equivalent: Armorsmith Layers line (armor layers)', 'armor mod'),
}
# Hand list of name links the automatic token match can't make (armory wording -> real client name), checked 14 Oct.
ALIASES = {
    'gaderffii stick': 'Gaderiffi Baton', 'vibro-knuckles': 'Vibro Knuckler', 'vibro-lance': 'Vibro Lance',
    'vibro-ax': 'Vibro Axe', 'forearm flamethrower': 'Flame Thrower', 'sonic blaster': 'Geonosian Sonic Blaster',
    'dxr-6 disruptor rifle': 'Tenloss DXR-6 Disruptor Rifle', 'training lightsaber': 'A Training Lightsaber',
    'double-bladed lightsaber': 'Double-Bladed Lightsaber', 'standard lightsaber': 'Lightsaber',
    'tusken cycler rifle': 'Tusken Rifle', 'wookiee bowcaster': 'Bowcaster', 'ryyk blade': 'Ryyk Blade',
    'stun baton': 'Stun Baton', 'class-a thermal detonator': 'Thermal Detonator',
    'fragmentation grenade': 'C22 Fragmentation Grenade', 'plx-1 portable missile launcher': 'Rocket Launcher (nearest)',
    'flechette pistol': 'FWG5 Pistol (a flechette pistol)', 'composite armor': 'Composite Armor',
    'bounty hunter kit suit': 'Bounty Hunter armor', 'vibroblade': 'Vibroblade', 'vibroknife': 'Survival Knife (nearest)',
    'ion rifle': 'Jawa Ion Rifle (nearest)',
}


def tables(md):
    """[(section, subsection, title, header, rows)] for every pipe table."""
    out, sec, sub, title = [], '', '', ''
    lines = md.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^##\s+(\d+)\.\s+(.*)', line)
        if m:
            sec, sub, title = m[1], m[1], m[2].strip()
        m = re.match(r'^###\s+(\d+\.\d+)\s+(.*)', line)
        if m:
            sub, title = m[1], m[2].strip()
        if line.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[i + 1]):
            header = [h.strip() for h in line.strip('|').split('|')]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([cell.strip() for cell in lines[i].strip('|').split('|')])
                i += 1
            out.append((sec, sub, title, header, rows))
            continue
        i += 1
    return out


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def main():
    md = open(SRC, encoding='utf-8').read()
    wnames = c.string_file(c.client_file('string/en/weapon_name.stf'))
    anames = c.string_file(c.client_file('string/en/wearables_name.stf'))
    skills = c.datatable(c.client_file('datatables/skill/skills.iff'))
    groups = c.datatable(c.client_file('datatables/crafting/schematic_group.iff'))
    grp_box = collections.defaultdict(list)
    for r in skills:
        for g in (r['SCHEMATICS_GRANTED'] or '').split(','):
            if g:
                grp_box[g].append(r['NAME'])
    schem_box, schem_path = {}, {}
    for r in groups:
        gid, path = list(r.values())[:2]
        stem = path.split('/')[-1].replace('.iff', '')
        schem_box[stem] = grp_box.get(gid, [])
        schem_path[stem] = path
    real_weapons = {v: k for k, v in wnames.items()}
    real_armor_families = sorted({re.sub(r'\s+(Armor\s+)?(Boots|Chest Plate|Gloves|Helmet|Left Bicep|Right Bicep|Left Bracer|'
                                         r'Right Bracer|Leggings|Pants|Belt|Bracer.*|Bicep.*|Guard.*|Jacket|Robe|Dress)$', '', v)
                                  for k, v in anames.items() if 'armor' in k})

    def real_match(name):
        low = name.lower()
        base = re.sub(r'\s*\[[A-Z]+\]', '', low).strip()
        for key, real in ALIASES.items():
            if base.startswith(key):
                return real
        codes = re.findall(r'\b([a-z]{1,4}-?\d{1,3}[a-z]?)\b', base)
        kind_words = [w for w in ('carbine', 'rifle', 'pistol') if w in base]
        for code in codes:
            n = norm(code)
            hits = [rv for rv in real_weapons if n and n in norm(rv)]
            if hits:  # same model code: prefer the same kind of weapon (an E-11 carbine is not the E-11 rifle)
                same = [h for h in hits if any(w in h.lower() for w in kind_words)]
                return min(same or hits, key=len)
        return None

    def box_for(real):
        """Skill boxes granting a schematic for this real item. Schematic files are named differently from the
        item strings (pistol_dl44 vs pistol_blaster_dl44), so match on the item's distinctive token."""
        name = real.split(' (')[0]
        key = real_weapons.get(name, '')
        tokens = [norm(t) for t in re.findall(r'[A-Za-z]+\d+[A-Za-z]*', name)] or \
                 [norm(w) for w in name.split() if len(w) > 3 and w.lower() not in ('pistol', 'rifle', 'carbine', 'armor', 'the')]
        if key and schem_box.get(key):
            return ', '.join(schem_box[key][:3])
        folders = ('/weapon/', '/munition/') if name in real_weapons else ('armor',)  # don't let "jawa" find Jawa beer
        for tok in tokens:
            found = sorted({b for s, bs in schem_box.items() if tok and tok in norm(s) and any(f in schem_path[s] for f in folders) for b in bs})
            if found:
                return ', '.join(found[:3])
        return None

    items = []
    for sec, sub, title, header, rows in tables(md):
        if sec not in ('6', '7', '8', '9'):
            continue
        crafter, kind = LINES.get(sub, ('?', '?'))
        for row in rows:
            rec = dict(zip(header, row))
            name = rec.get('Item') or rec.get('Mod') or row[0]
            tags = re.findall(r'\[([A-Z]+)\]', name)
            era = rec.get('Era', '')
            real = real_match(name) if sec in ('6', '7', '8') else None
            current = era in CURRENT or sec == '9'
            items.append({
                'id': 'arm-' + re.sub(r'[^a-z0-9]+', '-', re.sub(r'\[[A-Z]+\]', '', name).lower()).strip('-'),
                'name': re.sub(r'\s*\[[A-Z]+\]', '', name).strip(), 'tags': tags, 'section': f'{sub} {title}',
                'kind': kind, 'era': era, 'rarity': rec.get('Rar', ''), 'availability': rec.get('Avail', ''),
                'notes': rec.get('Notes') or rec.get('Effect', ''),
                'swg': {
                    'crafter': crafter,
                    'real_item': real,
                    'real_skill_box': box_for(real) if real else None,
                    'how_obtained': ('crafted (exists in SWG)' if real and current else
                                     'exists in SWG; as an older-era piece it is a found or restored item' if real else
                                     'crafted, new item' if current and not crafter.startswith('not player') else
                                     'found piece (loot, quest or Storyteller prop; restorable once a restoration mechanic exists)'
                                     if not crafter.startswith('not player') else 'not player-crafted'),
                },
                'status': 'optional, not enabled; stats not designed yet',
            })
    locations = []
    for sec, sub, title, header, rows in tables(md):
        if sec == '10' and header and header[0] == 'Location':
            locations = [dict(zip(header, r)) for r in rows]
    json.dump({'source': {'file': 'legacy_era_armory.md', 'author': 'the server owner', 'received': '2026-10-14',
                          'sha256': '0e040425d3ae0ceabde0473d5e8a835f5dbdddead705b4137577d59c5ab71f44'},
               'instruction': 'Owner, 14 Oct 2026: reference only; match to real SWG profession style; stats later.',
               'left_out': ['SW5e dice, ranges, AC and DCs', 'restoration DCs and day counts (tabletop rules)'],
               'real_armor_families_in_client': real_armor_families,
               'items': items, 'museum_locations_for_storytellers': locations},
              open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    count = collections.Counter(i['swg']['how_obtained'].split(';')[0].split(' (')[0] for i in items)
    print(f'{len(items)} items; {sum(1 for i in items if i["swg"]["real_item"])} match a real SWG item; {dict(count)}')
    for i in items:
        if i['swg']['real_item']:
            print(f"  {i['name'][:40]:40} -> {i['swg']['real_item'][:40]:40} {i['swg']['real_skill_box'] or ''}")


if __name__ == '__main__':
    main()
