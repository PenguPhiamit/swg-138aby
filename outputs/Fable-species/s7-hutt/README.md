# Species S7: the Hutt — concept, animation map, gear, new animations, Nal Hutta — Fable, 15 Oct 2026

Staging only. Nothing under `/opt/swg` was written; nothing was built or seen in a client. Owner's decision (15 Oct 15:25):
"Hutts launch with remapped animations (sit, dance, riding); Fable designs all three levels tonight (concept, animation map,
Hutt gear list, order), plus the photo studio set and Nal Hutta as a possible Hutt home." The photo studio is in
`Fable-studio/README.md`; Nal Hutta is section 8 here. **Verified** = read from the client archives or Core3-dev tonight with
the project's own tools (`tools/swgfmt`); **proposed** = my design, not yet tested; the real client is the judge of every
look described here.

| file | what |
|---|---|
| `README.md` | this: concept (1), Level 1 animation map (2), Level 2 gear (3), Level 3 new animations (4), species facts (5), what still looks wrong (6), order of work (7), Nal Hutta (8) |
| `animation-map.json` | Level 1 in machine form: 631 `all_m.lat` action names the Hutt table lacks, each with the existing Hutt `.ans` to use, the record kind to write, a note; plus 84 names deliberately left out and the build steps. All 52 distinct `.ans` paths it names exist in the client (`data_animation_00.tre` / `patch_05.tre`; checked) |

## 0. What was checked tonight (verified)

- `appearance/hutt_m.sat` (177 B, `data_other_00`): `MSGN appearance/mesh/hutt_m.lmg`, `SKTI appearance/skeleton/hutt.skt`, `LATX hutt.skt -> appearance/lat/hutt.lat`. `hutt_f.sat` is the same size and shape. The player templates `shared_hutt_male/female.iff` (MTG 023) use them.
- `appearance/skeleton/hutt.skt` (9,253 B, 4 LODs): 47 bones at LOD 0: `root, belly, tail01..tail06, spine, head, jaw, l_eye, r_eye, l_lid, r_lid, nose, tounge01, tounge02, l_eyebrow, r_eyebrow, l_clavicle, l_arm, l_forearm, l_ulna, l_wrist, l_index_01/02, l_middle_01/02, l_pinky_01/02, r_clavicle, r_arm, r_forearm, r_ulna, r_wrist, r_index_01/02, r_middle_01/02, r_pinky_01/02, hold_r` plus the hardpoints `dl44metal_l0, l0, polearm1_polearm, sword1_sword`. No legs, no `hold_l`, three fingers a hand. The human `all_b.skt` names its bones `lThigh, spine1..3, neck, Head, lClav, hold_l...`: not one name matches, which is why human clothing and masks cannot attach.
- `appearance/lat/hutt.lat` (winning copy `patch_05.tre`, 49,242 B): header `appearance/ash/all_b.ash` (the **same state hierarchy as humans**), 206 ANIM entries of four kinds: 190 PXAT (one file), 3 SPAT (walk/run blends), 3 YWAT (turn left/right + idle), 10 DRAT (directional ready/fire sets). The entries reference 116 of the 127 `hutt_*.ans` files in the client; the 11 unused include `hutt_loc_crawl.ans`, `hutt_idl_stand.ans`, `hutt_idl_stand_look_forward.ans`, swim get-hits and two aimed idles.
- `appearance/lat/all_m.lat` as installed (`local_planets.tre` = MTG's whole-file copy, 361,386 B): 904 entries (the stock patch_11_02 copy has 873). 714 names are absent from the Hutt table. The `all_b.ash` states both tables share: root/standing, sitting_chair, sitting_ground, crouched (sneaking), kneeling, **skill** (the entertainer performance state), riding, prone, blocking, stand_attention, swimming, knocked_down, incapacitated_face_up/down/water, and the weapon states pistol, rifle, sword_1h, sword_2h, polearm, each with a combat child. So the client *has* a sitting state for a Hutt; it simply finds no `loop_sitting_ground` in `hutt.lat`, and the model holds whatever frame it was on.
- Dances and music are not ANIM names: `loop_skill` is an SPAT whose idle is an SSAT on the performance variable (values `dance_1..dance_32`, `music_1..6`, 38 of them), `skill_action_1..10` and `skill_mistake` switch on the same variable; Core3 sends `"dance_" + danceVisualId` (`PerformanceManager.cpp:337`). Riding: `loop_riding` is an SSAT on `rider_pose` (46 values such as `vehicle_landspeeder`, `vehicle_barc_speeder`, `vehicle_hover_chair`), fed from `datatables/mount/rider_pose_map.iff` (70 rows installed); that is the entry MTG's table added for the BARC on 15 Oct.
- Core3-dev: `Races.h` ends at Chiss (`0xE7`); `CreatureObject.idl` has `CHISS = 0xE7` (S6 stages Nautolan `0xE8`, Togruta `0xE9`); `managers/creature_manager.lua` `aiSpeciesData` row `{31, "hutt"}` already exists for NPC Hutts; `NameManager::getSpeciesData` falls back to human names for unlisted species; `PlayerCreationManager::canWearRace` (the Chiss rule) refuses any wearable whose `playerRaces` list lacks the race file unless the race is in `humanRigRaces`, with the message `"You lack the necessary requirements to wear this object"` (`PlayerContainerComponent.cpp:36`) and a species-aware vendor message path at `CreatureManagerImplementation.cpp:1319`. The MTG vehicles exist client-side only (`object/mobile/vehicle/shared_a1_deluxe_floater.iff`, `shared_hover_chair.iff`, `shared_mechno_chair.iff` in MTG 022, all children of `shared_landspeeder_base.iff`); dev has 13 stock vehicle Lua templates and MTG's garage-display statics, no vehicle template for the floater.

## 1. Concept: the Hutt in 138–139 ABY

Krayt is dead on Coruscant (138 ABY) and the One Sith have gone to ground; the Fel loyalists and the Alliance Remnant are
rebuilding a Republic. Through all of it the kajidics never stopped trading. Under Krayt's Empire the Hutt Cartel kept its
licences by paying and informing; now that the Empire has fractured the Hutts are the one power with ships, credits and
warehouses on every Rim world, and they know it. Nar Shaddaa is the open market of the Legacy years; Nal Hutta is the
council world (section 8). In Legends the Legacy era shows Hutts as club owners and brokers on Coruscant itself (Queen
Jool's establishment is the known example), as cartel bosses who hire Mandalorian and Feeorin muscle, and as shipping
magnates. That is the register for our player Hutt: not a soldier, a **principal**.

**Kajidics.** A Hutt belongs to a clan-corporation (kajidic) and names it as a surname. We use the Legends names only as
lore background (Desilijic, Besadii, Anjiliac, Gorensla are the famous ones) and invent our own for play so no player
collides with a comic-book family: see the name tables in 5.5. The player picks a kajidic in the biography, not in a table;
it matters to roleplay and to the Nal Hutta content later (kajidic palaces as player-city sites).

**Roles the owner named:** trader and crime lord, with politician and merchant beside them. In pre-CU terms the Hutt is
built for the **non-combat spine**: Artisan -> Merchant, Architect, Tailor (yes: a Tailor who cannot wear what he makes is
good comedy and good lore), Weaponsmith, Armorsmith, Chef; **Politician** (mayor of a Hutt enclave city); **Entertainer**
(the remapped dance of Level 1 makes a Hutt dancer possible; musicians show no instrument until Level 2 gives them a hand
piece); **Image Designer**; **Smuggler** (pistols: the Hutt has the full 20-pose pistol set); **Brawler** (unarmed and the
one-hand sword set exist); **Marksman/Rifleman/Pistoleer** (rifle poses exist); **Creature Handler** (no animation need);
**Scout/Ranger** for camps and survey (remapped). Not recommended at launch: Pikeman and Swordsman (no polearm or
two-hand stance; the moves are mapped to the one-hand sword set so nothing freezes, but the weapon is held wrong), Teras
Kasi (the 56 unarmed moves all play as the two Hutt attacks), Jedi (no Force animations are mapped; owner's call later).

**What a Hutt player gets that nobody else has:** the biggest body in the game, a pistol stance that reads as a boss, 22
real Hutt emotes (bow, explain, furious, laugh, nervous, point, shrug, threaten, greet, goodbye, eat), and later the gear
of section 3. What they give up: human clothing and armour (section 5.4), speeder bikes and creature mounts (the launch
vehicle is a floating platform), and a crouch that is a crawl.

## 2. Level 1: the animation map (data only, `hutt.lat` in `local_planets.tre`)

Principle: every state and action a player can reach must find an entry in `hutt.lat`, so nothing freezes or T-poses.
Where the Hutt has no matching motion, the entry points at the idle or at the nearest emote. `animation-map.json` lists all
631 entries; the table here explains the choices that matter.

| Player action | `all_m.lat` name(s) | Hutt file to use | Why |
|---|---|---|---|
| Sit on the ground, stand up | `loop_sitting_ground`, `trn_standing_to_sitting_ground`, `trn_sitting_ground_to_standing` | `hutt_idl_stand_breathe.ans` for the loop; `hutt_idl_fidget.ans` as the transition | a Hutt is already seated: sitting = the idle. The human entry carries `mask_upper_body.iff` (human bone names); drop the mask. The fidget is a short shift of the bulk, so the posture change is visible without a new animation |
| Sit on a chair | `loop_sitting_chair`, the two chair transitions, `ag_sitting_chair_*` | same; ambient fidgets alternate `hutt_idl_stand_look_left/right.ans` and `hutt_idl_fidget.ans` | the Hutt will stand through the chair at launch (section 6); the owner may refuse chairs instead (5.4) |
| Kneel | `loop_kneeling`, `trn_standing_to_kneeling`, `trn_kneeling_to_standing` | idle + fidget | no legs; kneeling is a posture the server needs (medics, some emotes), so it exists but looks like standing |
| Crouch / sneak | `loop_crouched` (SPAT), `trn_standing_to_crouched`, `trn_crouched_to_standing`, `trn_crouched_to_kneeling` | idle + **`hutt_loc_crawl.ans`** as the crouched walk | the unused stock crawl is the one Hutt motion that reads as "low and quiet" |
| Prone | `loop_prone` (SPAT) and its transitions | idle + crawl | not `hutt_idl_incapacitated.ans`, which reads as dead |
| **Dance** (all 32 dances) | `loop_skill` (one branch for every `dance_N` / `music_N` value), `loop_dance_test`, `dance_lyrical` | an **AGAT** (ambient-gesture) form, interval 2.0–4.0 s, LOOP `hutt_idl_fidget.ans`, gestures `sp_02` (explain enthusiastic), `emt_gesticulate_wildly` (furious), `emt_laugh_cackle`, `emt_shrug_hands`, `emt_wave_2` (greet), `emt_nod_head_once` (yes), weight 200 each | the Hutt's own standing idle already works this way (its first AGAT fires `angry`/`threaten` every 5–10 s on a mood); copying that block with a short interval makes the Hutt sway and gesticulate every few seconds. It is the owner's "looping emote" without any new file. No rhythm; no instrument for musicians |
| Flourishes | `skill_action_1..10`, `skill_mistake` | ten one-shot emotes in turn (`explain_enthusiastic`, `greeting_enthusiastic`, `laugh`, `wave_item`, `furious`, `shrug`, `cbt_throw_item`, `bow`, `explain`, `greet`); mistake = `shocked` | flourishes are one-shots over the loop; the human table switches them per performance, the Hutt needs one each |
| **Ride** | `loop_riding` (SSAT on `rider_pose`), `loop_combat_riding`, `loop_*_riding` | `hutt_idl_stand_breathe.ans` for every rider pose, no mask; combat variant `hutt_idl_stand_combat.ans` | the body rests whole on the vehicle. **Launch vehicle: the A1 Deluxe Floater** (`object/mobile/vehicle/shared_a1_deluxe_floater.iff`, MTG 022; `rider_pose_map` gives it `vehicle_landspeeder`; appearance `pv_a1_deluxe_floater.sat`, MTG 016): a flat repulsor platform the Hutt's bulk can sit on, the Legends sled look at $0 of art. Its deed, PCD and mobile templates exist client-side; the server needs the three Lua templates (7.3). All other vehicles and creature mounts are refused for Hutts (5.4) until Level 3 gives a reclined pose |
| Survey, sample, forage | `std_survey`, `std_forage` | `hutt_std_hold_object.ans`, `hutt_std_pick_up_object.ans` | holds the device up / reaches to the ground. The human survey uses PPTR with `mask_spine3_arms.iff`: use PUNF, no mask |
| Craft, use objects | `std_manipulate_high/medium/low` | hold / pick up / put down | the three Hutt object animations are exactly the three heights |
| Heal self / other (all postures) | `heal_self*`, `heal_other*`, `sitting_*_heal_*` | hold object / `hutt_emt_point_straight.ans` | stim to the chest; reach toward the patient |
| Emotes (249 human names) | `emt_*` | by keyword to the 22 Hutt emotes (wave -> greet, bow -> bow, nod -> yes, shake head -> no, laugh family -> laugh, threats -> threaten, anger -> angry, applause/cheer/celebrate -> greeting enthusiastic, beg/cry/sad -> nervous, shock/cover -> shocked, eat/drink -> the two eats, look/search -> alert, think/talk -> explain, yawn -> stretch, afk/sleep -> fidget); 95 with no Hutt sense (adn, cartwheel, chicken...) -> `hutt_emt_shoulder_shrug.ans` | the ash already aliases chat emotes to these names (`ACTN bow -> emt_bow2`), so only the ANIM entries are missing; the shrug fallback means no emote ever freezes the model |
| Knockdown, incapacitation, getting up | `loop_knocked_down`, `loop_incapacitated_face_down`, `trn_*_to_incapacitated_*`, `trn_knocked_down_to_standing` | `hutt_idl_incapacitated.ans`, `hutt_rea_stand_combat_get_hit_heavy.ans`, `hutt_std_incapacitate_to_stand.ans` | one incapacitated pose serves face up and face down |
| Ranged from kneeling, prone, riding | `loop_pistol_*`, `loop_rifle_*` (18 YWAT/DRAT), `*_kneeling_fire_N`, `*_prone_fire_N`, fire 9/11, reloads | byte-copies of the Hutt standing ready and fire sets; reload = hold object | a Hutt shoots the same whatever the server calls its posture; 116 ranged transitions (dive, tumble, hurry, kip) all become the short stand-to-combat shift |
| Polearm, two-hand sword, extra unarmed | `pole_*`, `sword_2h_*`, `unarmed_*showoff*` | the one-hand sword light/heavy and the two melee attacks | nothing freezes; the weapon is held wrong (section 6) |
| Jump, flare, heavy weapon, charge, intimidate, war cry | `jump`, `fire_flare`, `heavy_weapon_launch`, `cbt_*` | fidget, throw, throw, threaten, threaten, furious | a Hutt does not jump |
| **Not added** (84) | `force_*`, `jedi_*`, `*_jedi_combo_*`, `add_force`, the three `*_attack_mask` | | no Hutt Jedi at launch; masks name human bones |

**Record kinds Claude writes** (from the dumps; all little-endian strings NUL-terminated): `ANIM = INFO "<name>\0" + sub-form`.
`PXAT/0000 = INFO "<ans>\0" + PUNF "<category>\0<category>\0"` (categories in use: emote, yaw, zero_speed, locomotion,
transition, action). `TSCL/0000 = INFO float32 2.0 + PXAT` (transitions). `SPAT/0000 = INFO byte 0x03 + idle + PXAT walk +
PXAT run` (as the Hutt `loop_standing`; for crouch/prone both locomotion children are the crawl). `YWAT` and `DRAT`: byte-copy
the named Hutt entry, change the INFO name. `AGAT/0000 = INFO float32 min, float32 max seconds + ACTN (int16 count, then
name\0 + float32 weight pairs) + FORM LOOP`. Append after the 206 existing entries inside `FORM LATT > FORM 0000`; there is
no count chunk. Round-trip the file with `tools/swgfmt/trn_iff.py`, resolve every `.ans` against the archives, and ship it
whole in `local_planets.tre` the way MTG's `all_m.lat` already ships (`MTG-merges/shadow-audit.md`, WHOLE_FILES; the Hutt
file is 49 KB, so a full copy costs nothing).

## 3. Level 2: Hutt gear rigged to `hutt.skt` (Blender, NSG SWG Tools 3.1.4)

How a wearable works here (verified in the formats, proposed for the Hutt): a visible wearable is a `.sat` of its own naming a
skinned `.mgn` (via a `.lmg` LOD list) whose vertex weights name bones; the client attaches it to the wearer's skeleton **by
bone name**, which is why human clothes cannot sit on a Hutt and why Hutt gear must be weighted to `belly`, `spine`,
`l_clavicle`... The add-on loads `hutt.skt` (`swg_load_skt_mgn`), lets us model and weight-paint against it, and exports
`.mgn`, `.lmg` and `.sat` (`export_mgn.py`, `export_lmg.py`, `export_sat.py`). Each item needs: the art (mesh, DDS via texconv,
a shader cloned from a stock `_as8`/`_aa7` as in `Fable-asset-pipeline/README.md` step 5), a client object template cloned from
the nearest stock wearable with `appearance` pointed at the new `.sat`, the matching server Lua with `playerRaces` = the two
Hutt race files only, a CRC-table row and strings. Pre-CU jewellery (rings, bracelets, necklaces) has **no visible mesh**, so
"Hutt jewellery" must occupy a visible slot to be seen; I put the jewels on the headdress, the collar and the arm bands.

Priority order (1 = first into Blender):

| # | Item | Role | Slot (stock base to clone) | Art note for rigging to `hutt.skt` |
|---|---|---|---|---|
| 1 | **Kajidic sash** (broad diagonal sash with a clan seal, three colour variants) | the one piece every Hutt wears; the "I am somebody" marker | `chest1` (clone `wearables/shirt/shirt_s01`, call it `hutt_sash_s01`) | a strip from `r_clavicle` over the belly to the left flank: weights `r_clavicle` 0.6/`spine` 0.4 at the top, `belly` 1.0 across the front, fading to `tail01` 0.5 at the hip; keep it 3–4 cm off the body so the belly breathe (`hutt_idl_stand_breathe`) does not poke through; ~600 triangles, one 512 texture with the seal as a decal |
| 2 | **Jewelled collar** (a heavy neck ring with pendants) | wealth; the crime lord's signature | `chest2` (clone `wearables/vest/vest_s01`, `hutt_collar_s01`) | ring around the neck base weighted `spine` 0.7/`head` 0.3 so it turns with the head a little; pendants hang on `spine` only; metal shader `_as8` with an emissive gem decal |
| 3 | **Arm bands** (pair, wide bracelets with inlay) | jewellery that is actually visible | `bracer_l` + `bracer_r` (clone `wearables/armor/.../bracer` shells or `wearables/bracelet`? no: bracelets are invisible; clone the padded armour bracer template and strip its armour stats) | one band each at `l_forearm`/`r_forearm` 1.0; cylinder, 200 triangles each |
| 4 | **Headdress / skullcap** (a flat jewelled cap with a hanging fringe; a visor variant for the pilot look) | the "merchant prince" silhouette; also hides the bald dome for players who want it | `hat` (clone `wearables/hat/hat_s01`, `hutt_headdress_s01`) | weighted `head` 1.0; the fringe `head` 0.8/`jaw` 0.2 so the mouth moving in `emt_explain` tugs it; check it clears `l_eyebrow`/`r_eyebrow` motion |
| 5 | **Mantle** (a short cape over the shoulders, open at the front) | the "robe" the owner asked for, cut for a body with no waist | `cloak` (clone `wearables/cloak/cloak_s01`? a pre-CU cloak slot exists on the player template; confirm in `abstract/slot/descriptor/player.iff`) | a yoke on `l_clavicle`/`r_clavicle`/`spine`, panels down the back weighted `spine` 0.6/`belly` 0.4; stop above `tail01` so the tail drag in `hutt_loc_walk` does not tear it; cloth shader `_aa7` with alpha edge |
| 6 | **Belly plate** (a single armour plate over the front with straps) | the armour piece: a Hutt bodyguard-boss look, armour stats of a padded chest | `chest2` armour (clone `wearables/armor/padded/armor_padded_s01_chest_plate`) | rigid plate weighted `belly` 1.0, straps `spine`/`l_clavicle`/`r_clavicle`; the plate must follow the breathe, so weight its rim to `belly` and leave the straps elastic |
| 7 | **Tail guard** (segmented plates along the tail top) | completes the armour set; the piece that shows the Hutt is armoured from any angle | `pants1` (clone `wearables/pants/pants_s01`; the Hutt has no legs so the slot is free) | six segments, one per `tail01..tail06` at 1.0 with 0.2 bleed to the neighbour; test against `hutt_loc_run` (the tail swings widest there) |
| 8 | **Trophy pack** (a back frame with a hookah, a cash box, a hanging trinket) | the trader on the move | `back` (clone `wearables/backpack/backpack_s01`) | one rigid piece on `spine` 1.0, offset back and up; the stock `gmf_huttlet_backpack_m.sat` is a human backpack shaped like a baby Hutt: reference only, do not reuse (human rig) |
| 9 | **Hand piece for musicians** (a small instrument the Hutt's three fingers can hold) | lets a Hutt Entertainer show an instrument at all | a tangible on `hold_r`, as weapons attach | later; needs the instrument-equip code path to accept a Hutt hand |
| 10 | **Repulsor sled** (a real Hutt sled: low platform, a rail, a cushion) | replaces the A1 Deluxe Floater placeholder; the Legends look | a vehicle: new `pv_hutt_sled.sat` + `.skt` (vehicles are skinned too: `pv_a1_deluxe_floater.skt` is the model), rows in the four `datatables/mount/*` tables, deed/PCD/mobile templates | the hardest piece because a vehicle's `.sat` names its own skeleton and the rider sits at a saddle hardpoint; copy the floater's skeleton (one root, one saddle) and swap the mesh. Do last, after Level 3's reclined pose exists |

Checks before any item ships: round trip the `.mgn` through the add-on (import -> export -> identical IFF structure, as the
wall model proved for `.msh`), attach it to `hutt_m.sat` in a test `.sat` and view it on a Hutt NPC in the client at idle,
walk, run, pistol ready and `emt_furious` (the widest arm swing). Nothing here is copied from stock Hutt NPC dress: the
`dressed_hutt_expedition_force_leader` body is one baked mesh, not separable clothing.

## 4. Level 3: new Hutt animations (`.ans`), in priority order

1. **Settle / sit** (3 files): `hutt_std_settle` (standing -> settled: the body sags, hands fold on the belly, 1.5 s),
   `hutt_idl_settled_breathe` (loop), `hutt_std_settled_to_stand`. Replaces the Level 1 idle in `loop_sitting_ground`,
   `loop_sitting_chair`, `loop_kneeling` and their transitions. First because /sit is the most used non-combat action and the
   only one where the idle stand-in is plainly wrong.
2. **Dance loop + two flourishes** (3): `hutt_dnc_sway_loop` (weight shifts side to side, arms roll, tail tip beats time),
   `hutt_dnc_flourish_1` (arms up, head back), `hutt_dnc_flourish_2` (a slow turn of the upper body). Replaces the AGAT
   stand-in in `loop_skill` and two `skill_action` entries.
3. **Riding pose** (1): `hutt_mnt_ride_sled` (reclined, one arm on the rail, tail trailing). Goes into `loop_riding` for
   `vehicle_landspeeder` (the floater) and later the sled.
4. **Low bow / "kneel"** (1): `hutt_std_bow_low` for `loop_kneeling` and the kneel transitions.
5. **Survey and craft** (2): `hutt_std_survey` (device raised, head tilts to read it), `hutt_std_craft` (both hands work at
   waist height, loop).
6. **Heal** (1): `hutt_std_heal_reach`.
7. **Emotes** (6): clap, cheer, belly laugh, rude slap, a slow sarcastic nod, a dismissive flick: the six fallbacks players
   will notice first.
8. **Crouched slither** (1): a quieter, lower `hutt_loc_sneak` to replace the crawl stand-in.
9. **Carbine and two-hand stances** (2 sets): only if Hutt Carbineers or Swordsmen are wanted.

**What `export_ans.py` must become to be usable** (read tonight at
`C:/Users/Pengw/Tools/blender-3.6.23-windows-x64/3.6/scripts/addons/io_scene_swg/export_ans.py`): it is a skeleton, not an
exporter. (a) It is not registered: `__init__.py` imports and registers every other operator (`import_scene.mgn`,
`export_scene.mgn`, `import_scene.lod`...) and never mentions `export_ans`; it needs an `ExportANS` operator and menu entry
like `ExportMGN`. (b) `create_kfat` writes a `FORM KFAT/0003` with hard-coded zeros: frame count 0, one transform `XFIN` with an
empty joint name, one rotation channel with one keyframe; nothing is read from the Blender action (`fcurves` are only in a
commented-out block). (c) `create_ckat` (the compressed form the stock files use: all 127 Hutt files should be checked for
KFAT vs CKAT before choosing) is the same stub. (d) The real work: walk the armature's bones in `hutt.skt` order, bake the
action at 30 fps, write per-bone rotation channels (quaternions, SWG order) and translation only for `root`, static values
for unchanged bones, and the message/locomotion metadata (`loop`, speed) the stock files carry; then prove it by a **round
trip**: import a stock `hutt_emt_bow.ans` (no importer exists either: writing `import_ans.py` first is the cheaper proof,
because a stock file re-exported identically settles the format), then export a one-bone test onto the Hutt NPC in the
client. This is the GPT/Claude research task the owner named; it serves every creature, not just the Hutt.

## 5. Species facts (proposed)

### 5.1 `player_species.stf` text (ours, not copied)

- `name_hutt` = "Hutt"
- `desc_hutt` = "Slow to move and quick to count, the Hutts of Nal Hutta have run the Rim's markets for longer than the
  Republic has had a Senate. A Hutt is immense, long-lived and hard to kill, resists mind tricks that bend lesser beings, and
  treats every conversation as a negotiation already won. Krayt's Empire tolerated the kajidics for their ships and their
  silence; its fall left them the richest power still standing. Hutts wear only Hutt-made gear and travel by repulsor
  platform." followed by the stock ATTRIBUTES block in the S5 format (`\>024Health: \>128+100\>000` ...) with the numbers
  of 5.2.
- `skl_n.stf` `species_hutt` = "Hutt Special Features"; `skl_d.stf` = "Hutt Abilities".

### 5.2 Attributes (`racial_mods.iff` row + `baseHAM` in the race template; 900-point budget like every stock row)

| Health | Strength | Constitution | Action | Quickness | Stamina | Mind | Focus | Willpower |
|---|---|---|---|---|---|---|---|---|
| 100 | 150 | 300 | 0 | 0 | 50 | 0 | 0 | 300 |

Constitution and Willpower carry the Hutt (hard to kill, hard to sway); nothing in Action or Quickness (slow); a little
Strength and Stamina for the bulk. `attribute_limits.iff`: derive the Hutt row the way the stock pairs do (human limits
shifted by the mods); Claude's `species_tables.py` already clones a row, check one stock pair (Wookiee vs human) to confirm
the shift rule before trusting it.

### 5.3 Starting skills and the species skill

`startingSkills = { "species_hutt", "social_language_basic_comprehend", "social_language_basic_speak" }` plus
`social_language_huttese_comprehend` and `_speak` **if** those rows exist in today's `skills.iff` (Huttese is a pre-CU
language skill; verify before adding). `species_hutt` = a clone of `species_human` with `SPECIES_REQUIRED = hutt`, as Chiss.
Creation UI block (`ui_avatardata.inc`) in the Chiss shape with `appearancemale/female = shared_hutt_male/female.iff`,
`Name='hutt'`, `skill='species_hutt'`; camera offsets need the Hutt's height: start from `cameraoffsety='1.2'`,
`cameraoffsetz='6'` (the body is as tall as a Chiss and three times as long) and adjust in the client. Hair: a NAME-only
block (hairless, as S6's Nautolan). Default clothing: **none** (empty `default_pc_equipment` block; the profession default
blocks list no wearables), because every stock default is human-rigged.

### 5.4 Actions that must still be refused, with the exact messages

| Action | Rule (server, C++) | Message (system message, our text) |
|---|---|---|
| Equip any wearable whose `playerRaces` lacks the Hutt race file (all 703 stock wearables and armour) | already refused by `canWearRace` because `hutt_male/female` are **not** added to `humanRigRaces`; add a Hutt branch at `CreatureManagerImplementation.cpp:1319` (next to the Ithorian/Wookiee vendor texts) and in `PlayerContainerComponent.cpp:36` | **"That was tailored for a two-legged frame. A Hutt wears Hutt-made gear only."** |
| Mount a creature, a speeder bike, a landspeeder, a jetpack or any vehicle not on the Hutt list | new check in `MountCommand.h` after the vehicle checks (line 60 region): if the rider's species is Hutt and the vehicle template is not in `huttVehicles` (Lua list in `player_creation_manager.lua`, launch value `{"object/mobile/vehicle/a1_deluxe_floater.iff"}`), refuse | **"That saddle was never built for a Hutt. A Hutt travels by repulsor platform."** |
| Call a vehicle whose deed a Hutt holds but may not ride | same list, checked in `VehicleControlDeviceImplementation::generateObject` so the datapad refuses before the vehicle appears | **"A Hutt cannot ride this. Sell it, or give it to someone with legs."** |
| Sit on a chair (optional, owner's call) | `SitCommand`'s chair branch: refuse for Hutts until Level 3 | **"No chair in the galaxy was built for a Hutt. You settle where you are."** then perform the ground sit |
| Equip a polearm or two-hand sword (optional) | not refused by default: the moves map to the one-hand set so nothing breaks; refuse only if the look offends in the client | **"A Hutt's arms were not made for that weapon."** |

Everything else (dance, kneel, crouch, prone, survey, craft, heal, every emote) is **allowed** and animates through Level 1.

### 5.5 Random names (our own tables, `managers/name/species/hutt.lua` in the human.lua shape; `NameManager::getSpeciesData` gets a `case CreatureObject::HUTT: return huttData;`)

- First names, 2–3 syllables, vowel-heavy with a doubled consonant or a hard ending. Syllables to combine: `Bor Gar Zor Dur Jil Mal Vog Nem Sud Kar Zav Grob Teem Ool Quan Ruk Mab Dess Tog Ull` + `ba ga dda rra llo vo mo ro ssa uk ool oga ulla eemo`. Examples the rules produce: Borvadda, Garulla, Zorrob, Dessuk, Teemollo, Quanoga, Rukmo, Ullavo.
- Last names = kajidic names (our inventions, no Legends clan): `Dromuul, Kessoth, Vollaka, Narissik, Tashuga, Bessolo, Qunaari, Zhorrak, Mogadda, Ollumbra, Kirrosta, Vendassi`; 40 % chance of no surname (a Hutt without a clan is a Hutt in disgrace, a roleplay hook).
- No apostrophes or hyphens (`specialCharChance = 0`); the filter rejects the Legends family names Desilijic, Besadii, Anjiliac, Gorensla and the first names Jabba, Ziro, Gardulla so no player claims them.
- Female Hutts take the same tables (Hutts are hermaphroditic in Legends; the two templates differ only in mesh).

### 5.6 Species id

`CreatureObject::HUTT = 0xEA` (next after S6's Togruta `0xE9`), `getSpeciesName() = "hutt"`, `SPECIES_HUTT` in
`DirectorManager.cpp`, two `Races.h` rows (`hutt_male`, `hutt_female`; `SharedRace` = SOE CRC of the shared templates, computed
by Claude as for Chiss). Option Claude may prefer: reuse `31`, the stock `aiSpeciesData` index for NPC Hutts, so NPC and player
Hutts share one species number; then check nothing in the player path assumes species < 0xE7 means a stock player race.

## 6. What still looks wrong after Level 1 (honest list)

- Sitting, kneeling and the chair: the Hutt stands. The chair clips through the body. (Level 3 item 1, or refuse chairs.)
- Dancing: a sway of fidgets and arm gestures, no rhythm, every dance the same; musicians hold nothing.
- Riding: the Hutt sits upright on the floater like a statue; its tail may hang through the platform depending on the saddle
  hardpoint height (the real client shows this; a `valid_scale_range` row for `pv_a1_deluxe_floater.sat` already allows scale
  0.5–2.5, so scaling the vehicle up is a lever).
- Survey and crafting: "hold object" is one pose; the sampling tool is held like a cup.
- 95 emotes shrug.
- Polearms and two-hand swords are swung like a one-hand sword; carbines use the rifle set (check whether the client sends
  `carbine_*` names: none exist in either table, so carbines are already the rifle set for everyone).
- The Hutt's one get-hit pose for every direction, and its two melee attacks for all 56 unarmed moves: that is the stock NPC
  table and nothing new.
- No clothing at all until Level 2 item 1 ships; a naked Hutt is the stock NPC look, so this is acceptable, not broken.

## 7. Order of work (patterned on Chiss S3–S5), and who builds what

1. **Fable (done tonight):** this README, `animation-map.json`.
2. **Claude, client data (`local_planets.tre`), in the S5 builder:** (a) the modified `appearance/lat/hutt.lat` from the JSON,
   round-tripped and resolved; (b) `stage_species(['hutt'])`: `racial_mods` and `attribute_limits` rows (5.2), the `species_hutt`
   skills row and `skl_n/skl_d` strings, `player_species.stf` (5.1), the two `ui_avatardata.inc` blocks, NAME-only hair block,
   empty equipment blocks, `customization_data` rows for the Hutt body (the 2016 package has them; re-emit as data; the ACST
   must be diffed for `appearance/hutt_m.sat` the way S6 did Togruta: Hutt skin palettes are an open question until that
   diff); (c) nothing new for the floater: its client files are all in MTG 016/017/022 and the four mount tables already carry
   its rows (checked in the installed `local_planets.tre`).
3. **Claude, server (dev patch, `git apply --check` clean, luac ok):** `Races.h` two rows, `CreatureObject.idl` `HUTT`,
   `DirectorManager.cpp`, `object/creature/player/hutt_male.lua` / `hutt_female.lua` (baseHAM of 5.2, starting skills of 5.3),
   `objects.lua` declarations and `serverobjects.lua` includes; **no** `humanRigRaces` pairs; the three refusals of 5.4 with their
   messages; `huttVehicles` list; `managers/name/species/hutt.lua` + the `NameManager` case; the A1 Deluxe Floater as a vehicle:
   `object/mobile/vehicle/a1_deluxe_floater.lua`, `object/tangible/deed/vehicle_deed/a1_deluxe_floater_deed.lua`,
   `object/intangible/vehicle/a1_deluxe_floater_pcd.lua` cloned from the x34 landspeeder trio (speed 20, the floater is a
   platform), `templateType` set (the BARC lesson, dev `740b2426`), and a schematic or a Hutt-only vendor to obtain the deed.
4. **GPT (Medium): review** of the patch and of the lat build; **research (Level 3):** the `.ans` KFAT/CKAT layout from the
   127 Hutt files and Core3's `utils/engine3` readers, written up as a format note with a round trip plan for `import_ans.py`
   / `export_ans.py` (no Blender runs tonight; nothing downloaded).
5. **Owner check (one creation visit):** Hutt in the species list, both genders, the description; a Hutt Artisan is created
   (expect: no default clothes, Species: Hutt in the skills window, HAM 100/150/300/0/0/50/0/0/300 plus profession); /sit,
   /kneel, /prone, sneak, /dance basic, survey, a human shirt refused with the 5.4 text, a speeder deed refused with its text,
   the floater deed called and ridden; screenshots front/side/back for section 6.
6. **Level 2** starts after the check with item 1 (the sash); **Level 3** after GPT's format note proves a round trip.

## 8. Nal Hutta as the Hutt home (`terrain/hutta.trn`, MTG `mtg_planets.tre`)

**What it is (verified tonight):** `hutta.trn` is 1,106,071 B, `PTAT 0014` (the modern layout Core3 and our Ossus use). Its DATA
header still carries the SOE build name `...\terrain\rori.trn`: Darklight's Nal Hutta was made from **Rori's terrain**,
heavily edited (0 of 270 4-KB blocks match the stock `rori.trn`, 1,129,001 B). Map 16,384 m, global water at **75 m** with
`wter_rori_swampbrown_spec` (brown swamp water), 16 fractal families, 88 layers (13 fractal heights, 19 constant heights, 77
circle boundaries, 24/14 flora layers, 11 shader-filter layers, 5 slope filters, one exclusion), 6 environment families
(`mainswamp`, `foggyswamp`, `islands-placeholder`...). `datatables/environment/hutta.iff` (25 rows; Dathomir misty-falls sky,
Dathomir cloud tiles), `datatables/clientregion/hutta.iff` (one row: **`@hutta_region_names:bilbousa`** at (-746, 1645), r 300;
the string file is not in the archives), `terrain/environment/hutta.iff` (sky), `snapshot/hutta.ws` (25,795 B, 281 nodes,
163 at world level, 33 templates). MTG 022 adds `texture/ui_planet_sel_nalhutta.dds`, `ui_map_nalhutta.dds`,
`terrain/environment/nalhutta.iff` and a colour ramp `terrain/colorramp/nalhutta_test.tga`. The installed planet CRC table
already has both `hutta` and `nalhutta` entries (MTG's merged table), so the zone name is registered client-side.

**The snapshot** is one town, Bilbousa, in a 480 x 600 m box (x -989..-505, y 1260..1853, ground 80–82 m: a flat shelf just
above the 75 m swamp). Buildings: Tatooine starport, cantina, bank, capitol, cloning facility, hotel, salon, parking garage,
Jabba's palace shell (`shared_palace_tatooine_jabba`) at the south end, **four Jabba-palace towers**, Nym's stronghold (Lok),
~30 Tatooine filler blocks, 10 merchant tents, 11 large Jawa tents, 16 banners, 2 Corellian braziers, and **70 green street
lamps**. Everything is stock art; the planet file and the layout are Darklight's work (catalogue: Levarrishawk/Darklight,
public version, **P, credit required**; the line in `Content-catalogue/SWG-content-catalogue.md`, Nal Hutta row; Sunrunner's
later Nal Hutta is a separate permission case and is **not** here).

**Does it fit 138–139 ABY?** Yes, better than most stock worlds: Nal Hutta in Legends is the kajidics' council world, a
polluted swamp planet with a capital, Bilbousa, and clan palaces; a brown-water swamp with one dense town of towers and tents
is exactly the register, and the Legacy years changed nothing there (the Hutts kept their homeworld through the Vong war and
Krayt). What does not fit is the **Tatooine architecture**: Bilbousa should read as Hutt palatial (domes, ramps, water
gardens), not Mos Eisley. At $0 the fix is dressing: Hutt POI pieces (`object/building/poi/hq/shared_hutt_lrg/med/sm.iff`,
the Tatooine Hutt assassin and businessmen camp sets, the Yavin Hutt scavenger camps, `shared_tatooine_hutt_cave.iff`),
Jabba-palace towers for every kajidic seat, green and amber lamps, banners with kajidic seals (our textures), and a spaceport
renamed. The planet also needs a reason for non-Hutts to come: the Hutt vendors of section 7.3, a smuggler mission terminal
set, a kajidic faction standing, and later the Nal Hutta content of a Hutt-home week.

**What a first look needs (Claude, test galaxy):** (1) `hutta` in `TEST_ZONES`/`ZonesEnabled`; (2) a `hutta` block in
`planet_manager.lua` (travel point at the starport pad: building at (-767, 80, 1795), yaw 180, so the pad offset is the Ossus
+20.3/+17.8 pattern -> test (-746.7, 80, 1812.8) and adjust; weather on, GCW off); (3) `managers/planet/hutta_regions.lua`
with the four edge strips, Bilbousa as CITY + NOSPAWN (r 400) with a no-build circle (r 600), no spawns anywhere else yet;
(4) client: `string/en/hutta_region_names.stf` (ours: "Bilbousa"), `planet_n` "Nal Hutta", travel rows (Tatooine <-> Nal Hutta
is the lore route), `waypoint_planets` pointing at MTG's `ui_planet_sel_nalhutta` if a `.apt` exists for it (else the Rori
globe as placeholder), loading screen strings (ours); (5) the credit line in `Community-content/CREDITS-and-sources.txt`
before anything is pushed; (6) the owner lands, walks Bilbousa, reports: swamp water colour, whether the Dathomir sky reads
as Nal Hutta, floating or buried buildings on the 80 m shelf, the four towers, lamp density at night, and the height of the
flora over the walkways. Open: whether MTG's `nalhutta.iff` environment or `hutta.iff` is the one Darklight meant (two sky
files exist), and whether any `hutta_*` string file exists in MTG's server package (not in the client).

## Owner questions

1. Species id `0xEA` (Fable convention) or `31` (the NPC Hutt row)? Claude decides unless you object.
2. Chairs: refuse for Hutts until Level 3, or allow the clip?
3. Huttese as a starting language if the skill rows exist?
4. The floater as the launch vehicle: given free at creation, sold by a Hutt vendor, or crafted (Artisan schematic)?
5. Nal Hutta first look: after the Hutt launch check, or in the same test-galaxy restart?
