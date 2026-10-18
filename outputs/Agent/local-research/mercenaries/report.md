# Mercenary Broker Mechanic Report

## 1. Short Answer

Players can hire up to three mercenaries from a broker NPC named Dax Venn near the Mos Eisley starport on Tatooine (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:6). The first contract is free; each mercenary costs nothing (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:10). Hired mercenaries follow the player as escorts and automatically join any combat the player enters (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:82-85, 104-125). They stay for up to 30 seconds after the player logs out or moves more than 120 meters away, at which point they are destroyed (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:128-157). Players can dismiss all mercenaries via conversation option "Dismiss my mercenaries." (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:14), or the system auto-dismisses them under certain conditions.

## 2. How It Works

### Conditions and Setup
- The broker NPC "Dax Venn (a mercenary broker)" spawns automatically when the SandboxMercenaries screenplay starts on Tatooine (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:13-31).
- The player must interact with this specific broker to access the conversation.
- The maximum number of mercenaries per player is 3 (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:5).

### Conversation Options
The broker conversation offers three options on the initial screen (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:12-16):
- **"Hire a mercenary."** → triggers screen "hired" (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:13)
- **"Dismiss my mercenaries."** → triggers screen "dismissed" (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:14)
- **"Not today."** → ends conversation (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:15)

### Hiring Process
When the player selects "Hire a mercenary":
1. The handler checks if the player already has 3 mercenaries; if so, it returns dialog: "You've already got three of my people. Dismiss some first if you want fresh blades." (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:178-181)
2. If under the limit, a new mercenary is spawned near the player's current position using `spawnMobile(planet, "sandbox_mercenary", ...)` (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:69-73).
3. The mercenary receives AI flags: `AI_NOAIAGGRO`, `AI_ESCORT`, and `AI_FOLLOW` (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:80-83).
4. It is set to follow the player with movement state `AI_FOLLOWING` (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:84-85).
5. The mercenary's object ID is saved to player string data under key `sandboxMercenaries` (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:88-89).
6. If this is the first mercenary for this player, a combat observer (`DEFENDERADDED`) and an upkeep timer (30-second interval) are created per player (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:94-98).

### Mercenary Stats
Each sandbox_mercenary has (src/bin/scripts/mobile/sandbox/sandbox_mercenaries.lua:3-47):
- Level 18 (line 10)
- Damage: 170-180 (lines 12-13)
- Base HAM: 3000, max HAM: 3500 (lines 15-16)
- Primary weapon: "imperial_weapons_medium" (line 40)
- Secondary weapon: "unarmed" (line 41)
- pvpBitmask: ATTACKABLE (line 28)

### Combat Behavior
When the player enters combat with a target, every idle mercenary joins the fight by calling `engageCombat(pTarget)` on each alive mercenary not already in combat (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:104-125).

### Timings and Auto-Dismissal
An upkeep event runs every 30 seconds (`checkInterval = 30 * 1000` milliseconds) per player (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:7, 97):
- Checks if the player is online (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:135).
- Checks if the mercenary is on the same planet as the player (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:142).
- Checks if the mercenary is within 120 meters of the player (`maxDistance = 120`) (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:8, 143).
- Mercenaries failing any check are destroyed via `destroyObjectFromWorld()` (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:146).
- If no mercenaries remain, the combat observer is removed (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:155).

### Dismissal
Manual dismissal via conversation screen "dismissed" calls `dismissAll(pPlayer)` which destroys all alive mercenaries and clears saved IDs (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:159-169, src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:30).

### Messages the Player Sees
- Initial greeting: "Need someone to watch your back out there? My crews follow you and fight whoever you fight. On this galaxy the first contract is on the house." (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:10)
- After hiring: "Done. They'll stick to you like a mynock. Come back if you want more, up to three at a time." (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:22)
- After dismissal: "Contracts closed. They'll head back to the cantina." (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:30)
- If at max capacity: "You've already got three of my people. Dismiss some first if you want fresh blades." (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:180)
- Declining: "Suit yourself. Tatooine isn't kind to loners." (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:38)

## 3. What a Bot Test Should Check

### Setup Required
1. Position the bot character near the broker at coordinates tatooine x=3552.0, y=-4782.0 (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:6).
2. Initiate conversation with the NPC named "Dax Venn (a mercenary broker)" (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:29).

### Observable Results to Verify
- **System/dialog messages**: Confirm the initial greeting appears, and after selecting "Hire a mercenary," the confirmation message appears (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:10, 22).
- **Mercenary spawn**: Verify a new creature object of type "sandbox_mercenary" spawns near the player within ~3 meters (random offset -3 to +3 on x and y) at the player's current floor height (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:70-72).
- **Mercenary state**: The spawned mercenary should have AI flags `AI_ESCORT` and `AI_FOLLOW`, and its follow target should be set to the player (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:81-85).
- **Combat behavior**: When the bot enters combat, verify all alive mercenaries call `engageCombat()` on the same target (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:119-121).
- **Dismissal**: After selecting "Dismiss my mercenaries," verify all mercenary objects are destroyed and no mercenary IDs remain in player data (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:159-169).
- **Max limit**: Attempting to hire a fourth mercenary should produce the "already got three" message instead of spawning a new one (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:178-181).

### Test Sequence
1. Talk to broker → select "Hire a mercenary" → verify mercenary spawns and follows.
2. Repeat twice more → verify total of 3 mercenaries.
3. Attempt fourth hire → verify rejection message.
4. Enter combat → verify all 3 mercenaries engage the same target.
5. Select "Dismiss my mercenaries." → verify all mercenaries destroyed.
6. Re-hire after dismissal → verify new mercenary spawns successfully.

## 4. Likely Reasons a Test Sees No Effect

- The bot is not on Tatooine or not near the broker's spawn location (x=3552.0, y=-4782.0) (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:6).
- The SandboxMercenaries screenplay has not started on this server instance, so the broker NPC was never spawned (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:13-31).
- The zone is disabled (`isZoneEnabled` returns false), preventing the broker from spawning (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:14-16).
- The bot already has 3 mercenaries saved in its string data, so new hires are rejected (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:65-67).
- The upkeep timer destroyed the mercenaries because the player logged out or moved beyond 120 meters (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:128-157).
- The bot lacks the required conversation skills or permissions to interact with the broker NPC.

## 5. Open Questions

- **Cost**: The initial greeting mentions "the first contract is on the house" (src/bin/scripts/mobile/conversations/sandbox/sandbox_mercenary_broker_conv.lua:10), but no code in these files implements any payment, credit deduction, or cost check. It is unclear if subsequent contracts have a cost that is not implemented yet, or if all mercenary hires are free.
- **Mercenary duration/expiration**: There is no explicit time limit on how long a hired mercenary stays active while the player remains online and nearby. They only persist as long as they stay within 120 meters of an online player (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:142-143).
- **Mercenary death**: If a mercenary dies in combat, it is removed from the alive list (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:50), but there is no code to spawn a replacement or refund. It is unclear if the player can hire another to replace a dead one immediately.
- **Player data storage**: The mercenary IDs are stored in player string data via `readStringData`/`writeStringData` (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:41, 59), but it is not clear if this data persists across server restarts or character relogins.
- **AI template**: The code calls `AiAgent(pMerc):setAITemplate()` with no arguments (src/bin/scripts/screenplays/sandbox/sandbox_mercenaries.lua:86). It is unclear what AI template is applied by default and whether this function requires a parameter.
