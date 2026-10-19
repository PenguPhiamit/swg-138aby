# Hoth Game Mechanics Report

## 1. Short Answer

Hoth contains four named ice caves (frostfang_cavern, icemaw_den, snowblind_lair, matriarch_cavern) each spawning regular wampas and one boss wampa variant with a 30-minute respawn; a separate mynock den at -2000, -4800 with 23 ice mynocks and a broodmother boss (also 30 min respawn); and a glacial rancor at 600, -4600 with a 30-minute respawn. Five camps (imperial_forward_camp, rebel_forward_camp, scavenger_camp, raider_camp, contested_ground) each have static props and NPCs respawning every 5 minutes. Echo Base is a single building at -5112.8, 37.6, 5096.6 with no NPCs. The Scavenger Starport outpost (0, -2000) has two mission terminals, artisan/entertainer terminals, and imperial/rebel recruiters. Quartermaster Vell at the outpost offers a three-mission salvage chain (retrieve → assassinate → deliver) rewarding 1500, 3000, and 2000 credits respectively plus loot and badge bdg_thm_park_hoth_salvage.

## 2. How It Works

### Regions
- The outpost is a CITY region at 0, -2000 with 200 m radius; no spawns inside (hoth_regions.lua:13). A 300 m NOBUILDZONEAREA surrounds it (line 14).
- Ice caves are grouped in a NAMEDREGION at -400, 2600 with 450 m radius (line 17).
- Named places (frostfang_cavern, icemaw_den, snowblind_lair, matriarch_cavern) each have a 40–60 m NAMEDREGION circle; no spawns or build rules (lines 35–38).
- Camps and zones are defined as SPAWNAREA circles with max counts: imperial_forward_camp (2600, -3900, 1200 m, 48), rebel_forward_camp (-2800, 1200, 1200 m, 48), scavenger_camp (-1500, -3200, 900 m, 48), raider_camp (-1200, -3600, 900 m, 48) (lines 39–42).
- Mynock den is a NAMEDREGION at -2000, -4800 (60 m radius) with a surrounding NOSPAWNAREA of 160 m (lines 54–56). Rancor grounds is a NAMEDREGION at 600, -4600 (200 m radius) (line 55).
- Echo Base has NOBUILDZONEAREA + NOSPAWNAREA at -5113, 5097 with 750 m radius (line 58).
- A world spawner covers the rest of the map with up to 1024 mobs from hoth_world (line 61).

### Ice Caves (hoth_ice_caves.lua)
- Four caves are hardcoded: cave_04_ice at -385, 2436 (icemaw_den), cave_02_ice at -543, 2674 (snowblind_lair), cave_01_ice at -622.5, 2292.3 (frostfang_cavern), cave_03_ice at -75, 2969 (matriarch_cavern) (lines 28, 63, 98, 133).
- Each cave spawns regular hoth_wampa with 420 s respawn (e.g., lines 30–31, 65–66, 100–101, 135–136) and one boss variant with 1800 s respawn: hoth_wampa_icemaw (line 60), hoth_wampa_snowblind (line 89), hoth_wampa_frostfang (line 130), hoth_wampa_patriarch (line 159).
- Bosses are accompanied by two hoth_elder_wampa guards with 420 s respawn each (e.g., lines 61–62, 90–91, 131–132, 160–161).
- The screenplay starts on zone load if "hoth" is enabled (lines 21–25).

### Mynock Den (hoth_mynock_den.lua)
- Spawns the cave building object_.../cave_06_flatland_s01_ice.iff at -2000, 44.8, -4800 (lines 13, 52).
- Validates the cave has 11 cells; prints an error if not (lines 59–63).
- Spawns 23 hoth_ice_mynock and hoth_greater_ice_mynock with 420 s respawn, plus one hoth_mynock_broodmother boss at cell 11 with 1800 s respawn (lines 17–39).
- Cells are looked up by number from the spawned building (line 67).

### Glacial Rancor Den (hoth_glacial_rancor_den.lua)
- Spawns one hoth_glacial_rancor at 600, 26.4, -4600 with heading 180 and 1800 s respawn (lines 11–12, 19).

### Camps (hoth_camps.lua)
- Five camps spawn scene objects (walls, tents, campfires, crates, ATST debris) and NPCs:
  - imperial_forward_camp at 2600, -3900: 6 hoth_snowtrooper + 1 hoth_snowtrooper_sergeant (lines 23–29, 63–69).
  - rebel_forward_camp at -2800, 1200: 6 hoth_rebel_snow_soldier + 1 hoth_rebel_snow_sergeant (lines 32–38, 71–77).
  - scavenger_camp at -1400, -3300: 5 hoth_scavenger + 1 junk_dealer (lines 40–48, 79–84).
  - raider_camp at -1200, -3600: 6 hoth_scavenger_raider (lines 50–53, 86–91).
  - contested_ground at 2400, 200: 4 hoth_snowtrooper + 1 hoth_snowtrooper_sergeant + 4 hoth_rebel_snow_soldier + 1 hoth_rebel_snow_sergeant (lines 55–57, 93–102).
- A salvage_detail at -100, -1960 spawns 3 hoth_imperial_salvage_tech and 2 hoth_snowtrooper (lines 104–108).
- All camp NPCs have 300 s respawn (e.g., lines 63, 71, 79, 86, 93, 104).

### Echo Base (hoth_echo_base.lua)
- Spawns one heroic building object/building/heroic/echo_base.iff at -5112.8, 37.6, 5096.6 with heading 0 (line 21).
- No NPCs are spawned; the screenplay only calls spawnSceneObjects (lines 14–18, 20–22).

### Outpost Terminals (hoth_outpost_terminals.lua)
- Two terminal_mission.iff at 48, 0, -1996 and 48, 0, -2002 facing west (lines 22–23).
- One terminal_mission_artisan.iff and one terminal_mission_entertainer.iff at 48, 0, -1990 and 48, 0, -1984 (lines 25–26).
- Imperial recruiter at 54, 0, -2016 and rebel recruiter at 54, 0, -1980, both with 60 s respawn (lines 31–32).

### Scavenger Quartermaster Task (scavenger_quartermaster.lua)
- Quartermaster Vell (hoth_quartermaster_vell) spawns at 44, 0, -2010 with AI_STATIC flags (line 74).
- Uses ThemeParkLogic framework with planetName "hoth" and distance 600 (lines 81–87).
- Three missions in sequence:
  1. retrieve: Find hoth_salvage_tech_baxx ("Ria Baxx") at the Lucky Despot wreck; two hoth_ice_mynock secondary spawns guard her; item object/tangible/mission/quest_item/power_regulator.iff is retrieved; reward 1500 credits (lines 11–31).
  2. assassinate: Kill hoth_raider_captain_korro ("Thane Korro"); two hoth_scavenger_raider secondary spawns; reward 3000 credits (lines 33–49).
  3. deliver: Deliver object/tangible/mission/quest_item/current_alternator.iff to hoth_salvage_broker_kett ("Doro Kett"); no secondary spawns; reward 2000 credits + lootGroup "hoth_decor_rare" + badge 141 (bdg_thm_park_hoth_salvage) (lines 51–68).
- Dialogue strings are in string/en/static_npc/hoth/scavenger_quartermaster.stf, loaded via getStringId (lines 3–5).
- Conversation handlers: mission_giver_conv_handler and mission_target_conv_handler both reference the ScavengerQuartermaster themePark (lines 91–96).

## 3. What a Bot Test Should Check

### Setup needed
- Ensure zone "hoth" is enabled (checked in each screenplay's start function: hoth_ice_caves.lua:22, hoth_glacial_rancor_den.lua:18, hoth_mynock_den.lua:46, hoth_outpost_terminals.lua:15, hoth_echo_base.lua:15).
- Verify the bot is on the correct planet (planetName = "hoth" in scavenger_quartermaster.lua:85).

### Ice caves
- Teleport to each cave center and verify wampa spawns exist within cell-local coordinates.
- Check boss variants spawn with 1800 s respawn timer vs 420 s for regular wampas.
- Confirm two elder_wampa guards accompany each boss (hoth_ice_caves.lua:61–62, 90–91, 131–132, 160–161).

### Mynock den
- Verify the cave building object spawns at -2000, 44.8, -4800 (hoth_mynock_den.lua:52).
- Check 23 mynock-type mobs exist across cells 1–11.
- Confirm hoth_mynock_broodmother is in cell 11 with 1800 s respawn (line 37).

### Glacial rancor
- Verify one hoth_glacial_rancor at 600, 26.4, -4600 with 1800 s respawn (hoth_glacial_rancor_den.lua:19).

### Camps
- For each camp, check scene objects (walls, tents, campfires) exist at expected coordinates.
- Verify NPC counts and types match the file (e.g., imperial_forward_camp: 6 snowtrooper + 1 sergeant).
- Confirm all camp NPCs have 300 s respawn timers.

### Echo Base
- Verify the echo_base.iff building exists at -5112.8, 37.6, 5096.6 (hoth_echo_base.lua:21).
- Confirm no NPCs are present inside or around the building.

### Outpost terminals
- Check two terminal_mission.iff exist at 48, 0, -1996 and 48, 0, -2002 (hoth_outpost_terminals.lua:22–23).
- Verify artisan and entertainer terminals at 48, 0, -1990 and 48, 0, -1984 (lines 25–26).
- Confirm imperial_recruiter at 54, 0, -2016 and rebel_recruiter at 54, 0, -1980 with 60 s respawn (lines 31–32).

### Scavenger quartermaster task
- Locate hoth_quartermaster_vell at 44, 0, -2010 (scavenger_quartermaster.lua:74).
- Interact to verify three missions are available in order.
- For mission 1: find hoth_salvage_tech_baxx; check two hoth_ice_mynock secondary spawns nearby; confirm power_regulator item is obtained via retrieve (talk).
- For mission 2: locate and kill hoth_raider_captain_korro with two hoth_scavenger_raider guards.
- For mission 3: deliver current_alternator to hoth_salvage_broker_kett; verify reward of 2000 credits, lootGroup "hoth_decor_rare", and badge 141 (bdg_thm_park_hoth_salvage).
- Check system messages for mission acceptance, completion, and rewards.

## 4. Likely Reasons a Test Sees No Effect

- Zone "hoth" is not enabled; all screenplays check isZoneEnabled("hoth") before spawning (hoth_ice_caves.lua:22, hoth_glacial_rancor_den.lua:18, hoth_mynock_den.lua:46, hoth_outpost_terminals.lua:15, hoth_echo_base.lua:15).
- The bot is outside the region boundaries (e.g., outside the 200 m CITY radius for the outpost, or beyond spawn area circles).
- Terrain patch not applied: the mynock den requires terrain flattening in outputs/Fable-hoth-batchB/staged/client/terrain/hoth.trn packed into local_planets.tre (hoth_mynock_den.lua:4–5).
- String file missing: scavenger_quartermaster.stf must be in a tre both client and server load (scavenger_quartermaster.lua:5).
- Echo Base building not in MTG snapshot: the mynock den cave template is noted as not in MTG's snapshot, requiring terrain patching (hoth_mynock_den.lua:1–4).
- Spawn timers not elapsed: bosses respawn after 1800 s; regular mobs after 420 s or 300 s depending on type. If the bot kills and rechecks too quickly, spawns may not have regenerated.
- NOBUILDZONEAREA or NOSPAWNAREA restrictions preventing world spawns near Echo Base (hoth_regions.lua:58) or the outpost (lines 13–14).

## 5. Open Questions

- The scavenger_quartermaster.lua references ThemeParkLogic and conversation handlers but does not include the actual dialogue strings; these live in string/en/static_npc/hoth/scavenger_quartermaster.stf which is not provided (scavenger_quartermaster.lua:3–5).
- No file shows how the three missions are sequenced or what conditions trigger mission 2 after mission 1, or mission 3 after mission 2. The npcMap and ThemeParkLogic framework handle this but the logic is not in these files (scavenger_quartermaster.lua:71–96).
- The file does not show where hoth_salvage_tech_baxx, hoth_raider_captain_korro, or hoth_salvage_broker_kett are spawned; only their templates and names are listed in primarySpawns (scavenger_quartermaster.lua:16, 37, 55). Their locations must be defined elsewhere.
- Echo Base has no NPCs or interior mechanics documented; it is described as a "go / no-go look for E1" (hoth_echo_base.lua:5), so interior access and content are unknown.
- The world spawner hoth_world.lua (referenced in hoth_regions.lua:59) is not provided; its spawn tables, lairs, herds, and patrols are unspecified.
- No file documents how the badge bdg_thm_park_hoth_salvage (badge 141) is awarded or what it displays (scavenger_quartermaster.lua:66).
- The lootGroup "hoth_decor_rare" contents are not defined in these files (scavenger_quartermaster.lua:65).

## ChatGPT's review (2026-10-18 22:35)

Checked Saluki leads and eight snapshots against current Core3-dev 9d08e265. Three supplied copies are stale: Echo Base,glacial rancor and region definitions. Source only, not a Hoth release/visibility acceptance.

**Holds:** four cave sites,regular/elder420-second spawns,mynock-den position/template,300-second camp NPCs,outpost terminals and the three quartermaster reward definitions remain (hoth_ice_caves.lua; hoth_mynock_den.lua; hoth_camps.lua; scavenger_quartermaster.lua:10-96). Saluki's variable-only objections miss values supplied in the same object: mynock caveX/Z/Y at13 and rancor x/z/y/respawn at12-13.

**Corrections:**
- There are **five** named wampa boss spawns across four caves: icemaw60,snowblind89,frostfang130,patriarch159,matriarch220 in bin/scripts/screenplays/caves/hoth_ice_caves.lua. The report misassigns patriarch to the matriarch cave and omits the final matriarch.
- Mynock list has **23 total**, including one broodmother and22 regular/greater, not23 plus a boss (bin/scripts/screenplays/poi/hoth_mynock_den.lua:17-39). It logs when cell count<11, not requires exactly11 (59-70).
- Current glacial rancor respawn is **7200 seconds**, not1800 (bin/scripts/screenplays/poi/hoth_glacial_rancor_den.lua:12-20).
- Current Echo Base spawns its interior population and baron (bin/scripts/screenplays/poi/hoth_echo_base.lua:17-61,72-97). Reject the proposed 'no NPCs inside/around' test; no-NPC is an old snapshot fact.
- Named camp circles are NAMEDREGION only; the wide imperial/rebel/scavenger zones are separate SPAWNAREA entries, not the report's camp-name48-mob circles (bin/scripts/managers/planet/hoth_regions.lua:23-44). Ice-cave region now includes NOBUILDZONEAREA+HARVESTERAREA (18), contradicting no-build-rule prose.
- Echo Base snapshot exclusion is not established by a comment about the **mynock cave**. NOSPAWN areas suppress relevant area spawners, not proof explicit screenplay objects/NPCs cannot spawn. Quartermaster mission definitions alone do not verify ThemePark dialogue, item delivery or badge/loot acceptance.

Verdict: Historical content inventory needs material updates for five bosses,total mynock count,Echo population,rancor timer and region semantics; gameplay/visibility/rewards untested.
