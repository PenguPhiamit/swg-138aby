# Echo Base on our Hoth: plan only — Fable, 14 Oct 2026

What a Rebel base could be in pre-CU terms on MTG's map. Nothing staged. Sources read as text only: the client archives
(our own readers; the merged CRC table in `local_planets.tre`), MTG's `terrain/hoth.trn` and `snapshot/hoth.ws`, SWGFlurry
(`Thrax989/SWGFlurry`, AGPL-3.0 in `LICENSE` and `MMOCoreORB/COPYING`), Bellum Gero (AGPL-3.0), Core3-dev, and the
setting policy (`setting-and-encounter-policy.md`: era 130–138 ABY; Echo Base may be "ruins, a recovered site or a
newly repurposed base", never the film garrison unchanged). Text here is ours. Numbers are mine unless a source is named.

## 1. What the client already has

**MTG prepared the site in the terrain.** `hoth.trn` has an `echobitmap` layer over the rectangle x -7000..-3200,
y 3200..7000 that raises a massif from `terrain/echo_base.tga` (peak about 304 m at -5375, 5125; the snow plain around
it is 15–30 m, the plateau east of it 82–93 m) and an `echobaseexclusions` layer with three terrain cut-outs named
**hangar** (-5300, 5690, on the north flank at 118 m), **main** (-5050, 5410, east flank at 85 m) and **tower**
(-5036, 5106, 185 m). Those are the openings of the NGE Echo Base building; MTG's snapshot does not place the building
(94 objects: starport, cloning facility, warehouse, four caves, debris, a camp). SWGFlurry's Hoth puts its `echobase`
region at (-5100, 5100), radius 2,000: the same site, so the same terrain lineage.

**The NGE heroic assets are in the MTG archives** and in the merged CRC table: `object/building/heroic/shared_echo_base.iff`
(mtg_patch_019) with its interior `appearance/echo_base_pob.pob` (mtg_patch_016; 33 rooms including the tauntaun
grounds; collision floors for every room), its doors, elevators, lifts, hatch, signs, tubes and wires as separate
props; `shared_hoth_generator.iff` and `shared_hoth_generator_destroyed.iff` (the shield generator, intact and as a ruin);
`shared_hoth_ion.iff` (the ion cannon); `shared_hoth_rebel_transport.iff`; `shared_frozen_tauntaun.iff` (already in two of
our caves); `object/intangible/vehicle/shared_hoth_at_st_pcd.iff`. Core3-dev already registers the three Echo Base door
templates (`object/custom_content/tangible/door/echo_base_door_{small,large,hangar}.lua`) and the `echo_base_token`
loot item. Nothing of this has been drawn by our client yet: the files are NGE-era and MTG's own Hoth never placed them.

**Stock pre-CU buildings with interiors, the safe set:** `military/shared_military_base_shed_rebel_style_01`,
`shared_military_base_shed_rebel_abandoned_01`, `shared_military_outpost_guard_house_rebel`, `shared_military_base_gate_house_rebel`,
`shared_military_base_police_station_rebel_style_01` (and its abandoned twin), `general/shared_bunker_rebel_01` (a
bunker dungeon), `shared_bunker_rebel_weapons_depot`, `shared_rebel_fuel_depot`, `shared_bunker_rebel_deep_chasm`,
`shared_bunker_rebel_spynet`, `base/shared_base_hangar`, `base/shared_base_military_building`, the player GCW
headquarters `faction_perk/hq/shared_hq_s01..s05_rebel`, plus the stock snow props and the ice caves' stalagmites.

## 2. What other servers did

- **SWGFlurry:** Echo Base is a separate instance zone, `dungeon2`, with its own snapshot (cell ids 14201113–14201144;
  the snapshot is not in our scripts-only checkout, so their positions cannot be reused). `dungeon/hothechobase.lua`
  places 35 NPCs by room (command room with General Rieekan, computer room, reactor room, corridor, storage, medbay,
  tauntaun grounds, a wampa cell) with the ordinary `spawnMobile(zone, template, respawn, x, z, y, heading, cell)`;
  two elevator terminals and an "Exit Dungeon" NPC use `createObserver(OBJECTRADIALUSED, ...)` and `switchZone` to
  teleport; `hoth/hoth_echo_base.lua` on the planet itself is an empty shell. Same Core3 screenplay API as ours; the
  work in a port is the mobiles (film characters: Rieekan, Derlin, Hobbie, Dack, Wedge, Luke, Vader; wrong for our era)
  and the missing snapshot. Licence AGPL-3.0, credit required for anything adapted.
- **Bellum Gero:** no Echo Base. Region names for a "shield generator battlefield" (5420, 780, r 450) and "generator
  ridge", shuttleports, turrets and a Rebel shuttle at their outposts, the glacial rancor world boss; their heroic
  server templates cover the frozen tauntaun only.

## 3. The site

MTG's massif at about (-5400, 5300): 9 km north-west of the Scavenger Starport, 5.2 km from the centre of the Rebel
patrol zone (-2500, 1000) and 4.9 km from the Rebel Forward Camp (-2800, 1200). The east plateau (x -4900..-3900, y 4600..6100) is flat at
82–93 m and takes an outpost; the west plain (15–30 m) is open ground for a battlefield. Travel: `travel.iff` already
has a Hoth → Hoth fare (100 credits), so a second travel point there works with a planet_manager entry and a stock
shuttleport building; without it the base is a long tauntaun ride.

## 4. Batches (same shape as the Hoth batches; effort is mine, test-galaxy time not included)

| Batch | What | Effort | Needs the owner |
|---|---|---|---|
| E0 Look | Place `shared_echo_base.iff` once with a screenplay `spawnSceneObject` at the cut-outs (origin and heading fitted to the hangar, main and tower polygons from the pob's portal geometry with our ws/pob readers) and look at it in the real client: does a pre-CU client draw an NGE heroic building and its 33 cells? The go/no-go for everything below. | 1 day | a client session |
| E1 Shell | Go: the building in `snapshot/hoth.ws` (local_planets.tre) plus server template `object/building/heroic/echo_base.lua`, door/elevator/lift props, no-build and named region, map marker "Echo Base" (sites.tsv row). No-go: the stock set instead: `shared_bunker_rebel_01` dug into the east flank at the main cut-out as the interior, sheds, gate and guard houses on the plateau. | 1–2 days | the era story: ruin, recovered or repurposed |
| E2 Outside | The plateau outpost: generator (intact or destroyed, by story), ion cannon, rebel transport, fuel depot, trench props from the stock military set, a shuttleport travel point, a no-spawn circle, the west plain as "Generator Field" with a skirmish like Contested Ground. | 1 day | shuttleport yes/no; faction labels (Alliance heirs vs Krayt-era Imperials) |
| E3 Inside | Screenplay in our caves/camps style: roster by room (hangar, command, computer, reactor, corridor, storage, medbay, tauntaun grounds, wampa cell), on our `hoth_*` mobiles (rebel snow soldiers and sergeants, snowtroopers, wampas, mynocks, scavenger raiders) with 3–4 named bosses at caves' levels; elevators with stock `terminal_elevator_up/down`; corpse loot through the hoth_* groups and the `echo_base_token` hook. | 2 days | who holds the base now |
| E4 Missions and GCW | Terminal missions and a Vell-style chain (recover the base's records, clear the lower levels, hold the generator); optional GCW: a `faction_perk/hq` Rebel HQ run by Core3's GCW manager, or none. | 1 day | GCW on at the base or not; which factions |
| E5 Names | Keys in `hoth_region_names`, POI and label rows through `stage_hoth_names` (sites.tsv), a `clientpoi` description, loading-screen text if wanted. | ½ day | names |

Risks: the NGE building in a pre-CU client (E0 decides; MTG shipped the files but never placed them); the pob's 33
cells and the server's navmesh for a building that size; film-era names and characters (policy says no); the 9 km
distance (E2's shuttleport). The stock-set fallback has none of these and is a two-day build.
