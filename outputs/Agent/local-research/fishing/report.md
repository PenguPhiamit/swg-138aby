# Fishing Mechanics Report

## 1. Short Answer

Fishing requires a pole equipped in the right hand and bait loaded into it; the player must stand on land near water (not swimming). A cast lands within a distance determined by pole quality, and if it hits water a bobber marker is created. The session cycles through states—WAITING, SNAGGED, NIBBLE, BITE, CATCH, REELING, REELGAME—each tick of a 7-second event, with random rolls modified by pole quality, bait freshness, vegetation, and fish density deciding whether the player catches a fish or loses the line. The player sees a SUI menu showing status, bait condition, line range, fish density, vegetation, and next action, plus system messages and fly text for state changes. A bot test should equip a pole with bait, stand in water, start fishing, verify the window and state transitions, then confirm inventory gains or loss messages. Tests may fail if fishing is disabled, no pole/bait is equipped, the player is swimming, or the cast lands outside valid water.

## 2. How It Works

### Conditions to Start Fishing
- The player must have a fishing pole in the right-hand slotted object (`hold_r`) (FishingManagerImplementation.cpp:920). If missing, the system sends `@fishing:must_have_pole` and returns (line 160).
- The pole must contain bait; `getBait()` checks the first container slot of the pole (lines 935-956). If missing, the system sends `@fishing:bait_your_pole` and returns (line 167).
- The player must not be swimming (`player->isSwimming()`) (line 177); if swimming, `@fishing:bad_cast` is sent (line 178).
- A location check computes a cast distance based on pole quality: `Math::min((Math::max(fabs(1.0 - (quality / 10.f)), 2.1) + randVal), 10.0)` (line 261). The terrain manager verifies water at the landing point (lines 274-285). If no water is found, `@fishing:too_far` is sent (line 189); if water exists under terrain, `@fishing:invalid_location` is sent (line 192).

### Fishing States
Defined in FishingManager.idl (lines 43-50):
- NOTFISHING = 0, WAITING = 1, SNAGGED = 2, NIBBLE = 3, BITE = 4, CATCH = 5, REELING = 6, REELGAME = 7.

The session begins in WAITING (line 206). Each FishingEvent tick (every 7 seconds, FishingEvent.h:23-26) calls `continueFishing()` which evaluates the current state and rolls a random number (line 406). Key modifiers:
- **Pole quality**: `poleMod = ceil(quality / 10)` (line 412); reduces mishap chance.
- **Vegetation**: computed from marker X position as `ceil(fabs(positionX / 100)) % 6` (FishingManagerImplementation.cpp:831); increases snag probability.
- **Fish density**: computed from marker Y position as `ceil(fabs(positionY / 100)) % 6` (line 838); affects bite chance.
- **Bait freshness**: if bait state > SOGGY and player is before CATCH state, there is a chance the bait is tossed (lines 418-425).

### State Transitions (FishingManagerImplementation.cpp:434-561)
- **WAITING**: Random roll determines SNAGGED (line 439), NIBBLE (line 446), or stays WAITING (line 456).
- **SNAGGED**: If roll succeeds, transitions to WAITING; otherwise stays SNAGGED (lines 466-470).
- **NIBBLE**: Mishap can snap the line (line 475); success transitions to BITE (line 481); otherwise may stay NIBBLE or return to WAITING (lines 492-498).
- **BITE**: Mishap causes lost bait or fish spools line (lines 506-510); success transitions to CATCH (line 516).
- **CATCH**: Mishap loses the catch (line 527); if player chooses REEL action, transitions to REELING (line 530).
- **REELING**: Updates marker position; stays in REELING until next tick (lines 537-541).
- **REELGAME**: If player is within 2.0 units of the marker, `success()` is called (line 547); otherwise marker updates and stays REELGAME (lines 550-556).

### Timings
- The FishingEvent is a Task scheduled every 7000 ms (FishingEvent.h:23; FishingManagerImplementation.cpp:1437).
- Each tick calls `continueFishing()` which processes the current state and schedules the next event (lines 1116-1125).

### Messages and Menus
- **Start**: Player sees `@fishing:start_fishing` (line 220) and performs `fishing_cast` animation (line 218).
- **SUI Window**: Created by `createWindow()` (lines 759-817). Shows:
  - STATUS, BAIT STATUS, LINE RANGE, FISH DENSITY, VEGETATION, NEXT ACTION (lines 794-799).
  - Menu items: TUG UP, TUG RIGHT, TUG LEFT, SMALL REEL, STOP (lines 807-811).
- **State messages** (FishingManagerImplementation.cpp:1043-1079):
  - WAITING from SNAGGED: `@fishing:line_free` (line 1046).
  - SNAGGED: `@fishing:fs_snag` (line 1049).
  - NIBBLE: `@fishing:fs_nibble` + fly text "fly_nibble" (lines 1056-1059).
  - BITE: `@fishing:fs_bite` + fly text "fly_bite" (lines 1063-1064).
  - CATCH: `@fishing:fs_caught` + fly text "fly_catch" (lines 1070-1071).
  - REELING: `@fishing:reel_in` (line 1078).
- **Success** (FishingManagerImplementation.cpp:564-731):
  - If fish > 80, may drop junk/weapon/armor loot (lines 593-605); chance > 190 for rare (line 597).
  - If fish <= 80, creates a FishObject with attributes (name, zone, time, length) (lines 624-650). Length modified by `creature_harvesting` skill mod (lines 637-646).
  - 5% chance fish is too small and tossed: `@fishing:size_matters` (lines 615-622).
  - Reward sent via `sendReward()` which opens the marker container to player and shows `fishing:prose_notify_catch` message (lines 745-747) or `@fishing:reel_loot` for junk (line 752).
- **Mishaps** (FishingManagerImplementation.cpp:1129-1150): Various `@fishing:` messages like `toss_bait`, `line_snap`, `lost_bait`, `line_spooled`, `tore_bait` depending on context.
- **Stop**: `@fishing:stop_fishing` message (line 334) and `fishing_reel` animation if not in combat/dead/incapacitated (lines 336-338).

### Other Mechanics
- Bait degrades over time; freshness values: FRESH = 0, SOGGY = 6, MUSH = 10 (FishingManager.idl:60-62).
- Bait loses freshness randomly when actions are taken (lines 1107-1109).
- If bait is MUSH and player hasn't reached CATCH, bait is tossed and fishing stops (lines 418-425).
- Player movement is monitored; if swimming starts, or distance to marker < 2.0 (before REELING) or > 20.0, fishing stops (FishingManagerImplementation.cpp:1534).
- During REELGAME, player must stay within 2.0 of the marker to succeed (line 547).

## 3. What a Bot Test Should Check

### Setup Required
- Equip a FishingPoleObject in the right hand slot (`hold_r`) (FishingManagerImplementation.cpp:920).
- Load a FishingBaitObject into the pole's container (lines 944-951).
- Stand on land adjacent to water (not swimming) at a valid fishing location.

### Observable Results to Verify
1. **Start fishing**: Call `startFishing()` and check:
   - System message `@fishing:start_fishing` received (line 220).
   - Player mood string set to "fishing" (line 219).
   - Fishing session created with state WAITING (FishingSession.idl:24; FishingManagerImplementation.cpp:293).
   - SUI fishing window opened with correct status text (lines 794-816).

2. **State progression**: Monitor the FishingEvent ticks (every 7 seconds) and verify:
   - State transitions through WAITING → SNAGGED/NIBBLE → BITE → CATCH → REELING → REELGAME (FishingManager.idl:43-50; FishingManagerImplementation.cpp:434-561).
   - Corresponding system messages and fly text at each transition (lines 1043-1079).
   - SUI window updates with current state, bait status, line range, fish density, vegetation (lines 794-799).

3. **Successful catch**: When REELGAME succeeds (player within 2.0 of marker):
   - FishObject created and transferred to player inventory (lines 624-719).
   - Fish attributes set: name, zone, time, length (lines 631-650).
   - System message `fishing:prose_notify_catch` with item name (line 745).
   - Marker container opened to player (line 755).
   - XP awarded for "camp" skill based on fish length (lines 652-658).

4. **Lost line / mishap**: Verify:
   - Appropriate `@fishing:` system message sent (e.g., `line_snap`, `lost_bait`) (lines 1130-1149).
   - Fishing session ends; state returns to NOTFISHING (FishingManager.idl:43).
   - If bait lost, pole container is empty or bait use count decreased (lines 1170-1178).

5. **Failure conditions**: Test and verify:
   - No pole: `@fishing:must_have_pole` (line 160).
   - No bait: `@fishing:bait_your_pole` (line 167).
   - Swimming: `@fishing:bad_cast` (line 178).
   - Bad cast location: `@fishing:too_far` (line 189) or `@fishing:invalid_location` (line 192).

## 4. Likely Reasons a Test Sees No Effect

- **Fishing disabled**: The server config may have `fishingEnabled = false` loaded from `scripts/managers/fishing_manager.lua` (FishingManagerImplementation.cpp:35-37, 49-54).
- **No pole in right hand**: `getSlottedObject("hold_r")` returns null or is not a FishingPoleObject (line 920-922).
- **No bait in pole**: Pole container is empty or first object is not a FishingBaitObject (lines 944-951).
- **Player swimming**: `isSwimming()` returns true, blocking start (line 177).
- **Invalid cast location**: Cast lands outside water or under terrain; position check fails (lines 274-285).
- **FishingManager not initialized**: The native `initialize()` or `loadConfigData()` may fail, leaving the manager non-functional.
- **Player moves too far**: During fishing, distance > 20.0 from marker stops the session (line 1534).
- **Player starts combat or dies**: Observer events trigger immediate stop (FishingManager.idl:95-96; FishingManagerImplementation.cpp:223-224).

## 5. Open Questions

- **Lua configuration file**: The actual values for fish types, colors, lengths, actions, states, and bait statuses are loaded from `scripts/managers/fishing_manager.lua` (FishingManagerImplementation.cpp:44), which is not included in the provided files.
- **Native function implementations**: Several methods are declared `native` in FishingManager.idl (lines 86, 88, 114, 123, 139, 151, 163, 174, 190, 199, 211, 222, 232, 243, 254, 266, 277, 288, 299, 309, 319, 330, 341, 352, 363, 375, 392, 407) and their C++ implementations are not in the provided files. Their exact behavior is unknown.
- **FishingSplashEvent class**: Referenced at FishingManagerImplementation.cpp:25 and 1419 but the file `FishingSplashEvent.h` is not provided.
- **StringIdChatParameter keys**: Messages like `@fishing:must_have_pole`, `@fishing:fs_nibble`, `fishing:prose_notify_catch` are client-side string IDs; their actual text content is not in the server source files.
- **Exact fish type mapping**: The mapping from integer fish codes (BLACKFISH=0 through STRIPED=6 in FishingManager.idl:52-58) to specific fish species names depends on the Lua config table `fishTypes`.

## ChatGPT's review (2026-10-18 22:30)

Checked disputed leads and matching snapshots against Core3-dev 9d08e265. Source only.

**Holds:** pole/bait, not-swimming and cast-water gates, explicit WAITING initialization (FishingManagerImplementation.cpp:206), seven-second events, SUI/state messages and fish/junk branches. Saluki's seven-seconds contradiction is self-contradictory; its WAITING objection misses line 206. Its other narrow-window objections do not refute complete success/state ranges.

**Corrections:**
- Do not require a fixed linear state sequence: NIBBLE/BITE need an action in TUGUP..REEL and can regress; CATCH accepts DONOTHING **or** REEL, not REEL alone (477-532).
- Fish rewards enter the **marker container**, which opens to the player; they do not automatically enter player inventory (733-755). Claim/retrieve the loot before asserting inventory gain. XP baseline is int((totalLength/baseLength)*90), independent of successful later retrieval (652-657).
- The small-fish discard check is random(20)<=1 (615-622): 2/21, about 9.52%, not 5% (inclusive API: utils/engine3/MMOEngine/src/system/lang/System.h:92-94; System.cpp:13-15).
- Soggy-plus bait loss is probabilistic and can begin before MUSH: baitState>SOGGY AND random(15)<baitState (418-425). MUSH does not guarantee loss on a particular tick.
- Not every mishap stops fishing: losebait=false recreates a WAITING event/session (1129-1146), including line_spooled and lost_catch (509,527). The test must distinguish reset from stop.
- The short answer's instruction to stand in water is unnecessary; valid non-swimming shore/cast location is what the gates establish. Native declarations do have implementations in this same supplied C++ file, so the broad missing-native-implementation claim is false.

Verdict: Core fishing flow supported; correct reward location, action-dependent transitions, discard odds, bait and mishap expectations; gameplay untested.
