# Hoth map names (batch B3): markers, labels and the names file — Fable, 14 Oct 2026

M1 answer, M2 data and M3 staging tool. Read-only on `/opt/swg`; nothing loaded by Core3 or seen in a client. Sources read
as text: Core3-dev (`e9094960`), the client archives through our own readers, Bellum Gero's change log and Hoth scripts
(AGPL-3.0; its `src/` is not in the research copy). Numbers below are mine unless a source is named.

## M1. How a place gets on the planetary map in Core3-dev (no C++ needed)

**The stock client draws its "Points of Interest" category from its own table, not from the server.**
`datatables/clientpoi/clientpoi.iff` (patch_12_00, 220 rows: `Name @clientpoi_n:key, Description @clientpoi_d:key, Planet,
Appearance, X, Y, Z`) is where Tatooine's Fort Tusken, Krayt Graveyard, Ben Kenobi's House and the rest come from; the
names and the tooltip descriptions are `string/en/clientpoi_n.stf` / `clientpoi_d.stf`. Core3's only use of that table is
`PlanetManagerImplementation::isInRangeWithPoi` (no player structure, event perk or shuttle beacon within 100–150 m of a
POI). This matches Bellum Gero's in-game finding (change log 2026-10-06) that server-sent `poi` map entries never show
and that it fell back to registering its MAPPOI regions as "Theme Park".

Server side, the only registration path is `setPlanetMapCategory` + `Zone::registerObjectWithPlanetaryMap` (C++: city
regions, vendors, camp kits, buildings with a template category); there is no Lua binding, and `camp` (index 49) is a
sub-category of the faction categories, not a main category, so it cannot be used from `getPlanetMapCategoryByName`.
A server route would need the 3-hunk patch Bellum describes (`readRegionObject`: flag → category → register;
`MapLocationEntry::setObject`: send the raw `@file:key` for regions, keep a POI's name inside a city), and it would still
land under "Theme Park". So: **markers through `clientpoi.iff`, location labels through `datatables/clientregion/hoth.iff`**
(the client's region-name table; MTG ships one row, the outpost), **and NAMEDREGION rows server side** (Core3 uses the
flag only to name a region for `PlayersNearYou`; harmless, keeps the server's list in step with the client's). The
outpost already shows as a city (CITY region) and needs nothing.

## M2. The sites (`sites.tsv`, one source for every file)

| kind | sites | marker | label radius |
|---|---|---|---|
| cave | Frostfang's Cavern, Icemaw's Den, Snowblind's Lair, The Matriarch's Cavern (MTG's four caves, names ours) | yes | 40–60 m |
| area | The Ice Caves (the existing no-build circle, renamed with `NAMEDREGION`) | no (four cave markers) | 450 m |
| camp | Imperial Forward Camp, Rebel Forward Camp, Scavengers' Camp, Raiders' Camp, Contested Ground, Lucky Despot Wreck (batch B1 sites) | yes | 60–150 m |
| zone | Western/Eastern Tauntaun Plains, Mynock Fields, Western/Southeastern Wampa Flanks, Imperial Patrol Zone, Rebel Patrol Zone, Scavenger Country (batch A circles) | yes, at the centre | 700–1800 m |
| held | Mynock Den (-2000 -4800), Glacial Rancor Grounds (600 -4600): not in dev yet (den option pending; the rancor is only a mobile template) | `--held` | |

Descriptions are our own text (`clientpoi_d`). `wampa_flanks_west/southeast` are two new keys (names.tsv had one
`wampa_flanks`; two areas with one server name would collide in `RegionMap`); the Mynock Fields marker sits 400 m north of
the centre so the den's marker has room. The 150 m no-build rule around every marker is a side effect to know about (it
also protects the camps and cave mouths).

## M3. `tools/hoth_names.py`

```python
from hoth_names import stage_hoth_names
report = stage_hoth_names(stage_dir)              # base = the client's winning copies (stock beats MTG)
report = stage_hoth_names(stage_dir, base=fn)     # fn(name) -> bytes of your merged copy (idempotent: present keys/rows kept)
```
Writes `string/en/hoth_region_names.stf` (MTG's 2 keys + the 22 names.tsv keys + 2), `datatables/clientregion/hoth.iff`,
`datatables/clientpoi/clientpoi.iff`, `string/en/clientpoi_n.stf`, `string/en/clientpoi_d.stf`, and
`snippets/hoth_regions_named.lua`. Every base file is round-tripped byte-exact before it is changed (assert), string ids
continue from `next_id` (bumped past the highest id if stale — Bellum's `frn_n` collision), and a second pass with the
staged files as base adds nothing and writes identical bytes (`checks.json`). `python -I hoth_names.py --verify <dir>`
re-reads a staged set. Options: `include_held=True`, `large_first=True` (label rows are written smallest circle first
so a cave label wins over "The Ice Caves"; stock tables only nest same-named circles, so the client's pick between
nested labels is untested — flip the order if the umbrella label shows inside a cave).

## Files

| path | what |
|---|---|
| `sites.tsv` | the 21 sites: key, kind, status, centre, radius, marker/region switches, name, description |
| `tools/hoth_names.py` | `stage_hoth_names(stage_dir, base)`, `verify()`, the snippet writer |
| `staged/client/…` | the five client files as built from the winning copies (for `local_planets.tre`) |
| `snippets/hoth_regions_named.lua`, `patches.tsv`, `new-files.txt`, `apply.sh` | server rows: 19 NAMEDREGION circles before the world-spawner comment, plus the ice-caves rename (replace) |
| `checks.json` | round trips, key/row counts, idempotence, held/large-first run |
| `work/` | the read-only queries (q*.sh), category/POI table dumps, scratch-apply script |

## Apply and verify

1. Client: `stage_hoth_names(<stage>)` from the archive builder (or take `staged/client/`) into `local_planets.tre`; the
   test galaxy reads the same archive first, so the server's `isInRangeWithPoi` sees the markers too.
2. Server: `bash …/Fable-hoth-mapnames/apply.sh --selftest`, `--check`, then apply (done here on a scratch copy of dev's
   `hoth_regions.lua`: 34 → 56 lines, `luac` ok, the table loads in lua5.3 with 34 rows / 19 named / no duplicate names,
   ice_caves flags 272 = NAMEDREGION + NOBUILDZONEAREA; a second apply changes nothing). Restart the test galaxy.
3. In the client: open the planetary map on Hoth, tick Points of Interest (18 markers with names and descriptions);
   walk a bot into Frostfang's Cavern and the Scavengers' Camp and read the location label; `/find` is unaffected.
   The staged rows follow the stock ground rows exactly (blank Appearance, `X, 0, Z` = world x, height 0, world y);
   if the Hoth list stays empty in the client, tell me what Tatooine's list shows in the same session and I will look
   at how the client picks the planet.
