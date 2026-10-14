# Species, batch S1-S3: provenance, the end-to-end map, and a staged first species (Chiss)

Fable, 14 Oct 2026. Roadmap Phase 4 ("port the original public species package first; Zeltron next"), feature
register F50/F51/F55, catalogue rows active-054..056. Read-only on the packages (zip members read as text or bytes in
memory, nothing extracted or run), on Core3-dev and on the owner's client. Owner rule kept: no hybrid species until
all the regular ones are in; neither package contains a hybrid, so nothing is deferred yet by that rule.

Contents: `provenance.json` (S1, by `tools/provenance.py`), this README (S2), `s3/` (the Chiss stage: staged Lua
with the self-tested applier, `tables/` with the rows and IFF fragments for the archive builder), `checks.json`.

## S1. What was downloaded, and what each piece may be used for

| Package | Bytes / sha256 | What it is | Terms found | Decision |
|---|---|---|---|---|
| `Content-catalogue/newspecies-original.zip` | 3.93 MB, `59b48293…6472` | Halyn's "New species for SWGEmu" (with Phoenix), Core3 beta 0.5 era (2016): `species/` = 3 C++ (Races.h, PlayerCreationManager.cpp, ImageDesignManager.cpp) + 45 Lua (20 player race templates, objects/serverobjects, base), and `species.tre` (EERT5000, 117 files, sha256 `b781cff1d78a…`) | no readme or licence inside; every source file carries the SWGEmu Core3 header (LGPL text, "see COPYING"; Core3 itself is AGPL-3.0); catalogue status **P, published for server use**, author asks permission for uses outside the species-mod purpose | **usable** for exactly this purpose, with credit to Halyn and Phoenix (and MTG as host) |
| `species.tre` inside it | 117 entries | 20 `object/creature/player/shared_*.iff`, custom art for Gotal (32 files) and Nautolan (42: .sat/.lmg/.mgn/.dds/.sht/.pal), and 2016 copies of 25 stock tables with the species added (creation, customization, strings, CRC table, `ui_avatardata.inc`) | as above | art and templates **usable** (the owner's client already has all 117 through MTG patch 023; 28 of them are shadowed by newer stock patches); tables **usable as rows only**, re-emitted on today's stock schema (column types differ: `i` vs `I`, `f[0]` vs `f[0.0]`, `i[256]` vs `I[10000]`); `player_species.stf` descriptions **excluded** (Wookieepedia text, CC BY-SA; we write our own; the names are fine); its CRC table excluded (the merged one already has the 20 entries) |
| `Content-catalogue/zeltros_client.zip`, `zeltros_server.zip` | 870 KB `d2d221…52cb`, 13.5 KB `ac6c30…860f` | the **Zeltros planet** (tienvogh): terrain, snapshot, buildings, region Lua; CC-BY-NC | not a species package | **excluded from this track**: Zeltros (planet) is not Zeltron (species). No Zeltron package was downloaded; Zeltron exists only in EiF's client (`EiF-starsider01-reference.tre`: 12 files, two player templates) under the unresolved F51 terms, so Zeltron is **held** |
| `EiF-Uprising/EiF-2017-species-source-reference.zip` (`acb60d…`), `EiF-starsider01-reference.tre` (`55dad9…`, 9,771 entries) | | EiF's 2017 source snapshot (player Lua + licence texts) and client reference | source: AGPL repository; client art: no reuse grant (F51) | **held**, reference only (which species exist, how Races.h was extended to 66 entries) |
| `mtg_patch_023.tre` in the owner's client (`30482e…`, 181 entries) | | MTG's compilation of the species package | MTG, catalogue status P with credit | **usable in place**; it is how the client already holds the files |

Package defects to design around (JSON `defects_seen`): `racial_mods.iff` lists Aqualish and Bith twice; `Races.h`
gives Aqualish, Bith, Gotal and Talz species id 0 (human); there are no `skills.iff` rows for any `species_<new>`
(only `skl_n/skl_d` names, and none for Hutt), so the species skill, and with it the starting certifications, would
silently not be granted; the Chiss hair list names `hair_human_female_s33`, absent from the client and dev; the Chiss
description claims +250/+250/+300 attributes while its `racial_mods` row is all 100.

Hybrids: none in either package (Nightsister and the Singing Mountain Clan witch are human character options); EiF
has none either. The rule applies when one is proposed.

## S2. What a playable species needs, end to end (pre-CU client + Core3-dev)

"Package" = the species package; "stock" = the owner's stock client / Core3-dev; "MTG" = patch 023 in the client.

| Piece | Where it lives | Package | Stock | Status for the 16 |
|---|---|---|---|---|
| Species list and creation UI | `ui/ui_avatardata.inc` (text; one `<Data appearancemale= appearancefemale= Name= skill= description= displayname=…/>` per species) | 2016 copy with 39 templates | 20 templates (patch_11_01 wins) | **missing in effect**: splice the new `<Data>` blocks into today's stock copy for `local_planets.tre` |
| Species names and descriptions | `string/en/player_species.stf` (`name_<x>`, `desc_<x>`) | 52 keys (16 new names + 16 descriptions) | 20 keys | names usable; descriptions must be ours |
| Player client templates | `object/creature/player/shared_<species>_<gender>.iff` | 20 | MTG patch 023 has all 20 (client) | present; all 20 in the merged CRC table |
| Appearance | `.sat` (+ `.lmg/.mgn` meshes, `.dds`, `.sht`) named by the template; all 20 templates use the **human player skeleton** (`clientdata/player/client_shared_player_human_m/f.cdf`) | custom art only for Gotal and Nautolan | the other 18 use stock NPC appearances (`chiss_m.sat`, `bith_f.sat`, `hutt_m.sat`… in `data_other_00.tre`; `gotal_m`, `nautolan_m`, `togruta_f` in patch 11) | present. Because every template rides the human skeleton, stock human clothing and animations fit; the Hutt looks like a Hutt on a human rig (owner question 3) |
| Customization sliders, palettes, image design | `datatables/customization/customization_data.iff` (42 rows for chiss_male, 148 for the 16), `customization_group_instance.iff`, `palette_columns.iff`, `allow_bald.iff`, `hair_assets_skill_mods.iff`; `customization/asset_customization_manager.iff` | 2016 copies with rows added | stock (patch 9/11/12) wins | **missing in effect**: rows to re-emit onto today's tables. `asset_customization_manager.iff` (ACST, 386 KB vs 341 KB) needs a byte-level diff before use (owner/Claude builder question 4). Server side reads the same `customization_data.iff` (`ImageDesignManager.cpp:334`, keyed by `object/creature/player/<species_gender>.iff`), no C++ change |
| Hair | `creation/default_pc_hairstyles.iff` (HAIR/PTMP per species; Chiss lists 40 + 39 stock human hairs), hair objects `object/tangible/hair/human/*` | 2016 copy with 20 blocks | stock 10 blocks; hair objects stock (server templates in dev) | **missing in effect**: splice the PTMP blocks; drop `s33` |
| Default clothing per profession | `creation/default_pc_equipment.iff` (LOEQ), `creation/profession_defaults_<profession>.iff` (PRFI ×7) | 2016 copies with blocks per species (22 stock wearables for Chiss, all in dev and in the merged CRC table) | stock | **missing in effect**: splice the blocks |
| Attributes | `datatables/creation/racial_mods.iff`, `attribute_limits.iff` (server reads both too: `PlayerCreationManager.cpp:57-110`, keyed by template name, human fallback) | rows for 16 (+ duplicates) | 10 rows | **missing in effect**: add rows on today's schema; put the same numbers in the race template's `baseHAM` |
| Species skill | `datatables/skill/skills.iff` row `species_<x>` (certs, innate mods), names in `skl_n.stf`/`skl_d.stf` (server loads skills.iff from the tre: `SkillManager.cpp:70`) | **none** (names only) | 10 stock rows | **missing**: clone `species_human` (`s3/tables/chiss-rows.json` -> `skills_row`) and add names; without it `awardSkill` returns false silently |
| Race templates (server) | `object/creature/player/<species>_<gender>.lua` + shared declarations in `objects.lua` + includes | 20 (2016 shape: `zoneComponent`) | 20 stock | re-written in dev's shape (ground/space zone components): `s3/` for Chiss |
| Race tables (C++) | `src/server/zone/objects/player/Races.h`: `Species`, `TemplateSpecies`, `Gender`, `RaceStrs`, `CCRaceStrs`, `SharedRace` (SOE CRC of the shared template, checked: human = 0xAF1DC1A1) + the hard-coded `20` bounds in `getRaceID/getSpeciesID/getCompleteRace`; `CreatureObject.idl` species constants (`getSpeciesName`), `ClientRandomNameRequest.h` (name species by race file), `NameManager.cpp` (human fallback), `DirectorManager.cpp:655` (`SPECIES_*` Lua constants), `managers/creature_manager.lua` `aiSpeciesData` (stock ids: aqualish 9, bith 12, devaronian 17, gotal 27, gran 28, hutt 31, ishi_tib 32, nikto 42, quarren 46, talz 50, weequay 55) | 40-entry Races.h (2016) | 20 entries | **C++ needed**: without it `Races::getRaceID` returns 0 and a Chiss is created as race 0 / species human (works, misreports). Model: EiF's 66-entry header |
| Wearable restrictions | `playerRaces` lists in 703 wearable templates (`object/tangible/wearables/**`, `SharedTangibleObjectTemplate.lua:81`), checked by `PlayerContainerComponent.cpp:31` and `CreatureManagerImplementation.cpp:1300` | not touched | stock lists name the 20 stock race files | **missing**: a new race file must be added to every wearable's `playerRaces`, or the player cannot equip clothing. One generated patch (sed-style) over 703 files, or a C++ "human-rig species wear human clothes" rule (owner question 5) |
| Species CRC entries | `misc/object_template_crc_string_table.iff` | 2016 table | merged table in `local_planets.tre` | present (all 20 + the hair/clothing they use) |
| Random names | `managers/name/species/*.lua`, `NameManager.cpp` switch | none | 10 | falls back to human names (acceptable; owner question 6) |
| Species language | `social_language_<x>_*` skills | none | per stock species | Basic only (as the package) |
| Account restriction | `datatables/creation/species_account_features_restrictions.iff` (Ithorian/Sullustan need feature 16) | none | stock | no entry needed for new species (unlisted = allowed) |

## S3. Staged plan for the first species: Chiss (male and female)

Why Chiss first: both genders, stock appearance already in the pre-CU client (`chiss_m/f.sat`, `data_other_00`),
human rig, no custom art, no palette work (`npc_chiss_eyes` row supplied). Nautolan/Togruta/Hutt (the owner's
active-054..056) come next; they add the package's custom art (Nautolan, Gotal) or the Hutt-on-a-human-rig look.

**Client, into `local_planets.tre` by the archive builder** (all rows/fragments in `s3/tables/`, extracted from the
package in memory; every referenced hair and wearable exists in dev and in the merged CRC table except
`hair_human_female_s33`, to drop):
1. `ui/ui_avatardata.inc`: insert `tables/ui_avatardata.chiss.inc.txt` after the stock zabrak `<Data>` block.
2. `string/en/player_species.stf`: add `name_chiss` = "Chiss", `desc_chiss` = our own text (draft: "A near-human
   people of the Unknown Regions, blue-skinned and red-eyed, disciplined and reserved; few are seen this far into the
   galaxy." plus the attribute block in the stock format).
3. `datatables/creation/racial_mods.iff` and `attribute_limits.iff`: the `chiss_male/chiss_female` rows (JSON).
4. `datatables/customization/customization_data.iff` (42 rows), `customization_group_instance.iff` (10),
   `hair_assets_skill_mods.iff` (79, minus s33), `palette_columns.iff` (2: `npc_chiss_eyes`), `allow_bald.iff` (2).
5. `creation/default_pc_hairstyles.iff`, `default_pc_equipment.iff`, `profession_defaults_*.iff` (6 of 7; jedi has no
   per-species block): the Chiss PTMP forms in `tables/*.chiss1/2.ptmp`, appended to today's stock copies.
6. `datatables/skill/skills.iff`: the `species_chiss` row (clone of `species_human`, `SPECIES_REQUIRED = chiss`);
   `skl_n.stf` "Chiss Special Features", `skl_d.stf` "Chiss Abilities" (our own wording).
7. `customization/asset_customization_manager.iff`: to be diffed first (owner/builder question 4).

**Core3-dev, Lua (staged, `s3/apply.sh`; self-test PASSED, dry run 2 copies + 3 patches, 0 refused, luac ok,
names free):** `object/creature/player/chiss_male.lua`, `chiss_female.lua` (dev shape, `baseHAM` all 100,
`startingSkills` species_chiss + Basic), the two shared declarations appended to `objects.lua`, two includes after
the zabrak_male line in `serverobjects.lua`. Loading them is harmless: nothing references the templates until the
client offers Chiss. Not staged: the 703 `playerRaces` lists (wait for owner question 5).

**Core3-dev, C++ (listed, not staged):** `Races.h` +2 entries in all six arrays (SharedRace CRCs 0x02F60EAC male,
0x614A1B68 female, computed and equal to the package's) and the bounds 20 -> N; `CreatureObject.idl` CHISS = 52
(0x34, as the package) in the species constants and `getSpeciesName`; optional: `ClientRandomNameRequest.h` and
`NameManager` (Chiss names), `DirectorManager` `SPECIES_CHISS`.

**Offline checks done:** package member hashes; every client file the package carries located in the owner's
archives (117/117, 89 via MTG patch 023, 28 shadowed by stock); schema comparison of the 7 datatables; Chiss hair
and clothing references resolved in dev (99/100) and the merged CRC table; `species_*` rows absent from stock,
merged and MTG skills tables (confirmed); Lua luac; applier self-test. **Only the owner's client can show:** the
species in the creation list, the sliders and palettes on the Chiss, hair and default clothing, and whether the
stock NPC `chiss_m/f.sat` holds up as a player body (eyes, blends); then on the test galaxy: creation succeeds,
the species skill and certs are granted, clothing equips.

## Owner questions

1. First species Chiss (both genders, no art risk), then Nautolan and Togruta (package art), then Hutt? Or the
   active-054..056 order (Hutt, Nautolan, Togruta)?
2. "Zeltron next" in the roadmap: no Zeltron package exists; only EiF's art (F51, unresolved). Hold Zeltron until
   EiF terms are settled, or try a stock-art stand-in (a red-skinned human palette)?
3. Hutt as a playable: the package's Hutt stands on the human skeleton (`hutt_m.sat` on `client_shared_player_human_m`);
   acceptable look?
4. `asset_customization_manager.iff`: use the package's 2016 copy (386 KB) over today's stock (341 KB) or diff and
   splice only the new entries (Claude's builder, one more round)?
5. Clothing: patch `playerRaces` in all 703 wearable templates per new species (generated, mechanical), or a C++
   rule that human-skeleton species may wear human clothing?
6. Random names for new species: human names (fallback) or our own name tables?
7. Attribute mods: the package gives Chiss a flat 100 everywhere; keep, or set a profile (its own description
   suggests constitution/action/quickness)?
