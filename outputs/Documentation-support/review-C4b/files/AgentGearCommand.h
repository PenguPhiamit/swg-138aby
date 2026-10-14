/*
				Copyright <SWGEmu>
		See file COPYING for copying conditions.*/

#ifndef AGENTGEARCOMMAND_H_
#define AGENTGEARCOMMAND_H_

#include "conf/ConfigManager.h"
#include "server/login/account/AccountManager.h"
#include "server/zone/ZoneServer.h"
#include "server/zone/objects/creature/CreatureObject.h"
#include "server/zone/objects/creature/commands/QueueCommand.h"
#include "server/zone/objects/player/PlayerObject.h"
#include "server/zone/objects/tangible/TangibleObject.h"

/*
 * Sandbox test helper: gear for agent bots on a TEST galaxy. Off unless Core3.AgentGear = true in
 * config-local.lua (test_galaxy.py --config AgentGear=true), and only for accounts in Core3.AgentAccounts.
 *
 *   /agentgear basic   a weapon for the starting profession (any other profession: a pistol), bone
 *                      armor, and stimpacks for medics. For ordinary combat groups.
 *   /agentgear boss    T21 rifle or battleaxe, composite armor, more stimpacks. For the world-boss group.
 *   /agentgear support the camp crew's tools: doctor enhancement packs and stimpacks (medics), camp kits
 *                      (scouts), an instrument (entertainers), a pistol and bone armor for everyone.
 *
 * Items go into free equipment slots, otherwise into the inventory. Answer, to the caller only:
 * "[agentgear] {json}" with what was equipped, what went to the inventory and what failed.
 */
class AgentGearCommand : public QueueCommand {
public:
	AgentGearCommand(const String& name, ZoneProcessServer* server) : QueueCommand(name, server) {
	}

	int doQueueCommand(CreatureObject* creature, const uint64& target, const UnicodeString& arguments) const {
		if (!creature->isPlayerCreature())
			return GENERALERROR;

		auto ghost = creature->getPlayerObject();

		if (ghost == nullptr)
			return GENERALERROR;

		auto account = AccountManager::getAccount(ghost->getAccountID(), true);
		const auto& allowed = ConfigManager::instance()->getStringVector("Core3.AgentAccounts");

		if (account == nullptr || !allowed.contains(account->getUsername()))
			return INSUFFICIENTPERMISSION;

		if (!ConfigManager::instance()->getBool("Core3.AgentGear", false)) {
			creature->sendSystemMessage("[agentgear] {\"error\":\"off on this galaxy (Core3.AgentGear)\"}");
			return GENERALERROR;
		}

		String kit = arguments.toString().trim().toLowerCase();

		if (kit != "basic" && kit != "boss" && kit != "support") {
			creature->sendSystemMessage("[agentgear] {\"error\":\"usage: /agentgear basic|boss|support\"}");
			return INVALIDPARAMETERS;
		}

		bool boss = kit == "boss";
		Vector<String> templates;

		if (kit == "support") {
			templates.add("object/weapon/ranged/pistol/pistol_cdef.iff");

			if (creature->hasSkill("science_medic_novice")) {
				const char* packs[] = {"health", "action", "strength", "constitution", "quickness", "stamina"};

				for (const char* pack : packs)
					for (int i = 0; i < 2; ++i)
						templates.add(String("object/tangible/medicine/crafted/medpack_enhance_") + pack + "_a.iff");

				for (int i = 0; i < 4; ++i)
					templates.add("object/tangible/medicine/crafted/crafted_stimpack_sm_s1_a.iff");
			}

			if (creature->hasSkill("outdoors_scout_novice")) {
				templates.add("object/tangible/scout/camp/camp_basic.iff");
				templates.add("object/tangible/scout/camp/camp_improved.iff");
			}

			if (creature->hasSkill("social_entertainer_novice"))
				templates.add("object/tangible/instrument/slitherhorn.iff");
		} else if (creature->hasSkill("combat_marksman_novice")) {
			templates.add(boss ? "object/weapon/ranged/rifle/rifle_t21.iff" : "object/weapon/ranged/rifle/rifle_cdef.iff");
			templates.add("object/weapon/ranged/pistol/pistol_cdef.iff");
		} else if (creature->hasSkill("combat_brawler_novice")) {
			templates.add(boss ? "object/weapon/melee/2h_sword/2h_sword_battleaxe.iff" : "object/weapon/melee/knife/knife_dagger.iff");
		} else {
			templates.add("object/weapon/ranged/pistol/pistol_cdef.iff");
		}

		const char* pieces[] = {"chest_plate", "leggings", "helmet", "boots", "gloves", "bicep_l", "bicep_r", "bracer_l", "bracer_r"};

		for (const char* piece : pieces)  // support gets bone armor too
			templates.add(boss ? String("object/tangible/wearables/armor/composite/armor_composite_") + piece + ".iff"
							   : String("object/tangible/wearables/armor/bone/armor_bone_s01_") + piece + ".iff");

		if (creature->hasSkill("science_medic_novice")) {
			for (int i = 0; i < (boss ? 6 : 3); ++i)
				templates.add(boss ? "object/tangible/medicine/crafted/crafted_stimpack_sm_s1_c.iff"
								   : "object/tangible/medicine/crafted/crafted_stimpack_sm_s1_a.iff");
		}

		ManagedReference<SceneObject*> inventory = creature->getSlottedObject("inventory");

		if (inventory == nullptr)
			return GENERALERROR;

		JSONSerializationType reply, equipped = JSONSerializationType::array(), stored = JSONSerializationType::array(),
			failed = JSONSerializationType::array();

		for (const String& path : templates) {
			ManagedReference<SceneObject*> item = server->getZoneServer()->createObject(path.hashCode(), 1);

			if (item == nullptr) {
				failed.push_back(path.toCharArray());
				continue;
			}

			String error;

			if (creature->canAddObject(item, 4, error) == 0 && creature->transferObject(item, 4, true)) {
				creature->broadcastObject(item, true);
				equipped.push_back(path.toCharArray());
			} else if (inventory->transferObject(item, -1, true)) {
				inventory->broadcastObject(item, true);
				stored.push_back(path.toCharArray());
			} else {
				item->destroyObjectFromDatabase(true);
				failed.push_back(path.toCharArray());
			}
		}

		reply["kit"] = kit.toCharArray();
		reply["equipped"] = equipped;
		reply["inventory"] = stored;
		reply["failed"] = failed;
		creature->sendSystemMessage("[agentgear] " + String(reply.dump().c_str()));

		return SUCCESS;
	}
};

#endif // AGENTGEARCOMMAND_H_
