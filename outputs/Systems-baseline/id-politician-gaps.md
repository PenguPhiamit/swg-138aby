# Image Designer and Politician: what Core3 actually implements

Static code reading by Claude, 15 Oct 2026, of `/opt/swg/Core3-dev` at `80b66e65` (upstream SWGEmu Core3 `403893d9`, 1 Oct 2026, plus 64 local commits). Paths are relative to `MMOCoreORB/`. **"Real" means the code exists and looks complete, not that it was tested in game.** Nothing here was run.

Owner's complaint: these two professions "feel very bare bones". Short answer: **in code, neither is bare bones.** Both are close to full pre-CU feature sets. The thin feel most likely comes from three things:

1. **Neither profession has slash commands to speak of.** Image Designer has 0 abilities in `skills.iff` (only the skill mods `hair`, `face`, `body`, `markings`); Politician has 27 abilities, of which 3 are commands. Everything happens through a client UI window (ID) or the city hall terminal's radial menu (Politician). A player looking at the abilities list sees almost nothing.
2. **The real gates are places and time.** ID stat migration only works inside one of 4 salon building types. City progress, taxes and elections run on a **7-day update cycle**, and an election takes **3 updates (about 3 weeks)**. Very little visibly happens in a short test session.
3. **A handful of genuine gaps** (listed below): two of eight city specialisations do nothing, militia have no law-enforcement powers, `/cityWarn` doesn't exist, city guards (`/startCitySpawner`) are a stub, and the server trusts the client on ID colour indices and holo-emote purchases.

---

## 1. Image Designer

### 1.1 How a session works (call chain)

| Step | Where | Status |
|---|---|---|
| `/imagedesign [target]` opens a session | `src/server/zone/objects/creature/commands/ImagedesignCommand.h:19-115` | **real**. Gate is `hasSkill("social_entertainer_novice")` (line 30), not an ID box. Target must be in the designer's group (lines 60-70), alive, visible, not already in a session. No target means design yourself (line 42-43). The salon requirement for starting is commented out (lines 72-89): any ID can design anywhere. |
| Session start: decide whether stat migration is allowed | `src/server/zone/objects/player/sessions/ImageDesignSessionImplementation.cpp:50-109` | **real**. Stat migration is enabled only if both designer and target are inside a `SALONBUILDING` (lines 56-80); a position observer is then registered on both. Sends `ImageDesignStartMessage` to both sides with the target's installed holo-emote. |
| Client sends a change (`0x238`) | `src/server/zone/packets/object/ImageDesignChangeMessageCallback.h:33-59`, registered at `src/server/zone/ZonePacketHandler.cpp:211` | **real**. Parses designer, target, tent, type and the full `ImageDesignData` block. Line 34 has a self-doubting `shiftOffset(4) // ?Not sure this should be here.` |
| Client rejects/cancels (`0x239`) | `src/server/zone/packets/object/ImageDesignRejectMessageCallback.h:40-52`, registered at `ZonePacketHandler.cpp:212` | **real**. Calls `cancelImageDesign`, which echoes the reject to both sides (`ImageDesignSessionImplementation.cpp:415-438`; a `// TODO: Needs research.` at line 435). |
| Update / commit | `ImageDesignSessionImplementation.cpp:111-318` | **real**. Commits only after the designer accepts and (if a different person) the target accepts; otherwise a 2-minute timeout is armed (lines 175-189). |
| Payment | `ImageDesignSessionImplementation.cpp:320-361` | **real**. Takes the larger of required/offered payment, cash first then bank, logged as `TrxCode::IMAGEDESIGN`. |
| Hair style | `ImageDesignSessionImplementation.cpp:225-241`; `src/server/zone/managers/skill/imagedesign/ImageDesignManager.cpp:396-487` | **real**. Checks the `hair` skill mod against the hair asset's required level (line 416), species compatibility (line 419), bald option (lines 401-408), validates the customization string (line 449). A `//TODO: Validate hairCustomization` at line 426 is effectively covered by line 449. Hair is moved into the slot by a delayed task (lines 458-478) to dodge a client bug. |
| Body / face sliders | `ImageDesignManager.cpp:26-151` | **real**. Reads `datatables/customization/customization_data.iff` (lines 331-378). Each slider is checked against the designer's skill mod (line 41), so a novice cannot apply master-level changes server-side. Height scaling uses the species min/max (lines 44-53). |
| Colours (skin, hair, markings, eyes...) | `ImageDesignManager.cpp:153-288` | **partial**. Ranged variables are clamped (lines 187-195), but palette indices are **not** checked against skill level: `validatePalette()` always returns true; the index check is commented out with the note that the client restricts it (lines 489-562, comment at 514-515). A modified client could use master colours with a novice designer. The skill-mod gate at line 231 still applies per customization row. |
| Stat migration | `ImageDesignSessionImplementation.cpp:134-210`; `src/server/zone/objects/player/sessions/MigrateStatsSession.idl:62-84`; commands `RequestStatMigrationDataCommand.h`, `RequestSetStatMigrationDataCommand.h` | **real**, with conditions. Target opens the stat migration window (`/requestStatMigrationData` creates a `MigrateStatsSession`), sets targets (`/requestSetStatMigrationData` checks each attribute against the species min/max and the total, lines 63-84). The ID commits it only inside a salon, after a **4-minute server-enforced timer** (lines 137-171), and gets 2000 ID XP (line 204). Staff and characters in the `tutorial` zone migrate instantly (RequestSetStatMigrationDataCommand.h:86-94). Small bug: line 198 checks the **designer's** salon twice instead of designer and target. |
| `/requestStatMigrationStart`, `/requestStatMigrationStop` | `RequestStatMigrationStartCommand.h`, `RequestStatMigrationStopCommand.h` | **stub** (empty handlers). Harmless: the working path is the two `Data` commands above. |
| Leaving the salon | `src/server/zone/objects/player/sessions/ImageDesignPositionObserverImplementation.cpp:25-31`; `src/server/zone/objects/player/events/ImageDesignTimeoutEvent.h:31-37`; `ImageDesignSessionImplementation.cpp:363-413` | **real**. Walking out queues the timeout; walking back in cancels it; timeout aborts the change. |
| XP | `ImageDesignSessionImplementation.cpp:196-308` | **real**. 100 for hair or cosmetic, 300 for physical, 100 for a holo-emote, 2000 for stat migration; halved when designing yourself. `imagedesigner` XP type. (The `switch` at 268-277 falls through from PHYSICAL to COSMETIC; harmless.) |
| Salons | `bin/scripts/object/building/{corellia,naboo,tatooine}/salon_*.lua` (`gameObjectType = 530`) | **real but scarce**: 4 templates (corellia, naboo x2, tatooine). No player-placeable salon or ID tent deed exists. Whether each salon building is present in the loaded world snapshots was not checked (unsure). |
| ID trainer | `bin/scripts/screenplays/trainers/trainerData.lua:430-`; one placed in Theed (`screenplays/cities/naboo_theed.lua:187`) plus others in city screenplays | **real**. |

### 1.2 Holo-emotes

| Feature | Where | Status |
|---|---|---|
| Buying one | Inside the ID session: `ImageDesignSessionImplementation.cpp:283-297` sets `installedHoloEmote` and 20 charges (`src/server/zone/objects/player/PlayerObject.idl:1913-1916`) | **partial**. The server installs whatever holo-emote name the client sends, including `holoemote_all`, **with no skill check and no price check** (price is whatever the two clients agreed). Pre-CU tied holo-emote sales to ID skill. |
| `/holoemote <name>`, `help`, `delete` | `src/server/zone/objects/creature/commands/HoloEmoteCommand.h:16-191` | **real**. 16 named emotes plus `kitty` alias (lines 165-189), 20 charges, 30-second cooldown (line 103), plays `clienteffect/holoemote_<name>.cef` on the head. Help window lists names. |

### 1.3 Image Designer gaps and fixes

1. **Palette and holo-emote trust** (palette index check off, holo-emote type/price unchecked). Fix: re-enable the commented palette check in `ImageDesignManager::validatePalette` using the designer's ID level, and gate `holoemote_all` / any holo-emote on an ID box. Low-medium effort.
2. **Salon-only stat migration with only 4 salon templates.** Faithful to pre-CU, but on a small LAN server it means one walk to Coronet, Theed or Mos Eisley. Option: an ID tent deed (new structure) or a config switch to allow migration anywhere. Medium.
3. **Gate uses Entertainer novice, not ID novice** (`ImagedesignCommand.h:30`). Entertainer novice can open sessions; the skill mods then decide what actually changes. Matches upstream; fine unless the owner wants ID-only.
4. **Designer salon checked twice** at `ImageDesignSessionImplementation.cpp:198`. One-line fix.
5. **Bot probe:** two grouped agents in a salon; designer `/imagedesign <target>`; change hair and one slider; both accept; then a stat migration after 4 minutes. Assert the target's hair object template and HAM base values changed and the designer got `imagedesigner` XP. Our agent body would need to send `0x238` ImageDesignChange packets: **not yet supported by the agent** (the agent cannot drive this UI today).

---

## 2. Politician and player cities

### 2.1 What the Politician boxes grant (from `skills.iff`, via `outputs/Claude-class-check/professions.json`)

| Box | Abilities | How the server uses them |
|---|---|---|
| Novice | `place_cityhall`, `manage_taxes`, `grantZoningRights` | `place_cityhall`: deed template `abilityRequired`, checked at `src/server/zone/managers/structure/StructureManager.cpp:445-449`. `manage_taxes`: `CityManagerImplementation.cpp:1852,1889`. `grantZoningRights`: a real command (`GrantZoningRightsCommand.h`). |
| Fiscal I-IV | `city_map`; `place_bank`, `place_shuttleport`; `city_spec_industry`; `city_spec_research` | `city_map` at `CityManagerImplementation.cpp:1721`; placement abilities via deed templates (as above); spec abilities checked when choosing a specialisation. |
| Martial I-IV | `manage_militia`; `place_cloning`, `city_spec_cloning`; `city_spec_stronghold`; `place_faction_terminal` | `manage_militia` at `CityManagerImplementation.cpp:1473`; `place_faction_terminal` at `src/server/zone/objects/creature/commands/sui/InstallMissionTerminalSuiCallback.h:61`. |
| Civic I-IV | `installMissionTerminal`; `recruitSkillTrainer`, `place_garage`; `city_spec_entertainer`, `city_spec_doctor`; `city_spec_missions`, `city_spec_sample_rich` | `InstallMissionTerminalCommand.h:31`, `RecruitSkillTrainerCommand.h:31` (both also require mayor, lines 39/41). `hasAbility` is case-insensitive (`AbilityList.cpp:15-27`), so the lower-case checks match. |
| Urban I-IV | `place_streetlamp`, `place_statue`; `place_fountain`; small/medium gardens; large/exotic gardens | `src/server/zone/managers/city/CityDecorationTask.h:68` for lamps/statues/fountains; gardens via deed templates. |
| (all) | `private_place_*` skill mods (9) | **No server reader** anywhere in the repo. They look like client-side markers; the server's real check is the ability. Harmless. |

Politician XP (`political`) comes only from city updates: **750 XP per weekly update to the mayor** (`CityManagerImplementation.cpp:776`) and **300 XP per vote received** at election time (line 1164). The Village XP converter also lists it (`screenplays/village/convos/convohelpers/experience_converter.lua:36`). With weekly updates and 5x sandbox XP, a fresh mayor still needs several real weeks to reach Master unless staff use the city hall "force update" option.

### 2.2 City manager: function by function

All in `src/server/zone/managers/city/CityManagerImplementation.cpp` unless noted. 2481 lines, **1 TODO** (line 2320, a chat refactor note).

| Feature | Function (line) | Status | Notes |
|---|---|---|---|
| Config load | `loadLuaConfig` (64) | real | Reads `bin/scripts/managers/city_manager.lua`. |
| Load cities at boot | `loadCityRegions` (149) | real | `cityregions` database. |
| Found a city | `createCity` (196); `src/server/zone/objects/player/sui/callbacks/PlaceCityHallSuiCallback.h:59-106` | real | Name filter (profane/reserved, lines 59-78), 1024 m spacing from other player cities (`validateCityInRange`, 350) and from NPC cities, unique name (380), per-planet rank caps (`isCityRankCapped`, 225). |
| Citizenship | `registerCitizen` (1405), `unregisterCitizen` (1436); `StructureManager::declareResidence` (`StructureManager.cpp:683-748`); `/declareResidence` | real | Citizen = declared residence inside the city limits. Mails mayor and citizen. |
| New-city grace and assessment | `assessCitizens` (682) | real | City hall is destroyed if the citizen minimum isn't met in the grace period (1440 min). |
| Weekly update | `processCityUpdate` (737) | real | Mayor XP, election check, rank up/down, rescheduling (+0-30 min random), income tax, maintenance. Interval `CityUpdateInterval = 10080` min (7 days). |
| Rank up / down | `expandCity` (1315), `contractCity` (1257); `CityRegionImplementation::destroyAllStructuresForRank` (`src/server/zone/objects/region/CityRegionImplementation.cpp:749`) | real | Radius per rank 150/200/300/400/450 m. Out-of-radius decorations, trainers, terminals and structures are cleaned up (CityRegionImplementation.cpp:1076-1157). |
| Disband | `destroyCity` (1360) | real | |
| Status / citizenship / structure / advancement / maintenance / treasury reports | `sendStatusReport` (427), `sendCitizenshipReport` (646), `sendStructureReport` (485), `sendCityAdvancement` (1594), `sendMaintenanceReport` (1945), `sendTreasuryReport` (1582) | real | |
| Treasury deposit / withdraw | `depositToCityTreasury` (617), `withdrawFromCityTreasury` (531) | real | Withdrawal cooldown 24 h (`city_withdrawal`), staff exempt. |
| Taxes | `promptAdjustTaxes` (1846), `promptSetTax` (1878), `setTax` (1915); `TaxPayMailTask.h:55-80`; `PayPropertyTaxTask.h` | real | All five taxes are wired to a consumer: **income** (weekly from citizens' banks, TaxPayMailTask), **property** (added to structure maintenance, `StructureObjectImplementation.cpp:561-562`, `StructureMaintenanceTask.cpp:79`, `StructureManager.cpp:1015`), **sales** (bazaar/vendors, `AuctionManagerImplementation.cpp:689,1022`), **travel** (ticket price, `PurchaseTicketCommand.h:61`, `PlanetTravelPointList.h:98`), **garage** (vehicle repair, `VehicleObjectImplementation.cpp:238`, `RepairVehicleSuiCallback.h:51`). Each change mails all citizens. |
| City maintenance | `deductCityMaintenance` (845), `collectCivicStructureMaintenance` (963), `collectNonStructureMaintenance` (936), maintenance/decay/destroy mails (1037-1116) | real | Sandbox halves it: `maintenanceDiscount = 0.5` (city_manager.lua:88). |
| Specialisation | `promptCitySpecialization` (389), `changeCitySpecialization` (404); `src/server/zone/objects/player/sessions/CitySpecializationSessionImplementation.cpp:53-60`; `CityRegionImplementation::applySpecializationModifiers` (872) / `removeSpecializationModifiers` (913) | **partial** | The menu lists only the specs whose `city_spec*` ability the mayor holds (session `:58`). Spec mods are applied to people inside the city. 7-day change cooldown. **Six of eight specs have a server reader; two do nothing:** see 2.3. |
| Elections | `updateCityVoting` (1118), `promptMayoralVote` (2134), `castMayoralVote` (2179), `registerForMayoralRace` (2207), `unregisterFromMayoralRace` (2266), `sendMayoralStandings` (2090); `src/server/zone/objects/region/components/CityVotingMenuComponent.cpp:23-60` | real | Candidates must be citizens and still hold Politician Novice (1156). Ties go to the incumbent (1167). New mayor inherits civic structures (1188) and the spec cooldown (1191-1206). Election every `CityVotingCycles = 3` updates (about 3 weeks); registration locks after 2. |
| Militia | `sendManageMilitia` (1463), `promptAddMilitiaMember` (1500), `addMilitiaMember` (1517), `removeMilitiaMember` (1559) | **partial** | List management is real (citizen, within 10 m). But militia powers are only `/cityBan` (`CitybanCommand.h:48`), `/cityPardon` (`CitypardonCommand.h:46`), `/grantZoningRights` (`GrantZoningRightsCommand.h:39`) and exemption from the Stronghold defence mod (`CityRegionImplementation.cpp:905`). The UI text promises "the ability to attack visitors for the purposes of law enforcement" (line 1480): **no code gives militia a PvP/TEF right**. |
| City ban | `/cityBan`, `/cityPardon` (real); `/unCityBan` (staff, **stub**) | partial | Bans block city services (mission terminals `MissionManagerImplementation.cpp:188`, cloning `PlayerManagerImplementation.cpp:1720`, buildings `BuildingObject.idl:152`). |
| `/cityWarn` | (none) | **missing** | `EnableCityWarn = false` exists in `city_manager.lua:73`, but there is **no command class or registration** anywhere. |
| Zoning | `promptToggleZoningEnabled` (2404), `CityManager.idl:199-201`; `GrantZoningRightsCommand.h:50-56`; enforced at `StructureManager.cpp:409` and `TransferstructureCommand.h:179` | real | Rights last 24 h (`CityRegion.idl:215`). |
| Rename city | `sendChangeCityName` (2346) | real | |
| Register on planetary map | `promptRegisterCity` (1712), `registerCity` (1762), `unregisterCity` (1802) | real | Needs `city_map`. |
| Civic structure placement | `StructureManager.cpp:401-450` | real | City rank requirement per template (401-421), civic structures only by the mayor (423), unique structures once per city (428), ability check (445). City deeds: bank, cantina, city hall, cloning, garage, hospital, shuttleport, theater (each in corellia/naboo/tatooine styles), gardens, fountain, statue, streetlamp (`bin/scripts/object/tangible/deed/city_deed/`, `object/draft_schematic/structure/city/`). |
| Shuttleport own check | `src/server/zone/objects/installation/shuttle/ShuttleInstallationImplementation.cpp:11-30` | stub (covered elsewhere) | Its own mayor/unique check is commented out with a TODO, but the general civic/unique checks above apply. |
| Decorations | `CityDecorationTask.h:40-80`, `canSupportMoreDecorations` (2325) | real | 10 per rank (`DecorationsPerRank`). |
| Trainers / mission terminals | `/recruitSkillTrainer`, `/installMissionTerminal`; `canSupportMoreTrainers` (2332), `canSupportMoreMissionTerminals` (2339) | real | 3 per rank each. Faction terminals need Martial IV. |
| Amenity alignment | `alignAmenity` (2473), `CityRemoveAmenityTask.h` | real | |
| City hall terminal menu | `src/server/zone/objects/region/components/CityManagementMenuComponent.cpp:32-178` | real | Info, treasury, management, militia, specialisation, taxes, zoning, plus a **God-mode "City Hacks" submenu** (lines 45-48): force rank up/down, force update/election (`promptForceRank` 2435, `promptForceUpdate` 2454). Use this to test elections without waiting 3 weeks. |
| City guards / NPC spawner | `/startCitySpawner`, `/stopCitySpawner` | **stub** | Both handlers are empty (`StartCitySpawnerCommand.h`, `StopCitySpawnerCommand.h`). Player cities get no guards or ambient NPCs. |
| Staff `/cityInfo` | `sendCityReport` (250) | real | Mails a per-planet city report. |

### 2.3 Specialisations: which ones do anything

From `bin/scripts/managers/city_manager.lua:186-244`; consumers found with `git grep` over the whole repo.

| Specialisation | Skill mod | Server reader | Status |
|---|---|---|---|
| Sample Rich | `private_spec_samplesize` +20, `private_spec_samplerate` +10 | `src/server/zone/managers/resource/resourcespawner/ResourceSpawner.cpp:1083,1096` | real |
| Manufacturing Center | `private_spec_assembly` +10 | `src/server/zone/managers/crafting/labratories/SharedLabratory.cpp:146` | real |
| Medical Center | `private_medical_rating` +10 | `HealEnhanceCommand.h:91`, `HealDroidWoundCommand.h:69`, `BuildingObjectImplementation.cpp:1211` | real |
| Research Center | `private_spec_experimentation` +15 | `src/server/zone/managers/crafting/CraftingManagerImplementation.cpp:66` | real |
| Improved Job Market | `private_spec_missions` +15 | `MissionManagerImplementation.cpp:638,667,696,725` | real |
| Stronghold | `private_defense` +90 (non-militia) | `CombatManager.cpp:2030`, `CityRegionImplementation.cpp:905` | real |
| **Clone Lab** | `private_spec_cloning` +20 | **none** (only in city_manager.lua:213) | **stub**: costs 80,000 credits and does nothing server-side |
| **Entertainment District** | `private_spec_entertainer` +10 | **none** (only in city_manager.lua:234) | **stub**: costs 80,000 credits and does nothing server-side |

### 2.4 Sandbox settings that change how cities feel

`bin/scripts/managers/city_manager.lua` (local commit `4357970d`): `CitizensPerRank = {1, 2, 3, 4, 5}` (upstream {2,4,6,8,10}; commented "live-like" {10,20,35,55,85}), `maintenanceDiscount = 0.5`. Still upstream: `CityUpdateInterval = 10080` (7 days), `CityVotingCycles = 3`, `NewCityGracePeriod = 1440`, `CitySpecializationCooldown = 604800000` ms (7 days; the comment says minutes but the value is milliseconds), cities allowed on Corellia, Dantooine, Lok, Naboo, Rori, Talus, Tatooine; **none on Dathomir, Endor or Yavin 4**, and Hoth and Ossus aren't listed in `CitiesAllowed` at all.

### 2.5 Politician gaps and build work, ranked

1. **Clone Lab and Entertainment District do nothing.** Clone Lab: read `private_spec_cloning` in cloning (cheaper/faster clone, less cloning sickness) in `PlayerManagerImplementation::sendPlayerToCloner` (around line 1740). Entertainment District: read `private_spec_entertainer` in `EntertainingSessionImplementation` (buff strength/duration or XP). Small C++ each.
2. **Militia law enforcement is missing.** Decide the rule (pre-CU: militia could attack city-banned or warned players), then add a TEF/attackable check for militia vs `isBanned` visitors in `CreatureObjectImplementation`'s pvp status code, and write `/cityWarn` (config switch already exists). Medium.
3. **Weekly cadence makes the profession invisible in tests.** Add a config multiplier for `CityUpdateInterval` on the test galaxy, or script tests through the God-mode "Force City Update or Election" menu. Low.
4. **City guards** (`/startCitySpawner`). Optional pre-CU-adjacent feature: spawn patrolling guards for Township+ cities. Medium (Lua + AI patrol `bin/scripts/ai/cityPatrol.lua` exists).
5. **`/unCityBan` staff stub.** Low.
6. **Cities on more planets.** Add Hoth/Ossus to `CitiesAllowed` if wanted. Config.

**Bot probe for the profession:** an agent with Politician Novice places a city hall deed (needs `/agentgear` to hand out the deed), a second agent `/declareResidence`s in a house inside the radius, staff runs "Force City Update" from the city hall menu, then assert: city rank in `/cityInfo`, a mail "New City Approved", `political` XP on the mayor, income tax paid mail. Then set a sales tax and check a bazaar price.

---

## 3. Other professions that look thin in code

Method: profession data from `outputs/Claude-class-check/professions.json` (client `skills.iff`), command status from `outputs/tools/core3_audit/command_audit.json`, and a whole-repo string search for every skill mod and ability flag the profession grants (`build_systems.py` recomputes this). "No reader" means the name never appears as a literal anywhere in `src/` or `bin/scripts/`; a few names are built at runtime from parts, so treat it as a lead, not proof. Abilities that are permission flags often turn out to be client-side tooltips while the server checks the skill box name instead; that is noted where seen.

| Profession | What the code has | What looks thin | Verdict |
|---|---|---|---|
| **Creature Handler** | Taming (`TameCommand.h`, `CreatureImplementation.cpp:47`), command training gated per box (`PetControlDeviceImplementation.cpp:1296-1309`), mount training at Support IV (line 1339), 26 pet commands all `implemented` in the audit, `/emboldenPets`, `/enragePets`, pet specials and ranged attack. Reads `tame_level`, `keep_creature`, `stored_pets`, `tame_bonus`, `tame_aggro`, `creature_knowledge`. | The three CH skill mods `private_creature_empathy`, `private_creature_training`, `private_creature_management` have **no reader**. The 17 `pet_*`/`trick*` ability flags are unread (the server checks box names instead, fine). `/dismountAndStore` is a stub. AI follow/indoor pathing TODO (`FollowActions.h:492`). Balance never measured (see `Documentation-support/creature-handler-top-tier-plan.md`). | Implemented; **thin in tuning, not in code**. |
| **Bio-Engineer** | `sampleDNA` (real, gated on BE Novice at `SampleDNACommand.h:39`), `DnaManager.cpp`, `DnaComponent`, `PetDeed`, `bio_dna_sets.lua`, `bio_skill_mods.lua`, 155 BE schematics. | Only 1 ability in the whole profession; everything else is schematics. `/sampleDNA` has no `characterAbility` in the command table (class-check "ungated" list), so the handler's `hasSkill` is the only gate. | Implemented; needs a craft-a-pet end-to-end probe. |
| **Merchant** | Vendors (`VendorManager.cpp`, `vendor_manager.lua` hiring tiers), merchant tent deeds (3 styles). The perks are checked by **skill box name**, not by the ability names: bazaar listing fee -20% / -40% (`AuctionManagerImplementation.cpp:744-749`), vendor rate (`VendorDataComponent.cpp:440-442`), ad barking (`VendorAdBarkingSessionImplementation.cpp:60`), barker droid (`DroidMerchantModuleDataComponent.cpp:41`), vendor map registration and NPC vendor options (`VendorMenuComponent.cpp:87-182`); maintenance discount by ability `maintenance_fees_1` (`StructureManager.cpp:1382`). | No slash commands, so it looks empty from the abilities list. The ability names `vendor_fees_1`, `ad_fees_1`, `merchant_fees_1` and the `shop_sign` mod are unread, but the box checks above cover their effects. `/giveMaintenanceToVendor` and `/giveVendorMaint` are stubs (maintenance goes through the vendor radial; check). | Implemented. |
| **Squad Leader** | 7 commands, all `implemented`: `/boostMorale`, `/formup`, `/rally`, `/retreat`, `/steadyAim`, `/volleyFire`, `/sysgroup`, plus `/setWarcry` etc. for custom shouts. Shared base `SquadLeaderCommand.h`. | The group "shout" helper is commented out (`SquadLeaderCommand.h:98`). SL waypoints/group-wide effects untested. | Implemented. |
| **Smuggler** | Slicing (`SlicingSessionImplementation.cpp`, gated by box names at lines 242-261), slicing tools, 18 spice schematics using `spice_assembly`, `/lastDitch`, `/feignDeath`, contraband scans in GCW code. | `slice_*` ability flags unread (box names used instead, fine). `language_all_comprehend` mod unread (Smuggler's "understand all languages" perk has no effect). | Implemented; one dead perk. |
| **Bounty Hunter** | Bounty missions (`BountyMissionObjectiveImplementation.cpp`), probe droids and tracking (`objects/mission/bountyhunter/`, reads `droid_find_chance`, `droid_track_chance`, `droid_tracks`), player bounties (`PlayerBounty.idl`), Jedi bounties (`Core3.MissionManager.MaxBountiesPerJedi`, visibility manager). 12 combat commands via the combat engine. | `bounty_mission_level` mod unread (mission level not driven by BH skill; unsure how level is chosen). TODO at `BountyMissionObjectiveImplementation.cpp:177`: "add observer to catch player kill and fail mission". Several `private_*_combat_difficulty` mods unread. | Implemented; edge cases open. |
| **Ranger** | `/areaTrack` (real, gated by box names `AreatrackCommand.h:29,58,61`), `/conceal`, `/rescue`, camps (`CampSiteActiveArea`), `/maskScent`. | `private_areatrack` mod and the `areatrack_*` flags unread (box names used instead). | Implemented. |
| **Commando** | Heavy weapons via weapon templates (accuracy/speed mods are referenced from `object/weapon/...` templates), grenades, flame/acid commands via the combat engine. | `private_heavyweapon_combat_difficulty` unread. | Implemented. |
| **Image Designer / Politician** | See sections 1 and 2. | | Implemented with the gaps above. |
| **Shipwright** | Crafting through 336 space schematics; 18 `private_shipwright_*` ability flags unread (client markers). | Depends on JTL being enabled (`Core3.JTL.JTLEnabled`, default false; the sandbox profile sets it true). | Implemented as crafting. |

**Professions that are genuinely the thinnest in code**, ranked: Politician (two dead specialisations, no militia powers, no `/cityWarn`, no city guards), Bounty Hunter (mission edge cases), Creature Handler (three dead skill mods; otherwise the gap is balance and AI reliability, not missing code), Smuggler (one dead language perk). No pre-CU profession is a shell. A recurring pattern: the ability names in `skills.iff` (e.g. `vendor_fees_1`, `slice_*`, `pet_*`, `areatrack_*`) are often unread because the server checks the skill box name instead, and some skill mods are built from parts at runtime (e.g. `melee_damage_mitigation_` + level at `CombatManager.cpp:1281-1298`). So "no reader" needs a look at the code before it is called a gap; the cases named above were checked.
