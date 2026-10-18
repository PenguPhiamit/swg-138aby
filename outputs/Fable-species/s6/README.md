# Species S6: Nautolan (male) and Togruta (female) — Fable, 14 Oct 2026

Stage only; read-only on /opt/swg (dev HEAD 08e6a924, Chiss in; the eight dev files were read with `wsl cat`); the species
package and the client archives read in memory; nothing written outside `outputs/Fable-species/s6/`. Staged like Chiss
(S3–S5), on top of the C29 chain. **Verified** = checked offline here; **staged** = not yet built, run or seen.
**Held until the owner's Chiss check passes** (section 5).

| path | what |
|---|---|
| `local_planets-s6.tre` | the C29 chain (Hoth build > stage_ossus > chiss > ossus_minerals > lore) + `stage_s6`; **sha256 b0bfdcf984414f5c8dc346b731a5603aea3d2ae060047341bf38b6658e8b11cd**, 4,044,929 B, 56 entries |
| `build_test_archive.py` | the chain wrapper with the checks below → `checks.json`, `work/closure.json` |
| `tools/stage_s6.py` | `stage_s6(stage_dir, base)`: `species_tables.stage_species(['nautolan','togruta'])` + the two palette rows, two NAME-only hair blocks, our own creation-UI blocks |
| `tools/acst_togruta.py` | the Togruta customization map (no ACST table anywhere maps `appearance/togruta_f.sat`) |
| `tools/make_patch.py`, `patch/species-s6.patch`, `new-files.txt`, `work/gitcheck.sh` | the dev patch: 6 files edited, 2 new; `git apply --check` clean on the dev copies, luac ok on the five Lua files |
| `tools/make_provenance.py`, `provenance.json` | every file the two species rely on (128) with source, hash, rights basis, credit |

## 1. Provenance (first)

Neither species needs a file shipped that is not already in the owner's client. The closure of the two player templates
(128 files, `work/closure.json`) resolves as: **42 from MTG patch 023** = the Halyn/Phoenix package's files (the two
templates and the 40 Nautolan mesh/shader/texture files), **29 from other MTG patches** (Togruta meshes 016, shaders 018,
textures 015, the player skeleton data), **39 stock** (`appearance/nautolan_m.sat` and `togruta_f.sat` in patch_11_00, the
two skin palettes, the human face skeletons and lats, textures), **18 missing** = the stock human voice `.snd` files that
the stock human templates miss identically (the S5 gap; silent emotes at worst). Our archive adds **tables only** (19
changed entries + the ACST), rows re-emitted from the package as data, descriptions ours.

Rights, per `provenance.json`: stock and MTG files are the owner's client assets, the same basis as every other MTG file
the galaxy uses (catalogue status P with credit); the package files are published for server use (status P, credit
Halyn/Phoenix, hosted by MTG 023). **Flag, not a stop:** the package has no licence file and does not say whether its 40
Nautolan art files are Halyn's own work or converted SOE NPC art, so their authorship is recorded as *unstated*; we ship
none of them and reference them only by path (the client already loads them from MTG 023). No file's rights are unclear
in the sense of blocking the stage. A credit line for `Community-content/CREDITS-and-sources.txt` is in the JSON.

Both species are **on the human rig**: `clientdata/player/client_shared_player_human_m.cdf` (Nautolan) /
`_f.cdf` (Togruta), skeleton `appearance/skeleton/all_b.skt` + the human face skeleton. So the Chiss clothing rule
(`humanRigRaces`) applies and human clothing equips; nothing extra for wearables.

## 2. Client (verified offline)

The C29 rebuild inside the wrapper is byte-identical to `Fable-resources3/lore/local_planets-lore.tre` (fbf62971…), so S6
adds to exactly that. Of C29's 55 entries **36 are byte-identical**, **19 change** and **1 is new**, and for each the
check proves a strict superset: the old rows/blocks/keys/lines stay in order and every addition names nautolan or
togruta: `racial_mods` +2, `attribute_limits` +2 (the package's Zabrak-profile rows: 200/0/0/300/0/0/0/0/400),
`customization_data` +10, `customization_group_instance` +8, `allow_bald` +2, `palette_columns` +2 (`npc_skin_nautolan`,
`npc_togruta`: 4 columns, 36 of 64 entries at creation; added by stage_s6 because stage_species's name filter does not
catch them), `skills.iff` +2 (`species_nautolan`, `species_togruta` cloned from `species_human`), `player_species.stf` +4
(names from the package, descriptions ours), `skl_n`/`skl_d` +2 each, `default_pc_equipment` and six
`profession_defaults_*` +2 blocks each (the package's), `default_pc_hairstyles` +2 NAME-only blocks (as the stock Mon
Calamari and Wookiee blocks: no hair, both have head-tails), `ui/ui_avatardata.inc` +2 blocks (ours, the 15-attribute
stock shape; the package has no Togruta block and its Nautolan block lacked displayname/localdisplayname). **Chiss output
unchanged:** every Chiss row of C29 is present and identical (counts C29 = S6: racial_mods 1, attribute_limits 1,
allow_bald 2, customization_data 42, group_instance 10, palette_columns 2, skills 1), the Chiss `<Data>` block and strings
are kept, and every one of the 19,265 ACST appearances (Chiss included) resolves to the same variables as before.

ACST (`customization/asset_customization_manager.iff`, 341,713 B): two appearances spliced into today's stock table —
`appearance/nautolan_m.sat` from the package's 2016 table (blend_fat/muscle/skinny, index_color_0 white,
index_color_skin on `palette/npc_skin_nautolan.pal`), and `appearance/togruta_f.sat` from **our** map
(`tools/acst_togruta.py`: the four blend shapes the Togruta meshes carry — fat, flat_chest, muscle, skinny, read from
`togruta_f_body_l0.mgn` — and index_color_skin on `palette/npc_togruta.pal`, the one palette both Togruta shaders use).
Verification: stock appearances unchanged, spliced ones resolve as designed, tables sorted, index limits kept. Neither
head mesh has face blends (NPC heads), so no face sliders; the package's customization rows agree (body group only).
Both species are listed in the creation UI after Chiss.

## 3. Server (staged; `git apply --check` clean, luac ok)

`patch/species-s6.patch` (+97/−6) on dev HEAD 08e6a924: `Races.h` Nautolan male and Togruta female appended to all six
arrays after the Chiss rows (SharedRace CRCs 0xAB03ACB1 and 0x3D953B50, SOE CRC of the shared templates; `RACE_COUNT`
follows); `CreatureObject.idl` `NAUTOLAN = 0xE8`, `TOGRUTA = 0xE9` (next after Chiss's 0xE7) and `getSpeciesName()`;
`DirectorManager.cpp` `SPECIES_NAUTOLAN`, `SPECIES_TOGRUTA`; `player_creation_manager.lua` two `humanRigRaces` pairs
(nautolan_male → human_male, togruta_female → human_female); `objects.lua` the two shared declarations appended;
`serverobjects.lua` two includes after the Chiss ones; new `object/creature/player/nautolan_male.lua` and
`togruta_female.lua` in dev's chiss_*.lua shape with `baseHAM = { 200, 0, 0, 300, 0, 0, 0, 0, 400 }` (= the package's
racial_mods rows, the Zabrak profile, and what dev's zabrak_male.lua carries) and `startingSkills` species_<x> + Basic.
Build needs: idlc on the idl, `Races.h` recompiles the player/creature managers; the Lua needs none. Nothing in
`PlayerCreationManager.cpp` changes (the Chiss patch made the race map data-driven).

## 4. Owner check, one creation visit per species (after the Chiss check, the build and a restart)

**Nautolan (male only)**
1. Creation list shows **Nautolan**; pick it. The gender toggle should keep the same body (one template for both):
   report if it blanks the model.
2. Appearance: green skin palette (4 columns), body sliders (muscle, height, weight, chest); **no hair page** and **no
   face sliders** (expected: NPC head mesh). Head-tails visible; a grey/untextured body means a shader or texture did not
   load from MTG patch 023 → report which part (head, body, hands).
3. Finish as Marksman: default clothes on (shirt_s04/pants_s05/shoes_s01); skills window shows **Species: Nautolan**; HAM
   200/0/0/300/… plus profession mods (Zabrak profile).
4. Clothing: a human shirt and boots equip (the Chiss rule); a refusal → "Loaded 4 human-rig race mappings" missing from
   the server log.
5. Failure lines to report: client "character creation failed", server "Unknown player template selected" (objects.lua /
   serverobjects.lua) or "Could not create player with template" (creation tables).

**Togruta (female only)**
1. Creation list shows **Togruta**; pick it; same gender-toggle note.
2. Appearance: orange/red skin palette (4 columns), body sliders (muscle, height, weight, chest); no hair page, no face
   sliders; montrals and head-tails visible. A body with sliders doing nothing → the ACST splice did not load (first
   real splice we ship: report it first). The Togruta art is MTG 015/016/018 + stock, not the package.
3. Finish as Scout: default clothes on (dress_s06/shoes_s07); **Species: Togruta** in the skills window.
4. Clothing: a human dress or shirt equips; before the Chiss rule a Togruta could not wear it.
5. Same failure lines as above; plus any client log line naming `togruta_f.sat`.

## 5. Gate: what in S6 depends on the Chiss pipeline

Everything Chiss exercises for the first time: `stage_species` itself (rows, PTMP blocks, strings, skills), the
`ui_avatardata.inc` splice, the `humanRigRaces` loader and `canWearRace`, the `RACE_COUNT` bounds in `Races.h`, the
0xE7+ species ids, and the test launcher reading `local_planets.tre` on both sides. S6 adds **five firsts** that Chiss does
not test: the ACST splice actually shipped (Chiss needed none), our own customization map (Togruta), NAME-only hair
blocks for a hairless new species, the package's palette_columns rows, and a single-gender species (both appearance
attributes point at one template). If the Chiss check fails in creation, read S6 as blocked by the same cause; if Chiss
passes, S6's own risks are the five above, in that order.

## 6. Existing characters

None affected (checked by reading the patch): the six Races.h arrays only gain rows at the end; new constants; the
clothing rule only widens; every client table keeps its stock, Hoth, Ossus, lore and Chiss rows (the superset checks);
the ACST keeps every existing appearance's variables. No database or character record changes.
