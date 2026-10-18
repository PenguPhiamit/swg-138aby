"""S6 server patch: Nautolan (male) and Togruta (female) on top of dev HEAD 08e6a924 (Chiss already in). Every edit is an
exact-anchor replacement on verbatim dev copies (work/orig, read through wsl cat) -> work/new; the diff plus the two new
race templates become patch/species-s6.patch; work/gitcheck.sh proves it with git apply --check and luac in a WSL
scratch repository. Our own code (Fable, 14 Oct 2026). Read-only on /opt/swg.
    python -I make_patch.py
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
S6 = os.path.normpath(os.path.join(HERE, '..'))
ORIG, NEW = os.path.join(S6, 'work', 'orig'), os.path.join(S6, 'work', 'new')
sys.path.insert(0, os.path.join(S6, '..', '..', 'tools'))
from swgfmt.swg_tables import soe_crc  # noqa: E402

LF = chr(10)
# species, gender, id (next free after CHISS 0xE7; the stock NPC species table ends at 230), baseHAM (= the package's racial_mods row, the Zabrak profile)
NEW_RACES = [('nautolan', 'male', '0xE8', '{ 200, 0, 0, 300, 0, 0, 0, 0, 400 }'),
             ('togruta', 'female', '0xE9', '{ 200, 0, 0, 300, 0, 0, 0, 0, 400 }')]
FILES = {
    'races': 'MMOCoreORB/src/server/zone/objects/player/Races.h',
    'idl': 'MMOCoreORB/src/server/zone/objects/creature/CreatureObject.idl',
    'director': 'MMOCoreORB/src/server/zone/managers/director/DirectorManager.cpp',
    'pcm_lua': 'MMOCoreORB/bin/scripts/managers/player_creation_manager.lua',
    'objects': 'MMOCoreORB/bin/scripts/object/creature/player/objects.lua',
    'serverobjects': 'MMOCoreORB/bin/scripts/object/creature/player/serverobjects.lua',
}
TEMPLATE_DIR = 'MMOCoreORB/bin/scripts/object/creature/player'


def load(rel):
    with open(os.path.join(ORIG, rel), encoding='utf-8', newline='') as f:
        return f.read()


def save(rel, text):
    path = os.path.join(NEW, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def replace_once(text, old, new, label):
    n = text.count(old)
    assert n == 1, '%s: anchor found %d times: %r' % (label, n, old[:90])
    return text.replace(old, new)


def main():
    shutil.rmtree(NEW, ignore_errors=True)
    for s, g, i, _ in NEW_RACES:
        for rel in FILES.values():
            assert s not in load(rel).lower(), '%s already names %s' % (rel, s)

    # 1. Races.h: one entry per new race at the end of all six arrays (same order everywhere), after the Chiss female entry
    t = load(FILES['races'])
    t = replace_once(t, '    "chiss"  // chiss female\n};', '    "chiss", // chiss female\n' + ''.join('    "%s"%s // %s %s (Fable species S6)\n' % (s, ',' if k < len(NEW_RACES) - 1 else ' ', s, g) for k, (s, g, _, _) in enumerate(NEW_RACES)) + '};', 'Species')
    t = replace_once(t, '\t\t0xE7  // chiss female\n};', '\t\t0xE7, // chiss female\n' + ''.join('\t\t%s%s // %s %s: CreatureObject::%s\n' % (i, ',' if k < len(NEW_RACES) - 1 else ' ', s, g, s.upper()) for k, (s, g, i, _) in enumerate(NEW_RACES)) + '};', 'TemplateSpecies')
    t = replace_once(t, '    "female"  // chiss female\n};', '    "female", // chiss female\n' + ''.join('    "%s"%s // %s %s\n' % (g, ',' if k < len(NEW_RACES) - 1 else ' ', s, g) for k, (s, g, _, _) in enumerate(NEW_RACES)) + '};', 'Gender')
    t = replace_once(t, '    "object/creature/player/shared_chiss_female.iff"  // chiss female\n};', '    "object/creature/player/shared_chiss_female.iff", // chiss female\n'
                     + ''.join('    "object/creature/player/shared_%s_%s.iff"%s // %s %s\n' % (s, g, ',' if k < len(NEW_RACES) - 1 else ' ', s, g) for k, (s, g, _, _) in enumerate(NEW_RACES)) + '};', 'RaceStrs')
    t = replace_once(t, '    "object/creature/player/chiss_female.iff"  // chiss female\n};', '    "object/creature/player/chiss_female.iff", // chiss female\n'
                     + ''.join('    "object/creature/player/%s_%s.iff"%s // %s %s\n' % (s, g, ',' if k < len(NEW_RACES) - 1 else ' ', s, g) for k, (s, g, _, _) in enumerate(NEW_RACES)) + '};', 'CCRaceStrs')
    crcs = [(s, g, soe_crc('object/creature/player/shared_%s_%s.iff' % (s, g))) for s, g, _, _ in NEW_RACES]
    t = replace_once(t, '    0x614A1B68  // chiss female\n};', '    0x614A1B68, // chiss female\n'
                     + ''.join('    0x%08X%s // %s %s: SOE CRC of object/creature/player/shared_%s_%s.iff\n' % (c, ',' if k < len(crcs) - 1 else ' ', s, g, s, g) for k, (s, g, c) in enumerate(crcs)) + '};', 'SharedRace')
    save(FILES['races'], t)

    # 2. CreatureObject.idl: the two species constants and their names
    t = load(FILES['idl'])
    anchor = '\tpublic static final int CHISS = 0xE7;'
    k = t.index(anchor)
    line_end = t.index('\n', k) + 1
    t = t[:line_end] + ''.join('\tpublic static final int %s = %s; // Fable species S6\n' % (s.upper(), i) for s, _, i, _ in NEW_RACES) + t[line_end:]
    t = replace_once(t, '\t\telse if(species == CHISS)\n\t\t\treturn "chiss";\n', '\t\telse if(species == CHISS)\n\t\t\treturn "chiss";\n'
                     + ''.join('\t\telse if(species == %s)\n\t\t\treturn "%s";\n' % (s.upper(), s) for s, _, _, _ in NEW_RACES), 'getSpeciesName')
    save(FILES['idl'], t)

    # 3. DirectorManager.cpp: the Lua constants
    t = load(FILES['director'])
    t = replace_once(t, '\tluaEngine->setGlobalInt("SPECIES_CHISS", CreatureObject::CHISS);\n', '\tluaEngine->setGlobalInt("SPECIES_CHISS", CreatureObject::CHISS);\n'
                     + ''.join('\tluaEngine->setGlobalInt("SPECIES_%s", CreatureObject::%s);\n' % (s.upper(), s.upper()) for s, _, _, _ in NEW_RACES), 'director')
    save(FILES['director'], t)

    # 4. player_creation_manager.lua: human-rig pairs (both templates ride clientdata/player/client_shared_player_human_m/f.cdf + all_b.skt)
    t = load(FILES['pcm_lua'])
    t = replace_once(t, '\t{ "object/creature/player/chiss_female.iff", "object/creature/player/human_female.iff" },\n}', '\t{ "object/creature/player/chiss_female.iff", "object/creature/player/human_female.iff" },\n'
                     + ''.join('\t{ "object/creature/player/%s_%s.iff", "object/creature/player/human_%s.iff" }, -- Fable species S6\n' % (s, g, g) for s, g, _, _ in NEW_RACES) + '}', 'humanRigRaces')
    save(FILES['pcm_lua'], t)

    # 5. objects.lua: the shared client template declarations, appended as the Chiss ones were
    t = load(FILES['objects'])
    assert t.endswith('ObjectTemplates:addClientTemplate(object_creature_player_shared_chiss_male, "object/creature/player/shared_chiss_male.iff")\n'), 'objects.lua tail changed'
    t += '\n-- Sandbox: Nautolan and Togruta shared client templates (Fable species S6, 14 Oct 2026); the client files are the species package\'s, carried by MTG patch 023.\n'
    for s, g, _, _ in NEW_RACES:
        t += ('object_creature_player_shared_%s_%s = SharedCreatureObjectTemplate:new {\n\tclientTemplateFileName = "object/creature/player/shared_%s_%s.iff"\n}\n'
              'ObjectTemplates:addClientTemplate(object_creature_player_shared_%s_%s, "object/creature/player/shared_%s_%s.iff")\n\n') % ((s, g) * 4)
    t = t.rstrip('\n') + '\n'
    save(FILES['objects'], t)

    # 6. serverobjects.lua: includes after the Chiss ones
    t = load(FILES['serverobjects'])
    t = replace_once(t, 'includeFile("creature/player/chiss_female.lua") -- Sandbox: Chiss (Fable species S3)\n', 'includeFile("creature/player/chiss_female.lua") -- Sandbox: Chiss (Fable species S3)\n'
                     + ''.join('includeFile("creature/player/%s_%s.lua") -- Sandbox: %s (Fable species S6)\n' % (s, g, s.capitalize()) for s, g, _, _ in NEW_RACES), 'serverobjects')
    save(FILES['serverobjects'], t)

    # 7. the race templates: dev's chiss_<gender>.lua shape with the species' own baseHAM and species skill
    new_files = []
    for s, g, _, ham in NEW_RACES:
        src = load('%s/chiss_%s.lua' % (TEMPLATE_DIR, g))
        body = src.split('\n\n', 1)[1]   # drop the Chiss header comment
        body = body.replace('chiss', s).replace('baseHAM = { 100, 100, 100, 100, 100, 100, 100, 100, 100 }', 'baseHAM = ' + ham)
        assert 'chiss' not in body and ham in body and '"species_%s"' % s in body, s
        head = ('-- %s %s player race template. Sandbox: Fable species S6 (14 Oct 2026; outputs/Fable-species/s6/README.md).\n'
                '-- Shape: dev\'s chiss_%s.lua (zabrak_male.lua lineage). The shared client template (object/creature/player/shared_%s_%s.iff) is\n'
                '-- the Halyn/Phoenix species package\'s, carried by MTG patch 023 and declared in objects.lua. baseHAM = the package\'s\n'
                '-- racial_mods row for %s (the Zabrak profile); the same row goes into the client\'s datatables/creation/racial_mods.iff.\n\n') % (s.capitalize(), g, g, s, g, s)
        rel = '%s/%s_%s.lua' % (TEMPLATE_DIR, s, g)
        save(rel, head + body)
        new_files.append(rel)

    # 8. the patch: diff of the edited files, then hand-written new-file hunks
    out = []
    for rel in FILES.values():
        p = subprocess.run(['diff', '-u', '--label', 'a/' + rel, '--label', 'b/' + rel, os.path.join(ORIG, rel), os.path.join(NEW, rel)], capture_output=True)
        assert p.returncode == 1 and p.stdout, rel
        out.append(p.stdout.decode('utf-8'))
    for rel in new_files:
        text = open(os.path.join(NEW, rel), encoding='utf-8', newline='').read()
        lines = text.split('\n')
        if lines and lines[-1] == '':
            lines.pop()
        out.append('--- /dev/null\n+++ b/%s\n@@ -0,0 +1,%d @@\n' % (rel, len(lines)) + ''.join('+' + l + '\n' for l in lines))
    os.makedirs(os.path.join(S6, 'patch'), exist_ok=True)
    path = os.path.join(S6, 'patch', 'species-s6.patch')
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(''.join(out))
    with open(os.path.join(S6, 'new-files.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# new files under the repository root, created by patch/species-s6.patch\n' + '\n'.join(new_files) + '\n')
    text = ''.join(out)
    print('patch', path, len(text.splitlines()), 'lines; +%d -%d' % (sum(1 for l in text.splitlines() if l.startswith('+') and not l.startswith('+++')),
                                                                     sum(1 for l in text.splitlines() if l.startswith('-') and not l.startswith('---'))))
    for s, g, c in crcs:
        print('SharedRace', s, g, '0x%08X' % c)
    return 0


if __name__ == '__main__':
    sys.exit(main())
