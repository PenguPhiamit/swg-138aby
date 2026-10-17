# C59: why the player Hutt's walk and run look janky

Claude (side session, taking over GPT's queued C59), 16 Oct 2026, about 10 PM. Read-only on the client and server.
Nothing installed. Refocused per the 9:45 PM update: interaction loss was CPU starvation (hutt-c54.md sections 6-7),
so the only open question is the walking animation.

Owner's words (7:23 PM quiet-galaxy test): "the animation is still kinda janky while moving the idle is better and
moving looks good while prone".

## 1. Cause: the Hutt's walk and run are timed for slow NPCs, and a player moves at human speed

Each locomotion `.ans` (CKAT 0001) ends with a `LOCT` chunk: the average forward speed of the cycle (float32), a key
count (int16) and 14-byte keys (int16 frame, float32 x, y, z of the root's travel). The client fits the playback rate
to the character's real speed using that number. The human files show the convention: they are authored to exactly
the player speeds.

| File (winning copy) | Frames at 30 fps | LOCT speed (m/s) | Used for | Real speed (m/s) | Playback |
|---|---|---|---|---|---|
| `all_b_loc_walk_male.ans` | 33 | **1.549** | human walk | 1.549 | 1.0x |
| `all_b_loc_run.ans` | 22 | 5.132 | human run | 5.376 | 1.05x |
| `hutt_loc_walk.ans` | 60 | **0.508** | Hutt `loop_standing` walk | 1.549 | **3.0x** |
| `hutt_loc_run.ans` | 35 | **0.865** | Hutt `loop_standing` run | 5.376 | **6.2x** |
| `hutt_loc_crawl.ans` | 80 | 0.381 | Hutt `loop_prone` (and `loop_crouched`) | prone 0.387 | **1.0x** |

Where the real speeds come from:

- `object/creature/player/base/shared_base_player.iff` (patch_14_00) `speed` = **5.376 run, 1.549 walk**. The Hutt
  player templates (`shared_hutt_male/female.iff`, MTG 023) and every other species leave `speed`, `acceleration`,
  `turnRate` and `movementDatatable` unset, so they inherit these. Core3 reads the same field
  (`CreatureObjectImplementation.cpp:258-259`; `DEFAULTRUNSPEED = 5.376f`).
- `datatables/movement/movement_human.iff` (from `shared_base_creature.iff`): prone (posture 2) has only the `slow`
  category and `movementScale` 0.25, so prone moves at 0.25 x 1.549 = **0.387 m/s**. Crouched (posture 1): 0.5, so
  0.775 m/s.

That matches the owner's report point for point. Standing, the Hutt plays its walk at 3x and its run at 6x: the arms,
tail and body ripple frantically. Prone, the crawl meets its authored speed almost exactly, so it "looks good". The
idle has no locomotion, so it is unaffected. The stock NPC Hutts never showed this because they almost never move
(their base creature speed would play the same files at 4x and 7x).

Not proven: the client code is closed, so "the client scales playback by real speed / LOCT speed" is inferred from
the data (human files authored to the player speeds, and the one Hutt case that matches is the one that looks right),
not traced. If the client instead ignores LOCT, the fix below changes nothing visible, and costs nothing.

Ruled out as the cause:

- **The `hutt.lat` structure.** `loop_standing` is the stock SPAT (`INFO 03`: the mood idle, `hutt_loc_walk.ans`,
  `hutt_loc_run.ans`, all `PUNF locomotion`), byte-identical to the stock NPC table in patch_05 (as is `loop_combat_standing`). Level 1 only appended
  entries.
- **The bone tracks.** The root has no animated translation in any of the three files (its XFIN mask is 0); only
  `LOCT` carries the travel, so nothing in the cycle fights the movement.
- **Speed selection between walk and run.** With 0.51 and 0.86 m/s, almost any player speed picks the run cycle. After
  the fix the two speeds are the player's own 1.549 and 5.376, the same split the human table uses.

## 2. Fix (built, untested in game): retimed copies of the walk and run

`tools/build_hutt_c59_walk.py`, on top of the installed Nal Hutta + floater archive:

1. **Two new files**, copies of the stock ones with every `LOCT` key and the average speed multiplied so the stored
   speed equals the player speed: `appearance/animation/hutt_loc_walk_player.ans` (x3.048, 0.508 -> 1.549 m/s) and
   `appearance/animation/hutt_loc_run_player.ans` (x6.217, 0.865 -> 5.376 m/s). Same size as the stock files; the
   builder checks that every other chunk is byte-identical. The stock files are not overwritten.
2. **`hutt.lat`**: `loop_standing` and `loop_combat_standing` name the new files instead of the stock walk and run (4
   paths). All 837 entries stay; every other path is unchanged (checked). The six `sp_*_locomotion_*` special-attack
   entries keep the stock run.

A Hutt has no feet, so playing the cycle at its authored rate while the body covers three or six times the ground
reads as a glide, not as sliding. If the run looks too lazy, `--run-rate 1.5` plays it at 1.5x at full run speed.

### Candidate archive

| | |
|---|---|
| Archive | `work/c59-hutt-walk/local_planets-c59-walk.tre` (not in the repo) |
| **sha256** | **`fe62b478ab348e7f280cc113795fca7c6954d2b0adf19d243fabf293771e2303`** |
| Base | `local_planets-nalhutta-floater.tre`, **`503401b49a0c…8d17`** (181 entries), the archive installed on 16 Oct |
| Entries | 183: 180 byte-identical to 503401b4, `appearance/lat/hutt.lat` changed (sha256 `d865da6d…`), 2 new `.ans` (walk `139c5a30…`, run `5ec99297…`) |
| Checks | `work/c59-hutt-walk/checks.json`; staged files in `work/c59-hutt-walk/stage/` |

Rebuild:

```bash
C:/Users/Pengw/miniconda3/python.exe -I tools/build_hutt_c59_walk.py
```

**Moving base.** At 9:48 PM the Nal Hutta session rebuilt `work/nal-hutta/local_planets-nalhutta-floater.tre` (now
`0e4fe92d…`, `datatables/travel/travel.iff` changed, not yet committed). The builder refuses that file by default.
Its `hutt.lat` is the same (`985385fc…`), so `--any-base` gives the same new `hutt.lat` (`d865da6d…`) and the two
`.ans` on it (output `9ce108a0…` on 0e4fe92d, reproduced twice). Whichever Nal Hutta archive is installed next, run
this builder on it last, with `--any-base` when it is not 503401b4.

Install like C54 and the floater (both sides, same hash; the server ignores animations). Rollback: put 503401b4 back.

### What the owner should look for (open questions, in their own words)

Walk (toggle walk) and run on flat ground, then in combat stance, and look from the side and from behind.

- How does the walk look now, compared with prone?
- How does the run look: too slow, about right, or still frantic?
- Does the Hutt look like it is sliding over the ground?
- Anything odd when starting, stopping or turning?

If the run looks too slow, rebuild with `--run-rate 1.5` (one more install and restart).

## 3. Left alone, for later

- **Crouched** uses the crawl at 0.775 m/s, so about 2x. Same fix if the owner notices it (a third copy at 0.775).
- **Swimming** (`hutt_loc_swim.ans`, `hutt_loc_tread_water.ans`) was not measured against the swim speed.
- **Turning on the spot** uses `hutt_std_turn_left/right.ans` (yaw category), which this does not touch.
- A proper player walk (a faster slither) needs new animation authoring (S7 README section 4, Level 3).
