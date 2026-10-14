/*
				Copyright <SWGEmu>
		See file COPYING for copying conditions.*/

#ifndef AGENTSKILLCOMMAND_H_
#define AGENTSKILLCOMMAND_H_

#include "conf/ConfigManager.h"
#include "server/zone/objects/creature/commands/SandboxTestGalaxy.h"
#include "server/login/account/AccountManager.h"
#include "server/zone/managers/skill/SkillManager.h"
#include "server/zone/objects/creature/CreatureObject.h"
#include "server/zone/objects/creature/commands/QueueCommand.h"
#include "server/zone/objects/player/PlayerObject.h"

/*
 * Sandbox test helper: skill boxes for agent bots on a TEST galaxy, so a squad can test what trained
 * characters do (doctor and entertainer buffs, ranger camps, multi-profession builds) without days of
 * grinding. Off unless Core3.AgentGear = true on a disposable test galaxy (SandboxTestGalaxy.h); only for
 * accounts in Core3.AgentAccounts.
 *
 *   /agentskill <skill box> [<skill box> ...]   e.g. science_doctor_novice outdoors_ranger_novice
 *
 * Prerequisite boxes are granted too, without XP (the same call character creation uses). Skill-point
 * limits still apply. Answer, to the caller only: "[agentskill] {json}" with granted/failed/unknown.
 * Training at trainers is a separate test and should keep using real trainers.
 */
class AgentSkillCommand : public QueueCommand {
public:
	AgentSkillCommand(const String& name, ZoneProcessServer* server) : QueueCommand(name, server) {
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

		if (!ConfigManager::instance()->getBool("Core3.AgentGear", false) || !isDisposableTestGalaxy()) {
			creature->sendSystemMessage("[agentskill] {\"error\":\"off on this galaxy (needs a test galaxy and Core3.AgentGear)\"}");
			return GENERALERROR;
		}

		JSONSerializationType reply, granted = JSONSerializationType::array(), failed = JSONSerializationType::array(),
			unknown = JSONSerializationType::array();
		StringTokenizer tokenizer(arguments.toString());
		auto skills = SkillManager::instance();
		int count = 0;

		while (tokenizer.hasMoreTokens() && count++ < 16) {
			String box;
			tokenizer.getStringToken(box);

			if (skills->getSkill(box) == nullptr)
				unknown.push_back(box.toCharArray());
			else if (creature->hasSkill(box) || skills->awardSkill(box, creature, true, true, true))
				granted.push_back(box.toCharArray());
			else
				failed.push_back(box.toCharArray());
		}

		if (count == 0) {
			creature->sendSystemMessage("[agentskill] {\"error\":\"usage: /agentskill <skill box> [...]\"}");
			return INVALIDPARAMETERS;
		}

		reply["granted"] = granted;
		reply["failed"] = failed;
		reply["unknown"] = unknown;
		creature->sendSystemMessage("[agentskill] " + String(reply.dump().c_str()));

		return SUCCESS;
	}
};

#endif // AGENTSKILLCOMMAND_H_
