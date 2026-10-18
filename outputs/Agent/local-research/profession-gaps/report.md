Written by Claude Haiku, 15 Oct 2026, from Core3-dev 90044b8e.
(The model switched mid-run; Claude Opus 5.5 finished and wrote this file. HEAD checked: 90044b8e, 2026-10-15 07:15. matrix.md was built from the older 60ed8971. The TODO lines below were re-checked on 90044b8e; the stub line ranges were not.)

# Profession gaps (pre-CU, Core3-dev)

Command paths are under `src/server/zone/objects/creature/commands/` (relative to MMOCoreORB/). `matrix.md` and `test-plan.md` are in `outputs/Claude-class-check/`. Result files are `outputs/Bot-reports/Aurek/class-check-*.json`.

## 1. Short answer

These are the most affected professions, worst first:
1. **Creature Handler**: the 17 pet-order abilities have no command row and no server reference under those names. 2 of its 3 tries are blocked because they need a pet.
2. **Politician**: 24 of its 27 abilities are passive flags, and the city_spec_* flags have no server reference. All 3 tries need a city.
3. **Image Designer**: it grants nothing to run. Its play loop is a session, and that session has an open "Needs research" TODO.
4. **Smuggler**: the five slice_* flags have no server reference.
5. **Merchant**: all 5 abilities are fee, ad and auction flags with no server reference.
6. **Bio-Engineer**: it has only one command (sampleDNA). There is no managers/genetics folder, and no bot can try tissue or DNA crafting.
7. **Artisan**: customizeVehicle is a template stub.
8. **Shipwright and the three pilot professions**: everything they have is space-only, and 22 space combat commands have no Lua script.

The combat, medic and entertainer lines only have cosmetic TODOs. "No server reference" comes from the matrix's quoted-name scan (matrix.md:125). The feature may still exist under other names (see section 5).

## 2. Per profession

**Creature Handler** (matrix.md:52: 20 abilities, 3 commands, 17 passive)
- 17 pet_flag abilities have no command row and no server reference (matrix.md:129). Examples: pet_attack, pet_follow, pet_guard, pet_patrol, pet_release, pet_specialattack1.
- tame is ungated, so any player can run it (matrix.md:117). The handler `TameCommand.h` is 80 lines, so it is not a stub (inferred from its size).
- emboldenpets and enragepets need an owned pet (matrix.md:198). Run order: 1 try ready, 2 blocked (matrix.md:336).
- No TODO or "not implemented" note was found in `src/server/zone/managers/creature/PetManagerImplementation.cpp` or `CreatureManagerImplementation.cpp`.
- What this blocks: taming can be run, but the whole pet-command half of the loop is unproven.

**Politician** (matrix.md:67: 27 abilities, 3 commands, 24 passive, skill points 0/0)
- 13 permission flags have no server reference (matrix.md:128). They include access_fee and city_spec_cloning, _doctor, _entertainer, _industry, _missions, _research, _sample_rich and _stronghold.
- grantZoningRights, installMissionTerminal and recruitSkillTrainer need a city where the bot is mayor or militia (matrix.md:160). All 3 tries are blocked (matrix.md:338). grantZoningRights is also ungated (matrix.md:117).
- `src/server/zone/managers/city/CityManagerImplementation.cpp:2320` has a TODO, but it is about mail only and does not block anything.
- Outside the profession grants there are 157 template-stub command rows, described as "staff/admin, city, vendor or client-side" (matrix.md:101). matrix.md does not say which city commands are among them.
- What this blocks: no bot has a city, so the whole loop is untested, and the city specialisations are unproven.

**Image Designer** (matrix.md:65: 0 abilities, 0 commands, 0 schematics)
- There is no `ImageDesignCommand.h` in the commands folder.
- `src/server/zone/objects/player/sessions/ImageDesignSessionImplementation.cpp:435` has the note "TODO: Needs research."
- class-check-social_imagedesigner.json has an empty `results` list: there was nothing to try.
- What this blocks: the class check cannot see this profession at all. The session, which is the whole loop (inferred), is untested.

**Smuggler** (matrix.md:61: 11 abilities, 4 commands)
- Five feature flags have no server reference (matrix.md:126): slice_armor, slice_containers, slice_terminals, slice_weaponsadvanced and slice_weaponsbasic. matrix.md does not say which boxes grant them; that they are Smuggler boxes is inferred. sneak has no reference either (matrix.md:127).
- All 4 commands are ready to try (matrix.md:334). None has been tried.

**Merchant** (matrix.md:60: 5 abilities, all passive, 0 commands)
- merchant_fees_1, ad_fees_1, premium_auctions and access_fee have no server reference (matrix.md:128).
- `CreateVendorCommand.h` exists (68 lines). The only TODO in `src/server/zone/managers/vendor/VendorManager.cpp:583` is about random hair, which is cosmetic.
- What this blocks: vendors probably work (inferred), but the fee, ad and auction perks are unproven. The bots can only check that the grant worked (test-plan.md:13).

**Bio-Engineer** (matrix.md:53: 1 command, 12 schematic groups)
- sampleDNA is ungated (matrix.md:117) and needs a live creature (matrix.md:164). `SampleDNACommand.h` is 113 lines.
- `src/server/zone/managers/genetics` does not exist. I did not find where tissue and DNA combining lives.
- The bot body has no crafting session (test-plan.md:13), so tissue and DNA crafting cannot be tested by a bot.

**Artisan** (matrix.md:38: 2 stubs)
- customizeVehicle is a template stub, with the note "treat as unimplemented" (matrix.md:96; `CustomizeVehicleCommand.h:16-25`).
- survey is also a stub, but it is not a real gap: the real gate is the survey tool (matrix.md:97; SurveyToolImplementation.cpp:45, cited in test-plan.md:115).

**Scout / Ranger**
- The areatrack_animal, _direction, _distance, _npc and _player flags have no server reference (matrix.md:126). `AreatrackCommand.h` exists (75 lines), so the flags may be read under other names (inferred).
- `ThrowTrapCommand.h` exists (145 lines). I did not check camps.

**Squad Leader** (matrix.md:66: 7 commands, all self, need a group)
- `VolleyFireAttackCommand.h:25` has a TODO saying the 'volleyfire' skill mod "has no effect atm".
- All 7 tries are ready (matrix.md:333), but the tester must lead a group (matrix.md:168). None has been tried.

**Droid programs** (droid_find, droid_track): neither has a server reference (matrix.md:127). That they belong to Droid Engineer is inferred.

**Shipwright / pilots**
- Shipwright: all 18 abilities are passive, plus 18 schematic groups (matrix.md:85).
- Pilots: 22 space-only commands (matrix.md:123). None has a Lua script, so defaults apply (matrix.md:120). `InstallShipComponentCommand.h:38` has a TODO.

**Jedi / Force**: the 12 force_* professions need a Jedi state, and the Force abilities are blocked (matrix.md:166, :278-289). This is a test gap, not a code gap I found.

**Minor TODOs (they do not block the play loop)**
- `SurpriseShotCommand.h:42`: the alertness check, noted as "broken Pre-CU" (rifleman).
- `PowerBoostCommand.h:31`: powerboost cancel.
- `HealDamageCommand.h:312`: area targets.
- `HealWoundCommand.h:314`: text.
- `RevivePlayerCommand.h:109` and `RegainConsciousnessCommand.h:39`, `:48`: end messages.
- `DeathBlowCommand.h:37`: animations.
- `ChangeMusicCommand.h:33`: outro check.
- `TransferstructureCommand.h:166`: a bare TODO.

## 3. What the class check has proven

Counts are result rows per file (verdict fields counted):

| profession | WORKS | RAN | BLOCKED | NOT_GRANTED | NO_EFFECT | note |
|---|---|---|---|---|---|---|
| combat_marksman | 46 | 2 | 1 | 0 | 0 | 49 rows for 25 planned tries (matrix.md:320); retries or controls (inferred) |
| science_medic | 10 | 0 | 6 | 0 | 0 | |
| outdoors_scout | 2 | 2 | 1 | 0 | 0 | |
| outdoors_ranger | 0 | 4 | 1 | 0 | 0 | the BLOCKED reason is "ally out of healing range" |
| science_doctor | 0 | 0 | 7 | 0 | 0 | bots were "in another scene"; 1 needs a medical/entertainment building |
| combat_brawler | 0 | 0 | 32 | 0 | 0 | 29 rows say "RunStopped: owner requested halt" |
| combat_rifleman | 0 | 0 | 13 | 0 | 0 | 13 rows say owner halt |
| combat_pistol | 0 | 0 | 12 | 0 | 0 | 12 rows say owner halt |
| social_imagedesigner | - | - | - | - | - | empty results (nothing to try) |
| P0 control | - | - | - | - | - | empty results, `completed: false` |

- No file has a NOT_GRANTED or NO_EFFECT verdict.
- The reason "missing ability or not allowed" appears 2 to 3 times in the brawler, pistol, rifleman, doctor and ranger files, but never as a verdict. These are probably the start-of-run controls (inferred, test-plan.md:120).
- Real evidence exists only for marksman, medic and part of scout. The P0 negative control never finished. test-plan.md:119 says nothing counts until it passes.

**Untested (45 of 54):**
- Starters: entertainer, artisan.
- P2: 1hsword, dancer, musician, squadleader, smuggler, bio_engineer, creaturehandler, politician.
- P3: carbine, 2hsword, polearm, unarmed, commando, bountyhunter, combatmedic.
- All 8 crafting professions, the 5 jedi_* professions, the 12 force_* professions and the 3 pilot_* professions.

Brawler, rifleman, pistol and doctor have result files but no usable result.

## 4. Suggested order to fill the gaps (most player-visible first)

1. **Creature Handler pet orders.** First find where pet orders are handled. A bot can try tame today, but tame is ungated, so a success is weak evidence. The pet commands need a pet.
2. **Politician / city.** A bot cannot test this until a city exists for it. Staging one by staff is inferred to be possible.
3. **Image Designer session.** There is no bot path (no command).
4. **Smuggler slicing.** A bot can try the 4 smuggler commands today, but not slicing.
5. **Merchant perks.** There is no bot path.
6. **Bio-Engineer DNA and tissue.** sampleDNA is ready; the crafting is not.
7. **Artisan customizeVehicle.** Needs a vehicle (matrix.md:202).
8. **Squad Leader volleyfire mod.** All 7 commands are ready.
9. **Space.** There is no bot path.

**What a bot can test today** (ready / tries, matrix.md:320-345):
- Run P0 first.
- Then re-run brawler 26/32, rifleman 13/13 and pistol 12/12, which were halted.
- Then: entertainer 31/31, squad leader 7/7, smuggler 4/4, bio-engineer 1/1, dancer 19/20, musician 16/17, 1h sword 12/12, carbine 15/15, 2h sword 11/11, polearm 12/12, commando 8/8, bounty hunter 12/12, combat medic 3/3.

test-plan.md:45 says P3 is mostly blocked on kits. The newer matrix lists those P3 runs as ready, so this list uses the matrix numbers.

## 5. Open questions

- Pet orders, slicing, area tracking, city specialisations and merchant perks may be handled under other names. The matrix scan only matched quoted names (matrix.md:125). I did not check how PetManager receives orders.
- Which of the 157 template-stub rows (matrix.md:101) are city or vendor commands that players use? matrix.md does not list them, and I did not read commands.json.
- Where is the Bio-Engineer DNA and tissue code, given that there is no managers/genetics folder?
- What does the TODO at `ImageDesignSessionImplementation.cpp:435` cover? I did not read it.
- I did not check Scout and Ranger camps.
- Why does marksman have 49 result rows for 25 tries? Why did P0 not finish?
- The stub line ranges in matrix.md were not re-read on 90044b8e. CustomizeVehicleCommand.h and SurveyCommand.h are both 29 lines there.


## ChatGPT's review (2026-10-18 02:30)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) (this topic has no `src/` snapshot); no in-game checks. The original draft remains above; corrections below take precedence.

**Holds as historical inventory:** the matrix really lists 17 pet flags, the city/merchant flags, zero named Image Designer commands and template-stub customizeVehicle (outputs/Claude-class-check/matrix.md:60-65,96-97,117-129). This establishes limitations of a quoted-name/slash-command audit, not absent gameplay. ImageDesignSessionImplementation.cpp:435 does contain the cited TODO.

**Corrections/current-source counterexamples:**
- Tame is not unrestricted gameplay just because its command-table characterAbility is empty. CreatureManagerImplementation.cpp:1113-1132 checks canTameMe/attackability, novice Creature Handler, tame_level and viciousness/tame chance. Only the explicitly gated TameAnything test path changes those requirements (1099-1112).
- Pet orders have a training and dispatch implementation (PetManagerImplementation.cpp:315-343,473-504). Missing pet_* literal references do not prove missing pet commands.
- Slicing checks real smuggler skill boxes under different names and awards slicing XP (SlicingSessionImplementation.cpp:245-261,473-486). 'No slice_* literal' cannot rank Smuggler as unimplemented.
- The missing managers/genetics folder is irrelevant: GeneticLabratory.cpp:187,549 implements initial values and experimentation under managers/crafting/labratories.
- The Image Designer TODO is on rejection cleanup (ImageDesignSessionImplementation.cpp:420-437), not a statement that the whole session is absent.
- The blanket 'bot body has no crafting session' is stale: AgentControl.cpp:987 handles the crafting schematic-list/session packet. Current crafting coverage must be checked separately, not inferred from the old test-plan limitation.
- All result counts/readiness rankings above are a 15 Oct snapshot. No current acceptance claim follows from them; later runs and source changes supersede them. Empty results/owner-halted runs are missing evidence, not failed game mechanics. File length and absence of TODOs are not proof of correctness.

**Verdict scope:** retain the matrix as a historical command/test coverage index only. The proposed worst-first defect ranking and 'any player can run' conclusion are not accepted. No new profession gameplay was tested.

**Verdict:** Reject as a current defect ranking; historical matrix facts hold, but literal-name scans, missing directories and empty command gates do not establish missing mechanics.
