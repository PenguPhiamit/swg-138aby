# Ossus O11: open the flatland cave mouths, and put the dungeon on its floor (Claude, 17 Oct 2026)

The owner, in game on run 28 at 10:05 AM, at the Great Library vault mouth (2297, 1921): "i can walk through the floor in the first cave ...
it goes to the dungeon so that part of the floor shouldnt be there anymore." The owner asked for that floor to go, so a terrain change limited
to the cave footprints is covered. **Staged, not installed, untested in game.**

**Correction to the first version of this step (commit 64f034c).** My floor-mesh reader skipped the 4-byte vertex count at the start of each
`.flr` VERT chunk, so every vertex was shifted by one value. That turned the mounds into imaginary 30 m "sinkholes". The same reader produced the
hidden Jedi's spot (PL-02/O10) and the O8 dungeon spawn points, which is why the spirit stood in the rock (the main session fixed his spot in dev
`3cf3d88f`). Both readers now read the floor files as `tools/navmap.py` does. This version replaces the first one completely: the pit layout is new,
and no props or NPCs move.

## Why it happens

Stock SWG's flatland caves (`cave_06/07/08_flatland_*`, which O7 placed at the sanctuary, the vault and the adit) are a rock mound standing on flat ground.
The mound's surface (the r0 floor) rises to 29 m. The first cell (r1) starts at the mouth (portal 0, building-space z = 18, its floor at ground level
as O7 placed it) and runs down under the mound, 12 m (sanctuary), 33 m (vault) or 18 m (adit) below the ground. The stock object templates carry no
terrain cut, and SWG terrain has no holes. So the planet's ground carries on inside the mound and slices across that first tunnel just past the mouth.
That is the grass in the opening, with the ramp running down "through" it.

## The fix: a pit under each mound (terrain only)

**`terrain/ossus.trn`:** one pit layer per cave, placed after the O7 layers. Its shape is world-aligned 1 m rectangles. A cell is cut when, at every sample of
the cell grown by 0.75 m, the mound's surface is more than 2 m above the current ground, and the grown cell lies at least 0.5 m behind the mouth.
So the cut stays inside the shell, clear of its sloping sides, and never reaches in front of the portal. Each pit sets the height (`AHCN` op 0,
no feather) 2 m below the lowest point of that cave's first tunnel.

| Cave | Node (x, y, z) | Pit area | Rectangles | Pit height | First-tunnel floor points under ground, before → after |
|---|---|---|---|---|---|
| Sanctuary | 2063, 2718, 167.0 | 1,543 m² | 46 | 152.84 m | 82 → 0 |
| Vault | 2300, 1907, 38.7 | 1,484 m² | 38 | 3.81 m | 137 → 75 |
| Adit | 4578, -297, 41.2 | 997 m² | 44 | 21.15 m | 135 → 70 |

All of the points still under ground are **10 m or more** below it: the vault's first tunnel runs on past the mound, and the adit's mound
is buried in the canyon wall by design. That is solid ground over a tunnel, as in any cave. No point less than 10 m under the ground is left at
any of the three caves; before the fix there were 51, 42 and 30, the shallowest 0.5-1.4 m deep and up to 3.5 m inside the mouth.

**Nothing else moves:** the height changes only inside the rectangles. The whole-planet 96 m grid shows 0 changes outside them, and a 1 m grid
within 120 m of each cave, about 56,500 points per cave outside the rectangles, shows 0 changes over 1 mm. The three terrain images are rebuilt
byte-identical, and no O7 prop or NPC stands inside a pit, so the snapshot and the spawn lists stay as they are.
Terrain file: `05c570f2…` (42,834 bytes, the O7 one) → `3d6f9493…` (56,418 bytes).

**Archive:** `build_cave_mouths.py` on the installed run-28 archive `b103e36f…`: **`work/ossus-cave-mouths/local_planets-cave-mouths.tre`,
sha256 `beb06d28108ace018468de351420412705dcdcbad0a7d55a64258a7f3b871afa`** (two builds, same hash). It has 337 entries; only `terrain/ossus.trn`
changes and the other 336 stay byte for byte. Details: `checks-cave-mouths.json`. The step refuses a base whose terrain is not the O7 one, and
takes about 3 minutes.

## The dungeon's spawn points (server)

**`server/core3-dev-ossus-dungeon-floor.patch`** against Core3-dev `3cf3d88f` (`git apply --check` and `luac -p` clean) replaces the 23 spawn points of
O8's One Sith cell (west foothill cave, cells 6900003-6900013) with points on each cell's floor. The points are centres of floor triangles with no
wall edge, up to three per cell about 6 m apart (`dungeon-points.json`). The old points came from the broken reader, like the spirit's spot.
My staged copy `o8-world/.../ossus_world.lua` has the same change. The spirit's new spot from `3cf3d88f` is copied into my staged copies too
(`o10-ghostfire` and `o7-build/people`), so no later patch puts the old one back.

## The bot's route in the sanctuary (reported, not changed)

The bot stopped in cell 6900108 because the server's route jumped from the entrance cell straight to the deepest chamber (6900118), "a doorway
step longer than 12 m". The cave's portal layout does not join those two cells. Its portals chain them
1 → 2 → 3 → (4 → 5 → 6, or 9) → 8 → 11, and that is the same in `cave_01` and `cave_06_flatland_s01_damprock`. So the skip comes from the
route-building side (the building path graph as Core3 or `/agentpath` reads it), not from the cave or from our placement. That code is the main
session's, so I left it alone.

## Install (the main session, with the server lock)

1. Use the archive above, or chain `build_cave_mouths.py --base <archive> --out <new>`. No other step may change `terrain/ossus.trn`.
2. Apply `server/core3-dev-ossus-dungeon-floor.patch` to Core3-dev and run `check_lua.py`.
3. Install the archive in both places and restart the test galaxy.

## Questions for the owner's visit (please answer in your own words)

1. At the vault mouth (2297 1921): what do you see in the opening now, and can you walk down the first tunnel without grass in the way?
2. The same at the sanctuary (2057 2735) and the adit (4590 -310).
3. Around and on top of each mound: is there any gap where you can see through the world, or grass poking through the rock?
4. In the west foothill cave (-2976 -4978): are the acolytes and enforcers standing on the floor in each chamber, and is the Keeper in the deepest one?

## O11b: the water in the vault (run 29) and moving two caves above it

The owner, on run 29 at about 12:00 PM, at the vault: "theres water there now, but i can still traverse". The pits opened the tunnels, but
Ossus's **global water table is 38.5 m**. The vault's first tunnel bottoms out at 5.8 m and the adit's at 23.2 m, so both pits filled with water. The
sanctuary (tunnel bottom 154.8 m) was never affected.

**The options and what they cost**

| Option | What it would take | Verdict |
|---|---|---|
| Lower the global water table | The vault's tunnel needs the water under about 4 m. 5.4 % of the planet lies under 38.5 m (96 m grid): Adega Lake, the west lowlands, the hamlet's pier over the lake. Lowering it that far would drain them all, against the Legends "two-thirds water". | No. It is a global change, and it would need your OK. |
| Keep water out of the pits only | SWG terrain can add local water bodies, but nothing removes the global water plane in one spot. A pit kept above the water would cross the tunnel again 4 m inside the vault's mouth. | Not possible as asked. |
| Raise the caves in place | The vault's mouth must be at 77.3 m or higher (it is at 42.6 m) and the adit's at 62.4 m (45.1 m): hills 35 m and 17 m high, about 100 m across, raised out of the plain and out of the canyon floor. | Possible, but a big change to the landscape. |
| **Move the two caves to high ground nearby** (done) | A grid search found flat ground above the need. The vault goes 470 m north onto the Academy Benchland (171 m, relief 1.2 m over r 45 m), nearer the ruins where the Great Library stood. The adit goes 130 m onto the mesa rim above Imhar Canyon (104 m, relief 0.8 m). Each moves with its camp. | Chosen: local, and both places keep their story. |

**What `build_cave_moves.py` changes** (on the installed run-29 archive `beb06d28…`; the O7 terrain without pits comes from `b103e36f…`):
- **Snapshot:** the vault and its camp (20 objects) move from (2299.7, 1907.0) to (1940.0, 2237.0), heading unchanged, cave mouth to the north.
  The adit and its camp (17 objects) move from (4578.1, -296.5) to (4488.0, -206.0), turned 177° so the mouth faces away from the canyon edge
  (yaw 315°, the flattest of 24 headings). Each object keeps its height above the ground; the cave node is set to the ground at its mouth - 3.85 m.
  The ground under each group varies by 0.38 m and 0.07 m.
- **Terrain:** the pits are cut afresh with the same rules at the new places (the sanctuary's is unchanged): vault 1,553 m² at 132.8 m,
  adit 1,532 m² at 80.65 m. That is 94 m and 42 m above the water. The old vault and adit sites are back to their natural ground (0.0 m change within 60 m),
  and the whole-planet grid shows 0 changes outside the pits. No first-tunnel floor point less than 10 m under ground is left at any cave (the vault
  has 75 deeper ones past its mound, the adit 3). No ground over any tunnel is below the water. No moved prop or NPC stands over a pit.
- **Archive:** **`work/ossus-cave-moves/local_planets-cave-moves.tre`, sha256 `cc6f4ebbaa7e1bd0f4a963117ac580d94395d98f12ba0e772ac687b82a68485e`**
  (two builds, same hash). It has 337 entries; `terrain/ossus.trn` and `snapshot/ossus.ws` change and the other 335 stay byte for byte. Details: `checks-cave-moves.json`.
- **Server: `server/core3-dev-ossus-cave-moves.patch`** against Core3-dev `4906d2eb` (`git apply --check` and `luac -p` clean). It moves, by the same transform:
  - the archivist → (1942.3, 2317.0), and the ghostfire vault site and its waypoint → (1940.3, 2255.0);
  - the foreman → (4475.4, -193.1) and the miner → (4469.7, -199.4), and Moll's adit waypoint → (4475, -193);
  - the two no-spawn circles → (1940, 2290) and (4465, -183), r 80.

  Three of Moll's lines now say the adit is "on the rim of Imhar Canyon". My staged copies in `o10-ghostfire` and `o7-build/people` have the same changes.

**Install:** use this archive (it replaces `beb06d28`; the step refuses other bases unless given `--base`), apply the patch, run `check_lua.py`,
restart the test galaxy.

**Questions for the owner's visit (in your own words)**
1. The vault, now at 1940 2255 on the benchland: is there water or grass in the opening? Can you walk down? Does the dig camp look right around it?
2. The adit, now on the canyon rim at 4475 -193: same questions. Can you see the canyon from the camp?
3. The old places (2300 1925 and 4590 -310): is the ground whole again?
4. Do the ghostfire waypoint (the vault mouth) and Moll's adit waypoint lead to the new places?

## O11c: one step for all six caves, plus the One Sith leash (run 29 reports, 12:00-12:30 PM)

The owner's reports, in their words, and what each one turned out to be:

| Report | Cause | Fix |
|---|---|---|
| Vault: "theres water there now, but i can still traverse"; adit: "adit has waTER TOO" (seen at the old places) | The pits went below the 38.5 m global water table | The O11b move (above), now in this step |
| "Sanctuary has a tree in the mouth" | Terrain flora. No snapshot object or screenplay prop stands within 8 m of the mouth; the rubble apron's boulders and the plains' trees reach it. | A 50 m flora-off circle at every cave: trees, bushes, grass, far trees and boulders |
| One Sith cave: "a big gap in the terrain you can fall through at the entrance" | O2 cut a real terrain hole (`AEXC`, 9 m) centred on each doorway of its three hillside caves, so half of it was in front of the door, where there is no cave floor | O2's three hole layers are left out of the build |
| One Sith cave: "it also has a floor in the doorway" | These are hillside caves: the tunnel runs into a hill, and O2's 30 m apron, levelled to the door's floor height, took the hill away, so the ground crossed the tunnel | The hill is rebuilt behind each door (below) |
| "one sith never de aggro" (chased a couple of hundred metres, attacking all the way) | Stock Core3: a mob goes home only when its target is more than **256 m** from the mob's home (`CheckRetreat 256` in `ai/default.lua` `moveDefault`). The home check uses world positions, so a mob spawned in a cave cell is measured correctly. Not a cell bug, and no C++ needed. | Our fighters get an 80 m leash (below) |

**Terrain and snapshot: `build_cave_fix.py`** (on the installed run-29 archive `beb06d28…`; it contains O11b's move):
- **Flatland caves** (sanctuary, vault, adit): the pits as before, at the moved places for the vault and the adit.
- **Hillside caves** (the One Sith cell `cave_01` at (-2976, -4978), the east foothill cave `cave_03`, the north cave `cave_02`): no holes. Behind each door,
  the ground is raised to 1.5 m over the roof of the first three tunnel cells (floor + 9.25 m, the door's height), and falls away from them at 0.6 m per
  metre (about 31°) to the natural ground, in 1 m cells and 0.5 m terraces. It is raised only behind the door's own plane, where the cave's rock face
  covers the step; the apron in front of the door is untouched. These layers go at the end of the layer list, after O2's apron, which would otherwise
  flatten them again.

  | Cave | Hill area | Hill heights | Ground inside the first three tunnel cells, before → after |
  |---|---|---|---|
  | One Sith cell (west) | 1,067 m² | 49.0-63.5 m | 32 → 0 floor points |
  | East foothill cave | 881 m² | 60.0-70.0 m | 46 → 0 |
  | North cave | 966 m² | 46.5-57.0 m | 38 → 0 |

- **Checks** (`checks-cave-fix.json`): no tunnel at any of the six caves has ground less than 10 m over its first cell. The planet's height changes only inside the
  pits and hills (the whole-planet grid shows 0 changes outside them). No snapshot object stands in a pit or a hill. The terrain has no `terrain hole`
  affector left (3 before). The three terrain images stay byte-identical.
- **Archive:** **`work/ossus-cave-fix/local_planets-cave-fix.tre`, sha256 `1f441e01870253f94231b13ae4b2aef93fc75558eac28d6ae6272deb5d168f91`**
  (6,851,817 bytes, 337 entries; `terrain/ossus.trn` and `snapshot/ossus.ws` change and the other 335 stay byte for byte). It replaces `cc6f4ebb` and
  `beb06d28`, and takes about 15 minutes to build.

**Server: three patches, all against Core3-dev `25344120`** (each and both together pass `git apply --check`; `luac -p` clean):
1. `core3-dev-ossus-dungeon-floor.patch`: already applied in dev (`4906d2eb`). Skip it.
2. `core3-dev-ossus-cave-moves.patch`: the archivist, the foreman, the miner, the vault's ghostfire site, two waypoints and two no-spawn circles move with the caves.
3. `core3-dev-ossus-short-leash.patch`:
   - a new file, `ai/ossus.lua`: a copy of the stock `moveDefault` with the leash at 80 m (node ids prefixed "ossus", so the copy shares no id with the stock tree);
   - `ai/templates.lua`: includes it and adds a custom AI map `ossusShortLeash` that overrides only the MOVE tree;
   - `mobile/sandbox/ossus_world.lua`: the six O8 fighters (the One Sith acolytes, enforcers and Keeper, and the three camp leaders) use that map.

   A stubbed load of `default.lua` + `ossus.lua` gives 18 of 18 nodes, unique ids, every parent present, and the leash at 80. Stock mobs keep 256 m.
   Not tested on a server: the bot test with the Forn dungeon crew was not run (the board claim would be the main session's).

**The bot route** in the sanctuary (cell 1 to cell 11 in one "doorway step") is still the route builder's, as reported above; nothing here changes it.

**Install (the main session):** this archive in both places; patches 2 and 3 on Core3-dev; `check_lua.py`; restart the test galaxy.

**Questions for the owner's visit (in your own words)**
1. The One Sith cave (-2976 -4960): any gap you can fall through, or a floor in the doorway? How does the hill behind the cave face look from the sides and from above?
2. The east foothill cave (4896 -4960) and the north cave (1376 5920): the same questions.
3. The sanctuary mouth: any tree or boulder left in it?
4. Pull a One Sith out of the cave and run: how far do they follow you before they turn back?
