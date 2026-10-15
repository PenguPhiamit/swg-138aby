# Pre-CU class check: profession / ability matrix

Generated 2026-10-15 04:32:30 by `outputs/Claude-class-check/build_matrix.py` (re-run it after any server or table change).
Source: Core3-dev `60ed8971 2026-10-15 Agent gear: item kits for the class check (C34, done by Claude while ChatGPT is out of usage) dev`. Data tables resolved by: server TreFiles order from bin/conf/config.lua. Archives: `skills.iff` from patch_14_00.tre; `command_table.iff` from patch_14_00.tre; `command_table_ground.iff` from patch_12_00.tre; `command_table_space.iff` from patch_11_03.tre; `skl_n.stf` from patch_12_00.tre; `cmd_n.stf` from patch_14_00.tre.

## Totals

| what | count |
|---|---|
| professions (IS_PROFESSION rows) | 54 |
| skill boxes (excluding the profession root rows) | 948 |
| skipped skills (languages, species, category roots, placeholders) | 66 |
| ability tokens granted by profession boxes (distinct) | 916 |
| ... of which resolve to a command row (slash command) | 357 |
| distinct command rows reached | 359 |
| command abilities whose handler looks like a stub or is missing | 2 |
| test kind `self` | 65 |
| test kind `attack` | 222 |
| test kind `heal_other` | 25 |
| test kind `target_friendly` | 6 |
| test kind `item` | 16 |
| test kind `crafting` | 0 |
| test kind `performance` | 53 |
| test kind `passive` | 507 |
| test kind `unknown` | 22 |

Table check: 804 Lua command scripts loaded, 804 listed in commands.lua, missing files none, unlisted files none.

## Per profession

`abilities` = distinct tokens in the profession's COMMANDS columns; `cmd` = those that are slash commands. The kind columns count abilities (see Test-kind rules). `stub` counts command abilities with a stub-looking handler. `pts` = skill points of the profession's own boxes / of the whole prerequisite closure. `schem` = schematic groups granted.

| profession | tier | boxes | pts own/closure | abil | cmd | self | attack | heal_other | target_friendly | item | crafting | performance | passive | unknown | stub | schem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| social_entertainer | starter | 18 | 77/77 | 52 | 4 | 0 | 0 | 0 | 0 | 5 | 0 | 26 | 21 | 0 | 0 | 2 |
| outdoors_scout | starter | 18 | 77/77 | 21 | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 18 | 0 | 0 | 8 |
| science_medic | starter | 18 | 77/77 | 27 | 9 | 1 | 0 | 6 | 2 | 0 | 0 | 0 | 18 | 0 | 0 | 11 |
| crafting_artisan | starter | 18 | 77/77 | 23 | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 20 | 0 | 2 | 14 |
| combat_brawler | starter | 18 | 77/77 | 65 | 32 | 3 | 29 | 0 | 0 | 0 | 0 | 0 | 33 | 0 | 0 | 0 |
| combat_marksman | starter | 18 | 77/77 | 67 | 25 | 5 | 20 | 0 | 0 | 0 | 0 | 0 | 42 | 0 | 0 | 0 |
| combat_rifleman | elite | 18 | 63/92 | 36 | 13 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 23 | 0 | 0 | 0 |
| combat_pistol | elite | 18 | 63/92 | 35 | 12 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 23 | 0 | 0 | 0 |
| combat_carbine | elite | 18 | 63/92 | 38 | 15 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 23 | 0 | 0 | 0 |
| combat_unarmed | elite | 18 | 63/92 | 36 | 14 | 3 | 11 | 0 | 0 | 0 | 0 | 0 | 22 | 0 | 0 | 0 |
| combat_1hsword | elite | 18 | 63/92 | 34 | 12 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 22 | 0 | 0 | 0 |
| combat_2hsword | elite | 18 | 63/92 | 24 | 11 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 0 | 0 |
| combat_polearm | elite | 18 | 63/92 | 22 | 12 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| social_dancer | elite | 18 | 63/106 | 22 | 6 | 0 | 0 | 0 | 0 | 1 | 0 | 19 | 2 | 0 | 0 | 0 |
| social_musician | elite | 18 | 63/106 | 19 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | 11 | 2 | 0 | 0 | 4 |
| science_doctor | elite | 18 | 63/140 | 8 | 7 | 0 | 0 | 5 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 23 |
| outdoors_ranger | elite | 18 | 63/140 | 8 | 3 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 5 | 0 | 0 | 10 |
| outdoors_creaturehandler | elite | 18 | 63/106 | 20 | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 17 | 0 | 0 | 0 |
| outdoors_bio_engineer | elite | 18 | 63/121 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 |
| crafting_armorsmith | elite | 18 | 63/92 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 15 |
| crafting_weaponsmith | elite | 18 | 63/92 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 18 |
| crafting_chef | elite | 18 | 63/92 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 16 |
| crafting_tailor | elite | 18 | 63/92 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 16 |
| crafting_architect | elite | 18 | 63/92 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 22 |
| crafting_droidengineer | elite | 18 | 63/92 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 29 |
| crafting_merchant | elite | 18 | 63/92 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 |
| combat_smuggler | elite | 18 | 63/121 | 11 | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 8 |
| combat_bountyhunter | elite | 18 | 63/169 | 19 | 12 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 |
| combat_commando | elite | 18 | 63/169 | 24 | 8 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 0 |
| science_combatmedic | elite | 18 | 63/169 | 4 | 3 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 19 |
| social_imagedesigner | elite | 18 | 47/76 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| outdoors_squadleader | elite | 18 | 63/135 | 7 | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| social_politician | elite | 18 | 0/0 | 27 | 3 | 0 | 0 | 0 | 1 | 2 | 0 | 0 | 24 | 0 | 0 | 0 |
| jedi_padawan | jedi_force | 18 | 250/250 | 25 | 24 | 10 | 12 | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 1 | 6 |
| jedi_light_side_journeyman | jedi_force | 18 | 0/250 | 34 | 33 | 7 | 19 | 7 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 5 |
| jedi_light_side_master | jedi_force | 18 | 0/250 | 23 | 21 | 3 | 12 | 6 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 5 |
| jedi_dark_side_journeyman | jedi_force | 18 | 0/250 | 30 | 29 | 7 | 15 | 7 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 5 |
| jedi_dark_side_master | jedi_force | 18 | 0/250 | 27 | 25 | 3 | 16 | 6 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 5 |
| force_sensitive_combat_prowess | jedi_force | 18 | 16/16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| force_sensitive_enhanced_reflexes | jedi_force | 18 | 16/16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| force_sensitive_crafting_mastery | jedi_force | 18 | 16/16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| force_sensitive_heightened_senses | jedi_force | 18 | 16/16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| force_discipline_light_saber | jedi_force | 18 | 89/89 | 50 | 38 | 0 | 38 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 8 |
| force_discipline_powers | jedi_force | 18 | 89/89 | 20 | 20 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| force_discipline_healing | jedi_force | 18 | 89/89 | 31 | 31 | 18 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| force_discipline_enhancements | jedi_force | 18 | 89/89 | 22 | 22 | 20 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| force_discipline_defender | jedi_force | 18 | 89/89 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| force_rank_light | jedi_force | 12 | 0/0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| force_rank_dark | jedi_force | 12 | 0/0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| force_title_jedi | jedi_force | 6 | 0/0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 2 |
| crafting_shipwright | space | 18 | 63/92 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 18 | 0 | 0 | 18 |
| pilot_rebel_navy | space | 18 | 0/0 | 64 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 54 | 10 | 0 | 0 |
| pilot_imperial_navy | space | 18 | 0/0 | 61 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 55 | 6 | 0 | 0 |
| pilot_neutral | space | 18 | 0/0 | 57 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 50 | 7 | 0 | 0 |

## Stub-looking or missing-handler commands

A handler is a *template stub* when its `doQueueCommand` only runs the state/locomotion guards and returns SUCCESS. The command then "succeeds" with no effect from this class; any real feature behind it must live in another code path (a packet handler, a radial menu, a tool object). A command row with no registered class would be dropped silently by the server (ObjectControllerImplementation.cpp, "unregistered queue command"); the count of those is below.

| ability | command | professions | class | status | doQueueCommand | reason | notes |
|---|---|---|---|---|---|---|---|
| customizeVehicle | customizeVehicle | crafting_artisan | CustomizeVehicleCommand | template_stub | src/server/zone/objects/creature/commands/CustomizeVehicleCommand.h:16-25 | only the state/locomotion guards, then return SUCCESS | handler is a template stub; no other server reference to this command was found; treat as unimplemented |
| survey | survey | crafting_artisan, jedi_padawan | SurveyCommand | template_stub | src/server/zone/objects/creature/commands/SurveyCommand.h:16-25 | only the state/locomotion guards, then return SUCCESS | handler is a template stub; see survey tool code; the real check is in the survey tool: SurveyToolImplementation.cpp handleObjectMenuSelect needs hasAbility("survey") (failure message @error_message:insufficient_skill); test by using a survey tool, not by /survey |

Command rows (all three tables) without a registered handler class: **0**.

Template-stub command rows anywhere in the tables (not only the ones a profession grants): **157**. Those granted by a profession are in the table above; the rest are staff/admin, city, vendor or client-side commands and are not part of a class check.

### Handlers with TODO / "no effect" comments in their own header

| ability | professions | notes (file:line text) |
|---|---|---|
| healDamage | science_medic | src/server/zone/objects/creature/commands/HealDamageCommand.h:312 // TODO: Replace this with a CombatManager::getAreaTargets() call |
| healEnhance | science_doctor | src/server/zone/objects/creature/commands/HealEnhanceCommand.h:207 if (BuffAttribute::isProtection(enhancePack->getAttribute())) { // If it's a protection enhancement, wound treatment has no effect |
| healWound | science_medic | src/server/zone/objects/creature/commands/HealWoundCommand.h:314 //TODO: Patch the tre later to include a %NT. |
| powerBoost | combat_unarmed | src/server/zone/objects/creature/commands/PowerBoostCommand.h:31 //TODO: fix powerboost cancel |
| regainConsciousness | force_discipline_enhancements | src/server/zone/objects/creature/commands/RegainConsciousnessCommand.h:39 // TODO: Find potential end message for force regen debuff<br>src/server/zone/objects/creature/commands/RegainConsciousnessCommand.h:48 // TODO: Find potential end message for groggy debuff |
| revivePlayer | science_doctor | src/server/zone/objects/creature/commands/RevivePlayerCommand.h:109 // TODO: Find potential end message for groggy debuff |
| surpriseShot | combat_rifleman | src/server/zone/objects/creature/commands/SurpriseShotCommand.h:42 /* TODO: Implement check against alertness for either failure chance or damage bonus. This was broken Pre-CU */ |

## Other findings from the source

* **Ungated commands** (command table has no characterAbility, so any player can run them; a "works" result proves nothing about the box): 8: customizeVehicle, grantZoningRights, sampleDNA, startDance, startMusic, stopDance, stopMusic, tame.
* **Ability token is not the command's gate**: diagnose (needs tendWound).
* **One ability gates several commands**: tendDamage -> tendDamage, tendDamageTool; tendWound -> diagnose, tendWound, tendWoundsTool.
* **Combat commands with no Lua script** (defaults apply): bstrike1, bstrike2, bstrike3, epulse1, epulse2, epulse3, eshields, ethrust, eweapons, iffscramble, inspacereload, inspacerepair, inspacerr, jstart1, jstart2, jstart3, nblast, ptrap1, ptrap2, pumpreactor, vrepair, vrepairother.
* **Lua scripts whose `name` matches no command row**: lootaicorpse. **Command rows with no Lua script**: 52 (all-profession commands among them: bstrike1, bstrike2, bstrike3, epulse1, epulse2, epulse3, eshields, ethrust, eweapons, iffscramble, inspacereload, inspacerepair, inspacerr, jstart1, jstart2, jstart3, nblast, ptrap1, ptrap2, pumpreactor, vrepair, vrepairother).
* **Lua `disabled = true`**: none.
* **Space-only commands** (cannot be tried on the ground): 22 (pilot_imperial_navy, pilot_neutral, pilot_rebel_navy).
* **Crafting**: 0 abilities have test kind `crafting`. Crafting professions grant skill mods and schematic groups (professions.json, `schematics_granted`), not slash commands.
* **Granted abilities with no command row and no server reference found** (quoted-name scan of src/server, src/templates, bin/scripts/managers, commands, object templates and screenplays, plus the run-time-built names listed in `dynamic_refs`):
  * feature_flag (10): areatrack_animal, areatrack_direction, areatrack_distance, areatrack_npc, areatrack_player, slice_armor, slice_containers, slice_terminals, slice_weaponsadvanced, slice_weaponsbasic
  * other_flag (4): droid_find, droid_track, forceIntimidate, sneak
  * permission_flag (13): access_fee, ad_fees_1, city_spec_cloning, city_spec_doctor, city_spec_entertainer, city_spec_industry, city_spec_missions, city_spec_research, city_spec_sample_rich, city_spec_stronghold, merchant_fees_1, premium_auctions ... (full list in commands.json)
  * pet_flag (17): pet_attack, pet_follow, pet_followother, pet_formation, pet_friend, pet_group, pet_guard, pet_patrol, pet_rangedattack, pet_release, pet_specialattack1, pet_specialattack2 ... (full list in commands.json)
  * private_flag (260): private_1hand_ability_1, private_1hand_ability_2, private_1hand_ability_3, private_1hand_ability_4, private_1hand_accuracy_1, private_1hand_accuracy_2, private_1hand_accuracy_3, private_1hand_accuracy_4, private_1hand_master, private_1hand_novice, private_1hand_speed_1, private_1hand_speed_2 ... (full list in commands.json)
* **Real handler, but its Lua configuration looks inert**: none found.
* **Hidden / god-only boxes**: 90 of the jedi_* boxes are flagged god_only in skills.iff. `awardSkill` does not check that flag (it checks prerequisites, species, Jedi state, and force_* via the Jedi manager), so `/agentskill` should be able to grant them; this has not been tried.

## Commands that need special setup

| setup tag | what the bot needs | abilities | which (first 40) |
|---|---|---|---|
| weapon:1h lightsaber | weapon class: 1h lightsaber | 11 | saber1hComboHit1, saber1hComboHit2, saber1hComboHit3, saber1hFlurry, saber1hFlurry2, saber1hHeadHit1, saber1hHeadHit2, saber1hHeadHit3, saber1hHit1, saber1hHit2, saber1hHit3 |
| weapon:1h melee | weapon class: 1h melee | 18 | melee1hBlindHit1, melee1hBlindHit2, melee1hBodyHit1, melee1hBodyHit2, melee1hBodyHit3, melee1hDizzyHit1, melee1hDizzyHit2, melee1hHealthHit1, melee1hHealthHit2, melee1hHit1, melee1hHit2, melee1hHit3, melee1hLunge1, melee1hLunge2, melee1hScatterHit1, melee1hScatterHit2, melee1hSpinAttack1, melee1hSpinAttack2 |
| weapon:2h lightsaber | weapon class: 2h lightsaber | 11 | saber2hBodyHit1, saber2hBodyHit2, saber2hBodyHit3, saber2hFrenzy, saber2hHit1, saber2hHit2, saber2hHit3, saber2hPhantom, saber2hSweep1, saber2hSweep2, saber2hSweep3 |
| weapon:2h melee | weapon class: 2h melee | 17 | melee2hArea1, melee2hArea2, melee2hArea3, melee2hHeadHit1, melee2hHeadHit2, melee2hHeadHit3, melee2hHit1, melee2hHit2, melee2hHit3, melee2hLunge1, melee2hLunge2, melee2hMindHit1, melee2hMindHit2, melee2hSpinAttack1, melee2hSpinAttack2, melee2hSweep1, melee2hSweep2 |
| weapon:carbine | weapon class: carbine | 23 | actionShot1, actionShot2, burstShot1, burstShot2, chargeShot1, chargeShot2, confusionShot, cripplingShot, fullAutoArea1, fullAutoArea2, fullAutoSingle1, fullAutoSingle2, knockdownFire, legShot1, legShot2, legShot3, scatterShot1, scatterShot2, sprayShot, suppressionFire2, underHandShot, wildShot1, wildShot2 |
| weapon:lightsaber | weapon class: lightsaber | 5 | saberSlash1, saberSlash2, saberThrow1, saberThrow2, saberThrow3 |
| weapon:melee_or_unarmed | weapon class: melee_or_unarmed | 3 | berserk1, berserk2, centerOfBeing |
| weapon:pistol | weapon class: pistol | 25 | bleedingShot, bodyShot1, bodyShot2, bodyShot3, disarmingShot1, disarmingShot2, diveShot, doubleTap, eyeShot, fanShot, fastBlast, healthShot1, healthShot2, kipUpShot, lastDitch, lowBlow, multiTargetPistolShot, panicShot, pistolMeleeDefense1, pistolMeleeDefense2, pointBlankArea2, pointBlankSingle2, rollShot, stoppingShot, torsoShot |
| weapon:polearm | weapon class: polearm | 18 | polearmActionHit1, polearmActionHit2, polearmArea1, polearmArea2, polearmHit1, polearmHit2, polearmHit3, polearmLegHit1, polearmLegHit2, polearmLegHit3, polearmLunge1, polearmLunge2, polearmSpinAttack1, polearmSpinAttack2, polearmStun1, polearmStun2, polearmSweep1, polearmSweep2 |
| weapon:polearm lightsaber | weapon class: polearm lightsaber | 11 | saberPolearmDervish, saberPolearmDervish2, saberPolearmHit1, saberPolearmHit2, saberPolearmHit3, saberPolearmLegHit1, saberPolearmLegHit2, saberPolearmLegHit3, saberPolearmSpinAttack1, saberPolearmSpinAttack2, saberPolearmSpinAttack3 |
| weapon:ranged | weapon class: ranged | 8 | aim, overChargeShot1, overChargeShot2, pointBlankArea1, pointBlankSingle1, suppressionFire1, threatenShot, warningShot |
| weapon:rifle | weapon class: rifle | 16 | concealShot, flurryShot1, flurryShot2, flushingShot1, flushingShot2, headShot1, headShot2, headShot3, mindShot1, mindShot2, sniperShot, startleShot1, startleShot2, strafeShot1, strafeShot2, surpriseShot |
| weapon:special heavy (flame/acid/lightning beam) | weapon class: special heavy (flame/acid/lightning beam) | 12 | fireAcidCone1, fireAcidCone2, fireAcidSingle1, fireAcidSingle2, fireLightningCone1, fireLightningCone2, fireLightningSingle1, fireLightningSingle2, flameCone1, flameCone2, flameSingle1, flameSingle2 |
| weapon:unarmed | weapon class: unarmed | 17 | unarmedBlind1, unarmedBodyHit1, unarmedCombo1, unarmedCombo2, unarmedDizzy1, unarmedHeadHit1, unarmedHit1, unarmedHit2, unarmedHit3, unarmedKnockdown1, unarmedKnockdown2, unarmedLegHit1, unarmedLunge1, unarmedLunge2, unarmedSpinAttack1, unarmedSpinAttack2, unarmedStun1 |
| affliction:battle_fatigue | the patient has battle fatigue | 2 | healBattleFatigueSelf1, healBattleFatigueSelf2 |
| affliction:bleeding | the patient is bleeding | 2 | firstAid, stopBleeding |
| affliction:disease | the patient is diseased | 2 | cureDisease, forceCureDisease |
| affliction:fire | the patient is on fire | 1 | extinguishFire |
| affliction:poison | the patient is poisoned | 2 | curePoison, forceCurePoison |
| affliction:state | the patient is stunned, dizzy, blind or intimidated | 3 | healState, healStatesOther, healStatesSelf |
| affliction:wounds | the patient has wounds (sustained combat damage) | 16 | healActionWoundOther1, healActionWoundOther2, healActionWoundSelf1, healActionWoundSelf2, healHealthWoundOther1, healHealthWoundOther2, healHealthWoundSelf1, healHealthWoundSelf2, healMindWoundOther1, healMindWoundOther2, healMindWoundSelf1, healMindWoundSelf2, healWound, tendWound, totalHealOther, totalHealSelf |
| building:medical_or_entertainment | inside a medical or entertainment building | 1 | registerWithLocation |
| city | a city with the bot as mayor or militia | 3 | grantZoningRights, installMissionTerminal, recruitSkillTrainer |
| combat_state | the bot is in combat | 1 | feignDeath |
| combat_state_optional | works with or without combat; the roll is harder in combat | 1 | takeCover |
| corpse | a dead creature (kill one first) | 1 | harvestCorpse |
| creature_target | a live creature that can be sampled/tamed | 2 | sampleDNA, tame |
| damaged_self | the bot has HAM damage or an affliction to heal | 18 | healActionSelf1, healActionSelf2, healActionWoundSelf1, healActionWoundSelf2, healAllSelf1, healAllSelf2, healBattleFatigueSelf1, healBattleFatigueSelf2, healHealthSelf1, healHealthSelf2, healHealthWoundSelf1, healHealthWoundSelf2, healMindSelf1, healMindSelf2, healMindWoundSelf1, healMindWoundSelf2, healStatesSelf, totalHealSelf |
| force_power | Force power in the pool (Jedi skill mods) and no armor worn | 112 | animalAttack, animalCalm, animalScare, avoidIncapacitation, channelForce, drainForce, forceAbsorb1, forceAbsorb2, forceArmor1, forceArmor2, forceChoke, forceCureDisease, forceCurePoison, forceFeedback1, forceFeedback2, forceIntimidate1, forceIntimidate2, forceKnockdown1, forceKnockdown2, forceKnockdown3, forceLightningCone1, forceLightningCone2, forceLightningSingle1, forceLightningSingle2, forceMeditate, forceResistBleeding, forceResistDisease, forceResistPoison, forceResistStates, forceRun1, forceRun2, forceRun3, forceShield1, forceShield2, forceSpeed1, forceSpeed2, forceThrow1, forceThrow2, forceWeaken1, forceWeaken2 ... |
| friendly_target | a second bot standing near, not in PvP | 5 | diagnose, grantZoningRights, healEnhance, rescue, transferForce |
| group_leader | the bot leads a group with at least one other member | 7 | boostmorale, formup, rally, retreat, steadyaim, sysgroup, volleyFire |
| group_member | at least one group member near the leader | 7 | boostmorale, formup, rally, rescue, retreat, steadyaim, volleyFire |
| hostile_target | a hostile creature or training target in range (and line of sight) | 219 | actionShot1, actionShot2, animalAttack, animalCalm, animalScare, applyDisease, applyPoison, bleedingShot, bodyShot1, bodyShot2, bodyShot3, burstShot1, burstShot2, chargeShot1, chargeShot2, concealShot, confusionShot, cripplingShot, disarmingShot1, disarmingShot2, diveShot, doubleTap, drainForce, eyeShot, fanShot, fastBlast, fireAcidCone1, fireAcidCone2, fireAcidSingle1, fireAcidSingle2, fireLightningCone1, fireLightningCone2, fireLightningSingle1, fireLightningSingle2, flameCone1, flameCone2, flameSingle1, flameSingle2, flurryShot1, flurryShot2 ... |
| incapacitated_friendly | a second bot that is incapacitated (or dead for revive) | 2 | dragIncapacitatedPlayer, revivePlayer |
| incapacitated_self | the bot itself is incapacitated | 2 | forceOfWill, regainConsciousness |
| item:cure_pack | item in inventory/equipped: cure pack | 3 | cureDisease, curePoison, extinguishFire |
| item:dot_pack | item in inventory/equipped: dot pack | 2 | applyDisease, applyPoison |
| item:enhance_pack | item in inventory/equipped: enhance pack | 1 | healEnhance |
| item:instrument | item in inventory/equipped: instrument | 13 | startMusic, startMusic+ballad, startMusic+ceremonial, startMusic+folk, startMusic+funk, startMusic+jazz, startMusic+rock, startMusic+starwars1, startMusic+starwars2, startMusic+starwars3, startMusic+starwars4, startMusic+virtuoso, startMusic+waltz |
| item:instrument:bandfill | item in inventory/equipped: instrument:bandfill | 1 | bandfill |
| item:instrument:fanfar | item in inventory/equipped: instrument:fanfar | 1 | fanfar |
| item:instrument:fizz | item in inventory/equipped: instrument:fizz | 1 | fizz |
| item:instrument:flutedroopy | item in inventory/equipped: instrument:flutedroopy | 1 | flutedroopy |
| item:instrument:kloohorn | item in inventory/equipped: instrument:kloohorn | 1 | kloohorn |
| item:instrument:mandoviol | item in inventory/equipped: instrument:mandoviol | 1 | mandoviol |
| item:instrument:nalargon | item in inventory/equipped: instrument:nalargon | 1 | nalargon |
| item:instrument:omnibox | item in inventory/equipped: instrument:omnibox | 1 | omnibox |
| item:instrument:slitherhorn | item in inventory/equipped: instrument:slitherhorn | 1 | slitherhorn |
| item:instrument:traz | item in inventory/equipped: instrument:traz | 1 | traz |
| item:medicine | item in inventory/equipped: medicine | 1 | firstAid |
| item:revive_pack | item in inventory/equipped: revive pack | 1 | revivePlayer |
| item:state_pack | item in inventory/equipped: state pack | 1 | healState |
| item:stimpack | item in inventory/equipped: stimpack | 1 | healDamage |
| item:survey_tool | item in inventory/equipped: survey tool | 2 | sample, survey |
| item:wound_pack | item in inventory/equipped: wound pack | 1 | healWound |
| meditating | the bot is meditating | 1 | powerBoost |
| no_armor | no armor worn | 111 | animalAttack, animalCalm, animalScare, avoidIncapacitation, channelForce, drainForce, forceAbsorb1, forceAbsorb2, forceArmor1, forceArmor2, forceChoke, forceCureDisease, forceCurePoison, forceFeedback1, forceFeedback2, forceIntimidate1, forceIntimidate2, forceKnockdown1, forceKnockdown2, forceKnockdown3, forceLightningCone1, forceLightningCone2, forceLightningSingle1, forceLightningSingle2, forceMeditate, forceResistBleeding, forceResistDisease, forceResistPoison, forceResistStates, forceRun1, forceRun2, forceRun3, forceShield1, forceShield2, forceSpeed1, forceSpeed2, forceThrow1, forceThrow2, forceWeaken1, forceWeaken2 ... |
| outdoors | outdoors, not in a building | 2 | forage, medicalForage |
| performance | entertainer: run the dance/song first | 44 | flourish+1, flourish+2, flourish+3, flourish+4, flourish+5, flourish+6, flourish+7, flourish+8, startDance, startDance+basic, startDance+basic2, startDance+breakdance, startDance+breakdance2, startDance+exotic, startDance+exotic2, startDance+exotic3, startDance+exotic4, startDance+footloose, startDance+footloose2, startDance+formal, startDance+formal2, startDance+lyrical, startDance+lyrical2, startDance+poplock, startDance+poplock2, startDance+popular, startDance+popular2, startDance+rhythmic, startDance+rhythmic2, startDance+tumble, startDance+tumble2, startMusic, startMusic+ballad, startMusic+ceremonial, startMusic+folk, startMusic+funk, startMusic+jazz, startMusic+rock, startMusic+starwars1, startMusic+starwars2 ... |
| performing | the bot is dancing or playing music (start one first) | 17 | colorlights, dazzle, distract, firejet, flourish+1, flourish+2, flourish+3, flourish+4, flourish+5, flourish+6, flourish+7, flourish+8, smokebomb, spotlight, stopDance, stopMusic, ventriloquism |
| pet | an owned pet | 2 | emboldenpets, enragepets |
| resource_point | a surveyed resource point | 1 | sample |
| ship | a piloted ship (space) | 22 | bstrike1, bstrike2, bstrike3, epulse1, epulse2, epulse3, eshields, ethrust, eweapons, iffscramble, inspacereload, inspacerepair, inspacerr, jstart1, jstart2, jstart3, nblast, ptrap1, ptrap2, pumpreactor, vrepair, vrepairother |
| sui | a pop-up window answer | 4 | areatrack, diagnose, installMissionTerminal, recruitSkillTrainer |
| vehicle | a vehicle | 1 | customizeVehicle |
| wounded_friendly | a second bot with HAM damage, wounds, bleeding or a state | 24 | cureDisease, curePoison, extinguishFire, firstAid, forceCureDisease, forceCurePoison, healActionWoundOther1, healActionWoundOther2, healAllOther1, healAllOther2, healDamage, healHealthWoundOther1, healHealthWoundOther2, healMind, healMindWoundOther1, healMindWoundOther2, healState, healStatesOther, healWound, quickHeal, stopBleeding, tendDamage, tendWound, totalHealOther |

Full per-ability lists are in commands.json (`setup_tags`).

## Test-kind rules

The rule that fired is stored with every entry (`test_kind_rule`). Order matters.

| rule | text |
|---|---|
| R0 | Ability token with no command row: certification / private flag / permission flag / droid program / pet flag = passive; startDance+x, startMusic+x, flourish+n = performance; instrument names = item (instrument). |
| R1 | Command defined only in command_table_space.iff = unknown (space-only, needs a ship). |
| R2 | Command row without a registered C++ class = unknown. |
| R3 | Plain-QueueCommand handlers (and combat-family debuffs such as warcry/taunt) are listed by name in KIND_BY_COMMAND, each set after reading the handler; the reason text says what the handler requires. |
| R4 | ForceHealQueueCommand classes: a name ending in Self or Lua allowedTarget SELF = self; a name ending in Other, or allowedTarget OTHER or SELF + OTHER = heal_other (the SELF + OTHER cures also work on the user). |
| R5 | JediCombatQueueCommand (lightsaber moves) = attack, needs a lightsaber, Force power and no armor. |
| R6 | ForcePowersQueueCommand = attack on a hostile target (Force power, no armor). |
| R7 | JediQueueCommand = self (Force buff). |
| R8 | SquadLeaderCommand = self with a group (the bot must lead a group). |
| R9 | CurePackCommand = heal_other (cure pack item, afflicted friendly target). |
| R10 | DotPackCommand = attack (dot pack item, hostile target). |
| R11 | Any other CombatQueueCommand descendant = attack (hostile target); weapon class comes from the Lua weaponType. |
| R12 | Anything else = unknown. |

`target_type` in the command table is stored by the server but never read (QueueCommand.h getter only); 0/1/2 are read as none/required/optional by the SWG command-table convention, which is not verified in this source.

## Granting a profession to a bot

Two server helpers exist (test galaxy only, bot accounts in Core3.AgentAccounts):

* `/agentgear profession <name>`: grants every box of an IS_PROFESSION row plus all prerequisites (also from other professions) with no XP and no skill-point limit; `/agentgear profession clear` surrenders all skills (character-builder "Unlearn All Skills"); `/agentgear profession list` answers with the current boxes. It refuses god_only professions and skips god_only boxes. Species/Jedi prerequisites are still enforced, so Force boxes land in `failed`.
* `/agentskill <box> ...`: awards boxes plus prerequisites without XP, but the point cap applies (250, `Core3.Sandbox.SkillPoints` default; the live value may differ in config-local.lua, which was not read) and there is no revoke. It does not check the god_only flag.

`agentgear` column: `ok` = every box should be granted; `unavailable_god_only_profession` = refused (use /agentskill); `partial_*` = some boxes will be in `failed`. `agentskill` column: `ok`, `over_cap`, or `blocked_jedi` (a box needs Jedi state or goes through the Jedi manager).

| profession | closure pts | closure boxes | agentgear | agentskill | also grants boxes of | blockers |
|---|---|---|---|---|---|---|
| social_entertainer | 77 | 18 | ok | ok |  |  |
| outdoors_scout | 77 | 18 | ok | ok |  |  |
| science_medic | 77 | 18 | ok | ok |  |  |
| crafting_artisan | 77 | 18 | ok | ok |  |  |
| combat_brawler | 77 | 18 | ok | ok |  |  |
| combat_marksman | 77 | 18 | ok | ok |  |  |
| combat_rifleman | 92 | 23 | ok | ok | combat_marksman |  |
| combat_pistol | 92 | 23 | ok | ok | combat_marksman |  |
| combat_carbine | 92 | 23 | ok | ok | combat_marksman |  |
| combat_unarmed | 92 | 23 | ok | ok | combat_brawler |  |
| combat_1hsword | 92 | 23 | ok | ok | combat_brawler |  |
| combat_2hsword | 92 | 23 | ok | ok | combat_brawler |  |
| combat_polearm | 92 | 23 | ok | ok | combat_brawler |  |
| social_dancer | 106 | 27 | ok | ok | social_entertainer |  |
| social_musician | 106 | 27 | ok | ok | social_entertainer |  |
| science_doctor | 140 | 36 | ok | ok | science_medic |  |
| outdoors_ranger | 140 | 36 | ok | ok | outdoors_scout |  |
| outdoors_creaturehandler | 106 | 27 | ok | ok | outdoors_scout |  |
| outdoors_bio_engineer | 121 | 28 | ok | ok | outdoors_scout, science_medic |  |
| crafting_armorsmith | 92 | 23 | ok | ok | crafting_artisan |  |
| crafting_weaponsmith | 92 | 23 | ok | ok | crafting_artisan |  |
| crafting_chef | 92 | 23 | ok | ok | crafting_artisan |  |
| crafting_tailor | 92 | 23 | ok | ok | crafting_artisan |  |
| crafting_architect | 92 | 23 | ok | ok | crafting_artisan |  |
| crafting_droidengineer | 92 | 23 | ok | ok | crafting_artisan |  |
| crafting_merchant | 92 | 23 | ok | ok | crafting_artisan |  |
| combat_smuggler | 121 | 28 | ok | ok | combat_brawler, combat_marksman |  |
| combat_bountyhunter | 169 | 41 | ok | ok | combat_marksman, outdoors_scout |  |
| combat_commando | 169 | 41 | ok | ok | combat_brawler, combat_marksman |  |
| science_combatmedic | 169 | 41 | ok | ok | combat_marksman, science_medic |  |
| social_imagedesigner | 76 | 23 | ok | ok | social_entertainer |  |
| outdoors_squadleader | 135 | 32 | ok | ok | combat_marksman, outdoors_scout |  |
| social_politician | 0 | 18 | ok | ok |  |  |
| jedi_padawan | 250 | 18 | unavailable_god_only_profession | ok |  |  |
| jedi_light_side_journeyman | 250 | 36 | unavailable_god_only_profession | ok | jedi_padawan |  |
| jedi_light_side_master | 250 | 54 | unavailable_god_only_profession | ok | jedi_light_side_journeyman, jedi_padawan |  |
| jedi_dark_side_journeyman | 250 | 36 | unavailable_god_only_profession | ok | jedi_padawan |  |
| jedi_dark_side_master | 250 | 54 | unavailable_god_only_profession | ok | jedi_dark_side_journeyman, jedi_padawan |  |
| force_sensitive_combat_prowess | 16 | 18 | partial_jedi | blocked_jedi |  | force_sensitive_combat_prowess_master needs Jedi state 1; force_sensitive_combat_prowess_melee_accuracy_01 needs Jedi state 1 |
| force_sensitive_enhanced_reflexes | 16 | 18 | partial_jedi | blocked_jedi |  | force_sensitive_enhanced_reflexes_master needs Jedi state 1; force_sensitive_enhanced_reflexes_melee_defense_01 needs Jedi state 1 |
| force_sensitive_crafting_mastery | 16 | 18 | partial_jedi | blocked_jedi |  | force_sensitive_crafting_mastery_assembly_01 needs Jedi state 1; force_sensitive_crafting_mastery_assembly_02 needs Jedi state 1 |
| force_sensitive_heightened_senses | 16 | 18 | partial_jedi | blocked_jedi |  | force_sensitive_heightened_senses_healing_01 needs Jedi state 1; force_sensitive_heightened_senses_healing_02 needs Jedi state 1 |
| force_discipline_light_saber | 89 | 21 | partial_jedi | blocked_jedi | force_title_jedi | force_discipline_light_saber_master needs Jedi state 2; force_discipline_light_saber_novice needs Jedi state 2 |
| force_discipline_powers | 89 | 21 | partial_jedi | blocked_jedi | force_title_jedi | force_discipline_powers_debuff_01 needs Jedi state 2; force_discipline_powers_debuff_02 needs Jedi state 2 |
| force_discipline_healing | 89 | 21 | partial_jedi | blocked_jedi | force_title_jedi | force_discipline_healing_damage_01 needs Jedi state 2; force_discipline_healing_damage_02 needs Jedi state 2 |
| force_discipline_enhancements | 89 | 21 | partial_jedi | blocked_jedi | force_title_jedi | force_discipline_enhancements_master needs Jedi state 2; force_discipline_enhancements_movement_01 needs Jedi state 2 |
| force_discipline_defender | 89 | 21 | partial_jedi | blocked_jedi | force_title_jedi | force_discipline_defender_force_defense_01 needs Jedi state 2; force_discipline_defender_force_defense_02 needs Jedi state 2 |
| force_rank_light | 0 | 12 | partial_jedi | blocked_jedi |  | force_rank_light_master needs Jedi state 4; force_rank_light_novice needs Jedi state 4 |
| force_rank_dark | 0 | 12 | partial_jedi | blocked_jedi |  | force_rank_dark_master needs Jedi state 8; force_rank_dark_novice needs Jedi state 8 |
| force_title_jedi | 0 | 6 | partial_jedi | blocked_jedi |  | force_title_jedi_master needs Jedi state 1; force_title_jedi_novice needs Jedi state 1 |
| crafting_shipwright | 92 | 23 | ok | ok | crafting_artisan |  |
| pilot_rebel_navy | 0 | 18 | ok | ok |  |  |
| pilot_imperial_navy | 0 | 18 | ok | ok |  |  |
| pilot_neutral | 0 | 18 | ok | ok |  |  |

### Fallback: suggested /agentskill builds (first-fit packing, <= 250 points per character, no revoke)

| build | points | professions (test order) | /agentskill calls |
|---|---|---|---|
| build01 | 246 | combat_marksman, outdoors_squadleader, combat_bountyhunter | combat_bountyhunter_master combat_marksman_master outdoors_squadleader_master |
| build02 | 232 | science_medic, science_doctor, science_combatmedic | science_combatmedic_master science_doctor_master science_medic_master |
| build03 | 232 | outdoors_scout, outdoors_bio_engineer, outdoors_ranger | outdoors_bio_engineer_master outdoors_ranger_master outdoors_scout_master |
| build04 | 250 | social_entertainer, social_imagedesigner, social_dancer, social_musician | social_dancer_master social_entertainer_master social_imagedesigner_master social_musician_master |
| build05 | 246 | crafting_artisan, combat_carbine, combat_pistol | combat_carbine_master combat_pistol_master crafting_artisan_master |
| build06 | 77 | combat_brawler | combat_brawler_master |
| build07 | 232 | combat_smuggler, combat_commando | combat_commando_master combat_smuggler_master |
| build08 | 198 | combat_rifleman, outdoors_creaturehandler | combat_rifleman_master outdoors_creaturehandler_master |
| build09 | 246 | combat_1hsword, combat_2hsword, combat_unarmed | combat_1hsword_master combat_2hsword_master combat_unarmed_master |
| build10 | 247 | combat_polearm, crafting_armorsmith, crafting_weaponsmith | combat_polearm_master crafting_armorsmith_master crafting_weaponsmith_master |
| build11 | 232 | crafting_architect, crafting_chef, crafting_tailor | crafting_architect_master crafting_chef_master crafting_tailor_master |
| build12 | 250 | social_politician, jedi_light_side_journeyman, jedi_light_side_master, jedi_padawan | jedi_light_side_journeyman_master jedi_light_side_master_master jedi_padawan_master social_politician_master |
| build13 | 232 | crafting_droidengineer, crafting_merchant, crafting_shipwright | crafting_droidengineer_master crafting_merchant_master crafting_shipwright_master |
| build14 | 250 | jedi_dark_side_journeyman, jedi_dark_side_master | jedi_dark_side_journeyman_master jedi_dark_side_master_master |

## Proposed run order (one profession per run)

Each run: `/agentgear profession clear`, grant the profession (it also grants boxes of the professions it needs), try every non-passive ability granted by the profession's own boxes, then the next row. `tries` = abilities tried; `excl` = of those, abilities that none of the prerequisite professions' boxes grant (a success proves this profession's boxes give it); the others also come from a prerequisite profession. Readiness counts are ready / needs_staging / needs_new_kit / blocked.

| step | phase | profession | grant | tries | excl | ready / staging / new kit / blocked |
|---|---|---|---|---|---|---|
| 1 | P1 | combat_marksman | /agentgear profession combat_marksman | 25 | 25 | 25 / 0 / 0 / 0 |
| 2 | P1 | combat_brawler | /agentgear profession combat_brawler | 32 | 32 | 26 / 0 / 6 / 0 |
| 3 | P1 | outdoors_scout | /agentgear profession outdoors_scout | 3 | 3 | 2 / 1 / 0 / 0 |
| 4 | P1 | science_medic | /agentgear profession science_medic | 9 | 9 | 5 / 4 / 0 / 0 |
| 5 | P1 | social_entertainer | /agentgear profession social_entertainer | 31 | 31 | 31 / 0 / 0 / 0 |
| 6 | P1 | crafting_artisan | /agentgear profession crafting_artisan | 3 | 3 | 1 / 1 / 0 / 1 |
| 7 | P2 | combat_rifleman | /agentgear profession combat_rifleman | 13 | 13 | 13 / 0 / 0 / 0 |
| 8 | P2 | combat_pistol | /agentgear profession combat_pistol | 12 | 12 | 12 / 0 / 0 / 0 |
| 9 | P2 | combat_1hsword | /agentgear profession combat_1hsword | 12 | 12 | 12 / 0 / 0 / 0 |
| 10 | P2 | social_dancer | /agentgear profession social_dancer | 20 | 20 | 19 / 1 / 0 / 0 |
| 11 | P2 | social_musician | /agentgear profession social_musician | 17 | 17 | 16 / 1 / 0 / 0 |
| 12 | P2 | outdoors_ranger | /agentgear profession outdoors_ranger | 3 | 3 | 3 / 0 / 0 / 0 |
| 13 | P2 | science_doctor | /agentgear profession science_doctor | 7 | 7 | 1 / 6 / 0 / 0 |
| 14 | P2 | outdoors_squadleader | /agentgear profession outdoors_squadleader | 7 | 7 | 7 / 0 / 0 / 0 |
| 15 | P2 | combat_smuggler | /agentgear profession combat_smuggler | 4 | 4 | 4 / 0 / 0 / 0 |
| 16 | P2 | outdoors_bio_engineer | /agentgear profession outdoors_bio_engineer | 1 | 1 | 1 / 0 / 0 / 0 |
| 17 | P2 | outdoors_creaturehandler | /agentgear profession outdoors_creaturehandler | 3 | 3 | 1 / 0 / 0 / 2 |
| 18 | P2 | social_imagedesigner | /agentgear profession social_imagedesigner | 0 | 0 | 0 / 0 / 0 / 0 |
| 19 | P2 | social_politician | /agentgear profession social_politician | 3 | 3 | 0 / 0 / 0 / 3 |
| 20 | P3 | combat_carbine | /agentgear profession combat_carbine | 15 | 15 | 15 / 0 / 0 / 0 |
| 21 | P3 | combat_2hsword | /agentgear profession combat_2hsword | 11 | 11 | 11 / 0 / 0 / 0 |
| 22 | P3 | combat_polearm | /agentgear profession combat_polearm | 12 | 12 | 12 / 0 / 0 / 0 |
| 23 | P3 | combat_unarmed | /agentgear profession combat_unarmed | 14 | 14 | 2 / 1 / 11 / 0 |
| 24 | P3 | combat_commando | /agentgear profession combat_commando | 8 | 8 | 8 / 0 / 0 / 0 |
| 25 | P3 | combat_bountyhunter | /agentgear profession combat_bountyhunter | 12 | 12 | 12 / 0 / 0 / 0 |
| 26 | P3 | science_combatmedic | /agentgear profession science_combatmedic | 3 | 3 | 3 / 0 / 0 / 0 |
| 27 | P4 | crafting_armorsmith | /agentgear profession crafting_armorsmith | 0 | 0 | 0 / 0 / 0 / 0 |
| 28 | P4 | crafting_weaponsmith | /agentgear profession crafting_weaponsmith | 0 | 0 | 0 / 0 / 0 / 0 |
| 29 | P4 | crafting_chef | /agentgear profession crafting_chef | 0 | 0 | 0 / 0 / 0 / 0 |
| 30 | P4 | crafting_tailor | /agentgear profession crafting_tailor | 0 | 0 | 0 / 0 / 0 / 0 |
| 31 | P4 | crafting_architect | /agentgear profession crafting_architect | 0 | 0 | 0 / 0 / 0 / 0 |
| 32 | P4 | crafting_droidengineer | /agentgear profession crafting_droidengineer | 0 | 0 | 0 / 0 / 0 / 0 |
| 33 | P4 | crafting_merchant | /agentgear profession crafting_merchant | 0 | 0 | 0 / 0 / 0 / 0 |
| 34 | P4 | crafting_shipwright | /agentgear profession crafting_shipwright | 0 | 0 | 0 / 0 / 0 / 0 |
| 35 | P5 | jedi_padawan | /agentskill jedi_padawan_master | 24 | 24 | 18 / 6 / 0 / 0 |
| 36 | P5 | jedi_light_side_journeyman | /agentskill jedi_light_side_journeyman_master | 33 | 33 | 25 / 8 / 0 / 0 |
| 37 | P5 | jedi_light_side_master | /agentskill jedi_light_side_master_master | 21 | 21 | 13 / 8 / 0 / 0 |
| 38 | P5 | jedi_dark_side_journeyman | /agentskill jedi_dark_side_journeyman_master | 29 | 29 | 21 / 8 / 0 / 0 |
| 39 | P5 | jedi_dark_side_master | /agentskill jedi_dark_side_master_master | 25 | 25 | 17 / 8 / 0 / 0 |
| 40 | P5 | force_sensitive_combat_prowess | blocked (force_sensitive_combat_prowess_master needs Jedi state 1) | 0 | 0 | 0 / 0 / 0 / 0 |
| 41 | P5 | force_sensitive_enhanced_reflexes | blocked (force_sensitive_enhanced_reflexes_master needs Jedi state 1) | 0 | 0 | 0 / 0 / 0 / 0 |
| 42 | P5 | force_sensitive_crafting_mastery | blocked (force_sensitive_crafting_mastery_assembly_01 needs Jedi state 1) | 0 | 0 | 0 / 0 / 0 / 0 |
| 43 | P5 | force_sensitive_heightened_senses | blocked (force_sensitive_heightened_senses_healing_01 needs Jedi state 1) | 0 | 0 | 0 / 0 / 0 / 0 |
| 44 | P5 | force_title_jedi | blocked (force_title_jedi_master needs Jedi state 1) | 0 | 0 | 0 / 0 / 0 / 0 |
| 45 | P5 | force_discipline_light_saber | blocked (force_discipline_light_saber_master needs Jedi state 2) | 38 | 38 | 0 / 0 / 0 / 38 |
| 46 | P5 | force_discipline_powers | blocked (force_discipline_powers_debuff_01 needs Jedi state 2) | 20 | 20 | 0 / 0 / 0 / 20 |
| 47 | P5 | force_discipline_healing | blocked (force_discipline_healing_damage_01 needs Jedi state 2) | 31 | 31 | 0 / 0 / 0 / 31 |
| 48 | P5 | force_discipline_enhancements | blocked (force_discipline_enhancements_master needs Jedi state 2) | 22 | 22 | 0 / 0 / 0 / 22 |
| 49 | P5 | force_discipline_defender | blocked (force_discipline_defender_force_defense_01 needs Jedi state 2) | 1 | 1 | 0 / 0 / 0 / 1 |
| 50 | P5 | force_rank_light | blocked (force_rank_light_master needs Jedi state 4) | 0 | 0 | 0 / 0 / 0 / 0 |
| 51 | P5 | force_rank_dark | blocked (force_rank_dark_master needs Jedi state 8) | 0 | 0 | 0 / 0 / 0 / 0 |
| 52 | P6 | pilot_rebel_navy | /agentgear profession pilot_rebel_navy | 10 | 10 | 0 / 0 / 0 / 10 |
| 53 | P6 | pilot_imperial_navy | /agentgear profession pilot_imperial_navy | 6 | 6 | 0 / 0 / 0 / 6 |
| 54 | P6 | pilot_neutral | /agentgear profession pilot_neutral | 7 | 7 | 0 / 0 / 0 / 7 |

Phases: P1 starters; P2 elites whose weapons and items exist today; P3 elites that need new weapon or medicine kits; P4 crafting elites (grant check only); P5 Jedi and Force; P6 space (cannot be tried on the ground).

## Readiness with today's bot tooling

`ready` = can be tried with `/agentgear` kits, `/agentskill`, a creature to fight and a second bot. `needs_new_kit` = an item or weapon `/agentgear` does not give. `needs_staging` = a situation the scenario must build (corpse, downed ally, building, survey point). `blocked_world` = city/pet/vehicle. `blocked_space` = ship. `blocked_jedi` = every profession that grants it needs Jedi state or the Jedi manager.

| test kind | ready | needs_staging | needs_new_kit | blocked_world | blocked_jedi | blocked_space | n/a_passive |
|---|---|---|---|---|---|---|---|
| self | 33 | 11 | 0 | 2 | 19 | 0 | 0 |
| attack | 188 | 1 | 17 | 0 | 16 | 0 | 0 |
| heal_other | 6 | 19 | 0 | 0 | 0 | 0 | 0 |
| target_friendly | 3 | 1 | 0 | 1 | 1 | 0 | 0 |
| item | 11 | 2 | 0 | 3 | 0 | 0 | 0 |
| crafting | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| performance | 53 | 0 | 0 | 0 | 0 | 0 | 0 |
| passive | 0 | 0 | 0 | 0 | 0 | 0 | 507 |
| unknown | 0 | 0 | 0 | 0 | 0 | 22 | 0 |
| total | 294 | 34 | 17 | 6 | 36 | 22 | 507 |

Kits the scenario needs that `/agentgear` does not have (proposed names; templates are candidates and not tried):

| proposed kit | candidate templates | abilities it unlocks | which (first 12) |
|---|---|---|---|
| unarmed | (no weapon: unequip the current one with transferItemWeapon) | 17 | unarmedBlind1, unarmedBodyHit1, unarmedCombo1, unarmedCombo2, unarmedDizzy1, unarmedHeadHit1, unarmedHit1, unarmedHit2, unarmedHit3, unarmedKnockdown1, unarmedKnockdown2, unarmedLegHit1 |

## Weapon classes and candidate templates

Every species starts with these certifications: cert_axe_heavy_duty, cert_carbine_cdef, cert_grenade_fragmentation_light, cert_knife_stone, cert_knife_survival, cert_lance_staff_wood_s1, cert_pistol_cdef, cert_rifle_cdef.

| weapon class | templates | species-cert usable | species-cert candidates | other candidates [cert <- box that grants it] |
|---|---|---|---|---|
| unarmed | 4 | 0 | - | object/weapon/melee/special/blacksun_razor.iff [cert_vibroknuckler <- combat_unarmed_novice] |
| 1h melee | 23 | 3 | object/weapon/melee/knife/knife_stone.iff (cert_knife_stone)<br>object/weapon/melee/knife/knife_stone_noob.iff (cert_knife_stone) | object/weapon/melee/baton/baton_stun.iff [cert_baton_stun <- combat_1hsword_novice]<br>object/weapon/melee/knife/knife_dagger.iff [cert_knife_dagger <- combat_brawler_novice]<br>object/weapon/melee/baton/baton_gaderiffi.iff [cert_baton_gaderiffi <- combat_brawler_1handmelee_01] |
| 2h melee | 11 | 1 | object/weapon/melee/axe/axe_heavy_duty.iff (cert_axe_heavy_duty) | object/weapon/melee/2h_sword/2h_sword_maul.iff [cert_sword_2h_maul <- combat_2hsword_novice]<br>object/weapon/melee/2h_sword/2h_sword_battleaxe.iff [cert_sword_2h_axe <- combat_brawler_2handmelee_01]<br>object/weapon/melee/2h_sword/2h_sword_blacksun_hack.iff [combat_2hsword_speed_02 <- no profession box grants it] |
| polearm | 14 | 2 | object/weapon/melee/polearm/lance_staff_janta.iff (cert_lance_staff_wood_s1)<br>object/weapon/melee/polearm/lance_staff_wood_s1.iff (cert_lance_staff_wood_s1) | object/weapon/melee/polearm/lance_nightsister.iff [cert_lance_vibrolance <- combat_polearm_novice]<br>object/weapon/melee/polearm/lance_controllerfp.iff [cert_lance_controllerfp <- combat_brawler_polearm_02]<br>object/weapon/melee/polearm/lance_staff_metal.iff [cert_lance_staff_metal <- combat_brawler_polearm_01] |
| pistol | 23 | 3 | object/weapon/ranged/pistol/pistol_cdef.iff (cert_pistol_cdef)<br>object/weapon/ranged/pistol/pistol_cdef_corsec.iff (cert_pistol_cdef) | object/weapon/ranged/pistol/pistol_d18.iff [cert_pistol_d18 <- combat_marksman_novice]<br>object/weapon/ranged/pistol/pistol_dx2.iff [cert_pistol_dx2 <- combat_pistol_novice]<br>object/weapon/ranged/pistol/pistol_republic_blaster.iff [cert_pistol_republic_blaster <- combat_pistol_novice] |
| carbine | 13 | 2 | object/weapon/ranged/carbine/carbine_cdef.iff (cert_carbine_cdef)<br>object/weapon/ranged/carbine/carbine_cdef_corsec.iff (cert_carbine_cdef) | object/weapon/ranged/carbine/carbine_dh17.iff [cert_carbine_dh17 <- combat_marksman_novice]<br>object/weapon/ranged/carbine/carbine_elite.iff [cert_carbine_elite <- combat_carbine_novice]<br>object/weapon/ranged/carbine/carbine_nym_slugthrower.iff [cert_carbine_nym_slugthrower <- combat_carbine_novice] |
| rifle | 17 | 1 | object/weapon/ranged/rifle/rifle_cdef.iff (cert_rifle_cdef) | object/weapon/ranged/rifle/rifle_dlt20.iff [cert_rifle_dlt20 <- combat_marksman_novice]<br>object/weapon/ranged/rifle/rifle_t21.iff [cert_rifle_t21 <- combat_rifleman_novice]<br>object/weapon/ranged/rifle/rifle_beam.iff [cert_rifle_beam <- no profession box grants it] |
| special heavy (flame/acid/lightning beam) | 8 | 0 | - | object/weapon/ranged/heavy/heavy_rocket_launcher.iff [cert_rocket_launcher <- combat_commando_novice]<br>object/weapon/ranged/pistol/pistol_launcher.iff [cert_pistol_launcher <- combat_commando_novice]<br>object/weapon/ranged/rifle/rifle_acid_beam.iff [cert_rifle_acid_beam <- combat_commando_novice] |
| grenade | 8 | 2 | object/weapon/ranged/grenade/grenade_bug_bomb.iff (cert_grenade_fragmentation_light)<br>object/weapon/ranged/grenade/grenade_fragmentation_light.iff (cert_grenade_fragmentation_light) | object/weapon/ranged/grenade/grenade_fragmentation.iff [cert_grenade_fragmentation <- combat_commando_novice]<br>object/weapon/ranged/grenade/grenade_cryoban.iff [cert_grenade_cryoban <- combat_commando_heavyweapon_accuracy_01]<br>object/weapon/ranged/grenade/grenade_glop.iff [cert_grenade_glop <- combat_commando_heavyweapon_accuracy_02] |
| 1h lightsaber | 99 | 0 | - | object/weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_gen1.iff [cert_onehandlightsaber_gen1 <- force_discipline_light_saber_novice]<br>object/weapon/melee/sword/sword_lightsaber_anakin.iff [cert_onehandlightsaber <- jedi_padawan_novice]<br>object/weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_gen2.iff [cert_onehandlightsaber_gen2 <- force_discipline_light_saber_one_hand_02] |
| 2h lightsaber | 75 | 0 | - | object/weapon/melee/2h_sword/crafted_saber/sword_lightsaber_two_handed_gen1.iff [cert_twohandlightsaber_gen1 <- force_discipline_light_saber_novice]<br>object/weapon/melee/2h_sword/crafted_saber/sword_lightsaber_two_handed_s1.iff [cert_twohandlightsaber <- jedi_dark_side_journeyman_novice, jedi_light_side_journeyman_novice]<br>object/weapon/melee/2h_sword/crafted_saber/sword_lightsaber_two_handed_gen2.iff [cert_twohandlightsaber_gen2 <- force_discipline_light_saber_two_hand_02] |
| polearm lightsaber | 21 | 0 | - | object/weapon/melee/polearm/crafted_saber/sword_lightsaber_polearm_gen1.iff [cert_polearmlightsaber_gen1 <- force_discipline_light_saber_novice]<br>object/weapon/melee/polearm/crafted_saber/sword_lightsaber_polearm_s1.iff [cert_polearmlightsaber <- jedi_dark_side_master_novice, jedi_light_side_master_novice]<br>object/weapon/melee/polearm/crafted_saber/sword_lightsaber_polearm_gen2.iff [cert_polearmlightsaber_gen2 <- force_discipline_light_saber_polearm_02] |

Class comes from the template's `xpType`; candidates must also have a `shared_` template in the client data (`in_client_data`). Lightsabers are not species-usable; their certs come from jedi_* / force_title boxes.

## Reference lines used by test-plan.md (generated from the current source)

| what | file | line |
|---|---|---|
| ability is required before a command runs (client error 2) | src/server/zone/managers/objectcontroller/ObjectControllerImplementation.cpp | 94 |
| an unregistered command is dropped with no reply | src/server/zone/managers/objectcontroller/ObjectControllerImplementation.cpp | 80 |
| handler result goes to onFail / onComplete | src/server/zone/managers/objectcontroller/ObjectControllerImplementation.cpp | 176 |
| command table files that define commands | src/server/zone/managers/objectcontroller/command/CommandConfigManager.h | 138 |
| Lua fields the server reads | src/server/zone/managers/objectcontroller/command/CommandConfigManager.cpp | 598 |
| return codes of a handler | src/server/zone/objects/creature/commands/QueueCommand.h | 65 |
| wrong weapon message | src/server/zone/objects/creature/commands/QueueCommand.cpp | 180 |
| Jedi armor message | src/server/zone/objects/creature/commands/QueueCommand.cpp | 194 |
| cooldown message | src/server/zone/objects/creature/commands/QueueCommand.cpp | 381 |
| combat: out of range message | src/server/zone/objects/creature/commands/CombatQueueCommand.h | 140 |
| combat: line of sight message | src/server/zone/objects/creature/commands/CombatQueueCommand.h | 233 |
| combat: weapon type check | src/server/zone/objects/creature/commands/CombatQueueCommand.h | 166 |
| combat: hit/miss/evade spam keys | src/server/zone/objects/creature/commands/CombatQueueCommand.h | 792 |
| self buff example: success message | src/server/zone/objects/creature/commands/Berserk1Command.h | 63 |
| self buff example: failure message | src/server/zone/objects/creature/commands/Berserk1Command.h | 28 |
| performance example: success message | src/server/zone/objects/creature/commands/StartMusicCommand.h | 127 |
| performance example: no instrument | src/server/zone/objects/creature/commands/StartMusicCommand.h | 58 |
| performance effect without a performance | src/server/zone/objects/creature/commands/DazzleCommand.h | 29 |
| heal example: no line of sight | src/server/zone/objects/creature/commands/HealDamageCommand.h | 447 |
| heal example: not permitted to help | src/server/zone/objects/creature/commands/ForceHealQueueCommand.cpp | 386 |
| bot body: command_failed event | src/client/agent/AgentControl.cpp | 830 |
| bot body: command_failed reason names (index = error code) | src/client/agent/AgentControl.cpp | 820 |
| equip a weapon or instrument: /transferItemWeapon <dest oid> 4 0 0 0 | src/server/zone/objects/creature/commands/TransferItemWeaponCommand.h | 44 |
| bot body: system message event | src/client/agent/AgentControl.cpp | 701 |
| bot body: combat event | src/client/agent/AgentControl.cpp | 772 |
| bot body: posture/combat state events | src/client/agent/AgentControl.cpp | 668 |
| /agentskill: grants boxes and prerequisites, 16 per call | src/server/zone/objects/creature/commands/AgentSkillCommand.h | 59 |
| /agentskill: answer prefix | src/server/zone/objects/creature/commands/AgentSkillCommand.h | 79 |
| /agentgear: the only item kits | src/server/zone/objects/creature/commands/AgentGearCommand.h | 262 |
| /agentgear profession <name>: whole profession, no point limit | src/server/zone/objects/creature/commands/AgentGearCommand.h | 252 |
| /agentgear profession: refused for god-only or non-profession rows | src/server/zone/objects/creature/commands/AgentGearCommand.h | 186 |
| /agentgear profession clear (unlearn all) | src/server/zone/objects/creature/commands/AgentGearCommand.h | 173 |
| /agentgear profession: answer carries granted/failed/skills | src/server/zone/objects/creature/commands/AgentGearCommand.h | 210 |
| squad.py gear(): skipped when armor is already carried | outputs/tools/bots/squad.py | 396 |
| /agentgear: support kit (medic packs, camps, instrument) | src/server/zone/objects/creature/commands/AgentGearCommand.h | 104 |
| skill point cap | src/server/zone/managers/skill/SkillManager.cpp | 428 |
| Jedi state gate for boxes | src/server/zone/managers/skill/SkillManager.cpp | 940 |
| force_* boxes go through the Jedi manager | src/server/zone/managers/skill/SkillManager.cpp | 948 |
| abilities are added only when the table lists them | src/server/zone/managers/skill/SkillManager.cpp | 263 |
| weapon certification check | src/server/zone/objects/tangible/weapon/WeaponObjectImplementation.cpp | 679 |
| instrument skill check | src/server/zone/managers/skill/PerformanceManager.cpp | 289 |
| flourish ability check | src/server/zone/objects/creature/commands/FlourishCommand.h | 49 |

