# PL-05 Hoth leftovers: what is staged and how to install it

Claude, 17 Oct 2026, 2:00 AM scheduled run. **Staged only: nothing installed, nothing run on a galaxy, untested in game.**
Built from the owner's answers in `SWG-handoff.md`: "Owner's answers, 15 Oct 15:30-16:10", Q4 (Hoth leftovers), and the
14 Oct set, question 9 (mynock den: the ice-cave building, option 1, with the added flatten layer).

## What was already in dev (no work needed)

Read-only check of `/opt/swg/Core3-dev` at `07d9f61e` (the task named `69f5c879`; HEAD has moved on since, and the
patch is checked against the current HEAD):

| Owner's answer | State |
|---|---|
| Density 1024 | already: `hoth_world_spawner` is 1024 (batch A areas on top) |
| Map names for the areas and camps | already: 18 NAMEDREGION rows + `clientpoi`/`clientregion` in the installed archive (batch B3) |
| A junk dealer at the camps | already: one at the Scavengers' Camp (batch B1); kept, none added |
| No lower mission band | nothing to do |
| Tauntaun riding as its own test batch | not part of this build (needs two client object changes first, batch C, C2) |

## What this build adds

**Server patch** `hoth-leftovers.patch` (sha256 `26e27de7...`, 13 files, +148 / -7), against Core3-dev `07d9f61e`.
`git apply --check` passes there (run read-only as swgemu) and `luac5.3 -p` passes on every patched file.
`tools/stage_server.py` regenerates it from copies of the dev files (each edit needs its anchor exactly once).

| Answer | Change |
|---|---|
| Mynock den: the stock ice cave | `screenplays/poi/hoth_mynock_den.lua`: Fable's batch B2 screenplay unchanged (cave_06_flatland_s01_ice at -2000, -4800 and its 23 mynocks by cell); include line; a 160 m NOSPAWNAREA circle over the cave so the mynock-fields lairs keep off its mouth |
| Glacial rancor in a fixed den with a respawn timer | `screenplays/poi/hoth_glacial_rancor_den.lua`: Hoarfang at the Glacial Rancor Grounds (600, -4600, ground 26.4 m), respawn 1800 s like the cave bosses. Site and timer are open questions below |
| Pale blue, ideally the Chiss skin palette | `hoth_glacial_rancor.lua` now uses `object/mobile/rancor_ice.iff`, hue 5; new server template `object/mobile/rancor_ice.lua` + its `objects.lua` and `serverobjects.lua` rows |
| Quest chain gives a badge and a rare-decor roll | Vell's third job adds `{ loot, hoth_decor_rare }` and `{ badge, 141 }` to its 2000 credits |
| Artisan and entertainer terminals at the starport | two terminals in the row of mission terminals at (48, -1990) and (48, -1984), pad ground 0 m |
| Recruiters at the starport only | the two recruiters leave the forward camps; imperial and rebel recruiters at (54, -2016) and (54, -1980) |
| Delivery points at the camps | the Imperial Forward Camp, Rebel Forward Camp and Scavengers' Camp become mission "cities" (`mission_cities.lua`, radius 80) with three neutral spawn points each, so general deliver missions from the starport can end at a camp. The Raiders' Camp and the Contested Ground are fights, so they get none |
| Map names for the dens | NAMEDREGION rows `mynock_den` (60 m) and `rancor_grounds` (200 m) |

**Client step** `build_hoth_leftovers.py`. It chains on the installed archive `work/chain-1016/local_planets-chain-1016.tre`
(sha256 `df1d538e...`, still the archive named on the board's server-lock line), and every one of its 178 other entries
comes through byte for byte. Candidate: `work/hoth-leftovers/local_planets-hoth-leftovers.tre`,
**sha256 `108d4234e43b9b1804cd89416745f13f65c399f07625e7ce1a2aead8fcc52812`**, 199 entries. Two runs give the same bytes.
Its checks are in `checks-client.json`.

| Entry | What |
|---|---|
| `terrain/hoth.trn` (new) | Fable's B2 terrain patch, which the owner approved: MTG's `hoth.trn` plus one layer (a 160 m feathered flatten disc at 44.8 m and a 12 m mouth exclusion). The step checks that the client's MTG copy is still the one Fable patched (`51ede670...`) and that the staged file is unchanged (`ef2c1ee2...`). No other terrain edit |
| `clientpoi.iff`, `clientpoi_n/_d.stf`, `clientregion/hoth.iff` | the two den markers and labels, from Fable's `hoth_names.py` (held sites) on the archive's own copies. Only the 2 rows and keys are new. `hoth_region_names.stf` already had both keys, so it is unchanged |
| `badge_map.iff`, `badge_n/_d.stf` | badge **141** `bdg_thm_park_hoth_salvage` ("Vell's Salvage Crew"), in the shape of the stock theme-park badges (category 2, shown, type content). The step stops if 141 or the key is already taken, or if 141 is not the next free index |
| `object/mobile/shared_rancor_ice.iff`, `appearance/rancor_ice.sat`, `mesh/rancor_ice.lmg`, `rancor_ice_l0-4.mgn`, `shader/rancor_ice_*.sht` (new) | the stock `rancor_hue` meshes and texture. Its four shaders are rebound from `palette/creature_rancor.pal` to the stock `palette/npc_chiss_skin.pal` with default index 5 = RGB (0, 128, 182), the lightest of the palette's 8 blues |
| `misc/object_template_crc_string_table.iff` | + the CRC row for `shared_rancor_ice.iff` (29,359 rows) |

## Install order (for the session holding the server lock)

1. Owner's OK for a client archive change, as for every archive so far.
2. Back up the current archive on the server and in the client (the `.bak-<sha>` convention), then copy the candidate
   over `local_planets.tre` on both sides. **The server needs it before the patch:** the rancor's template reads
   `shared_rancor_ice.iff`, and badge 141 must be in the server's badge list.
3. `git -C /opt/swg/Core3-dev apply --check .../Hoth-leftovers/hoth-leftovers.patch`, then apply it and commit on dev, then
   run `check_lua.py`. Lua only, so no C++ build is needed.
4. Restart the test galaxy (the standing OK covers this only with no owner client running and no squad round in progress).
5. If another archive step lands first (Nal Hutta's 1:55 AM step, say), rebuild with `--base <that archive>`. The step
   stops on its own if badge 141 was taken in the meantime.

## Checks after install (untested so far)

- Server log: no `HothMynockDenScreenPlay: could not spawn` and no "cave has N cells" warnings. Hoarfang spawns at 600, -4600.
- `/find` or a bot visit: the den, the cave's 23 mynocks in their cells, and the camps without recruiters.
- Owner in the client: the mynock cave mouth is open (the mouth offset is inferred from the four stock caves); Hoarfang
  is blue (the base texture sets how pale it looks); the two new markers show on the planetary map; artisan and
  entertainer missions are offered at the starport; a deliver mission sometimes points to a camp.
- GPT's C23 Hoth acceptance covers the rest. GPT is back on 22 Oct.

## Questions for the owner (also on the board)

1. Where should the glacial rancor's den be? Staged: the Glacial Rancor Grounds, an open valley with no client change.
   Alternatives: one cell of the new mynock ice cave, or a second stock ice cave at the grounds (that needs another
   flatten layer and your OK).
2. Rancor colour: the Chiss palette's lightest blue (staged; a true blue, not pastel), or our own pastel-blue palette
   file (one new `.pal` in the archive)?
3. Rancor respawn: 30 minutes (staged, like the cave bosses), 2 hours or 6 hours? Each kill drops a rare decor item
   every time and a vehicle deed half the time.
