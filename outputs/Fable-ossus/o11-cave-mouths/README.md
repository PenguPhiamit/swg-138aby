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
