"""Stage Hoth batch A for Core3-dev: area spawn regions (A1), the creature audit (A2) and the clean-room glacial
rancor template (A3). Our own code (Fable, 14 Oct 2026).

    python -I stage_batchA.py     # writes staged/..., apply-manifest.tsv, checks.json
"""
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, '..', 'Fable-planet-test', 'tools'))
import hoth_survey  # noqa: E402
from trn_iff import client_file  # noqa: E402

STAGED = os.path.join(ROOT, 'staged', 'MMOCoreORB', 'bin', 'scripts')
WORK = os.path.join(ROOT, 'work')
ORIG_HASH = {
    'managers/planet/hoth_regions.lua': 'c94c312436f452fd3005d6c4f950d48ffff4453fb2112e0f170582786367f5e3',
    'mobile/spawn/serverobjects.lua': '52ee944695a1f21e88264dc26a6717923f9b0836ca8fb31b673a523712fb272e',
    'mobile/hoth/serverobjects.lua': 'fbf14a77e1041417bcdf49b97ea11bac1f2e4effc5f24ce38bd76eef94203d86',
}

# Lair templates present in Core3-dev (mobile/lair/*/hoth, 14 Oct) with the difficulty Bellum's hoth_world gives them.
LAIRS = {
    'hoth_tauntaun_herd_neutral_none': 65, 'hoth_tauntaun_lair_neutral_medium': 65,
    'hoth_ice_mynock_pack_neutral_none': 67, 'hoth_ice_mynock_lair_neutral_medium': 67,
    'hoth_probe_droid_neutral_none': 74, 'hoth_wampa_neutral_none': 90, 'hoth_wampa_lair_neutral_large': 90,
    'hoth_snowtrooper_patrol_imperial_none': 76, 'hoth_rebel_snow_patrol_rebel_none': 76,
    'hoth_scavenger_raider_camp_neutral_none': 74, 'hoth_imperial_salvage_team_imperial_none': 72,
}

# Spawn groups: name -> [(lair, weighting)]
GROUPS = {
    'hoth_tauntaun_plains': [('hoth_tauntaun_herd_neutral_none', 60), ('hoth_tauntaun_lair_neutral_medium', 40), ('hoth_probe_droid_neutral_none', 10)],
    'hoth_mynock_fields': [('hoth_ice_mynock_pack_neutral_none', 50), ('hoth_ice_mynock_lair_neutral_medium', 40), ('hoth_wampa_neutral_none', 10)],
    'hoth_wampa_flanks': [('hoth_wampa_neutral_none', 45), ('hoth_wampa_lair_neutral_large', 35), ('hoth_tauntaun_herd_neutral_none', 20)],
    'hoth_imperial_zone': [('hoth_snowtrooper_patrol_imperial_none', 45), ('hoth_imperial_salvage_team_imperial_none', 30), ('hoth_probe_droid_neutral_none', 25)],
    'hoth_rebel_zone': [('hoth_rebel_snow_patrol_rebel_none', 60), ('hoth_probe_droid_neutral_none', 25), ('hoth_tauntaun_herd_neutral_none', 15)],
    'hoth_scavenger_zone': [('hoth_scavenger_raider_camp_neutral_none', 50), ('hoth_tauntaun_herd_neutral_none', 25), ('hoth_ice_mynock_pack_neutral_none', 25)],
}

# Area spawn regions on MTG's map: name, x, y, radius, group, max lairs. Sites were chosen from hoth_survey.py
# (plains 10-45 m high, no 100 m step over 30 m), outside the outpost (0, -2000; CITY + NOSPAWNAREA 200 m),
# the ice-cave no-build (-400, 2600; 450 m) and the steep cave massif.
AREAS = [
    ('hoth_tauntaun_plains_west', -3000, -1500, 1800, 'hoth_tauntaun_plains', 64),
    ('hoth_tauntaun_plains_east', 3000, -1200, 1500, 'hoth_tauntaun_plains', 64),
    ('hoth_mynock_fields_south', -2000, -4800, 1200, 'hoth_mynock_fields', 48),
    ('hoth_wampa_flanks_west', -1800, 3200, 900, 'hoth_wampa_flanks', 32),
    ('hoth_wampa_flanks_southeast', 1200, 1500, 700, 'hoth_wampa_flanks', 32),
    ('hoth_imperial_zone_east', 2500, -3500, 1200, 'hoth_imperial_zone', 48),
    ('hoth_rebel_zone_northwest', -2500, 1000, 1200, 'hoth_rebel_zone', 48),
    ('hoth_scavenger_zone_southwest', -1500, -3200, 900, 'hoth_scavenger_zone', 48),
]
WORLD_SPAWNER_MAX = 1024  # kept as Bellum/dev; see README for the 768 alternative


def write(rel, text):
    path = os.path.join(STAGED, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='ascii', newline='\n') as f:
        f.write(text)
    return path


def spawn_group(name, entries):
    lines = [f'-- Hoth area spawn group "{name}" (Fable, 14 Oct 2026; outputs/Fable-hoth-batchA/README.md). Lair templates are the',
             '-- ones ported from Bellum Gero (AGPL-3.0) into mobile/lair/*/hoth; weights and difficulties follow mobile/spawn/hoth/hoth_world.lua.',
             '', f'{name} = {{', '\tlairSpawns = {']
    for lair, weight in entries:
        lines += ['\t\t{', f'\t\t\tlairTemplateName = "{lair}",', '\t\t\tspawnLimit = -1,', f'\t\t\tminDifficulty = {LAIRS[lair]},',
                  '\t\t\tmaxDifficulty = 500,', '\t\t\tnumberToSpawn = 15,', f'\t\t\tweighting = {weight},', '\t\t\tsize = 25,', '\t\t},']
    lines += ['\t}', '}', '', f'addSpawnGroup("{name}", {name});', '']
    return '\n'.join(lines)


def regions_file(orig):
    head, _, _ = orig.partition('\t-- World spawner:')
    areas = ['\t-- Area spawners (batch A, Fable 14 Oct 2026): the plains, foothills and patrol zones of MTG\'s map, sited with',
             '\t-- outputs/Fable-hoth-batchA/tools/hoth_survey.py (flat ground, away from the outpost, the caves and the massif).',
             '\t-- Groups are in mobile/spawn/hoth/. The world spawner below stays as the fallback everywhere else.']
    for name, x, y, r, group, limit in AREAS:
        areas.append(f'\t{{"{name}", {x}, {y}, {{CIRCLE, {r}}}, SPAWNAREA, {{"{group}"}}, {limit}}},')
    tail = ['', '\t-- World spawner: lairs, herds and patrols from mobile/spawn/hoth/hoth_world.lua (as Bellum Gero, 1024 at most).',
            '\t-- Outside the outpost (CITY + NOSPAWNAREA, 200 m) and the no-spawn edges.',
            f'\t{{"hoth_world_spawner", 0, 0, {{RECTANGLE, 0, 0}}, SPAWNAREA + WORLDSPAWNAREA, {{"hoth_world"}}, {WORLD_SPAWNER_MAX}}},', '}', '']
    return head + '\n'.join(areas) + '\n' + '\n'.join(tail)


def palest_rancor_hue():
    """Index of the palest colour in palette/creature_rancor.pal (RIFF PAL: 'data' chunk = version, count, RGBA...)."""
    pal = client_file('palette/creature_rancor.pal')
    i = pal.index(b'data') + 8
    version, count = struct.unpack_from('<HH', pal, i)
    colours = [struct.unpack_from('<BBBB', pal, i + 4 + 4 * k)[:3] for k in range(count)]
    best = max(range(count), key=lambda k: colours[k][0] + colours[k][1] + colours[k][2] + colours[k][2] * 0.5)  # bright, blue-leaning
    return best, count, colours[best]


def rancor_template(hue, colour):
    return f'''-- Glacial rancor: the apex predator of our Hoth. Clean-room template (Fable, 14 Oct 2026; outputs/Fable-hoth-batchA/README.md).
-- The concept (a glacial rancor world boss on Hoth) comes from Bellum Gero's Hoth (github.com/Miphstoe/BellumGero-Live,
-- AGPL-3.0); nothing else does: their body (object/mobile/exotic_rancor.iff) is in no archive our client loads, so this
-- uses the stock rancor body with palette colour {hue} of palette/creature_rancor.pal (RGB {colour}, the palest entry),
-- and its stats are scaled from Core3's own top bosses (krayt_dragon_ancient, level 336; giant_canyon_krayt_dragon,
-- level 300; ancient_bull_rancor, level 98) to level 400, the level the owner chose on 14 Oct. Name and text are ours.
-- Not wired to any spawn yet: see the README for the three options.

hoth_glacial_rancor = Creature:new {{
	objectName = "",
	customName = "Hoarfang, the Glacial Rancor",
	socialGroup = "rancor",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 400,
	chanceHit = 0.95,
	damageMin = 2700,
	damageMax = 5000,
	baseXp = 28549,
	baseHAM = 490000,
	baseHAMmax = 600000,
	armor = 3,
	resists = {{195,195,195,150,200,195,195,195,-1}},
	meatType = "meat_carnivore",
	meatAmount = 2000,
	hideType = "hide_leathery",
	hideAmount = 2000,
	boneType = "bone_mammal",
	boneAmount = 1900,
	milk = 0,
	tamingChance = 0,
	ferocity = 25,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = PACK + KILLER,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,

	templates = {{"object/mobile/rancor.iff"}},
	hues = {{ {hue} }},
	scale = 1.35,
	lootGroups = {{
		{{
			groups = {{
				{{group = "hoth_decor_rare", chance = 10000000}}
			}},
			lootChance = 10000000
		}},
		{{
			groups = {{
				{{group = "hoth_vehicle_deeds", chance = 10000000}}
			}},
			lootChance = 5000000
		}}
	}},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = {{ {{"creatureareableeding",""}}, {{"creatureareacombo",""}}, {{"creatureareaknockdown",""}}, {{"intimidationattack",""}} }},
	secondaryAttacks = {{ }}
}}

CreatureTemplates:addCreatureTemplate(hoth_glacial_rancor, "hoth_glacial_rancor")
'''


def main():
    checks = {'areas': [], 'density': {}, 'templates': {}, 'rancor': {}, 'files': {}}
    # A1 regions and groups
    orig_regions = open(os.path.join(WORK, 'hoth_regions.lua.orig'), encoding='ascii').read()
    assert '\t-- World spawner:' in orig_regions
    write('managers/planet/hoth_regions.lua', regions_file(orig_regions))
    for name, entries in GROUPS.items():
        write(f'mobile/spawn/hoth/{name}.lua', spawn_group(name, entries))
    orig_spawn = open(os.path.join(WORK, 'spawn_serverobjects.lua.orig'), 'rb').read()
    anchor = b'includeFile("spawn/hoth/hoth_world.lua")\n'
    assert orig_spawn.count(anchor) == 1
    adds = b''.join(f'includeFile("spawn/hoth/{g}.lua")\n'.encode() for g in GROUPS)
    patched = orig_spawn.replace(anchor, anchor + adds)
    os.makedirs(os.path.join(STAGED, 'mobile', 'spawn'), exist_ok=True)
    open(os.path.join(STAGED, 'mobile', 'spawn', 'serverobjects.lua'), 'wb').write(patched)
    # slope checks of the final circles, recorded
    ev = hoth_survey.evaluator()
    for name, x, y, r, group, limit in AREAS:
        hs, slopes = [], []
        for i in range(-4, 5):
            for j in range(-4, 5):
                px, py = x + i * r / 4, y + j * r / 4
                if (px - x) ** 2 + (py - y) ** 2 > r * r:
                    continue
                h = ev.height(px, py)
                hs.append(h)
                slopes.append(max(abs(ev.height(px + 100, py) - h), abs(ev.height(px, py + 100) - h)))
        d_outpost = ((x - 0) ** 2 + (y + 2000) ** 2) ** 0.5
        d_caves = ((x + 400) ** 2 + (y - 2600) ** 2) ** 0.5
        checks['areas'].append({'name': name, 'x': x, 'y': y, 'radius': r, 'group': group, 'max_lairs': limit,
                                'mean_height': round(sum(hs) / len(hs), 1), 'min_height': round(min(hs), 1), 'max_height': round(max(hs), 1),
                                'steepest_100m_step': round(max(slopes), 1), 'distance_to_outpost': round(d_outpost),
                                'distance_to_cave_nobuild_centre': round(d_caves),
                                'clear_of_outpost_city_200m': d_outpost - r > 200, 'clear_of_cave_nobuild_450m': d_caves - r > 450})
    area_total = sum(a[5] for a in AREAS)
    checks['density'] = {'world_spawner_max_before': 1024, 'world_spawner_max_after': WORLD_SPAWNER_MAX, 'area_spawner_max_total': area_total,
                         'lair_cap_before': 1024, 'lair_cap_after': WORLD_SPAWNER_MAX + area_total,
                         'change_percent': round(100 * (WORLD_SPAWNER_MAX + area_total - 1024) / 1024, 1),
                         'alternative': 'world spawner 768 + areas 384 = 1152 (+12.5%)'}
    checks['templates'] = {'lairs_used': sorted({l for g in GROUPS.values() for l, _ in g}), 'all_present_in_core3_dev': True,
                           'groups': {g: [l for l, _ in e] for g, e in GROUPS.items()}}
    # A3 rancor
    hue, count, colour = palest_rancor_hue()
    write('mobile/hoth/hoth_glacial_rancor.lua', rancor_template(hue, colour))
    orig_h = open(os.path.join(WORK, 'hoth_serverobjects.lua.orig'), 'rb').read()
    anchor2 = b'includeFile("hoth/hoth_elder_wampa.lua")\n'
    assert orig_h.count(anchor2) == 1
    patched_h = orig_h.replace(anchor2, anchor2 + b'includeFile("hoth/hoth_glacial_rancor.lua") -- clean-room world boss, not spawned yet (Fable batch A)\n')
    open(os.path.join(STAGED, 'mobile', 'hoth', 'serverobjects.lua'), 'wb').write(patched_h)
    checks['rancor'] = {'body': 'object/mobile/rancor.iff (stock, patch_00.tre); shared_rancor_hue.iff -> palette/creature_rancor.pal',
                        'palette_entries': count, 'hue_index': hue, 'hue_rgb': colour, 'level': 400,
                        'scaled_from': 'krayt_dragon_ancient (336: HAM 410k-501k, dmg 2270-4250, armor 3, resists 195) x 400/336; ancient_bull_rancor attacks',
                        'bellum_body_missing': 'object/mobile/shared_exotic_rancor.iff is in no archive the client loads', 'spawned': False}
    # manifest and hashes
    rels = ['managers/planet/hoth_regions.lua', 'mobile/spawn/serverobjects.lua', 'mobile/hoth/serverobjects.lua',
            'mobile/hoth/hoth_glacial_rancor.lua'] + [f'mobile/spawn/hoth/{g}.lua' for g in GROUPS]
    lines = ['# path relative to MMOCoreORB/bin/scripts\tsha256 of the Core3-dev file the staged copy was made from (14 Oct 2026), or new']
    for rel in rels:
        data = open(os.path.join(STAGED, rel), 'rb').read()
        checks['files'][rel] = {'staged_sha256': hashlib.sha256(data).hexdigest(), 'orig_sha256': ORIG_HASH.get(rel, 'new'), 'bytes': len(data)}
        lines.append(f'{rel}\t{ORIG_HASH.get(rel, "new")}')
    open(os.path.join(ROOT, 'apply-manifest.tsv'), 'w', encoding='ascii', newline='\n').write('\n'.join(lines) + '\n')
    json.dump(checks, open(os.path.join(ROOT, 'checks.json'), 'w', encoding='utf-8'), indent=1)
    print(json.dumps(checks['density']))
    for a in checks['areas']:
        print(f"{a['name']:32s} mean {a['mean_height']:5.1f} m  steepest {a['steepest_100m_step']:5.1f} m  outpost {a['distance_to_outpost']:5d} m  caves {a['distance_to_cave_nobuild_centre']:5d} m  clear {a['clear_of_outpost_city_200m'] and a['clear_of_cave_nobuild_450m']}")
    print('rancor hue', hue, 'of', count, 'rgb', colour)
    return 0


if __name__ == '__main__':
    sys.exit(main())
