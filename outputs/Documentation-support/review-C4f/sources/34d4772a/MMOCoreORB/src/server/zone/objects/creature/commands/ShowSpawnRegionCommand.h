/*
				Copyright <SWGEmu>
		See file COPYING for copying conditions.*/

#ifndef SHOWSPAWNREGIONCOMMAND_H_
#define SHOWSPAWNREGIONCOMMAND_H_

#include "server/zone/objects/region/SpawnArea.h"
#include "server/zone/managers/creature/LairSpawn.h"
#include "server/zone/objects/player/sui/messagebox/SuiMessageBox.h"

/*
 * Sandbox (Claude, 14 Oct 2026; owner asked for the empty staff stubs to work): /showSpawnRegion lists the spawn
 * areas the caller stands in: spawned count against the limit, players in range, and what can spawn there (lair
 * template, weighting, per-type limit, difficulty range). No-spawn areas the caller is in are named too. Read-only.
 */
class ShowSpawnRegionCommand : public QueueCommand {
public:

	ShowSpawnRegionCommand(const String& name, ZoneProcessServer* server)
		: QueueCommand(name, server) {

	}

	int doQueueCommand(CreatureObject* creature, const uint64& target, const UnicodeString& arguments) const {

		if (!checkStateMask(creature))
			return INVALIDSTATE;

		if (!checkInvalidLocomotions(creature))
			return INVALIDLOCOMOTION;

		if (!creature->isPlayerCreature())
			return GENERALERROR;

		Zone* zone = creature->getZone();

		if (zone == nullptr || zone->isSpaceZone()) {
			creature->sendSystemMessage("/showSpawnRegion works on ground zones.");
			return GENERALERROR;
		}

		StringBuffer msg;
		msg << "Spawn areas at " << (int) creature->getPositionX() << " " << (int) creature->getPositionY()
			<< " on " << zone->getZoneName() << endl;

		int spawnAreas = 0;
		SortedVector<ManagedReference<ActiveArea*>> areas = *creature->getActiveAreas();

		for (int i = 0; i < areas.size(); ++i) {
			ManagedReference<ActiveArea*> area = areas.get(i);

			if (area == nullptr)
				continue;

			if (area->isNoSpawnArea()) {
				msg << endl << "No-spawn area: " << area->getAreaName() << endl;
				continue;
			}

			SpawnArea* spawnArea = dynamic_cast<SpawnArea*>(area.get());

			if (spawnArea == nullptr)
				continue;

			++spawnAreas;
			msg << endl << spawnArea->getAreaName() << (spawnArea->isWorldSpawnArea() ? " (world spawner)" : "")
				<< ": " << spawnArea->getTotalSpawnCount() << " spawned of " << spawnArea->getMaxSpawnLimit()
				<< " allowed; " << spawnArea->getPlayersInRange() << " player(s) in range" << endl;

			auto spawnList = spawnArea->getSpawnList();

			if (spawnList == nullptr || spawnList->size() == 0) {
				msg << "  nothing can spawn here" << endl;
				continue;
			}

			int total = Math::max(spawnArea->getTotalWeighting(), 1);

			for (int j = 0; j < spawnList->size() && j < 20; ++j) {
				const LairSpawn* lair = spawnList->get(j);

				if (lair == nullptr)
					continue;

				msg << "  " << lair->getLairTemplateName() << ": weight " << lair->getWeighting()
					<< " (" << (lair->getWeighting() * 100 / total) << "%), limit " << lair->getSpawnLimit()
					<< ", difficulty " << lair->getMinDifficulty() << "-" << lair->getMaxDifficulty() << endl;
			}

			if (spawnList->size() > 20)
				msg << "  ... and " << (spawnList->size() - 20) << " more" << endl;
		}

		if (spawnAreas == 0)
			msg << endl << "You are not inside any spawn area." << endl;

		creature->sendSystemMessage("/showSpawnRegion: " + String::valueOf(spawnAreas) + " spawn area(s) here; details in the window.");

		ManagedReference<SuiMessageBox*> box = new SuiMessageBox(creature, SuiWindowType::NONE);
		box->setPromptTitle("Spawn areas here");
		box->setPromptText(msg.toString());
		creature->sendMessage(box->generateMessage());

		return SUCCESS;
	}

};

#endif //SHOWSPAWNREGIONCOMMAND_H_
