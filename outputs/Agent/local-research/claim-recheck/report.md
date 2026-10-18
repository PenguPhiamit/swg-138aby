# Claim recheck: saluki against qwen3.5:9b (draft)

18 Oct 1:20 AM. The claims the first claim check (report-precheck, qwen3.5:9b) called contradicted or not shown, asked again with the same instruction of saluki (Underdog Saluki 27B 1.0, Qwen3.8 27B at IQ2, on the friend's PC, 2.8 min for all). wen-turbo (Qwen3.8 27B Q4_K_M, this PC) did the first chunks before it was stopped for being slow; its verdicts are shown where it has one.
On the 24-claim test (18 Oct) saluki was the strictest of the three and right on 4 of 7 disputed claims against wen-turbo's 2 and qwen's 2; it repeated qwen's misreading of an `!= nullptr` guard. A changed verdict is a place to look, not an answer: Claude checks each against the code.

130 claims: 70 changed, 60 kept. contradicted -> contradicted: 10, contradicted -> not shown: 7, contradicted -> supported: 11, not shown -> contradicted: 4, not shown -> not shown: 50, not shown -> supported: 48.

## Claude's check (18 Oct 1:50 AM)

Claude read all 70 changed verdicts against the code lines the models were given (`input.jsonl`), judging them by the same rule as the models.

**Right: 62 of 70.** Saluki cleared about 55 of qwen3.5:9b's false alarms. It read `!= nullptr` guards, message names and numbers correctly.

**Wrong: 6.**
- **player-vendors#13**, changed to supported. Line 514 sends `@player_structure:vendor_maint_denied`, so "fails silently" is contradicted. qwen was right.
- **structure-placement#28**, changed to not shown. Line 470 constructs and line 473 then destroys the deed. "Destroys the deed before calling constructStructure" is therefore contradicted, and qwen was right.
- **profession-gaps#13**, changed to contradicted. Line 39 is the TODO the claim names. Saluki called the same kind of line supported in #12.
- **fishing#17**, changed to supported. Line 43 only defines `NOTFISHING = 0`; the session ending is not shown.
- **image-design#21** and **medic-xp-healing#40**, changed to contradicted. The lines shown don't contain the rest of each claim, so the answer is not shown.

**Borderline: 3.** fishing#20, resource-quality#23 and travel-shuttles#6 have only part of the claim shown.

**Can't judge: player-vendors#3.** Its claim text is cut off before the sentence its citation supports, because claim-check cuts claims at 400 characters.

**Kept verdicts (sampled).**
- Both models called 10 contradicted. Six of those hold.
- resources#18 and npc-conversations#25 are too strict: the numbers match, and only the labels or packet names are not shown.
- contraband-scans#25 is wrong for both models, and #27 rests on the same mistake. Both trusted the source comment "10 iterations = 10 s". In fact the scan task repeats every `TASKDELAY` = 2000 ms or more (ContrabandScanSessionImplementation.cpp:144-145), so `SCANTIME` and `TIMETORETURNFORSCAN` are each at least 20 s, and the research claims of 20 s hold.
- Of 8 sampled "not shown" verdicts both models agreed on, all 8 hold.

**Verdict.** Saluki is a good first pass: about 9 in 10 right here, at 43 tokens/s. But it errs in both directions and follows stale comments, so Claude still checks a report before anyone quotes it.

## Changed verdicts

- **bazaar-flow#2**: qwen3.5:9b not shown (Cited code shows buyItem, not search listing query.); saluki supported (Code shows getData with locationType, searchType, itemCategory matching claim.); wen-turbo supported
- **bazaar-flow#4**: qwen3.5:9b contradicted (Code shows buying an item, not selling or searching.); saluki not shown (Code shows buyItem, not CreateImmediateAuctionMessage or addSaleItem.); wen-turbo not shown
- **bazaar-flow#28**: qwen3.5:9b contradicted (Code proceeds only if auctionManager is NOT nullptr, not when it is.); saluki supported (Code shows null check and addSaleItem call as claimed.); wen-turbo supported
- **bounty-hunter#11**: qwen3.5:9b contradicted (Code shows time 20 subtracts 15, not matching claim.); saluki supported (Code shows t=20 case sending exact message at line 57.); wen-turbo supported
- **camps#23**: qwen3.5:9b contradicted (Cited lines show addActiveArea, not player seeing message.); saluki supported (Code shows player->sendSystemMessage("@camp:camp_complete") at line 307.); wen-turbo supported
- **combat-states#5**: qwen3.5:9b not shown (Cited lines show posture setting but do not define knockdown duration.); saluki supported (Code shows setPosture(KNOCKEDDOWN) but no duration logic.); wen-turbo not shown
- **containers-inventory#34**: qwen3.5:9b not shown (Cited line checks limit but implementation of getContainerVolumeLimit is missing.); saluki supported (Code shows getContainerVolumeLimit() call but no implementation.); wen-turbo not shown
- **containers-inventory#35**: qwen3.5:9b not shown (Code shows parameter definition and check, but not where it is set to true.); saluki supported (Code shows allowOverflow param but no usage setting it true.); wen-turbo not shown
- **containers-inventory#37**: qwen3.5:9b not shown (Code validates parent type, but does not show limit propagation logic.); saluki supported (Code checks parent ContainerType::NONE but no limit propagation.); wen-turbo not shown
- **contraband-scans#11**: qwen3.5:9b not shown (Cited lines define constants but do not show jediDetect() logic or reductions.); saluki supported (Code shows JEDIAVOIDDETECTIONBASECHANCE = 80 at line 22.); wen-turbo supported
- **contraband-scans#22**: qwen3.5:9b not shown (Cited lines define constants; code for faction decrease is in Implementation.cpp, not Idl.); saluki supported (Code shows WAITFORPAYFINEANSWERTIMEOUT = 60 at line 20.); wen-turbo supported
- **contraband-scans#27**: qwen3.5:9b not shown (Cited lines do not mention player moving out of range/LOS logic.); saluki contradicted (Code comment says 10 iterations = 10 s, not 20 seconds.); wen-turbo contradicted
- **crafting-factories#17**: qwen3.5:9b not shown (Cited line calls function but does not show its implementation or logic.); saluki supported (Code shows call at line 706 with type and displayedName args.); wen-turbo supported
- **crafting-factories#18**: qwen3.5:9b not shown (Cited line calls function but does not show its implementation or calculation details.); saluki supported (Code shows updateMaintenance call at line 684 with timeToWorkTill.); wen-turbo supported
- **cure-poison#10**: qwen3.5:9b not shown (Cited lines show poison/disease checks, not healer message order.); saluki supported (Code shows canPerformSkill checks state, target condition, and sends healer messages.); wen-turbo supported
- **cure-poison#13**: qwen3.5:9b not shown (Cited code lacks message logic; claim about missing message not proven here.); saluki supported (Code shows playerEntryCheck returns false without sending any message.); wen-turbo supported
- **cure-poison#31**: qwen3.5:9b contradicted (Code checks for healing rise, not poison loss or power thresholds.); saluki not shown (Code shows HAM rise check, not poisoned state loss or power threshold.); wen-turbo not shown
- **cure-poison#33**: qwen3.5:9b contradicted (Code swaps kit items; it does not define wait times or healer text logic.); saluki not shown (Code shows kit manipulation, not wait time calculation.); wen-turbo not shown
- **cure-poison#37**: qwen3.5:9b not shown (Cited lines show gear-kit logic, not cure pack name or inventory full handling.); saluki supported (Code shows gear-kit logic, confirming claim about incomplete reading.); wen-turbo not shown
- **doctor-enhance-wounds#5**: qwen3.5:9b contradicted (Code shows adding/removing mods, not checking private_medical_rating > 0 or ignoring room/cell checks.); saluki not shown (Code shows droid skill mod addition, not doctor command checks.); wen-turbo not shown
- **doctor-enhance-wounds#10**: qwen3.5:9b not shown (Cited lines show staticObject=false but do not mention createClientObject or onEnter.); saluki supported (Code shows super.staticObject = false at line 75.); wen-turbo supported
- **entertainer-buffs#15**: qwen3.5:9b not shown (Code shows usage of constant but does not define its value.); saluki supported (Code shows PerformanceManager::HEAL_RANGE used in isInRange check.); wen-turbo supported
- **factions#4**: qwen3.5:9b contradicted (Cited lines show setFactionStatus(1) but claim cites wrong line range 36-37 for both actions.); saluki supported (Code shows setFaction with hash and setFactionStatus(1) exactly as claimed.); wen-turbo supported
- **fishing#17**: qwen3.5:9b not shown (Cited line defines NOTFISHING constant, not session end logic.); saluki supported (Code shows NOTFISHING = 0 constant definition.); wen-turbo not shown
- **fishing#20**: qwen3.5:9b not shown (Cited lines show registration, not the immediate stop logic.); saluki supported (Code registers PLAYERKILLED and STARTCOMBAT observers on player.); wen-turbo supported
- **groups#1**: qwen3.5:9b contradicted (Code shows 80ft limit in claim but code checks for 128.f range.); saluki supported (Code shows group size cap at 20 with full message check.); wen-turbo supported
- **groups#35**: qwen3.5:9b contradicted (Claim says buttons are @group:ok/@group:leave_group; code shows @group:ok/@group:leave_group but title is correct, however claim implies non-leader members receive it which matches code logic. Wait, re-reading claim vs code: Claim says 'non-leader members receive...'. Code at 652 creates box for 'member' (looping group members). This seems supported actually. Let me re-evaluate strictly.); saluki supported (Code matches SUI box title, prompt, and button labels exactly.); wen-turbo supported
- **ham#3**: qwen3.5:9b not shown (Cited lines show function calls but not regeneration rules.); saluki supported (Code shows activateHAMRegeneration(latency) called at line 2408.); wen-turbo supported
- **ham#18**: qwen3.5:9b not shown (Cited lines show Power Boost ticks, not max differences or fixHAM.); saluki supported (Code shows addMaxHAM for HEALTH, ACTION, MIND with pbTick.); wen-turbo supported
- **harvester-operation#32**: qwen3.5:9b contradicted (Cited lines show item 78 added to radial menu in InstallationObjectImplementation, not HarvesterObjectImplementation.); saluki supported (Code shows addRadialMenuItemToRadialID(118, 78, 3, "@harvester:manage").); wen-turbo supported
- **image-design#21**: qwen3.5:9b not shown (Cited lines show XP minimums but omit halving logic for same person.); saluki contradicted (Code shows 300/100 minimums but no 2000 stat migration or halving logic.); wen-turbo not shown
- **medic-xp-healing#1**: qwen3.5:9b not shown (Cited lines show variable retrieval, not the minimum usage check logic.); saluki supported (Line 88 shows medicineUse from healing_ability skill mod.); wen-turbo supported
- **medic-xp-healing#2**: qwen3.5:9b not shown (Cited lines show variable retrieval, not the minimum usage check logic.); saluki supported (Line 202 shows medicineUse from healing_ability skill mod.); wen-turbo supported
- **medic-xp-healing#3**: qwen3.5:9b not shown (Cited lines show variable retrieval, not the minimum usage check logic.); saluki supported (Line 136 shows medicineUse from healing_ability skill mod.); wen-turbo supported
- **medic-xp-healing#11**: qwen3.5:9b not shown (Cited lines show message sending but do not confirm target bar increases.); saluki supported (Line 234 shows 'You heal <name> for...' message to player.); wen-turbo supported
- **medic-xp-healing#40**: qwen3.5:9b not shown (Cited code calculates power*0.25 but does not show healDamage() return value or clamping logic.); saluki contradicted (Code multiplies power by 0.25, not (healthHealed + actionHealed).)
- **npc-conversations#36**: qwen3.5:9b not shown (Code shows arg2 usage but does not define the packet structure.); saluki supported (Code shows selectedOption = arg2 at line 51, matching claim.)
- **player-vendors#1**: qwen3.5:9b contradicted (Code shows SUI list box for categories, no input box for maintenance payment shown.); saluki supported (Code shows SuiListBox with category menu items for vendor registration.)
- **player-vendors#2**: qwen3.5:9b not shown (Cited lines show start of pay function but cut off before logic completion.); saluki supported (Code shows SuiInputBox for maintenance payment with callback.)
- **player-vendors#3**: qwen3.5:9b contradicted (Code shows strike handling and deletion, not AuctionManager usage for tracking items.); saluki supported (Code shows vendor deletion after 100 days with mail notification.)
- **player-vendors#13**: qwen3.5:9b contradicted (Code sends messages on failure, not silent return.); saluki supported (Code checks bankCredits + cashCredits >= value and fails silently otherwise.)
- **player-vendors#19**: qwen3.5:9b not shown (Code shows reading items, not how players add them or set prices.); saluki supported (Code references AuctionsMap and TerminalListVector for items for sale.)
- **player-vendors#20**: qwen3.5:9b not shown (Code shows server-side item counting, not buyer interaction logic.); saluki supported (Code shows AuctionItem usage but no buyer-side interaction logic.)
- **profession-gaps#9**: qwen3.5:9b not shown (Code shows a TODO comment, not the implementation of 'powerboost cancel'.); saluki supported (Line 31 contains TODO: fix powerboost cancel, matching the claim.)
- **profession-gaps#10**: qwen3.5:9b not shown (Code shows a TODO comment, not the actual area targets logic.); saluki supported (Line 312 contains TODO about replacing with CombatManager::getAreaTargets() call.)
- **profession-gaps#12**: qwen3.5:9b not shown (Cited lines show buff addition, not end messages for grogginess.); saluki supported (Line 109 contains TODO: Find potential end message for groggy debuff.)
- **profession-gaps#13**: qwen3.5:9b not shown (Cited lines show code, not end messages.); saluki contradicted (Code shows TODO comment, not an end message.)
- **profession-gaps#14**: qwen3.5:9b not shown (Cited lines show TODO and logic, not animations.); saluki supported (Line 37 contains TODO about coup de grace animations.)
- **profession-gaps#15**: qwen3.5:9b not shown (Cited lines show closing brace and TODO, not outro check.); saluki supported (Line 33 contains TODO comment about outro check.)
- **profession-gaps#16**: qwen3.5:9b not shown (Cited line shows empty comment, not specific TODO content.); saluki supported (Line 166 contains bare TODO comment.)
- **resource-quality#3**: qwen3.5:9b not shown (Code shows weight initialization, not the specific data fields mentioned.); saluki supported (Code shows experimental properties, weights, min, max, precision, combine type.)
- **resource-quality#23**: qwen3.5:9b not shown (Code shows hidden check and value calculation, not components adding stats on top.); saluki supported (Code shows component value multiplied by contribution.)
- **resources#3**: qwen3.5:9b not shown (Cited lines show start function calls, not DB load order or pool update sequence.); saluki supported (Code shows load then shift in start().)
- **resources#14**: qwen3.5:9b not shown (Cited lines show zone selection, not pool size scaling formula.); saluki supported (Code matches random(maxpool-minpool)+minpool, capped at activeZones, zone-restricted logic.)
- **resources#31**: qwen3.5:9b not shown (Cited lines read fields but do not show inner table reading logic.); saluki supported (Code shows getStringAt(1) and getIntAt(2), matching the claim.)
- **secure-trade#3**: qwen3.5:9b not shown (Cited lines define class but do not show item-add callback logic.); saluki supported (Code shows AddItemMessageCallback class with parse and run methods.)
- **secure-trade#9**: qwen3.5:9b not shown (Code shows run() logic but does not mention sending VerifyTradeMessageCallback.); saluki supported (Code shows VerifyTradeMessageCallback with empty parse and run calling handleVerifyTradeMessage.)
- **secure-trade#11**: qwen3.5:9b not shown (Code defines AbortTradeMessageCallback class but does not show abort logic or 'any time' claim.); saluki supported (Code shows AbortTradeMessageCallback with empty parse and run method.)
- **skills-training#18**: qwen3.5:9b not shown (Cited lines show message setup but do not prove absence of other messages.); saluki supported (Code shows god-only ability grant message with skill_command_acquired_prose.)
- **slicing#12**: qwen3.5:9b not shown (Cited line 33 initializes firstCable, but range logic is missing.); saluki supported (Code shows firstCable = System::random(1) at session init.)
- **structure-placement#27**: qwen3.5:9b not shown (Cited lines show call to constructStructure, not its implementation.); saluki supported (Code shows session->constructStructure call, confirming logic is in PlaceStructureSession.)
- **structure-placement#28**: qwen3.5:9b contradicted (Deed is destroyed after calling constructStructure, contradicting claim it happens before.); saluki not shown (Code only shows deed destruction, not credit refund or constructStructure logic.)
- **structure-placement#30**: qwen3.5:9b not shown (Cited line includes header but does not show its full API or behavior.); saluki supported (Line 23 includes PlaceStructureSession.h, confirming the header reference exists.)
- **survey-sample#2**: qwen3.5:9b contradicted (Claim says lumber is 3, but code shows inorganic template uses toolType 10 and animation 'lumber'.); saluki supported (Code shows toolType = 10 for inorganic, matching the claim.)
- **survey-sample#3**: qwen3.5:9b not shown (Cited lines define tool properties, not the specific resource counts or types listed in the claim.); saluki supported (Code shows toolType = 0 for organic, matching the claim.)
- **survey-sample#11**: qwen3.5:9b contradicted (Code returns None if tool missing, not 'no mind check' leading to survey_mind.); saluki not shown (Code shows tool selection and wait, not five surveys or mind check.)
- **survey-sample#13**: qwen3.5:9b contradicted (Cited code defines forage function, not chemical tool labeling or water distinction.); saluki not shown (Code shows forage function, not liquid tool or TL file.)
- **travel-shuttles#6**: qwen3.5:9b not shown (Cited lines show ticket args but do not confirm the specific setup claims.); saluki supported (Line 27 shows point names with underscores and 'single'.)
- **vehicle-mount#14**: qwen3.5:9b not shown (Cited lines show pending task check but not the specific delay logic or message trigger.); saluki supported (Code shows pending task check and sends 'pet/pet_menu:call_delay_finish_vehicle'.)
- **vehicle-mount#17**: qwen3.5:9b not shown (Cited lines show instantiation, not internal task implementation details.); saluki supported (Code shows CallMountTask instantiation at line 106 with 'call_mount' argument.)

## Kept verdicts

- **bazaar-flow#3**: qwen3.5:9b not shown (Cited code is response message builder, not client query.); saluki not shown (Code shows createMessage internals, not AuctionQueryHeadersMessage fields.); wen-turbo not shown
- **bounty-hunter#5**: qwen3.5:9b not shown (Cited lines show move flag logic but do not mention 10-second interval or spawning distance.); saluki not shown (Code lacks 10s interval, 256 units, starport logic, and spawn trigger.); wen-turbo not shown
- **camps#38**: qwen3.5:9b not shown (Cited lines show task execution, not the specific firing conditions mentioned.); saluki not shown (Code lacks DESPAWNTIME value, 55 minutes, or abandonment logic.); wen-turbo not shown
- **containers-inventory#38**: qwen3.5:9b not shown (File included but numeric enum values are not provided in code.); saluki not shown (Code shows CANTADDTOITSELF, not CONTAINERFULL or SLOTOCCUPIED.); wen-turbo not shown
- **contraband-scans#25**: qwen3.5:9b contradicted (Code says SCANTIME=10 iterations, but comment claims 10s, not 20s.); saluki contradicted (Code shows SCANTIME = 10 iterations = 10 s, not 20 seconds.); wen-turbo contradicted
- **crafting-factories#1**: qwen3.5:9b not shown (Cited lines show function start, not the specific SUI creation or filtering logic.); saluki not shown (Lines 192-194 only show function start, no SUI details or filtering.); wen-turbo not shown
- **cure-poison#1**: qwen3.5:9b not shown (Cited lines only show constructor; missing logic for range, LOS, and pack requirements.); saluki not shown (Code only shows constructor setting state; no distance, LOS, healable, or inventory checks.); wen-turbo supported
- **cure-poison#26**: qwen3.5:9b not shown (Cited lines show JSON reply structure, not DoT stats or target restrictions.); saluki not shown (Code only shows JSON reply fields; no DoT stats, duration, or target checks.); wen-turbo not shown
- **cure-poison#27**: qwen3.5:9b not shown (Cited lines check parent relationship, not partner's poisoned state.); saluki not shown (Code shows return statement, not partner state check for poisoned.); wen-turbo not shown
- **cure-poison#28**: qwen3.5:9b contradicted (Code adds a speederbike deed, not the cure pack object.); saluki contradicted (Line 102 shows mandalorian helmet, not medpack_cure_poison_a.iff.); wen-turbo contradicted
- **cure-poison#30**: qwen3.5:9b not shown (Cited lines define medical facility locations, not the specific text string.); saluki not shown (Code shows MEDICAL_FACILITY tuple, not HEAL_TEXT or poison antidote text.); wen-turbo not shown
- **cure-poison#32**: qwen3.5:9b not shown (Cited lines map attributes; they do not mention string-table message parsing.); saluki not shown (Code shows state building, not string-table parsing or BLOCKED logic.); wen-turbo not shown
- **cure-poison#34**: qwen3.5:9b not shown (Cited lines return item data; they do not contain poisoned state checks.); saluki not shown (Code shows return statement, not poisoned state check.); wen-turbo not shown
- **cure-poison#38**: qwen3.5:9b not shown (Cited lines show dungeon door permission check, not playerEntryCheck rest.); saluki not shown (Code shows dungeon door permission check, not playerEntryCheck logic.); wen-turbo not shown
- **doctor-enhance-wounds#1**: qwen3.5:9b not shown (Cited lines handle parent assignment, not skill mod checks or thresholds.); saluki not shown (Code shows building entry logic, not skill mod checks or city exclusion.); wen-turbo not shown
- **doctor-enhance-wounds#4**: qwen3.5:9b not shown (Cited lines show calling addTemplateSkillMods, not the specific checks claimed.); saluki not shown (Code shows camp skill mod addition, not doctor command checks.); wen-turbo not shown
- **doctor-enhance-wounds#6**: qwen3.5:9b not shown (Cited code defines createClientObject but does not show the rating check logic or error messages.); saluki not shown (Code only shows createClientObject setting flag, not location logic or messages.); wen-turbo supported
- **doctor-enhance-wounds#7**: qwen3.5:9b not shown (Cited code adds city skill mods but does not show the rating checks or error message logic.); saluki not shown (Code shows skill mod addition, not createClientObject or location logic.); wen-turbo not shown
- **entertainer-buffs#16**: qwen3.5:9b not shown (Code shows loading datatable, not the specific heal values for 'basic' dance.); saluki not shown (Code shows loading logic only, not specific heal values or basic dance data.); wen-turbo supported
- **fishing#2**: qwen3.5:9b not shown (Cited lines show constructor; WAITING state and tick logic not present.); saluki not shown (Code shows constructor with 7000ms, not WAITING state or continueFishing logic.); wen-turbo supported
- **fishing#8**: qwen3.5:9b not shown (Cited lines show success logic but do not define freshness values or bait degradation mechanics.); saluki not shown (Code shows only initial null checks, not success logic or loot handling.); wen-turbo not shown
- **fishing#13**: qwen3.5:9b not shown (Cited lines show constructor but do not explicitly set state to WAITING.); saluki not shown (Code shows constructor parameters, not state WAITING assignment.); wen-turbo not shown
- **fishing#16**: qwen3.5:9b not shown (Cited code shows WAITING logic but does not show full transition sequence.); saluki not shown (Code shows WAITING/SNAGGED/NIBBLE only, not BITE/CATCH/REELING/REELGAME.); wen-turbo supported
- **food-drink-spice#3**: qwen3.5:9b not shown (Cited lines show duration load but omit flavor/add_flavor modification details.); saluki not shown (Code only shows duration set from template; no crafting flavor or add_flavor lines.); wen-turbo not shown
- **groups#39**: qwen3.5:9b not shown (Cited lines show packet creation, not the specific claim about session creation or eligibility logic.); saluki not shown (Code only shows OpenLotteryWindow creation; no 128ft check or distance message.); wen-turbo not shown
- **harvester-operation#11**: qwen3.5:9b contradicted (Code shows both active/else branches; claim implies only successful activation sets active=true.); saluki contradicted (Code lacks extractionRemainder, resourceHopperTimestamp, and broadcast to operators.); wen-turbo supported
- **image-design#19**: qwen3.5:9b not shown (Cited lines show file loading, not skill mod storage or skipping logic.); saluki not shown (Code only shows opening the iff file, not skill mod values or skip logic.); wen-turbo not shown
- **lairs-spawning#5**: qwen3.5:9b not shown (Cited IDL file shows constants, not the specific spawning logic claimed.); saluki not shown (Code shows spawn time constants, not wave 1 damage check or spawn amounts.); wen-turbo not shown
- **lairs-spawning#6**: qwen3.5:9b not shown (Cited lines show random spawn time logic, not Wave 1 damage check or spawn count.); saluki not shown (Code shows random spawn time calculation, not wave 1 damage check or spawn amounts.); wen-turbo not shown
- **lairs-spawning#8**: qwen3.5:9b not shown (Cited lines show boss check start, but missing specific threshold formula and spawn delay details.); saluki not shown (Code lacks spawnNumber=3, difficultyLevel, 500ms, and comparison logic.); wen-turbo supported
- **lairs-spawning#9**: qwen3.5:9b not shown (Cited lines show random selection logic, not the specific damage threshold or 500ms delay.); saluki not shown (Code lacks spawnNumber=3, difficultyLevel, and 500ms delay details.); wen-turbo supported
- **lairs-spawning#29**: qwen3.5:9b contradicted (Claim says spawnNumber 1; code requires getSpawnNumber() > 1.); saluki contradicted (Code shows spawnNumber > 1, not == 1; no 10s shown.); wen-turbo contradicted
- **lairs-spawning#33**: qwen3.5:9b not shown (Cited lines show spawn logic but do not confirm initial wave trigger.); saluki not shown (Code lacks nullptr attacker and repopulation context.); wen-turbo not shown
- **medic-xp-healing#16**: qwen3.5:9b contradicted (Code shows XP formula uses 'power' variable, not the specific numbers in claim.); saluki contradicted (Code shows power-based amount, not fixed 50 or woundHealed*2.5.)
- **medic-xp-healing#17**: qwen3.5:9b not shown (Cited lines show cooldown calculation but do not show the failure message or wait logic.); saluki not shown (Code shows delay calculation, not failure message or cooldown block.)
- **medic-xp-healing#34**: qwen3.5:9b not shown (Cited lines show cooldown calculation, not the blocking logic itself.); saluki not shown (Code shows delay calculation, not pending task blocking re-use.)
- **medic-xp-healing#35**: qwen3.5:9b not shown (Cited lines show skill mod and function start, not blocking logic.); saluki not shown (Code shows deactivate function start, not blocking or delay expiry.)
- **npc-conversations#2**: qwen3.5:9b not shown (Cited lines define class members but do not show screen content or ID linking logic.); saluki not shown (Code shows screen structure, not session creation or initial screen send.)
- **npc-conversations#25**: qwen3.5:9b contradicted (Code sends messages via sendMessage, not NpcConversationMessage packet.); saluki contradicted (Code shows generic sendMessage, not specific NpcConversationMessage or StringList packets.)
- **npc-conversations#34**: qwen3.5:9b not shown (Cited lines show normal flow, not exception handling or loop exit.); saluki not shown (Code shows null screen handling, not Lua exception/return loop exit.)
- **player-vendors#17**: qwen3.5:9b not shown (Cited lines check container objects, not vendor destruction state.); saluki not shown (Line 210 shows container iteration, not isVendorData() check.)
- **profession-gaps#7**: qwen3.5:9b not shown (Cited code shows TODO about slot 112, not space-only commands count.); saluki not shown (Code shows TODO about slot 112, not 22 space-only commands or Lua scripts.)
- **profession-gaps#17**: qwen3.5:9b not shown (The TODO comment exists but the specific research content is not shown in the code.); saluki not shown (Line 435 only shows a generic TODO comment, no specific coverage.)
- **quests#3**: qwen3.5:9b not shown (Cited lines show tutorial start, not custom screenplays or second copy.); saluki not shown (Code shows includeFile for the_tutorial, not custom_screenplays or second copy.)
- **resource-quality#5**: qwen3.5:9b not shown (Cited file defines constants, not the specific weight data fields.); saluki not shown (Code shows crafting resource constants, not weight sources or templates.)
- **resource-quality#8**: qwen3.5:9b not shown (Cited lines show attribute setup, not start values or ceiling logic.); saluki not shown (Code shows start values but no ceiling logic.)
- **resource-quality#14**: qwen3.5:9b not shown (Cited lines show assembly roll start but not full calculation.); saluki not shown (Code shows assembly success calculation, not a roll.)
- **resources#6**: qwen3.5:9b contradicted (Claim says 'empty or !inShift'; code shows only '!inShift' (despawned > time).); saluki contradicted (Code shows inShift() returns despawned > time(0), not 'despawned now'.)
- **resources#15**: qwen3.5:9b contradicted (Claim formula differs from code's (pool * zones + offset) / scale logic.); saluki contradicted (Code uses (pool*zones+poolScaleZones/2)/poolScaleZones, not (poolzones+5)/10.)
- **resources#18**: qwen3.5:9b contradicted (Code shows ranges 90-99, 75-94, 50-74, not the claimed intervals.); saluki contradicted (Code shows 0.90-0.99, 0.75-0.95, 0.50-0.75 but labels are 1,2,3 not HIGH/MEDIUM/LOW.)
- **slicing#8**: qwen3.5:9b contradicted (Code applies mods to levels 2-5, but default (below 2) returns without adding mods.); saluki contradicted (Code shows levels 3-5 get mods, not levels 2 and below.)
- **slicing#9**: qwen3.5:9b not shown (Cited lines show detachPowerUp, not slicing range logic.); saluki not shown (Code shows detachPowerUp and handleSliceDamage, not skill-based range.)
- **slicing#25**: qwen3.5:9b not shown (Cited lines show detachPowerUp and handleSliceDamage, not armor slicing logic.); saluki not shown (Code shows detachPowerUp and handleSliceDamage, not handleArmorSlice or XP award.)
- **slicing#35**: qwen3.5:9b not shown (Cited lines check skills but do not specify combat_smuggler_slicing_01 or smuggler bot.); saluki not shown (Code shows generic skill checks, not specific combat_smuggler_slicing_01 skill.)
- **slicing#39**: qwen3.5:9b not shown (Code shows inventory check, but does not show placing object in inventory.); saluki not shown (Code shows inventory check and error message, not placing object in inventory.)
- **survey-sample#5**: qwen3.5:9b not shown (Cited lines show waypoint logic, not costs, grid math, or specific message names mentioned in claim.); saluki not shown (Cited code lacks grid, cost, waypoint, or 3s delay details.)
- **survey-sample#10**: qwen3.5:9b not shown (Cited lines define constants and mind function, not range pop-up logic.); saluki not shown (Code shows constants and mind function, not range pop-up logic.)
- **survey-sample#12**: qwen3.5:9b not shown (Cited lines show tool selection logic, not positive percent counting rules.); saluki not shown (Code shows tool selection, not percent counting logic.)
- **survey-sample#15**: qwen3.5:9b not shown (Cited lines show wait logic, not 'sample' text matching start_sampling.); saluki not shown (Code shows select/wait, not sample text or units check.)
- **vehicle-mount#7**: qwen3.5:9b not shown (Cited lines show vehicle setup, not the specific cooldown logic mentioned in claim.); saluki not shown (Code shows control setup, not 2-second cooldown.)
