# Ossus O7: install notes (Claude, 16 Oct 2026)

Update 16 Oct 11:32 PM: **installed on the test galaxy (run 19)**. Archive `df1d538e` (floater v2 → PL-01 → PL-02) on client and server; dev `ad7b5a9d` (regions) and `742ace54` (people). Untested in game until the owner's visit.

Ready to install and **not installed**. Nothing under `/opt/swg`, `SWG-client/`, the galaxy or the bots was touched. All of it is
untested in game until the owner's visit.

## What the test galaxy has now (checked 16 Oct, about 11 PM)

| Part | Installed | O7 |
|---|---|---|
| Client and server archive `local_planets.tre` | `9ce108a0…` (`/opt/swg/tre/`, the C59 walk archive): O5's Ossus, terrain 27,322 bytes, snapshot 87 nodes, 6 region labels | not applied |
| Core3-dev `d4b9d9a1` Lua | O2/O5/C30: planet entry, Knossa travel point, fauna habitats, no-build circles (ruins r 260) | not applied |
| O7 statics, craters, fields | none | in this step |

## PL-01: what changes

**Client and server archive** (`build_ossus_o7.py`, a builder step that works on any base archive):

| Entry | Change |
|---|---|
| `terrain/ossus.trn` | 27,322 → 42,834 bytes: 14 layers (five craters 2-3.5 m, four scorch fans, the glass pan and rubble apron, Westmarch and Knossa Fields flattened, the POI 17 glass plain painted). The three TGAs are rebuilt and checked identical to the base. |
| `snapshot/ossus.ws` | 87 → 462 nodes (45,291 bytes): the 295 O7 statics at 16 places plus 80 cell nodes for 12 buildings, ids 6900087-6900461. |
| `datatables/clientregion/ossus.iff` | + Westmarch (-5344, 96) r 400, + Knossa Fields (1500, -3300) r 450 |
| `string/en/ossus_region_names.stf` | + "Westmarch", "Knossa Fields" |

The other 179 entries come through byte for byte. The step refuses a base whose four Ossus entries are not the O5 ones.

Candidate on the installed archive: **`work/ossus-o7/local_planets-ossus-o7.tre`**, 4,700,364 bytes, 183 entries,
**sha256 `efeff508409964b43380a172bd34324d6778d9058db66448740629573bb264a9`** (two builds, same hash). Details: `checks-build.json`.

**Server** (`server/core3-dev-ossus-o7-regions.patch`, against Core3-dev `d4b9d9a1`; `git apply --check` clean, `luac -p` clean):
`managers/planet/ossus_regions.lua` only. The ruins circle goes from r 260 to r 270 so the garrison's outer wall is inside it.
It adds ten circles at the new places: no spawns and no building at the vaults, both Ysanna sites, the hamlet (r 150, pier included),
the adit, the crashed fighter (a hole in the north open ground, where the kirruk packs spawn), the sky burial and the Hutt field.
The canyon crossing and the watch ruin get no building only. The fields stay ordinary ground, as o6 asked. No server templates are needed:
all 89 exist in dev. No player cities: the planet has no `CitiesAllowed` row, which dev `64156084` already treats as none allowed.

## What the bot census said, and what it changed

Data used: `Bot-reports/launch-sim/ossus-census.md/.csv` (800 explorers, 10:11 PM to 12:20 AM) and `Bot-reports/planet-data/ossus.md`
(run 13: 326 unnamed sightings; tonight's early run 18 file: 32).
- **Creatures.** None of the six Ossus creatures is aggressive (`mobile/ossus/*.lua`: ATTACKABLE, no AGGRESSIVE bit). Kirruk (L19) and
  mud yak (L19) are the strong ones. Kirruk run in packs in the west open ground and the north (-1500, 5200), and the mud yaks are around Adega Lake.
  Only two places are close to them: the hamlet (mud yaks 240 m off; the lake ring starts 90 m from it) and the crashed fighter (inside the
  north kirruk area). Both get no-spawn circles. Nothing had to move.
- **Flat ground.** The places already stand on the terrain model, which matches the census's ground samples to 0.26 m on average
  (`checks.json`). The census's flattest squares (the 104 m mesa east of Knossa) back the Hutt field at (3400, -2300).
- **The unnamed statics.** Of the 278 in the census, **4 are ours**: the O2 ruin walls and pillars at the academy, which use
  stock static templates with no name string. Naming them would mean editing stock server templates that every planet uses,
  so they stay unnamed. In-game statics have no name anyway. The other **274 are not ours**: 236 lie within 64 m of a
  creature sighting and all of them lie in the spawn areas. They are objects the creature spawner makes. Nothing to replace.

## Install order (the main session, with the server lock)

1. Chain the client steps on the installed archive in any order; this one only replaces the four Ossus entries:
   ```bash
   C:/Users/Pengw/miniconda3/python.exe -I Fable-ossus/o7-build/build_ossus_o7.py --base <the previous step's .tre> --out <next .tre>
   ```
   It takes about a minute (the terrain build).
2. Apply the server patch to Core3-dev (as swgemu), then run `check_lua.py`:
   ```bash
   wsl -d Debian -u swgemu -- git -C /opt/swg/Core3-dev apply /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o7-build/server/core3-dev-ossus-o7-regions.patch
   ```
3. Install the final archive as `/opt/swg/tre/local_planets.tre` and `SWG-client/local_planets.tre` (the server reads terrain and
   snapshot from it too), then restart the test galaxy under the standing OK (no owner client running, no squad round).
4. PL-02's patch (below) comes after step 2. It needs this archive's snapshot because its spawns stand on the O7 ground and inside the O7 caves.

## PL-02: Ossus people (details in `people/README.md`)

- **Server:** `server/core3-dev-ossus-people.patch` adds three new files: `mobile/sandbox/ossus_people.lua` (8 templates for the people who talk),
  `mobile/conversations/sandbox/ossus_people_conv.lua` and `screenplays/sandbox/ossus_people.lua` (33 spawns, the hidden Jedi's visits, three missions).
  It also adds one include line each to `mobile/serverobjects.lua`, `mobile/conversations.lua` and `screenplays/screenplays.lua`.
  It applies on dev `d4b9d9a1` alone or after the regions patch, and `luac -p` is clean.
- **Client and server archive:** `build_ossus_people.py --base <PL-01's output>` adds `datatables/badge/badge_map.iff`: the stock table
  plus row 140, `bdg_exp_oss_memorial_road`. It also adds the badge's name and description to `string/en/badge_n.stf` and `badge_d.stf`.
  The server reads the badge list from this archive too. The step stops if another step already used index 140.
  Candidate on PL-01's output: **`work/ossus-o7/local_planets-ossus-people.tre`**, 4,702,331 bytes, 184 entries,
  **sha256 `0084def40f8bdfa49dedbb8c874b0c51680ea52bfc18ad9d9d596fbc2c374b66`** (two builds, same hash). Details: `checks-people.json`.

Full order: PL-01 client step → PL-02 client step (on any chain, as long as both run) → both server patches (regions first) → install the archive
in both places → restart the test galaxy.

## PL-02: questions for the owner's visit

1. Talk to Elder Iravi at the Ysanna camp (-1326 -4932) and do the hunt. What happened with the waypoint, the kirruk and the pay?
2. Fetch Lieutenant Moll's coupling (-1476 5194 → the adit at 4590 -310 → back). Did each step say what you expected?
3. Walk the memorial road: the first stone (116 -3012), the middle stone (892 -31) and the ring (1960 2780). Did the badge appear, and what does
   the badge window show for it? Then see Archivist Oduro (2302 1987).
4. The garrison (2171 3041): what did the troopers and the major do when you came near?
5. Did you find the robed stranger in the sanctuary's deepest chamber? (They are there one hour in three to five.) Where were they standing,
   on the floor or somewhere odd?
6. Which of the people felt wrong for Ossus in 138-139 ABY, by look or by word?

## PL-01: questions for the owner's visit

Use `/teleport x y ossus`. Please tell me what you see at each place in your own words:
1. The five craters (1870 2930, 2140 2790, 2010 3010, 1930 2700, 2210 2920): how do the depth, the burnt ground and the scorch fans look?
   Can you walk in and out?
2. The glass pan and memorial ring (1960 2780) and the drop pod on crater 2's lip: do you see anything floating or sunk?
3. The three flatland caves: the sanctuary mouth (2057 2735), the vault (2300 1925) and the adit (4590 -310). Does each mouth meet the ground?
   Can you go in, and do the rooms load?
4. The garrison (gate 2148 3030, dig 2131 3006): which way do the doors and towers face, and how do the walls sit on the rim?
5. Westmarch (-5344 96) and Knossa Fields (1500 -3300): how do the flat ground and its edges look? Does the map name them?
6. The Adega hamlet and pier (-3050 1100): how does the pier sit on the water?
7. The bridge over Imhar Canyon (4470 -530): how does it look from above and from the canyon floor?
8. Knossa old town (0 -3660), the road markers, the watch ruin (290 -6400), the crashed fighter (-1500 5200), the burial platform
   (5233 786), the Hutt field (3400 -2300): is anything floating, sunk, white or purple?
9. Did you see creatures inside any of the camps?
