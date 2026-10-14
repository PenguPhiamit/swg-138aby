/*
				Copyright <SWGEmu>
		See file COPYING for copying conditions.*/

#ifndef SPAWNSTATUSCOMMAND_H_
#define SPAWNSTATUSCOMMAND_H_

#include "server/zone/objects/creature/ai/AiAgent.h"
#include "server/zone/objects/creature/CreatureObject.h"
#include "server/zone/managers/creature/CreatureManager.h"
#include "server/zone/objects/region/SpawnArea.h"
#include "server/zone/objects/player/sui/messagebox/SuiMessageBox.h"
#include <algorithm>
#include <vector>

/*
 * Sandbox (Claude, 14 Oct 2026; owner asked for the empty staff stubs to work): /spawnStatus summarises the
 * caller's planet: every spawn area with its spawned count against its limit, players in range and how many
 * kinds of spawn it holds, busiest first, plus the planet totals. Read-only. /showSpawnRegion gives the details
 * of the areas where you stand.
 */
class SpawnStatusCommand : public QueueCommand {
public:

	SpawnStatusCommand(const String& name, ZoneProcessServer* server)
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
			creature->sendSystemMessage("/spawnStatus works on ground zones.");
			return GENERALERROR;
		}

		CreatureManager* creatureManager = zone->getCreatureManager();

		if (creatureManager == nullptr)
			return GENERALERROR;

		struct Row {
			String name;
			int spawned, limit, players, kinds;
			bool world;
		};

		std::vector<Row> rows;
		int totalSpawned = 0, totalLimit = 0;
		int count = creatureManager->getSpawnAreaCount();

		for (int i = 0; i < count; ++i) {
			ManagedReference<SpawnArea*> area = creatureManager->getSpawnAreaAt(i);

			if (area == nullptr)
				continue;

			auto spawnList = area->getSpawnList();
			Row row = {area->getAreaName(), area->getTotalSpawnCount(), area->getMaxSpawnLimit(),
					   area->getPlayersInRange(), spawnList == nullptr ? 0 : spawnList->size(), area->isWorldSpawnArea()};

			totalSpawned += row.spawned;
			totalLimit += row.limit;
			rows.push_back(row);
		}

		std::sort(rows.begin(), rows.end(), [](const Row& a, const Row& b) { return a.spawned > b.spawned; });  // busiest first

		StringBuffer msg;
		msg << zone->getZoneName() << ": " << (int) rows.size() << " spawn areas, " << totalSpawned << " spawned of "
			<< totalLimit << " allowed in all." << endl << endl;

		for (int i = 0; i < (int) rows.size() && i < 40; ++i) {
			const Row& row = rows[i];
			msg << row.name << (row.world ? " (world spawner)" : "") << ": " << row.spawned << "/" << row.limit
				<< ", " << row.players << " player(s) in range, " << row.kinds << " kind(s) of spawn" << endl;
		}

		if (rows.size() > 40)
			msg << "... and " << (int) (rows.size() - 40) << " more" << endl;

		msg << endl << "Use /showSpawnRegion where you stand for what can spawn there.";

		creature->sendSystemMessage("/spawnStatus: " + String::valueOf((int) rows.size()) + " spawn areas on " + zone->getZoneName()
				+ ", " + String::valueOf(totalSpawned) + " spawned; details in the window.");

		ManagedReference<SuiMessageBox*> box = new SuiMessageBox(creature, SuiWindowType::NONE);
		box->setPromptTitle("Spawn status: " + zone->getZoneName());
		box->setPromptText(msg.toString());
		creature->sendMessage(box->generateMessage());

		return SUCCESS;
	}

};

#endif //SPAWNSTATUSCOMMAND_H_
