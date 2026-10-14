"""Write work/new/MMOCoreORB/... from the verbatim copies in work/orig (R2 backfill patch)."""
import os

R = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources2'
O = R + '/work/orig/MMOCoreORB'
N = R + '/work/new/MMOCoreORB'


def edit(rel, reps):
    s = open(O + '/' + rel, encoding='utf-8', newline='').read()
    for old, new in reps:
        assert s.count(old) == 1, (rel, old[:70], s.count(old))
        s = s.replace(old, new)
    os.makedirs(os.path.dirname(N + '/' + rel), exist_ok=True)
    open(N + '/' + rel, 'w', encoding='utf-8', newline='').write(s)


HDR = 'src/server/zone/managers/resource/resourcespawner/ResourceSpawner.h'
CPP = 'src/server/zone/managers/resource/resourcespawner/ResourceSpawner.cpp'
MGR = 'src/server/zone/managers/resource/ResourceManagerImplementation.cpp'
LUA = 'bin/scripts/managers/resource_manager.lua'

edit(HDR, [
    ("\tVector<String> activeResourceZones;\n",
     "\tVector<String> activeResourceZones;\n"
     "\tVector<String> backfillZones;   // zones that take a share of the spawns already in shift at load (Lua backfillZones)\n"),
    ("\tvoid addZone(const String& zoneName);\n",
     "\tvoid addZone(const String& zoneName);\n\tvoid addBackfillZone(const String& zoneName);\n"),
])

ADD_ZONE = '''void ResourceSpawner::addBackfillZone(const String& zoneName) {
	if (!activeResourceZones.contains(zoneName)) {
		warning("backfillZones: " + zoneName + " is not in activeZones, ignored");
		return;
	}

	if (!backfillZones.contains(zoneName))
		backfillZones.add(zoneName);
}

void ResourceSpawner::removeZone(const String& zoneName) {'''

COUNTERS = '''	uint64 objectID = 0;

	Vector<int> backfillChecked, backfillAdded, backfillAlready, backfillAtMax, backfillLost;

	for (int z = 0; z < backfillZones.size(); ++z) {
		backfillChecked.add(0);
		backfillAdded.add(0);
		backfillAlready.add(0);
		backfillAtMax.add(0);
		backfillLost.add(0);
	}

	while (iterator.getNextKey(objectID)) {
'''

TOPUP_END = '''					resourceSpawn->createSpawnMaps(resourceEntry->isJTL(), minPool - spawnMapSize,
							resourceEntry->getMaxpool() - spawnMapSize, resourceEntry->getZoneRestriction(), activeZones);
				}
'''

BACKFILL = '''
				// Backfill (Fable, 14 Oct 2026): a zone added to activeZones after this spawn was created never gets a
				// spawn map (getSpawnZones chooses the zones once). Give each backfill zone the chance it would have had
				// then: getSpawnZones keeps zonecount of the active zones at random, so one zone's chance is
				// zonecount / zones, and zonecount is this spawn's map count today. The roll hashes the spawn's name
				// and the zone, so every restart decides the same way: nothing to store, no re-rolling of the losers.
				if (backfillZones.size() > 0 && resourceEntry->getZoneRestriction().isEmpty() && activeResourceZones.size() > 0) {
					int maxPool = resourceEntry->getMaxpool();
					uint32 zones = activeResourceZones.size();

					for (int z = 0; z < backfillZones.size(); ++z) {
						const String& zoneName = backfillZones.get(z);
						uint32 mapSize = resourceSpawn->getSpawnMapSize();
						bool onZone = false;

						for (uint32 i = 0; i < mapSize; ++i) {
							if (resourceSpawn->getSpawnMapZone(i) == zoneName)
								onZone = true;
						}

						backfillChecked.set(z, backfillChecked.get(z) + 1);

						if (onZone) {
							backfillAlready.set(z, backfillAlready.get(z) + 1);
							continue;
						}

						if ((int) mapSize >= maxPool) {
							backfillAtMax.set(z, backfillAtMax.get(z) + 1);
							continue;
						}

						uint32 roll = (resourceSpawn->getName() + ":" + zoneName).hashCode() % 1000;

						if (roll * zones >= mapSize * 1000) {   // chance = mapSize / zones
							backfillLost.set(z, backfillLost.get(z) + 1);
							continue;
						}

						Vector<String> one;
						one.add(zoneName);

						Locker locker(resourceSpawn);

						resourceSpawn->createSpawnMaps(resourceEntry->isJTL(), 1, 1, "", one);
						backfillAdded.set(z, backfillAdded.get(z) + 1);
					}
				}
'''

LOG = '''	for (int z = 0; z < backfillZones.size(); ++z) {
		info(true) << "Resource backfill: zone " << backfillZones.get(z) << ": " << backfillChecked.get(z)
				<< " in-shift galaxy-wide spawns checked, " << backfillAdded.get(z) << " added, " << backfillAlready.get(z)
				<< " already there, " << backfillAtMax.get(z) << " at max pool, " << backfillLost.get(z) << " not chosen";
	}

	if(resourceMap->size() == 0 && scriptLoading) {'''

edit(CPP, [
    ("void ResourceSpawner::removeZone(const String& zoneName) {", ADD_ZONE),
    ("\tuint64 objectID = 0;\n\n\twhile (iterator.getNextKey(objectID)) {\n", COUNTERS),
    (TOPUP_END, TOPUP_END + BACKFILL),
    ("\tif(resourceMap->size() == 0 && scriptLoading) {", LOG),
])

MGR_OLD = '''		resourceSpawner->addZone(zoneName);
	}

	shiftInterval = lua->getGlobalInt("averageShiftTime");'''
MGR_NEW = '''		resourceSpawner->addZone(zoneName);
	}

	// Zones that take a fair share of the spawns already in shift when the server starts
	// (ResourceSpawner::loadResourceSpawns); empty unless a planet has just joined activeZones.
	String backfillString = lua->getGlobalString("backfillZones");

	StringTokenizer backfillTokens(backfillString);
	backfillTokens.setDelimeter(",");

	while (backfillTokens.hasMoreTokens()) {
		String zoneName;
		backfillTokens.getStringToken(zoneName);
		resourceSpawner->addBackfillZone(zoneName);
	}

	shiftInterval = lua->getGlobalInt("averageShiftTime");'''
edit(MGR, [(MGR_OLD, MGR_NEW)])

LUA_OLD = 'activeZones = "corellia,tatooine,lok,naboo,rori,endor,talus,yavin4,dathomir,dantooine,hoth"\n'
LUA_NEW = LUA_OLD + '''
-- Zones (from activeZones) that take a fair share of the spawns already in shift when the server starts: a planet
-- added to activeZones otherwise waits for every galaxy-wide spawn to expire (6-11 days) before minerals, gas and
-- chemicals reach it. Set it to the new planet for its first start, e.g. "hoth"; leave it "" on live. Each in-shift
-- galaxy-wide spawn is added with the chance it would have had at creation (its planet count over the active zones),
-- decided by a fixed hash of spawn and zone, so a second start adds nothing new. The log line "Resource backfill:"
-- gives the count.
backfillZones = ""
'''
edit(LUA, [(LUA_OLD, LUA_NEW)])
print('new copies written')
