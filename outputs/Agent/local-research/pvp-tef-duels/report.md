# Report: Duels and Temporary Enemy Flags (TEF)

## 1. Short Answer

A duel starts when a player issues `/duel <target>` within 25 meters, not in a no-duel area, and not already dueling that target. The sender adds the target to their duel list and sends a "challenge" system message; if the target has also challenged first, both sides receive an "accept" message and gain each other as defenders with ATTACKABLE/AGGRESSIVE PVP flags. A duel ends when either side uses `/endduel`, which removes both from each other's duel lists, clears defender status, and sends "end" messages to both. TEFs are temporary enemy flags set after PvP combat actions; they last for `FactionManager::TEFTIMER` (value not defined in these files) and mark the target as attackable until the timer expires. Four TEF kinds exist: GCW Crackdown, GCW PvP, Bounty Hunter, and PvP Area, each triggered by different combat conditions.

## 2. How It Works

### Duel Lifecycle

**Initiation (`DuelCommand.h`)**
- Checks player state, locomotion, that both are CreatureObjects, distance ≤ 25 m (line 51), not in a no-duel area (lines 37–49), not already dueling (lines 64–70), and target does not ignore the challenger (lines 77–78).
- Calls `CombatManager::requestDuel(creature, targetPlayer)` (line 81).

**`requestDuel` (`CombatManager.cpp:3214–3277`)**
- Adds target to challenger's duel list via `ghost->addToDuelList(targetPlayer)` (line 3234).
- If the target has *also* challenged the player (`targetGhost->requestedDuelTo(player)`, line 3236):
  - Both sides send each other an "accept" system message (`duel/accept_self` and `duel/accept_target`, lines 3249–3267).
  - Both players' PVP status bitmasks gain `ObjectFlag::ATTACKABLE | ObjectFlag::AGGRESSIVE` (lines 3237, 3253).
  - Both sets of active pets receive matching PVP updates (lines 3240–3247, 3256–3263).
- If only the challenger challenged:
  - Challenger receives `duel/challenge_self` (line 3269), target receives `duel/challenge_target` (line 3273).

**Ending (`EndDuelCommand.h` and `CombatManager.cpp`)**
- `/endduel <target>` when in a duel calls `requestEndDuel` (line 53 of EndDuelCommand.h), which:
  - Removes both from each other's duel lists (lines 3299, 3303).
  - Calls `removeDefender` on both players and their pets (lines 3300, 3304, 3312, 3335).
  - Sends PVP status updates to both sides (lines 3306, 3329).
  - Sends `duel/end_self` and `duel/end_target` system messages (lines 3325–3327, 3348–3350).
- If the command is used with no target or an invalid target, `freeDuelList` clears *all* pending duels for the player (line 38 of EndDuelCommand.h).
- If the challenger has an open challenge but not a full duel, `/endduel` cancels it (`cancel_self`/`cancel_target`, lines 56–64 of EndDuelCommand.h).
- If the target has an open challenge to the player, `/endduel` rejects it (`reject_self`/`reject_target`, lines 66–83 of EndDuelCommand.h).

**Declining**
- `declineDuel` (lines 3438–3461) removes the challenger from the target's duel list and sends `duel/cancel_self` and `duel/cancel_target`.

**Checking duel state**
- `areInDuel` returns true only when *both* sides have challenged each other (lines 3468–3469).
- `hasActiveDuelChallenge` checks one-sided pending challenges (lines 3475–3482).

### Temporary Enemy Flags (TEF)

**Kinds and triggers**
1. **GCW Crackdown TEF** – set when a GCW crackdown combat action occurs; tracked by `lastCrackdownGcwCombatActionTimestamp` and `crackdownFactionTefCrc` (lines 2831–2833, 2915–2928).
2. **GCW PvP TEF** – set when a GCW PvP combat action occurs; tracked by `lastGcwPvpCombatActionTimestamp` (lines 2827–2829, 2907–2909).
3. **Bounty Hunter (BH) TEF** – set when a BH combat action occurs; tracked by `lastBhPvpCombatActionTimestamp` (lines 2823–2825, 2911–2913).
4. **PvP Area TEF** – set when entering a PvP area and performing combat; tracked by `lastPvpAreaCombatActionTimestamp` (lines 2835–2837, 2882–2897).

**Duration**
- All four types use the same constant: `FactionManager::TEFTIMER` (lines 2849, 2855, 2863, 2889). The actual millisecond value is not defined in these files.
- Each type's timestamp is advanced by this duration when the corresponding combat action occurs.

**How TEFs are checked and removed**
- `hasTef()` returns true if any of GCW Crackdown, GCW PvP, or BH TEFs are active (line 2899–2901).
- `hasPvpTef()` checks GCW PvP, BH, and PvP Area timestamps (lines 2903–2905).
- Individual checks: `hasGcwTef()`, `hasBhTef()`, `hasCrackdownTef()` compare the respective timestamp against "is past" (lines 2907–2913, 2926–2928).
- A scheduled task (`PvpTefRemovalTask`) removes TEFs when the earliest-expiring timer elapses (lines 2962–2977). The schedule time is the minimum of all four remaining durations (lines 2964–2971).

**GCW-specific logic in `checkForTefs` (`CombatManager.cpp:3486–3520+`)**
- When the covert/overt system is enabled and attacker/target are in different factions with the attacker at COVERT status, GCW TEF is set (lines 3514–3516).
- When covert/overt is disabled and both players are OVERT in different factions, regular PvP TEF logic applies (lines 3518–3520+).

**What TEF allows**
- Sets `ObjectFlag::TEF` on the parent CreatureObject (lines 2870, 2893), which marks the player as temporarily attackable.
- Updates in-range building permissions when a new TEF is acquired (line 2869).

## 3. What a Two-Bot Test Should Check

**Setup needed first**
- Ensure both bots are CreatureObjects and players (not pets/vehicles).
- Position bots within 25 meters of each other.
- Verify neither bot is in a no-duel area (check `getActiveAreas()` for areas where `isNoDuelArea()` returns true).
- Confirm neither bot ignores the other's first name.

**Observable results to verify**

*When Bot A challenges Bot B (one-sided):*
- Bot A receives system message `duel/challenge_self` with Bot B's object ID.
- Bot B receives system message `duel/challenge_target` with Bot A's object ID.
- `areInDuel(A, B)` returns false (neither side has accepted yet).

*When Bot B accepts (mutual challenge):*
- Both bots receive `duel/accept_self` and `duel/accept_target` messages respectively.
- Both bots' PVP status bitmasks include `ObjectFlag::ATTACKABLE | ObjectFlag::AGGRESSIVE`.
- `areInDuel(A, B)` returns true.
- Each bot appears in the other's duel list (`getDuelListSize() > 0`).

*When either bot ends the duel:*
- Both bots receive `duel/end_self` and `duel/end_target` messages.
- PVP status bitmasks no longer include ATTACKABLE/AGGRESSIVE for each other.
- Duel lists are empty (`getDuelListSize() == 0`).
- `areInDuel(A, B)` returns false.

*TEF verification:*
- After a combat action between bots, check that the attacker's parent CreatureObject has `ObjectFlag::TEF` set in its PVP status bitmask.
- Verify `hasTef()` or the specific TEF type function returns true on the attacker's PlayerObject.
- Wait for the TEF timer to expire and confirm the flag is cleared (or check that `schedulePvpTefRemovalTask` has run).

## 4. Likely Reasons a Test Sees No Effect

1. **Distance > 25 m** – `checkDistance(creature, targetObject, 25.0f)` in DuelCommand.h line 51 rejects the command silently (returns `TOOFAR`).
2. **No-duel area** – If either bot is inside an ActiveArea where `isNoDuelArea()` is true, the command fails with `@duel:not_here` and returns `GENERALERROR` (lines 37–49).
3. **Already dueling** – `areInDuel` check in DuelCommand.h line 64 prevents re-challenging; sends `duel/already_dueling`.
4. **Target ignores challenger** – `isIgnoring(creature->getFirstName())` returns true (line 77); command silently fails with `GENERALERROR`.
5. **Covert/overt system disabled** – GCW TEF logic only triggers when `ConfigManager::instance()->useCovertOvertSystem()` is true (line 3511). If false, the condition at line 3514 never matches.
6. **Faction/status mismatch** – TEF requires different factions and specific status levels (COVERT for GCW TEF, OVERT for regular PvP TEF); bots on the same faction or with wrong status won't trigger it.
7. **TEFTIMER not defined or zero** – The constant `FactionManager::TEFTIMER` is referenced but its value is not in these files; if undefined or zero, TEFs expire immediately.
8. **Pets not active** – Pet PVP updates only occur if `getActivePetsSize() > 0`; inactive pets won't show changes.

## 5. Open Questions

1. **Value of `FactionManager::TEFTIMER`** – The constant is used at lines 2849, 2855, 2863, and 2889 but its definition is not in these files. Without it, the exact TEF duration is unknown.
2. **What triggers each specific combat action type** – `updateLastCombatActionTimestamp` (lines 2839–2872) accepts boolean flags (`updateGcwCrackdownAction`, `updateGcwAction`, `updateBhAction`) but the callers that set these flags are not in this file range. We don't know which combat events or commands invoke each variant.
3. **PvP Area TEF trigger** – `updateLastPvpAreaCombatActionTimestamp` (lines 2882–2897) exists but its caller is not shown; unclear what "PvP area" means in this codebase.
4. **BH TEF faction logic** – `hasBhTef()` and `updateLastBhPvpCombatActionTimestamp` exist, but the condition that sets a BH TEF (versus GCW TEF) is not visible here; `checkForTefs` only shows GCW logic in this range.
5. **Missing file for `FactionManager`** – The class and its `TEFTIMER` constant are referenced but not included.
6. **Missing file for `PvpTefRemovalTask`** – The task class is instantiated at line 2938 but its implementation is not in this range.
7. **What happens to duel state on logout/login** – `freeDuelList` is called with `spam=false` (line 3401) during cleanup, but the trigger for that call on disconnect is not shown here.
