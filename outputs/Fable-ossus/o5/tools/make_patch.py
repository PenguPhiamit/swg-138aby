"""O5 server patch: Ossus zone for the first look (no creatures), from the verbatim dev copies in work/orig."""
import os
import subprocess

R = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o5'
S = 'MMOCoreORB/bin/scripts'
O, N = R + '/work/orig', R + '/work/new'
LF = chr(10)


def rd(rel):
    with open(O + '/' + rel, encoding='utf-8', newline='') as f:
        return f.read()


def wr(rel, text):
    os.makedirs(os.path.dirname(N + '/' + rel), exist_ok=True)
    with open(N + '/' + rel, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def edit(rel, old, new):
    s = rd(rel)
    assert s.count(old) == 1, (rel, old[:60])
    wr(rel, s.replace(old, new))


PLANET_BLOCK = LF.join([
    'ossus = {',
    '\t-- Sandbox: Ossus first look (Fable O5, 14 Oct 2026; outputs/Fable-ossus/o5/README.md). Our own terrain',
    '\t-- (terrain/ossus.trn) and snapshot (snapshot/ossus.ws) in local_planets.tre; the Knossa starport sits on the',
    '\t-- flattened pad at 0 -3600 (50.3 m). Reached from Corellia (datatables/travel/travel.iff; placeholder fares, Q10).',
    '\tweatherEnabled = 1,',
    '\tgcwEnabled = 1,',
    '',
    '\tplanetTravelPoints = {',
    '\t\t-- the outpost_starport landing pad: the same offset from the building as Hoth and Yavin IV (yaw 180); the',
    '\t\t-- building\'s own child objects give the travel terminal, the ticket collector and the shuttle, as on Hoth',
    '\t\t{name = "Knossa", x = 20.3, z = 50.3, y = -3582.2, interplanetaryTravelAllowed = 1, incomingTravelAllowed = 1, landingRange = 3},',
    '\t},',
    '',
    '\tbadgeAreas = {',
    '\t},',
    '',
    '\tnavAreas = {',
    '\t\t{"ossus_knossa", 0, -3600, 150},',
    '\t},',
    '',
    '\tplanetObjects = {',
    '\t}',
    '}',
    '',
    'tutorial = {'])
edit(S + '/managers/planet/planet_manager.lua', 'tutorial = {', PLANET_BLOCK)
edit(S + '/managers/resource_manager.lua',
     'activeZones = "corellia,tatooine,lok,naboo,rori,endor,talus,yavin4,dathomir,dantooine,hoth"' + LF,
     '-- Sandbox Ossus (14 Oct 2026, Fable O5): ossus added; its 45 native types are in the merged resource_tree.iff of the' + LF +
     '-- test-session local_planets.tre (stage_ossus, O4). Give it backfillZones = "hoth,ossus" for its first start (test_galaxy.py).' + LF +
     'activeZones = "corellia,tatooine,lok,naboo,rori,endor,talus,yavin4,dathomir,dantooine,hoth,ossus"' + LF)
wr(S + '/managers/planet/ossus_regions.lua', LF.join([
    'require("scripts.managers.planet.regions")',
    '',
    '-- Sandbox: Ossus first look (Fable O5, 14 Oct 2026; outputs/Fable-ossus/o5/README.md): the edges, the Knossa landing',
    '-- field as a city (its name is string/en/ossus_region_names.stf in local_planets.tre), no-build circles at the ruins',
    '-- and the three caves. No spawn areas and no world spawner yet: O2b\'s fauna, lairs and spawn groups follow once the',
    '-- owner has seen the planet (outputs/Fable-ossus/o2/staged/.../ossus_regions.lua holds the full file).',
    'ossus_regions = {',
    '\t-- No Build Zones',
    '\t{"northedge_ossus_nobuild", -8000, 7640, {RECTANGLE, 8000, 8000}, NOSPAWNAREA + NOBUILDZONEAREA},',
    '\t{"westedge_ossus_nobuild", -8000, -7640, {RECTANGLE, -7640, 7640}, NOSPAWNAREA + NOBUILDZONEAREA},',
    '\t{"southedge_ossus_nobuild", -8000, -8000, {RECTANGLE, 8000, -7640}, NOSPAWNAREA + NOBUILDZONEAREA},',
    '\t{"eastedge_ossus_nobuild", 7640, -7640, {RECTANGLE, 7999, 7640}, NOSPAWNAREA + NOBUILDZONEAREA},',
    '',
    '\t-- The landing field',
    '\t{"@ossus_region_names:knossa", 0, -3600, {CIRCLE, 200}, CITY + NOSPAWNAREA},',
    '\t{"ossus_knossa_nobuild", 0, -3600, {CIRCLE, 320}, NOBUILDZONEAREA},',
    '',
    '\t-- The academy ruins and the three cave mouths',
    '\t{"ossus_academy_ruins_nobuild", 2016, 2848, {CIRCLE, 260}, NOSPAWNAREA + NOBUILDZONEAREA},',
    '\t{"ossus_cave_foothills_west_nobuild", -2976, -4960, {CIRCLE, 120}, NOBUILDZONEAREA},',
    '\t{"ossus_cave_foothills_east_nobuild", 4896, -4960, {CIRCLE, 120}, NOBUILDZONEAREA},',
    '\t{"ossus_cave_north_nobuild", 1376, 5920, {CIRCLE, 120}, NOBUILDZONEAREA},',
    '}',
    '']))

os.makedirs(R + '/patch', exist_ok=True)
out = b''
for rel in (S + '/managers/planet/planet_manager.lua', S + '/managers/resource_manager.lua'):
    p = subprocess.run(['diff', '-u', '--label', 'a/' + rel, '--label', 'b/' + rel, O + '/' + rel, N + '/' + rel], capture_output=True)
    out += p.stdout
rel = S + '/managers/planet/ossus_regions.lua'
body = open(N + '/' + rel, encoding='utf-8', newline='').read().split(LF)
if body and body[-1] == '':
    body.pop()
out += ('--- /dev/null' + LF + '+++ b/' + rel + LF + '@@ -0,0 +1,%d @@' % len(body) + LF + ''.join('+' + l + LF for l in body)).encode('utf-8')
with open(R + '/patch/ossus-first-look.patch', 'wb') as f:
    f.write(out)
print('patch lines', len(out.splitlines()))
