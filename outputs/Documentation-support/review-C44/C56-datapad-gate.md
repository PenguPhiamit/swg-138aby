# C56: refuse a mission when the datapad is full

16 Oct, 10:05 PM. Claude (side session, taking over GPT's queued task; review C44 row "Full datapad"). Patch: `C56-datapad-gate.patch`, against Core3-dev `8edfd13f`. **Untested in game**: the patch applies and compiles; the main session builds and tests it.

## Cause

`MissionManagerImplementation::handleMissionAccept` (`MissionManagerImplementation.cpp:294`) calls `datapad->transferObject(mission, -1, true)`, ignores the result, and goes on to `createMissionObjectives`.

It is worse than an ignored return value. `ContainerComponent::transferObject` (`scene/components/ContainerComponent.cpp`, the `containmentType == -1` branch) does these steps in this order:

1. It removes the mission from its old parent, the mission bag (`objParent->removeObject(object, sceneObject, false, false)`). The client isn't told, and the parent pointer is kept.
2. Only then does it check `containerObjects->size() >= getContainerVolumeLimit()` and return false.

So with a full datapad (volume limit 100, `bin/scripts/object/tangible/datapad/objects.lua:62`, which pets, vehicles and other contents share), the mission ends up in neither container. Its objective is still created and activated: for a destroy mission, a waypoint, a spawn area and later a lair. The player can't see the mission or abort it, and nothing cleans it up.

The other refusal paths (too many missions, expired bounty) return before the transfer and are fine. The bounty path claims the bounty (`addBountyHunterToPlayerBounty`) before the transfer, so a failed transfer also left a stale hunter on the bounty.

## Fix

```diff
-	if (mission->getParent().get() == datapad)
+	if (datapad == nullptr || mission->getParent().get() == datapad)
 		return;
 ...
+	// C56: a full datapad refuses the mission before anything is claimed or created. ...
+	if (datapad->getContainerObjectsSize() >= datapad->getContainerVolumeLimit()) {
+		StringIdChatParameter stringId("mission/mission_generic", "datapad_full"); // Your datapad is full. You must first free some space.
+		player->sendSystemMessage(stringId);
+		return;
+	}
 ...
-	datapad->transferObject(mission, -1, true);
+	if (!datapad->transferObject(mission, -1, true)) {
+		// Refused for another reason: back on the terminal's list (the client was not told it left), the bounty claim
+		// undone without the abort cooldown, and no objective.
+		if (!missionBag->hasObjectInContainer(mission->getObjectID()))
+			missionBag->transferObject(mission, -1, false, true);
+
+		if (mission->getTypeCRC() == MissionTypes::BOUNTY && mission->getTargetObjectId() != 0) {
+			Locker listLocker(&playerBountyListMutex);
+
+			PlayerBounty* bounty = playerBountyList.get(mission->getTargetObjectId());
+
+			if (bounty != nullptr)
+				bounty->removeBountyHunter(player->getObjectID());
+		}
+
+		StringIdChatParameter stringId("mission/mission_generic", "datapad_full");
+		player->sendSystemMessage(stringId);
+		return;
+	}
```

The full diff is in `C56-datapad-gate.patch`.

- **The capacity check comes first.** It sits after the too-many-missions check and before the bounty claim, so a refused mission claims nothing and creates nothing: no objective, waypoint, spawn area, lair or expiry task. The mission stays in the mission bag, so it is still on the terminal's list.
- **The message is the stock mission string.** `mission/mission_generic:datapad_full` reads "Your datapad is full.  You must first free some space." (read from the client's `string/en/mission/mission_generic.stf`). Taming and pet deeds use the same text from `faction_recruiter`.
- **The transfer result is checked as a backstop** for any other refusal (`canBeTransferred`). The mission goes back into the bag with overflow allowed. The bounty hunter is removed directly, not through `removeBountyHunterFromPlayerBounty`, which would add the abort cooldown for a mission never taken. Nothing is created.
- **A null datapad now returns** instead of crashing.

## Other mission paths checked

| Path | Result |
|---|---|
| `handleMissionListRequest`, mission bag fill loop (`:222-227`) | Also ignores `transferObject`, and the `while` loop would spin if a transfer failed. Not reachable: the bag's limit is 100 (`mission_bag/objects.lua:62`) and the loop fills at most 36 (12 + 6 + 6 + 12 with every factional option on). Left alone. |
| Crafting and deliver objectives (`CraftingMissionObjectiveImplementation.cpp:84`, `DeliverMissionObjectiveImplementation.cpp:198`) | Already check the inventory transfer. |
| Destroy, recon and entertainer objectives | Transfer into the zone, which has no volume limit. |
| BotPop (`BotPopLaunchBrain.h:2011`) | Already checks that the mission's parent is the datapad after accepting, and retries in 10 minutes. It now also gets the message. |
| `MissionAcceptCallback.h:79` | Always sends MissionAcceptResponse with success `0x01`, even for refusals (stock, and true for too-many-missions too). Not changed: what the real client does with `0x00` is unverified. Possible follow-up, tested with the real client. |

## Checks run (inside WSL, read-only)

- `git apply --check` in `/opt/swg/Core3-dev`: clean.
- Syntax-only compile of the patched `MissionManagerImplementation.cpp` with its `build/dev/compile_commands.json` flags (clang++ 19, `-fsyntax-only`): exit 0.
- A copy with an `#error` line failed, which proves the patched file was the one compiled.

## In-game test (main session, test galaxy)

1. **Six, then a seventh.** With a near-empty datapad, accept six missions: all six are taken. The seventh gets "You cannot accept any more missions." (unchanged path; regression check).
2. **Full datapad.** Filling 100 slots by hand is slow, so lower the character datapad's `containerVolumeLimit` in the test galaxy's script copy (`object/tangible/datapad/objects.lua`, `shared_character_datapad`, line 62) to the number of items it already holds plus one. Restart the test galaxy, accept one mission (fills the last slot), then try another.
   - Expect "Your datapad is full.  You must first free some space."
   - The mission stays offered at the terminal after a list refresh.
   - No new waypoint appears, and no lair appears at its spot.
   - The server log shows no transfer error.
   - Then drop an item from the datapad: the same mission can now be accepted and works.
3. Restore the limit to 100 afterwards. The test-galaxy copy only; never the live scripts.
4. Optional, bounty: with the bounty check on, a refused bounty mission leaves the target's hunter list unchanged (`/server ... bounty` debug or `sendPlayerBountyDebug`).

## Not done

- No build, no in-game test, no agent-client test (overrides for this task).
- The C44 review rows for these lines are in `C44-review.md:102`. This file answers that row.
