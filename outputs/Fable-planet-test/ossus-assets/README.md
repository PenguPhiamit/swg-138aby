# Ossus asset plan

14 Oct 2026, Fable. Research only: nothing downloaded, bought, installed or contacted. Every store and creator page was read on 14 Oct; the clauses that matter are quoted in `assets.json` (`licences`) and summarised below. Wookieepedia text was paraphrased, no images taken. Written only into this folder.

**Short version.** A first playable Ossus needs no new art and costs nothing: the owner's own client already holds temperate ground shaders, forests, rocks, the Dantooine ruined Jedi temple pieces, two Yavin IV Jedi-enclave interiors, caves, an outpost starport, Imperial outposts, the Dantari tribal camps and bodies (an exact stand-in for the Ysanna), creature bodies for every native animal in the lore, a two-sun sky file and forest/grassland loops. A second pass can add an Ossus-specific look from CC0 sources (Poly Haven and ambientCG ground textures, two OpenGameArt ambience loops, Quaternius' modular ruins) once the Blender→SWG mesh path is validated. The only cheap paid pack worth considering (Arludus, $14) has a redistribution clause that needs the author's written OK first. Store assets from Fab, CGTrader and the old Sketchfab store are ruled out by their extractability clauses, since SWG archives are openly extractable.

## 1. What Ossus needs and where it comes from

Stock file names are the actual paths in the client archives (checked against the load order with our TRE reader). Full lists per need are in `assets.json` → `needs`.

| Need | Stock SWG (owned, referenced in place) | MTG (credit MTG + contributors) | Open / paid candidates |
|---|---|---|---|
| Terrain shaders: hills, forest floor, gorges, rock, scorched crater, water | `grss_long_darkgreen`, `grss_dant_*`, `frst_fallenleaves`, `frst_dirtwtwigs`, `dirt_mossydirt`, `rock_cliffbrwngray`, `rock_endr_selmamountains`, `rock_mtns_whitelimestone`, `dirt_scorched_*`, `rock_scorched_limestone`, `wter_dant_lake` (76 grass, 75 forest, 359 rock, 125 dirt, 28 water shaders in stock) | – | C1 Poly Haven, C2 ambientCG (CC0) |
| Flora | `decd_blba_tree` (kingwood stand-in), `decd_whitebirch*`, `ever_pinetree_*`, `conf_mtns_pine_*`, `leaf_bamboo_*`/`leaf_bamboogrove` (the lore's bambwood), `shrb_leafbush_*`, `fern_*`, radials `radl_dant_grassflowers`, `radl_darkfrstgrass` | 112 Kashyyyk/Mustafar trees | C3 Kenney Nature Kit, C4 KayKit Forest, C5 Quaternius Nature (all stylized; weak fit) |
| Rocks and cliffs | `rock_dant*`, `rock_graniteslab_*`, `rock_weatheredmossy_*`, `mtns_rock_grey*`, `rock_crystl_arch_*` (crystal caves) | – | C9 Kenney Cave Kit |
| Ruins: Library/Temple remains, the 137 ABY crater, hidden-Jedi dwellings | `thm_dant_jedi_temple_altar/pillar(_base,_fallen,_med,_sm)`, `poi_temple_ancient_ruined`, Gungan ruined walls and pillars, Tatooine ruined pillars, `poi_all_obelisk_s01`, interiors `thm_yavn_jedi_enclave_light/dark.pob`, the Yavin temple `.pob`s, scorched Massassi trees, Death Star wreckage and cargo debris props, caves `shared_cave_01..08` | `must_jeditemple_dome/platform/wall_*` (Trials of Obi-Wan Jedi temple ruins), `exarkun_pillar`, `aurilia_obelisk` | C6 Quaternius Modular Ruins, C7 OGA Modular Temple, C8 Kenney Graveyard; paid C15 Arludus; excluded C14, C16–C18 |
| Knossa spaceport | `shared_outpost_starport.iff` → `mun_all_landing_pad_s01.pob` (spawns its own terminals, proven on Hoth); `shared_starport_general*` | – | none needed |
| Ysanna settlement and looks | Dantari camps `shared_dantooine_janta_*`/`kunga_*`, Dantari caves, tents `eqp_camping_tent_s1..s6`, `poi_all_tent_hut_s01`; bodies `shared_dantari_male/female`; `shared_singing_mountain_clan_mask_s01`, Tusken bandoliers and helmet, Nightsister hats; mounts `shared_bol`, `shared_brackaset` | `item_mask_*` | C10 Kenney Survival Kit, C11 OGA Tribal Hut (CC-BY) |
| Native creatures | gokob → womp rat/vrelt/kima; tribis → `shared_tybis`; kaddyr bug → kliknik; kirruk → gurreck/huf dun; tree frog → vir vur or none; mount → bol; all with `_hue` recolours | 3,032 MTG mobiles | none (no rig path) |
| Imperial watch post | `shared_military_imperial_forward_outpost`, `_outpost_guard_house_imperial`, `_outpost_guard_tower_1`, `shared_poi_all_impl_bunker_recon_outpost`, Imperial walls/gates; stormtrooper looks | – | none needed |
| Sky and sound | `terrain/environment/tatooine.iff` as template (it carries a second-sun `SSUN` chunk; Ossus has two suns) with `grad_sky_dantooine.dds`; `amb_forest_outside/night`, `amb_grassland_outside`, `amb_mountains_outside`, `amb_cave_*`; `mus_theme_generic_a/b/c` | MTG themes | C12, C13 OGA CC0 loops |

Two stock caveats: `shared_poi_all_jedi_temple_ruined.iff` exists but its `poi_all_jedi_temple_ruined.pob` is in none of the archives the client loads, so it is unusable; and the disc's `patch_18+`/later `sku` archives are TRE version 6 with an all-zero header, which neither our reader nor Core3's version-6 branch can index, so the owner's own Trials of Obi-Wan copies of the Mustafar temple ruins are not readable today (MTG carries the same files).

## 2. Open and cheap candidates (details and licence quotes in `assets.json`)

| Id | Candidate | Licence (checked on the page) | Client-archive redistribution | Price | Format / size | Fit for SWG |
|---|---|---|---|---|---|---|
| C1 | Poly Haven ground/rock textures (forest_floor, forrest_ground_01, forest_leaves_02, brown_mud_leaves_01, aerial_grass_rock, aerial_rocks_02, mossy_rock, lichen_rock, rock_01/04/05, grass_path_2, gravel_ground_01, coast_sand_rocks_02) | CC0 1.0 (polyhaven.com/license) | yes | free | PNG/JPG 1K–8K | good: photographic tiles like SWG's |
| C2 | ambientCG (Grass001/004/005, Ground037 forest moss, Ground020 leaves, Ground030 path, Rock063/064 mossy cliff, Rock051/058/060 cliff, Rock035 cave) | CC0 1.0 (docs.ambientcg.com/license allows raw files in games) | yes | free | PBR 1K–8K | good |
| C3 | Kenney Nature Kit (330 files) | CC0 | yes | free | formats not listed on page (Kenney ships FBX/OBJ/glTF) | weak: flat palette look |
| C4 | KayKit Forest Nature Pack | CC0 stated on page | yes | free tier $0 (100+ models), Extra $9.99 | FBX/glTF/OBJ, 1024 atlas | weak–medium |
| C5 | Quaternius Ultimate Nature Pack (150 models) | pack page links CC0; site licence page now says QAL v1.0 (no attribution, finished games OK, "may not extract, repackage ... redistribute the Assets") | finished-game distribution allowed; clarify if archives are shared | free | FBX/OBJ/Blend, untextured | weak |
| C6 | Quaternius Ultimate Modular Ruins (90 models, textured) | as C5 | as C5 | free | FBX/OBJ/Blend | medium–good for ruin props |
| C7 | OGA Modular Temple (Fertile Soil Productions; itch version 213 OBJ) | CC0 | yes | free | OBJ + mtl, untextured | medium: ornate, not ruined |
| C8 | Kenney Graveyard Kit (90 files) | CC0 | yes | free | zip | weak–medium |
| C9 | Kenney Modular Cave Kit (40 files, 2026) | CC0 | yes | free | zip | props only; SWG caves are `.pob` interiors |
| C10 | Kenney Survival Kit (80 files) | CC0 | yes | free | zip | medium camp props |
| C11 | OGA Low-Poly Tribal Hut (NoLogoGames) | CC-BY 3.0 (credit "would be polite" for games; required in paid packs) | yes with credit | free | FBX, 512 px PBR | good, one hut |
| C12 | OGA Forest Ambience (TinyWorlds) | CC0 | yes | free | mp3 loop, 717 KB | good |
| C13 | OGA Birds and Wind (Spring Spring; bird recordings public domain) | CC0 | yes | free | mp3 mixes, ~1.9 MB | good (plain mix) |
| C14 | SrushtiLabs "100+ Ancient South Indian Temple Ruins" (Fab, free) | description says CC0, Fab's licence field says Standard License, Fab flags "Generated with AI: Yes" | unclear | free | glb, 730 MB | **excluded** (AI provenance, licence conflict) |
| C15 | Arludus Low Poly Temple Ruins Pack Modular (86 FBX, ~200 tris each, 6 atlas textures) | creator's terms: "not CC0", games and commercial use allowed, "Redistribution or resale of the files (even modified) is not allowed" | **needs the author's written OK** | $14 itch / $12 Unity | FBX, 864 KB | very good (low poly, dated, readable) |
| C16 | ART Ancient Ruin Temple (Fab) | Fab Standard | no | $49.99–59.99 | 99 FBX, Nanite high poly | poor |
| C17 | Ancient Temple Modular Asset Kit (Fab) | Fab Standard | no | $12.99–15.99 | Unreal package only | not practical |
| C18 | Shapefarm Ancient Temple Ruins (Epic promo, ended 13 Jan 2026) | Fab Standard | no | n/a | UE 5.2+ package | not practical |
| C19 | Sketchfab free CC downloads | per model (CC0/BY; flag SA, exclude NC) | per licence | free | varies | varies; none selected yet |

Store EULAs, in one line each (quotes in `assets.json`): **Fab Standard**: any tool, modify, no credit, but a distributed project must keep content "in object code" and "restrict end users from extracting", and no stand-alone redistribution; SWG archives are extractable, so paid Fab content is out. **Unity Asset Store**: distribute only "as incorporated and embedded"; no extractability clause but no clear yes either. **CGTrader Royalty Free**: games only "inside a proprietary format" with "commercially reasonable measures to prevent the end user from gaining access": out. **Sketchfab store** (legacy): no "stand-alone file ... or in a way that allows third parties to ... extract": out. **ArtStation Marketplace**: use and modify in "computer games"; stand-alone clause not captured, check per product. **itch.io**: per creator. CC0 is the only licence that answers every question with yes; CC-BY needs the credit line; CC-BY-SA is flagged; NC is excluded.

The C15 catalogue (ChatGPT) already covers Poly Haven snow, Quaternius/Kenney sci-fi kits, Kenney sounds and particles, cgbookcase and the ambientCG/ShareTextures gates; nothing above repeats those entries except the two sites as sources.

## 3. Conversion path and what our tools can do today

- **Ground textures (C1, C2):** colour map → 512 or 1024 px, light AO bake → DXT1 DDS `texture/<name>.dds` → clone a stock `.sht` (a 285-byte IFF whose `NAME` chunk holds `texture\<name>.dds`; stock terrain shaders use `effect/a_simple.eft`, one texture, no normal map) → new `SFAM` family in our `.trn`. Our IFF tool does the `.sht` and `.trn` parts now; DDS compression needs NVIDIA Texture Tools or texconv (install = owner's OK) or an uncompressed-DDS writer of our own.
- **Audio (C12, C13):** mp3 → mono WAV `sample/amb_ossus_*_lp.wav` → cloned `.snd` (stock `amb_forest_outside.snd` is a 161-byte `SD2D` template naming `sample/amb_forest_lp.wav`) → region ambient hookup. All within our tools except the WAV conversion.
- **Static props (C6, C7, C10, C11, C15):** FBX/OBJ → Blender → io_scene_swg_msh (MIT; MSH/LOD/POB/MGN/SKT import/export, generates `.apt`; Blender 2.9/3.x; no animation, SKT export unreliable, collision stored but not editable) → `.msh` + `.lod` + `.apt`, textures to DDS, `.sht` per material. **Not validated by us yet** (feature register F86): the first external prop is a validation task, done once, before any content depends on it.
- **Creatures:** no path for new rigged, animated bodies; stock bodies with our names (the owner's encounter policy allows original replacements).
- **Interiors:** a CC0 cave or ruin mesh is not a walkable SWG building; `.pob` cells, portals and floors are a separate, high-effort job. Use stock `.pob` interiors.

## 4. Recommended set

**First playable Ossus: stock only, $0, no downloads.** Terrain shader families, flora, rocks, Dantooine temple pieces, `poi_temple_ancient_ruined`, Gungan ruined walls, Yavin enclave interiors for the hidden temple, scorched shaders plus debris for the crater, stock caves, `shared_outpost_starport` for Knossa, Dantari camps/caves/bodies with the SMC mask and Tusken bandoliers for the Ysanna, bol mounts, stock creature bodies renamed, the Imperial forward outpost and guard tower, Tatooine's two-sun environment file with Dantooine's sky, stock loops and a generic theme. Rights basis: the same as Hoth (stock art referenced in place in the owner's own client, never copied out). Optional MTG Mustafar temple walls for a larger ruin field, with the MTG credit.

**Second pass (owner's OK per download):** C1 (about 8 textures, 1–3 MB each) and C2 (4–6 materials) for an Ossus-specific ground look; C12 and C13 loops (about 3 MB); C6 Quaternius ruins as the first external prop after the F86 validation; C10/C9 only if camp or cave variety is wanted. Record each zip's source, hash, licence text and credit line at download, as AGENTS.md requires.

**Paid:** nothing required. C15 ($14) only if the author confirms in writing that converted files may ship inside our client archive; that message is outbound and needs the owner's OK. Everything else paid is excluded by the extractability clauses or format.

**Total: $0 recommended, $14 optional.**

## 5. What needs the owner

1. OK for each download in the second pass (sizes above; saved outside the client, hashed, recorded).
2. Whether to ask Arludus about C15 (outbound message, then $14).
3. Confirm the Blender add-on validation task (F86) before any external 3D prop; until then only textures and audio are importable.
4. Allow a DDS tool install (NVIDIA Texture Tools or texconv), or accept uncompressed DDS from our own writer.
5. Accept stock bodies for the native creatures.
6. Whether MTG's Mustafar Jedi-temple ruins (SOE Trials of Obi-Wan art, MTG credit) may be used, given that the owner's own disc copies sit in unreadable version-6 archives.

## Files

`README.md`, `assets.json` (needs, candidates, licences, recommended set, owner actions), `tools/disc_tre_headers.sh` (lists the disc archives and their TRE versions), `tools/tre_v6_probe.py` (the version-6 index probe; it found all-zero headers).
