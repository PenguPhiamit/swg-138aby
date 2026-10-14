# Fable planet test: a planet with less to work with

14 Oct 2026, Fable (helper run for the owner, relayed by Claude). Everything here was written into this folder only; nothing was installed in the client or the server, no server or bot command was run, nothing was downloaded. Core3 was read, not built or executed. Bellum Gero's repository was read for comparison only; none of its code is used by the tools here.

## Summary

- **Pick: Ossus** (Legends; Outer Rim, Auril sector, grid R-6). Nothing exists for it anywhere we can use: no terrain, no snapshot, no art named after it in the stock or MTG archives, nothing in Bellum's scripts. Its Legacy-era story is the strongest on the list (the Sith attack on the Jedi Academy in 130 ABY, the Temple levelled in 137 ABY, Jedi and Yuuzhan Vong in hiding, Ysanna tribes), and its terrain (temperate hills, mountains, gorges, forests, caves) can be dressed entirely with stock shaders, flora and ruins. Runner-up: Dagobah (even less to build, weak era relevance).
- **Proved:** I wrote our own `.trn` reader (`tools/trn_read.py`) that walks the file in exactly the order Core3's `IffStream` does, and a port of Core3's height evaluation. The port reproduces the Hoth server heights Claude recorded in `hoth-port-log.md` to 0.1 m at all 20 exactly specified points. With that, I generated a minimal Ossus terrain (`out/terrain/ossus_test.trn`, 1,829 bytes): one shader family, two fractals, a flattened landing pad, a water table. It round-trips byte for byte, re-reads in Core3's order with no complaints, uses only form/version pairs that stock SOE terrains use, and names only shaders the owner's client has.
- **Not proved:** the file has not been through Core3 itself (no build or run allowed) and the real client has not drawn it (`um win` needs the owner). Those are the next two checks.

## 1. Planet pick

Candidates not in the game. "Client" counts files whose names contain the planet's name in the archives the client loads (stock, then MTG). "Bellum" counts files in its scripts mentioning the name; most are incidental.

| Planet | What exists | Legacy-era fit | Risks | Verdict |
|---|---|---|---|---|
| **Ossus** | client: nothing; MTG: nothing; Bellum: 4 incidental mentions (a robe loot item, an event mobile, a tool) | Strongest: Academy massacre 130 ABY, Temple destroyed 137 ABY, hidden Jedi, Imperial watch, Ysanna, Vong shapers (Wookieepedia, Ossus/Legends) | No canon map, so we lay it out; Academy building and native fauna need stand-ins from stock art; a snapshot writer is needed (true for any planet) | **recommended** |
| Dagobah | client: 12 MTG textures of a "Dagobah ground beetle" item; Bellum: 0 Lua | Weak: no Legacy events; no cities (good for scope) | Swamp needs water/flora tuning; little gameplay anchor; catalogue status A (Sunrunner version not reusable) | runner-up |
| Ilum | nothing anywhere; stock has snow shaders (`snow_mtnspeak*`) and ice-cave shaders | Good: sacred Jedi crystal world; Unknown Regions needs a travel excuse | Ice look depends on a handful of stock shaders; crystal caves are interior work | third |
| Myrkr | nothing | Fair: ysalamiri world, hiding place for outlaws | No ysalamiri/vornskr art; forest otherwise stock | possible later |
| Ryloth | nothing; Twi'lek looks are stock; Bellum 1 Lua mention | Good: listed under Darth Krayt's Empire in Legends | Tidally locked world is hard to show; cities need art | possible later |
| Csilla | nothing; Chiss species in MTG (catalogue P) | Good: Chiss in Krayt's era | Underground cities = interiors; ice shaders as Ilum | later |
| Bastion | nothing (Bellum's 1 hit is the word "bastion") | Central: Fel's Empire-in-exile capital | Urban, art-heavy | later |
| Bespin | stock: a drink; MTG: 146 files of a Bespin player house; Bellum: house deed | Fair | Cloud City is platforms, not ground terrain; biggest art cost | no |
| Taanab (comparison) | **stock** `terrain/taanab.trn` (39 KB, a real 0014 terrain with 15 shader and 27 flora families, not a stub) + MTG snapshot, loading, region and theme music; Bellum: zone listed in config | Fair (agriworld) | It is other people's head start (MTG/Takhomasak), the opposite of this test; note that the stock copy wins the client load order over MTG's restored `taanab.trn` | not for this test |

Why Ossus: it is the one planet where every piece must be ours, which is the point of the test; the era fit is exact for 137 ABY; the physical world (hills, mountains, gorges, forests, caves, one spaceport at Knossa, one ruined academy, the Great Jedi Library in Ooroo Canyon, crystal caves under the Eocho Mountains) maps onto stock ground shaders, stock trees, Yavin IV temple ruins, Dantooine enclave pieces and stock cave interiors; scope is Hoth-sized. The owner's "optional encounters" policy applies: fauna named in lore (gokob, kirruk, tribis) have no art, so they would be our own creatures on stock bodies.

Lore sources read (Legends pages, 14 Oct): Ossus/Legends, Dagobah/Legends, Ilum/Legends, Myrkr, Ryloth/Legends, Csilla/Legends, Bastion/Legends, Taanab/Legends on Wookieepedia. Text above is our own wording.

## 2. How a `.trn` works

A `.trn` is an IFF tree: 4-byte tag, big-endian size, body; `FORM` records carry a type and children, other records are leaf chunks with little-endian data and zero-terminated strings. The planet terrain is `FORM PTAT > FORM 0014` (version; `0013` is the old test style, `0015` is post-CU and not read by Core3) with three children:

1. **`DATA` header:** name, map size (16,384 m for every stock planet, so coordinates run -8192..8192), chunk size (8 m), tiles per chunk (2), global water table on/off, its height and shader (`wter_*.sht`), day length, then four blocks (collidable flora, non-collidable flora, near radial, far radial): min/max draw distance, tile size, tile border, seed.
2. **`FORM TGEN > FORM 0000`, the generator:**
   - `SGRP/0006` shader families (`SFAM` chunks): id, name, surface file (`abstract/terrain_surface/grass.iff` etc.), colour, size, feather clamp, then child shaders with weights. Children are bare names; the client resolves `shader/<name>.sht`. All 41 names Tatooine uses, 41 Yavin uses and 48 Dantooine uses resolve in the owner's client.
   - `FGRP/0008` flora families (`FFAM`): collidable trees and rocks, each child an `.apt` appearance with weight, align-to-terrain, displacement, period, sway, scale range. `RGRP/0003` radial families (`RFAM`): grass and small plants drawn as `radl_*` shader sprites. `EGRP/0002` environment families (`EFAM`): named ids that layers assign to areas (weather/lighting lookups).
   - `MGRP/0000` fractals (`MFAM` > `MFRC/0001`): seed, bias, gain, octaves, octave multiplier, amplitude, x/y frequency, offsets, combination (0/1 plain Perlin sum scaled to 0..1, 2 ridged `1-|n|`, 3 `|n|`, 4/5 clamped). A second `MGRP` may follow with bitmap families (8-bit greyscale TGA, uncompressed type 3) for painted heights; Mustafar, Kashyyyk and MTG's Hoth use them, the stock pre-CU planets do not.
   - `LYRS` > `LAYR/0003` layers, each: `IHDR` (enabled flag, name), `ADTA` (invert boundaries, invert filters), then any mix of **boundaries** (`BCIR` circle, `BREC` rectangle, `BPOL` polygon, `BPLN` polyline with width; each with a feather type and amount), **filters** (`FHGT` height band, `FFRA` fractal band, `FSLP` slope, `FDIR` direction, `FSHD` shader, `FBIT` bitmap band), **affectors** (`AHCN` constant height with an operation: replace/add/subtract/multiply, `AHFR` fractal height, `AHTR` terrace, `AROA` road, `ARIV` river, `ASCN` shader, `ASRP` shader replace, `ACCN`/`ACRH`/`ACRF` colour, `AFSN`/`AFSC`/`AFDN`/`AFDF`/`AFCN`/`ARCN` flora and radial add/remove, `AENV` environment, `AEXC` exclude, `APAS` passable) and **child layers**. Evaluation at a point: boundary influence (max over boundaries, feathered; 1.0 if there are none) → filters narrow it (min) → affectors apply with that strength → children run with the product. Stock planets have 130–365 layers; the tutorial has one.
3. **Maps:** `FORM 0001 > DATA, WMAP, SMAP` (water and seed maps, 2048×2048 bits on the big planets) or empty chunks (tutorial, simple, Taanab). Local water is per boundary: `BREC/0003` and `BPOL` carry a water flag, height and shader; the header's global table covers the rest.

Feathering types everywhere: 0 linear, 1 x², 2 √x, 3 smoothstep. Everything is procedural: there is no heightfield in the file; the client and the server both compute heights from the rules, which is why they agree.

## 3. What Core3 needs server-side (read from Core3-dev, 14 Oct)

- **Loading:** `PlanetManager.idl:117` calls `terrainManager.initialize("terrain/" + zoneName + ".trn")`; the file comes from the server's `TreFiles` list through `TemplateManager`. `CmdStartScene.h:28` sends the same name to the client, so the client archive must hold it too. Zones are data-driven (`ZonesEnabled` in `config.lua`/`config-local.lua`, `planet_manager.lua`, `<zone>_regions.lua`); `Terrain.h`'s fixed name table is not used by zone code.
- **What it computes:** `ProceduralTerrainAppearance::getHeight` (height affectors only: `AHCN`, `AHFR`, `AHTR`, `AROA` with `HDTA` data), `getWater` (global table and the water boundaries collected at load), `getEnvironmentID` (`AENV`). `TerrainManager::getHeight` returns 0 outside ±size/2 and rounds coordinates down to 0.1 m before a cache lookup.
- **Field layouts confirmed** (file: `src/terrain/**`): header `ProceduralTerrainAppearance.cpp:119-186`; groups `ShaderFamily.h`, `FloraFamily.h`, `RadialFamily.h`, `EnvironmentData.h`, `MapFractal.cpp:149`, `BitmapFamily.h`; layer `Layer.cpp:53` (`IHDR`, `ADTA`, then children dispatched by form type, `Layer.cpp:120-303`); every boundary, filter and affector reader in `layer/boundaries`, `layer/filters`, `layer/affectors`. Versions accepted: PTAT 0013/0014, TGEN 0000, SGRP 0006, FGRP 0008, RGRP 0003, EGRP 0002, MGRP 0000, MFRC 0001, LAYR 0003, IHDR 0001, BCIR 0002, BREC 0002/0003, BPOL 0005, BPLN 0001, FHGT 0002, FFRA 0005, FSLP 0002, FDIR 0000, FSHD 0000, FBIT 0000, AHCN 0000, AHFR 0003, AHTR 0004, ASCN 0001, ASRP 0001, ACCN 0000, ACRH 0000, ACRF 0001, flora/radial affectors 0004/0002, AEXC/APAS/AENV 0000, AROA/ARIV 0005, maps 0000/0001. `ACBM`, `AFBM`, `AHBM`, `AHSM`, `ASBM`, `BALL`, `BSPL` are skipped. My reader flags any other version the way Core3 logs it.
- **Two things worth knowing:** (a) `FilterSlope`, `FilterDirection` and `FilterShader` do not override the virtual `process()` that `processTerrain` calls (different signature), so on the server any layer gated by a slope, direction or shader filter contributes no height, while the client applies those filters; this is one source of client/server height differences. (b) Core3 reads only the first fields of `ACRF` and a few others; stock files carry more bytes there, which Core3 ignores. My reader reports those as notes; all stock planets otherwise walk cleanly in Core3's order.

## 4. The prototype and its verification

Tools (all our own, Python 3 standard library, run with `python -I` from this folder):

- `tools/trn_iff.py`: IFF tree parse/build, our own TRE index reader, `client:<path>` access to the owner's archives (stock order first, MTG below, like the test-session launcher), `dump` and byte `roundtrip` commands.
- `tools/trn_read.py`: the `.trn` reader in Core3 order (`summary`, `check`), plus the height port (`height`): Park-Miller/shuffle random, Perlin noise, fractal combinations, boundaries, filters, affectors, TGA bitmap filter, 0.1 m rounding.
- `tools/trn_write.py`: builds `out/terrain/ossus_test.trn` and runs five checks; `verify <file>` runs them on any terrain.
- `tools/trn_preview.py`: greyscale heightmap PNG from the port; `tools/wslcat.sh`: read-only helper for Core3 sources.

What `ossus_test.trn` contains: PTAT 0014; size 16,384 m, chunk 8 m, 2 tiles; one shader family (stock Dantooine `grss_long_darkgreen` ×3 on `abstract/terrain_surface/grass.iff`); one environment family; two fractals; three layers: rolling hills (`AHFR`, 0–90 m), the Eocho mountain band along the south edge (`BREC` feathered 0.7 + ridged `AHFR` +320 m), and the Knossa landing pad (`BCIR` r 160 m feather 0.45, `AHCN` replace at 47.3 m, a value the builder read from its own draft so the pad meets the ground, the Hoth bowl lesson); global water at 35.5 m (the builder's 6th percentile of the plains, so hollows become lakes); empty flora/radial groups and empty maps, as SOE's tutorial and simple terrains ship.

Results (`out/ossus_test-report.json`):

| Check | Result |
|---|---|
| Byte round trip (parse → build) | identical |
| Re-read in Core3's chunk order | version 0014, 3 layers, no notes |
| Structure: every parent/child pair also in stock tutorial/simple/tatooine | 51 pairs, 0 unseen |
| Height survey, 256 m grid, 4,096 samples (Core3 port) | 25.7–361.8 m, mean 78.3 m, 5.8 % under water |
| Pad: spread over the inner 80 m / steepest 10 m step walking out | 0.000 m / 2.33 m |
| Shader and water shader names present in the client | all present |

Cross-check of the height port against the server (Hoth, from `hoth-port-log.md`, 14 Oct 02:20; server values in brackets): north of the pad at 250/300/350/400/450/500/550/600 m: 43.4 (43.4), 38.6 (38.6), 35.3 (35.3), 34.4 (34.4), 37.2 (37.2), 44.9 (44.9), 35.6 (35.6), 28.5 (28.5); east: 22.5, 23.6, 26.7, 31.7, 37.9, 44.0, 38.9, 32.5 (all equal); south 250/300/600: 8.7, 16.2, 10.9 (equal); west 250/300/600: 5.1, 13.5, 33.3 (equal); far north (0, 6000): 51.6 (51.6); pad: 0.0 (0.0). Three points the log describes only loosely ("2 km east", "3 km west", "at the ice caves") did not match at my guessed coordinates (42.5, 39.3, 196.2 vs 45.0, 45.0, 163.5); the exact probe points are not recorded. MTG's Hoth uses bitmap filters and ten slope filters, so this exercises those paths too.

Limits, stated plainly: Core3 never parsed this file (simulated by a reader that follows its code path); the client never drew it; that an empty flora/radial group and empty maps are acceptable to the client is inferred from the tutorial zone, which ships that way; `wter_dant_lake` as a global water shader is a reasonable guess (Yavin uses `wter_yavin_aqua` globally); road affectors are not in the height port (Ossus has none); Perlin noise is 0 on its lattice, so a few points such as (0, 0) sit exactly at mid-height, as in the client.

Previews: `out/ossus_test-height.png` (north up; the bright band is the southern mountains, grey specks the lakes) and `out/hoth-mtg-height-128.png` (MTG's Hoth through the same port).

## 5. Plan for a full Ossus (every piece, as in the Hoth log)

Effort is in agent working days for a first playable version; "gate" is the rights gate; "owner" is what needs the owner.

**Client (packed into our own `local_planets.tre`, above stock; Hoth's method):**

| Piece | Work | Effort | Gate | Owner |
|---|---|---|---|---|
| `terrain/ossus.trn` | grow the prototype: 6–10 shader families, flora and radial families from stock, the Academy benchland and Imhar Canyon as painted bitmaps, a road, caves as `AEXC` holes; our writer already covers every chunk type | 2–4 | ours; stock shaders referenced in place (same basis as Hoth) | none until the real-client look |
| `snapshot/ossus.ws` | a snapshot writer (Core3's `WorldSnapshotNode` reads it; MTG's `hoth.ws` is a 9 KB example): Knossa starport (`outpost_starport`, which spawns its own terminals), ruined temple and library from Yavin IV Massassi pieces and Dantooine enclave pieces, cave entrances (stock caves), Ysanna camps | 2–3 | stock buildings referenced in place | choose the story point (ruins only, or a crater where Stryfe levelled the Temple) |
| planet CRC table, `travel.iff`, `planet_n.stf`, `waypoint_planets.iff`, ticket UI, planet-map UI | as Hoth; we should replace Bellum's AGPL format tools with our own small writers (datatable and STF readers already exist in Claude's `swg_client_data.py`) | 1 | ours | galaxy-map position (R-6, near Yavin at P-6 and Dromund Kaas at R-5) |
| `texture/ui_map_ossus.dds`, `ui_planet_sel_ossus.apt` + texture | our own map art rendered from the heightfield (no wiki images) and a cloned stock planet model with our texture; DDS writer needed | 1 | ours | none |
| `terrain/environment/ossus.iff` (sky, suns: Ossus has two), `datatables/environment/ossus.iff`, `datatables/clientregion/ossus.iff`, `datatables/loading/ossus.iff`, loading screen | copy-and-edit from Dantooine; present for every stock planet (necessity unverified, so provide them) | 0.5 | ours | none |
| Real-client checks | terrain loads without the `not a valid terrain file` crash, ground renders, water, flora, ticket list, galaxy map, planetary map | 0.5 per round | – | **`um win` with the owner at the PC**, or the owner looks |

**Server (test galaxy first, Claude's area):**

| Piece | Work | Effort | Owner |
|---|---|---|---|
| zone registration | `ossus` in `ZonesEnabled` (test-galaxy `--config`), `local_planets.tre` first in `TreFiles` | 0.2 | test galaxy run |
| `planet_manager.lua` | Knossa travel point at the pad, weather, GCW, navmesh over the outpost | 0.3 | fares (Corellia → Ossus, as Hoth) |
| `ossus_regions.lua` | edge no-build strips, Knossa as a city, no-build over the ruins, spawn areas | 0.3 | none |
| creatures and NPCs | our own mobiles on stock bodies (Ysanna hunters, mount beasts, forest fauna, Imperial watch patrol, hidden Jedi encounter), lairs, world spawner | 2–3 | levels and the Imperial presence |
| screenplays | ruined Academy and Library POIs, crystal cave, a short Ysanna chain; all original text | 2–4 | yes to the story point |
| resources | the resource manager hard-codes planet lists in C++ (Hoth log, step 3) | 0.5 (C++) | none |
| bots | an Ossus smoke scenario (travel, ground profile, spawns) on Claude's Hoth pattern | 0.5 | none |

**Rights, by source:** our own files (terrain, snapshot, tables, strings, map art, scripts) need nothing. Stock client art and buildings are referenced in place in the owner's own client, the same basis the Hoth port rests on; they must not be copied out or redistributed. MTG material is not needed for Ossus; if any is used, catalogue status P with credit applies. Bellum's tools are not needed any more for terrain; for the six planet-list files either keep using them read-only under AGPL or replace them (recommended). Anything from Sunrunner (catalogue A), the Zeltros pack (CC-BY-NC) or the downloaded community packs is not needed and would need a rights check. Open-licensed kits (CC0, see `KOTOR-to-SWG-and-open-assets-feasibility.md`) could later supply props the stock game lacks.

## 6. Open questions for the owner

1. Ossus or Dagobah? (Ossus recommended.)
2. Which moment: 137 ABY after Darth Stryfe levelled the Temple (ruins, hidden Jedi gone to ground, Imperial patrols), or 130–137 ABY with the Temple standing in ruins and Jedi hiding inside?
3. Is an Imperial garrison present (Krayt's Empire), and are player Jedi encounters wanted here at all?
4. May the stock buildings (Yavin IV ruins, Dantooine enclave, outpost starport, caves) be reused in place for Ossus, as for Hoth?
5. Who runs the first real-client check of `ossus_test.trn` (`um win` with you at the PC, or you alone), and may Claude put it on the test galaxy and in a test-session `local_planets.tre` first?
6. Galaxy-map placement near Yavin IV (R-6 vs P-6)?

## 7. Files written (all under `h/outputs/Fable-planet-test/`)

`README.md`; `tools/trn_iff.py`, `tools/trn_read.py`, `tools/trn_write.py`, `tools/trn_preview.py`, `tools/wslcat.sh`; `out/terrain/ossus_test.trn`, `out/ossus_test-report.json`, `out/ossus_test-height.png`, `out/hoth-mtg-height-128.png`.
