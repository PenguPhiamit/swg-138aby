# The player Hutt on the A1 Deluxe Floater: a lower riding pose

Update 16 Oct 11:32 PM: **v2 installed on the test galaxy (run 19)** as the first step of archive `df1d538e` (then Ossus O7 and Ossus people) on client and server. Untested in game.

Claude, 16 Oct 2026, from the owner's 7:45 PM floater test (test galaxy, archive `6ff21312` on client and server).
Status: **v1 installed at 10:05 PM (inside `9ce108a0`) and tested by the owner: "the floater was fixed with just a
little bit of clipping remaining". v2 (section 6) built on top of it, untested in game, not installed.** Only the Hutt
changes; the floater, the mount tables and every other species are left as they are.

## 1. What is wrong (from the close-up and the 8-second clip)

- **The head pokes through the canopy.** The camera sits behind and above the floater. Through the glass you can see
  both seats and the Hutt's grey shoulders and arms over the front seat. Its dark green head sticks up through the
  glass at the front of the canopy. Every frame of the clip looks the same: still or moving, the Hutt never shifts.
- **The rest looks right.** The floater moves, steers and turns round Mos Eisley with no stutter. The camera follows
  at its normal distance. No tail shows under or behind the hull (the tail stays inside it). Nothing hangs below the
  floater. The Hutt holds its standing idle the whole time, which is the planned Level 1 look (README section 6).
- The owner's words on the walking animation ("still kinda janky while moving ... looks good while prone") are about
  walking, not the floater, and this change does not touch walking. The Hutt's `loop_prone` uses the same idle plus
  the crawl, so "prone" does not give a lower pose to borrow for riding.

## 2. The cause, in the data

Measured with `tools/swgfmt` from the files the client loads:

| What | File (archive) | Offset | Value |
|---|---|---|---|
| Floater seat hardpoint `player` | `appearance/lod/a1_deluxe_floater.lod` (mtg_patch_016), the saddle appearance `appearance/a1_deluxe_floater.apt` points to | HPNT chunk at `0x40D`; its y float at `0x431` | (0, **1.474**, 1.069) m; `passenger_1` is (0, 1.474, −1.45) |
| Canopy (glass shader `a1_deluxe_floater_glass_aae15`) | `appearance/mesh/a1_deluxe_floater_l0.msh` (mtg_patch_016) | shader name at `0x473C3` | rim y 1.47 m, **apex y 2.34 m**, z −2.63 to 2.63, x ±1.06 |
| Hutt root bone, bind pose | `appearance/skeleton/hutt.skt` (data_other_00) | BPTR at `0x89A`, root y at `0x8A6` | **0.573 m** above the Hutt's base |
| Hutt mesh | `appearance/mesh/hutt_m_l0.mgn`, `hutt_f_l0.mgn` | POSN | **1.80 m** tall, 4.24 m long, 2.11 m wide; player scale 0.89–1.11 |
| Riding entry | `appearance/lat/hutt.lat` in `6ff21312` | `loop_riding` at `0x1A56B`, its .ans path at `0x1A597` | `hutt_idl_stand_breathe.ans`, the standing idle (root translation 0) |

**How the client seats a rider.** On every stock vehicle the rider pose puts the human pelvis (the root bone) exactly
on the seat hardpoint. The speeder bike's `player` hardpoint is (0, 1.156, −0.041). `all_b_mnt_ride_speeder_bike.ans`
moves the root by (0, +0.153, +0.013) from its bind pose (0, 1.002, −0.054), which lands it at (0, 1.155, −0.041).
Luke's landspeeder matches the same way to 1 mm. So the rider's root ends up on the hardpoint.

**For the Hutt:** the root is on the floater's hardpoint at 1.474 m, so the Hutt's base is at about 1.474 − 0.573 =
0.90 m. Its head top is then about 0.90 + 1.80 = 2.70 m (up to 2.9 m for the largest Hutt), 0.4–0.6 m above the
2.34 m canopy apex. The shoulders sit at about 2.1–2.3 m, just under the glass near the centre line. That is what
the close-up shows. The idle is a standing pose (root translation 0), so nothing lowers the body.

(The S7 README section 6 expected the problem to be the tail through the platform. The floater is a closed pod with a
glass canopy, not the flat platform the design assumed, so the problem is height, not the tail.)

## 3. The change (built)

`tools/build_hutt_c54_floater.py` (it extends `tools/build_hutt_c54_crafting.py`, on top of its output):

1. **New file `appearance/animation/hutt_mnt_ride_floater.ans`:** a copy of the stock `hutt_idl_stand_breathe.ans`
   (same breathing, same 60 frames). The y translation of the three children of `root` (`belly`, `tail01`, `spine`)
   is moved down **0.70 m**: `tail01` and `spine` are static slots 33 and 108, and `belly`'s animated channel 3 is
   shifted on all 57 keys. The root bone itself is untouched, so it stays on the hardpoint whether the client pins it
   there or applies the pose's own root offset, and the whole body sinks 0.70 m under it. The file is the same size
   as the idle and differs only in those values.
2. **`appearance/lat/hutt.lat`:** the six non-combat riding entries now name the new file instead of the idle:
   `loop_riding` and `loop_{pistol,rifle,polearm,sword_1h,sword_2h}_riding`. All 837 entries are still there, and
   every other path is unchanged (the builder checks each one).

Expected result: head top at about 2.0 m (1.8–2.2 m across the Hutt scale range), under the 2.34 m apex. The head
and upper chest show through the glass above the 1.47 m rim, the arms sit at the rim, and the tail sits lower inside
the hull (no lower than about 0.2 m, still inside it). The build uses neither the floater nor any other species,
and needs no server change (no patch file).

Not covered: the `*_combat_riding` entries still use the standing combat poses. Pre-CU riders are not meant to fight from a
vehicle, so they should rarely or never play. Whether Core3 dismounts the rider first was not checked for this note.

### Candidate archive

| | |
|---|---|
| Archive | `work/c54-floater/local_planets-c54-floater.tre` (not in the repo) |
| **sha256** | **`1ca2a091d467dabf397ae991ff06a4810a6b958dadf722666b25aa793eff044a`** |
| Base | `work/c54-crafting/local_planets-c54.tre`, `6ff2131229b3e917b8a274f334013f1534fa1a555d18080f1c595bb23141564f` (the builder refuses any other base) |
| Entries | 177: 175 byte-identical to `6ff21312`, `appearance/lat/hutt.lat` changed (sha256 `985385fc…`), `appearance/animation/hutt_mnt_ride_floater.ans` new (sha256 `ce467f89…`) |
| Checks | `work/c54-floater/checks.json`; staged files in `work/c54-floater/stage/` |

The C54 builder was run again into a scratch folder: it still rebuilds `6ff21312…` byte for byte from
`local_planets-s7.tre`, so the base is reproducible. To rebuild the candidate:

```bash
C:/Users/Pengw/miniconda3/python.exe -I tools/build_hutt_c54_floater.py
```

`--drop <metres>` changes the depth (see section 5); nothing else needs editing.

## 4. A/B options weighed

| Option | What it changes | Who it affects | Verdict |
|---|---|---|---|
| **A. Lower Hutt riding pose (built)** | 1 new .ans and 6 lat paths, Hutt only | Hutts only | Smallest and safest; reversible by reinstalling `6ff21312` |
| B. Lower the floater's `player` hardpoint (y 1.474 → ~0.8 at `0x431` in a copy of `a1_deluxe_floater.lod`) | 1 float in the floater's saddle LOD | Every species riding the floater: humans would sink 0.7 m into the hull | Rejected: not Hutt-only |
| C. Scale the floater up (server vehicle scale or a client object-template scale; `valid_scale_range` allows 0.5–2.5) | The floater's size | Everyone, and the floater grows to ~15 m long | Hardpoint and apex scale together. The head clears the apex only above scale ~1.45 (1.6 for the largest Hutt). Rejected |
| D. A reclined Hutt pose (`hutt_mnt_ride_sled`, S7 Level 3 item 3) | New authored animation | Hutts only | The proper look later. It needs animation authoring (rotations), not just a translation, so it is not tonight's fix |

Option A is the small first step towards D: D can replace the same lat paths later.

## 5. How the main session installs it (both sides, like C54)

With the owner's client closed and at the next planned test-galaxy restart:

1. Check the hash: `sha256sum work/c54-floater/local_planets-c54-floater.tre` must be `1ca2a091d467…044a`.
2. **Client:** back up `outputs/SWG-client/local_planets.tre` (`6ff21312`) as `local_planets.tre.bak-c54-6ff21312`,
   then copy the candidate over `outputs/SWG-client/local_planets.tre`.
3. **Server:** in WSL as root, back up `/opt/swg/tre/local_planets.tre` as `local_planets.tre.bak-c54-6ff21312`. Copy
   the candidate to `/opt/swg/tre/local_planets.tre` and `chown swgemu:swgemu` it (the current file belongs to swgemu).
   The server ignores animation files, but both sides stay on the same archive hash.
4. Restart the test galaxy as usual and record the new archive hash on the board.

**Rollback:** copy the `.bak-c54-6ff21312` files back on both sides.

**What the owner should look for** (open questions, in their own words): call the floater from the datapad and mount
it, then look at it from behind, from the side and from the front (zoom in), standing still and driving.

- Does the head still come out of the canopy?
- Can you see the Hutt inside the glass, or has it vanished into the hull?
- Does anything (tail, body) stick out below or behind the floater?
- Does dismounting put the Hutt back on the ground normally?

If the head still pokes out, rebuild with `--drop 0.9`. If the Hutt is hidden in the hull, rebuild with `--drop 0.5`.
Each needs one more install and restart.

## 6. v2: the spikes left after v1 (owner, 10:35 PM)

**What the owner saw on v1:** "the floater was fixed with just a little bit of clipping remaining", "clipping like
spikes of his model poking up when in the cockpit".

**Cause.** The client keeps the rider's `root` bone on the seat hardpoint, so v1 lowers root's three children
(`belly`, `tail01`, `spine`) by 0.70 m and leaves `root` itself where it was. In `hutt_m_l0.mgn` and `hutt_f_l0.mgn`,
**197 of the 1,350 vertices carry some `root` weight**: the upper chest, neck and chin (bind height 0.97–1.37 m, plus
some near the tail base). Most have weights of 0.01–0.5, and 7 are fully on `root`. When the rest of the body sinks
0.70 m, each of these vertices sinks only 0.70 × (1 − its root weight). A vertex with half its weight on root stays
0.35 m above its neighbours, and a fully rooted one stays 0.70 m above. Those vertices are the spikes.

What this rules out:

- **Lowering the pose further** only makes the spikes longer.
- **Moving `root` in the animation** has no effect, because the client places `root` on the hardpoint regardless (section 2).
- **Scaling the floater** would need a server change, because the floater's Lua template has no scale. It would also change the floater for every species, and the stretch would remain.

A bind-pose check of every vertex against the floater's real triangles agrees. Vertex by vertex, v1 puts no
non-root vertex above the canopy for any Hutt scale from 0.89 to 1.11. The only defect left is the skin stretching.

**The change (built).** In the two LOD 0 Hutt meshes, each vertex's `root` weight moves to the nearest child of root
by bind-pose distance, and is added to any weight the vertex already has on that bone. The split is 100 vertices to
`spine`, 66 to `belly` and 31 to `tail01`. Each vertex's weights still sum to what they did, and the TWDT count goes
from 2,018 to 1,884 entries. Positions, normals, triangles, shaders and blend targets stay byte-identical (the builder
checks), and the floater, `hutt.lat` and the v1 animation are untouched. In the same check, every vertex of the
reweighted mesh sinks the full 0.70 m: the head top is at 1.94–2.06 m and nothing reaches the 2.34 m canopy.

| | |
|---|---|
| Builder | `tools/build_hutt_c54_floater_v2.py` (imports the v1 builder; requires v1 in the base) |
| Archive | `work/c54-floater-v2/local_planets-c54-floater-v2.tre` (not in the repo) |
| **sha256** | **`5ee3f914a6d0ba06fc6c545ea43f7d3e46be24a50b972d3d58c4a116151c07d6`** |
| Base | `work/c59-walk-on-0e4fe92d/local_planets-c59-walk.tre`, `9ce108a03b027ff9e344f02866aadb796cec2c817064d774a30f4e1614f9745b` (v1 → Nal Hutta → C59 walk). The builder refuses any other base unless `--any-base` is given, and then still requires v1 in it |
| Entries | 185: all 183 entries of `9ce108a0` byte-identical, plus 2 new: `appearance/mesh/hutt_m_l0.mgn` (`d22e5339…`) and `hutt_f_l0.mgn` (`ab49f429…`) |
| Checks | `work/c54-floater-v2/checks.json`; staged meshes in `work/c54-floater-v2/stage/` |

**Side effects and limits (honest list).**

- **Outside the riding pose**, those 197 vertices now follow `spine`, `belly` or `tail01` fully instead of partly.
  - `belly` never rotates in any of the 127 stock Hutt animations; it only bobs up and down, by up to 0.15 m in walk, run and get-hit.
  - `spine` and `tail01` sway.
  - So the chest and neck may bob or sway slightly more with the body in the walk, the run and emotes. The idle should look the same.
  - NPC Hutts (`object/mobile/hutt_*`) use the same meshes and get the same small change.
- **LODs 1–3 keep their weights.** Those meshes have no `belly` or `spine` (only `tail01`, which sways with the tail),
  so their root vertices (84, 35 and 10, including the belly) cannot be moved without adding a bone to the mesh. These
  meshes only show from a distance. A distant riding Hutt may still look a little spiky, but inside the glass.
- Not checked in game: the actual animated pose, rather than the bind pose. The arms and head move a little in the idle.

**Install** exactly as in section 5, with this archive and hash in place of v1's. Back up the current `9ce108a0` on
both sides as `local_planets.tre.bak-9ce108a0`. Rollback: put `9ce108a0` back.

**What the owner should look for** (open questions):

- Mounted on the floater, close up from behind, the side and the front: are any spikes or stretched bits still
  sticking up in the cockpit? Does anything come through the glass?
- Off the floater: do the idle, the walk and a couple of emotes look the same as before, especially the chest and neck?
- Optional, from 30 m or more away: does a riding Hutt look spiky (the LOD 1–3 limit above)?

**If something still pokes out close up**, it comes from the animated pose (arms or head moving in the idle), not
the skin. Send a close-up and say where it pokes; rebuilding v1 with a deeper `--drop` and then this builder on top
handles that. **If the walk or emotes look worse**, roll back to `9ce108a0` and say what changed.
