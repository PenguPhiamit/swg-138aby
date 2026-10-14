"""Stage Hoth batch B: camps (B1), the mynock den as a spawned ice cave plus its terrain patch (B2), and the names
TSV (B3). Our own code (Fable, 14 Oct 2026). Heights come from the Core3 height port validated on Hoth.

    python -I stage_batchB.py
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
OUT = os.path.join(ROOT, '..')
sys.path.insert(0, os.path.join(OUT, 'Fable-planet-test', 'tools'))
sys.path.insert(0, os.path.join(OUT, 'Fable-hoth-caves', 'tools'))
import trn_read  # noqa: E402
import trn_write  # noqa: E402
import ws_read  # noqa: E402
from trn_iff import build, client_file, form, chunk, parse  # noqa: E402

STAGED = os.path.join(ROOT, 'staged', 'MMOCoreORB', 'bin', 'scripts')
CLIENT_STAGED = os.path.join(ROOT, 'staged', 'client')
WORK = os.path.join(ROOT, 'work')
SCREENPLAYS_ORIG_SHA = 'd8f9b5f701f6150886f53a5a196b6225b22d5e2f66ca3e47702ff194d6d9cbe0'
BELLUM_CAVES = os.path.join(OUT, '..', 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'bin', 'scripts', 'screenplays', 'caves', 'hoth_ice_caves.lua')

P = {  # client shared templates (all present in local_planets.tre's merged CRC table; server templates checked by dev_check.sh)
    'tent': 'object/static/structure/general/camp_tent_s01.iff', 'fire': 'object/static/structure/general/campfire_fresh.iff',
    'cot': 'object/static/structure/general/camp_cot_s01.iff', 'stool': 'object/static/structure/general/camp_stool_short_s01.iff',
    'spit': 'object/static/structure/general/camp_spit_s01.iff', 'pallet': 'object/static/structure/general/palette_supply_01.iff',
    'rebl_corral': 'object/static/structure/general/poi_all_rebl_corral_64x64_s01.iff',
    'atst': 'object/static/structure/general/atst_debris_01.iff',
    'impl_wall': 'object/static/structure/military/military_wall_med_imperial_16_style_01.iff',
    'rebl_wall': 'object/static/structure/military/military_wall_med_rebl_16_style_01.iff',
    'crate': 'object/static/structure/military/bunker_crate_style_01.iff',
}
CAVE = 'object/building/general/cave_06_flatland_s01_ice.iff'
CAVE_SITE = (-2000.0, -4800.0, 0)  # x, y, heading; mynock fields south (batch A), ground 44.8 m, 100 m steps <= 13 m
CAVE_BUILDING_ID_BELLUM = 6453174
MOUTH_OFFSET = (0.0, 12.0)  # stock s01 caves: the terrain exclusion disc sits ~12 m north of the building origin, r 9-10

# Camps: name, (x, y), zone, props [(key, dx, dy, heading)], npcs [(template, respawn, dx, dy, heading)]
CAMPS = [
    ('imperial_forward_camp', (2600.0, -3900.0), 'hoth_imperial_zone_east',
     [('impl_wall', -14, 18, 0), ('impl_wall', 14, 18, 0), ('impl_wall', -14, -18, 0), ('impl_wall', 14, -18, 0), ('tent', -8, 6, 180), ('crate', 7, 7, 30), ('fire', 0, 2, 0), ('pallet', 10, -4, 0)],
     [('hoth_snowtrooper', 300, 12, 0, -90), ('hoth_snowtrooper', 300, -12, 0, 90), ('hoth_snowtrooper', 300, 0, 13, 180), ('hoth_snowtrooper', 300, 0, -13, 0),
      ('hoth_snowtrooper', 300, 9, 9, -135), ('hoth_snowtrooper', 300, -9, -9, 45), ('hoth_snowtrooper_sergeant', 300, 3, -3, 135), ('imperial_recruiter', 60, -4, 4, -45)]),
    ('rebel_forward_camp', (-2800.0, 1200.0), 'hoth_rebel_zone_northwest',
     [('rebl_corral', 0, 0, 0), ('rebl_wall', -14, -18, 0), ('rebl_wall', 14, -18, 0), ('tent', 8, -6, 0), ('tent', -9, -5, 20), ('fire', 0, -2, 0), ('cot', 6, 4, 90)],
     [('hoth_rebel_snow_soldier', 300, 12, 0, -90), ('hoth_rebel_snow_soldier', 300, -12, 0, 90), ('hoth_rebel_snow_soldier', 300, 0, 13, 180), ('hoth_rebel_snow_soldier', 300, 0, -13, 0),
      ('hoth_rebel_snow_soldier', 300, 9, 9, -135), ('hoth_rebel_snow_soldier', 300, -9, -9, 45), ('hoth_rebel_snow_sergeant', 300, 3, 3, -135), ('rebel_recruiter', 60, -4, -4, 45)]),
    ('scavenger_camp', (-1400.0, -3300.0), 'hoth_scavenger_zone_southwest',
     [('tent', -7, 5, 150), ('tent', 7, 6, 210), ('fire', 0, 0, 0), ('spit', 0, 3, 0), ('cot', -6, -3, 60), ('stool', 2, -2, 0), ('stool', -2, -2, 0), ('pallet', 9, -5, 0), ('atst', 18, 14, 40)],
     [('hoth_scavenger', 300, 5, 1, 15), ('hoth_scavenger', 300, 3, -5, 87), ('hoth_scavenger', 300, -4, -6, 159), ('hoth_scavenger', 300, -6, 2, -129), ('hoth_scavenger', 300, -1, 6, -57), ('junk_dealer', 60, 4, 4, -120)]),
    ('raider_camp', (-1200.0, -3600.0), 'hoth_scavenger_zone_southwest',
     [('tent', 0, 7, 180), ('fire', 0, 0, 0), ('crate', 6, 3, 0), ('crate', -6, 3, 0)],
     [('hoth_scavenger_raider', 300, 0, 10, 0), ('hoth_scavenger_raider', 300, 8.7, 5, 60), ('hoth_scavenger_raider', 300, 8.7, -5, 120),
      ('hoth_scavenger_raider', 300, 0, -10, 180), ('hoth_scavenger_raider', 300, -8.7, -5, -120), ('hoth_scavenger_raider', 300, -8.7, 5, -60)]),
    ('contested_ground', (2400.0, 200.0), None,
     [('atst', 0, 0, 75), ('crate', -4, 14, 0), ('crate', 4, -14, 0)],
     [('hoth_snowtrooper', 300, -6, 14, 180), ('hoth_snowtrooper', 300, -3, 14, 180), ('hoth_snowtrooper', 300, 3, 14, 180), ('hoth_snowtrooper', 300, 6, 14, 180), ('hoth_snowtrooper_sergeant', 300, 0, 18, 180),
      ('hoth_rebel_snow_soldier', 300, -6, -14, 0), ('hoth_rebel_snow_soldier', 300, -3, -14, 0), ('hoth_rebel_snow_soldier', 300, 3, -14, 0), ('hoth_rebel_snow_soldier', 300, 6, -14, 0), ('hoth_rebel_snow_sergeant', 300, 0, -18, 0)]),
    ('salvage_detail', (-100.0, -1960.0), 'outpost (MTG debris field, flattened ground)',
     [],
     [('hoth_imperial_salvage_tech', 300, 5, 4, 60), ('hoth_imperial_salvage_tech', 300, -2, 7, 180), ('hoth_imperial_salvage_tech', 300, -6, 2, -60), ('hoth_snowtrooper', 300, 10, -6, 0), ('hoth_snowtrooper', 300, -10, -6, 0)]),
]

NAMES = [  # stf, key, English, used by
    ('string/en/hoth_region_names.stf', 'hothstarport', 'Scavenger Starport', 'exists (MTG); outpost city region'),
    ('string/en/hoth_region_names.stf', 'world_spawner', 'Hoth', 'exists (MTG); world spawner'),
    ('string/en/hoth_region_names.stf', 'ice_caves', 'The Ice Caves', 'cave no-build region, if renamed to @hoth_region_names:ice_caves'),
    ('string/en/hoth_region_names.stf', 'frostfang_cavern', "Frostfang's Cavern", 'cave_01_ice (-622, 2292), map POI'),
    ('string/en/hoth_region_names.stf', 'icemaw_den', "Icemaw's Den", 'cave_04_ice_s01 (-385, 2436), map POI'),
    ('string/en/hoth_region_names.stf', 'snowblind_lair', "Snowblind's Lair", 'cave_02_ice (-543, 2674), map POI'),
    ('string/en/hoth_region_names.stf', 'matriarch_cavern', "The Matriarch's Cavern", 'cave_03_ice (-75, 2969), map POI'),
    ('string/en/hoth_region_names.stf', 'mynock_den', 'Mynock Den', 'spawned cave (-2000, -4800), map POI'),
    ('string/en/hoth_region_names.stf', 'rancor_grounds', 'Glacial Rancor Grounds', 'rancor option (c), (600, -4600)'),
    ('string/en/hoth_region_names.stf', 'imperial_forward_camp', 'Imperial Forward Camp', 'B1 camp (2600, -3900)'),
    ('string/en/hoth_region_names.stf', 'rebel_forward_camp', 'Rebel Forward Camp', 'B1 camp (-2800, 1200)'),
    ('string/en/hoth_region_names.stf', 'scavenger_camp', "Scavengers' Camp", 'B1 camp (-1400, -3300)'),
    ('string/en/hoth_region_names.stf', 'raider_camp', "Raiders' Camp", 'B1 camp (-1200, -3600)'),
    ('string/en/hoth_region_names.stf', 'contested_ground', 'Contested Ground', 'B1 skirmish line (2400, 200)'),
    ('string/en/hoth_region_names.stf', 'lucky_despot_wreck', 'Lucky Despot Wreck', 'MTG debris field by the outpost (-100, -1960)'),
    ('string/en/hoth_region_names.stf', 'tauntaun_plains_west', 'Western Tauntaun Plains', 'batch A area (optional name)'),
    ('string/en/hoth_region_names.stf', 'tauntaun_plains_east', 'Eastern Tauntaun Plains', 'batch A area (optional name)'),
    ('string/en/hoth_region_names.stf', 'mynock_fields', 'Mynock Fields', 'batch A area (optional name)'),
    ('string/en/hoth_region_names.stf', 'wampa_flanks', 'Wampa Flanks', 'batch A areas (optional name)'),
    ('string/en/hoth_region_names.stf', 'imperial_zone', 'Imperial Patrol Zone', 'batch A area (optional name)'),
    ('string/en/hoth_region_names.stf', 'rebel_zone', 'Rebel Patrol Zone', 'batch A area (optional name)'),
    ('string/en/hoth_region_names.stf', 'scavenger_zone', 'Scavenger Country', 'batch A area (optional name)'),
]

_ev = None


def ground(x, y):
    global _ev
    if _ev is None:
        _ev = trn_read.HeightEvaluator(trn_read.read_trn(client_file('terrain/hoth.trn')), trn_read.client_bitmap_loader)
    return round(_ev.server_height(x, y), 1)


def write(rel, text, base=STAGED):
    path = os.path.join(base, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='ascii', newline='\n') as f:
        f.write(text)
    return path


def camps_lua():
    lines = ['-- Hoth camps and patrol posts (Fable batch B, 14 Oct 2026; outputs/Fable-hoth-batchB/README.md).',
             '-- Layout idea from Bellum Gero\'s Hoth static spawns (github.com/Miphstoe/BellumGero-Live, AGPL-3.0: NPC rings',
             '-- at each outpost, two trooper/rebel lines, a raider camp), re-sited into our batch A zones on MTG\'s map with',
             '-- stock camp props. Heights are the terrain heights at each point (Core3 height port, validated on Hoth).',
             '', 'HothCampsScreenPlay = ScreenPlay:new {', '\tnumberOfActs = 1,', '', '\tscreenplayName = "HothCampsScreenPlay"', '}', '',
             'registerScreenPlay("HothCampsScreenPlay", true)', '', 'function HothCampsScreenPlay:start()', '\tif (isZoneEnabled("hoth")) then',
             '\t\tself:spawnSceneObjects()', '\t\tself:spawnMobiles()', '\tend', 'end', '', 'function HothCampsScreenPlay:spawnSceneObjects()']
    report = []
    for name, (cx, cy), zone, props, npcs in CAMPS:
        lines.append(f'\t-- {name} at {cx:.0f}, {cy:.0f} ({zone or "between the zones"})')
        for key, dx, dy, heading in props:
            x, y = cx + dx, cy + dy
            z = ground(x, y)
            lines.append(f'\tspawnSceneObject("hoth", "{P[key]}", {x:g}, {z:g}, {y:g}, 0, {heading})')
            report.append({'camp': name, 'object': P[key], 'x': x, 'z': z, 'y': y})
    lines += ['end', '', 'function HothCampsScreenPlay:spawnMobiles()']
    for name, (cx, cy), zone, props, npcs in CAMPS:
        lines.append(f'\t-- {name}')
        for template, respawn, dx, dy, heading in npcs:
            x, y = cx + dx, cy + dy
            z = ground(x, y)
            lines.append(f'\tspawnMobile("hoth", "{template}", {respawn}, {x:g}, {z:g}, {y:g}, {heading}, 0)')
            report.append({'camp': name, 'mobile': template, 'x': x, 'z': z, 'y': y})
    lines += ['end', '']
    return '\n'.join(lines), report


def den_lua(rows):
    cx, cy, heading = CAVE_SITE
    z = ground(cx, cy)
    lines = ['-- Mynock den: Bellum Gero\'s fifth Hoth cave (cave_06_flatland_s01_ice, 23 spawns) re-homed on MTG\'s map, where',
             '-- that building is not in the snapshot. The cave is spawned here and its cells looked up by number, so the',
             '-- cell-local spawn points from Bellum\'s generated hoth_ice_caves.lua (AGPL-3.0) apply unchanged.',
             '-- Needs the terrain patch in outputs/Fable-hoth-batchB/staged/client/terrain/hoth.trn (flatten + mouth exclusion)',
             '-- packed into local_planets.tre; see the README. Fable batch B, 14 Oct 2026.',
             '', 'HothMynockDenScreenPlay = ScreenPlay:new {', '\tnumberOfActs = 1,', '', '\tscreenplayName = "HothMynockDenScreenPlay",', '',
             f'\tcaveTemplate = "{CAVE}",', f'\tcaveX = {cx:g}, caveZ = {z:g}, caveY = {cy:g}, caveHeading = {heading},', '',
             '\t-- {template, respawn, cell-local x, z, y, heading, cell number (1..11 in portal-layout order)}', '\tmobiles = {']
    for r in rows:
        cell = r['cell'] - CAVE_BUILDING_ID_BELLUM
        lines.append(f'\t\t{{"{r["template"]}", {r["respawn"]}, {r["x"]:g}, {r["z"]:g}, {r["y"]:g}, {r["heading"]:g}, {cell}}},')
    lines += ['\t}', '}', '', 'registerScreenPlay("HothMynockDenScreenPlay", true)', '',
              'function HothMynockDenScreenPlay:start()', '\tif (isZoneEnabled("hoth")) then', '\t\tself:spawnDen()', '\tend', 'end', '',
              'function HothMynockDenScreenPlay:spawnDen()',
              '\tlocal pCave = spawnSceneObject("hoth", self.caveTemplate, self.caveX, self.caveZ, self.caveY, 0, self.caveHeading)', '',
              '\tif (pCave == nil or not SceneObject(pCave):isBuildingObject()) then',
              '\t\tprint("HothMynockDenScreenPlay: could not spawn " .. self.caveTemplate)', '\t\treturn', '\tend', '',
              '\tlocal cells = BuildingObject(pCave):getTotalCellNumber()', '',
              '\tif (cells < 11) then', '\t\tprint("HothMynockDenScreenPlay: cave has " .. cells .. " cells, expected 11")', '\tend', '',
              '\tfor i = 1, #self.mobiles do', '\t\tlocal m = self.mobiles[i]',
              '\t\tlocal pCell = BuildingObject(pCave):getCell(m[7])', '', '\t\tif (pCell ~= nil) then',
              '\t\t\tspawnMobile("hoth", m[1], m[2], m[3], m[4], m[5], m[6], SceneObject(pCell):getObjectID())', '\t\telse',
              '\t\t\tprint("HothMynockDenScreenPlay: cave has no cell " .. m[7])', '\t\tend', '\tend', 'end', '']
    return '\n'.join(lines), z


def terrain_patch(z):
    """MTG's hoth.trn plus one layer: a feathered flatten disc at the cave site and an exclusion disc at the mouth,
    the same two rules the stock caves use (see the README)."""
    cx, cy, heading = CAVE_SITE
    data = client_file('terrain/hoth.trn')
    before = trn_read.read_trn(data)
    nodes = parse(data)
    lyrs = None
    for n in nodes[0].children[0].children[1].children[0].children:  # PTAT > 0014 > TGEN > 0000 > ...
        if n.is_form and n.form == 'LYRS':
            lyrs = n
    assert lyrs is not None
    mouth = form('AEXC', form('0000', trn_write.ihdr(True, 'fable mynock den mouth'), chunk('DATA', b'')))
    layer = trn_write.layer('fable_mynock_den',
                            trn_write.boundary_circle('den flatten', cx, cy, 160.0, feather_type=3, feather=0.45),
                            trn_write.affector_height_constant('den floor', 0, z),
                            trn_write.layer('mouth exclusion', trn_write.boundary_circle('mouth', cx + MOUTH_OFFSET[0], cy + MOUTH_OFFSET[1], 12.0, 0, 0.0), mouth))
    lyrs.children.append(layer)
    out = build(nodes)
    after = trn_read.read_trn(out)
    ev_b = trn_read.HeightEvaluator(before, trn_read.client_bitmap_loader)
    ev_a = trn_read.HeightEvaluator(after, trn_read.client_bitmap_loader)
    probes = {'cave centre': (cx, cy), 'cave mouth': (cx, cy + 12), '150 m south': (cx, cy - 150), '250 m north': (cx, cy + 250),
              'starport pad': (20.3, -1982.2), '500 m north of pad': (20.3, -1482.2), 'cave_03_ice': (-75, 2969)}
    heights = {k: (round(ev_b.server_height(*p), 2), round(ev_a.server_height(*p), 2)) for k, p in probes.items()}
    os.makedirs(os.path.join(CLIENT_STAGED, 'terrain'), exist_ok=True)
    open(os.path.join(CLIENT_STAGED, 'terrain', 'hoth.trn'), 'wb').write(out)
    return {'source': 'terrain/hoth.trn from mtg_patch_022.tre', 'source_sha256': hashlib.sha256(data).hexdigest(),
            'patched_sha256': hashlib.sha256(out).hexdigest(), 'bytes': (len(data), len(out)), 'round_trip_identical': build(parse(out)) == out,
            'core3_order_notes_before': len(before['notes']), 'core3_order_notes_after': len(after['notes']),
            'top_layers': (len(before['layers']), len(after['layers'])), 'heights_before_after': heights,
            'layer': {'flatten': {'cx': cx, 'cy': cy, 'r': 160, 'feather': 0.45, 'height': z}, 'exclusion': {'cx': cx + MOUTH_OFFSET[0], 'cy': cy + MOUTH_OFFSET[1], 'r': 12}}}


def main():
    checks = {}
    rows, _ = ws_read.read_bellum(BELLUM_CAVES)
    den_rows = [r for r in rows if r['cave_comment'] == CAVE_BUILDING_ID_BELLUM]
    assert len(den_rows) == 23, len(den_rows)
    camps_text, placed = camps_lua()
    write('screenplays/poi/hoth_camps.lua', camps_text)
    den_text, z = den_lua(den_rows)
    write('screenplays/poi/hoth_mynock_den.lua', den_text)
    checks['terrain_patch'] = terrain_patch(z)
    # include lines, alphabetical in the poi block
    orig = open(os.path.join(WORK, 'screenplays.lua.orig'), 'rb').read()
    assert hashlib.sha256(orig).hexdigest() == SCREENPLAYS_ORIG_SHA
    lines = orig.split(b'\n')
    poi = [i for i, l in enumerate(lines) if l.startswith(b'includeFile("poi/')]
    at = next((i for i in poi if lines[i] > b'includeFile("poi/hoth'), poi[-1] + 1)
    lines[at:at] = [b'includeFile("poi/hoth_camps.lua") -- Sandbox: Hoth camps (Fable batch B)',
                    b'includeFile("poi/hoth_mynock_den.lua") -- Sandbox: Hoth mynock den (Fable batch B)']
    patched = b'\n'.join(lines)
    os.makedirs(os.path.join(STAGED, 'screenplays'), exist_ok=True)
    open(os.path.join(STAGED, 'screenplays', 'screenplays.lua'), 'wb').write(patched)
    # names TSV
    with open(os.path.join(ROOT, 'names.tsv'), 'w', encoding='ascii', newline='\n') as f:
        f.write('stf\tkey\tenglish\tused_by\n')
        for row in NAMES:
            f.write('\t'.join(row) + '\n')
    # checks
    checks['camps'] = [{'name': n, 'centre': c, 'zone': zn, 'ground': ground(*c), 'props': len(p), 'npcs': len(m)} for n, c, zn, p, m in CAMPS]
    checks['placed_objects'] = placed
    checks['den'] = {'building': CAVE, 'site': CAVE_SITE, 'ground': z, 'spawns': len(den_rows),
                     'cells_used': sorted({r['cell'] - CAVE_BUILDING_ID_BELLUM for r in den_rows}),
                     'templates': sorted({r['template'] for r in den_rows})}
    checks['client_templates_in_crc_table'] = sorted(set(P.values()) | {CAVE})
    checks['files'] = {}
    rels = ['screenplays/screenplays.lua', 'screenplays/poi/hoth_camps.lua', 'screenplays/poi/hoth_mynock_den.lua']
    man = ['# path relative to MMOCoreORB/bin/scripts\tsha256 of the Core3-dev file the staged copy was made from (14 Oct 2026), or new']
    for rel in rels:
        d = open(os.path.join(STAGED, rel), 'rb').read()
        checks['files'][rel] = {'staged_sha256': hashlib.sha256(d).hexdigest(), 'bytes': len(d)}
        man.append(f'{rel}\t{SCREENPLAYS_ORIG_SHA if rel == "screenplays/screenplays.lua" else "new"}')
    open(os.path.join(ROOT, 'apply-manifest.tsv'), 'w', encoding='ascii', newline='\n').write('\n'.join(man) + '\n')
    json.dump(checks, open(os.path.join(ROOT, 'checks.json'), 'w', encoding='utf-8'), indent=1)
    print(json.dumps(checks['terrain_patch'], indent=1))
    print('camps:', [(c['name'], c['ground'], c['props'], c['npcs']) for c in checks['camps']])
    print('den:', checks['den'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
