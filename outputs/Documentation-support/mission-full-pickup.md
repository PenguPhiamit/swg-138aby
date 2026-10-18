# Mission pickup into a full inventory: stuck mission (staged fix)

Claude (missions side session), 17 Oct 2026. Bug 2 of `functional-test-plan.md` section 11. **Staged, not installed, unbuilt.** The main session builds it with the next restart batch.

- Patch: [`mission-full-pickup.patch`](mission-full-pickup.patch), made against Core3-dev `4b113bb7`. `git apply --check` is clean there and on the newer head `1be13676`. It changes three files:
  - `DeliverMissionObjectiveImplementation.cpp` (`updateMissionStatus`);
  - `CraftingMissionObjectiveImplementation.cpp` (`updateMissionStatus`);
  - `DeliverMissionScreenHandler.cpp` (`handleScreen`).
- Compile: each patched file passes a syntax-only compile (`-fsyntax-only`, with the flags from `build/dev/compile_commands.json`, at nice 19). Nothing was written to the build tree.
- Checks:
  - Offline: `python -I tools/bots/test_missions.py` (44 tests, OK). `test_a_full_pickup_is_kept_and_finished_with_the_pickup_patch` and `test_a_full_pickup_is_stuck_on_stock_core3` run the fake galaxy both ways.
  - In game, after the build: `missions.py` `full_pickup()`, check "a full inventory is told and keeps the pickup". It runs only when `M.PICKUP_FIX` is True (see below).

## The bug

When a player talks to a deliver mission's pickup NPC, `DeliverMissionScreenHandler` calls `updateMissionStatus`, then always shows the pickup line (`m<N>p`).

- In `updateMissionStatus`, if the datadisk does not fit in the inventory, `transferObject` fails and the objective calls `abort()`.
  - `abort()` despawns both NPCs. It does not remove the mission, which stays in the datapad.
  - The player gets no message, and the waypoint stays on the pickup spot, where there's now no NPC.
  - The mission can't be finished. It sits in the datapad until it expires, and it counts toward the mission cap.
- A crafting mission's pickup does the same with its schematic parts (`CraftingMissionObjectiveImplementation::updateMissionStatus`). By then it has already granted the schematic, and some parts may already be in the inventory.

## Evidence (test galaxy)

Run of `cresh-missions.py` on 17 Oct at 5:38 AM, report `Bot-reports/Cresh/20261017-053833-cresh-missions.json`:

- Cresh accepted "@mission/mission_deliver_neutral_easy:m3t" (reward 70), mission `281474994540511`, at t = 54.5 s. His inventory was full: 80 of 80 items, mostly spare /agentgear kits.
- The NPC was at the waypoint, and its line was the pickup line `@mission/mission_deliver_neutral_easy:m3p`. But:
  - "the pickup hands something over" failed: nothing new in the inventory;
  - "the waypoint moves to the destination" failed: it stayed at (3293.1, -4651.7).
- The mission was still in the datapad afterwards.
- Since then, `take()` refuses to give a carry mission to a bot with fewer than 3 free slots.

## The fix

- **Deliver.** Before the datadisk is created, an inventory that is full (`isContainerFullRecursive`, the server's usual test) or missing makes the pickup stop:
  - the player gets `@error_message:inv_full` ("Your inventory is full.");
  - the objective stays in INITSTATUS, and both NPCs and the waypoint stay.
  
  If the transfer fails anyway, the datadisk is destroyed and the same message is sent, with no `abort()`. The player makes room and talks to the NPC again.
- **Crafting.** Before the schematic is granted, the inventory needs room for one part per draft slot (`getCountableObjectsRecursive() + getDraftSlotCount() > getContainerVolumeLimit()`, as `FishObjectImplementation` counts). If it doesn't have room, the player gets the same message and the objective stays in INITSTATUS. Nothing is granted or handed out.
- **Conversation.** If the objective is still in INITSTATUS after `updateMissionStatus`, the NPC says `@error_message:inv_full` instead of the pickup line.

Limits:

- In the crafting objective, a part that still fails to transfer halfway through the loop keeps stock's `abort()`. With the room check first, only an odd container failure can reach it.
- The other early returns in `updateMissionStatus` also leave INITSTATUS, so the NPC says "inventory full" for them too. Those are a missing mission or schematic, which never happens in normal play.
- A mission that is already stuck (aborted before this build) stays stuck: its NPCs are gone. It expires on its own.

## How to check it after the build

1. Set `PICKUP_FIX = True` in `tools/bots/missions.py`, in the same commit that records the build.
2. In `cresh-missions.py` (deliver) and `besh-missions.py` (crafting), a carrier with a full inventory now takes the mission (`take(full_ok=M.PICKUP_FIX)`). `errand()` then:
   - checks "a full inventory is told and keeps the pickup": `inv_full` heard, the mission still held, the waypoint still on the pickup NPC;
   - destroys up to three spare items (medicine first, else a duplicated plain item; never a mission item);
   - talks to the NPC again ("pickup again"), and the delivery runs to the end as usual.
3. Unpatched, the first check fails and "pickup again: an NPC stands at the waypoint" fails, because the NPCs despawned. That's why `PICKUP_FIX` stays False until the build: on stock Core3 the check would leave the bot a stuck mission.
