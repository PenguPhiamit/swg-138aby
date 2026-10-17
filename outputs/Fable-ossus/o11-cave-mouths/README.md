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
