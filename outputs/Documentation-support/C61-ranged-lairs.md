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

## Addendum, 10:45 PM: the "skill points mismatch" errors aren't from this patch

The main session reported 748 `skill points mismatch calculated: 985 found: 235` errors in the test galaxy's `core3.log` after fe399424 went live (run 18, from 10:25 PM).

- The file starts 15 Oct, 11:31 PM, and holds several runs.
- All 748 errors are at lines 16893-17886, from **16 Oct, 1:13-1:14 AM**: 429 at 1:13 and 319 at 1:14. That is 21 hours before fe399424.
- Every one is the same pair: calculated 985, found 235, a difference of 750. That is a 1,000-point budget (`config-local.lua` `SkillPoints = 1000`) against bots that were given 250. So it was a config change at that start, not a skill.
- Since 10:25 PM, `core3.log` has no such error. It has two error lines in total: an `unknown appearance type SPRT` and one Lua line.
- The check is `SkillManager.cpp:427-438` (awardSkill) and `:633-644` (surrenderSkill). It subtracts each skill's `POINTS_REQUIRED` from `Core3.Sandbox.SkillPoints`. The species skills cost 0 points (`skills.iff` `POINTS_REQUIRED` is empty for every `species_*` row), so awarding them can't change the sum.
- Gameplay effect: none now. Back then the check reset each bot's points to the calculated value, so the 1:13 AM bots got the full 1,000. No real-player path is involved: creation sets the points from the same config key.
- No fix2 patch is needed.
- First run-18 signs of the fix: ranged lair_check rows with damage show 124, 524 and 1,095 (3 of 306 rows so far). Before, those values were 3-10.

## Addendum 2, 17 Oct, 12:00 AM: why ranged bots still fail now that they damage lairs

Claude (side session). Read-only on Core3-dev (HEAD `69f5c879`) and run 18's log (`botpop-launch.jsonl.2332.old`, 10:25-11:30 PM 16 Oct, dev `d4b9d9a1` with fe399424). **Untested in game.** The patch applies and compiles. The main session builds and runs it.

### Answer

The damage now lands. A carbine bot left alone takes **about 1,030 condition a minute** off a lair (14 quiet one-minute pairs). That is what certified 37-75 shots every 3.5 s should give, so the shot cadence, the 2 s enqueue and attack costs are fine. Three other things stop the missions:

1. **Rifle and pistol bots never fight back.** BotPop notices an attacker only through `bot->getMainDefender()` (`launchHunt`, `BotPopLaunchBrain.h:1134-1155`). A creature's attack never puts the creature on the bot's defender list: `CombatManager::startCombat` (`CombatManager.cpp:110-113`) sets only the attacker's list and both combat states. The defender adds its attacker only through its own counterattack: `creoTargetCombatAction` case COUNTER, `:463-467`, which runs `attack` back at the attacker. Only some weapons can counter: `getWeaponDefendResult` (`CombatManager.h:282-295`) gives carbine and two-hand COUNTER, rifle and polearm BLOCK, pistol and one-hand DODGE, and unarmed a random one of the three. So the main defender is either nothing or the lair. That isn't a nearby creature, so BotPop calls `clearCombatState(true)` and the bot keeps shooting the lair while the creatures kill it. Run 18, by the bot's weapon:

   | weapon (defence) | aggro rows | incaps | kills with `aggro: true` |
   |---|---|---|---|
   | rifle (block) | 0 | 649 | 0 of 1,643 |
   | pistol (dodge) | 4 | 312 | 1 of 375 |
   | carbine (counter) | 460 | 232 | 365 of 857 |
   | unarmed (random) | 1,245 | 1,102 | 949 of 3,146 |
   | two-hand (counter) / one-hand (dodge) / polearm (block) | | | 9 of 20 / 2 of 66 / 0 of 6 |

   At mission lairs, carbine users fought the creatures in 90 of 92 missions. Rifle and pistol users fought them in 0 of 402, the same for hunters and samplers. Those 402 missions logged 801 incaps and 136 deaths. A median of 41 s passed between a lair check and the next incap. Then came 60 s down, a walk to town and up to 3 minutes' rest. While the bot was away, the lair's living creatures healed it back to 0 (for example 535 → 0 and 611 → 0 between visits; heal rule as above, `LairObserverImplementation.cpp:304-375`). Within the 20-minute abort, that left about three visits of 40 s each.

2. **The clear also drops the shot.** `clearCombatState` calls `clearQueueActions(true)` (`CreatureObjectImplementation.cpp:906`). With the lair as main defender it runs every 1 s tick, so the next queued shot is often thrown away. Only 8 quiet minute pairs exist for rifles and pistols, with a median of 158 a minute against the carbine's 1,030. That's too few to be sure, but it fits.

3. **Melee bots can't reach the lair at 6 m.** Core3-dev `a8ece12b` (16 Oct, 10:59 AM) moved every weapon from 20 m (ranged) or 4 m (melee) to 6 m from the lair's centre. A melee weapon reaches 5 m. In run 18, 94% of melee lair checks were beyond weapon range. Over 75 quiet minutes at 6 m, melee damage rose in 7, with a median of 0. Melee damages a lair only when a fight with its creatures happens to leave the bot closer. Brawlers fell from 46% of missions (run 13, at 4 m) to 14% (run 18).

**Then mission level decides it.** Run 18 missions that reached a lair, by mission level minus bot level:

| gap | melee | carbine | rifle/pistol |
|---|---|---|---|
| 0 or less | 61 of 95 (64%) | 3 of 11 | 7 of 56 (12%) |
| 1-2 | 16 of 158 (10%) | 2 of 37 | 0 of 128 |
| 3 or more | 0 of 156 | 0 of 39 | 0 of 192 |

Scouts already fight back and still finish 4 of 83, mostly because they take missions 1-6 levels above themselves. Fixing 1-3 should bring marksmen up to the carbine and melee rows. It won't fix the 3-or-more rows. `launchMission` takes the easiest mission offered, up to level + 6 (the owner's 15 Oct rule). **Owner's decision:** a lower cap, such as level + 2, would turn most of the 0% missions into skipped ones. This patch doesn't change that rule.

### Real-player impact

None.

- A real player who is attacked fights back by their own input; the client sends the attack. The defender-list behaviour is stock Core3, the same on live SWGEmu.
- The lair heal and `clearQueueActions` are stock too.
- The 6 m reach and the main-defender test are BotPop code (`a8ece12b`, `launchHunt`).
- A real ranged player who stands at a lair and ignores its creatures fails the same way. That is pre-CU play: kill the creatures first.

### Fix

`C61-ranged-lairs/C61-fight-back.patch`, against Core3-dev `69f5c879`. Two files, 68 lines.

- `launchHunt`: if the main defender isn't a nearby living creature, the bot asks its own threat map, `bot->getThreatMap()->getHighestThreatAttacker()`. Every creature that hits the bot is added there (`startCombat` `:115-120`, `inflictDamage`). That call locks the map and drops dead, incapacitated and out-of-range (128 m) entries. A nearby creature on it (same checks: alive, same zone, not given up on, under 80 m) is adopted with an `aggro` row, exactly as a counterattacking bot does today.
- `launchHunt`: no `clearCombatState` while the main defender is the mission's lair and the bot is within 16 m of it, so the queued shot survives. Walking off to rest still clears.
- `launchMission`: lair reach is 6 m for ranged weapons and 4 m (the old value) for melee.
- `BotPopManager.h` includes `server/zone/objects/tangible/threat/ThreatMap.h`.
- Side effects:
  - The threat map can keep a creature that hit the bot and then lost interest. If it's still alive and within 80 m, the bot attacks it, as an annoyed player would.
  - `getHighestThreatAttacker` keeps its pick for 24 s (`EVALUATIONCOOLDOWN`). It picks at random among the creatures that hit the bot, so a bot under several attackers fights them one at a time, not nearest first.
  - The bot's own threat map isn't used for experience or loot (the creature's map is).

Checks run (inside WSL, read-only):

- `git apply --check` in `/opt/swg/Core3-dev` at `69f5c879`, botpop tree clean: OK.
- Syntax-only compile of `ServerCore.cpp` (clang++ 19, flags from `build/dev/compile_commands.json`, patched headers first on the include path): exit 0.
- A copy with an `#error` line failed, so the patched headers were the ones compiled.

### How to verify (7 AM style report)

Run as usual with the patch. Compare with run 18:

1. **Aggro by weapon:** join each `aggro` row to the bot's weapon from its latest `kill` or `lair_check` row. Rifle aggro rows should go from 0 to hundreds, and pistol from 4. Rifle `kill` rows with `aggro: true` should go from 0 of 1,643 to a share like carbine's (about 40%).
2. **At the lair:** rifle and pistol missions should show `aggro` and `kill` rows after the first `lair_check` in most missions (run 18: 0 of 402). The time from a lair check to the next incap should grow (run 18 median: 41 s).
3. **Melee reach:** the findings line "Mission lairs (lair_check rows). melee" should show beyond weapon range near 0% (run 18: 94%) and median distance 4 m. Brawler missions should go back toward run 13's 46% (run 18: 14%).
4. **Missions by role:** marksmen should pass 10% (run 18: 8 of 515, 2%). Read it by mission level gap: a gap of 0 or less should climb from 12% toward the melee 64%, while 3 or more stays near 0% until the mission cap changes.
5. **Damage rate:** rifle and pistol quiet minute pairs (two `lair_check` rows within 80 s with nothing between them) should rise toward carbine's 1,030 a minute.

Steps 1, 2 and 5 aren't in `botpop_findings.py` yet. The scripts used here are short Python over the `.jsonl` (missions split from `mission_take` to `mission_done`/`mission_abort` per bot).

### Not done

- No in-game or agent-client test, no build, no run. The galaxy stays the main session's.
- The mission level cap is left alone. It's the owner's call (see above).
