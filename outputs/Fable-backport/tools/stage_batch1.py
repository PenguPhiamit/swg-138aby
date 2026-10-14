"""Stage backport batch 1 for Core3-dev (writes only under Fable-backport/).

Batch 1a: repair the 1,073 Mod the Galaxy server-template registrations in custom_content whose path string was
mangled when MTG generated the files (an underscore became a slash: creature_loot -> creature/loot, npc_loot ->
npc/loot, generic_usable -> generic/usable, loot_schematic -> loot/schematic, simple_kit -> simple/kit,
generic_deed -> generic/deed, cube_loot -> cube/loot, nova_orion -> nova/orion, kashyyyk_loot -> kashyyyk/loot).
The client file is object/<folder>/shared_<name>.iff, so the server path Core3 expects is object/<folder>/<name>.iff.
Also repairs the same strings in object/sandbox/mtg_catalog.lua (the staff builder catalogue).
Files keep their original bytes and line endings apart from the one string.

Batch 1b: 13 new wearable templates (NGE necklaces, rings and pants with no server template anywhere), under
custom_content/tangible/wearables/{necklace,pants,ring}/ in the custom_content style, plus the include-chain edits
to custom_content/tangible/wearables/serverobjects.lua and allobjects.lua.

Inputs: work/registration_fixes.json, work/core3_orig/ (copies of the Core3-dev files, taken at the commit noted
in the README). Outputs: staged/, diffs/, batch1.diff, apply-manifest.tsv, work/batch1_objects.json.

Run: python -I tools/stage_batch1.py
"""
import difflib, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
W = os.path.join(ROOT, 'work')
ORIG = os.path.join(W, 'core3_orig')
STAGED = os.path.join(ROOT, 'staged', 'MMOCoreORB', 'bin', 'scripts', 'object')
DIFFS = os.path.join(ROOT, 'diffs')
sys.path.insert(0, HERE)
import swg_iff  # noqa: E402
from swg_iff import scd  # noqa: E402

RACES_ALL_B = [  # stock object/tangible/wearables/necklace/necklace_s01.lua and pants/pants_s01.lua (pre-CU skeleton all_b)
    "object/creature/player/bothan_male.iff", "object/creature/player/bothan_female.iff",
    "object/creature/player/human_male.iff", "object/creature/player/human_female.iff",
    "object/creature/player/moncal_male.iff", "object/creature/player/moncal_female.iff",
    "object/creature/player/rodian_male.iff", "object/creature/player/rodian_female.iff",
    "object/creature/player/sullustan_male.iff", "object/creature/player/sullustan_female.iff",
    "object/creature/player/trandoshan_male.iff", "object/creature/player/trandoshan_female.iff",
    "object/creature/player/twilek_male.iff", "object/creature/player/twilek_female.iff",
    "object/creature/player/zabrak_male.iff", "object/creature/player/zabrak_female.iff",
    "object/mobile/vendor/aqualish_female.iff", "object/mobile/vendor/aqualish_male.iff",
    "object/mobile/vendor/bith_female.iff", "object/mobile/vendor/bith_male.iff",
    "object/mobile/vendor/bothan_female.iff", "object/mobile/vendor/bothan_male.iff",
    "object/mobile/vendor/devaronian_male.iff", "object/mobile/vendor/gran_male.iff",
    "object/mobile/vendor/human_female.iff", "object/mobile/vendor/human_male.iff",
    "object/mobile/vendor/ishi_tib_male.iff", "object/mobile/vendor/moncal_female.iff",
    "object/mobile/vendor/moncal_male.iff", "object/mobile/vendor/nikto_male.iff",
    "object/mobile/vendor/quarren_male.iff", "object/mobile/vendor/rodian_female.iff",
    "object/mobile/vendor/rodian_male.iff", "object/mobile/vendor/sullustan_female.iff",
    "object/mobile/vendor/sullustan_male.iff", "object/mobile/vendor/trandoshan_female.iff",
    "object/mobile/vendor/trandoshan_male.iff", "object/mobile/vendor/twilek_female.iff",
    "object/mobile/vendor/twilek_male.iff", "object/mobile/vendor/weequay_male.iff",
    "object/mobile/vendor/zabrak_female.iff", "object/mobile/vendor/zabrak_male.iff",
]
RACES_RING = [  # stock object/tangible/wearables/ring/ring_s01.lua (rings are a mesh, every species)
    "object/creature/player/bothan_male.iff", "object/creature/player/bothan_female.iff",
    "object/creature/player/human_male.iff", "object/creature/player/human_female.iff",
    "object/creature/player/ithorian_male.iff", "object/creature/player/ithorian_female.iff",
    "object/creature/player/moncal_male.iff", "object/creature/player/moncal_female.iff",
    "object/creature/player/rodian_male.iff", "object/creature/player/rodian_female.iff",
    "object/creature/player/sullustan_male.iff", "object/creature/player/sullustan_female.iff",
    "object/creature/player/trandoshan_male.iff", "object/creature/player/trandoshan_female.iff",
    "object/creature/player/twilek_male.iff", "object/creature/player/twilek_female.iff",
    "object/creature/player/wookiee_male.iff", "object/creature/player/wookiee_female.iff",
    "object/creature/player/zabrak_male.iff", "object/creature/player/zabrak_female.iff",
    "object/mobile/vendor/aqualish_female.iff", "object/mobile/vendor/aqualish_male.iff",
    "object/mobile/vendor/bith_female.iff", "object/mobile/vendor/bith_male.iff",
    "object/mobile/vendor/bothan_female.iff", "object/mobile/vendor/bothan_male.iff",
    "object/mobile/vendor/devaronian_male.iff", "object/mobile/vendor/gran_male.iff",
    "object/mobile/vendor/human_female.iff", "object/mobile/vendor/human_male.iff",
    "object/mobile/vendor/ishi_tib_male.iff", "object/mobile/vendor/ithorian_female.iff",
    "object/mobile/vendor/ithorian_male.iff", "object/mobile/vendor/moncal_female.iff",
    "object/mobile/vendor/moncal_male.iff", "object/mobile/vendor/nikto_male.iff",
    "object/mobile/vendor/quarren_male.iff", "object/mobile/vendor/rodian_female.iff",
    "object/mobile/vendor/rodian_male.iff", "object/mobile/vendor/sullustan_female.iff",
    "object/mobile/vendor/sullustan_male.iff", "object/mobile/vendor/trandoshan_female.iff",
    "object/mobile/vendor/trandoshan_male.iff", "object/mobile/vendor/twilek_female.iff",
    "object/mobile/vendor/twilek_male.iff", "object/mobile/vendor/weequay_male.iff",
    "object/mobile/vendor/wookiee_female.iff", "object/mobile/vendor/wookiee_male.iff",
    "object/mobile/vendor/zabrak_female.iff", "object/mobile/vendor/zabrak_male.iff",
]

# kind -> (experimental block from the stock s01 file of that kind, extra fields)
EXPERIMENTAL = {
    'necklace': (
        '\tnumberExperimentalProperties = {1, 1, 1},\n'
        '\texperimentalProperties = {"XX", "XX", "XX"},\n'
        '\texperimentalWeights = {1, 1, 1},\n'
        '\texperimentalGroupTitles = {"null", "null", "null"},\n'
        '\texperimentalSubGroupTitles = {"null", "null", "hitpoints"},\n'
        '\texperimentalMin = {0, 0, 1000},\n'
        '\texperimentalMax = {0, 0, 1000},\n'
        '\texperimentalPrecision = {0, 0, 0},\n'
        '\texperimentalCombineType = {0, 0, 4},\n', ''),
    'ring': (
        '\tnumberExperimentalProperties = {1, 1, 1},\n'
        '\texperimentalProperties = {"XX", "XX", "XX"},\n'
        '\texperimentalWeights = {1, 1, 1},\n'
        '\texperimentalGroupTitles = {"null", "null", "null"},\n'
        '\texperimentalSubGroupTitles = {"null", "null", "hitpoints"},\n'
        '\texperimentalMin = {0, 0, 1000},\n'
        '\texperimentalMax = {0, 0, 1000},\n'
        '\texperimentalPrecision = {0, 0, 0},\n'
        '\texperimentalCombineType = {0, 0, 4},\n', '\tobjectMenuComponent = "RingObjectMenuComponent",\n'),
    'pants': (
        '\tnumberExperimentalProperties = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1},\n'
        '\texperimentalProperties = {"XX", "XX", "XX", "XX", "XX", "XX", "XX", "XX", "XX", "XX", "XX", "XX", "XX", "XX", "XX", "XX"},\n'
        '\texperimentalWeights = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1},\n'
        '\texperimentalGroupTitles = {"null", "null", "null", "null", "null", "null", "null", "null", "null", "null", "null", "null", "null", "null", "null", "null"},\n'
        '\texperimentalSubGroupTitles = {"null", "null", "sockets", "hitpoints", "mod_idx_one", "mod_val_one", "mod_idx_two", "mod_val_two", "mod_idx_three", "mod_val_three", "mod_idx_four", "mod_val_four", "mod_idx_five", "mod_val_five", "mod_idx_six", "mod_val_six"},\n'
        '\texperimentalMin = {0, 0, 0, 1000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},\n'
        '\texperimentalMax = {0, 0, 0, 1000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},\n'
        '\texperimentalPrecision = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},\n'
        '\texperimentalCombineType = {0, 0, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1},\n', ''),
}

# batch 1b objects: (kind, name)  -> client object/tangible/wearables/<kind>/shared_<name>.iff
WEARABLES = [
    ('necklace', 'necklace_gcw_imperial'), ('necklace', 'necklace_gcw_rebel'), ('necklace', 'necklace_lifeday'),
    ('necklace', 'necklace_medallion_black_sun'), ('necklace', 'necklace_primitive_01'),
    ('necklace', 'necklace_primitive_03'), ('necklace', 'necklace_primitive_04'), ('necklace', 'necklace_rodian_safari'),
    ('pants', 'pants_outbreak_prison_guard'), ('pants', 'wod_nightsister_pants_s01'), ('pants', 'wod_nightsister_pants_s02'),
    ('ring', 'ring_gcw_imperial'), ('ring', 'ring_gcw_rebel'),
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_orig(rel):
    with open(os.path.join(ORIG, rel), 'rb') as f:
        return f.read()


def write_staged(rel, data):
    p = os.path.join(STAGED, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb') as f:
        f.write(data)


def write_diff(rel, old, new, combined):
    a = old.decode('latin-1').splitlines(keepends=True) if old is not None else []
    b = new.decode('latin-1').splitlines(keepends=True)
    lines = list(difflib.unified_diff(a, b, fromfile=('a/' + rel) if old is not None else '/dev/null', tofile='b/' + rel))
    text = ''.join(lines)
    if text and not text.endswith('\n'):
        text += '\n'
    p = os.path.join(DIFFS, rel + '.diff')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb') as f:
        f.write(text.encode('latin-1'))
    combined.append(text)


def newline_of(data):
    return b'\r\n' if b'\r\n' in data else b'\n'


def main():
    fixes = json.load(open(os.path.join(W, 'registration_fixes.json'), encoding='utf-8'))['fixes']
    scd._build_index()
    manifest, objects, combined = [], [], []

    # ---- 1a: registration repairs ----------------------------------------------------------------------
    for mangled, v in sorted(fixes.items()):
        correct = v['correct']
        assert len(v['files']) == 1, (mangled, v['files'])
        rel = v['files'][0]
        old = read_orig(rel)
        needle = ('"%s"' % mangled).encode('ascii')
        assert old.count(needle) == 1, (rel, old.count(needle))
        new = old.replace(needle, ('"%s"' % correct).encode('ascii'))
        write_staged(rel, new)
        write_diff(rel, old, new, combined)
        manifest.append((rel, sha256(old)))
        h, t = correct.rsplit('/', 1)
        objects.append({'batch': '1a', 'kind': 'repair', 'server': correct, 'shared': h + '/shared_' + t,
                        'was': mangled, 'files': [rel], 'line_endings': 'CRLF' if newline_of(old) == b'\r\n' else 'LF'})

    # ---- 1a: one more server-path repair that the underscore rule cannot derive --------------------------
    # MTG registered the Kashyyyk cave driftwood static as "emperors_cave_driftwood"; the client file is
    # object/building/kashyyyk/shared_cave_driftwood.iff, so Core3 expects object/building/kashyyyk/cave_driftwood.iff.
    rel = 'custom_content/building/kashyyyk/cave_driftwood.lua'
    old = read_orig(rel)
    needle = b'"object/building/kashyyyk/emperors_cave_driftwood.iff"'
    assert old.count(needle) == 1
    new = old.replace(needle, b'"object/building/kashyyyk/cave_driftwood.iff"')
    write_staged(rel, new)
    write_diff(rel, old, new, combined)
    manifest.append((rel, sha256(old)))
    objects.append({'batch': '1a', 'kind': 'repair', 'server': 'object/building/kashyyyk/cave_driftwood.iff',
                    'shared': 'object/building/kashyyyk/shared_cave_driftwood.iff', 'was': 'object/building/kashyyyk/emperors_cave_driftwood.iff',
                    'files': [rel], 'line_endings': 'CRLF' if newline_of(old) == b'\r\n' else 'LF', 'note': 'static prop (STAT form), SharedStaticObjectTemplate'})

    # ---- 1c: client-path repairs (objects.lua strings the client cannot resolve) ------------------------
    CLIENT_FIXES = [
        # (file, old string, new string, server path, shared path, also-fix-server-file-or-None)
        ('custom_content/tangible/loot/creature_loot/kashyyyk_loot/objects.lua',
         b'object/tangible/loot/creature_loot/kashyyyk/loot/shared_adventurers_remains_03.iff',
         b'object/tangible/loot/creature_loot/kashyyyk_loot/shared_adventurers_remains_03.iff', None),
        ('custom_content/static/worldbuilding/mechanical/objects.lua',
         b'object/object/static/worldbuilding/mechanical/shared_hoth_elevator.iff',
         b'object/static/worldbuilding/mechanical/shared_hoth_elevator.iff', None),
        ('custom_content/tangible/dungeon/avatar_platform/objects.lua',
         b'object/dungeon/avatar_platform/shared_avatar_terminal_technical_readout.iff',
         b'object/tangible/dungeon/avatar_platform/shared_avatar_terminal_technical_readout.iff',
         ('custom_content/tangible/dungeon/avatar_platform/avatar_terminal_technical_readout.lua',
          b'object/dungeon/avatar_platform/avatar_terminal_technical_readout.iff',
          b'object/tangible/dungeon/avatar_platform/avatar_terminal_technical_readout.iff')),
    ]
    for rel, old_s, new_s, server_fix in CLIENT_FIXES:
        old = read_orig(rel)
        n = old.count(old_s)
        assert n == 2, (rel, n)  # clientTemplateFileName and addClientTemplate
        new = old.replace(old_s, new_s)
        write_staged(rel, new)
        write_diff(rel, old, new, combined)
        manifest.append((rel, sha256(old)))
        files = [rel]
        if server_fix:
            srel, so, sn = server_fix
            sold = read_orig(srel)
            assert sold.count(so) == 1, (srel, sold.count(so))
            snew = sold.replace(so, sn)
            write_staged(srel, snew)
            write_diff(srel, sold, snew, combined)
            manifest.append((srel, sha256(sold)))
            files.append(srel)
        shared = new_s.decode('ascii')
        h, t = shared.rsplit('/', 1)
        objects.append({'batch': '1c', 'kind': 'client_repair', 'server': h + '/' + t[len('shared_'):], 'shared': shared,
                        'was': old_s.decode('ascii'), 'files': files, 'line_endings': 'CRLF' if newline_of(old) == b'\r\n' else 'LF'})

    # ---- 1a: the staff builder catalogue ----------------------------------------------------------------
    rel = 'sandbox/mtg_catalog.lua'
    old = read_orig(rel)
    new = old
    replaced = {}
    for mangled, v in fixes.items():
        needle = ('"%s"' % mangled).encode('ascii')
        n = new.count(needle)
        if n:
            new = new.replace(needle, ('"%s"' % v['correct']).encode('ascii'))
            replaced[mangled] = n
    write_staged(rel, new)
    write_diff(rel, old, new, combined)
    manifest.append((rel, sha256(old)))
    catalogue_note = {'file': rel, 'paths_replaced': len(replaced), 'occurrences': sum(replaced.values()),
                      'fixes_not_in_catalogue': sorted(m for m in fixes if m not in replaced)}

    # ---- 1b: new wearables -------------------------------------------------------------------------------
    by_kind = {}
    for kind, name in WEARABLES:
        by_kind.setdefault(kind, []).append(name)
    for kind, names in by_kind.items():
        folder = f'custom_content/tangible/wearables/{kind}'
        obj_lines = ['-- Fable backport batch 1 (14 Oct 2026): shared templates for NGE %s with no server template in Core3-dev.' % kind,
                     '-- Client files come from the Mod the Galaxy archives (see README.md, rights); style as custom_content/tangible/wearables/belt/objects.lua.',
                     '']
        srv_lines = ['-- Fable backport batch 1 (14 Oct 2026): server objects for NGE %s.' % kind, '']
        for name in names:
            shared = f'object/tangible/wearables/{kind}/shared_{name}.iff'
            server = f'object/tangible/wearables/{kind}/{name}.iff'
            var = f'object_tangible_wearables_{kind}_{name}'
            svar = f'object_tangible_wearables_{kind}_shared_{name}'
            info = swg_iff.resolved(shared)
            win = scd._index.get(shared.lower())
            obj_lines += ['--**********************************************', '',
                          f'{svar} = SharedTangibleObjectTemplate:new {{',
                          f'\tclientTemplateFileName = "{shared}"', '}',
                          f'ObjectTemplates:addClientTemplate({svar}, "{shared}")', '']
            exp, extra = EXPERIMENTAL[kind]
            races = RACES_RING if kind == 'ring' else RACES_ALL_B
            race_text = '\tplayerRaces = { ' + ',\n\t\t\t\t'.join(f'"{r}"' for r in races) + ' },\n'
            srv = (f'-- Fable backport batch 1 (14 Oct 2026). Client template {shared} ({os.path.basename(win[0]) if win else "?"}),\n'
                   f'-- form {info["form"] if info else "?"}, gameObjectType {hex(info["gameObjectType"]) if info and info["gameObjectType"] is not None else "?"}, '
                   f'appearance {info["appearanceFilename"] if info else "?"}.\n'
                   f'-- Style: object/tangible/wearables/{kind}/{kind}_s01.lua (pre-CU species list; new species are added when they are in).\n\n'
                   f'{var} = {svar}:new {{\n{extra}{race_text}\n{exp}}}\n\n'
                   f'ObjectTemplates:addTemplate({var}, "{server}")\n')
            srel = f'{folder}/{name}.lua'
            write_staged(srel, srv.encode('ascii'))
            write_diff(srel, None, srv.encode('ascii'), combined)
            manifest.append((srel, 'new'))
            srv_lines.append(f'includeFile("{srel}")')
            objects.append({'batch': '1b', 'kind': 'new', 'server': server, 'shared': shared, 'var': var, 'shared_var': svar,
                            'files': [srel, f'{folder}/objects.lua', f'{folder}/serverobjects.lua'], 'line_endings': 'LF'})
        for fname, lines in ((f'{folder}/objects.lua', obj_lines), (f'{folder}/serverobjects.lua', srv_lines)):
            data = ('\n'.join(lines) + '\n').encode('ascii')
            write_staged(fname, data)
            write_diff(fname, None, data, combined)
            manifest.append((fname, 'new'))

    # include-chain edits: custom_content/tangible/wearables/serverobjects.lua and allobjects.lua
    def insert_after(rel, anchors):
        old = read_orig(rel)
        nl = newline_of(old)
        lines = old.split(nl)
        for anchor, new_line in anchors:
            anchor_b, new_b = anchor.encode('ascii'), new_line.encode('ascii')
            idx = [i for i, l in enumerate(lines) if l.strip() == anchor_b]
            assert len(idx) == 1, (rel, anchor, idx)
            assert not any(l.strip() == new_b for l in lines), (rel, new_line, 'already present')
            lines.insert(idx[0] + 1, new_b)
        new = nl.join(lines)
        write_staged(rel, new)
        write_diff(rel, old, new, combined)
        manifest.append((rel, sha256(old)))

    insert_after('custom_content/tangible/wearables/serverobjects.lua', [
        ('includeFile("custom_content/tangible/wearables/jacket/serverobjects.lua")', 'includeFile("custom_content/tangible/wearables/necklace/serverobjects.lua")'),
        ('includeFile("custom_content/tangible/wearables/necklace/serverobjects.lua")', 'includeFile("custom_content/tangible/wearables/pants/serverobjects.lua")'),
        ('includeFile("custom_content/tangible/wearables/robe/serverobjects.lua")', 'includeFile("custom_content/tangible/wearables/ring/serverobjects.lua")'),
    ])
    insert_after('allobjects.lua', [
        ('includeFile("custom_content/tangible/wearables/jacket/objects.lua")', 'includeFile("custom_content/tangible/wearables/necklace/objects.lua")'),
        ('includeFile("custom_content/tangible/wearables/necklace/objects.lua")', 'includeFile("custom_content/tangible/wearables/pants/objects.lua")'),
        ('includeFile("custom_content/tangible/wearables/robe/objects.lua")', 'includeFile("custom_content/tangible/wearables/ring/objects.lua")'),
    ])

    # ---- outputs -----------------------------------------------------------------------------------------
    with open(os.path.join(ROOT, 'batch1.diff'), 'wb') as f:
        f.write(''.join(combined).encode('latin-1'))
    with open(os.path.join(ROOT, 'apply-manifest.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# path relative to MMOCoreORB/bin/scripts/object<TAB>sha256 of the Core3-dev file this was diffed against, or new\n')
        for rel, h in manifest:
            f.write(f'{rel}\t{h}\n')
    with open(os.path.join(W, 'batch1_objects.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'objects': objects, 'catalogue': catalogue_note, 'manifest': manifest}, f, indent=1)
    print(f'staged {len(manifest)} files: {sum(1 for _, h in manifest if h != "new")} changed, {sum(1 for _, h in manifest if h == "new")} new; '
          f'objects: {sum(1 for o in objects if o["batch"] == "1a")} repaired, {sum(1 for o in objects if o["batch"] == "1b")} new')
    print('catalogue:', catalogue_note['paths_replaced'], 'paths /', catalogue_note['occurrences'], 'occurrences; not in catalogue:', len(catalogue_note['fixes_not_in_catalogue']))


if __name__ == '__main__':
    main()
