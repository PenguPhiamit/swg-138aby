# Report: Sandbox Datapad Tools (sandbox_tools_datapad.lua)

## 1. Short Answer

The sandbox datapad is an admin-only test tool obtained from the character builder terminal's "Sandbox Tools" menu. It provides four categories of one-click actions via a radial menu: teleporting to preset locations on every test planet, spawning any creature near the player, distributing complete test kits (medicine, instruments, traps, tools, weapons, bounty hunter droids), and applying or clearing conditions on the user (heal, damage, wounds, fatigue, poison, disease, fire, bleeding). Access is gated by a privilege check that rejects non-admin players with a system message. A bot test should verify admin-only access, each category's observable effects (teleport location change, creature presence in world, items in inventory, HAM/wounds/state changes), and the error messages when conditions aren't met.

## 2. How It Works

### Who gets them and when
- The datapad item is `object/tangible/sandbox/tools_datapad.iff` (line 4).
- It is obtained from the character builder terminal's "Sandbox Tools" menu (line 5).
- Only privileged (admin) players can use it; non-admins receive `"The test datapad only works for admins."` and get nothing (lines 109–122, specifically line 117).

### Teleports
- The radial "Test menu" opens a list of preset destinations: back to last jump point, Mos Eisley, Coronet, Theed, Hoth locations, Ossus locations (lines 8–21).
- Each entry is `{description, zoneName, x, z}` or `{"Back to where I was before my last jump (also /goto back)", "back"}` for the return point.
- For "back", it reads `"dev_back"` from screenplay data and validates the zone/cell still exists; errors include `"No earlier spot to go back to yet..."` (line 183) or `"The earlier cell no longer exists..."` (line 195).
- For named planets, it checks `isZoneEnabled()` and sends `"X is not enabled on this galaxy."` if disabled (lines 203–206), otherwise calls `switchZone()` (line 208).

### Spawn creatures
- Opens a multi-level menu: new Hoth/Ossus creatures first, then folders from `SandboxCreatureFolders` (lines 215–226, 228–230).
- Creatures spawn approximately 6 meters east of the player at the world floor height (lines 304–312).
- Gate: player must be outdoors; indoors yields `"Step outside first: creatures spawn outdoors only."` (lines 307–309).
- If `spawnMobile()` returns nil, the message is `"Could not spawn X."` (line 315).

### Give test kits
- Six kit categories with item lists: medicine packs, ten instruments, scout traps/camps, crafting/survey tools, weapons, bounty hunter droids/slicing tools (lines 41–81).
- Items are given to the player's slotted inventory via `giveItem()` (line 339).
- Message reports success/failure count: `"Test kit: X items given, Y failed (inventory full?)."` (line 346).

### Conditions on self
- Eight options (lines 83–92): heal fully, damage to half HAM, wounds of 100 per pool, fatigue of 200, poison/disease for 120 seconds, fire/bleeding for 60 seconds.
- Implementation details:
  - **Heal**: clears all wounds (pools 0–8), restores HAM to max, clears shock wounds, clears all state bits (lines 363–371).
  - **Damage**: halves HAM for pools 0, 3, 6 (health, action, mind) with floor at 1 (lines 372–375).
  - **Wounds**: sets wounds to 100 on all pools 0–8 (lines 376–379).
  - **Fatigue**: sets shock wounds to 200 (line 381).
  - **Poison/Disease**: calls `addDotState()` with duration 120 seconds, tick interval 30, damage per tick 100 (lines 383, 385).
  - **Fire/Bleeding**: same `addDotState()` but duration 60 seconds (lines 387, 389).
- After applying, sends `"Test datapad: <description>."` (line 392).

### State bits used
- Defined at lines 106–107: `STUNNED=0x1000`, `BLINDED=0x2000`, `DIZZY=0x4000`, `INTIMIDATED=0x8000`, `POISONED=0x800000`, `BLEEDING=0x1000000`, `DISEASED=0x2000000`, `ONFIRE=0x4000000`.

### Radial menu integration
- The datapad adds two radial items: "Character builder (full menu)" (ID 20) and "Test menu" (ID 120) via `fillObjectMenuResponse()` (lines 397–401).
- Selecting ID 120 calls `SandboxTestDatapad:openMain()` (lines 403–406).

## 3. What a Bot Test Should Check

### Setup needed first
1. Ensure the bot character is an admin/privileged player (the test galaxy's method for setting this).
2. Obtain the datapad item `object/tangible/sandbox/tools_datapad` from the character builder terminal or spawn it directly.
3. Be outdoors (not inside a cell) to test creature spawning.

### Observable results to verify

**Admin gate:**
- Use a non-admin character: expect system message `"The test datapad only works for admins."` and no menu/action (lines 114–119).

**Teleports:**
- Select a named planet destination: verify the player's zone name changes to that planet and coordinates match the preset (e.g., Mos Eisley at 3528, -4804 per line 10).
- Test "back" teleport after a prior jump: verify return to recorded location; test without prior jump for error message (line 183).
- Test a disabled zone if applicable: expect `"X is not enabled on this galaxy."` (line 204).

**Creature spawning:**
- Select a creature from the list: verify a mobile with that template appears ~6m east at world floor (lines 304–312).
- Test indoors: expect `"Step outside first: creatures spawn outdoors only."` (line 308).

**Test kits:**
- Select a kit category: verify all listed items appear in the player's inventory (check slotted object "inventory" per line 330).
- Verify message reports correct count of given/failed items (line 346).

**Conditions:**
- **Heal**: verify HAM pools 0,3,6 are at max, wounds on all pools 0–8 are 0, shock wounds is 0, and no state bits are set (lines 363–371).
- **Damage**: verify HAM pools 0,3,6 are halved (floor 1) (line 374).
- **Wounds**: verify all pools 0–8 have exactly 100 wounds (line 378).
- **Fatigue**: verify shock wounds equals 200 (line 381).
- **Poison/Disease**: verify the corresponding state bit (`POISONED` or `DISEASED`) is set and persists for ~120 seconds with tick damage of 100 every 30 seconds (lines 383, 385).
- **Fire/Bleeding**: verify `ONFIRE` or `BLEEDING` state bit set for ~60 seconds, tick damage 100 every 30 seconds (lines 387, 389).
- Confirm system message `"Test datapad: <description>."` appears after each action (line 392).

## 4. Likely Reasons a Test Sees No Effect

1. **Bot is not privileged/admin**: The `isPrivileged()` check on line 116 rejects non-admins silently (no menu opens, or the allowed() gate blocks it).
2. **Player is indoors when spawning creatures**: The parent ID check on line 307 prevents spawning; no creature appears and only the error message shows.
3. **Inventory full when giving kits**: `giveItem()` returns nil for each item that fails (line 339), so fewer items appear than expected.
4. **Zone not enabled on this galaxy**: Teleport to a disabled planet sends an error and does nothing (lines 203–206).
5. **"back" teleport with no recorded point**: If the player has never jumped in god mode, `readScreenPlayData()` returns nil and the action fails (line 180–184).
6. **Creature spawn failure**: `spawnMobile()` can return nil for invalid templates or server constraints; only an error message appears (line 315).

## 5. Open Questions

1. **How is `isPrivileged()` implemented?** The file calls `PlayerObject(pGhost):isPrivileged()` (line 116) but does not define it; the implementation is in a different file (likely `playerobject.lua` or similar).
2. **What is `SandboxCreatureFolders`?** It is referenced on lines 217, 249, 264, 267 as an external variable populated by `sandbox_menus.py` (line 213), but its structure and contents are not defined in this file.
3. **How does `addDotState()` work internally?** The file calls it with specific parameters (lines 383–389) but the function definition is elsewhere; tick behavior, stacking rules, and removal timing are unknown from this file alone.
4. **What exactly counts as "indoors" for the spawn gate?** The check `getParentID() ~= 0` (line 307) treats any parented object as indoors, but it is unclear if being inside a building with no explicit parent still counts.
5. **How does the character builder terminal integration work?** Line 400 adds a radial item that delegates to `CharacterBuilderTerminal`, but that file is not included here.

## ChatGPT's review (2026-10-18 22:35)

Checked supplied matching Lua against Core3-dev 9d08e265 and traced the DoT binding. No Saluki disputed lead. Source only; no admin tool use or game mutations.

**Holds:** privilege gate,teleport menu/outdoor spawn6 m in+x,six kit groups,partial kit accounting and eight condition actions (bin/scripts/screenplays/sandbox/sandbox_tools_datapad.lua:109-121,302-346,353-406).

**Corrections:**
- addDotState arguments are **strength30,health pool0,duration120/60,potency100,objectID0,defense0** (Lua:383-389; src/server/zone/objects/creature/LuaCreatureObject.cpp:258-271). The report swaps strength/potency into 'damage100 every30 seconds'. There is **no tick-interval parameter** here. Actual DoT cadence/resistance/application must be traced separately; the confirmation string does not prove a DoT landed.
- Heal clears wounds/restores all9 HAM attributes and only clears entries in STATE_BITS, not every possible state bit (Lua:363-371). It does not call a DoT-list removal method, so a cleared bit alone does not prove the underlying timed effect is gone.
- Damage halves **current** HAM, not maximum; wound writes are requests to setWounds and may be constrained downstream (374-378). Confirm actual values rather than treating a requested100 as an unconditional outcome.
- Nonprivileged rejection is not silent: it explicitly sends the admin-only message (116-118). Menu radial visibility versus action permission are distinct (397-405).
- 'X items given' is always sent, but ',Y failed' is conditional on failures>0 (346), not an unconditional two-count string. giveItem failure is not proved to be inventory-full only.
- Privilege is a PlayerObject server binding, not evidenced as a playerobject.lua implementation. The current file's APIs do not establish the bot exposes all menu/state operations. Preset teleports cover listed places, not literally every enabled test planet.

Verdict: Tool categories/gates hold; correct DoT parameter units, limited heal cleanup, conditional messages and effect-success assumptions; gameplay untested.
