# Lair Mechanics Report

## 1. Short Answer

Creature lairs spawn waves of mobiles at two damage thresholds: on first damage (wave 1) and when condition drops past half (wave 2). After both waves, if the lair has boss mobs defined, a boss spawns once the difficulty-scaled condition threshold is met. Healers are randomly selected from living spawned creatures to repair the lair periodically. The lair is destroyed when its condition reaches zero, broadcasting an XP reward via the threat map and playing a heavy damage effect. Lair mobiles respawn individually every 2–4 minutes until the lair is destroyed. A "repopulated" lair can reset its spawn cycles and heal itself if no players are nearby and it still has living creatures.

## 2. How It Works

### Spawn Waves

- **Wave 0 (initial):** When a lair is first inserted into the zone, `spawnNumber` starts at 0 and immediately increments to 1, spawning the initial passive mobiles via `SpawnLairMobileTask` scheduled almost instantly (`(j + 1) * 200` ms) ([LairObserverImplementation.cpp:448–450][LairObserverImplementation.cpp:526]).

- **Wave 1 (first damage):** When the lair receives its first damage, `checkForNewSpawns` sees `spawnNumber == 1` and checks `conditionDamage > 0`. If true, it increments to 2 and spawns a new wave ([LairObserverImplementation.cpp:453–457]). The amount spawned is calculated from the lair's difficulty level for creature lairs (`Math::min(difficultyLevel, lairTemplate->getSpawnLimit() / 3)`) or randomly between half and full spawn limit for NPC lairs ([LairObserverImplementation.cpp:478–491]). Spawn delay for wave 2+ is random between `SPAWN_TIME_MIN` (1s) and `SPAWN_TIME_MAX` (10s) ([LairObserver.idl:23–24][LairObserverImplementation.cpp:529]).

- **Wave 2 (half condition):** When `spawnNumber == 2`, the code checks `conditionDamage > (maxCondition / 2)`. If true, it increments to 3 and spawns another wave ([LairObserverImplementation.cpp:461–465]).

- **Boss spawn:** After `spawnNumber >= 3`, if the lair type is `CREATURE` and has boss mobs defined, the code checks whether `(difficultyLevel * (lairMaxCondition / 5)) > lairConditionDamage`. If the condition damage meets or exceeds this threshold, a random boss mobile is spawned after 500 ms ([LairObserverImplementation.cpp:99–121][LairObserverImplementation.cpp:564–577]). Bosses only spawn once per normal lair (or twice if repopulated) ([LairObserverImplementation.cpp:552–553]).

- **Spawn limits:** For creature lairs, the spawn limit is tripled (`spawnLimit *= 3`) ([LairObserverImplementation.cpp:409][LairObserverImplementation.cpp:672]). If the lair has been repopulated, the limit doubles again ([LairObserverImplementation.cpp:414]).

### Healing

- Every time damage is received, if `lastHealTime` has passed, a task is scheduled after 200 ms to call `checkForHeal` ([LairObserverImplementation.cpp:125–138]).
- `HEAL_CHECK_INTERVAL` is 15 seconds ([LairObserver.idl:32]), meaning heal checks happen at most once every 15 seconds.
- `checkForHeal` iterates through `spawnedCreatures`, skipping dead, pet, or zoneless creatures, collecting live ones ([LairObserverImplementation.cpp:320–328]).
- If at least one live creature exists, it picks a random one up to 5 times until it finds an `AiAgent` ([LairObserverImplementation.cpp:344–357]).
- The selected healer sets its blackboard variable `"healTarget"` to the lair reference and changes movement state to `AiAgent::LAIR_HEALING` ([LairObserverImplementation.cpp:365–366]). The actual healing amount is not set here; it is handled by the AI agent's behavior.

### Lair Destruction

- When the lair receives the `OBJECTDESTRUCTION` event (condition reaches zero), `notifyDestruction` is called ([LairObserverImplementation.cpp:64–68]).
- It creates a `DisseminateExperienceTask` from the lair's threat map and executes it, distributing XP to attackers on the threat list ([LairObserverImplementation.cpp:216–217]).
- The threat map observers are removed and cleared ([LairObserverImplementation.cpp:219–220]).
- A heavy damage client effect (`clienteffect/lair_damage_heavy.cef`) is broadcast to all nearby players in both object-local and zone-local forms ([LairObserverImplementation.cpp:227–231]).
- The lair object is destroyed from the world with `destroyObjectFromWorld(true)` ([LairObserverImplementation.cpp:233]).

### Creature Respawn

- When a spawned creature dies (`CREATUREDESPAWNED` event), `checkRespawn` schedules a respawn task after a random delay between `RESPAWN_TIME_MIN` (120s) and `RESPAWN_TIME_MAX` (240s) ([LairObserver.idl:26–27][LairObserverImplementation.cpp:632]).
- The respawn uses the same template as the dead creature ([LairObserverImplementation.cpp:623–639]).
- Destroy mission lairs do not respawn mobiles ([LairObserverImplementation.cpp:619–621]).

### Lair Repopulation ("Milking")

- When `NOPLAYERSINRANGE` fires, the code first checks if condition damage is below half of max; if so, it returns early ([LairObserverImplementation.cpp:164–166]).
- If the lair type is `CREATURE`, `spawnNumber > 1`, and at least one living creature exists, a `LairRepopulateTask` is scheduled after 10 seconds ([LairObserverImplementation.cpp:168–173]).
- When the repopulation task runs, it verifies no players are in range and the lair isn't already repopulated ([LairRepopulateTask.h:30–31]).
- `repopulateLair` sets maxCondition to 75% of original (`lairCond * 0.75`), heals all damage back to full, resets `spawnNumber` to 0, and marks the lair as repopulated ([LairObserverImplementation.cpp:839–848]).
- After repopulation, `checkForNewSpawns` is called with `nullptr` attacker, which will trigger a new initial spawn wave ([LairObserverImplementation.cpp:853–856][LairObserverImplementation.cpp:435–436]).

### Aggro

- On each damage event, if an attacker is present and `lastAggroTime` has passed (checked every `AGGRO_CHECK_INTERVAL` = 30 seconds), a `LairAggroTask` is scheduled after `AGGRO_TASK_DELAY` = 4 seconds ([LairObserver.idl:33–34][LairObserverImplementation.cpp:418–427]).
- The aggro task calls `doAggro`, which iterates through `spawnedCreatures` and adds the attacker as a defender to each live AI agent, with a 50% chance per creature if not forcing all to attack ([LairObserverImplementation.cpp:267–296]).

### Baby Spawn Chance

- For creature lairs, there is a `BABY_SPAWN_CHANCE` of 500 (out of some larger denominator, likely 1000) that a spawned creature will be a baby ([LairObserver.idl:19][LairObserverImplementation.cpp:692]).
- Babies follow an adult creature with escort flags and formation offsets ([LairObserverImplementation.cpp:744–770]).

### Scout Spawn

- For creature lairs, if no scout has been spawned yet (`scoutCreatureId == 0`), there is a `SCOUT_SPAWN_CHANCE` of 10 in 100 that the first spawn will be marked as a scout ([LairObserver.idl:36][LairObserverImplementation.cpp:674–676]).
- Scouts have a custom name suffix "(scout)" and their object ID is stored ([LairObserverImplementation.cpp:732–737]).

## 3. What a Bot Test Should Check

### Setup

1. Target a creature-type lair (not NPC) with known difficulty level and spawn limit from its template.
2. Ensure the lair has boss mobs defined in its template (`hasBossMobs()` returns true).
3. Confirm the lair is not a destroy mission lair (those skip respawn).

### Observable Results to Verify

- **Initial state:** After approaching, verify initial passive mobiles are present and `spawnNumber` is effectively 1 (initial wave already triggered).
- **Wave 1 trigger:** Deal enough damage to exceed 0 condition damage. Within ~1–10 seconds, new creatures should appear. Check system messages or creature count increase.
- **Wave 2 trigger:** Continue damaging until `conditionDamage > maxCondition / 2`. Another wave should spawn within 1–10 seconds.
- **Boss spawn:** After both waves (spawnNumber >= 3), continue damage until `(difficultyLevel * (maxCondition / 5)) <= conditionDamage`. A boss mobile should appear after ~500 ms. Verify only one boss spawns per normal cycle.
- **Healer behavior:** During combat, observe if any creature stops attacking and moves toward the lair to heal it. The healer's blackboard `"healTarget"` is set to the lair ([LairObserverImplementation.cpp:365]). Heal checks occur every 15 seconds ([LairObserver.idl:32]).
- **Destruction:** When condition reaches zero, verify:
  - A heavy damage client effect plays at the lair location.
  - XP is distributed to attackers (check system messages or XP log).
  - The lair object no longer exists in the world.
  - All spawned creatures are set to despawn when no players are nearby ([SpawnObserverImplementation.cpp:76]).
- **Repopulation:** After destroying a lair, wait for it to be removed from zone. Then approach an intact creature lair that has living creatures and condition damage above half max. If no players are in range for 10 seconds, the lair should repopulate: heal to full, reset spawnNumber to 0, and allow new spawns ([LairObserverImplementation.cpp:839–848]).
- **Individual respawn:** Kill a single creature from the lair. It should respawn after 2–4 minutes (random between 120–240 seconds) ([LairObserver.idl:26–27]).

### Attributes to Monitor

- Lair condition damage vs. max condition.
- `spawnNumber` counter (via debug or reflection if accessible).
- Number of living creatures in the lair's spawned list.
- Whether the lair has the "repopulated" flag set.
- Threat map entries on the lair before destruction.

## 4. Likely Reasons a Test Sees No Effect

1. **Wrong lair type:** The code only spawns waves and bosses for `LairTemplate::CREATURE` type lairs ([LairObserverImplementation.cpp:407–409][LairObserverImplementation.cpp:99]). NPC lairs skip wave spawning entirely ([LairObserverImplementation.cpp:435–436]).
2. **Spawn limit reached:** If `spawnedCreatures.size() >= spawnLimit`, no new spawns occur ([LairObserverImplementation.cpp:439–441][LairObserverImplementation.cpp:679–681]). The bot may have killed too many creatures, filling the limit.
3. **Condition threshold not met:** Waves only trigger at specific damage thresholds (0 and half max). If the bot's damage per hit is too small or too large, it might skip a threshold check between ticks.
4. **Boss condition not met:** The boss spawn requires `(difficultyLevel * (maxCondition / 5)) > lairConditionDamage` to be false (i.e., condition damage must meet or exceed the threshold) ([LairObserverImplementation.cpp:109]). If the lair is destroyed before reaching this, no boss spawns.
5. **No healer available:** If all spawned creatures are dead, pets, or zoneless, `checkForHeal` returns early with no healer assigned ([LairObserverImplementation.cpp:337–339]).
6. **Repopulation blocked:** The lair won't repopulate if players are in range, if it's already repopulated (once per normal cycle), or if condition damage is below half max ([LairRepopulateTask.h:30–31][LairObserverImplementation.cpp:847]).
7. **Destroy mission lair:** These skip creature respawn entirely ([LairObserverImplementation.cpp:619–621]).
8. **Debug defines disabled:** `DEBUG_WILD_LAIRS` and `DEBUG_LAIR_HEALING` are commented out by default ([LairObserverImplementation.cpp:25–26]), so debug logging won't appear.

## 5. Open Questions

1. **Actual healing amount:** The code sets the healer's `"healTarget"` blackboard and movement state but does not specify how much health is restored per heal tick. This logic likely resides in the AI agent's `LAIR_HEALING` behavior, which is not in the provided files.
2. **DisseminateExperienceTask details:** The XP distribution formula, thresholds, and system messages are in a separate file not provided here ([LairObserverImplementation.cpp:216]).
3. **BABY_SPAWN_CHANCE denominator:** `BABY_SPAWN_CHANCE = 500` is compared with `System::random(100)` at line 692, which seems inconsistent (500 vs. range 0–99). The actual comparison logic or a different random scale may be in `checkSpawnAsBaby`, which is not included.
4. **Scout creature behavior:** The scout flag and custom name are set, but the scout's specific AI behavior or purpose is not explained in these files.
5. **Dynamic lair vs. static lair distinction:** `DynamicSpawnObserverImplementation.cpp` handles dynamic spawns with different initial mobile counts and respawn timers (`(60 + level * 2)` seconds at line 74). It is unclear which lairs use this observer versus `LairObserver`.
6. **Threat map XP messages:** The exact system messages players see when receiving distributed XP are not in these files.
7. **`repopulateLair` limit:** The code allows one repopulation per normal cycle (checked via `isRepopulated()` at line 847), but it is unclear if there is a global limit or if this can be repeated indefinitely under the right conditions.

## ChatGPT's review (2026-10-18 22:30)

Checked Saluki's disputed leads first, then all supplied observer/task snapshots against Core3-dev 9d08e265 (these copies match). Source review only.

**Holds:** initial/first-hit/over-half damage stages, condition boss gate, 15-second damage-driven heal checks, threat-map XP dispatch, 120-240-second despawn-triggered replacement and once-only repopulation are present. Saluki stripped comparison symbols from several claims: the original correctly says >0 and spawnNumber >1. Both explosion forms exist (LairObserverImplementation.cpp:227-231); its objections to that, the heal task/filters, repopulation reset and aggro loop are false when the complete ranges are read.

**Corrections:**
- Healing selection permits six attempts (counter 0 through 5), not five (344-357); Saluki is right here.
- Wave size has a **minimum of two** after the min(difficulty, template limit/3) calculation (478-484). NPC lairs reject normal damage-wave checks but can force-spawn (433-436,485-490); they do not skip every kind of spawning.
- Boss timing is two tasks: 200 ms observer callback (99-121), then 500 ms spawn task (569-575), not simply 500 ms from damage. Subsequent damage after spawnNumber reaches three is needed to take that branch; destruction/invalid attacker can prevent it.
- Respawn is on CREATUREDESPAWNED, not immediately on death; allow corpse/despawn time before the 120-240-second task (177 onward,590-639).
- BABY_SPAWN_CHANCE=500 is passed to checkSpawnAsBaby, not compared with random(100) here (692). CreatureManagerImplementation.cpp:307-318 checks tame>0 and random(chance * max(1,babiesSpawned)) < tame*100. Scout selection instead uses random(100)<=10 (674), so do not call it exactly 10/100.
- The doubled repopulation limit exists in checkForNewSpawns (412-414) but spawnLairMobile uses only the tripled limit (666-680); doubled effective capacity is not established. Missing a threshold between hits is not shown: >half remains true on later hits until destroyed. None of these source gates proves a specific failed run's cause.

Verdict: Wave/heal/repopulation skeleton supported; correct retry count, minimum wave, timing, respawn event, baby probability and effective-limit claims; gameplay untested.
