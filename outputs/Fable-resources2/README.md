# R2 resource backfill patch and T1 one home for the format tools — Fable, 14 Oct 2026

Stage only: nothing applied, read-only on /opt/swg (HEAD 1c4c24fb), no git in h/ (the `git apply --check` ran in a
scratch repo in WSL). Numbers are mine unless a source is named.

| path | what |
|---|---|
| `cpp/resource-backfill.patch` | R2: git diff against Core3-dev 1c4c24fb (4 files, +97 lines), `git apply --check` clean, `luac5.3 -p` clean |
| `work/estimate.py`, `work/estimate.json` | R2: the offline estimate |
| `t1/staged/tools/swgfmt/` | T1: the package (`__init__`, swg_tables, trn_iff, tre_write, ui_inc, fmt_tools, hoth_ui, ws_read) |
| `t1/staged/<old paths>` | T1: the seven shims at the old module paths and the nine patched importers |
| `t1/patch/*.patch` | T1: unified diffs for every importer and shim; `t1/make_package.py` regenerates all of it |
| `t1/prove.py`, `t1/proof.json` | T1: the proof runs |
| `checks.json` | both |

## R2. Resource backfill for a planet that joins activeZones

**Lua-only route first.** There is none that keeps the spawns: a pool entry restricted to a planet (what dev 1c4c24fb
did with the ten `*_hoth` types) covers only types the tree ties to that planet; `ResourceCommand.h` offers `list`,
`health`, `dump`, `despawn`, `info`, `find`, `perfect` and `create` (lines 38–62) — `/resource despawn <name>` would make
the pool spawn a replacement with the new zone in the draw, but that throws away the galaxy's current spawns one by one
(crafters' stocks and names) and is manual; usable on the test galaxy, not on live. No pool option adds zones.

**Why the gap exists.** Zones are chosen once, at creation (`ResourceSpawner.cpp:543 newSpawn->createSpawnMaps(...)`
with a clone of `activeResourceZones`), by `ResourceSpawnImplementation::getSpawnZones` (lines 160–189):

```cpp
	if (minpool == maxpool)
		zonecount = maxpool;
	else
		zonecount = System::random(maxpool - minpool) + minpool;

	if (zonecount > activeZones.size())
		zonecount = activeZones.size();

	/// If resource is zone restricted, add only the restricted zone
	if (zonerestriction != "") { zonenames.add(zonerestriction); return zonenames; }

	/// Randomly remove entries until the Vector contains
	/// a number of elements equal to zonecount
	while (activeZones.size() > zonecount)
		activeZones.remove(System::random(activeZones.size() - 1));
```
So a galaxy-wide spawn lives on `zonecount` zones drawn uniformly from the active list, `zonecount` uniform in
[minpool, maxpool] from the tree's "Minimum/Maximum # Pools", capped at the number of zones: **any one zone's chance is
zonecount / zones.** At load, `ResourceSpawner::loadResourceSpawns` (lines 147–171) only tops up a spawn whose map
count is below `minPool` ("Create spawn maps for zones that were disabled when the resource spawned"), so a zone added
later gets nothing until the spawn expires.

**The patch** (`ResourceSpawner.{h,cpp}`, `ResourceManagerImplementation.cpp`, `resource_manager.lua`):
- `backfillZones = ""` in `resource_manager.lua`, read next to `activeZones` (`ResourceManagerImplementation.cpp:94–103`
  pattern) into `ResourceSpawner::addBackfillZone`, which ignores a zone not in `activeZones` with a warning. Empty
  string → nothing changes anywhere: live is unaffected unless it is set.
- In `loadResourceSpawns`, right after the stock top-up and under the same `inShift()` / tree-entry checks, for every
  in-shift spawn with an empty zone restriction: for each backfill zone, skip if the spawn already has that zone
  ("already there"), skip if its map count is at `maxPool` ("at max pool": it already lives on as many planets as its
  type allows; it reaches the new planet only when it expires), otherwise roll with chance mapCount / activeZones and,
  on a win, `Locker locker(resourceSpawn)` (as the top-up) and `createSpawnMaps(entry->isJTL(), 1, 1, "", {zone})`, so
  the density map gets the same concentration rule as a creation-time map.
- **JTL spawns are included**: the JTL flag only changes the concentration (`getConcentration`, line 150) and the shift
  length; their zones come from the same `getSpawnZones` rule on the same active list (`jtlresources` are ground-mined
  types such as steel_bicorbantium, all in the fixed pool), so a new planet is owed its share of them too.
- **Idempotent without remembering losers:** the roll is `(spawn name + ":" + zone).hashCode() % 1000` against
  `mapCount * 1000 / zones`, a fixed function of the spawn and the zone, so a second start decides every spawn exactly as
  the first did and adds nothing new (winners are "already there", losers lose again). Without that, a plain random
  roll would need a stored "rolled" mark per spawn and zone (an IDL field on ResourceSpawn or a keyed set in the
  manager) or the planet would gain every spawn after enough restarts; the hash is the smallest fix. The chance moves
  only when the number of active zones changes (then every spawn's share moves with it, as it should).
- One log line per zone at the end of the load: `Resource backfill: zone hoth: N in-shift galaxy-wide spawns checked, A
  added, B already there, C at max pool, D not chosen`.

**Offline estimate** (`work/estimate.py`: pools from `resource_manager.lua` at 1c4c24fb, min/max pools from the merged
tree, k uniform in [min, max] capped at the 10 zones of creation, chance k/11). The test galaxy's 15,020 spawn records
are mostly history; in shift and galaxy-wide there are **64**: minimum pool 15 (13 types, polymer and lubricating oil
twice), random pool 27, fixed pool 22 (iron 14 + the 8 JTL types). The 42 native and 10 Hoth-restricted spawns are
zone-restricted and untouched. Expected on Hoth after the first backfill start: **mineral 16.4, chemical 5.1, gas 2.7,
water 0.05, energy 0 (no galaxy-wide energy spawns; Hoth's wind and solar are natives) — 24.3 of 64 (38%)**; ores,
iron and petrochem fuels (1–3 planets each) mostly stay away (chance 0.17–0.18), gemstones, carbonate ore and inert
petrochems (8 planets each) nearly all arrive (0.73). The real count is the log line.

**Test plan (test galaxy).** 1. Build, then start with `backfillZones = "hoth"`: read the `Resource backfill:` line
(expect about 24 added of 64 checked, 0 already, a few at max pool). 2. `/resource list hoth` (admin) before and after:
the after list gains the added names; `/resource info <name>` on one shows hoth among its planets. 3. Survey with a
mineral, chemical and gas tool on Hoth: types appear with real names. 4. Restart with the same setting: the line now
reads `0 added, 24 already there` (idempotence); set `backfillZones = ""` and restart: no line. 5. Corellia unchanged:
`/resource list corellia` identical before and after. 6. When Ossus joins: `backfillZones = "ossus"` for its first
start, zones = 12.

## T1. One home for the format tools: `outputs/tools/swgfmt/`

A package (`from swgfmt import swg_tables, trn_iff, tre_write, ui_inc, fmt_tools, hoth_ui, ws_read` after one
`sys.path.insert(0, <outputs>/tools)`), relative imports inside, no `sys.path` walks across Fable-* folders. `ws_read`
(the .ws snapshot reader) joins the six named modules because `hoth_snapshot.py` needs it (`ws_objects()` added, the
tuple shape Bellum's `iff_tool.ws_objects` gave); `fmt_tools` gains `walk_tres`, `cfg_priorities` and `extract_entry`
(our own code, the contract the Hoth scripts used from `tre_inventory`); `trn_iff` finds the project root by walking up
to `outputs/SWG-client` instead of counting `..`, so it also works from a staging folder.

**Shims:** each old path (`Fable-ossus/tools/swg_tables.py`, `Fable-planet-test/tools/trn_iff.py`,
`Fable-builder/tools/{tre_write,fmt_tools,hoth_ui}.py`, `Fable-ossus/o4/tools/ui_inc.py`, `Fable-hoth-caves/tools/ws_read.py`)
becomes a 12-line file that puts `outputs/tools` on the path and sets `sys.modules[<name>]` to the package module — the
same object, so every other Fable tool (stage_tables, stage_env, O2, acst, species_tables, resource_names, trn_read's
`from trn_iff import ...`) keeps working unchanged; run as a script it forwards to the package module's `main`.

**Patched importers** (`t1/patch/`): `hoth_client_build.py` and `client_load_order.py` (`from swgfmt.fmt_tools import ...`),
`hoth_names.py`, `stage_ossus.py`, `map_art.py` (which keeps its inserts for `trn_read`, `trn_road` and `dds`: those stay
beside their batches), and the four Hoth scripts: `hoth_client_files.py`, `hoth_registration_check.py` and
`hoth_snapshot.py` drop the `exec` of `tre_inventory` entirely; `hoth_closure.py` drops it for the TRE side but still
execs `iff_tool.py` for `refs()`, Bellum's regex scanner of asset references — **missing from our readers**: a path
scanner for `.apt/.msh/.sht/.lod/.pob/.cdf` and terrain family references. If wanted, that is a 40-line module of our
own (the regexes are the whole of it) and the last Bellum import in `tools/`.

**Proof** (`t1/proof.json`): the builder rebuilt in a scratch folder with the patched builder and loader → 12 round trips
exact, archive verified, the same 20 entries with the same bytes and **the same sha256 aee83cc675a1e6cf** as
`Local-content/local_planets.tre`; `client_load_order.py` identical stdout; `hoth_names.py` and `stage_ossus.py` identical
files and stdout (stage_ossus `--selftest` passes); `map_art.py` identical `--check` output and identical 128-pixel
renders. The three scripts whose current versions exec Bellum's reader were not run in their old form (downloaded code
is read, not run); their new output was checked against the recorded facts instead: `hoth_client_files.py roundtrip` →
"all round trips exact"; `hoth_snapshot.py hoth` → 94 objects, 17 at world level, the outpost starport at 0 -2000 (port
log 13 Oct); `hoth_registration_check.py hoth` → the six stock winners report "no hoth", as the port log recorded on 13 Oct.
`hoth_closure.py` was run once with its TRE side ours (that run exec-ed `iff_tool.py` for `refs()`): its TSV is
byte-identical to the recorded `Documentation-support/hoth/hoth-closure.tsv` (488 rows).
