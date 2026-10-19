# Sandbox World Bosses Report

## 1. Short Answer

The sandbox world boss system maintains three active bosses at any time, drawn from a roster of fourteen named creatures across nine planets. Each boss spawns with health/action/mind HAM pools multiplied by a species-specific factor (1.25× to 8×), lives for six hours unless killed, then respawns after a delay. Players who deal damage receive 25,000 bank credits each when the boss dies, and all players see galaxy-wide announcements at spawn, death, or escape. A big game hunter NPC at Mos Eisley provides approximate coordinates and waypoints to current bosses on request.

## 2. How It Works

**Conditions & Timings**
- The system keeps `activeBosses = 3` slots alive simultaneously (line 12).
- After server start, the first boss spawns after `firstSpawnDelay = 120` seconds; subsequent slots spawn every 5 seconds thereafter (lines 13–14, 75–78).
- Each boss has a `lifetime = 6 * 3600` (21,600 seconds / 6 hours) timer; if still alive and not in combat when it expires, it slips away after an additional `combatGrace = 10 * 60` (600 seconds / 10 minutes) grace period (lines 14–15, 183–200).
- After a kill, the slot refills after `respawnAfterKill = 90 * 60` (5,400 seconds / 90 minutes); after an escape, it refills after `respawnAfterEscape = 2 * 60` (120 seconds / 2 minutes) (lines 16–17, 177, 211).

**Boss Roster & Health Multipliers**
- The roster contains 14 entries with template name, display name, health multiplier (`ham`), and home planet (lines 22–37):
  - tatooine: Ghost-Scale the Canyon Krayt (ham 1.5), Old Rattlebones Ancient Krayt (ham 1.25)
  - endor: The Gorax Patriarch (ham 1.5), Razorback the Blurrg Raptor (ham 4)
  - dantooine: Gnasher the Graul Marauder (ham 3), Old Thunderhide (ham 4)
  - lok: The Dune Tyrant (ham 3)
  - naboo: Stormwing the Elder Peko-Peko (ham 3)
  - dathomir: The Life Stealer (ham 4), Widowmaker (ham 4)
  - corellia: Ironhide the Gronda Juggernaut (ham 6)
  - yavin4: The Mad Angler Queen (ham 4)
  - talus: Mirefang (ham 6)
  - rori: The Bark Mite Broodmother (ham 8)

**Spawn Mechanics**
- Bosses spawn at one of several wilderness reference points per planet, chosen randomly (lines 40–51, 112).
- A `spawnRadius = 400` metre random offset is applied around the reference point; if no valid spawn point exists, it falls back to the exact reference coordinates (lines 18, 113–117).
- The boss receives a custom object name: `[boss name] (world boss)` (line 127).

**Health/Combat Modifications**
- For each of the three HAM pools (health=0, action=3, mind=6), the boss's max HAM is multiplied by `ham`, then both max and current HAM are set to that value (lines 129–133). This means a ham 8 boss has 8× the base creature's health/action/mind pools.

**Rewards & Announcements**
- When killed, every player on the boss's damage dealer list who is a player creature receives `reward = 25000` bank credits (lines 19, 163).
- Each damaged player sees: `"You receive 25000 credits for helping bring down [boss name]."` (line 164).
- A galaxy-wide broadcast announces the kill: `"[World boss] [name] has been slain on [planet] by [names]!"` (lines 171–172).
- At spawn, a galaxy broadcast says: `"[World boss] [name] has been sighted on [planet]. Ask a big game hunter in Mos Eisley for its trail."` (line 143).
- If the boss expires without being killed and is not in combat, it is destroyed and the broadcast reads: `"[World boss] [name] has slipped away from [planet]. Something else is stirring..."` (lines 207–210).

**Big Game Hunter NPC**
- A stationary hunter named "Rhea Tannor (a big game hunter)" spawns at Mos Eisley on tatooine at coordinates (3546.0, -4786.0) with heading 120° (lines 53, 66–72).
- The NPC is defined as `sandbox_big_game_hunter`: level 40, INVULNERABLE + CONVERSABLE, no loot (mobile file lines 4–43).
- Talking to the hunter returns approximate coordinates rounded to the nearest 50 m and adds an orange waypoint to the player's datapad for each active boss (lines 215–241, 245–255).

## 3. What a Bot Test Should Check

**Setup needed first:**
- Ensure the server has been running long enough for at least one boss to spawn (wait > 120 seconds, or trigger slot filling manually if possible).
- Verify that the zone containing the target planet is enabled (`isZoneEnabled` check at line 99).
- Confirm the big game hunter NPC exists on tatooine at the expected coordinates.

**Observable results to verify:**
- **System messages**: After a boss dies, check that damaged players receive the credit system message `"You receive 25000 credits for helping bring down [boss name]."` (line 164).
- **Galaxy broadcast**: Verify the broadcast text format at spawn, death, and escape (lines 143, 172, 210). The color code `\#ffcc66` should render as orange.
- **Inventory/attributes**: Confirm that `addBankCredits(25000, true)` actually increased the player's bank balance by exactly 25,000 (line 163).
- **Boss state**: Check that a spawned boss has a custom object name ending with `(world boss)` (line 127) and that its HAM pools are multiplied correctly (lines 129–133). For example, a ham 4 boss should have 4× the base template's maxHAM for health, action, and mind.
- **Waypoints**: After talking to the hunter, verify that orange waypoints appear on the player's datapad pointing to the boss's approximate location (line 231).
- **Rotation behavior**: After a boss is killed or expires, confirm that a new boss eventually fills the slot (after respawnAfterKill or respawnAfterEscape delay) and that no duplicate roster entries exist simultaneously (lines 82–91, 175–178, 208–211).

## 4. Likely Reasons a Test Sees No Effect

- **Server not running long enough**: The first boss does not appear until 120 seconds after server start (line 13); testing too early will find no bosses.
- **Zone disabled**: If the target planet's zone is disabled, `isZoneEnabled` returns false and the boss is excluded from spawning (line 99).
- **All roster entries already active**: The system avoids duplicates via `activeRosterIndexes()`; if all 14 bosses are somehow marked active (unlikely but possible), no new spawn occurs (lines 82–91, 104–107).
- **Boss expired before test ran**: If the boss's 6-hour lifetime elapsed and it was not in combat, it slipped away and a new one may have spawned elsewhere (lines 183–212).
- **Player not on damage dealer list**: Only players who dealt damage receive credits; a player who merely observed or arrived after the kill gets nothing (line 157).
- **Hunter NPC not spawned**: If `isZoneEnabled(tatooine)` returned false during server start, the hunter was never created (lines 67–73).

## 5. Open Questions

- **Which creature templates are used as base stats?** The health multipliers reference `CreatureObject(pBoss):getMaxHAM(pool)` (line 130), but the actual base HAM values for each template (e.g., `giant_canyon_krayt_dragon`) are not defined in these files. They would be in separate creature definition files.
- **How does `getDamageDealerList()` work?** The function is called at line 157, but its implementation and whether it persists across server restarts or only tracks damage within the current session are unclear.
- **What happens if a player disconnects before receiving credits?** The code iterates the damage dealer list at kill time (line 161); if a player is offline, `SceneObject(pPlayer):isPlayerCreature()` may fail or the credit addition may not persist. This is not addressed in these files.
- **Can players stack credits by relogging and re-damaging?** The system does not appear to track per-player damage history across boss lifetimes; a player could potentially deal minimal damage, log out, log back in, and deal damage again to the same or another boss for repeated rewards. This behavior is not explicitly prevented.
- **What if `getSpawnPoint` fails consistently?** The fallback at line 116 uses raw reference coordinates, but whether those are valid spawn locations (e.g., inside terrain or buildings) is unknown without additional zone data.

## ChatGPT's review (2026-10-18 22:34)

Checked both supplied Lua snapshots against current Core3-dev 9d08e265 (matching). No Saluki mechanic claim set for this topic. Source only; this review does not enable or test encounters.

**Holds:**14 roster entries,three rotation slots, listed HAM multipliers (floor applied),25,000 bank-credit request for player damage-dealer entries,90-minute kill refill,2-minute escape refill and nearest50 m waypoints (bin/scripts/screenplays/sandbox/sandbox_world_bosses.lua:12-37,129-177,215-240).

**Corrections:**
- Roster spans **ten planets**, not nine (22-36). Slots are a target capacity, not three bosses always alive: deaths/refill/failure create gaps.
- Initial events are at **125,130,135 seconds**, since delay is firstSpawnDelay+slot*5 with slots1..3 (75-77), not120 then125/130.
- At six hours an out-of-combat boss disappears immediately; the ten-minute delay is scheduled **only while in combat**, and can recur repeatedly (183-211). It is not mandatory grace after every expiry.
- Reward eligibility is the returned damage-dealer list filtered to player creatures; the script does not prove every nearby helper or pet owner receives credit (157-167). It also does not establish a relog duplicate-payment exploit. Repeated damage before a single death does not itself create repeated reward executions; remove that speculative diagnosis pending dealer-list/observer evidence.
- HAM multiplier applies to spawned getMaxHAM after spawn, with floor, not necessarily a fixed template numeric base independent of spawn-level randomness (129-133).
- Snapshot presence/registerScreenPlay does not prove the running server started this screenplay or restored bosses after a restart. Fallback spawn safety, offline pay and missing-object slot recovery remain runtime/source-follow-up questions, not established failures.

Verdict: Rotation/reward outline supported after correcting planet count, slot guarantees, initial delays, expiry grace and unsupported relog speculation; gameplay untested.
