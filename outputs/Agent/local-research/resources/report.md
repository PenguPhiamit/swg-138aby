Written by Claude Haiku, 15 Oct 2026, from Core3-dev 90044b8e.
(Run resumed and finished by Claude Opus 5.5. HEAD of /opt/swg/Core3-dev confirmed as 90044b8e. Paths are relative to MMOCoreORB/.)

# Resources: spawns, shifts, harvesters, stacking

## 1. Short answer
Five pools (minimum, random, fixed, native, manual) each keep slots filled with resource spawns. Every 2 h a shift task replaces any spawn whose despawn time has passed. Each new spawn gets random stats within the resource tree's ranges, a random lifetime (6-22 days organic, 13-22 JTL, 6-11 other), and one simplex-noise density map per chosen planet. Harvesters add `minutes x density x extractionRate` units to their hopper, up to the hopper's capacity, while they have power and maintenance. Resource stacks max out at 999,999 units; anything above that spills into a new container. Per-planet types come from `datatables/resource/resource_tree.iff` (Hoth and Ossus need the merged copy in local_planets.tre) and from the pool lists in resource_manager.lua.

## 2. How it works
**Config.** `bin/scripts/managers/resource_manager.lua`:
- active zones (12, including hoth and ossus): :51
- `backfillZones=""`: :59
- `poolScaleZones=10`: :66
- `averageShiftTime=7200000` ms (comment suggests 15000 for testing): :68-72
- `aveduration=86400` s: :74
- `spawnThrottling=90`: :81
- `lowerGateOverride=1000`: :89
- `maxSpawnQuantity=0`: :99
- JTL list: :121
- minimum pool, plus one each of the Hoth, Ossus and lore types: :125-149
- random pool (weights, excludes iron and fiberplast, 27 slots): :154-156
- fixed pool (iron x14 plus each JTL type x1): :159
- native list (45 organics, energies, fiberplast, water_vapor): :165

The loader is in `src/server/zone/managers/resource/ResourceManagerImplementation.cpp:83-161`. If the Lua fails it uses 10 stock zones and 2 h / 86400 / 90 / 1000 / 0 (:163-178). The spawner clamps throttling to 10-90 and the gate override to 1-1000 (`resourcespawner/ResourceSpawner.cpp:127-146`).

**Shift.** At start: load the DB, then shift (ResourceSpawner.cpp:148-151). The task reschedules itself every `shiftInterval` (ResourceManagerImplementation.cpp:186-212). A shift updates the random, fixed, native, minimum and manual pools in that order, then dumps the resources to Lua (ResourceSpawner.cpp:465-473).
- A slot is refilled when it is empty or `!inShift()`, where `inShift` means despawned > now (`src/server/zone/objects/resource/ResourceSpawnImplementation.cpp:24-26`).
- The minimum pool first reuses a random-pool spawn of the same type (`resourcepool/MinimumPool.cpp:69-81`).
- The random pool picks an included type by weighted index (`RandomPool.cpp:71`).
- Native slots are keyed `<type>_<zone>`, one per zone (`NativePool.cpp:41-50, 77-119`).
- Despawn drops the spawn from the per-zone lists but keeps it in the global name map (`ResourceSpawner.cpp:672-681`; `resourcemap/ResourceMap.cpp:71-95`).
- Each pool logs "<Pool> updating: Spawned X Despawned Y" (e.g. MinimumPool.cpp:99-100).

**Creating a spawn** (ResourceSpawner.cpp:578-654):
- Name: unique, from the name manager (:683-694).
- Stats: `random(max-min)+min`, with min lowered to `lowerGateOverride` if it is above it. Below 90 throttling there is a 1-in-10 roll for an above-breakpoint value (:696-721); at 90 the result is a plain uniform roll.
- Lifetime: `now + random((max-min)*aveduration) + min*aveduration` (:723-738).
- Planet count: `random(maxpool-minpool)+minpool`, capped at the active zone count; a zone-restricted type gets only its own zone (ResourceSpawnImplementation.cpp:160-189).
- Pool sizes are scaled: `(pool*zones+5)/10`, clamped to 1..zones (ResourceSpawner.cpp:107-116).

**Backfill.** On start, for zones listed in `backfillZones`, each in-shift unrestricted spawn is added to that zone when `hash(name:zone)%1000 * zones < baseMaps*1000`. It is skipped if already on the zone or at max pool. The roll is the same on every restart. Log: "Resource backfill: zone ..." (ResourceSpawner.cpp:213-263, 297-301).

**Concentration maps.**
- Density class: HIGH for JTL, chemical and gas_inert; LOW for ore, water, solar and wind; MEDIUM for everything else (ResourceSpawnImplementation.cpp:144-158).
- Peak density: HIGH 0.90-0.99, MEDIUM 0.75-0.95, LOW 0.50-0.75 (`src/server/zone/objects/resource/SpawnDensityMap.h:128-148`).
- Map scale: frequency 0.00015 for ore, 0.0006 for others (:131-134).
- Density at a point = `max(0, simplex(x*m, y*m, seed*m)) * density`, measured from the zone's min X / max Y (:106-115). It reads 0 off-planet or after expiry (ResourceSpawnImplementation.cpp:191-201).

**Survey and sample** (ResourceSpawner.cpp):
- Survey: costs `100 - focus/15` mind and sends a grid of up to 6x6 points. A "Resource Survey" waypoint is placed if the peak is at least 0.1 (:897-992).
- Sample fails below 0.10 density, or when `density*100 < 32 - (surveying/20)*6` (:1060-1079).
- Units = `density*(25+random(3)) * surveying/100`; the gamble or a rich node multiplies this by 5; under 2 units counts as a trace amount (:1094-1133).

**Harvester (installation)**, in `src/server/zone/objects/installation/InstallationObjectImplementation.cpp`:
- Start is refused when density < 0.10, when power is needed and there is none ("power_deposit_incomplete"), or when maintenance is needed and there is none ("harvester_no_maint_4") (:76-107).
- Maintenance is paid at `elapsed/3600 * maintenanceRate`, and power is spent at `elapsed/3600 * basePowerRate` while the harvester is active. Running out cuts the work time short and shuts it down (:272-328). Negative maintenance becomes condition damage (:757-758).
- Hopper gain = `floor((elapsedSec/60) * spawnDensity * extractionRate + remainder)`, capped at `hopperSizeMax - hopperSize`, and worked only up to the spawn's expiry (:383-402).
- It shuts down when the hopper is full or the spawn has expired. Expiry sends "harvester_resource_depleted"; no spawn sends "harvester_no_resource" (:365-371, 420-428).
- The displayed rate is `extractionRate * spawnDensity` (:733-740). Density is fixed when the resource is selected (:150-199).

Power from the player's inventory = sum of `qty * max(1, PE/500)` over energy and radioactive stacks (ResourceManagerImplementation.cpp:314-339).

**Containers.** MAXSIZE is 999999 (`src/server/zone/objects/resource/ResourceContainer.idl:20`).
- Examine shows `resource_contents` as `qty/999999` (`ResourceContainerImplementation.cpp:12-25`).
- `setQuantity` above the max moves the excess into a new container in the same parent (:41-92).
- split (:94-133, 135-166); combine adds the quantities and destroys the source (:168-177).
- Sampled units go onto an existing stack of the same spawn name; anything past 999999 goes into a new container. A full inventory gives "no_inv_space" (ResourceSpawner.cpp:1171-1233).

**Per-planet lists.** The tree is read from `datatables/resource/resource_tree.iff` (`resourcespawner/resourcetree/ResourceTree.cpp:32`). The Lua comments say the Hoth (52) and Ossus (45) native types live in the merged tree inside local_planets.tre, and that the `_hoth`/`_ossus` substring is the zone restriction (resource_manager.lua:47-50, 127-149).

## 3. What a bot test should check
- **Spawned:** the server log shows "Resource Map Built with N resources" (ResourceSpawner.cpp:309-311) and the pool lines with Spawned > 0. On the planet, a survey tool's resource list shows only in-shift spawns of that tool's type (:858-895). For Hoth/Ossus, expect one `*_hoth` / `*_ossus` spawn per minimum-pool entry. Setup: tre archive in place, zone in activeZones.
- **Shifted:** set `averageShiftTime` low, or call the despawn path (ResourceManagerImplementation.cpp:461-474, which sets despawned to now-1 and shifts). Then check that the old name is gone from the zone list and the same pool slot has a new name. The old name should still resolve globally.
- **Harvested:** first place the harvester at a point with survey density ≥ 0.10, select the spawn, add power and maintenance, and activate. After T seconds, read the hopper quantity: it should be about `T/60 * density * extractionRate`, read from the operator's delta updates (updateHopperSize / updateExtractionRate, :143-147, 192-196). Also check that power and maintenance drop by rate × hours.
- **Stacked:** sample twice the same spawn and confirm there is one container whose quantity equals the sum. Then split N and confirm two objects whose quantities add up to the original.

## 4. Likely reasons a test sees no effect
- Density below 0.10 at the spot, or a low surveying skill.
- The harvester has no power or maintenance, its hopper is full, or its spawn has expired.
- The merged resource_tree.iff is missing, so the log shows "Resource type not found" (ResourceSpawner.cpp:588) and "Couldn't spawn resource type in ...".
- The planet was added after the galaxy-wide spawns were created and `backfillZones` was not set.
- Shifts run only every 2 h and spawns last for days, so a restart does not re-roll anything.
- `extractResource` only counts units and never depletes the spawn (ResourceSpawnImplementation.cpp:221-224), so "depletion" cannot be observed.
- Changing posture cancels sampling (ResourceManagerImplementation.cpp:52-81).
- Hopper work is only computed when `updateInstallationWork` runs (:264-270), so the hopper may look stale until it does (inferred).

## 5. Open questions
- `HarvesterObjectImplementation.cpp` was not read, so the source of extractionRate, hopperSizeMax and the base power and maintenance rates is unconfirmed (probably the templates, inferred).
- `ResourceTree.cpp` was not read beyond its iff path, so minpool/maxpool parsing, how excludes match, and the `_hoth` substring restriction are unconfirmed.
- `ResourcePool.h:104-105` reads `includes.getStringAt(1)` and not the inner table; whether that reads each entry correctly depends on LuaObject, which was not checked.
- No use of `maxSpawnAmount` (maxSpawnQuantity) was found in the files read.
- `totalUnits` / `unitsHarvested` in SpawnDensityMap appear never to be updated.
- Whether `System::random(n)` includes n was not checked.
- The GM command names that call `listResourcesForPlanetOnScreen`, `despawnResource` and `healthCheck` were not traced.
- The script-loaded spawns from `resource_manager_spawns.lua` are created already expired (ResourceSpawner.cpp:377); their purpose was not confirmed.


## ChatGPT's review (2026-10-18 02:27)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) (this topic has no `src/` snapshot); no in-game checks. The original draft remains above; corrections below take precedence.

**Holds:** pool/shift design, 6-22/13-22/6-11 day base lifetimes, throttling==90 uniform path, deterministic map density, 999999 default stack maximum and harvester minutes*density*rate basis hold (ResourceSpawner.cpp:696-738; ResourceSpawnImplementation.cpp:144-200; SpawnDensityMap.h:106-148; ResourceContainerImplementation.cpp:41-91; InstallationObjectImplementation.cpp:272-433).

**Corrections/current changes:**
- Current activeZones has 13 zones including hutta, not 12 (resource_manager.lua:51-55). Old line references have shifted; the configuration values at 70-93 still support scale 10, 2 h shift, one-day unit, throttling 90 and gate 1000.
- Survey tools expose 3x3, 4x4 or 5x5 grids, not 'up to 6x6' (SurveyToolImplementation.cpp:150-159).
- Sampling units include staged integer truncation, samplingMultiplier and city samplesize; gamble success is a one-in-three random(2)==1, not a guaranteed fivefold bonus (ResourceSpawner.cpp:1094-1122).
- Density is refreshed on activation as well as selection (InstallationObjectImplementation.cpp:82-88). Maintenance is charged even while inactive; only power has the isActive gate (282-305). Hopper capacity is clamped BEFORE extractionRemainder is added (392-402); the draft's floor-then-cap formula is an approximation near capacity.
- Stack overflow is not guaranteed to be preserved: ignoreMax bypasses the split, no parent cannot receive excess, and failed transfer destroys the new overflow object (ResourceContainerImplementation.cpp:57-78). Test quantity conservation, not merely presence of a second stack.
- Peak-density numbers are map amplitude bounds, not a guarantee a sampled coordinate achieves that peak (SpawnDensityMap.h:106-114,136-148). Resource quantity extraction does not by itself end the time shift.

**Not established:** installed archive data, currently active spawn counts and current hopper/runtime accounting. The draft's destructive shift/config test suggestions were not executed.

**Verdict:** Useful source overview with corrections to current zones, grid size, sampling, maintenance, hopper rounding and overflow guarantees; runtime untested.
