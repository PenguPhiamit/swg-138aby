# End-to-end functional test plan: test galaxy

Claude, 16 Oct 2026 (evening). Owner, 16 Oct about 7 PM: test the game end to end and make sure everything works before new content. This plan is what the main session and GPT work through. It is a plan only: nothing here has been run for it.

Sources read: `Bot-reports/GATE.md` (gate of 15 Oct, 4:31 PM: FAIL, 22 of 35), `Bot-reports/fallback-coverage.md`, `Bot-reports/OVERNIGHT.md`, `tools/bots/scenarios/` (25 files and the README), `Bot-reports/launch-sim/FINDINGS.md` and `MORNING-SHEET.md` (BotPop runs 1 to 8), `Documentation-support/class-check-results.md`, `bot-coverage-matrix.csv`, `hutt-c54.md`, `live-release-1.md`, `swg-performance-options.md`, `Agent/local-research/bot-gap-list/report.md`, `Owner-test-list.md`, the board, and the test galaxy's `config-local.lua` (read only).

## How to use this plan

**Who checks.** Five kinds of checker, named the same way in every section:
- **Squad**: a Python scenario bot in `tools/bots/scenarios/` (real agent client, real packets), run by `squad.py`.
- **BotPop**: the server-side bots (`/botpop`, `managers/botpop`). They show what the server does at scale. They skip the client: no windows, no packets, planet moves are jumps, they walk through walls.
- **Gate**: `tools/bots/gate.py`, after every test-galaxy start. Verdict in `Bot-reports/GATE.md`.
- **GPT**: source review in `/opt/swg/Core3-gpt`, new scenarios, log and report analysis.
- **Owner**: in game, for what only a person can judge. The owner's list is the last section.

**What counts as a pass.** Each system has a pass line that a log or a bot can confirm: a gate check label, a report field, a console line or a database value. A system passes only when that line is seen on the current dev build and archive. "Untested" stays the label until then.

**Two traps to keep in mind.**
1. **The test galaxy is not live.** Its `config-local.lua` sets `SkillPoints = 1000`, `TrainingCostMultiplier = 0.25`, `CraftSeconds = 1`, `FactoryTimeMultiplier = 0.25`, `StructureMaintenanceMultiplier = 0.5`, `HouseItemsPerLot = 1000`, `MedicalAnywhere = true`, `TameAnything = true`, `JediXpMultiplier = 2.0`, and `AgentGear`/`BotPop` on. A pass here can hide a failure under live rules. Systems marked **[live rules]** below need one more check in the dress rehearsal (`live-release-1.md`, step 3: live's config on the 45xxx ports).
2. **Load on Miniverse.** The interaction loss of 16 Oct was CPU starvation from 1,700 active bots, not the game. Owner sessions and timing checks run with BotPop despawned or cut down (main session's call), or the result means nothing.

**Order of work.** Close the ranked gaps (section 3) first. Then run the full gate. Then the owner's session (section 4).

## 1 and 2. Systems, checks and coverage

27 systems in 10 groups (A to J). "Coverage" names the file that provides it today.

### A. Getting in

#### 1. Server start, account and login
- **Check:** the galaxy starts clean; the launcher logs in; character select lists the account's characters; a relog keeps position, items and credits; up to 15 characters per galaxy.
- **Who:** Gate (server check), Squad (`squad.py setup` logs in 24 accounts), Owner (launcher and screens).
- **Coverage:** `gate.py` checks running, initialised, dev commit and archive, and logs in missing bots. `besh-gather.py` checks "keeps all items through a relog". `tools/live_status.py` writes console tail and errors.
- **Gaps:** no check of a 15th character or the limit message; no check that credits and bank survive a relog; restart persistence (since 15 Oct a stop keeps the copy) has no automated check.
- **Pass:** `GATE.md` server line shows "server errors at start: 0"; a Squad relog check shows the same item OIDs, cash and bank before and after; a 16th creation attempt is refused (console or SUI text recorded).

#### 2. Character creation for each species
- **Check:** every playable species and both genders create without a crash: the ten stock species (Human, Zabrak, Twi'lek, Rodian, Trandoshan, Mon Calamari, Wookiee, Bothan, Ithorian, Sullustan), plus the Chiss and the Hutt from `local_planets.tre`. Sliders, palettes, hair, the description text, the name filter (canon names allowed, whole words), each starting profession, each starting city.
- **Who:** Squad (agent-client creation), GPT (data-table checks: `racial_mods.iff`, `attribute_limits.iff`, `player_species.stf`), Owner (looks).
- **Coverage:** **`tools/bots/scenarios/creation-sweep.py` (17 Oct, `b244f27`; README "Creation sweep")** creates every species and gender, checks the C54 F2/F3 data and the name filter in game, then deletes the characters. `squad.py setup` creates missing characters, but for the bots' own species only. `hutt-c54.md`: an agent-client Hutt (`huttcheck`) was created and its server side works. `Owner-test-list.md` section 1: Chiss by hand.
- **Gaps:** sliders, palettes and hair are judged by eye (owner). Each starting city is section 3 (`fresh_start.py`). The two bugs below.
- **Pass:** a new `creation-sweep` scenario creates 24 characters (12 species × 2 genders, where the gender exists), each logs in, reports `status()` with the expected species and non-zero HAM, then is deleted; the console has no creation errors; the Hutt's HAM matches the approved S7 row.
- **Result, 17 Oct 6:17 AM** (run 25: dev `7be8837a`, archive `f0191ab5` on client and server; report `Bot-reports/Creation/20261017-061803-creation-sweep.json`; 55 of 57 checks, the two failures below). **Passes, except the console line (bug B2).**
  - **24 of 24 created and logged in**, 8 at a time. The bodies ran 6:17:47 to 6:18:03 AM: 0.3 to 1.3 s per creation, 1.3 s per login.
    - Species and gender: for each one the object CRC matched the template it asked for, and the shown name matched. The 24 `characters_dirty` rows also had the right templates (checked by hand at 6:19 AM; the scenario now reads that table itself).
    - Starting attributes: all nine equal `profession_mods` + `racial_mods`, with current equal to maximum (24 of 24). Each profession appears four times, and each species has two different professions.
  - **Hutt (C54 F1 to F3) checked in game:**
    - Male Medic 700/450/600/700/300/350/1000/500/800 and female Entertainer 600/450/600/1000/400/450/800/400/700: each is its profession row plus S7's 100/150/300/0/0/50/0/0/300.
    - In the archive: the limits follow S7, `desc_hutt` is S7's own prose with the approved numbers, and the skill labels are "Hutt Special Features" / "Hutt Abilities".
    - A Hutt with a kajidic surname was accepted and a 3-letter Hutt name was refused, so creation applies Hutt name rules, not the Wookiee ones.
  - **Name filter, 21 of 21:**
    - Refused with the right code (8 of 8): Admin, "Dev" as a whole word (`name_declined_developer`); Captain, "Bank" as a surname (`name_declined_reserved`); a Wookiee surname, a 3-letter Hutt name, a digit (`name_declined_racially_inappropriate`); a name in use (`name_declined_in_use`).
    - Accepted (13 of 13): the old substring traps Rebecca, Victor, Devon, Sigmund, Modesto, Christopher and Cassandra; the canon surnames stock refused (Skywalker, Solo, Fett, Vader); the canon first name Lando; the Hutt kajidic.
  - **Deleted:** 24 of 24 rows moved to `deleted_characters` at 6:23 AM with the login server's own statements. None are left in `characters` or `characters_dirty`; the zone purges the objects on its next delete pass.
    - The run's own cleanup at 6:18 AM found no rows and touched nothing (the FAIL). New characters wait in `characters_dirty` until the zone's next save (about every 10 minutes), and the delete statements only see `characters`.
    - The scenario now waits for that save. That wait has run live only through `creation-sweep.py cleanup`, not yet inside a full run.
  - **Bug B1 (stock SOE text, cosmetic):** the creation screen shows the wrong bonuses for two species. The Sullustan description shows the Zabrak's 200/0/0/300/0/0/0/0/400 (real row 150/0/0/250/50/50/200/100/100). The Ithorian description shows the Mon Calamari's 0/0/0/0/0/150/300/300/150 (real row 400/100/100/100/0/0/200/0/0). Both come from `patch_12_00`'s `player_species.stf`, which our `local_planets.tre` copies unchanged. Fix proposed, not made: correct the two attribute blocks in our archive (needs a client and server install).
  - **Bug B2 (stock data gap):** the Ithorian male Brawler's starting jacket `object/tangible/wearables/ithorian/ith_jacket_s16.iff` (in `profession_defaults_combat_brawler.iff`) has no template on the server or in the client. Creating one logs 3 ERROR lines (`unknown template key 0xf940567d`, 6:17:55 AM), and the character starts without that jacket. It is the only starting item in the seven creation tables without a server template. The sweep now checks this ("data: every starting item has a server template") and ties such errors to the character. Fix proposed, not made: swap in an Ithorian jacket that exists, in our archive.
  - **B1 and B2 fix staged, 17 Oct, not installed:** `Fable-species/creation-fixes/local_planets-creation-fixes.tre` (5,308,443 bytes, SHA-256 `150909f0644b25c0ed27cdb0026d2445a5053f4a7e7a1b19c369407c1167e335`), built by `build_creation_fixes.py` on the installed `f0191ab5`. 199 of 201 entries are byte-identical; only `player_species.stf` and `profession_defaults_combat_brawler.iff` change (`checks.json`).
    - B1: only the nine numbers of the two ATTRIBUTES blocks change. The Sullustan now shows 150/0/0/250/50/50/200/100/100 and the Ithorian 400/100/100/100/0/0/200/0/0, each equal to its `racial_mods` row. The prose and every other text are unchanged.
    - B2: the Ithorian male Brawler gets `ith_jacket_s12`, "Ithorian Warm Jacket" (the human male Brawler wears `jacket_s16`, "Cold Weather Jacket"; the female Brawler has no jacket). It has a server template and a client appearance.
    - The sweep's own checks against the staged archive (`check_with_sweep.py`, in WSL, read-only): 8 of 8 pass, including "stock creation texts show their racial rows" (10 match) and "every starting item has a server template" (433 items in 7 tables). `test_creation_sweep.py`: 33 tests OK.
    - Waits for the owner's OK (board, Questions) and an install on client and server at the next test-galaxy restart. After that, a sweep run should show 57 of 57 and no `0xf940567d` lines.
  - **Stock behaviour, from the source and untested in the client:** a player can't delete a character until the zone's next save. Before it, the login server's move from `characters` finds no row and replies with a failure.

#### 3. Tutorial, starting city and the helper droid
- **Check:** the tutorial runs or is skipped cleanly; the player lands in the chosen city; the helper droid arrives and works (C55 F1: the stock lock-order bug that deadlocked for real new players).
- **Who:** Squad, Owner.
- **Coverage:** `squad.py setup` "leaves the tutorial room". `hutt-c54.md`: the agent-client Hutt "took the starting-city command and got its helper droid".
- **Gaps:** **the helper droid fix (dev `c5d713b8`) is not on the running build (run 13 is on `a8ece12b`).** No check walks the full tutorial. No check covers every starting city.
- **Pass:** on a build with `c5d713b8`, ten fresh characters in parallel each get a helper droid within 60 s, the server keeps answering (radial round trip under 1 s in the latency probe), and the console has no deadlock or lock-timeout line.

### B. Basic play

#### 4. Movement, collision and indoor cells
- **Check:** walking, running, swimming, slopes, doors and stairs, entering and leaving buildings, no rubber-banding, no falling through floors.
- **Who:** Squad, Owner, GPT (server movement validation source).
- **Coverage:** `esk-routes.py` (three routes at once), `esk-fallback-grid.py`, `esk-hoth.py` (snow loop, cliff check), `check_c40_floor.py`, `movement_evidence.py`, `Bot-reports/navmaps/`.
- **Gaps:** ~~the gate's largest failure~~ **passed 17 Oct (run 24, dev `7c2f2605`; cause and fix in `movement-pushback.md`).** "The server keeps putting us back (blocked, rooted or dead)" broke three checks on 15 Oct (Besh hide patrol, Cresh mission terminal, Esk plateau). Cause: the server bounces a walker when packets reach it bunched after a stall (its speed check divides client distance by server time; five bots bounced in one second while 300 BotPop bots logged in, 6.2 to 9.3 m/s measured against 5.68 allowed), and the body gave up after three bounces per move however long the walk; crouched or sitting bots were also bounced every step. Now the body re-plans after a bounce, gives up only on three within 10 m, stands up first and keeps under the server's speed for its posture; the server logs every bounce with its reason (`[Movement]` lines in the console log, for real players too). Still open: the server's speed check itself still misfires during stalls, which can rubber-band a real player (a follow-up for the owner to decide); walls and steps indoors have no check beyond the routes above. BotPop has no collision (it walks through walls), so its movement proves nothing here.
- **Result 17 Oct:** gate PASS 47 of 56 at 5:38 AM, no regressions; `esk-routes.py` 5 of 5 at 5:33 AM and again at 5:50 AM (Tovan on the plateau at z 178.9); Besh hide patrol reached; Cresh reaches the mission terminal and the mission area; Dova's 268 m walk into the cloning cell, which failed at 3:26 AM, arrives with 0 corrections; a kneeling bot stands up and walks 20 m with 0. In the 8 reports since the restart: 78 moves, **0 "putting us back" errors**, 5 server bounces, all absorbed. Probes: `claude-probe-movement.py`, `claude-probe-pathwalk.py`.
- **Pass:** `esk-routes.py` all three "reaches the …" checks PASS twice in a row, and "Tovan is up on the plateau (z > 150)" PASS; zero "putting us back" errors in that round's reports.

#### 5. Chat, emotes, radials and windows
- **Check:** spatial chat, tells, group chat, emotes, the radial menu on players, NPCs, items and terminals, SUI windows open and answer.
- **Who:** Squad, Owner (window layout and text).
- **Coverage:** `dorn-social.py` ("spatial chat heard by both", "tell arrives", "menu: …"), `esk-fallback-reach.py` (radials), the latency probe of 16 Oct (radial round trip 0.05 s at 6:56 PM).
- **Gaps:** no check of planet or galaxy chat channels, `/emote` lists, or a full screen of raw `@string` keys. `Agent/local-research/proofread-player-text/` exists but nothing checks text in game.
- **Pass:** `dorn-social.py` chat and tell checks PASS; a new scan of all `messages()` across one gate round finds no text that starts with `@` and has no translation (count recorded, target 0 new).

#### 6. Terminals and the character builder
- **Check:** bank (deposit, withdraw), character builder (test galaxy only), the sandbox tools datapad (admin only), travel and mission terminals (in their own sections), cloning and insurance terminals (section 9).
- **Who:** Squad, Owner (admin menus).
- **Coverage:** `esk-map-terminals.py` maps terminals into `tools/bots/places.json`. `hutt-c54.md`: an agent-client Hutt opened the character builder ("Character Options returned its page"). `d5554d44`: the builder no longer hands out draft schematics.
- **Gaps:** no bank transaction check; no check that the builder is absent on live (dress rehearsal); the MTG Content Library must not be used on live (`research-review-20261014.md`).
- **Pass:** a bank scenario moves 100 credits each way and the cash and bank values change by exactly 100; in the dress rehearsal the builder terminal is absent or refuses a normal player.

### C. Progression

#### 7. Skills, XP, trainers and the six starting professions
- **Check:** each starting profession (Brawler, Marksman, Scout, Medic, Entertainer, Artisan) gains XP from its own activity, trains its boxes at a real trainer for the right price, and every granted ability works. Then the elite professions.
- **Who:** Squad (`class-check.py`), BotPop (pacing at scale), GPT (skill data), Owner (trainer windows). **[live rules]** for skill points and training cost.
- **Coverage:** `class-check-results.md`: P0 controls PASS; `combat_marksman` 23 WORKS of 25. BotPop run 8 (`MORNING-SHEET.md`): 5,785 training purchases, no master reached. `test_professions.py` offline.
- **Gaps:** **class check pending for Brawler, Scout, Medic, Entertainer and Artisan.** Training at a real trainer through its window is untested ("a separate test", scenarios README); the bots get boxes from `/agentskill`. Scouts stall on trapping and exploration XP; Entertainers on image-designer XP (bots can't earn them). No elite profession has been run.
- **Pass:** `class-check-<profession>.json` for all six starters with 0 NOT_GRANTED and 0 NO_EFFECT; a new `trainer-buy` scenario buys one novice box at a real trainer and the box appears in the skill list with cash down by the listed price.

#### 8. Combat (PvE), states and damage over time
- **Check:** melee, ranged and unarmed attacks; specials; states (stun, dizzy, knockdown); poison, disease, fire and bleeding; creature aggro and leashing; XP after a kill.
- **Who:** Squad, BotPop (20,009 kills in run 8).
- **Coverage:** `aurek-hunt.py` ("combat XP message", "the creature goes down"), `forn-crew.py` (three tiers of fights), `crew_combat.py`, `claude-probe-c34r.py` (DOTs land 10 of 10), BotPop runs 1 to 8.
- **Gaps:** NPC humanoid fights (not just wildlife) by Squad bots; group XP split (section 21); creatures that attack first have no check.
- **Pass:** `aurek-hunt.py` and `forn-crew.py` combat checks PASS in the gate; BotPop's death share near Tatooine cities stays under 2% (`numbers.md` city table).

#### 9. Death, incapacitation, cloning and insurance
- **Check:** incapacitation and recovery, death, the clone window, cloning at the chosen facility, wounds and battle fatigue, item decay, insurance at the terminal.
- **Who:** Squad, BotPop, Owner (clone window).
- **Coverage:** every Squad run does `recover()` first (waits out incap, clones if dead). `esk-recovery-proof.py`. BotPop: about one death per bot per hour, all cloned.
- **Coverage (17 Oct, 3:37 AM, 11 of 11 PASS; the 3:32 AM run also checked the 1,000-credit bind):** `besh-death-insurance.py` (Dova, Mos Eisley). Binds at one cloner (terminal radial 20, confirm window, 1,000 credits); `/insure` at the insurance terminal in the same room (list of insurable items, first row, 100 credits, `prose_insure_success`); dies at the other cloner, 447 m away, from three incapacitations in a row (`/agentgear afflict incap`); the clone window offers `revive_closest` and `revive_bind`; picking the bind clones it 18 m from the bound cloner (the spawn point is outdoors); the decay report shows the insured item lost 1% and every other item 5% (98% against 90% after two deaths); all 53 items kept.
- **Gaps:** wounds and battle fatigue after cloning (the body does not track wounds); the new-player cloning coupon; insure-all; a second planet's cloner (off-planet binds show as unavailable). Walking straight into a building's cell from 270 m away failed with "the server keeps putting us back"; two legs (outdoors to the building, then in) work. Since dev `7c2f2605` the straight walk arrives too (section 4, 17 Oct).
- **Pass:** a new scenario insures one item (cash down by the fee, the item shows insured), dies, clones at the bound facility (planet and position match), and the item is still in inventory.

#### 10. Spawns and danger near the starting cities
- **Check:** a new character can hunt near every starting city without meeting creatures far above its level; the spawn level gate (`b20a46d7`, fix F2 in `c5d713b8`) protects new characters without removing spawns for others.
- **Who:** BotPop, GPT (`spawn-review.md`, `city-spawn-proposals.md`).
- **Coverage:** `launch-sim/FINDINGS.md` sections 4 and 5; run 8: 18 of 1,039 deaths from enemies 8+ levels higher.
- **Gaps:** the F2 fix (krayts for solo masters) is not on the running build; the T1/T2 and S1 to S5 proposals wait for the owner.
- **Pass:** on `c5d713b8`, a BotPop run shows deaths from enemies 8+ levels higher under 2% of deaths, and a master-level test character still sees krayt spawns in the Dune Sea.

### D. Making money

#### 11. Missions (all terminal types)
- **Check:** destroy, deliver, crafting, survey, entertainer and musician, bounty hunter, scout/recon, and faction missions; list, accept, waypoint, complete, reward into the bank; the 2-mission cap on live, 6 on test; a full datapad refuses cleanly (C56).
- **Who:** Squad, BotPop, GPT (C56 gate).
- **Coverage (17 Oct):** four scenarios with a shared helper, `tools/bots/missions.py`:
  - `cresh-missions.py`: general terminal, destroy, deliver, the 6-mission cap, newbie and statue terminals;
  - `besh-missions.py`: artisan terminal, crafting and survey;
  - `dorn-missions.py`: entertainer terminal, dancer and musician, plus a general deliver;
  - `forn-missions.py`: scout terminal (hunting, recon), bounty terminal, imperial and rebel terminals.

  Each mission is checked from the terminal to the end: listed, accepted into the datapad, travelled to, done, gone from the datapad, and the share in the bank. The share is reward // group size: the server divides the reward by the group, so a grouped bot never gets the whole reward. 41 offline tests: `python -I tools/bots/test_missions.py`. Also BotPop run 8: 2,358 completed missions, 3,218,196 credits paid. `review-C44/F1-fix.md` lists the crafting-mission checks.
- **Results (17 Oct, test galaxy runs 24 to 29, Mos Eisley).** Runs at 5:38 AM (the gate), 6:25 AM, 11:56 AM and 12:35 PM; reports in `Bot-reports/<Group>/20261017-*-missions.json`. Every share below is exact.

  | Terminal | Mission | Result | Reward → share paid (group size), time |
  |---|---|---|---|
  | general | destroy | **PASS** (12:41 PM): lair destroyed, mission removed, owner paid; the two helpers were not (bug 1) | 774 → 258 (3), 344 s |
  | general | deliver | **PASS** twice (Rusk; Cresh's group all have full inventories) | 62 → 20 (3), 80 s; 64 → 21 (3), 85 s |
  | general | the cap | **PASS** four times: Ilsa holds 6, and a 7th stays in the mission bag; 11:18 PM, on the new body (dev `1be13676`), the exact message arrives: `@mission/mission_generic:too_many_missions` | before that only as `@mission:mission_generic` (bug 4) |
  | artisan | crafting | **PASS** twice: the NPC's schematic and parts, the generic tool, the hand-over | 64 → 16 (4), 83 s; 102 s |
  | artisan | survey | **PASS** (10:12 PM, run 30): Dova, guarded by Varo, found Vesoide at 75.9% (non-ferrous metal, 50% needed) 1150 m out | 471 → 117 (4), 290 s |
  | entertainer | dancer | **PASS** twice: 10 minutes dancing inside the mission's building | 133 → 44 (3), 667 s; 169 → 56 (3), 706 s |
  | entertainer | musician | **PASS** twice: slitherhorn, same building; the bank also gets the dancer's share | 157 → 52 (+44), 701 s; 205 → 68 (+56), 709 s |
  | scout | hunting | **PASS** (12:35 PM and 10:20 PM): 15 kills counted by the server | 1038 → 207 (5), 817 s; 2051 → 410 (5), 673 s. 11:56 AM: completed, hunter paid 0 (bug 1) |
  | scout | recon | **PASS** (10:28 PM, run 30): Forn, now a Marksman, after his hunt; 2 fights on the way, nobody downed | 454 → 90 (5), 510 s |
  | bounty | bounty | **not completed**: listing (Novice Bounty Hunter) and accepting work; 10:05 PM: a target within 4 km on the first list, but Ressa's accept is refused (`too_many_missions`: she already holds a far bounty from the morning, and the server allows one at a time); 10:35 PM: Brask, given Novice Bounty Hunter, got no bounty offers in 30 lists (the bag kept other terminals' offers; his walk ended "could not reach the destination" near the terminal) | 5400 to 10584; 7074 |
  | imperial | recon | **PASS** (10:47 PM, run 30): Dask with Mirren as escort, both Marksmen; 2 fights, both downed once on the way and got up. Mos Eisley's imperial and rebel terminals offer no deliver missions | 573 → 114 (5), 809 s |
  | rebel | recon | **PASS** twice | 314 → 62 (5), 328 s; 385 → 77 (5), 471 s |
  | newbie, statue | list | none stands within 3 km of Mos Eisley | — |

  Terminals within 3 km of Mos Eisley, by the server's search: general at least 11, entertainer 10, scout 10, artisan 8, bounty 6, imperial 2, rebel 2.
- **Bugs found (17 Oct; evidence in the reports named):**
  1. **Group pay is judged from the mission's end point only** (server). A destroy mission's end stays at its first spot when the lair spawns up to 256 m away; a hunting mission's end is where it was listed.
     - 5:38 AM: Cresh and Kor at the lair were unpaid; Ilsa, dead at the first waypoint, was paid.
     - 12:22 PM: Forn's hunting mission completed and he was paid 0.
     - 12:41 PM: Ilsa and Kor at the lair were paid 0.
     - **Staged fix:** `mission-group-pay.patch` with `mission-group-pay.md`, built into run 30 (dev `cbd85fdf`). Check: "general/destroy: everyone who fought at the lair is paid": **not yet run.** 10:15 PM: all three died at a held difficulty-14 kreetle lair (1152 credits); 10:35 PM and 11:18 PM: no destroy mission of difficulty 10 or less within 2.3 km among the 6 offered. The shown difficulty is the lair's level (at least 4) plus the group's level (`Agent/local-research/easy-destroy/report.md`), so a fixed 10 never fits these groups; `cresh-missions.py` now takes the lowest on offer and reuses a held one only if it is no harder (3b76661). 18 Oct 2:31 AM (run 30b): the lowest on offer was 14, so the held 14 (a small kreetle lair) was taken; the grouped three reached it (Kor downed on the way) and Ilsa and Kor died, Cresh incapacitated, the lair standing. These Marksmen can't clear the easiest lair Mos Eisley offers them, so the check waits for the fighting fix (the "why marksmen still fail" work) or stronger fighters.
  2. **A deliver pickup into a full inventory leaves the mission stuck** (server). `DeliverMissionObjectiveImplementation::updateMissionStatus` aborts the objective when the datadisk can't be added, but leaves the mission in the datapad with no message. The NPC still says the pickup line (`m3p`). Cresh, 5:38 AM: inventory 80 of 80, no datadisk, waypoint unchanged; the mission is still held. Crafting pickups have the same pattern. Proposed, not fixed.
  3. **A bank terminal's Deposit/Withdraw window opens at any range** (server). Kor, dead and 2 km from the nearest terminal, opened it about 6 AM. The scenarios use it, read only and cancelled, to read the balance. Proposed, not fixed.
  4. **Bot body:**
     - string-id messages from `mission/mission_generic` lose their key (`AgentControl::onStringIdSystemMessage` splits at the `/`), so the exact refusal message can't be confirmed;
     - the body forgets the bank balance at the first character delta it can't parse;
     - `find` from inside a building searches around cell-local x and y (Cresh, cloned indoors, found nothing at 11:56 AM);
     - there is no mission abort.

     Dev `1be13676` (11:14 PM on Forn's and Cresh's bodies) fixes the first and the last: the refusal now reads `@mission/mission_generic:too_many_missions`. New with it, 11:18 PM: Forn's walk to a scout terminal 1 km away failed at once with "walking without z requires the /agentpath helper" (`Bot-reports/Forn/20261017-232839-forn-missions.json`).

     The scenarios work around all four.
  5. **Squad bots:** 10 of 24 have full inventories (80 items), mostly spare `/agentgear` kits (Cresh, Ilsa, Kor, Dorn, Nima, Mirren, Aurek, Sela, Oren, Besh), so they can't take deliver, crafting or survey missions.
- **Gaps:**
  - **Survey** passes since 10:12 PM (run 30), after the class match, the density fraction and the guarded walk back.
  - **Scout and imperial recon** pass since 10:28 PM and 10:47 PM (run 30): Marksman walkers (89737ca), Mirren escorting Dask, and a walk to the building first after "no path" (3a4414e).
  - **Bounty** isn't completed. Level-1 targets spawn at random spawn points anywhere on the planet, and each list request draws new offers, so the scenario lists again until one starts within 4 km (89737ca; found on the first list at 10:05 PM). The server allows one bounty at a time and Ressa holds a far one (no abort in the old body; dev `1be13676` adds `mission_abort`), so Brask hunted at 10:35 PM (3a4414e), but his lists showed no bounty offers: he likely stood out of the terminal's range ("stopped at the end of the last path"). 11:18 PM (new body): he stepped up to the terminal and listed 30 more times, still no bounty offers (only the bag's earlier offers), but range is the cause after all (main session's review, 18 Oct 3 AM; `Agent/local-research/bounty-offers/report.md`): his events hold 93 `@radial_out_of_range_prose:ui_radial`, the 6 m list check, so every list was refused and the bag kept other terminals' offers. Ressa's held bounty was not aborted (no abort event; most likely its target is within 4 km of where she now stands). The scenario now walks to within 5 m of an outdoor terminal before listing (3b76661). 18 Oct 2:31 AM (run 30b): Brask still "arrived" at the end of a short path, never moved (no server position events), and got 93 refusals again, so that step did not close the gap either; why it did not move is open (the report cuts the step replies). Next: check the bot's range to the terminal before listing, or abort Ressa's far bounty with the new body's `mission_abort` (dev `1be13676`; the squad bodies still run the old binary). The informant step is offline tested only.
  - **The full-datapad gate (C56)** is not run.
  - **The 2-mission cap on live** is not checked (live's config).
- **Pass:** met for 9 of 11 terminal missions, with the exact refusal message on the new body (11:18 PM); bounty and the group-pay check are open. `cresh-missions.py` "the mission leaves the datapad" and "the share reaches the bank" PASS (general/destroy, 12:41 PM). Deliver and crafting PASS in new scenarios. The seventh mission is refused, but the message reaches the body only as `@mission:mission_generic` (bug 4), so "with the exact message" waits for the body fix.

#### 12. Loot and items
- **Check:** creature and NPC drops have real names; looting works; items stack and split; the junk dealer buys.
- **Who:** BotPop, Squad, Owner (names).
- **Coverage:** BotPop: corpses looted (2,951 in one report), junk dealer (3 sales in run 3). `Owner-test-list.md` 5.2: named Hoth drops.
- **Gaps:** about 11,000 log lines an hour of missing loot base templates (`retrieve_quest_base.lua`, `loot_base.lua`) bury real errors. No check that drop names resolve.
- **Pass:** console lines for missing loot templates fall to 0 after a fix, or are listed as a known set; a Squad loot check finds no item name starting with `@`.

### E. Crafting and resources

#### 13. Resources, surveying and sampling
- **Check:** every survey tool type finds resources on every planet, Hoth and Ossus included; samples land in inventory with a quantity; resources rotate.
- **Who:** Squad, GPT (resource spawner review), Owner (resource names on Hoth and Ossus).
- **Coverage:** `besh-gather.py` (mineral, liquid, chemical, flora, gas, moisture, wind, solar surveys and samples); `Owner-test-list.md` section 3; `hoth-release-gate.md` (R2 reviewed in source).
- **Gaps:** gas survey lists nothing; moisture and wind surveys return null; the body cannot read sample quantities (`bot-gap-list`). Geothermal, tidal and hydron-3 have no survey device (stock, by design).
- **Pass:** `besh-gather.py` "{kind} survey lists resources" and "finds a concentration" PASS for all eight kinds on Tatooine, and for mineral on Hoth and Ossus.

#### 14. Creature harvesting
- **Check:** meat, hide and bone from a fresh kill go into a new resource container.
- **Who:** Squad, BotPop (Scouts harvest).
- **Coverage:** `besh-harvest.py`; BotPop (561 harvests in one report).
- **Gaps:** ~~`besh-harvest.py` regressed (hide patrol unreachable, same movement gap)~~ the hide patrol is reached again (17 Oct, section 4); ordinary wild prey near the patrol spots is scarce, so the meat and hide checks still fail ("prey level unknown or above 5").
- **Pass:** `besh-harvest.py` "Pell receives new {kind} resource container" PASS for meat, hide and bone.

#### 15. Crafting, experimentation and factories
- **Check:** the crafting window, schematic list, ingredient slots, assembly, experimentation, the finished item; tools and stations; factories and schematics; Artisan XP. **[live rules]** for `CraftSeconds` and factory time.
- **Who:** GPT (new body API and scenario), Squad, Owner (crafting window feel).
- **Coverage (17 Oct, 3:19 AM, 21 of 21 PASS):** `besh-crafting.py` (Dova). The body now speaks crafting (dev `fc3bb3e2`: `craft_add`, `craft_experiment`, `crafting`; events `craft_schematics`, `craft_slots`, `craft_result`), and `/agentgear resources` gives metal, mineral and chemical. A Mineral Survey Device made twice: with the generic tool (schematic list, slots after `synchronizeduilisten`, four slots filled, assembly, `prototype_transferred`, the device in the inventory, XP), and with the weapon tool at Mos Eisley's public weapon station (3497, -4757) with one experimentation point (result 1, great success).
- **Gaps:** factories and manufacture schematics; component slots (only resource slots tested); whether experimentation changes the item's stats (only the result code is checked); the item's stats; the live `CraftSeconds`. Besh's own inventory is full on the server although his client lists about ten items: every kit item failed for him on 17 Oct (a body or server question to look at). BotPop still leaves Artisans out.
- **Pass:** a new crafting scenario makes one survey tool from sampled resources, the item lands in inventory with stats, and Artisan XP rises by the message's amount.

#### 16. Harvesters and installations
- **Check:** place a harvester deed, power and maintain it, collect output.
- **Who:** Squad (after the body can place structures), Owner.
- **Coverage:** none.
- **Gaps:** no check.
- **Pass:** a placed harvester holds a non-zero hopper after 30 minutes on the test galaxy.

### F. Getting around

#### 17. Shuttles and starports
- **Check:** buy a ticket at a travel terminal, board at the collector, arrive; every loaded planet's ports; Hoth only from Corellia; Ossus from Coronet (3,000 credits).
- **Who:** Squad, Owner (shuttle landing animation, loading screens).
- **Coverage:** `cresh-travel.py` and `cresh-fallback-travel.py` (Mos Eisley and Bestine), `esk-hoth.py` (Tatooine to Corellia to Hoth and back), `esk-recover-home.py`.
- **Gaps:** ticket purchase fails sometimes ("ticket purchase failed", 3 times on 15 Oct). Most of the travel graph has never been walked. Ossus travel has only the owner's first look. BotPop planet moves are jumps, not tickets.
- **Pass:** `cresh-travel.py` "{leg}: buy a ticket" and "{leg}: ride the shuttle" PASS five rounds in a row; a new sweep rides every route in the travel table once with zero failures.

#### 18. Vehicles and mounts
- **Check:** vehicle deeds, call, mount, ride, store, repair (BARC fix); creature mounts; the Hutt's Artisan floater (only that platform for Hutts).
- **Who:** GPT (body support), Squad, Owner (riding feel).
- **Coverage:** none in game; C54 F4 reviewed the Hutt vehicle refusal in source.
- **Gaps:** the body cannot mount (scenarios README, "remaining body gaps"). No check at all.
- **Pass:** a scenario calls a speeder, mounts (state "riding mount" in `status().states`), moves 100 m, and stores it; a Hutt is refused any vehicle except the floater with the exact text.

### G. Owning things

#### 19. Housing and structures
- **Check:** place a house deed, enter, permissions (admin, entry, ban), place and pick up items, maintenance, redeed. **[live rules]** for item limits and maintenance.
- **Who:** Squad (once the body can place), Owner.
- **Coverage:** none.
- **Gaps:** no check. Matrix item F34 (house pack-up) is design only.
- **Pass:** a scenario places a small house, a second bot is refused entry until added, an item placed inside is still there after a restart.

#### 20. Player cities
- **Check:** found a city, citizens, ranks, civic structures, taxes, mayor election, `CitiesAllowed` (no cities on Hoth or Ossus).
- **Who:** GPT (design and source: `player-cities-research.md`, `bot-cities-plan.md`), BotPop (later, simulated towns).
- **Coverage:** research and 13 owner questions only. The `CitiesAllowed` guard is in the release-1 list.
- **Gaps:** no check; zoning rights are "blocked_world: city" for bots.
- **Pass:** placing a city hall on Hoth or Ossus is refused with a message; on Tatooine a test city reaches rank 1 with five citizens.

### H. Social professions and people

#### 21. Groups, guilds, mail and friends
- **Check:** invite, join, leave, group XP split, group loot; guild create, join, chat; mail send and receive with an attachment; friends list online status.
- **Who:** Squad, Owner.
- **Coverage:** `squad.py setup` makes groups (joins "not confirmed" for non-leaders, `OVERNIGHT.md`); `dorn-social.py` "menu: another member offers to switch"; `forn-escort.py` "waypoints mailed to {owner}".
- **Gaps:** no check of group XP split, guilds, friends or mail read back.
- **Pass:** setup shows every member in the group; a two-bot kill gives both bots an XP message; a mail sent from one bot is listed in the other's inbox.

#### 22. Entertainer, musician and image designer
- **Check:** dances and songs, flourishes, the mind buff after watching, instruments, band play, image design.
- **Who:** Squad, BotPop (dancers in town), Owner (dance and music animation).
- **Coverage:** `dorn-social.py`, `aurek-boss-camp.py` ("Sela dances in camp"); BotPop: 2,659 of 2,661 rests watched a dancer (run 3).
- **Gaps:** **"Nima watches Dorn dance" and "gets the dance buff after 70 s" still fail** (`@healing:no_line_of_sight`, no `performance_enhance` message). Music and image design have no check.
- **Pass:** `dorn-social.py` both dance-buff checks PASS.

#### 23. Medic, doctor and hospitals
- **Check:** heal damage and wounds, cure poison and disease, revive, doctor enhancements in a hospital cell, medical XP. **[live rules]**: `MedicalAnywhere = true` lets buffs land outside a hospital on test, so test passes can hide a live failure.
- **Who:** Squad, BotPop, GPT (`Agent/local-research/doctor-enhance-wounds/report.md`, `medic-xp-healing/`).
- **Coverage:** `aurek-doctor-buffs.py`, `aurek-boss-camp.py`, `forn-crew.py` ("Mirren buffs the crew"); BotPop medics heal 109 times an hour each (run 3).
- **Gaps:** **four doctor-buff regressions**: max HAM did not rise for health and action, on Aurek and Jesh (the server answered "You re-apply …", so the buff may already be on, or the check is wrong). `curePoison` NO_EFFECT; `healState` refused. Medic class check pending.
- **Pass:** `aurek-doctor-buffs.py` four "receives … enhancement" checks PASS on fresh, unbuffed fighters; in the dress rehearsal a doctor outside a hospital is refused.

#### 24. Factions, GCW and recruiters
- **Check:** join Rebel or Imperial at a recruiter, faction points, covert and overt, PvP flags, faction missions, bases. The setting work (`Fable-factions/README.md`, option A) will rename sides later; test the stock system first.
- **Who:** Squad, GPT, Owner.
- **Coverage:** none.
- **Gaps:** no check of any faction feature.
- **Pass:** a bot joins a faction at a recruiter (faction shown in `status()`), goes overt, and a second bot of the other side can attack it.

#### 25. Vendors, the bazaar and secure trade
- **Check:** bazaar list and buy; player vendor placement and sale; secure trade of items and credits between two players.
- **Who:** GPT (body API), Squad.
- **Coverage:** none. `esk-fallback-reach.py` only opens the bazaar terminal's radial.
- **Gaps:** secure trade is unsupported in the body (matrix F23). No bazaar or vendor check.
- **Pass:** one bot lists an item on the bazaar and another buys it; both cash values change by the price minus the fee; a secure trade moves one item and 100 credits.

### I. Companions

#### 26. Pets, droids, the helper droid and the mercenary broker
- **Check:** calling, storing and commanding pets; taming (**[live rules]**: `TameAnything = true` on test); droids and droid engineer modules; the helper droid (section 3); Dax Venn's mercenaries; `/leash`.
- **Who:** Squad, Owner.
- **Coverage:** `dorn-social.py` (Dax Venn offers options, leash on and off), `forn-escort.py` (escort crew).
- **Gaps:** "leash brings Nima to Dorn after he stops" still fails (12 m away). No pet or droid command check; "blocked_world: pet" for bots.
- **Pass:** `dorn-social.py` leash check PASS (within 5 m); a new scenario calls a pet, it follows 50 m and attacks a target on command.

### J. Our own worlds and additions

#### 27. Hoth, Ossus and the server additions
Hoth, Ossus, world bosses with Rhea Tannor, the Botanist and Jump to Lightspeed are grouped here because each is either ours or switched on only on the test galaxy.
- **Hoth.** Check: travel from Corellia, the Scavenger outpost, Echo Base doors and rooms, Quartermaster Vell's first job, resources, named loot. Coverage: `esk-hoth.py`, `check_hoth_scenario.py`, `hoth-release-gate.md` (NO-GO), `Fable-hoth-guide/hoth-first-session.md`. Gap: the "no cliff" check failed (43 m rise north of the outpost); the quest has never been run end to end. Pass: `esk-hoth.py` all PASS, and a Squad run of Vell's job pays 1,500 credits.
- **Ossus.** Check: Knossa pad, ramps, terrain, map labels, fauna, the O7 points of interest. Coverage: BotPop 200 Ossus explorers, `ossus_census.py`, `launch-sim/ossus-census.md`, `Owner-test-list.md` section 2. Gap: no Squad bot has travelled there; O7 placements unseen in the client. Pass: a Squad bot flies Coronet to Knossa and back, and the census lists creatures at every planned spawn.
- **World bosses and Rhea Tannor.** Coverage: `cresh-travel.py` ("Rhea Tannor is at the starport", "she talks"), `aurek-boss-camp.py`. Gap: no boss kill or reward check. Pass: a boss kill gives the reward to the top damage dealer.
- **Botanist.** Coverage: `OVERNIGHT.md` 5:57 AM 14 Oct (one bot, trainer). Gap: no recurring check. Pass: trainer skill names show no `@skl_n:` keys.
- **Jump to Lightspeed.** `JTLEnabled = true` and `LaunchFromDevice = true` on test. Coverage: none. Pass: a ship launches from its device and the client loads the space zone. Lowest priority.

## 3. Gaps to close first

Ranked by what breaks a new player's first hour, first.

| Rank | Gap | Why first | Who | Done when |
|---|---|---|---|---|
| 1 | Fresh start: creation of every species, starting city, helper droid on a build with `c5d713b8` — **done 16 Oct:** all 12 species created and through the first minutes (`fresh-start-test.md`, `4a6b431`); **`creation-sweep` 17 Oct:** 24 of 24 species and genders, attributes and the Hutt's S7 row in game, name filter 21 of 21 (section 2). | Every new player passes through it in the first ten minutes; the droid deadlock reached real new players | Main session (build and restart), GPT (`creation-sweep` scenario) | Pass lines of sections 2 and 3 |
| 2 | "The server keeps putting us back" — **done 17 Oct:** section 4's pass line met on run 24, gate PASS with 0 regressions (`movement-pushback.md`, dev `b034d15f`, `7c2f2605`). | Three gate regressions; it hides the mission, harvest and route checks behind it; a real player may see the same rubber-band | Main session (server log at the moment of the push-back), GPT (body vs server source) | Pass line of section 4 and a re-run gate with 0 regressions from it |
| 3 | Training at a real trainer, and the class check for the other five starters | Every profession trains in the first hour; the bots only ever get boxes by command | GPT (`trainer-buy` scenario), main session (class-check slices) | Pass line of section 7 |
| 4 | Missions through the terminal — **mostly done 17 Oct:** 7 of 11 terminal missions complete with exact pay, and the 7th mission is refused (section 11); survey, two recons and bounty left; group-pay fix staged | The only real income for a new character (FINDINGS section 3); Squad mission check is down | GPT after rank 2 | Pass line of section 11 |
| 5 | ~~Crafting session~~ **done 17 Oct** (section 15: 21 of 21) | An Artisan's whole first hour; zero coverage | GPT (body API proposal), main session (C++ body) | Pass line of section 15 |
| 6 | Doctor and entertainer buffs | Four doctor and two dance regressions; town social play | GPT (check logic: "re-apply" receipts on already-buffed fighters) | Pass lines of sections 22 and 23 |
| 7 | Death, cloning and insurance — **done 17 Oct** (section 9: 11 of 11) | About one death per hour for new characters; insurance has no check | GPT (new scenario) | Pass line of section 9 |
| 8 | Spawn danger near cities and the F2 spawn fix — **fixed 16 Oct:** deaths to killers 8+ levels up 25.6% → 5.0% with the creature-level gate (dev `69f5c879`, run 19). | Deaths far from home in the first hour on Naboo, Rori and Talus | BotPop run on `c5d713b8`, owner's T1/T2 choices | Pass line of section 10 |
| 9 | Ticket purchase failures and the untested travel graph — **passed at scale 16 Oct:** BotPop real travel, 66 of 73 shuttle trips (`1fd17e4`). | A failed ticket strands a new player | Squad sweep | Pass line of section 17 |
| 10 | Gas, moisture and wind surveys | Surveying is an Artisan's first task | GPT (body or server) | Pass line of section 13 |
| 11 | Live-rules checks in the dress rehearsal | `MedicalAnywhere`, `TameAnything`, skill points and training cost mask live behaviour | Main session (dress rehearsal) | Each [live rules] pass line seen there |
| 12 | Groups (XP split), mail, guilds, friends | Social play in the first evening | Squad | Pass line of section 21 |
| 13 | Bazaar, vendors and secure trade | Second-day economy; body API missing | GPT | Pass line of section 25 |
| 14 | Vehicles and mounts | Not first-hour; body cannot mount | GPT, main session | Pass line of section 18 |
| 15 | Housing, harvesters, cities, factions | Later play; zero coverage | GPT (scenarios after the body can place structures) | Pass lines of sections 16, 19, 20, 24 |
| 16 | The Hutt is not playable as a player | One species, held back from live already | Main session | Owner can move and chat as a Hutt |
| 17 | Hoth, Ossus, bosses, JTL | Held back from release 1 | As in section 27 | Section 27 pass lines |

## 4. Owner checklist: one in-game session

About 90 minutes on the test galaxy. Answer in your own words; a sentence or two each is plenty. Note where you were (`/loc`) when something looks wrong, and take a screenshot if it is visual. Start the client with the "SWG Test Galaxy" desktop shortcut (`Play SWG Test Galaxy.cmd`). Ask the main session to cut the bots down first, so the PC is not starved.

**The client changes installed today**
1. With DXVK 3.1.1 and the 60 fps cap, how smooth does the game feel in Mos Eisley, in the countryside and in a busy cantina? Where, if anywhere, does it stutter or tear?
2. How does the game look compared with before DXVK: colours, shadows, water, text sharpness? What looks different?
3. With the 4 GB patch, how did the client behave over the whole session: any crash, freeze or slow-down later on? Roughly when?
4. With GPU skinning on (`lodManagerEnable`, 100 characters hard-skinned), how do crowds look: do distant characters move naturally, pop, freeze in pose or lose detail?
5. With the network thread on (`useNetworkThread=true`), how responsive are menus, radials and combat? Where do you see delay or rubber-banding?
6. With the client at Above normal priority, how does the rest of the PC behave while you play: Discord, the browser, alt-tab?

**The Hutt**
7. When you move your Hutt (walk, run, turn, stop), how does it look and feel? What does the body do?
8. What does the Hutt do when idle, when it emotes, sits or kneels, when it fights and when it dies? Which poses look wrong?
9. What happens when you try chat, commands and the radial menu as a Hutt?

**Your first hour as a new character**
10. Make a new character of a species you haven't tried. What was creation like: sliders, colours, hair, the description, the name check?
11. How did the first minutes feel: the tutorial or the skip, landing in the city, the helper droid?
12. At a trainer, how clear was the window, the price and what you got?
13. What was the first fight like: the animations, the sounds, the combat text, how fast it went?
14. If you die or are incapacitated, what did the clone window and the trip back look like?

**Looks and feel around the galaxy**
15. Ride one shuttle. How do the landing, the boarding and the loading screen look?
16. Watch a bot dance or play near the cantina. How do the dance and music animations look?
17. Open the crafting window with any tool. How does it read and feel?
18. On Hoth (Echo Base corridors) and on Ossus (the Knossa pad and the ground around it), what looks wrong: textures, lighting, sky, places you got stuck?
19. Which window, text or message anywhere looked broken, raw (`@…`) or hard to read?
20. What, if anything, made you want to stop playing?

Results go back to the main session in your own words; it checks the logs for each answer before calling anything fixed.

## 5. Real-client session, 17 Oct: the interaction loss

Claude (real-client session), 17 Oct, 5:10 AM. Main target: the intermittent loss of interaction the owner saw on 16 Oct (radials, NPC conversations, terminals or commands stop responding; headless bots never notice it). Section 4's list stays for a longer session; this one takes about 40 minutes and repeats the same small set of interactions at each stop, so a failure can be pinned to a time and a place.

**The round (R), under a minute, at every stop below.** (R1) Right-click an NPC: does the radial open? (R2) Right-click a terminal and pick its main option: does its window open? Close it. (R3) `/sit`, then `/stand`. (R4) Say one line in spatial chat.

**If anything stops responding.** Press **Insert three times** (the input listener writes the exact second), keep trying the same thing for up to a minute, and remember whether it came back by itself and roughly when. Don't relog to fix it unless it lasts more than two minutes. Tell Claude afterwards, in your own words.

| Step | Where | What | About |
|---|---|---|---|
| 1 | Log in | Start with the SWG Test Galaxy shortcut, pick the character, then R where you land | 3 min |
| 2 | Mos Eisley terminals | Bank terminal (open, close), character builder (open one page, close), travel terminal (open the ticket window, close) | 4 min |
| 3 | NPC conversations | Talk to a trainer and open its training list; talk to one more NPC that has a conversation | 4 min |
| 4 | Cantina | R inside (indoor cell, busy); watch a bot dance for a minute | 5 min |
| 5 | Mission terminal | Open the list, accept one destroy mission | 4 min |
| 6 | Outside town | Fight one creature with two or three hotbar specials; then right-click the corpse and loot it | 6 min |
| 7 | Shuttle | Buy a ticket Mos Eisley to Bestine and ride it; R as soon as you land | 7 min |
| 8 | Idle and alt-tab | Stand still for 2 min without touching anything, then R; alt-tab to another window for 1 min, come back, R | 4 min |
| 9 | Relog | Log out to character select, log back in, R | 3 min |

**Questions afterwards (answer in your own words).** Did anything stop responding? For each time: what were you doing, what stopped (radial, window, conversation, command, chat, movement), did it come back, after how long, and what brought it back? How did the game feel overall: smooth or stuttering, and where? What else looked wrong?

**What Claude records meanwhile** (read-only; nothing on the galaxy changes):
- Windows, every 2 s: total CPU, the client's CPU (percent of one core), whether Windows says its window is responding, its memory, VmmemWSL's CPU.
- WSL, every 2 s: load average, WSL CPU, core3's CPU; the console log with wall-clock times; per-second UDP packet counts for each client port on the zone and login ports, so a stall can be split into "the client sent nothing", "the server did not answer" and "both kept talking".
- `core3.log` (it has wall-clock times) and `who.json` for the owner's session; the input listener's key and click times (with the owner's OK).
- BotPop stays as it is (300 bots, WSL load about 1.5 at 5:00 AM), so a failure at this load tests the 16 Oct explanation (CPU starvation at 1,700 bots).

### Results, 17 Oct, 5:32 to 5:48 AM

**Conditions.** [name removed] (admin, the Chiss that lost interaction on 16 Oct) on the test galaxy's run 24 (the galaxy owner's new dev build, restarted 5:24 to 5:26 AM, before the client started at 5:27:47). BotPop "all" at 300 throughout (console: `online 300, active avg 300`; re-spawned at about 5:28). The galaxy owner's bot work overlapped the session, and its load is included in the readings below: the gate (five squad groups) 5:29 to 5:38, esk-routes and a Besh probe 5:40 to 5:47, esk-routes 5:47 to 5:50. The client was started with the test launcher (Above normal priority, DXVK, LAA). The owner played about 15 minutes and logged out at 5:48:08; the full 40-minute list was not finished.

**The owner, in their own words.** *(Waiting for the owner's answers to the four questions above.)* During the session they sent two tells to the Esk bot: "the bots are moving correct lanes and such but, 1 their nowhere near looking like an actual population the way their moving. and im concerned their not progressing/ building guilds and cities and working together" (passed to the BotPop social-play session at their request), and "could you tell me what im testing here myself?" (answered in chat).

**What the logs show** (scripts and raw data: the session's scratchpad, `rc/`):

| Evidence | Value (Windows rows: client running 5:27:47 to 5:48:09, character select included; the rest: logged in 5:32:44 to 5:48:08) |
|---|---|
| Windows says the client is responding | 602 of 602 samples (every 2 s); never "not responding" |
| Client CPU, percent of one core | median 20, max 89 |
| Windows total CPU | median 21%, max 70% (16 Oct failure: 97%) |
| Client memory | median 801 MB, max 830 MB |
| WSL load average | max 2 of 12 threads (16 Oct failure: 9.7) |
| core3 CPU, percent of one core | median 56, max 108 |
| Zone packets, session port 61325 | traffic in 903 of 925 seconds. The client was never sending without the server answering. Silent gaps (nothing either way): 5 s at 5:45:20, while the client was not in front; 2 to 6 s each at 5:46:58, 5:47:03, 5:47:12, 5:48:03 and 5:48:06, between character select and logout. Client quiet for 4 s at 5:32:46, while the server sent the login's object data |
| `core3.log` for the session | login 5:32:45 (`Player 281474994121128 logged in.`); `CheckupTime` changes at 5:41:03 and 5:46:54; logout 5:48:08 `Disconnecting client, hasError = false`. No error or warning for this session |
| Rubber-band lines (`[Movement] ... bounce`, new in run 24) | none for [name removed] (`0x100000109A9A8`); the only 10 lines are five bots at 5:29:47, before login |
| Input listener | gate open eight times (the owner switched windows often); 29 right-clicks, 71 left-clicks; **no Insert presses** |
| Client crash dumps | none new (the newest is 16 Oct, 11:12 PM) |

**Reading.** At 300 bots, with the PC at about a fifth of its CPU, the session shows no sign of the interaction loss. The client always responded, the server always answered, and the logout was clean. This fits the 16 Oct explanation (CPU starvation at 1,700 bots) but does not prove it. The session was short and covered part of the list, and the owner's own account is still to come. The per-second packet counts show that the session talked both ways. They cannot show whether a particular radial request got its particular answer: the packets are encrypted, and the counts are per second.

**Next, proposed (not done).** (1) A repeat at 1,000 to 1,700 bots with the same monitors would test the starvation explanation directly, if the owner wants it. (2) The full 40-minute list (shuttle, fight, relog, idle) is still unplayed. (3) Not part of this test: `Play SWG.cmd` (live) keeps the client's login address as it is, and that address is the old WSL NAT address `172.23.208.109:44453`. Since WSL moved to mirrored networking it is `192.168.1.210`, so the live launcher probably cannot reach the live galaxy when it next runs (the test launcher writes the current address each time).
