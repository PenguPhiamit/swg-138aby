"""Stage the Hoth ice-cave screenplay for Core3-dev from Bellum Gero's generated file, keeping only spawns whose cell
exists in MTG's snapshot/hoth.ws (verified with ws_read.py). Our own code (Fable, 14 Oct 2026).

    python -I stage_caves.py        # writes staged/.../caves/hoth_ice_caves.lua, staged/.../screenplays.lua, checks.json
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
H = os.path.normpath(os.path.join(ROOT, '..', '..'))
sys.path.insert(0, HERE)
import ws_read  # noqa: E402

BELLUM = os.path.join(H, 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'bin', 'scripts', 'screenplays', 'caves', 'hoth_ice_caves.lua')
STAGED = os.path.join(ROOT, 'staged', 'MMOCoreORB', 'bin', 'scripts', 'screenplays')
ORIG = os.path.join(ROOT, 'work', 'screenplays.lua.orig')
REGISTERED = {'hoth_elder_wampa', 'hoth_greater_ice_mynock', 'hoth_ice_mynock', 'hoth_imperial_salvage_tech',
              'hoth_mynock_broodmother', 'hoth_probe_droid', 'hoth_rebel_snow_sergeant', 'hoth_rebel_snow_soldier',
              'hoth_scavenger', 'hoth_scavenger_raider', 'hoth_snowtrooper', 'hoth_snowtrooper_sergeant',
              'hoth_tauntaun_bull', 'hoth_tauntaun', 'hoth_wampa_frostfang', 'hoth_wampa_icemaw', 'hoth_wampa',
              'hoth_wampa_matriarch', 'hoth_wampa_patriarch', 'hoth_wampa_snowblind'}  # mobile/hoth/*.lua, 14 Oct
INCLUDE_AFTER = 'includeFile("caves/endor_orphaned_marauder_cave.lua")\n'
INCLUDE_LINE = 'includeFile("caves/hoth_ice_caves.lua") -- Sandbox: Hoth ice caves (Bellum Gero, AGPL-3.0)\n'

HEADER = """-- Hoth ice caves: wampa dens in the four ice caves of MTG's snapshot/hoth.ws.
-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/screenplays/caves/hoth_ice_caves.lua (their generated file; spawn rows are
-- {template, respawn, cell-local x, z, y, heading, cell object id}). Staged for this server 14 Oct 2026 (Fable;
-- outputs/Fable-hoth-caves/README.md). Every cell id below was checked against MTG's hoth.ws: it exists, it is a
-- cell of the named cave, and the cave sits where Bellum's comment says.
-- Changed: {skipped} spawns in Bellum's fifth cave (cave_06_flatland_s01_ice, building 6453174, cells
-- 6453175-6453185: the mynock den) are left out because that building is not in MTG's snapshot; the per-player
-- boss reward (WorldBossLootManager, giveHothBossRewards, HOTH_CAVE_BOSS_LOOT) and the two boss observers are
-- dropped, so the five named wampa bosses keep the corpse loot of their mobile templates; written in the style
-- of the other caves/ screenplays. Respawn times are Bellum's (420 s, bosses 1800 s).
"""


def main():
    report = ws_read.verify('client:snapshot/hoth.ws', BELLUM)
    kept = [r for r in report['rows'] if r['keep']]
    skipped = [r for r in report['rows'] if not r['keep']]
    lines = [HEADER.replace('{skipped}', str(len(skipped))),
             'HothIceCavesScreenPlay = ScreenPlay:new {', '\tnumberOfActs = 1,', '',
             '\tscreenplayName = "HothIceCavesScreenPlay"', '}', '',
             'registerScreenPlay("HothIceCavesScreenPlay", true)', '',
             'function HothIceCavesScreenPlay:start()', '\tif (isZoneEnabled("hoth")) then', '\t\tself:spawnMobiles()',
             '\tend', 'end', '', 'function HothIceCavesScreenPlay:spawnMobiles()']
    current_cave, current_cell = None, None
    for r in kept:
        if r['cave_comment'] != current_cave:
            current_cave = r['cave_comment']
            c = report['caves'][str(current_cave)]
            lines.append(f'\t-- {c["name"]} at {c["snapshot_x"]:.1f}, {c["snapshot_y"]:.1f} (height {c["snapshot_z"]:.1f}; building {current_cave})')
            current_cell = None
        if r['cell'] != current_cell:
            current_cell = r['cell']
            lines.append(f'\t--Cell[{current_cell}]')
        lines.append(f'\tspawnMobile("hoth", "{r["template"]}", {r["respawn"]}, {r["x"]:g}, {r["z"]:g}, {r["y"]:g}, {r["heading"]:g}, {r["cell"]})')
    lines += ['end', '']
    os.makedirs(os.path.join(STAGED, 'caves'), exist_ok=True)
    cave_path = os.path.join(STAGED, 'caves', 'hoth_ice_caves.lua')
    with open(cave_path, 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(lines))

    orig = open(ORIG, 'rb').read()
    assert orig.count(INCLUDE_AFTER.encode()) == 1 and b'hoth_ice_caves' not in orig
    patched = orig.replace(INCLUDE_AFTER.encode(), (INCLUDE_AFTER + INCLUDE_LINE).encode())
    with open(os.path.join(STAGED, 'screenplays.lua'), 'wb') as f:
        f.write(patched)

    templates_used = sorted({r['template'] for r in kept})
    checks = {
        'bellum_source': os.path.relpath(BELLUM, H).replace('\\', '/'),
        'snapshot': 'snapshot/hoth.ws from mtg_planets.tre (owner\'s client), read with our ws_read.py',
        'snapshot_nodes': report['nodes'], 'snapshot_world_level': report['world_level'],
        'bellum_rows': report['bellum_rows'], 'kept': len(kept), 'skipped': len(skipped),
        'per_cave': {str(k): dict(v, **{kk: vv for kk, vv in report['caves'].get(str(k), {}).items() if kk in ('name', 'building_in_snapshot', 'position_matches', 'template')})
                     for k, v in report['per_cave'].items()},
        'caves': report['caves'],
        'cell_ids_in_bellum': len({r['cell'] for r in report['rows']}),
        'cell_ids_missing_in_mtg': report['missing_cells'],
        'skipped_rows': [{k: r[k] for k in ('template', 'respawn', 'x', 'z', 'y', 'heading', 'cell', 'reason')} for r in skipped],
        'templates_used': templates_used,
        'templates_registered_in_core3_dev': {t: t in REGISTERED for t in sorted({r['template'] for r in report['rows']})},
        'floor_check': 'skipped: needs PortalLayout/CellProperty/FloorMesh readers (Core3-dev src/templates/appearance); see README',
        'screenplays_lua_orig_sha256': hashlib.sha256(orig).hexdigest(),
        'screenplays_lua_staged_sha256': hashlib.sha256(patched).hexdigest(),
        'screenplays_lua_line_endings': 'LF' if b'\r\n' not in orig else 'CRLF',
        'include_line_inserted_after': INCLUDE_AFTER.strip(),
        'cave_file_sha256': hashlib.sha256(open(cave_path, 'rb').read()).hexdigest(),
        'luac': 'see luac.txt (run after staging)',
    }
    with open(os.path.join(ROOT, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(f'kept {len(kept)}, skipped {len(skipped)}, per cave {report["per_cave"]}; templates {templates_used}')
    print('missing cells:', report['missing_cells'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
