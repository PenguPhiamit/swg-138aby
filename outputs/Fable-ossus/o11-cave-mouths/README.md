# Ossus O11: open the flatland cave mouths (Claude, 17 Oct 2026)

The owner, in game on run 28 at 10:05 AM, at the Great Library vault mouth (2297, 1921): "i can walk through the floor in the first cave ...
it goes to the dungeon so that part of the floor shouldnt be there anymore." The owner asked for that floor to go, so a terrain change limited
to the cave footprints is covered. **Staged, not installed, untested in game.**

## Why it happens

Stock SWG's flatland caves (`cave_06/07/08_flatland_*`, which O7 placed at the sanctuary, the vault and the adit) are **sinkholes**. Their outside
floor (the r0 collision floor of each `.pob`) is a bowl that drops 30-44 m from the rim down to the entrance of the cave proper. Their object
templates carry no terrain layer (`terrainModificationFileName`) or other terrain cut, and SWG terrain has no holes. So the stock art simply assumes
the ground is open there. On Ossus the ground stayed at its height over each bowl: the client draws grass across the bowl, and the bowl's
floor lets you walk down "through" it. All three O7 flatland caves had it. Before the fix, 1,230, 1,250 and 1,327 sampled floor points (vertices and triangle
centres of the r0 floor, out of 2,224 per cave) lay under the ground, up to 34, 35 and 44 m deep (`survey-b103e36f.json`, from `survey_caves.py`).

## The fix

**Terrain (`terrain/ossus.trn`):** one pit layer per cave, placed after the O7 layers. Its shape is world-aligned 1 m rectangles: a cell is cut when the
bowl's floor lies over it and the floor there is more than 0.5 m below the current ground. That cuts the part of the bowl the ground covered, plus
one cell behind its deep rock walls, where the walls hide the cut. It never cuts the shallow rim where the floor meets the ground. Each pit sets the height
(`AHCN` op 0, no feather) 2 m below that cave's lowest floor point, so the bowl's own floor hides the pit from every angle.

| Cave | Node (x, y, ground z) | Pit area | Rectangles | Pit height | Covered floor points before → after |
|---|---|---|---|---|---|
| Sanctuary (2063, 2718) | 167.0 | 1,801 m² | 60 | 134.43 m | 1,230 → 33 |
| Vault (2300, 1907) | 38.7 | 1,788 m² | 36 | 6.13 m | 1,250 → 41 |
| Adit (4578, -297) | 41.2 | 1,810 m² | 80 | 8.65 m | 1,327 → 46 |

The 33-46 points left per cave are where the floor turns into a near-vertical wall within one metre, so the ground may overhang the wall top by
less than a metre. That is for your eyes in game.

**Nothing else moves:** the height changes only inside the rectangles. The whole-planet 96 m grid shows 0 changes outside them, and a 1 m grid
within 120 m of each cave, about 56,000 points per cave outside the rectangles, shows 0 changes over 1 mm. The three terrain images are rebuilt
byte-identical. Terrain file: `05c570f2…` (42,834 bytes, the O7 one) → `cad58f12…` (61,286 bytes).

**Snapshot (`snapshot/ossus.ws`):** 14 O7 props stood on the old false ground inside the bowls. Each moves straight out from the bowl's middle to the
first point 2.5 m clear of the pit, at the ground height there (unchanged ground):

| Cave | Props moved (distance) |
|---|---|
| Sanctuary | fallen pillar at the mouth ×2 (7.75, 9.5 m), rubble at the mouth (3.75 m) |
| Vault | half-buried pillar base ×2 (5.5, 8.75 m), fallen pillar ×2 (7.5, 13.5 m), pillar stub at the door (5.5 m) |
| Adit | ore cart (4.25 m), timber prop ×3 (3-8.75 m), lamp ×2 (6.75, 10.25 m) |

At the adit, a moved lamp ends 0.8 m from the moved ore cart (they may touch), and two other props are 2.3-2.5 m apart.

**Server (`server/core3-dev-ossus-adit-npcs.patch`):** against Core3-dev `b39ff477`, `git apply --check` and `luac -p` clean. By the same rule,
the adit foreman (4590, -310) → (4600.6, -317.1) and the miner (4596, -304) → (4608.6, -302.1) move 12.75 m out of the sinkhole. No other
server change is needed: Core3 reads the terrain and the snapshot from the same archive. The ghostfire vault site (2300, 1925, r 20) still triggers
anywhere in and around the bowl.

**Archive:** `build_cave_mouths.py` on the installed run-28 archive `b103e36f…`: **`work/ossus-cave-mouths/local_planets-cave-mouths.tre`,
sha256 `18d8d8828be4a5736097839460820e6b99f7b4fd910988119e0263e32261033e`** (two builds, same hash). It has 337 entries; `terrain/ossus.trn`
and `snapshot/ossus.ws` change and the other 335 stay byte for byte. Details: `checks-cave-mouths.json`. The step refuses a base whose terrain is not
the O7 one. It takes about 3 minutes.

## Install (the main session, with the server lock)

1. Use the archive above, or chain `build_cave_mouths.py --base <archive> --out <new>`. Other steps must not change `terrain/ossus.trn` or `snapshot/ossus.ws`.
2. Apply `server/core3-dev-ossus-adit-npcs.patch` to Core3-dev and run `check_lua.py`.
3. Install the archive in both places and restart the test galaxy.

## Questions for the owner's visit (please answer in your own words)

1. At the vault mouth (2297 1921): can you see down into the bowl now and walk down to the cave entrance? What does the bottom look like?
2. The same at the sanctuary (2057 2735) and the adit (4590 -310).
3. Around each bowl's rim: is there any grass hanging over the edge, a gap where you can see through the world, or a strange cliff?
4. Are the moved pillars, rubble, carts and lamps standing on the ground near each mouth, and is anything floating, sunk or overlapping?
5. At the adit, where are the foreman and the miner standing now?
