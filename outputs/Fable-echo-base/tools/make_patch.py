"""E0 server patch: work/new/ from the verbatim dev copies in work/orig/ plus four new files; patch/echo-base-e0.patch."""
import os
import subprocess

R = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-echo-base'
S = 'MMOCoreORB/bin/scripts'
O, N = R + '/work/orig', R + '/work/new'
ORIGIN = (-5112.8, 37.6, 5096.6)       # x, height, y from tools/fit_echo_base.py (out/fit.json)
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


edit(S + '/screenplays/screenplays.lua',
     'includeFile("poi/hoth_outpost_terminals.lua") -- Sandbox: Hoth mission terminals (Fable batch C)' + LF,
     'includeFile("poi/hoth_outpost_terminals.lua") -- Sandbox: Hoth mission terminals (Fable batch C)' + LF +
     'includeFile("poi/hoth_echo_base.lua") -- Sandbox: Hoth Echo Base, first look (Fable E0)' + LF)
edit(S + '/managers/planet/hoth_regions.lua',
     '\t-- World spawner: lairs, herds and patrols from mobile/spawn/hoth/hoth_world.lua (as Bellum Gero, 1024 at most).' + LF,
     '\t-- Echo Base (Fable E0, 14 Oct 2026): the NGE building at MTG\'s terrain cut-outs; no building and no world spawns over it.' + LF +
     '\t{"hoth_echo_base_nobuild", -5113, 5097, {CIRCLE, 750}, NOBUILDZONEAREA + NOSPAWNAREA},' + LF +
     '\t-- World spawner: lairs, herds and patrols from mobile/spawn/hoth/hoth_world.lua (as Bellum Gero, 1024 at most).' + LF)
edit(S + '/object/allobjects.lua',
     'includeFile("building/general/objects.lua")' + LF,
     'includeFile("building/general/objects.lua")' + LF +
     'includeFile("building/heroic/objects.lua") -- Sandbox: Hoth Echo Base (Fable E0): the MTG-shipped NGE building' + LF)
edit(S + '/object/building/serverobjects.lua',
     'includeFile("building/general/serverobjects.lua")' + LF,
     'includeFile("building/general/serverobjects.lua")' + LF +
     'includeFile("building/heroic/serverobjects.lua") -- Sandbox: Hoth Echo Base (Fable E0)' + LF)

wr(S + '/object/building/heroic/objects.lua', LF.join([
    '-- Sandbox: Hoth Echo Base (Fable E0, 14 Oct 2026; outputs/Fable-echo-base/README.md). The shared template is the NGE',
    '-- heroic building MTG ships (mtg_patch_019.tre); the server reads its portal layout (appearance/echo_base_pob.pob,',
    '-- mtg_patch_016.tre, 41 cells) and the rest from the client file through clientTemplateFileName, as the other',
    '-- building templates do.',
    'object_building_heroic_shared_echo_base = SharedBuildingObjectTemplate:new {',
    '\tclientTemplateFileName = "object/building/heroic/shared_echo_base.iff"',
    '}',
    '',
    'ObjectTemplates:addClientTemplate(object_building_heroic_shared_echo_base, "object/building/heroic/shared_echo_base.iff")',
    '']))
wr(S + '/object/building/heroic/echo_base.lua', LF.join([
    '-- Sandbox: Hoth Echo Base (Fable E0). Server template for the building the screenplay poi/hoth_echo_base.lua places.',
    'object_building_heroic_echo_base = object_building_heroic_shared_echo_base:new {',
    '',
    '}',
    '',
    'ObjectTemplates:addTemplate(object_building_heroic_echo_base, "object/building/heroic/echo_base.iff")',
    '']))
wr(S + '/object/building/heroic/serverobjects.lua', LF.join([
    '-- Sandbox: Hoth Echo Base (Fable E0)',
    'includeFile("building/heroic/echo_base.lua")',
    '']))
wr(S + '/screenplays/poi/hoth_echo_base.lua', LF.join([
    '-- Hoth: Echo Base, first look (Fable E0, 14 Oct 2026; outputs/Fable-echo-base/README.md).',
    "-- The NGE heroic building (object/building/heroic/shared_echo_base.iff, from the MTG archives) placed where MTG's",
    '-- hoth.trn cut the terrain for it: its hangar, main-door and tower openings fit MTG\'s three cut-outs within 2.3 m RMS',
    '-- at origin %.1f, %.1f, heading 0, height %.1f m (the three doors agree within 2.1 m). One building, no NPCs: the' % (ORIGIN[0], ORIGIN[2], ORIGIN[1]),
    '-- go / no-go look for E1 (outputs/Fable-hoth-guide/echo-base-plan.md). Owner: /teleport -5051 5440 hoth (main door),',
    '-- /teleport -5307 5750 hoth (hangar), /teleport -5036 5120 hoth (tower).',
    'HothEchoBaseScreenPlay = ScreenPlay:new {',
    '\tnumberOfActs = 1,',
    '\tscreenplayName = "HothEchoBaseScreenPlay",',
    '}',
    '',
    'registerScreenPlay("HothEchoBaseScreenPlay", true)',
    '',
    'function HothEchoBaseScreenPlay:start()',
    '\tif (isZoneEnabled("hoth")) then',
    '\t\tself:spawnSceneObjects()',
    '\tend',
    'end',
    '',
    'function HothEchoBaseScreenPlay:spawnSceneObjects()',
    '\tspawnSceneObject("hoth", "object/building/heroic/echo_base.iff", %.1f, %.1f, %.1f, 0, 0)' % (ORIGIN[0], ORIGIN[1], ORIGIN[2]),
    'end',
    '']))

os.makedirs(R + '/patch', exist_ok=True)
files = [S + '/screenplays/screenplays.lua', S + '/managers/planet/hoth_regions.lua', S + '/object/allobjects.lua', S + '/object/building/serverobjects.lua']
new_files = [S + '/object/building/heroic/objects.lua', S + '/object/building/heroic/echo_base.lua', S + '/object/building/heroic/serverobjects.lua', S + '/screenplays/poi/hoth_echo_base.lua']
out = b''
for rel in files:
    p = subprocess.run(['diff', '-u', '--label', 'a/' + rel, '--label', 'b/' + rel, O + '/' + rel, N + '/' + rel], capture_output=True)
    out += p.stdout
for rel in new_files:                                   # new-file hunks written by hand (diff against nul fails on Windows)
    body = open(N + '/' + rel, encoding='utf-8', newline='').read().split(LF)
    if body and body[-1] == '':
        body.pop()
    hunk = '--- /dev/null' + LF + '+++ b/' + rel + LF + '@@ -0,0 +1,%d @@' % len(body) + LF + ''.join('+' + l + LF for l in body)
    out += hunk.encode('utf-8')
with open(R + '/patch/echo-base-e0.patch', 'wb') as f:
    f.write(out)
print('patch lines', len(out.splitlines()), 'files', len(files) + len(new_files))
