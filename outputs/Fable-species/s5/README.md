# Chiss S5: the first Chiss on the test galaxy — Fable, 14 Oct 2026

Stage only; read-only on /opt/swg (dev HEAD 8f2072e7 when built; the eight C++/Lua files the patch touches have no
commits since e9094960, so it also fits HEAD + Ossus); nothing in h/tools or Local-content touched. Your calls applied:
species id 0xE7, per-gender humanRigRaces pairs, Races.h kept manual. **Verified** = checked offline here; **staged** =
not yet built, run or seen.

| path | what |
|---|---|
| `local_planets.tre` | test-session archive = the O5 build (Hoth + Ossus) + `stage_species(['chiss'])`; **sha256 b1a0a232a13072cd5a2805a5e0f53ebd0b89da348aaf5a4af4abe8020fc46354**, 3,784,927 B, 55 entries |
| `build_test_archive.py` | the wrapper (builder main → stage_ossus → stage_species → tre_write), writes `checks.json` |
| `patch/species-chiss.patch` | one dev patch: S4's C++ (8 files) + S3's Lua (objects.lua append, two includes, two new race templates); 10 files, +105/−17; `git apply --check` clean, luac ok on the five Lua files |
| `checks.json` | the numbers below |

## 1. Client (verified offline)

The O5 rebuild inside the wrapper is byte-identical to `o5/local_planets.tre` (254d0e49…), so Chiss is added to exactly
that. Of O5's 38 entries **35 are byte-identical**; **3 change only by Chiss rows**: `datatables/skill/skills.iff`
(+1 row, `species_chiss`, on top of the Botanist rows), `string/en/skl_n.stf` and `skl_d.stf` (+1 key each). **17 new
entries**: `racial_mods` and `attribute_limits` (+1 block each), five customization tables, `default_pc_hairstyles`,
`default_pc_equipment`, six `profession_defaults_*` (seven PTMP tables +2 blocks each; `_jedi` has no per-species block
and is written unchanged), `ui/ui_avatardata.inc` (+1 block), `player_species.stf` (+2 keys), the ACST
(`customization/asset_customization_manager.iff`, served from today's stock copy; Chiss needs no splice). Both planets
remain registered (planet CRC, travel columns `… yavin4, hoth, ossus`, rows, waypoint rows). Closure from the two Chiss
player templates (`shared_chiss_male/female.iff`, MTG patch 023, the human rig): 134 files, the only 18 "missing" are
stock human voice `.snd` files that the stock human templates miss identically (a stock gap, silent emotes at worst).

## 2. Server (staged; `git apply --check` clean, luac ok)

`patch/species-chiss.patch` = S4's `cpp/species-chiss-human-rig.patch` unchanged (Races.h: the Chiss male/female rows in
the six arrays and `RACE_COUNT` replacing the hard-coded 19/20; `CreatureObject.idl`: `CHISS = 0xE7`, `getSpeciesName()`
"chiss"; `DirectorManager.cpp`: `SPECIES_CHISS`; `PlayerCreationManager.h/.cpp`: `humanRigRaces` loaded from Lua +
`canWearRace()`; `PlayerContainerComponent.cpp:34` and `CreatureManagerImplementation.cpp:1303` use it; the
`humanRigRaces` pairs in `player_creation_manager.lua`) + S3's Lua: `object/creature/player/chiss_male.lua`,
`chiss_female.lua` (new; dev shape, baseHAM 100s, startingSkills `species_chiss` + Basic), the two shared declarations
appended to `object/creature/player/objects.lua`, two `includeFile` lines after `zabrak_male.lua` in
`serverobjects.lua`. Player creation reads `racial_mods.iff`, `attribute_limits.iff` and the `profession_defaults_*.iff`
from the archive (TreFiles, local_planets first), keyed by template with the human fallback; starting locations are
species-independent; names: `NameManager::getSpeciesData` switches on the species id, unlisted species take the human
tables (S4 §S4b), so Chiss names are human names until a Chiss list is written.

**Build needs:** `CreatureObject.idl` → idlc regenerates `CreatureObject.h`; `Races.h` is included by the player/creature
managers, so expect a near-full rebuild; the three `.cpp` files recompile; the Lua needs none. Install the archive on
server (`/opt/swg/tre/local_planets.tre`) and client, restart. Nothing else to configure.

## 3. Owner check (one test-session client visit, after the build and restart)

1. Character creation: the species list shows **Chiss** (male and female) with its own description text; pick each in
   turn. Missing from the list → `ui/ui_avatardata.inc` not loaded (archive); listed but the client errors on select →
   report the client log line naming the template (`object/creature/player/shared_chiss_*`).
2. Appearance: the human slider set; skin palette blue-toned (the package's palette), hair styles and colours from the
   human lists; eyes red if the palette carries it (report what you see). A grey/untextured body → a customization
   table did not apply; report which page (skin / hair / eyes).
3. Finish creation with a Marksman and a Scout. Failure here → the server log: "Unknown player template selected"
   (template not registered: objects.lua/serverobjects.lua) or "Could not create player with template" (creation
   tables), or the client's "character creation failed" box; report the exact line.
4. In game: default clothes on (`default_pc_equipment`); open the skills window: **Species: Chiss** box under the
   species branch; `/getPlayerBaseHAM` is not needed — the HAM bars show 100s plus profession mods.
5. Clothing rule: buy or `/giveitem` a human shirt and a pair of boots (`object/tangible/wearables/shirt/shirt_s01.iff`,
   `wearables/boots/boots_s01.iff`): both equip; before the patch a Chiss could not wear them ("You cannot wear that").
   A refusal → the humanRigRaces pairs did not load; look for "Loaded 2 human-rig race mappings" in the server log.
6. Names: the random name button gives human-style names (expected); the name filter accepts a typed name.
7. Report: the species list, each failure line (client log / server log), and screenshots of the two faces.

## 4. Existing characters

None affected (checked by reading the patch): the six Races.h arrays only gain the two Chiss rows at the end and the
bounds become `RACE_COUNT`, so ids 0–19 map as before; `CHISS = 0xE7` is a new constant; the clothing rule only widens
what a race may wear; every client table and string file gains rows and keeps the stock ones (stage_species asserts
the stock round trips); the ACST is today's stock copy untouched. No database or character record changes.
