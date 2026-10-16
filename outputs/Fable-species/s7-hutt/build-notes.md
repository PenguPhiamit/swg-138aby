# S7 Level 1 build notes: the playable Hutt's animation table (`hutt.lat`), 16 Oct 2026

Staging only: **built and re-parsed, not packed, not seen in a client.** Nothing under `/opt/swg` was written, nothing was
downloaded or installed. Built from Fable's `animation-map.json` (631 entries) and the stock table in the client archives.
Everything marked *checked* below is output of `tools/build_hutt_lat.py`; everything marked *inferred* or *untested* is not.

| file | what |
|---|---|
| `tools/build_hutt_lat.py` | reads the stock `appearance/lat/hutt.lat` (client archives, `patch_05.tre` wins) and `animation-map.json`, writes the new table, then runs 21 checks. Deterministic: two runs gave the same bytes |
| `staged/client/appearance/lat/hutt.lat` | the output: 208,161 B, **837 ANIM entries** (206 stock + 631 added), sha256 `1b7e2f03b314f64454f992ad1be0e4487c7087ec3593fd707e2430ebbcf0aa7b`. A stock table plus our rows, the Chiss/Ossus staging precedent. Git ignores it (`*.lat` added to `.gitignore`, like `*.iff`/`*.skt`/`*.ans`); the script rebuilds it |
| `out/hutt-lat-check.json` | the check results and numbers quoted here (tracked) |

Stock input: 49,242 B, sha256 `80424b19f79a09ed6f2f36a4f6af231fec183cae051b4508ed657ae4e1e8bfcb`, from `patch_05.tre` (priority 31).
Older copies sit in `data_other_00` (146 entries), `patch_01` and `mtg_patch_001` (206 each; the MTG one is the same size as patch_05).
Both `hutt_m.sat` and `hutt_f.sat` name `appearance/lat/hutt.lat` in their `LATX` chunk, so one file serves both genders, and
every NPC Hutt (they use the same `.sat`) shares it.

## 1. How a `.lat` works (read from the stock tables)

A logical animation table (LAT) answers one question for the client: *the animation state hierarchy asked for the logical
name X; which `.ans` file(s) play for this skeleton?* Two files cooperate:

- `appearance/ash/all_b.ash` (the state hierarchy, shared by humans and Hutts) says **what to ask for**. `FORM ASHT > 0002 > STAT`
  per state: `INFO "<state>\0<loop animation>\0"`, `ACTS` (`ACTN "<action>\0<animation>\0"` + 3 flag bytes, and `MVAC` pairs
  of two), `LNKS` (`LINK`: uint16 n, n state names, 1 flag byte, `<transition animation>\0`), `CHLD` (child states). The
  winning copy is `patch_11_00` (priority 38): 935 distinct animation names, 45 state loops.
- `appearance/lat/<x>.lat` says **what plays**. A skeleton's `.sat` points at it (`LATX`).

IFF framing is the project's usual one: 4-byte tag, big-endian size, body; FORM bodies start with a 4-byte form type;
chunk contents are little-endian. `tools/swgfmt/trn_iff.py` parses and rebuilds all of it byte for byte (round trip: identical).

```
FORM LATT
  FORM 0000
    INFO   "appearance/ash/all_b.ash\0" + uint16 N          <- N = number of ANIM forms that follow
    FORM ANIM  x N
      INFO   "<logical animation name>\0"
      FORM <node>                                             <- exactly one node, see below
```

**The count (a correction to Fable's recipe).** Fable wrote that no count exists. It does: the two bytes after the path's NUL
are the number of ANIM forms. *Checked* on nine stock/MTG tables: hutt 146 (`data_other_00`), 206 (`patch_01`, `patch_05`,
`mtg_001`); `all_m` 771 (`patch_05`), 877 (`patch_11_02`), 908 (`mtg_022`, `local_planets`); `all_f` 908 (`mtg_022`): the field equals
the ANIM count in every one. Appending entries without raising it would leave the new rows past the count. *Untested:* what the
client does then (reads only N, or errors). The builder writes 837 and a check fails if the field and the forms disagree
(tried on a deliberately stale copy: it fails).

Node types (tag, body, what it does; "seen" = where I read it):

| node | body | meaning | seen |
|---|---|---|---|
| `PXAT` | `FORM 0000 > INFO "<ans>\0"` [+ `PUNF "<cat>\0<cat>\0"` or, human only, `PPTR "<cat>\0<mask.iff>\0<cat>\0<cat>\0"`] | play one `.ans`. The category is one of `action emote locomotion reaction transition yaw zero_speed`. The Hutt `std_hold_object` family has no `PUNF` at all | Hutt: 190 stock |
| `TSCL` | `INFO float32` + one child | time scale around a child; can nest (human `trn_crouched_to_kneeling` is 2.0 around 1.25 around a PXAT) | human transitions |
| `SPAT` | `INFO uint8 n` + n children | speed blend: the child with `zero_speed` is the idle, `locomotion` children are walk/run. Child order is free (the Hutt `DRAT` sets list run, idle, walk; human `loop_skill` lists the dance switch last) | Hutt `loop_standing`, human `loop_crouched` |
| `YWAT` | `FORM YNEG`, `FORM YPOS`, `FORM NONE`, each holding a node | turn left / turn right / idle | Hutt pistol and rifle stances |
| `DRAT` | `INFO uint8 n` + n x `FORM DIR` (`INFO uint8 code` + node) | directional set. Codes 1,2,4,5,6,9,10 = right, left, front, front-right, front-left, back-right, back-left (from the file names `..._fire_3_front_right.ans`) | Hutt fire and aimed-ready sets |
| `AGAT` | `INFO float32 min, float32 max` (seconds), `ACTN` (uint16 n, n x `<action>\0` + float32 weight), `FORM LOOP` + node | ambient gestures: every min..max seconds one of the actions is played over the loop. **The names are ash action names**, not table names (`angry` -> `emt_pound_fist_palm`) | Hutt `loop_standing` (mood), human sitting loops |
| `SSAT` | `INFO "<variable>\0"`, `FORM ANMS` (`INFO uint16 n` + n nodes), `VAL` (uint16 n, n x `<value>\0` + uint16 child index), `DFLT uint16` | switch on an animation variable (`mood`, `gender`, `rider_pose`, `skill`) | human |
| `PBAT` / `COMP` | pose blend: upper/lower body components with bone masks | human riding | human, **not written** |

*Inferred, not tested:* AGAT action names resolve through the ash, and a child state sees the root state's actions. Evidence:
all 9 gestures in the stock Hutt table are root-state actions of the ash whose animation exists in the Hutt table, and the
human sitting-ground AGAT names `ag_sitting_ground_fidget_1..3`, which only the root state's `ACTS` define.

## 2. What was added

631 entries appended after the 206 stock ones, in the order of `animation-map.json`; the stock 206 are byte-identical.

| top node | n | used for |
|---|---|---|
| `PXAT` | 455 | 284 emotes (keyword to the 22 Hutt emotes, 95 to `hutt_emt_shoulder_shrug`), 153 actions (survey, craft, heal, melee, jump), 12 `zero_speed` posture loops (`loop_sitting_ground`, `loop_kneeling`, `loop_riding`, ...), 6 `locomotion` |
| `TSCL` > `PXAT` (scale 2.0) | 116 | posture transitions and every ranged dive/tumble/hurry (`hutt_idl_fidget` for sit/kneel/prone, `hutt_std_stand_to_stand_combat` for the ranged ones) |
| `DRAT` (byte copy of a stock set, renamed) | 38 | 28 fire sets (copies of `pistol_combat_standing_fire_3`, `rifle_standing_aimed_fire_3`) and 10 aimed-ready sets (copies of the pistol and rifle `loop_*_combat_standing_aimed`) |
| `YWAT` (byte copy) | 18 | out-of-combat pistol and rifle stances while kneeling, prone, riding, and the polearm/sword ready loops (`loop_pistol_kneeling`, `loop_polearm`...) |
| `SPAT` | 2 | `loop_crouched`, `loop_prone`: idle `hutt_idl_stand_breathe` + the stock-unused `hutt_loc_crawl` |
| `AGAT` over `LOOP` | 2 | `loop_skill` (all 32 dances and 6 music values) and `dance_lyrical` |

Player actions (the full table is in `README.md` section 2): sit/kneel/prone = idle loop + `hutt_idl_fidget` transitions;
dance = `hutt_idl_fidget` loop with a gesture every 2 to 4 s, `skill_action_1..10` = ten one-shot emotes, `skill_mistake` =
`shocked`; riding = `hutt_idl_stand_breathe` (combat riding `hutt_idl_stand_combat`), no bone mask; survey/forage/craft/heal =
`hold object`, `pick up`, `put down`, `point straight`.

**Chairs (owner, 15 Oct 23:15: the server refuses chairs for Hutts until new animations exist).** All 13 chair-related names
are still mapped (`loop_sitting_chair`, both chair transitions, `ag_sitting_chair_*`, `emt_sitting_chair_idl_*`, `heal_*_sitting_chair`)
to the same idle/fidget/look-left/look-right stand-ins, so a chair state the server fails to block cannot freeze the model.
They are a safety net, not a feature: the Hutt would stand through the chair.

**The dance gestures** (Fable's list, translated to ash action names): `sp_02`, `gesticulate_wildly`, `laugh_cackle`,
`shrug_hands`, `greet` (plays `emt_wave_2`), `nod_head_once`; weight 100.0 each (the stock Hutt blocks use 100.0, Fable's note
said 200; weights are relative), interval 2.0 to 4.0 s, loop `hutt_idl_fidget`.

## 3. The check (re-parse of the output; all 21 PASS, rerun with `build_hutt_lat.py --check`)

| check | result |
|---|---|
| parse then rebuild equals the file | identical |
| header path | `appearance/ash/all_b.ash` (unchanged) |
| count field = number of ANIM forms | 837 = 837; also 206 + 631 |
| first 206 entries byte-identical to stock, same order | yes |
| entry names unique; every one of the 631 map actions present, in map order | yes |
| a second, struct-only walker (not `trn_iff`) counts the ANIM forms | 837 |
| every action name in the human tables is present, except the skip rules | human `all_m.lat` (`local_planets.tre`) and `all_f.lat` (`mtg_patch_022`) have 908 entries each but **904 distinct names** (4 names appear twice). 820 of the 904 are in the new table (190 were already); the 84 absent are exactly the rules: 70 `force_*`, 8 `*_jedi_combo_*`, 4 `jedi_*`, 1 `add_force*`, 1 `sword_attack_mask` |
| no `PPTR` (human bone masks) in the added entries | none |
| every referenced `.ans` exists in the archives the live cfg chain loads | 117 distinct `.ans` in the table (116 stock + `hutt_loc_crawl.ans`); 0 missing |
| winning archive per `.ans` | 102 in `data_animation_00.tre` (priority 25), 15 in `patch_05.tre` (31); none from an MTG archive; no `.ans` is held by two archives at the same top priority |
| every `.ans` is a `hutt_*` file, a `CKAT`/`KFAT` animation, and animates only bones that exist in `hutt.skt` (LOD 0, 47 bones) | yes |
| every AGAT gesture is an ash action whose animation is in the table | 14 distinct gestures in 6 AGAT blocks (4 stock in `loop_standing`, 2 new), all resolve |
| **every state loop the ash can enter has a table entry** | 45 loops; **35 were missing from the stock Hutt table** (`loop_sitting_ground`, `loop_kneeling`, `loop_skill`, `loop_riding`, `loop_crouched`, `loop_prone`, the pistol/rifle/polearm/sword kneeling, prone and riding loops...), none are now. This is the "model holds whatever frame it was on" problem of README section 0, measured |
| my writers reproduce real entries byte for byte | `pxat()`: 189 of 189 stock PXAT entries that carry a PUNF; `agat()`: the stock `loop_standing` block; `tscl()`: a human transition; `spat()`: the human `loop_crouched` |

Not a pass/fail: of the 935 animation names the ash can ask for, 731 were missing from the stock Hutt table and 156 still are:
84 are the Force/Jedi names left out on purpose, and 72 exist in **neither** table (35 `face_*` facial expressions, `sp_09..sp_21`,
`emt_trick_1/2`, `std_power_up/down`, `trn_stand_to_stand_combat` and `trn_stand_combat_to_stand`, two names with typos in the ash such as
`std_maniipulate_high`, a few ranged melee names). A human player gets nothing for those either; the list is in the JSON.

## 4. What still looks wrong (nothing below has been seen in a client)

From Fable's list, unchanged in substance:

- Sitting, kneeling, crouching: the Hutt plays its breathing idle, transitions are a `hutt_idl_fidget` shift. Chair is refused by the server; the entries only prevent a freeze.
- Dancing: a sway of fidgets and six gestures; no rhythm; every dance and every instrument looks the same; musicians hold nothing.
- Riding: upright and still; the tail may clip the floater; the pose is the standing idle.
- Survey and crafting: one "hold object" pose.
- 95 emotes play `hutt_emt_shoulder_shrug`.
- Polearm and two-hand sword are swung as the one-hand sword; carbines use the rifle set; one get-hit for every direction; 56 unarmed moves play the two melee attacks.
- No clothing until Level 2.

New from this build:

- **Time scale and loop seams are untested.** `TSCL 2.0` is Fable's value; whether the client treats it as a speed factor or a duration is not confirmed from data, and `hutt_idl_fidget.ans` was not checked for being loop-clean (it is the dance loop and the sit/kneel/prone transition). If the dance loop pops at its seam, or sit/kneel look too quick, change `TRANSITION_SCALE` or the loop file in the script, not the table by hand.
- **Crouch and prone speed.** The one locomotion child is the stock `hutt_loc_crawl`, so sneaking plays the crawl at whatever speed it was authored for; if the Hutt skates, that is the cause.
- **Two masks are mapped although the skip rule lists them:** `polearm_attack_mask` and `unarmed_attack_mask` (Fable's map has them as attacks). Harmless (they are plain `PXAT`, no bone mask). `std_manipulate_low` is not in either human table but the ash asks for it, so it stays.
- **Hutt NPCs change too.** They share `hutt_m.sat`, so after packing they also gain the 631 names; nothing they used before changes.
- **Ten Hutt `.ans` stay unused**: `hutt_idl_stand`, `hutt_idl_stand_look`, `hutt_idl_stand_look_forward`, the three `hutt_rea_stand_get_hit_*`, the two `hutt_rea_swim_get_hit_*`, and the pistol and rifle `standing_aimed_idle` (candidates for kneeling-aimed and a better get-hit later).

## 5. Departures from Fable's map and README (all corrected in the build)

1. **Entry count**: the header count must be raised to 837 (section 1).
2. **Dance gestures**: Fable listed animation names (`emt_gesticulate_wildly`, `emt_wave_2`...); an AGAT needs ash action names (`gesticulate_wildly`, `greet`...). Translated by `gesture_action()`; weight 100.0, not 200.
3. **Rifle stance source**: three YWAT entries copy "hutt `loop_rifle_standing`"; the stock Hutt entry is `loop_rifle` (same three files). Aliased.
4. **`loop_crouched`/`loop_prone`**: the README text says three SPAT children (idle, crawl, crawl); the JSON lists two. Built with two, as the human `loop_crouched` has (idle + walk).
5. The map's `counts` (714 missing, 631 mapped, 84 skipped) add up to 715: 630 human names plus `std_manipulate_low`, which only the ash knows.

## 6. The packing step (Claude, later; nothing is packed here)

1. `python -I Fable-species/s7-hutt/tools/build_hutt_lat.py` (needs the client archives in `SWG-client`); expect the sha256 above and RESULT: PASS.
2. Ship the file **whole**, as MTG's `all_m.lat` already ships: copy `staged/client/appearance/lat/hutt.lat` to `<stage>/appearance/lat/hutt.lat` in the `local_planets` staging folder, after the Hoth/Ossus/species steps and before `tre_write.pack_dir(stage, OUT_TRE)` (the order of `Fable-species/s5/build_test_archive.py`; a `stage_hutt_lat(stage)` helper there is enough). It is a full file, not a patch, and `local_planets.tre` (priority 49) then outranks `patch_05` (31).
3. After the pack: the archive's `appearance/lat/hutt.lat` entry must equal the staged bytes (sha256 above); every other entry unchanged against the previous archive (the S5 check); `tools/hoth/client_load_order.py appearance/lat/hutt.lat` with the test session's login cfg must name `local_planets.tre` as the winner.
4. Owner's client check (README 7.5): `/createCreature object/mobile/hutt_male.iff` first (the NPC Hutt shows the same table, no species work needed), then a player Hutt: `/sit`, `/kneel`, `/prone`, sneak, `/dance basic`, a flourish, survey, a vehicle call, an emote, a pistol and a rifle; no T-pose, no frozen frame. Report which of section 4 are real.
5. The server side (race, species skill, refusals including the chair) is untouched by this table.
