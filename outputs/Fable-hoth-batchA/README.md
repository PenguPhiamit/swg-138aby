# Fable: Hoth batch A, staged (14 Oct 2026)

A1 area spawn regions, A2 creature audit, A3 clean-room glacial rancor. Staged for Claude to review, apply to `/opt/swg/Core3-dev` and test; nothing has been loaded by Core3 or seen in game. Read-only sources: Bellum Gero's Hoth files (AGPL-3.0, read as text), MTG's server scripts (`work/research/mod-the-galaxy`), MTG's `hoth.trn`/`hoth.ws` in the owner's client (our own readers), Core3-dev (`cat`/`grep`). No git run.

## Folder

| Path | What |
|---|---|
| `staged/MMOCoreORB/bin/scripts/managers/planet/hoth_regions.lua` | dev's file + 8 area spawn regions (changed; dev sha256 `c94c3124…`) |
| `staged/.../mobile/spawn/hoth/hoth_{tauntaun_plains,mynock_fields,wampa_flanks,imperial_zone,rebel_zone,scavenger_zone}.lua` | 6 new spawn groups |
| `staged/.../mobile/spawn/serverobjects.lua` | dev's file + 6 include lines after `spawn/hoth/hoth_world.lua` (changed; `52ee9446…`) |
| `staged/.../mobile/hoth/hoth_glacial_rancor.lua` | A3 template (new) |
| `staged/.../mobile/hoth/serverobjects.lua` | dev's file + 1 include line (changed; `fbf14a77…`) |
| `apply.sh`, `apply-manifest.tsv` | hash-checked copy (same script as the caves batch); `--check` ran clean: 3 to change, 7 new, 0 refused |
| `checks.json`, `luac.txt` | area slope/clearance checks, density numbers, template list, rancor derivation, file hashes; luac5.3 -p passes all 10 files |
| `tools/hoth_survey.py` (height/slope survey on MTG's terrain through the validated Core3 port), `tools/stage_batchA.py` (generator), `tools/luac_staged.sh`, `work/*.orig` (dev originals) | |

Apply, as swgemu inside Debian: `bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchA/apply.sh --check`, then without `--check`. Hoth resources are already done (dev 2f205cd2); nothing here touches them.

## A1. Area spawn regions

**Bellum vs dev today.** Bellum's `hoth_regions.lua` has no area spawners either: edges, three outpost cities (their moved sites), named POIs with map markers (ice caves, each boss den, a northern ice cavern, generator ridge, shield-generator battlefield, raider camp, Lucky Despot wreck, glacial rancor grounds), two shuttleport no-builds, and one world spawner (`hoth_world`, 1024). Dev has the edges, MTG's outpost at (0, -2000) as city + no-build, the cave no-build (-400, 2600; 450 m) and the same world spawner with the same 11 lairs. MTG's own `hoth_regions.lua` is empty. So the "area split" is new work, not a port; the lairs and weights come from the ported `hoth_world` (Bellum, AGPL, credited in each file).

**Siting on MTG's map.** `tools/hoth_survey.py grid 1024` (Core3 height port, matched to the server on Hoth) shows plains at 10-45 m over most of the map, a mountain massif around the caves (up to 270 m), ranges in the north-west, north-east and south (140-165 m), and a flat band at 2 m along the edges. Every area below sits on ground where no 100 m step exceeds 30 m, outside the outpost city (200 m) and the cave no-build (450 m), and off the massif (`checks.json` -> `areas`):

| Region | Centre, radius | Group (lairs, weight) | Max lairs | Mean height / steepest 100 m step |
|---|---|---|---|---|
| hoth_tauntaun_plains_west | (-3000, -1500) 1800 m | tauntaun herd 60, tauntaun lair 40, probe droid 10 | 64 | 32 m / 21 m |
| hoth_tauntaun_plains_east | (3000, -1200) 1500 m | same | 64 | 32 m / 21 m |
| hoth_mynock_fields_south | (-2000, -4800) 1200 m | mynock pack 50, mynock lair 40, wampa 10 | 48 | 33 m / 29 m (southern foothills) |
| hoth_wampa_flanks_west | (-1800, 3200) 900 m | wampa 45, wampa lair 35, tauntaun herd 20 | 32 | 25 m / 20 m (1.5 km west of the caves) |
| hoth_wampa_flanks_southeast | (1200, 1500) 700 m | same | 32 | 20 m / 17 m (1.9 km south-east of the caves) |
| hoth_imperial_zone_east | (2500, -3500) 1200 m | snowtrooper patrol 45, salvage team 30, probe droid 25 | 48 | 29 m / 22 m |
| hoth_rebel_zone_northwest | (-2500, 1000) 1200 m | rebel patrol 60, probe droid 25, tauntaun herd 15 | 48 | 29 m / 18 m |
| hoth_scavenger_zone_southwest | (-1500, -3200) 900 m | scavenger raider camp 50, tauntaun herd 25, mynock pack 25 | 48 | 21 m / 22 m (1.9 km from the outpost) |

Rejected sites (too steep): north foothills (2500, 5100) 46 m steps, (1800, 3000) 94 m, (-5000, 3600) 137 m, (-1200, 1700) 114 m, (3500, -5000) 71 m. Region names are plain strings (MTG's `hoth_region_names.stf` has only `world_spawner` and `hothstarport`), so they do not appear on the planetary map; map POIs need `.stf` keys in `local_planets.tre` (owner question 3). The world spawner stays unchanged as the fallback.

**Density.** Before: one lair cap of 1024. After: 1024 + 384 area lairs = 1408 (+37.5 %), concentrated where the terrain is flat. Alternative in one number: world spawner 768 -> 1152 total (+12.5 %). Owner question 1.

## A2. Creature audit

Every Hoth creature or NPC template referenced by MTG's server scripts and Bellum's Hoth files, against Core3-dev (`addCreatureTemplate` names) and the client archives (bodies):

| Source | Templates | In Core3-dev | Client body |
|---|---|---|---|
| MTG (`mobile/custom_content/mobile/`) | wampa (lvl 178), baby_wampa (25, wampa body), wampa_static, snowtrooper_s01, rebel_snow_f_01, rebel_snow_m_01, dressed_rebel_snow_echo_base_derlin + f_01-04 + m_01-04, tauntaun_static, tcg_armored_tauntaun, tcg_tauntaun_ride, hoth_collector, hoth_turret_s1, hoth_turret_s2, snowspeeder, snowspeeder_ai | all present (MTG import in dev) | all present (`mtg_patch_022.tre`, `mtg_patch_010_object_01.tre`) |
| Bellum (`mobile/hoth/`, 21) | hoth_wampa, hoth_elder_wampa, 5 named wampas, hoth_ice_mynock, hoth_greater_ice_mynock, hoth_mynock_broodmother, hoth_tauntaun, hoth_tauntaun_bull, hoth_probe_droid, hoth_snowtrooper(_sergeant), hoth_rebel_snow_soldier/_sergeant, hoth_scavenger(_raider), hoth_imperial_salvage_tech | 20 present | present: wampa (MTG), salt_mynock_hue, tauntaun_hue, probot, snowtrooper_s01, rebel_snow_* (MTG), dressed_tatooine_scavenger, dressed_goon_twk_male_01, dressed_robber_human_female_01, dressed_mercenary_commander_zab_m, dressed_imperial_atat_pilot_m (stock) |
| Bellum | hoth_glacial_rancor | **missing** | **missing** (`object/mobile/shared_exotic_rancor.iff` in no archive the client loads) |
| Bellum static spawns (`screenplays/static_spawns/hoth_*.lua`) | hoth_* above plus stock junk_dealer, rebel_recruiter, imperial_recruiter, and Bellum's own myswg_vendor | all stock ones present; myswg_vendor is Bellum-only (vendor system) | – |

Result: no template is "missing with a client body", so A2 stages nothing; the one gap is the glacial rancor (A3). Bellum's `hoth_wampa` family and MTG's `wampa` (level 178) overlap; dev uses Bellum's.

## A3. Glacial rancor, clean-room

`mobile/hoth/hoth_glacial_rancor.lua`, registered through `mobile/hoth/serverobjects.lua`, **not spawned anywhere**. Only the concept (a glacial rancor world boss on Hoth) is Bellum's; body, name, text and stats are ours:

- **Body:** stock `object/mobile/rancor.iff` with `hues = {15}` from `palette/creature_rancor.pal` (RGB 244, 220, 139, the palest of its 32 entries; the stock palette has greens, yellows, browns and reds, no white or blue), `scale = 1.35`. A true ice-white/blue needs a palette of our own in `local_planets.tre` plus a cloned hue appearance chain (owner question 5).
- **Name:** "Hoarfang, the Glacial Rancor" (customName). Description text for a `.stf` entry, if wanted: "A rancor the colour of old ice. Nothing on this plain hunts it; everything on this plain has learned to run."
- **Stats (level 400, Bellum's own value for this boss; not an owner decision, corrected by Claude 08:20):** scaled from Core3's top stock bosses: krayt_dragon_ancient (336: HAM 410k-501k, damage 2270-4250, armor 3, resists 195, XP 28,549) and giant_canyon_krayt_dragon (300: 385k-471k, 1645-3000). Ours: HAM 490k-600k, damage 2700-5000, armor 3, resists 195 with cold 200 and heat 150, XP 28,549 (the stock cap), ancient_bull_rancor's attacks plus knockdown and intimidation, ferocity 25, carnivore meat / leathery hide / mammal bone 2000/2000/1900. Bellum's own numbers (HAM 1.4-2 M) were not used; they assume a 25-player per-player reward fight.
- **Loot:** `hoth_decor_rare` 100 % and `hoth_vehicle_deeds` 50 % on the corpse, as a placeholder for the owner's boss-loot decision (caves README).
- **Spawn options:** (a) the world-boss rotation (dev bda2c0dd): add `{ template = "hoth_glacial_rancor", name = "Hoarfang, the Glacial Rancor", ham = 1, planet = "hoth" }` to the roster and a Hoth entry in `spawnPoints` (e.g. the southern plain (600, -4600), mean 19 m, Bellum's "glacial rancor grounds" site, which is flat on MTG's map too); it then shares the rotation's per-player bank reward; (b) a fixed den: a screenplay spawn in one of the two unused ice-cave cells or at the mynock den once that building exists; (c) a NAMEDREGION + MAPPOI "glacial rancor grounds" with a dedicated screenplay and respawn timer.

## Owner questions

1. Density: keep the world spawner at 1024 (+37.5 % lairs with the areas) or drop it to 768 (+12.5 %)?
2. Level 400 for the glacial rancor (Bellum's value; a 2-4 group fight above krayt scale), or a lower Core3-style level such as 336 like the ancient krayt?
3. Should the areas and the cave dens get planetary-map names (needs `hoth_region_names.stf` keys in `local_planets.tre`)?
4. Which spawn option for the rancor: rotation (a), den (b) or grounds (c)?
5. Is a white/blue palette worth the client-side work (new `.pal` + hue appearance chain), or is the cream stock hue enough for now?
6. Boss loot: corpse loot (current) or the per-player reward from the caves README?

Untested in Core3 and the client; Claude applies and tests (test galaxy, then a bot walk through the plains to count lairs).
