/*
				Copyright <SWGEmu>
		See file COPYING for copying conditions.*/

#ifndef LEASHCOMMAND_H_
#define LEASHCOMMAND_H_

#include "conf/ConfigManager.h"
#include "server/zone/ZoneServer.h"
#include "server/zone/objects/creature/CreatureObject.h"
#include "server/zone/objects/creature/commands/QueueCommand.h"
#include "server/zone/objects/building/BuildingObject.h"
#include "server/zone/objects/cell/CellObject.h"
#include "server/zone/objects/player/PlayerObject.h"
#include "server/zone/managers/collision/CollisionManager.h"
#include "server/zone/managers/collision/PathFinderManager.h"
#include "server/zone/managers/player/PlayerManager.h"

#include <memory>

/*
 * Sandbox: a follow assist for group members.
 *
 * The client's own /follow steers in a straight line and never tells the server, so it gets stuck
 * on corners and doorways. While a leash is on, the server checks every 2 s: when the follower is
 * more than STUCK_RANGE metres from the leader and has not closed the gap for STUCK_CHECKS checks
 * in a row, it moves the follower to a walkable point a few metres behind the leader (taken from a
 * navmesh path). Otherwise it does nothing and the client's follow keeps steering.
 *
 * It only ever moves the follower along a navmesh route (never across walls or cliffs), and not at all when
 * the route ends where they already are.
 * Start/stop: right-click a group member → "Leash (follow assist)" / "Stop leash", or
 * /leash [name|target] and /leash off. Group members only; never while in combat, dead,
 * incapacitated or mounted; never into a building the follower may not enter. It ends when they
 * leave the group, change planet, drift more than MAX_RANGE apart or log out.
 * Core3.LeashEnabled = false (config-local.lua) turns the feature off.
 */
class LeashTask : public Task {
	ManagedWeakReference<CreatureObject*> followerRef, leaderRef;
	uint64 leaderID;
	float lastDistance = -1;
	int stuckChecks = 0;
	bool warned = false; // told the follower that moving wouldn't help; reset once they're close again

public:
	static const int INTERVAL = 2000;
	static const int STUCK_CHECKS = 3;
	constexpr static float STUCK_RANGE = 10.f;
	constexpr static float MAX_RANGE = 512.f;
	constexpr static float BEHIND = 3.f; // where an unstick puts the follower: this far short of the leader

	LeashTask(CreatureObject* follower, CreatureObject* leader) : followerRef(follower), leaderRef(leader), leaderID(leader->getObjectID()) {
	}

	uint64 getLeaderID() const {
		return leaderID;
	}

	void run() {
		ManagedReference<CreatureObject*> follower = followerRef.get();

		if (follower == nullptr)
			return;

		Locker locker(follower);

		if (follower->getPendingTask("leash") != this)
			return; // stopped or replaced meanwhile

		PlayerObject* ghost = follower->getPlayerObject();

		if (ghost == nullptr || !ghost->isOnline()) {
			follower->removePendingTask("leash");
			return;
		}

		ManagedReference<CreatureObject*> leader = leaderRef.get();

		if (leader == nullptr || leader == follower) {
			stop(follower, "no leader");
			return;
		}

		// Every check below and the move itself use one consistent view of both characters: the leader can't
		// change planet, cell or group between them. Cross-locking (follower held, then leader) is the engine's
		// deadlock-safe pattern, so two players leashed to each other can't deadlock.
		Locker clocker(leader, follower);

		String reason = checkPair(follower, leader);

		if (!reason.isEmpty()) {
			stop(follower, reason);
			return;
		}

		float distance = follower->getWorldPosition().distanceTo(leader->getWorldPosition());

		if (distance > MAX_RANGE) {
			stop(follower, "you are too far from " + leader->getFirstName());
			return;
		}

		bool busy = follower->isInCombat() || follower->isDead() || follower->isIncapacitated() || follower->isRidingMount() ||
					leader->isRidingMount();

		if (distance <= STUCK_RANGE)
			warned = false;

		if (busy || distance <= STUCK_RANGE)
			stuckChecks = 0;
		else if (lastDistance >= 0 && distance > lastDistance - 0.5f)
			++stuckChecks;
		else
			stuckChecks = 0;

		lastDistance = distance;

		if (stuckChecks >= STUCK_CHECKS) {
			stuckChecks = 0;
			lastDistance = -1;
			unstick(follower, leader);
		}

		reschedule(INTERVAL);
	}

	// Why the pair can't be leashed, or empty when it can. Both locked (or the follower, from the command).
	static String checkPair(CreatureObject* follower, CreatureObject* leader) {
		if (leader == nullptr || leader == follower || !leader->isPlayerCreature())
			return "no leader";

		PlayerObject* leaderGhost = leader->getPlayerObject();

		if (leaderGhost == nullptr || !leaderGhost->isOnline())
			return leader->getFirstName() + " is offline";

		if (follower->getGroupID() == 0 || follower->getGroupID() != leader->getGroupID())
			return "you are not in a group with " + leader->getFirstName();

		if (follower->getZone() == nullptr || follower->getZone() != leader->getZone())
			return leader->getFirstName() + " is on another planet";

		return "";
	}

private:
	// Move the follower along a navmesh route toward the leader: to a point BEHIND metres short of them when the
	// route reaches them, otherwise to the route's reachable end. Never off the route (no jumping across walls,
	// cliffs or closed interiors), and not at all when it gains nothing. Both characters locked.
	void unstick(CreatureObject* follower, CreatureObject* leader) {
		Zone* zone = follower->getZone();

		if (zone == nullptr || leader->getZone() != zone)
			return;

		WorldCoordinates start(follower);
		WorldCoordinates goal(leader);
		Vector3 leaderPosition = leader->getWorldPosition();
		Vector3 followerPosition = follower->getWorldPosition();
		std::unique_ptr<Vector<WorldCoordinates>> path(PathFinderManager::instance()->findPath(start, goal, zone));

		if (path == nullptr || path->size() < 2) {
			warn(follower, "Leash: there's no walkable way to " + leader->getFirstName() + " from here.");
			return;
		}

		WorldCoordinates target = path->get(path->size() - 1); // the route's end: the closest reachable point

		if (target.getWorldPosition().distanceTo(leaderPosition) <= BEHIND) {
			// The route reaches the leader. Path points can be far apart, so walk back from the leader to the
			// first point at least BEHIND metres away and stop BEHIND metres short of the leader on that segment.
			for (int i = path->size() - 2; i >= 0; --i) {
				const WorldCoordinates& far = path->get(i);
				const WorldCoordinates& near = path->get(i + 1);

				if (far.getWorldPosition().distanceTo(leaderPosition) < BEHIND)
					continue;

				if (far.getCell() != near.getCell()) {
					target = near; // segment crosses a doorway: don't blend coordinates of two cells
					break;
				}

				Vector3 from = near.getPoint(), to = far.getPoint();
				float length = from.distanceTo(to);
				Vector3 point = length > BEHIND ? from + (to - from) * (BEHIND / length) : to;

				if (far.getCell() == nullptr)
					point.setZ(CollisionManager::getWorldFloorCollision(point.getX(), point.getY(), zone, false));

				target = WorldCoordinates(point, far.getCell());
				break;
			}
		}

		Vector3 targetPosition = target.getWorldPosition();

		// A route that stops short (raised ground, a spot off the mesh) can end where the follower already is:
		// moving them there again would only rubber-band.
		if (targetPosition.distanceTo(followerPosition) < 2.f ||
			targetPosition.distanceTo(leaderPosition) > followerPosition.distanceTo(leaderPosition) - 1.f) {
			warn(follower, "Leash: you're already as close to " + leader->getFirstName() + " as the ground allows; keep following.");
			return;
		}

		ManagedReference<CellObject*> cell = target.getCell(); // held until the move is done

		if (cell != nullptr) {
			ManagedReference<SceneObject*> parent = cell->getParent().get();
			BuildingObject* building = parent != nullptr && parent->isBuildingObject() ? cast<BuildingObject*>(parent.get()) : nullptr;

			if (building != nullptr && !building->isAllowedEntry(follower)) {
				warn(follower, "Leash: " + leader->getFirstName() + " is inside a building you can't enter.");
				return;
			}
		}

		follower->teleport(target.getX(), target.getZ(), target.getY(), cell != nullptr ? cell->getObjectID() : 0);
		follower->sendSystemMessage("Leash: you were stuck, so you've been moved closer to " + leader->getFirstName() + ".");
	}

	void warn(CreatureObject* follower, const String& text) {
		if (!warned)
			follower->sendSystemMessage(text);

		warned = true;
	}

	void stop(CreatureObject* follower, const String& reason) {
		follower->removePendingTask("leash");
		follower->sendSystemMessage("Leash ended: " + reason + ".");
	}
};

class LeashCommand : public QueueCommand {
public:
	LeashCommand(const String& name, ZoneProcessServer* server) : QueueCommand(name, server) {
	}

	int doQueueCommand(CreatureObject* creature, const uint64& target, const UnicodeString& arguments) const {
		if (!creature->isPlayerCreature())
			return GENERALERROR;

		if (!ConfigManager::instance()->getBool("Core3.LeashEnabled", true)) {
			creature->sendSystemMessage("The leash is turned off on this galaxy.");
			return GENERALERROR;
		}

		String args = arguments.toString().trim();
		Reference<Task*> pending = creature->getPendingTask("leash");
		LeashTask* current = dynamic_cast<LeashTask*>(pending.get());

		// Who to leash to: a name, else the target (the right-click menu passes the group member).
		ManagedReference<CreatureObject*> leader;

		if (!args.isEmpty() && args.toLowerCase() != "off") {
			leader = server->getZoneServer()->getPlayerManager()->getPlayer(args);
		} else if (target != 0 && args.isEmpty()) {
			ManagedReference<SceneObject*> object = server->getZoneServer()->getObject(target);

			if (object != nullptr && object->isPlayerCreature())
				leader = object.castTo<CreatureObject*>();
		}

		// "/leash off", "/leash" with nobody chosen, or the menu/target on the current leader again: stop.
		// Naming the current leader keeps it on.
		if (current != nullptr && leader != nullptr && leader->getObjectID() == current->getLeaderID() && !args.isEmpty()) {
			creature->sendSystemMessage("Already leashed to " + leader->getFirstName() + ". /leash off to stop.");
			return SUCCESS;
		}

		if (current != nullptr && (leader == nullptr || leader->getObjectID() == current->getLeaderID())) {
			creature->removePendingTask("leash");
			creature->sendSystemMessage("Leash off.");
			return SUCCESS;
		}

		if (leader == nullptr) {
			creature->sendSystemMessage("Usage: /leash <group member> (or target them), /leash off. Right-click a group member for the same option.");
			return INVALIDPARAMETERS;
		}

		String reason = LeashTask::checkPair(creature, leader);

		if (!reason.isEmpty()) {
			creature->sendSystemMessage("Can't leash: " + reason + ".");
			return GENERALERROR;
		}

		creature->removePendingTask("leash");
		creature->addPendingTask("leash", new LeashTask(creature, leader), LeashTask::INTERVAL);
		creature->sendSystemMessage("Leashed to " + leader->getFirstName() +
			": keep using /follow; if it gets stuck you'll be moved closer. /leash off to stop.");

		return SUCCESS;
	}
};

#endif // LEASHCOMMAND_H_
