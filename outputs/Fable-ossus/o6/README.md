# Ossus O6: the owner's pass — scorch and craters, settlement fields, points of interest — Fable, 15 Oct 2026

Design only; nothing under `/opt/swg` written, nothing built. Owner, 15 Oct (question 1): keep the O1 layout; add scorch
marks and craters to the academy ruins for the 130 ABY attack; add some flat areas for player settlements (terrain flatten
layers, outside the no-build circles); add as many lore-friendly points of interest as possible. Caves stay on the hillsides
until the owner looks. **Creature levels are not touched** (owner question 2: shelved; Ossus keeps 6–19). Coordinates are
x east / y north in metres from `Fable-ossus/out/ossus-sites.json` and the O1 layout; heights are the terrain survey's.
Everything named here is stock or MTG art referenced by template path, or our own terrain data; exact template paths marked
*(confirm)* are to be resolved against the merged CRC table by Claude before the snapshot is written.

## 1. The 130 ABY attack on the academy: scorch marks and craters

The Massacre at Ossus (130 ABY, `Documentation-support/legends-timeline-njo-legacy.md`): Krayt's Sith and Imperial forces
struck the Jedi academy from orbit and on the ground; the survivors scattered. Eight years on, the benchland still shows it.

**Terrain (`ossus.trn`, new layers after the Academy ruins pad, before the road):**

| layer | where | what | how (Core3 and client both read these) |
|---|---|---|---|
| **Impact craters** x5 | (1870, 2930) r 22; (2140, 2790) r 18; (2010, 3010) r 14; (1930, 2700) r 12; (2210, 2920) r 9 | bowls 2–4 m deep with a raised lip | `BCIR` boundary, feather 0.6; `AHCN`-relative height −3.5 / −2.5 / −2.0 / −1.5 / −1.0 m with an inner `BCIR` r+4 at +0.4 m for the lip; shader `ACCN` to a dark burnt ground (candidates: the Mustafar ash shaders `shader/must_ash_*` *(confirm)*, else Dathomir's black rock) ; `AEXC`-free (keep flora off with the family's density, not an exclusion) |
| **Scorch fans** x4 | from each large crater, a 40–60 m streak toward the south-west (the attack came from orbit at a low angle) | black ground fading out | `BPOL` polygon (a long triangle), feather 0.8, shader `ACCN` dark; radial `ARCN` off so no grass tufts grow on the burn |
| **Glass pan** | (2016, 2848) the ruins pad itself, r 60 | a sheen where the main hall stood | shader `ACCN` to a smooth light stone (the limestone family already in the file) with a `FSHD` filter so it only overrides the meadow; keeps the pad flat (170.4 m) |
| **Rubble apron** | r 60–130 around the pad | the flora family switched to the rock family (no flowers) | `ACRF` radial/flora off inside, rocks on |

All five craters sit inside the ruins no-build circle (r 260) so no player can build in them; none touches the road end.
Height check rule: the ruins pad is flattened to 170.4 m by an earlier layer; craters come **after** it in layer order so
they cut the pad, and the survey (`tools/ossus_terrain.py` probes) must show the lip under 0.6 m so a player can walk in.

**Snapshot (`ossus.ws`, add to the 31 ruin statics):** blast debris: `shared_debris_*` stock piles *(confirm names; Endor and
Corellia have `object/static/structure/general/shared_debris_*`)*, 3 per large crater; two **fallen Jedi temple pillars**
(already in the set) knocked outward from the pad centre; a **downed Imperial drop-pod or shuttle**: the stock crashed-ship
statics (Tatooine's `shared_crashed_ship_*` or Dantooine's crashed escape pod *(confirm)*) at (2160, 2700), yaw 30, half in
the crater lip; **blaster scoring** cannot be painted on stock walls, so scorched walls are the Gungan and Tatooine *ruined*
wall variants already used for the outer courts, moved closer. A **memorial**: six standing stones in a ring at (1960, 2780)
(stock `shared_marker_*`/Dantooine standing stones *(confirm)*), one per Master who fell; no names on them (players will
write their own).

## 2. Settlement fields (terrain flatten layers, outside every no-build circle)

The no-build circles today: Knossa r 320 at (0, −3600); the ruins r 260 at (2016, 2848); three caves r 120 at (−2976, −4960),
(4896, −4960), (1376, 5920); the four edge strips. The survey already measured four flat-ish sites for camps; three are far
from the circles and become settlement fields, plus two new ones chosen on the plain where the height survey is gentlest
(the lake shore and the Knossa east plain). Each field is a `BCIR` + `AHCN` flatten (feather 0.5 over the outer 100 m), no
flora inside, meadow shader, and a **CITY-eligible** radius so the Politician can found a city on it.

| field | centre | r | flattened to | why here |
|---|---|---|---|---|
| **Westmarch** | (−5344, 96) | 400 | 46.0 m | the survey's flattest plain site (spread 3.1 m over r 60); grass plains, 1.7 km from the lake |
| **North Reach** | (−3744, 5792) | 350 | 49.0 m | north hills, near the forest east spawn area but outside it; a hunter town |
| **Rim Mesa** | (3232, −2656) | 300 | 104.0 m | canyon-rim mesa (spread 1.3 m): a view town above Imhar Canyon; the mesa raise exists already, the flatten only trims it |
| **Lakeshore** | (−3000, 1700) | 350 | 44.0 m | the plain east of Adega Lake (water 38.5 m): 5.5 m above water, the lake in view; re-survey first (not in the sites file) |
| **Knossa Fields** | (1500, −3300) | 450 | 50.0 m | 1.5 km east of the starport, same plain height as the pad (50.3): the commuter town; must stay outside the Knossa no-build (r 320) and the pad clearing (r 300) |

Regions: each field gets a `{"ossus_field_<name>", x, y, {CIRCLE, r}, SPAWNAREA-free}` row is **not** needed; the fields are
ordinary ground. What they need is to be left out of the no-spawn list (so lairs still come near, as on stock planets) and a
map label (`ossus_region_names.stf` + `clientregion` rows) so the owner can find them: "Westmarch", "North Reach", "Rim Mesa",
"Lakeshore", "Knossa Fields".

## 3. Points of interest (Legends, in the 138–139 ABY state)

Each: where, what it is made of, what a visitor finds. Fauna levels unchanged; NPCs noted as roles only. Sources are
Wookieepedia (Legends) articles on Ossus, the Great Jedi Library, the Ysanna, Knossa, the Ossus Project and the Massacre;
our text is our own.

| # | POI | Era state | Location idea | Made of (stock / MTG) | What a visitor finds |
|---|---|---|---|---|---|
| 1 | **The Academy ruins and the glass pan** | destroyed 130 ABY | the benchland pad (2016, 2848) | section 1 | craters, the memorial ring, the drop-pod; the entrance to #2 |
| 2 | **The hidden sanctuary** (owner: where the rare Jedi are met) | in use, secret | under the ruins: a cave interior reached by a door static behind the fallen main hall; interior = the stock Dantooine Jedi-temple-style cave `.pob` or `thm_all_cave_s01` reskinned by its own lighting | `shared_cave_01` placed with its mouth inside the rubble apron, or a cellar `.pob` from the stock bunker set *(confirm)* | a quiet cell set: meditation mats, a holocron pedestal (stock `shared_holocron_*` decor *(confirm)*), a healer NPC; the rare hidden Jedi encounter spawns here only |
| 3 | **Krayt's garrison, Knossa** (owner: Imperial garrison, yes) | holding Ossus since 130 ABY; after Krayt's death (138) the commander's loyalty is in question | the plain east of Knossa, (600, −3300), inside the no-spawn ring edge | stock Imperial outpost pieces (`object/building/military/shared_military_guard_tower`, `shared_military_outpost_*`, the Hoth-style prefab shelters we already place) *(confirm)* | an Imperial officer with a GCW-neutral conversation (the Empire here answers to Nihl's regency and knows it); patrols on the Knossa road; a bounty board with Jedi "sightings" that lead nowhere |
| 4 | **The Great Jedi Library's vaults** | destroyed in 3996 BBY (Exar Kun's supernova), buried, partly dug out by the New Jedi Order (36 ABY onward), abandoned again | the limestone summits south of the benchland, (2300, 1900), a mouth on the north face | the third stock cave (`cave_02` flatland variant) + Dantooine temple pillars half-buried at the mouth | a dig camp (tents, crates, a lamp post), a scholar droid, shelves with "Deciphered fragment" datapads (collection items, F93 collections first); a locked vault door the Jedi quest opens later |
| 5 | **Ysanna hunting camp** | the Ysanna (Force-sensitive descendants of Jedi who survived the supernova) still hunt the highlands | highland band south, (−1200, −5200), 180 m | the stock Tusken/Dantari-style camp statics (hide tents, racks, a fire) | Ysanna hunters (neutral; attack if attacked), a shaman who sells nothing but talks; a "beast of the highland" hunt mission from the camp |
| 6 | **Ysanna stone circle** | ancient, in use | a ridge above #5, (−900, −5600), 230 m | standing stones + a fire pit + bone totems | a dance/ritual at night (Ysanna NPCs loop an emote); a Force-sensitive player feels a system message |
| 7 | **The Ossus Project fields** (the Yuuzhan Vong terraforming, 127–130 ABY, sabotaged by the Sith to start the Sith–Imperial War) | the shaped plants ran wild and were burned; some still grow | the forest east, (1400, 4900) | MTG/stock Kashyyyk Vong statics if the merged table has them *(confirm `shared_vong_*` names)*, else twisted Dathomir trees and coral-like Mustafar rocks | a quarantine fence with Imperial warning signs; **Nei Rin's shaper hut** (a damutek-like dome) locked; the voxyn-line tame concept (owner, 15 Oct) starts here later |
| 8 | **Adega Lake fishing hamlet** | civilian survivors of Knossa | the lake's east shore, (−2900, 1300) | Dantooine farmstead set (a small house, a dock of Naboo pier pieces, nets) | a fisher who sells bait and one lake-fish schematic; the only place on Ossus with a "quiet life" dialogue; the Lakeshore field (#2 above) is next door |
| 9 | **Kathracite adit** (the Adega system's crystals, Legends: the Adegan/Ilum crystal family) | worked by a Hutt-backed crew since the Empire pulled its miners | a canyon wall in Imhar, (4500, −300), floor 44.5 m | the stock mine entrance static + ore carts + a lamp string; the cave mouth is a flatland cave | a foreman (Hutt-run operation: ties to the S7 Hutt launch), a crafting station, the resource spawn zone for the five adegan grades already in the tree (R3), no quest yet |
| 10 | **Imhar Canyon crossing** | old road | the canyon's narrowest point, (4300, −700) | Naboo or Corellian bridge pieces *(confirm a static bridge exists; else a rope-bridge of `shared_platform_*`)* | a shortcut from the mesa field to the adit; a bandit ambush spawn under it (levels as the canyon group) |
| 11 | **Knossa old town** | partly abandoned | around the starport pad, inside the city circle | Tatooine/Dantooine filler blocks, half of them the ruined variants, a market street of merchant tents | the artisan and entertainer terminals (as Hoth), a junk dealer, a cantina (stock Dantooine cantina), the Imperial recruiter at the pad only |
| 12 | **The Jedi memorial road** | after 130 ABY | the 16-piece Knossa -> ruins road: a marker every 480 m (16) | small standing stones or lamp posts with a datapad each | a walk that tells the attack in sixteen datapad lines (ours), a badge at the end (ties to the Hoth badge pattern) |
| 13 | **Eocho watch ruin** | ancient Jedi watchtower, long ruined | a summit on the Eocho range south, (300, −6400), ~300 m | Dantooine temple base + one pillar, Yavin-style tower stub *(confirm)* | the best view on Ossus; a surveying "vantage" waypoint; nothing hostile |
| 14 | **Sith interrogation post** | 130–138 ABY; emptied in a hurry when Krayt fell | the west foothill cave (−2976, −4960) interior | the cave's cells dressed with stock Imperial crates, a cage, a terminal | datapads with the names redacted; a "something still lingers" dark-side ambient; the first lead toward the owner's Krayt raid chain (`Documentation-support/krayt-raid-design.md`) |
| 15 | **Crashed Alliance Remnant fighter** | 138 ABY skirmish | the north plains, (−1500, 5200) edge of the spawn area | the stock crashed X-wing/A-wing static *(confirm `shared_crashed_*`)* | a pilot survivor (neutral) who wants a part fetched from #9's crew; a 10-minute errand |
| 16 | **Ysanna sky-burial cliff** | ancient custom | canyon country north rim, (5000, 900) | bone totems, a wooden platform | ambient only; a lore datapad |
| 17 | **Supernova glass plain** | 3996 BBY; still barren | the south-west highland between the two foothill caves, (0, −5500) | terrain: a `BPOL` with the limestone shader and flora off, 600 x 300 m; no statics | an empty, glassy plain with a wind sound (environment family `ossus_mountains` row with no music); surveyors find the solar-energy PE floor raised here (R3 Q4) |
| 18 | **The Hutt landing field** | new under the Hutt-run adit | a flat on the Rim Mesa field's north edge, (3400, −2300) | the Tatooine Hutt businessmen camp set (`shared_tatooine_hutt_businessmen_camp_medium.iff`, verified to exist in the client) | a Hutt broker NPC on `object/mobile/hutt_male.iff` (the player Hutt's own body, so he doubles as the Level 1 animation test subject), kathracite buyers, the S7 floater deed vendor if the owner picks "vendor" |

Order of building: 1–3 (they are the owner's story point), then 11 and 12 (the Knossa road already exists), then 4, 5, 9,
18 (they tie into collections, resources and the Hutt launch), then the rest as snapshot-only dressing. Every static and
building needs its server template in dev (`dev_check.sh` pattern from O2) and its `.pob` in the client; the sanctuary (#2)
and the vaults (#4) are the only pieces with interiors.

## 4. What Claude builds

1. `ossus.trn`: the crater/scorch/glass/apron layers (section 1) and the five flatten layers (section 2), re-surveyed with the
   O1 report (`tools/ossus_terrain.py build` then the probes: pad spread, crater lip < 0.6 m, each field spread < 1.5 m).
2. `ossus.ws`: the section 1 statics now; POIs 1–3, 11, 12 in the next pass; the rest by batch.
3. `ossus_regions.lua`: nothing removed; add the five field labels to `clientregion` + `ossus_region_names.stf`; the garrison
   (#3) sits inside Knossa's no-spawn ring so its NPCs are placed by screenplay, not spawn area.
4. Strings (ours): region names, 16 road datapads, memorial text, warning signs.
5. The owner looks at the craters and one field before the POIs are placed (the client decides crater depth and lip).

## Owner questions

1. Crater depth 2–4 m with a 0.4 m lip, or shallower for walking?
2. Five fields: keep all, or start with Westmarch and Knossa Fields?
3. The garrison east of Knossa (inside the no-spawn ring, patrols on the road) or on the benchland rim overlooking the ruins?
4. POI #7 (the Vong project fields) now, or hold until the voxyn-line decision has content behind it?
