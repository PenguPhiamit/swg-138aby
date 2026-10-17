"""PL-06: the edits to files that already exist in Core3-dev, applied to copies (a/ = dev HEAD, b/ = ours).
    python3 -I edit_dev.py <dir with a/ and b/>      (run by make_patch.sh inside WSL; never touches /opt/swg)
"""
import os, re, sys
D = sys.argv[1]
S = 'MMOCoreORB/bin/scripts/'


def edit(rel, reps):
    p = os.path.join(D, 'b', rel)
    s = open(p, newline='').read()
    for a, b in reps:
        assert s.count(a) == 1, (rel, a[:70], s.count(a))
        s = s.replace(a, b)
    open(p, 'w', newline='').write(s)


def entry(name, lo, hi, weight=15):
    return ('\t\t{\n\t\t\tlairTemplateName = "%s",\n\t\t\tspawnLimit = -1,\n\t\t\tminDifficulty = %d,\n\t\t\tmaxDifficulty = %d,\n'
            '\t\t\tnumberToSpawn = 15,\n\t\t\tweighting = %d,\n\t\t\tsize = 20,\n\t\t},\n') % (name, lo, hi, weight)


# more wildlife: wandering packs (creature_dynamic, stock) in each ring, at that ring's levels
ADD = {
    'hutta_lowlands_near': [('rori_swamp_tusk_cat_hunt_neutral_none', 20, 26), ('talus_rot_mite_pack_neutral_none', 19, 24),
                            ('rori_borgle_pack_neutral_none', 19, 24), ('talus_fynock_pack_neutral_none', 21, 26)],
    'hutta_lowlands_mid': [('talus_guf_drolg_pack_neutral_none', 31, 36), ('rori_leviasquall_pack_neutral_none', 32, 37),
                           ('naboo_sharupat_pack_diseased_neutral_none', 31, 36), ('talus_jungle_fynock_pack_neutral_none', 33, 38)],
    'hutta_deep_swamp': [('talus_savage_guf_drolg_pack_neutral_none', 40, 46), ('rori_midnight_vir_vur_pack_neutral_none', 42, 48),
                         ('talus_mutated_kahmurra_pack_neutral_none', 44, 50), ('naboo_veermok_marauder_neutral_none', 45, 52)],
}
for group, rows in ADD.items():
    rel = S + 'mobile/spawn/hutta/%s.lua' % group
    s = open(os.path.join(D, 'b', rel), newline='').read()
    tail = '\t}\n}\n\naddSpawnGroup("%s", %s);' % (group, group)
    assert s.count(tail) == 1, (group, s[-200:])
    note = '\t\t-- PL-06 (17 Oct 2026): wandering packs, so the ring feels alive between the lairs\n'
    s = s.replace(tail, note + ''.join(entry(*r) for r in rows) + tail)
    open(os.path.join(D, 'b', rel), 'w', newline='').write(s)

edit(S + 'managers/planet/hutta_regions.lua', [
    ('-- (31-38) and the deep swamp 3,200-5,200 m (37-56).',
     '-- (31-38) and the deep swamp 3,200-5,200 m (37-56).\n-- PL-06 (17 Oct 2026): the owner found the planet empty; each ring\'s spawn limit is doubled or nearly (48 -> 96,\n-- 64 -> 112, 64 -> 96) and its group gains four wandering packs.'),
    ('{"hutta_lowlands_near"}, 48}', '{"hutta_lowlands_near"}, 96}'),
    ('{"hutta_lowlands_mid"}, 64}', '{"hutta_lowlands_mid"}, 112}'),
    ('{"hutta_deep_swamp"}, 64}', '{"hutta_deep_swamp"}, 96}'),
])

rm = open(os.path.join(D, 'b', S + 'managers/resource_manager.lua'), newline='').read()
m = re.search(r'(?m)^activeZones = "([a-z0-9_,]+)"$', rm)
assert m and 'hutta' not in m.group(1).split(','), m
edit(S + 'managers/resource_manager.lua', [
    (m.group(0), '-- Nal Hutta (PL-06, 17 Oct 2026, Claude): hutta added. It was missing, so the planet had no resources at all and the\n'
                 '-- test galaxy logged "backfillZones: hutta is not in activeZones, ignored". Its 45 planet types (water, flora,\n'
                 '-- creature, energy: Rori\'s rows cloned, the planet was made from Rori) are in the merged resource_tree.iff of\n'
                 '-- local_planets.tre (nal-hutta-life/build_nal_hutta_life.py); this needs that archive.\n'
                 'activeZones = "%s,hutta"' % m.group(1)),
])

edit(S + 'screenplays/screenplays.lua', [
    ('includeFile("sandbox/hutta_home.lua")\n',
     'includeFile("sandbox/hutta_home.lua")\nincludeFile("sandbox/hutta_life_places.lua")\nincludeFile("sandbox/hutta_life.lua")\n'),
])
edit(S + 'mobile/serverobjects.lua', [
    ('includeFile("sandbox/hutta_home.lua")\n', 'includeFile("sandbox/hutta_home.lua")\nincludeFile("sandbox/hutta_life.lua")\n'),
])
edit(S + 'mobile/conversations.lua', [
    ('includeFile("conversations/sandbox/hutta_home_conv.lua")\n',
     'includeFile("conversations/sandbox/hutta_home_conv.lua")\nincludeFile("conversations/sandbox/hutta_life_conv.lua")\n'),
])
print('edits ok')
