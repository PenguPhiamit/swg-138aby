# Vehicles that draw and vehicles that don't, 17 Oct

Claude, 17 Oct, after run 29. Owner, about 12:40 PM: "light bendning barc has no model i can see its name so its there,
i cant use or see the model". Earlier: "the speeders textures are gone and are uncallable" (two speeders).
Checked against the installed archive `beb06d28`, the client archives, and Core3-dev `a48e1d7d` (read-only). Nothing
installed.

## How a vehicle's body is drawn

The object template's `appearanceFilename` (`pv_*.sat`) is an 8-vertex skeletal dummy, for stock vehicles too (the
X31's `pv_landspeeder_luke.mgn` has 8 vertices, and so does the floater's). The visible body is the **saddle
appearance**:

`.sat` → `datatables/mount/logical_saddle_name_map` → `saddle_appearance_map` → `*.apt` → `lod/*.lod` → `mesh/*_lN.msh`
→ `shader/*.sht` → `effect/*.eft` and `texture/*.dds`.

The floater proves it. Its `.sat` is the dummy, and the owner saw its whole body, which is `a1_deluxe_floater.apt`
(floater README section 2). A few MTG vehicles (podracers, walkers, droids) use a full-mesh `.sat` as their own saddle.

For every vehicle, the full chain was resolved file by file, and the archive each file comes from was recorded. **All
chains are complete**, so no file is missing.

## Why the Light Bending BARC is invisible

Every shader of its body is `lb_barc_combined_med_2d10.sht` or `..._sm_2d10.sht` (all three LODs). Both use
`effect\2d_distort.eft` (mtg_patch_011), a screen-distortion "cloak" effect from MTG's later-client files. It is the
**only** effect no other vehicle uses. The light-bending podracer (`lb_gasgano_pod_racer_*_2d10.sht`) is the only other
user. Our pre-CU client draws nothing visible with it, which matches "I can see its name, can't see the model". Every
other MTG-only effect a vehicle uses is `a_envmask_specmap_cbmp.eft`. It has the same five implementations as stock
effects (ps20, ps20 without dot3, ps11 and two fixed-function), so it should fall back cleanly.

## Every vehicle, sorted

Renders, verified in game:

- X31 and X34 (Luke's landspeeder body), speeder bike, swoop: stock, owner-tested before today.
- **A1 Deluxe Floater**: owner, 16 Oct 10:35 PM ("the floater was fixed").

Should render (complete chain, effects with stock-style fallbacks; not seen in game):

- Stock: AV-21, Flash speeder, jetpack.
- MTG:
  - Speeders and swoops: BARC (regular, Imperial, Rebel), AB-1, desert skiff, lava skiff, Organa, Tantive IV, USV-5, V-35, AIR-2 swoop, Flare-S swoop (and crafted), Geonosian, STAP (and gift), Koro-2, hoverlifter (and crafted), swamp speeder body, Sith speeder, snowspeeder, XJ-6.
  - Podracers: FG 8T8, Balta, IPG longtail, Gasgano (`pod_racer_one`), Mawhonic (`pod_racer_two`), Anakin.
  - Chairs and pods: hover chair, mechno chair, senate pod.
  - Walkers and droids: AT-RT camo and `temp_walker1`, AT-PT (`tcg_at_pt_walker`), basilisk war droid, Mustafar panning droid.
  - Others: RIC-920, single-pod airspeeder, Republic gunship, military transport, HK-47 jetpack, Grievous wheel bike.
- Of these, the hover chair, mechno chair, RIC-920, single-pod airspeeder, gunship and XJ-6 use `a_envmask_specmap_cbmp`.

Does not render, or cannot be created:

| Vehicle | Why | Reachable how |
|---|---|---|
| Light Bending BARC | body is all `2d_distort` | builder deed: **fixed by the archive below** |
| Light-bending podracer | body is all `2d_distort`, and it has no saddle row | builder deed |
| XP-38 landspeeder | stock placeholder `monstrosity.sat` (22 vertices), no saddle row | builder deed, **Hoth loot** |
| `vehicle_atat`, `vehicle_atpt`, `vehicle_atrt`, `vehicle_atst`, `vehicle_atxt` | the server's mobiles have **no client template file** in any archive, so the client cannot create them | builder deeds |
| `swoopracer_black`, `_blue`, `_gold`, `_green`, `_purple`, `_red`, `_silver` | the same: no client template file (only the CRC table names them) | builder deeds |

Deeds that do nothing: the server deed template is an empty stub with no `templateType`, no PCD and no vehicle:

- `swamp_speeder_deed` and `vehicle_deed_mechno_chair`. **Both are Hoth loot rewards.**
- `pod_racer_one_deed`, `pod_racer_two_deed`, `walker_at_xt`, `walker_at_rt_reg`, `tcg_at_pt_walker`.
- `vehicular_prototype_deed`, `vehicular_prototype_bike_deed`.
- `instant_travel_terminal_royal_ship_deed`, `instant_travel_terminal_snowspeeder`.

These are the likely "uncallable" speeders.

Client templates with no saddle row are not drawn as rideable, but no server deed produces them: `hoth_at_st`,
`walker_at_st`, `walker_at_xt(_player)`, `landspeeder_tantive4_adv`, `landspeeder_usv5_s02`,
`tcg_merr_sonn_jt12_jetpack`, `walker_at_rt_reg` (its `.sat` is missing too).

## Fixes

**1. Archive (staged): the Light Bending BARC uses the regular BARC body.** `tools/build_vehicle_fixes.py` changes one
row of `logical_saddle_name_map`: `appearance/light_bending_barc_speeder.sat` now points to `lookup/clone_barc_speeder`
instead of `lookup/barc_speeder_light_bend`. That gives it `clone_barc_speeder.apt`, `clientdata/vehicle/barc_speeder.iff`
and rider pose `vehicle_barc_speeder`, all of which exist and are checked. Its scale row is unchanged. The name, deed,
PCD and server templates are untouched.

| | |
|---|---|
| Archive | `work/vehicle-fixes/local_planets-vehicle-fixes.tre` |
| **sha256** | **`a58f732ad4e39d27ee741f7028de0aab170138e2161102df58a827f4c890984a`** |
| Base | `beb06d28108ace018468de351420412705dcdcbad0a7d55a64258a7f3b871afa` (`work/ossus-cave-mouths/local_planets-cave-mouths.tre`) |
| Changed | `datatables/mount/logical_saddle_name_map.iff` only (one row). The other 336 entries are byte-identical |

Install it on client and server like the other archive steps. Owner check: call the Light Bending BARC. Does it show a
BARC body, can you mount it, does it drive?

**2. Core3-dev patch (staged): take the 25 deeds that cannot work out of the character builder.**
`Documentation-support/vehicles-render-17oct-catalog.patch` edits the "Vehicle Deed" group of
`bin/scripts/object/sandbox/mtg_catalog.lua`. It removes the light-bending podracer, the XP-38, the five `vehicle_at*`,
the seven swoop racers and the eleven empty stub deeds. The Light Bending BARC stays because fix 1 repairs it, and 28
deeds remain. It passes `git apply --check` on Core3-dev `a48e1d7d` (run read-only as swgemu). Line endings are kept.
Not run through `check_lua.py`; the edit only drops pairs and moves the group's closing `}}`.

**3. Needs the owner's choice: Hoth loot.** Three of the 17 Hoth vehicle rewards are broken: XP-38 (placeholder), swamp
speeder and mechno chair (empty deeds). The options:

- (a) Swap them for working deeds, such as the stock X34, speeder bike and swoop, or MTG ones from the "should render" list.
- (b) Fill the two stubs. This needs mobile, PCD and deed templates, as C54 did for the floater (client templates `shared_swamp_speeder.iff` and `shared_mechno_chair.iff` exist).
- (c) Drop them from the loot table.

The rest (the five walkers and seven swoop racers) could only come back with new client templates. That is content
work for later, not a fix.
