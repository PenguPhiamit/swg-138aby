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
#include "server/zone/objects/building/BuildingObject.h"
#include "server/zone/objects/creature/commands/LeashCommand.h"

#include <cmath>
#include <algorithm>
#include <memory>
#include <unordered_map>
#include <vector>

/*
 * Sandbox helper for the agent client (headless bot): it has no terrain or navmeshes,
 * so it asks the server, which plans with the same PathFinderManager the NPCs use.
 *
 *   /agentpath [id:<n>] path <x> <y> [<z> <cellId>]   route from our position; x/y/z are cell-local
 *                                             when a cell is given, world coordinates otherwise
 *   /agentpath height <x> <y>                 ground height at a world position
 *   /agentpath find <x> <y> <radius> <text>   the nearest objects (up to 30) within radius metres whose
 *                                             template, name key or displayed name contains text,
 *                                             including objects inside buildings (with cell + local x/y/z)
 *
 * The answer is a system message "[agentpath] {json}" sent only to the caller. It echoes the
 * request ("request") so the client can tell a late answer from the one it is waiting for.
 * Routes are capped at MAX_POINTS; a capped or detoured route is marked "partial" and the
 * client re-plans from where it ends.
 * Only accounts listed in Core3.AgentAccounts (config-local.lua) may use it.
 */
class AgentPathCommand : public QueueCommand {
public:
	static const int MAX_POINTS = 256;

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
		String requestId;

		try {
			StringTokenizer args(arguments.toString());
			String mode;
			args.getStringToken(mode);

			if (mode.beginsWith("id:")) { // optional request id (agent client); echoed back as "id"
				requestId = mode.subString(3);
				args.getStringToken(mode);
			}
			float x = args.getFloatToken();
			float y = args.getFloatToken();

			if (!std::isfinite(x) || !std::isfinite(y) || fabs(x) > 8192 || fabs(y) > 8192) {
				reply = {{"ok", false}, {"error", "coordinates out of range"}};
			} else if (mode == "height") {
				reply = {{"mode", "height"}, {"ok", true}, {"x", x}, {"y", y},
						 {"z", CollisionManager::getWorldFloorCollision(x, y, zone, false)}};
			} else if (mode == "path") {
				reply = findPath(creature, zone, x, y, args);
			} else if (mode == "find") {
				float radius = args.getFloatToken();
				String text;
				args.getStringToken(text);
				reply = findObjects(zone, x, y, radius, text.toLowerCase());
			} else {
				return INVALIDPARAMETERS;
			}
		} catch (const Exception& e) {
			reply = {{"ok", false}, {"error", "usage: path x y [z cellId] | height x y"}};
		}

		reply["request"] = arguments.toString().toCharArray();

		if (!requestId.isEmpty())
			reply["id"] = requestId.toCharArray();
		creature->sendSystemMessage("[agentpath] " + String(reply.dump().c_str()));

		return SUCCESS;
	}

	// Read-only search of the zone around (x, y); building interiors are read the way Core3's own
	// in-range code reads them (no extra locks, guarded).
	JSONSerializationType findObjects(Zone* zone, float x, float y, float radius, const String& text) const {
		const int MAX_FOUND = 30;
		radius = std::max(1.f, std::min(radius, 3000.f));

		if (text.length() < 3)
			return {{"mode", "find"}, {"ok", false}, {"error", "text needs at least 3 characters"}};

		std::vector<std::pair<float, JSONSerializationType>> hits;
		std::unordered_map<uint64, size_t> seen; // object id -> its entry in hits

		auto consider = [&](SceneObject* object, CellObject* cell, SceneObject* building) {
			if (object == nullptr)
				return;

			SharedObjectTemplate* objectTemplate = object->getObjectTemplate();
			String path = objectTemplate != nullptr ? objectTemplate->getFullTemplateString() : "";
			String key = object->getObjectNameStringIdName();
			String shown = object->getDisplayedName();

			if (!path.toLowerCase().contains(text) && !key.toLowerCase().contains(text) && !shown.toLowerCase().contains(text))
				return;

			Vector3 world = object->getWorldPosition();
			float dx = world.getX() - x, dy = world.getY() - y;
			float distance = std::sqrt(dx * dx + dy * dy);

			if (distance > radius)
				return;

			JSONSerializationType entry = {{"oid", object->getObjectID()}, {"template", path.toCharArray()},
				{"name", shown.toCharArray()}, {"key", key.toCharArray()}, {"x", world.getX()}, {"y", world.getY()},
				{"z", world.getZ()}, {"distance", std::round(distance * 10) / 10}};

			if (cell != nullptr) {
				entry["cell"] = cell->getObjectID();
				entry["local"] = {{"x", object->getPositionX()}, {"y", object->getPositionY()}, {"z", object->getPositionZ()}};
				entry["building"] = building != nullptr ? building->getObjectID() : 0;
			}

			// The zone lists objects inside buildings too; keep one entry each, the one with the cell.
			auto known = seen.find(object->getObjectID());

			if (known != seen.end()) {
				if (cell != nullptr)
					hits[known->second].second = entry;

				return;
			}

			seen[object->getObjectID()] = hits.size();
			hits.push_back({distance, entry});
		};

		SortedVector<TreeEntry*> closeObjects;
		zone->getInRangeObjects(x, 0, y, radius, &closeObjects, true, true);

		for (int i = 0; i < closeObjects.size(); ++i) {
			ManagedReference<SceneObject*> object = static_cast<SceneObject*>(closeObjects.get(i));

			if (object == nullptr)
				continue;

			consider(object, nullptr, nullptr);

			if (!object->isBuildingObject())
				continue;

			try {
				for (int c = 0; c < object->getContainerObjectsSize(); ++c) {
					ManagedReference<SceneObject*> child = object->getContainerObject(c);

					if (child == nullptr || !child->isCellObject())
						continue;

					CellObject* cell = child.castTo<CellObject*>();

					if (!cell->isContainerLoaded())
						continue;

					for (int j = 0; j < cell->getContainerObjectsSize(); ++j) {
						ManagedReference<SceneObject*> inside = cell->getContainerObject(j);
						consider(inside, cell, object);
					}
				}
			} catch (...) {
			}
		}

		std::sort(hits.begin(), hits.end(), [](const auto& a, const auto& b) { return a.first < b.first; });
		JSONSerializationType objects = JSONSerializationType::array();

		for (int i = 0; i < (int) hits.size() && i < MAX_FOUND; ++i)
			objects.push_back(hits[i].second);

		return {{"mode", "find"}, {"ok", true}, {"count", (int) hits.size()}, {"partial", (int) hits.size() > MAX_FOUND},
				{"objects", objects}};
	}

	JSONSerializationType findPath(CreatureObject* creature, Zone* zone, float x, float y, StringTokenizer& args) const {
		CellObject* cell = nullptr;
		float z = 0;

		if (args.hasMoreTokens()) {
			z = args.getFloatToken();
			uint64 cellID = args.getLongToken();
			ManagedReference<SceneObject*> object = server->getZoneServer()->getObject(cellID);

			if (object == nullptr || !object->isCellObject() || !std::isfinite(z))
				return {{"mode", "path"}, {"ok", false}, {"error", "unknown cell"}};

			auto root = object->getRootParent();

			if (root == nullptr || root->getZone() != zone)
				return {{"mode", "path"}, {"ok", false}, {"error", "cell is not in this zone"}};

			cell = object.castTo<CellObject*>();
		} else {
			z = CollisionManager::getWorldFloorCollision(x, y, zone, false);
		}

		WorldCoordinates start(creature);
		WorldCoordinates end(Vector3(x, y, z), cell);

		if (start.getWorldPosition().distanceTo(end.getWorldPosition()) > 2048)
			return {{"mode", "path"}, {"ok", false}, {"error", "destination more than 2 km away"}};

		std::unique_ptr<Vector<WorldCoordinates>> path(PathFinderManager::instance()->findPath(start, end, zone));
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

				float px = from.getX() + direction.getX() * step / length, py = from.getY() + direction.getY() * step / length;
				WorldCoordinates waypoint(Vector3(px, py, CollisionManager::getWorldFloorCollision(px, py, zone, false)), nullptr);
				path.reset(PathFinderManager::instance()->findPath(start, waypoint, zone));

				if (path != nullptr && path->size() > 0) {
					partial = true;
					break;
				}
			}
		}

		if (path == nullptr || path->size() == 0)
			return {{"mode", "path"}, {"ok", false}, {"error", "no path"}};

		// [x, y, z, cell]: cell-local coordinates inside buildings, world coordinates outside.
		// Long outdoor legs get extra points every 8 m with the ground height, so the client can
		// follow the terrain. Every append is checked against MAX_POINTS; when the budget runs out
		// the answer is the continuous prefix so far, marked partial.
		// Each step of the pathfinder's route (from where we stand) checked the way the leash checks it: "ok", or why it
		// isn't proved walkable. The pathfinder fills gaps with straight lines it never checked.
		JSONSerializationType proof = JSONSerializationType::array();

		for (int i = 0; i < path->size(); ++i) {
			String why = LeashTask::whyNotWalkable(i == 0 ? start : path->get(i - 1), path->get(i), zone);
			proof.push_back(why.isEmpty() ? "ok" : why.toCharArray());
		}

		JSONSerializationType points = JSONSerializationType::array();
		auto add = [&points](float px, float py, float pz, uint64 cellID) {
			if ((int) points.size() >= MAX_POINTS)
				return false;
			points.push_back({px, py, pz, cellID});
			return true;
		};
		const WorldCoordinates* previous = nullptr;

		for (int i = 0; i < path->size(); ++i) {
			const WorldCoordinates& point = path->get(i);
			CellObject* pointCell = point.getCell();
			bool full = false;

			if (pointCell == nullptr && previous != nullptr && previous->getCell() == nullptr) {
				float dx = point.getX() - previous->getX(), dy = point.getY() - previous->getY();
				int steps = (int) (Math::sqrt(dx * dx + dy * dy) / 8.f);

				for (int s = 1; s < steps && !full; ++s) {
					float px = previous->getX() + dx * s / steps, py = previous->getY() + dy * s / steps;
					full = !add(px, py, CollisionManager::getWorldFloorCollision(px, py, zone, false), 0);
				}
			}

			if (full || !add(point.getX(), point.getY(), point.getZ(), pointCell != nullptr ? pointCell->getObjectID() : 0)) {
				partial = true;
				break;
			}

			previous = &point;
		}

		return {{"mode", "path"}, {"ok", true}, {"partial", partial}, {"points", points}, {"proof", proof}};
	}
};

#endif // AGENTPATHCOMMAND_H_
