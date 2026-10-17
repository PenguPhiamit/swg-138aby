# C61: why ranged bots never destroy mission lairs

16 Oct, 10:00 PM. Claude (side session, taking over GPT's queued task). Read-only on Core3-dev (HEAD `8edfd13f`) and the test galaxy. **Untested in game**: the patch applies and compiles; the main session builds and runs it.

## Answer

**BotPop's bots have no weapon certifications, so their CDEF rifles and carbines hit a lair for 5-10.** This affects BotPop only. A real player is not affected.

- A real character gets its species skill at creation: `PlayerCreationManager::addRacialMods` awards the template's starting skills (`PlayerCreationManager.cpp:445`, `1100-1103`).
- That skill (for example `species_human`, from `datatables/skill/skills.iff`) carries the starting certifications: `cert_rifle_cdef`, `cert_carbine_cdef`, `cert_pistol_cdef`, `cert_knife_survival`, `cert_knife_stone`, `cert_lance_staff_wood_s1`, `cert_axe_heavy_duty` and `cert_grenade_fragmentation_light`. No profession box grants the CDEF certifications (see `Claude-class-check/matrix.md:402`).
- BotPop makes its characters on the server (`BotPopManager.h:455` `spawnOne`, then `setupLaunch` at `BotPopLaunchBrain.h:488`). It adds skill points, credits and the profession's novice box, but never the species skill. Nothing in `managers/botpop/` mentions `species_`.
- `rifle_cdef` requires `cert_rifle_cdef` (`bin/scripts/object/weapon/ranged/rifle/rifle_cdef.lua:84`). `WeaponObjectImplementation::isCertifiedFor` (`:668-685`) is therefore false for every BotPop marksman and scout.
- Against a lair (a TanO defender), `CombatManager::calculateDamage` (`CombatManager.cpp:1203`) replaces an uncertified weapon's damage with **5-10**. After the player ×1.5, that is 7-15 per shot every 3.5 s, about 3 per second, against a lair's 2,000-7,000 condition.
- Against creatures, the same check (`CombatManager.cpp:1127`) lowers only the minimum, to 5, and keeps the weapon's damage range. That is why ranged bots still hunt and level normally, and why nobody noticed.
- Unarmed has no certification, so brawlers deal full damage. That is the 46% against 0.06%.
- The lair also heals. While its creatures live, a creature heals it by a fifth of its maximum (`AiAgentImplementation.cpp:2113-2116`), at most once per 15 s heal check (`LairObserver.idl:32`, `LairObserverImplementation.cpp:304-375`). At 3 damage per second, a ranged bot can't outpace that. A full kill would take 10-36 minutes even without healing, and a mission aborts at 20 minutes (`BotPopLaunchBrain.h` `launchMission`, 1,200,000 ms).

## Evidence

**Run 16 `lair_check` rows** (dev `665bea04`; 1,014 rows by 9:55 PM, from `/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/botpop-launch.jsonl`):

| | rows | rows with damage | smallest damage values | median damage |
|---|---|---|---|---|
| ranged (rifle_cdef, carbine_cdef) | 503 | 93 | 3, 6, 7, 7, 7, 7, 9, 9, 10, 10 | 41 |
| melee (unarmed) | 511 | 121 | 28, 33, 53, 58, 58, 61, 75 | 625 |

- One certified CDEF rifle hit can't be below 37 (25 × 1.5). The ranged values of 7 and 9 are single uncertified hits (5-10 × 1.5).
- On rows for the same bot and lair, the lair took about 100 damage a minute from melee bots and about 13 from ranged bots.
- Every row passed the other checks: line of sight true, attackable true, posture upright (0), distance 5-7 m, and `max_range` 64 for rifles. So the shot is fired and lands. It just does almost nothing.
- Missions so far in run 16 (9:55 PM): brawlers took 411 and finished 43. Marksmen took 368 and finished 0. Scouts took 62 and finished 0.

**Run 13** (`botpop-launch.jsonl.1602.old`), outcome within 20 minutes of reaching a lair:

| role | lairs reached | destroyed | with an aggro row | incaps |
|---|---|---|---|---|
| brawler | 7,406 | 3,213 | 1,610 | 1,944 |
| marksman | 5,657 | 10 | 232 | 1,331 |
| scout | 1,028 | 1 | 952 | 3,103 |

- Brawlers destroyed more lairs (3,213) than they had fights at (1,610). They usually finish the lair after its creatures are dead, standing at it at full health.
- Marksmen stand at the lair for the whole 20 minutes, shooting it and resting.

**Ruled out, from the code** (`CombatQueueCommand.h:149-262`, `CombatManager.cpp:211-420`, `1623-1680`):

- Range, line of sight, attackability, posture and attack cost give the same result for ranged and melee shots at a lair.
- A TanO defender has no accuracy or defence roll (`doTargetCombatAction`: "No Accuracy / Defense Calculation for TanO defender").
- The lair's damage path (`applyDamage` → `inflictDamage` → `LairObserver` DAMAGERECEIVED) doesn't look at the weapon.
- The only weapon-dependent differences are certification, the melee ×1.25 and attack speed.

## Real-player impact

None from this cause.

- Every character made through the normal client creation (including the agent client's accounts) gets its species skill and the CDEF certifications.
- A real player using a weapon they aren't certified for gets the same 5-10 on lairs. That is stock Core3 behaviour, not something new here.
- The heal rule is also stock. Kill a lair's creatures first, then the lair. That is pre-CU play and needs no change.
- Not checked: characters made by any other server-side path (admin tools, scripts). This search found none besides BotPop.

## Fix

`C61-ranged-lairs/C61-species-certs.patch`, against Core3-dev `8edfd13f`:

- `setupLaunch` (`BotPopLaunchBrain.h`, before the novice box) awards the player template's starting skills, exactly as `addRacialMods` does: `awardSkill(skill, bot, false, true, true)` for each skill in `PlayerCreatureTemplate::getStartingSkills()` that the bot lacks.
- `BotPopManager.h` includes `templates/creature/PlayerCreatureTemplate.h`.
- Side effect: bots also get their species' skill mods (for example a Trandoshan's `unarmed_damage=15`), the same as a real player of that species.
- Bots that already exist keep their state, but `setupLaunch` runs for every bot `spawnOne` makes, so each new spawn gets the skill.

Checks run (inside WSL, read-only):

- `git apply --check` in `/opt/swg/Core3-dev`: clean.
- Syntax-only compile of `ServerCore.cpp` with its `build/dev/compile_commands.json` flags (clang++ 19, `-fsyntax-only`), with the two patched headers placed first on the include path: exit 0.
- A copy with an `#error` line failed, which proves the patched headers were the ones compiled.

## How to verify (main session)

1. Apply, build dev, and start a BotPop run as usual.
2. A marksman's `lair_check` rows should show `damage` rising by roughly 37-75 per shot, so in the hundreds between rows a minute apart. The smallest non-zero values should be 37 or more, not 3-15.
3. Over the first hour, marksmen and scouts should finish destroy missions at a rate near brawlers' (run 16 before the fix: brawlers 43 of 411, marksmen 0 of 368). Level-matched missions still matter; see FINDINGS-2026-10-16 item 2.
4. Optional, on one bot: its skill list should include `species_<race>`, and `isCertifiedFor` on its `rifle_cdef` should be true.

## Not done

- No in-game test and no agent-client test (overrides for this task).
- A spot-check of one bot's skills wasn't possible without touching the galaxy.
