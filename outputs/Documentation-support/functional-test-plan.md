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
- **Coverage:** `squad.py setup` creates missing characters, but for the bots' own species only. `hutt-c54.md`: an agent-client Hutt (`huttcheck`) was created and its server side works. `Owner-test-list.md` section 1: Chiss by hand.
- **Gaps:** **no scenario creates every species and gender.** The Hutt's racial row and limits (C54 F2) and its creation text (F3) are still open. Name filter cases have offline tests only.
- **Pass:** a new `creation-sweep` scenario creates 24 characters (12 species × 2 genders, where the gender exists), each logs in, reports `status()` with the expected species and non-zero HAM, then is deleted; the console has no creation errors; the Hutt's HAM matches the approved S7 row.

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
- **Gaps:** **the gate's largest failure.** "The server keeps putting us back (blocked, rooted or dead)" broke three checks on 15 Oct (Besh hide patrol, Cresh mission terminal, Esk plateau), and is the top server gap in `bot-gap-list/report.md`. Nobody has shown yet whether it is the bot body or the server's position check. BotPop has no collision (it walks through walls), so its movement proves nothing here.
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
- **Gaps:** **no insurance check at all.** No check of clone-location binding, wounds after cloning or item decay.
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
- **Coverage:** `cresh-missions.py` (destroy only); BotPop run 8: 2,358 completed missions, 3,218,196 credits paid. `review-C44/F1-fix.md` lists the crafting-mission checks.
- **Gaps:** **`cresh-missions.py` regressed** ("reach the mission terminal" FAIL, then two checks did not run) because of the movement gap. Only destroy missions have a Squad check. Crafting missions (`db5952f5`, `74fa3e8c`) need an in-game test. The full-datapad gate (C56) is not run. Bounty, faction and recon have no check at all.
- **Pass:** `cresh-missions.py` checks "the mission completes" and "the reward reaches the bank" PASS; one PASS each for deliver and crafting missions in new scenarios; the seventh mission on test is refused with the exact message.

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
- **Gaps:** `besh-harvest.py` regressed (hide patrol unreachable, same movement gap); ordinary wild prey near the patrol spots is scarce.
- **Pass:** `besh-harvest.py` "Pell receives new {kind} resource container" PASS for meat, hide and bone.

#### 15. Crafting, experimentation and factories
- **Check:** the crafting window, schematic list, ingredient slots, assembly, experimentation, the finished item; tools and stations; factories and schematics; Artisan XP. **[live rules]** for `CraftSeconds` and factory time.
- **Who:** GPT (new body API and scenario), Squad, Owner (crafting window feel).
- **Coverage:** `besh-fallback-crafting.py` reports BLOCKED by design: the body has no crafting session API.
- **Gaps:** **no crafting check exists at all.** Artisan is a starting profession, so this is a crafter's whole first hour. BotPop leaves Artisans out.
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
| 1 | Fresh start: creation of every species, starting city, helper droid on a build with `c5d713b8` | Every new player passes through it in the first ten minutes; the droid deadlock reached real new players | Main session (build and restart), GPT (`creation-sweep` scenario) | Pass lines of sections 2 and 3 |
| 2 | "The server keeps putting us back" | Three gate regressions; it hides the mission, harvest and route checks behind it; a real player may see the same rubber-band | Main session (server log at the moment of the push-back), GPT (body vs server source) | Pass line of section 4 and a re-run gate with 0 regressions from it |
| 3 | Training at a real trainer, and the class check for the other five starters | Every profession trains in the first hour; the bots only ever get boxes by command | GPT (`trainer-buy` scenario), main session (class-check slices) | Pass line of section 7 |
| 4 | Missions through the terminal | The only real income for a new character (FINDINGS section 3); Squad mission check is down | GPT after rank 2 | Pass line of section 11 |
| 5 | Crafting session | An Artisan's whole first hour; zero coverage | GPT (body API proposal), main session (C++ body) | Pass line of section 15 |
| 6 | Doctor and entertainer buffs | Four doctor and two dance regressions; town social play | GPT (check logic: "re-apply" receipts on already-buffed fighters) | Pass lines of sections 22 and 23 |
| 7 | Death, cloning and insurance | About one death per hour for new characters; insurance has no check | GPT (new scenario) | Pass line of section 9 |
| 8 | Spawn danger near cities and the F2 spawn fix | Deaths far from home in the first hour on Naboo, Rori and Talus | BotPop run on `c5d713b8`, owner's T1/T2 choices | Pass line of section 10 |
| 9 | Ticket purchase failures and the untested travel graph | A failed ticket strands a new player | Squad sweep | Pass line of section 17 |
| 10 | Gas, moisture and wind surveys | Surveying is an Artisan's first task | GPT (body or server) | Pass line of section 13 |
| 11 | Live-rules checks in the dress rehearsal | `MedicalAnywhere`, `TameAnything`, skill points and training cost mask live behaviour | Main session (dress rehearsal) | Each [live rules] pass line seen there |
| 12 | Groups (XP split), mail, guilds, friends | Social play in the first evening | Squad | Pass line of section 21 |
| 13 | Bazaar, vendors and secure trade | Second-day economy; body API missing | GPT | Pass line of section 25 |
| 14 | Vehicles and mounts | Not first-hour; body cannot mount | GPT, main session | Pass line of section 18 |
| 15 | Housing, harvesters, cities, factions | Later play; zero coverage | GPT (scenarios after the body can place structures) | Pass lines of sections 16, 19, 20, 24 |
| 16 | The Hutt is not playable as a player | One species, held back from live already | Main session | Owner can move and chat as a Hutt |
| 17 | Hoth, Ossus, bosses, JTL | Held back from release 1 | As in section 27 | Section 27 pass lines |

## 4. Owner checklist: one in-game session

About 90 minutes on the test galaxy. Answer in your own words; a sentence or two each is plenty. Note where you were (`/loc`) when something looks wrong, and take a screenshot if it is visual. Start the client with `Start SWG (above normal).cmd` in `SWG-client/`. Ask the main session to cut the bots down first, so the PC is not starved.

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
