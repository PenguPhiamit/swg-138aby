# Fresh start and spawn danger (test plan gaps 1 and 8)

Claude (side session), 16 Oct, 10:45 PM to 11:30 PM, on the test galaxy during run 18 (dev `d4b9d9a1`, optimised
build, 1,700 BotPop bots online). Nothing under `/opt/swg` was changed and no console or botpop command was sent.

- **Part 1:** one new character for each of the 12 species the server offers, created through the agent client (real
  login and creation packets). Driver: `tools/bots/fresh_start.py` (new). Raw rows:
  `fresh-start/results-20261016.json`.
- **Part 2:** why the spawn level gate doesn't protect new characters, where the killers spawn, and a patch:
  `fresh-start/spawn-gate-creature-level.patch`.

## Summary

- **Creation works for all 12 species.** The template the server built matched the species asked for every time
  (object CRC check). 12 characters were created in parallel within 48 s while 1,700 BotPop bots ran, and the Wookiee
  at 11:07 PM. Each one landed
  in the skip-tutorial room.
- **Helper droid works.** It was beside every character in its city. Its menu answered in 0.3 s, and "how to travel"
  opened its page in 0.3 s. Over the whole test the console had no deadlock or lock-timeout line.
- **First trainer box bought by 13 of 13**, through the real trainer conversation (not `/agentskill`). Each paid 25
  credits.
- **Fight: 7 of 13 hit a real creature** (5 kills, 2 runs stopped at the 60 s limit). Two picked a load-lifter droid
  that takes no damage (my target choice). Four found no creature within about 500 m of Bestine or Kaadara.
- **The tutorial is off** (`Core3.PlayerCreationManager.EnableTutorial` defaults to false, as in stock). A player who
  chooses the tutorial gets the skip-tutorial room with no message.
- **Only 9 starting cities are valid**, and every Talus and Rori city is missing from that list.
- **Spawn danger is caused by the gate's design, not by the C55 F2 change.** The gate compares a table row's *minimum
  difficulty* with `10 + 3 × level`. A lair's creatures keep their own fixed template levels. 144 of the 164 deaths to
  killers 8 or more levels up came from rows the gate lets through. The patch also gates on the lair's strongest
  creature.
- **"Worse than run 13" is mostly a comparison artefact.** Over the same first 17 minutes, run 13 was at 10.9%, not
  5%, and it ran on the overloaded Debug build. Details in Part 2.

## Part 1: one new character per species

How each run went (`fresh_start.py ACCOUNT run NAME RACE PROFESSION CITY`):

1. Create with the client's JSON `createCharacter` action; it can set the tutorial flag. The client logs out once it
   has created the character.
2. Log in again by first name.
3. Read `status`, and `inspect` self to compare the template CRC with `object/creature/player/shared_<race>.iff`.
4. `newbieSelectStartingLocation <city>` from the skip room.
5. Look for the helper droid, open its menu, and pick "how to travel".
6. `/agentpath find` a trainer of another starting profession (the character's own novice box comes with creation,
   and its second box needs XP). Walk there, talk, then choose "what can I learn", the box, and "yes".
7. Fight the nearest creature found by `look` that is at most 8 levels up, walking out of town on up to three legs.
8. List the inventory, then collect the core3.log ERROR lines from the run.

Most of this ran in four parallel batches: 13 bodies at 11:04 PM, 13 at 11:07 PM, 13 at 11:11 PM and 5 at 11:17 PM.
Batches 2 to 4 logged the characters made in batch 1 back in, after I fixed driver bugs: missed reply events, the
wrong city names below, and a town NPC picked as a fight target. All accounts are existing bot accounts; each
character is an extra one on its account and the account's own character was left alone.

| Species | Character (account, profession) | Created, species | Landed, then city | Droid (menu / answer) | Trainer box (cash) | Fight | Starting HAM (H/A/M) | Result |
|---|---|---|---|---|---|---|---|---|
| Human (female) | Selane Varrick (dorn1, Entertainer) | 11:04 PM, match | skip room, Bestine | yes (0.3 s / 0.3 s) | Novice Scout (10,000 to 9,975) | none within ~500 m on 3 legs | 600/1100/900 | pass; fight not done |
| Human (male), tutorial chosen | Halden Merrow (esk3, Marksman) | 11:05 PM, match | **skip room** (tutorial is off), Mos Eisley | yes (0.3 / 0.3) | Novice Scout (25 cr) | rockmite L8: **killed** (57 s) | 1100/900/700 | pass, see Q1 |
| Human (male), by hand | Torvane Quillet (esk1, Marksman) | 10:53 PM, match | skip room, Mos Eisley | droid at 1 m on arrival; travel page | Novice Scout (25 cr) | not tried | 1100/900/700 | pass (manual, 10:53 to 11:00 PM) |
| Zabrak (male) | Kordo Haxtel (dorn2, Brawler) | 11:04 PM, match | skip room, Mos Espa | yes (0.3 / 0.3) | Novice Scout (25 cr) | CLL-8 load lifter L4: no damage in 18 attacks (a droid NPC, my bad pick) | 1200/1100/500 | pass; fight invalid |
| Twi'lek (female) | Imari Dossel (dorn3, Medic) | 11:04 PM, match | skip room, Coronet | yes (0.3 / 0.3) | Novice Scout (25 cr) | CLL-8 load lifter: as above | 600/950/1100 | pass; fight invalid |
| Rodian (male) | Pekko Rindalt (cresh1, Marksman) | 11:04 PM, match | skip room, Tyrena | yes (0.3 / 0.3) | Novice Scout (25 cr) | corellian butterfly L7: health 276 to 153, 60 s limit | 1000/1000/600 | pass |
| Trandoshan (male) | Grashuk Volnar (cresh2, Scout) | 11:04 PM, match | skip room, Kor Vella | yes (0.3 / 0.3) | Novice Brawler (25 cr) | butterfly drone L5: **killed** (41 s) | 1050/800/700 | pass |
| Mon Calamari (female) | Neela Quorvin (cresh3, Artisan) | 11:04 PM, match | skip room, Theed | yes (0.3 / 0.3) | Novice Scout (25 cr) | chuba L5: **killed** (47 s) | 600/800/1200 | pass |
| Wookiee (male) | Rrowkah (forn1, Brawler) | 11:07 PM, match. "Rrowkah Taarv" refused first: `name_declined_racially_inappropriate` (stock: no Wookiee surnames, `NameManager.cpp:357`) | skip room, Moenia | yes (0.3 / 0.3) | Novice Scout (25 cr) | domestic falumpaset L10: health 1370 to 1362 in 21 attacks, 60 s limit | 1350/1000/600 | pass |
| Bothan (female) | Telsa Brevin (forn2, Marksman) | 11:04 PM, match | skip room; `keren` refused; Kaadara | yes (0.3 / 0.3) | Novice Scout (25 cr) | none within ~500 m | 1000/1100/700 | pass; fight not done |
| Ithorian (male) | Ommor Vashtel (forn3, Medic) | 11:04 PM, match | skip room; `narmle` refused; Theed | yes (0.3 / 0.3) | Novice Scout (25 cr) | chuba L5: **killed** (49 s) | 1000/800/1200 | pass |
| Sullustan (female) | Dabbi Sorrin (forn4, Entertainer) | 11:04 PM, match | skip room; `restuss` refused; Bestine | yes (0.3 / 0.3) | Novice Scout (25 cr) | none within ~500 m | 650/1250/1000 | pass; fight not done |
| Chiss (male), archive species | Varrin Okkaro (forn5, Scout) | 11:04 PM, match | skip room; `dearic` refused; faction row `tatooine_imp` put him in Bestine | yes (0.3 / 0.3) | Novice Brawler (25 cr) | none within ~500 m | 900/900/800 | pass; fight not done |
| Hutt (male), archive species | Borgo Tashuri (esk2, Artisan) | 11:05 PM, match | skip room, Mos Eisley | yes (0.3 / 0.3) | Novice Scout (25 cr) | rockmite L8: **killed**, but left at **31 of 700 health** | 700/800/900 | pass server-side; see Q4 |

**Starting inventory** (from `inventory` after the first minutes):

- Every character had a survival knife, a foraged fruit, a generic crafting tool, an `@pet_deed:landspeeder_x31`, the
  helper droid's control device in the datapad, and an `unknown_weapon` in the hand slot.
- By profession:
  - Marksman: CDEF pistol, carbine and rifle.
  - Brawler: heavy-duty axe, stone knife and wooden staff; the Wookiee also had a bowcaster.
  - Medic: a food tool.
  - Entertainer: a slitherhorn.
  - Artisan: a second generic tool.
- Clothes: each species got its own set (the Ithorian `ith_*`). **The Hutt had no clothes at all.**
- The scout trainer's box also brought the helper droid's crafting-tool step (`@new_player:given_crafting_tool`).
- Every new character starts with **10,000 cash and 100,000 bank** on this galaxy.

**Server errors in core3.log from 10:53 PM to 11:22 PM** (all kinds):

- **791 × `BaseClient::handleNetStatusRequest … StreamIndexOutOfBoundsException at 8`**, every 5 s from each agent
  client's session (`192.168.1.210`, the WSL host). It is the agent body's NetStatus packet. A real client doesn't
  send it, and nothing broke.
- **14 × `decreaseOnlineCharCount missing account N in onlineZoneClientMap`**, one per creation. They come from the
  client logging out straight after creation, before it enters the world (the JSON create path). A real player who
  quits at that moment would log the same harmless line.
- No ERROR at login, at the city move, at the droid, at the trainer or in the fights. No deadlock, lock-timeout or
  lock-trace line.
- The five bad city names logged only an INFO line (`Attempted to start at invalid starting location: keren.`). The
  player gets no message at all.

**Against the test plan's pass lines:**

- **Section 2 (creation).** Every species created, logged in and reported its expected species with non-zero HAM. Not
  covered: both genders of every species (7 male and 5 female here) and deleting the characters afterwards (they are
  still on the test galaxy). The Hutt's HAM against the approved S7 row isn't checked here (see Q4).
- **Section 3 (droid).**
  - 12 creations ran in parallel, and the radial round trip was 0.3 s in every batch of 5 to 13 bodies, with no lock
    line.
  - Caveat: the droid's appearance on the first city arrival was timed only by hand (Torvane: there at once). The
    batch driver missed that moment and saw the droid on the next login (0 s, 13 of 13).
  - The full tutorial can't be walked while it is switched off.

**Driver notes** (agent body, not the game):

- `talk` right after a long `move` is ignored until one more short step. The server checks the last *validated*
  position against 5 m.
- `path` only plans; `move` walks.
- A CLL-8 load lifter has an `@mob/creature_names:` name, so creature filters need a level or faction check.

## Part 2: spawn danger near the cities

### What the gate does and doesn't stop

The gate (`SpawnAreaImplementation.cpp:303-307` at `d4b9d9a1`) skips a spawn-table row when all of these hold:

- `LevelGateBase > 0`;
- the player's level is below `LevelGateMaxLevel`;
- the row's `minDifficulty > LevelGateBase + 3 × level`.

The test galaxy's `config-local.lua` sets neither `Core3.SpawnArea.LevelGateBase` nor `LevelGateMaxLevel`, so both
are at their default of 10.

- **The level is the weapon's.** It comes from `calculatePlayerLevel`, `min(25, private_<weapon>_combat_difficulty /
  100 + 1)`. Launch bots are in the spawn registry only in observer mode, so "all" mode bots do make the world spawn
  (`BotPopManager.h:547`). Their `lvl` column in the event log is this same value: 2 or 3 for 160 of the 164
  high-gap deaths.
- So the threshold for these characters is **16 (level 2) or 19 (level 3)**.
- **A row's minimum isn't the level of its creatures.** `tryToSpawn` uses the row's min and max only to pick the
  lair's building level. The creatures come out at their own template level: a giant worrt is level 13 in a row that
  starts at 15, and a greater desert womp rat is level 22.
- **173 rows a level-2 character can draw hold a creature of level 20 or more.** Among them is the canyon krayt dragon
  pack (dragons of level 122 and 275), whose rows start at **1** in `tatooine_hard_dune_sea`,
  `tatooine_medium_valarian_ne` and `tatooine_hard_alkhara_ne`.

### Where the killers come from

Source: `botpop-launch.jsonl`, death rows up to 11:12 PM (run 18, minutes 0 to 46): 673 deaths, of which **164
(24.4%)** were to a killer 8 or more levels above the bot. For each of the 164, I looked for spawn areas
(`managers/planet/<planet>_regions.lua`) at the death's x/y whose table holds a lair template containing the killer:

- **144 (88%)** came from a row whose minimum passes the gate for that bot. The gate can't stop these.
- 17: no spawn-area row at that spot holds the killer. These are static spawns and camps: Black Sun initiates near
  Nashal, Restuss's swamp-rat camps, Garyn's thieves near Narmle. Or the creature followed from elsewhere.
- 3: the row was above the gate (spawned for someone else, or pulled from further away).

| Killer (level) | Deaths | Table row (min to max) |
|---|---|---|
| giant_worrt (13) | 33 | `tatooine_mos_eisley_se_hard` (15 to 20) |
| greater_shaupaut (14) | 17 | Naboo planet-wide `northeast`, `plains_1`, `northwest` (5 to 500) |
| greater_desert_womp_rat (22) | 8 | `tatooine_mos_eisley_se_hard` (15 to 20) |
| rogue_bageraset (13) | 9 | Corellia `grassland1`/`grassland5` (10 to 500) |
| mutant_womp_rat (13) | 6 | `tatooine_mos_eisley_se_hard` (15 to 20) |
| scyk (12) | 8 | `mos_eisley_se_medium` (10 to 15), `anchorhead_medium_newbie` (6 to 10) |
| highwayman (10) | 5 | `mos_eisley_se_medium` (10 to 15) |
| shaupaut_hunter (22) | 5 | Naboo `northeast`, `plains_1` (5 to 500) |
| narglatch_hunter (12) | 7+ | Naboo newbie tables (`moenia_easy_newbie`, `kaadara_easy_newbie`, 1 to 8) |

**Relative to the cities:**

- **`mos_eisley_se_hard` is a stock rectangle from (-2909, -7700) to (7841, 930).** It covers Mos Eisley, Anchorhead
  and Bestine and overlaps their newbie circles and rings. **Anchorhead alone has 57 of the 164.** Giant worrts killed
  bots 24, 37, 82 and 92 m from Anchorhead's start point.
- Naboo's planet-wide tables start at 5 and cover all four Naboo cities.
- Distance from the bot's start point to its death: quartiles **460, 805 and 1,279 m**. 25 deaths were within 300 m
  and 48 within 500 m.
- 154 of the 164 were brawlers or scouts. In 159 the killer attacked first (an `aggro` row by the killer); in 76 of those
  the bot was resting.

### Why run 18 looks worse than run 13

- **The windows differ.** Run 13's 4.9% is over 193 minutes, by which time bots have outlevelled what is near town.
  Over the first 17.5 minutes of each run:
  - run 13 (`botpop-launch.jsonl.1955.old`): 16 of 147 deaths, **10.9%**;
  - run 18: 79 of 302 deaths, **26.2%**.
- **The gate didn't change for these bots.** `b20a46d7` is in run 13's build (`a8ece12b`), and F2 only removed the gate
  for levels 10 and up.
- **The server did change** (likely cause, not proven). Run 13 ran on the Debug build: worst tick 2.1 s, 153 skipped
  passes. Run 18 runs the optimised build (worst tick 4 ms). In the same 17.5-minute window, incapacitations rose for
  every combat role: marksman 88 to 481, brawler 153 to 455. Brawler deaths went from 53 to 163. Creatures that once
  acted on a slow server now attack at full speed.

### The fix: gate on the creature, not only the row

`fresh-start/spawn-gate-creature-level.patch` (against Core3-dev `d4b9d9a1`, one file):

- **Inside the existing gate** (level below `LevelGateMaxLevel`, so masters are unchanged), a row is also skipped
  when the strongest *regular* mobile of its lair template is more than **`Core3.SpawnArea.LevelGateCreatureMargin`**
  (default 7, 0 = off) above the player. Template levels come from `CreatureTemplateManager`.
- Boss mobiles are left out, because they appear only once the lair is attacked.
- **Checks:** `git apply --check` passes on `/opt/swg/Core3-dev` at `d4b9d9a1`, and a `clang++ -fsyntax-only` compile
  of the patched file with the dev build's flags succeeded (11:13 PM). Nothing was built or deployed.
- **Untested in game.** It needs a dev build and a restart (the main session), then a BotPop run.
  - Pass line: deaths to killers 8+ levels up under 2% (test plan section 10).
  - A level-25 character must still see krayts (unchanged: the gate stops at level 10).
- **Expected effect** (from the tables, not measured): all 144 spawn-area killers above are filtered out for
  characters of the level they killed. The static and camp spawns (17) stay.

What a level-2 character can still draw within 900 m of each start point, as a share of all table weight there
(gate now, then with the patch), and the strongest creature:

| City | Weight share | Strongest creature |
|---|---|---|
| Mos Eisley | 60% to 36% | 22 to 9 |
| Bestine | 43% to 26% | 275 to 8 |
| Mos Espa | 56% to 22% | 25 to 7 |
| Mos Entha | 14% to 13% | 10 to 7 |
| Anchorhead | 47% to 21% | 275 to 8 |
| Coronet | 24% to 23% | 17 to 9 |
| Tyrena | 32% to 25% | 17 to 9 |
| Kor Vella | 11% to 10% | 17 to 9 |
| Theed | 43% to 30% | 31 to 9 |
| Moenia | 33% to 16% | 32 to 9 |
| Keren | 31% to 17% | 32 to 9 |
| Kaadara | 32% to 18% | 32 to 9 |
| Dearic, Nashal | unchanged (21%, 16%) | 7 |
| Narmle | 8% to 7% | 12 to 7 |
| Restuss | 50% to 42% | 12 to 7 |

**Not patched** (owner's call or other sessions):

- Shrinking `mos_eisley_se_hard` away from the three towns. It is stock data, and the patch makes it safe for levels 1
  to 9 anyway.
- C58 finding 1: the gate's level is the weapon in hand, not the character's best. It is still open, and it matters
  for veterans holding another line's weapon.
- The agent body's NetStatus packet.

## For the owner (in game)

1. **Tutorial.** It is switched off (stock default). The creation screen still offers it, and choosing it lands you
   in the skip room without a word. Do you want the tutorial on (then someone walks it in the real client), or should
   choosing it say something?
2. **Creation screen.** Do the species descriptions, sliders and looks read right for each species, especially the
   Chiss and the Hutt? The agent client can't see that screen.
3. **Starting cities.** The list has 9 cities and 9 faction rows (Imperial, Rebel and Privateer starts for Tatooine,
   Corellia and Naboo; `tatooine_imp` put the Chiss in Bestine). No Talus or Rori city can be chosen. Is that what you
   want, and what does the skip-room picker show you?
4. **The Hutt.**
   - It starts with no clothes at all.
   - Its starting HAM as an Artisan is 700/800/900.
   - It needed nearly all its health (31 of 700 left) to kill a level-8 rockmite next to Mos Eisley.
   - Does that feel right for a Hutt, and can you now move and act as one in the real client (gap 16)?
5. **The gate's margin.** With 7, a level 1 to 9 character meets nothing more than 7 levels above it. Mos Espa keeps
   22% of its table weight within 900 m, Anchorhead 21%. Is that the danger you want near town, or a looser margin
   (for example 10)?
6. **Training.** The trainer conversation and the box purchase work. How do the trainer window and the price
   (25 credits for a novice box) look to you, and is 25 the price you want on live?
7. **The purse.** New characters here start with 10,000 cash, 100,000 bank and an X-31 landspeeder deed. Is that only
   for the test galaxy, or meant for live too?
