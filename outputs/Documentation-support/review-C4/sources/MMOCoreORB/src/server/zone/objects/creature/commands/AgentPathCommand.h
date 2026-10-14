/*
				Copyright <SWGEmu>
		See file COPYING for copying conditions.*/

#ifndef AGENTPATHCOMMAND_H_
#define AGENTPATHCOMMAND_H_

#include "conf/ConfigManager.h"
#include "server/zone/ZoneServer.h"
#include "server/zone/objects/creature/CreatureObject.h"
#include "server/zone/objects/creature/commands/QueueCommand.h"
#include "server/login/account/AccountManager.h"
#include "server/zone/managers/collision/CollisionManager.h"
#include "server/zone/managers/collision/PathFinderManager.h"
#include "server/zone/objects/cell/CellObject.h"

/*
 * Sandbox helper for the agent client (headless bot): it has no terrain or navmeshes,
 * so it asks the server, which plans with the same PathFinderManager the NPCs use.
 *
 *   /agentpath path <x> <y> [<z> <cellId>]   route from our position; x/y/z are cell-local
 *                                             when a cell is given, world coordinates otherwise
 *   /agentpath height <x> <y>                 ground height at a world position
 *
 * The answer is a system message "[agentpath] {json}" sent only to the caller.
 * Only accounts listed in Core3.AgentAccounts (config-local.lua) may use it.
 */
class AgentPathCommand : public QueueCommand {
public:
	AgentPathCommand(const String& name, ZoneProcessServer* server) : QueueCommand(name, server) {
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

		Zone* zone = creature->getZone();

		if (zone == nullptr)
			return GENERALERROR;

		JSONSerializationType reply;

		try {
			StringTokenizer args(arguments.toString());
			String mode;
			args.getStringToken(mode);
			float x = args.getFloatToken();
			float y = args.getFloatToken();

			if (mode == "height") {
				reply = {{"mode", "height"}, {"x", x}, {"y", y},
						 {"z", CollisionManager::getWorldFloorCollision(x, y, zone, false)}};
			} else if (mode == "path") {
				reply = findPath(creature, zone, x, y, args);
			} else {
				return INVALIDPARAMETERS;
			}
		} catch (const Exception& e) {
			reply = {{"ok", false}, {"error", "usage: path x y [z cellId] | height x y"}};
		}

		creature->sendSystemMessage("[agentpath] " + String(reply.dump().c_str()));

		return SUCCESS;
	}

	JSONSerializationType findPath(CreatureObject* creature, Zone* zone, float x, float y, StringTokenizer& args) const {
		CellObject* cell = nullptr;
		float z = 0;

		if (args.hasMoreTokens()) {
			z = args.getFloatToken();
			uint64 cellID = args.getLongToken();
			ManagedReference<SceneObject*> object = server->getZoneServer()->getObject(cellID);

			if (object == nullptr || !object->isCellObject())
				return {{"mode", "path"}, {"ok", false}, {"error", "unknown cell"}};

			cell = object.castTo<CellObject*>();
		} else {
			z = CollisionManager::getWorldFloorCollision(x, y, zone, false);
		}

		WorldCoordinates start(creature);
		WorldCoordinates end(Vector3(x, y, z), cell);

		if (start.getWorldPosition().distanceTo(end.getWorldPosition()) > 2048)
			return {{"mode", "path"}, {"ok", false}, {"error", "destination more than 2 km away"}};

		Vector<WorldCoordinates>* path = PathFinderManager::instance()->findPath(start, end, zone);
		bool partial = false;

		// Leaving a building for a far destination can fail on the outdoor leg; head for a point
		// part of the way there instead and let the client re-plan from outside.
		if ((path == nullptr || path->size() == 0) && start.getCell() != nullptr && cell == nullptr) {
			Vector3 from = start.getWorldPosition(), to = end.getWorldPosition();
			Vector3 direction = to - from;
			float length = direction.length();

			for (float step : {32.f, 64.f, 128.f}) {
				if (step >= length)
					break;

				delete path;
				float px = from.getX() + direction.getX() * step / length, py = from.getY() + direction.getY() * step / length;
				WorldCoordinates waypoint(Vector3(px, py, CollisionManager::getWorldFloorCollision(px, py, zone, false)), nullptr);
				path = PathFinderManager::instance()->findPath(start, waypoint, zone);

				if (path != nullptr && path->size() > 0) {
					partial = true;
					break;
				}
			}
		}

		if (path == nullptr || path->size() == 0) {
			delete path;
			return {{"mode", "path"}, {"ok", false}, {"error", "no path"}};
		}

		// [x, y, z, cell]: cell-local coordinates inside buildings, world coordinates outside.
		// Long outdoor legs get extra points every 8 m with the ground height, so the client
		// can follow the terrain.
		JSONSerializationType points = JSONSerializationType::array();
		const WorldCoordinates* previous = nullptr;

		for (int i = 0; i < path->size() && points.size() < 256; ++i) {
			const WorldCoordinates& point = path->get(i);
			CellObject* pointCell = point.getCell();

			if (pointCell == nullptr && previous != nullptr && previous->getCell() == nullptr) {
				float dx = point.getX() - previous->getX(), dy = point.getY() - previous->getY();
				int steps = (int) (Math::sqrt(dx * dx + dy * dy) / 8.f);

				for (int s = 1; s < steps; ++s) {
					float px = previous->getX() + dx * s / steps, py = previous->getY() + dy * s / steps;
					points.push_back({px, py, CollisionManager::getWorldFloorCollision(px, py, zone, false), 0});
				}
			}

			points.push_back({point.getX(), point.getY(), point.getZ(), pointCell != nullptr ? pointCell->getObjectID() : 0});
			previous = &point;
		}

		delete path;

		return {{"mode", "path"}, {"ok", true}, {"partial", partial}, {"points", points}};
	}
};

#endif // AGENTPATHCOMMAND_H_
