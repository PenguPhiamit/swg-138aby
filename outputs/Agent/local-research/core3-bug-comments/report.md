# Core3 Bug Comments Report: Player-Noticeable Issues

## 1. Short Answer

The Core3 source contains 283 developer comments admitting bugs, gaps, or incomplete work. Many are code-tidying notes (TODOs about refactoring, logging, or cleanup) that players would never see. The player-visible issues cluster in **space travel** (multiple ship-related client crashes during hyperspace and zone transitions), **SUI interfaces** (listbox and chat room creation crashes), **combat balance** (unimplemented TanO vs TanO damage, unknown unskilled penalties), **city building exploits** (decorations blocking POI entrances), and **sandbox tools** (item creation crashes). The most critical bugs for pre-CU players are the space-related crashes that break hyperspace travel and ship boarding, followed by the city decoration path-blocking exploit and broken Hoth vehicle reward deeds.

## 2. How It Works: Conditions, Numbers, Timings, and Player Messages

### Space/Crash Bugs (Most Critical)

**Conditions:** Ship zone transitions, hyperspace travel, pilot boarding, and object creation during async scene initialization.

**What the code says is wrong:**
- `src/server/zone/objects/ship/PobShipObjectImplementation.cpp:586` — Objects are still in the old zone when sends occur between zones, crashing the client.
- `src/server/zone/objects/ship/PobShipObjectImplementation.cpp:593` — Premature creates before zone switch crashes the client; inter-player sends affected.
- `src/server/zone/objects/ship/PobShipObjectImplementation.cpp:774` — Ship destruction causes client crash; only COV setup and reverse sends work below this point.
- `src/server/zone/objects/ship/PobShipObjectImplementation.cpp:811` — Duplicate object creation crashes the client; only `sendToOwner(forceLoad=true)` should be used.
- `src/server/zone/objects/ship/PobShipObjectImplementation.cpp:864` — `notifyInsert` on a creature in the octree crashes the client.
- `src/server/zone/objects/ship/PobShipObjectImplementation.cpp:865` — Sending via `player->sendTo` also crashes due to container/slotted chain issues.
- `src/server/zone/objects/ship/PobShipObjectImplementation.cpp:962` — Duplicate create crashes the client.
- `src/server/zone/objects/ship/components/ShipStationContainerComponent.cpp:113` — Container sends crash the client during hyperspace.
- `src/server/zone/objects/ship/components/ShipStationContainerComponent.h:8` — Sends regardless of `notifyClient` cause client crashes during hyperspace because...
- `src/server/zone/objects/ship/events/HyperspaceToLocationTask.h:138` — Frame as CmdStartScene; the client may crash due to async scene initialization.
- `src/server/zone/objects/ship/events/InsertPilotIntoShipTask.h:62` — Must send cell permissions prior to player inserting or it will crash the client.

**How a player would see it (inferred):** Players experience client crashes when hyperspacing, boarding ships, or when ships transition between zones. The game becomes unresponsive or closes unexpectedly during space travel and ship interactions.

### City Decoration Path-Blocking Exploit

**Conditions:** Placing city decorations near POI area entrances/exits.

**What the code says is wrong:**
- `src/server/zone/managers/city/CityDecorationTask.h:85` — "We don't want players to exploit-block entrances or exits to POI areas & buildings."

**How a player would see it (inferred):** Players can place decorations that block access to points of interest, preventing other players from entering or exiting those areas. This is an unintended exploit.

### Combat Balance Issues

**Conditions:** Tank vs tank combat and unskilled player combat.

**What the code says is wrong:**
- `src/server/zone/managers/combat/CombatManager.cpp:584` — "Implement TanO vs TanO damage -- This currently has no use."
- `src/server/zone/managers/combat/CombatManager.cpp:1980` — "unskilled penalty, TODO: this might be -50 or -125, do research"

**How a player would see it (inferred):** Tank vs tank combat does not function properly. Unskilled players may have incorrect or missing combat penalties, affecting game balance.

### Slicing Lock Bug

**Conditions:** Player attempts to slice an object that was previously sliced.

**What the code says is wrong:**
- `src/server/zone/objects/player/sessions/SlicingSessionImplementation.cpp:798` — "This will reactivate the 'broken' lock. (1 Hour)"

**How a player would see it (inferred):** Slicing locks do not work correctly; players may be unable to slice objects that should be available, or the 1-hour cooldown may not function as intended.

### Login API Issues

**Conditions:** Player login attempts and admin connections.

**What the code says is wrong:**
- `src/server/login/SWGRealmsAPI.cpp:163` — "API cleanly instead of crashing init - admin will see a clear error and..."
- `src/server/login/SWGRealmsAPI.cpp:605` — "class as the URI bug, but at every login attempt)."

**How a player would see it (inferred):** Players may experience login failures or errors during authentication. Admins see crashes when connecting.

### SUI Interface Crashes

**Conditions:** Using SUI listboxes and creating chat rooms.

**What the code says is wrong:**
- `src/server/zone/objects/player/sui/listbox/SuiListBoxImplementation.cpp:27` — "This crashes the client, but is what makes the third button..."
- `src/server/zone/packets/chat/ChatOnCreateRoom.h:78` — "Error Code (override to stop error spam due to autojoin client bug)"

**How a player would see it (inferred):** Client crashes when using certain SUI listbox interfaces. Error messages spam when creating chat rooms due to an autojoin client bug.

### Tutorial Building Destruction Crash

**Conditions:** Admins teleporting into tutorial buildings that are subsequently destroyed.

**What the code says is wrong:**
- `bin/scripts/screenplays/tutorial/tutorial.lua:82` — "In case any admins had teleported in, as any players in the building when it is destroyed will get a client crash"

**How a player would see it (inferred):** Players inside tutorial buildings when they are destroyed experience client crashes.

### Sandbox Tools Datapad Crash

**Conditions:** Using sandbox tools to create items from draft schematics.

**What the code says is wrong:**
- `bin/scripts/screenplays/sandbox/sandbox_tools_datapad.lua:412` — "inventory item, and the client crashes building it (no client constructor for object/draft_schematic/*). From the..."
- `bin/scripts/object/sandbox/tools_datapad.lua:25` — "The terminal gives every entry as an item, and a draft schematic as an item crashes the client (15 Oct: the MTG..."

**How a player would see it (inferred):** Players crash when using sandbox tools to create items that are draft schematics. The client lacks a constructor for these object types.

### Hoth Vehicle Deed Bugs

**Conditions:** Receiving vehicle deeds as Hoth quest rewards.

**What the code says is wrong:**
- `bin/scripts/loot/items/hoth/hoth_vehicle_barc_speeder_imperial_deed.lua:1` — "Hoth reward (owner, 17 Oct 2026: swap the broken swamp_speeder_deed for a working deed; Documentation-support/vehicles-render-17oct.md)"
- `bin/scripts/loot/items/hoth/hoth_vehicle_barc_speeder_rebel_deed.lua:1` — "Hoth reward (owner, 17 Oct 2026: swap the broken landspeeder_xp38_deed for a working deed; Documentation-support/vehicles-render-17oct.md)"
- `bin/scripts/loot/items/hoth/hoth_vehicle_landspeeder_tantive4_deed.lua:1` — "Hoth reward (owner, 17 Oct 2026: swap the broken mechno_chair_deed for a working deed; Documentation-support/vehicles-render-17oct.md)"

**How a player would see it (inferred):** Players receive non-functional vehicle deeds as quest rewards. The deeds do not work properly and need to be swapped for working versions.

### Vendor Item Exploit

**Conditions:** Player interactions with vendor objects, particularly when driven straight at the object.

**What the code says is wrong:**
- `src/server/zone/objects/tangible/components/vendor/VendorDataComponent.h:49` — "a sanctioned removal from one driven straight at the object (exploit, stray command)."

**How a player would see it (inferred):** Players can exploit vendor interactions by driving directly at vendor objects, potentially triggering unintended item removal or commands.

## 3. What a Bot Test Should Check

### Space Travel Crashes
- **Setup:** Player character in a ship, initiate hyperspace travel, board/unboard ships, zone transition scenarios.
- **Observable results:** Client remains responsive (no crash), ship appears correctly in new zone, no duplicate objects visible, pilot insertion succeeds without errors.
- **Check:** Monitor for client disconnects during hyperspace, verify ship state after zone transitions, confirm no duplicate ship instances.

### City Decoration Path Blocking
- **Setup:** Place city decorations near POI entrances/exits.
- **Observable results:** NPCs and players can still access the POI area, pathfinding works correctly around decorations.
- **Check:** Verify NPC pathing to POIs is not blocked by player-placed decorations.

### Combat Balance
- **Setup:** Tank vs tank combat scenarios, unskilled player combat encounters.
- **Observable results:** TanO vs TanO damage calculations occur, unskilled players receive appropriate combat penalties.
- **Check:** Verify damage numbers for tank combat, confirm skill modifiers apply to unskilled players.

### Slicing Locks
- **Setup:** Attempt to slice an object with an active lock, wait for lock expiration.
- **Observable results:** Lock duration functions correctly (1 hour), slicing succeeds after lock expires.
- **Check:** Monitor lock timer accuracy, verify slicing success/failure messages.

### Login Issues
- **Setup:** Multiple login attempts, admin connection scenarios.
- **Observable results:** Login completes without crashes, clear error messages displayed on failure.
- **Check:** Verify login API responses, monitor for crash reports during authentication.

### SUI Interface Stability
- **Setup:** Open SUI listboxes, create chat rooms.
- **Observable results:** Interfaces remain responsive, no client crashes, error spam stopped.
- **Check:** Monitor for client stability during SUI interactions, verify chat room creation succeeds without excessive errors.

### Tutorial Building Destruction
- **Setup:** Place player in tutorial building, trigger building destruction.
- **Observable results:** Player survives without client crash, receives appropriate survival message.
- **Check:** Verify player state after building destruction, confirm no crash occurs.

### Sandbox Tools
- **Setup:** Use sandbox tools datapad to create items from draft schematics.
- **Observable results:** Items created successfully, no client crash, item appears in inventory.
- **Check:** Verify item creation success, monitor for crash reports during sandbox tool usage.

### Hoth Vehicle Deeds
- **Setup:** Complete Hoth quest to receive vehicle deed reward.
- **Observable results:** Deed functions correctly, vehicle can be spawned/used as intended.
- **Check:** Verify deed activation, confirm vehicle spawn and functionality.

## 4. Likely Reasons a Test Sees No Effect

1. **Crash bugs require specific triggers:** Space crashes occur during hyperspace or zone transitions; tests may not reach these states if ship travel is not properly initiated.

2. **Exploits need precise conditions:** City decoration path blocking requires decorations placed at exact coordinates near POI entrances; random placement may not trigger the exploit.

3. **Combat balance issues are subtle:** Unskilled combat penalties and TanO damage may produce small numerical differences that tests do not check for explicitly.

4. **Slicing locks have time dependencies:** The 1-hour lock duration means tests cannot verify expiration without waiting or fast-forwarding time.

5. **Login bugs depend on server state:** URI bugs and API crashes may only occur under specific authentication conditions or with certain account states.

6. **SUI crashes require specific UI interactions:** Listbox crashes may only happen with particular item counts or interface configurations that tests do not replicate.

7. **Tutorial crashes need admin presence:** The tutorial building crash only affects players who were teleported in by admins; normal player login does not trigger it.

8. **Sandbox tools crash on specific item types:** Only draft schematic items cause crashes; tests using other item types will not see the issue.

9. **Hoth deeds may appear functional but be broken:** Deeds might spawn vehicles that do not work correctly, requiring extended testing to verify full functionality.

10. **Vendor exploits need precise positioning:** Driving straight at vendor objects requires exact coordinates and angles that tests may not replicate.

## 5. Open Questions

1. **What is the correct unskilled combat penalty value?** `CombatManager.cpp:1980` states it "might be -50 or -125" but does not specify which. Missing research document or live server data needed.

2. **How does TanO vs TanO damage work on live SWG?** `CombatManager.cpp:584` notes this feature has no use, but does not describe the intended mechanics. Missing design document or live server reference.

3. **What is the exact URI bug in login?** `SWGRealmsAPI.cpp:605` references "the URI bug" without details. Missing context about which URI class or endpoint is affected.

4. **Which SUI listbox triggers the crash?** `SuiListBoxImplementation.cpp:27` mentions a specific third button but does not identify which interface or condition causes the crash. Missing test case documentation.

5. **What are the exact coordinates for city decoration path blocking?** `CityDecorationTask.h:85` warns about the exploit but does not specify which POI entrances/exits are vulnerable. Missing map data or coordinate list.

6. **How do Hoth vehicle deeds fail?** The deed files reference swapping broken deeds for working ones but do not describe the specific failure mode. Missing error messages or crash logs from affected players.

7. **What is the "class as the URI bug" in login?** `SWGRealmsAPI.cpp:605` references this without explanation. Missing class name or URI endpoint specification.

8. **Which objects trigger slicing lock issues?** `SlicingSessionImplementation.cpp:798` mentions a "broken" lock but does not specify which object types or conditions cause it. Missing object type list or scenario documentation.

9. **What is the correct path for chat room creation?** `ChatManagerImplementation.cpp:466-473` references broken paths in chat rooms but does not specify what constitutes a valid path. Missing chat room structure documentation.

10. **How does async scene initialization cause crashes?** `HyperspaceToLocationTask.h:138` and `SpaceZoneComponent.cpp:272` reference async initialization issues but do not describe the timing or conditions that trigger them. Missing synchronization mechanism documentation.

## Claude's review (18 Oct 2:54 AM)

**Not usable as a bug list.** The model read comments that *explain a guard already in the code* as open bugs, and it read our own fix notes as bugs. Checked in Core3-dev:

- **The space "crashes" are guards.**
  - PobShipObjectImplementation.cpp:583-595 skips sends during hyperspace *because* they would crash the client.
  - InsertPilotIntoShipTask.h:62 sends cell permissions first for the same reason.
  - SuiListBoxImplementation.cpp:27 sits on code that is commented out.
- **The city "exploit" is the check that prevents it.** CityDecorationTask.h:85 refuses with `@player_structure:not_permitted`.
- **Workarounds or intended behaviour, not bugs:**
  - tutorial.lua:82 is the comment on `clearPlayers`, which removes players before the building is destroyed.
  - SlicingSessionImplementation.cpp:798 is the intended relock after the lock time.
  - VendorDataComponent.h:49 describes a guard against unsanctioned vendor removal.
- **Our own fix notes, read as bugs:** the "Hoth vehicle deed bugs" and the "sandbox tools crash" are notes on fixes we already made (17 Oct deed swap; schematics not given as items).
- **Not our server:** `SWGRealmsAPI.cpp` is the official servers' account service.
- **"TanO vs TanO" is not "tank vs tank".** It means object-on-object damage (CombatManager.cpp:584), which has no player use.

**The one real lead:** an unskilled attacker's accuracy is -15, with the comment "might be -50 or -125, do research" (CombatManager.cpp:1980). That is a pre-CU balance question for GPT's known-bugs research (C64).

**For a rerun:** give the model each comment with about 10 lines of code around it, and ask "does the code around it already handle this?" A bare comment can't answer that. Public bug reports (C64) and our own bot findings are better sources of real bugs.
