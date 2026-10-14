"""S4b: build the reviewable Core3-dev patch (Chiss race entries, the species id, the data-driven human-rig clothing
rule, the Director constant, the Lua table) from verbatim copies of the dev files in ../work/orig: every edit is an
exact-anchor replacement that must match once, the edited copies go to ../work/new, and the WSL step diffs them
(../cpp/species-chiss-human-rig.patch) and runs `git apply --check` in a scratch repository. Our own code (Fable,
14 Oct 2026). Read-only on /opt/swg.

    python -I make_cpp_patch.py
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
S4 = os.path.normpath(os.path.join(HERE, '..'))
ORIG = os.path.join(S4, 'work', 'orig')
NEW = os.path.join(S4, 'work', 'new')

CHISS_ID = '0xE7'   # first id past the stock species table in managers/creature_manager.lua (aiSpeciesData ends at 230)
FILES = {
    'races': 'src/server/zone/objects/player/Races.h',
    'idl': 'src/server/zone/objects/creature/CreatureObject.idl',
    'director': 'src/server/zone/managers/director/DirectorManager.cpp',
    'pcc': 'src/server/zone/objects/player/components/PlayerContainerComponent.cpp',
    'cmi': 'src/server/zone/managers/creature/CreatureManagerImplementation.cpp',
    'pcm_h': 'src/server/zone/managers/player/creation/PlayerCreationManager.h',
    'pcm_cpp': 'src/server/zone/managers/player/creation/PlayerCreationManager.cpp',
    'lua': 'bin/scripts/managers/player_creation_manager.lua',
}


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
    assert n == 1, '%s: anchor found %d times: %r' % (label, n, old[:80])
    return text.replace(old, new)


def main():
    shutil.rmtree(NEW, ignore_errors=True)
    hunks = []

    # 1. Races.h: the two Chiss entries in all six arrays, and bounds that follow the array size
    t = load(FILES['races'])
    t = replace_once(t, '    "ithorian"  // DA E7   -   ithorian female\n};', '    "ithorian", // DA E7   -   ithorian female\n    "chiss", // chiss male (Fable species S4)\n    "chiss"  // chiss female\n};', 'Species')
    t = replace_once(t, '\t\t0x31,\n\t\t0x21\n};', '\t\t0x31,\n\t\t0x21,\n\t\t%s, // chiss male: CreatureObject::CHISS\n\t\t%s  // chiss female\n};' % (CHISS_ID, CHISS_ID), 'TemplateSpecies')
    t = replace_once(t, '    "female"  // DA E7   -   ithorian female\n};', '    "female", // DA E7   -   ithorian female\n    "male", // chiss male\n    "female"  // chiss female\n};', 'Gender')
    t = replace_once(t, '    "object/creature/player/shared_ithorian_female.iff"  // DA E7   -   ithorian female\n};',
                     '    "object/creature/player/shared_ithorian_female.iff", // DA E7   -   ithorian female\n    "object/creature/player/shared_chiss_male.iff", // chiss male\n    "object/creature/player/shared_chiss_female.iff"  // chiss female\n};', 'RaceStrs')
    t = replace_once(t, '    "object/creature/player/ithorian_female.iff"  // DA E7   -   ithorian female\n};',
                     '    "object/creature/player/ithorian_female.iff", // DA E7   -   ithorian female\n    "object/creature/player/chiss_male.iff", // chiss male\n    "object/creature/player/chiss_female.iff"  // chiss female\n};\n\n'
                     '// the number of race entries above; every array in this file has RACE_COUNT entries in the same order\nconst static int RACE_COUNT = sizeof(CCRaceStrs) / sizeof(CCRaceStrs[0]);', 'CCRaceStrs')
    t = replace_once(t, '    0xB3E08013\n};', '    0xB3E08013,\n    0x02F60EAC, // chiss male: SOE CRC of object/creature/player/shared_chiss_male.iff\n    0x614A1B68  // chiss female\n};', 'SharedRace')
    assert t.count('raceid > 19') == 5, t.count('raceid > 19')
    t = t.replace('raceid > 19', 'raceid >= RACE_COUNT')
    t = replace_once(t, '\t\tfor (int i = 0; i < 20; ++i) {\n\t\t\tif (SharedRace[i] == sharedRaceCRC) {', '\t\tfor (int i = 0; i < RACE_COUNT; ++i) {\n\t\t\tif (SharedRace[i] == sharedRaceCRC) {', 'getCompleteRace loop')
    t = replace_once(t, '    \tfor (int i = 0; i < 20; i++) {\n        \tif (strcmp(name.toCharArray(), CCRaceStrs[i]) == 0)', '    \tfor (int i = 0; i < RACE_COUNT; i++) {\n        \tif (strcmp(name.toCharArray(), CCRaceStrs[i]) == 0)', 'getRaceID loop')
    t = replace_once(t, '\t\treturn attributeLimits[raceid % 10];', '\t\t// the ten stock limit rows; added races use the human row (their real limits come from datatables/creation/attribute_limits.iff)\n\t\treturn attributeLimits[raceid < 20 ? raceid % 10 : 0];', 'getAttribLimits')
    save(FILES['races'], t)
    hunks.append(('Races.h', 'Chiss male/female appended to Species, TemplateSpecies (CreatureObject::CHISS), Gender, RaceStrs, CCRaceStrs and SharedRace (SOE CRCs of the shared templates, the same hash the stock entries use); RACE_COUNT derived from CCRaceStrs replaces the five "> 19" bounds and the two "< 20" loops; getAttribLimits keeps the ten stock rows and maps added races to the human row.'))

    # 2. CreatureObject.idl: the species constant and its name
    t = load(FILES['idl'])
    t = replace_once(t, '\tpublic static final int SULLUSTAN = 0x31;\n', '\tpublic static final int SULLUSTAN = 0x31;\n\tpublic static final int CHISS = %s; // Fable species S4: first id past the stock species table (managers/creature_manager.lua aiSpeciesData ends at 230)\n' % CHISS_ID, 'CHISS constant')
    t = replace_once(t, '\t\telse if(species == 0x31)\n\t\t\treturn "sullustan";\n\t\telse\n\t\t\treturn "";', '\t\telse if(species == 0x31)\n\t\t\treturn "sullustan";\n\t\telse if(species == CHISS)\n\t\t\treturn "chiss";\n\t\telse\n\t\t\treturn "";', 'getSpeciesName')
    save(FILES['idl'], t)
    hunks.append(('CreatureObject.idl', 'CHISS = %s (unused in the stock NPC species table, unlike the package\'s 0x34 = tulgah) and getSpeciesName() -> "chiss".' % CHISS_ID))

    # 3. DirectorManager.cpp: the Lua constant
    t = load(FILES['director'])
    t = replace_once(t, '\tluaEngine->setGlobalInt("SPECIES_SULLUSTAN", CreatureObject::SULLUSTAN);\n', '\tluaEngine->setGlobalInt("SPECIES_SULLUSTAN", CreatureObject::SULLUSTAN);\n\tluaEngine->setGlobalInt("SPECIES_CHISS", CreatureObject::CHISS);\n', 'SPECIES_CHISS')
    save(FILES['director'], t)
    hunks.append(('DirectorManager.cpp', 'SPECIES_CHISS for screenplays, next to the stock species constants.'))

    # 4. PlayerCreationManager: the human-rig race map from player_creation_manager.lua and the two helpers
    t = load(FILES['pcm_h'])
    t = replace_once(t, '\tVectorMap<String, Reference<HairStyleInfo*> > hairStyleInfo;\n', '\tVectorMap<String, Reference<HairStyleInfo*> > hairStyleInfo;\n\n\t/**\n\t * Fable species S4: race file -> the race file whose wearable permissions it shares (a species whose player\n\t * template rides the human skeleton wears what a human of the same gender wears). From player_creation_manager.lua.\n\t */\n\tVectorMap<String, String> humanRigRaces;\n', 'humanRigRaces member')
    t = replace_once(t, '\t//void generateHologrindProfessions(CreatureObject* creature);\n\npublic:\n', '\t//void generateHologrindProfessions(CreatureObject* creature);\n\npublic:\n\t/**\n\t * True when the wearable\'s playerRaces list names the race file, or the race file it stands in for (humanRigRaces).\n\t */\n\tbool canWearRace(const Vector<uint32>* races, const String& raceFile) const;\n\n', 'canWearRace declaration')
    save(FILES['pcm_h'], t)
    t = load(FILES['pcm_cpp'])
    t = replace_once(t, '\tracialCreationData.setNoDuplicateInsertPlan();\n', '\tracialCreationData.setNoDuplicateInsertPlan();\n\thumanRigRaces.setNoDuplicateInsertPlan();\n', 'constructor')
    t = replace_once(t, '\tfreeGodMode = lua->getGlobalByte("freeGodMode");\n', '\tfreeGodMode = lua->getGlobalByte("freeGodMode");\n\n'
                     '\t// Fable species S4: { race file, race file whose playerRaces entries apply } pairs\n'
                     '\thumanRigRaces.removeAll();\n\n'
                     '\tLuaObject humanRig = lua->getGlobalObject("humanRigRaces");\n\n'
                     '\tif (humanRig.isValidTable()) {\n'
                     '\t\tfor (int i = 1; i <= humanRig.getTableSize(); ++i) {\n'
                     '\t\t\tLuaObject pair = humanRig.getObjectAt(i);\n\n'
                     '\t\t\tif (pair.isValidTable() && pair.getTableSize() >= 2)\n'
                     '\t\t\t\thumanRigRaces.put(pair.getStringAt(1), pair.getStringAt(2));\n\n'
                     '\t\t\tpair.pop();\n'
                     '\t\t}\n'
                     '\t}\n\n'
                     '\thumanRig.pop();\n\n'
                     '\tinfo() << "Loaded " << humanRigRaces.size() << " human-rig race mappings.";\n', 'loadLuaConfig')
    t = t.rstrip('\n') + '\n\nbool PlayerCreationManager::canWearRace(const Vector<uint32>* races, const String& raceFile) const {\n\tif (races == nullptr)\n\t\treturn false;\n\n\tif (races->contains(raceFile.hashCode()))\n\t\treturn true;\n\n\tif (humanRigRaces.contains(raceFile))\n\t\treturn races->contains(humanRigRaces.get(raceFile).hashCode());\n\n\treturn false;\n}\n'
    save(FILES['pcm_cpp'], t)
    hunks.append(('PlayerCreationManager.h/.cpp', 'humanRigRaces (race file -> stand-in race file) loaded from the humanRigRaces table in player_creation_manager.lua inside loadLuaConfig; canWearRace(races, raceFile) = the stock contains() test, then the stand-in\'s. No behaviour change for stock races (an empty or absent table leaves the map empty).'))

    # 5. the two clothing checks use the helper
    t = load(FILES['pcc'])
    t = replace_once(t, '#include "server/zone/managers/player/PlayerManager.h"\n', '#include "server/zone/managers/player/PlayerManager.h"\n#include "server/zone/managers/player/creation/PlayerCreationManager.h"\n', 'pcc include')
    t = replace_once(t, '\t\t\tif (!races->contains(race.hashCode())) {\n', '\t\t\tif (!PlayerCreationManager::instance()->canWearRace(races, race)) {\n', 'pcc check')
    save(FILES['pcc'], t)
    t = load(FILES['cmi'])
    t = replace_once(t, '#include "server/zone/objects/transaction/TransactionLog.h"\n', '#include "server/zone/objects/transaction/TransactionLog.h"\n#include "server/zone/managers/player/creation/PlayerCreationManager.h"\n', 'cmi include')
    t = replace_once(t, '\tif (clothing->isWearableObject() && !races->contains(race.hashCode())) {\n', '\tif (clothing->isWearableObject() && !PlayerCreationManager::instance()->canWearRace(races, race)) {\n', 'cmi check')
    save(FILES['cmi'], t)
    hunks.append(('PlayerContainerComponent.cpp:34 and CreatureManagerImplementation.cpp:1303', 'the playerRaces test goes through canWearRace; everything else (faction, encumbrance, certifications, the vendor/actor messages) is untouched.'))

    # 6. the Lua table
    t = load(FILES['lua'])
    t = t.rstrip('\n') + '\n\n-- Fable species S4: species whose player template rides the human skeleton wear what a human of the same gender\n-- wears. Each pair = { race file, race file whose playerRaces entries apply }; read by PlayerCreationManager::loadLuaConfig.\nhumanRigRaces = {\n\t{ "object/creature/player/chiss_male.iff", "object/creature/player/human_male.iff" },\n\t{ "object/creature/player/chiss_female.iff", "object/creature/player/human_female.iff" },\n}\n'
    save(FILES['lua'], t)
    hunks.append(('bin/scripts/managers/player_creation_manager.lua', 'the humanRigRaces table with the two Chiss race files; add a pair per human-rig species.'))

    with open(os.path.join(S4, 'work', 'hunks.txt'), 'w', encoding='utf-8', newline='\n') as f:
        for name, text in hunks:
            f.write('%s: %s\n' % (name, text))
    print('edited copies in', NEW)
    for name, text in hunks:
        print('-', name, ':', text[:120])
    return 0


if __name__ == '__main__':
    sys.exit(main())
