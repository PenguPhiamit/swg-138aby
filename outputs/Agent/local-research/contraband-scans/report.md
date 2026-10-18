# Contraband Scan Mechanic Report

## 1. Short Answer

Contraband scans are initiated by Imperial or Rebel AI agents (or NPCs using the winning faction) when they randomly decide to scan a nearby player creature. The scan proceeds through several states: a chance check, dismount/greeting, optional Jedi mind-trick interaction, faction-rank detection, and finally a contraband count. If contraband items are found, the player receives a fine (credits deducted from cash/bank) or a faction-point penalty if they refuse or timeout. Smugglers with specific skills can avoid detection entirely; Jedi can attempt to mind-trick the scanner or resist detection. The scan also detects opposite-faction players and calls Lambda shuttle reinforcements, starting combat.

## 2. How It Works

### Conditions for Initiation
- **Who scans**: Any AI agent (AiAgent) that is not dead and not in combat can initiate a scan on a player creature that is alive, not feigning death, not incapacitated, and not in combat (`src/.../ContrabandScanSessionImplementation.cpp:344-351`).
- **Faction determination**: If the scanner has FACTIONIMPERIAL or FACTIONREBEL, that faction is used; otherwise it falls back to `currentWinningFaction` from GCWManager (`src/.../ContrabandScanSessionImplementation.cpp:47-57`).
- **Random chance**: Only 1 in SCANINITIATECHANCE (12) attempts initiate a scan (~8.3%) (`src/.../ContrabandScanSession.idl:11`, `src/.../ContrabandScanSessionImplementation.cpp:500-501`).

### Smuggler Avoidance
- Before the scan begins, `calculateSmugglingSuccess()` checks if the player (or any grouped member within 35 meters) has smuggler combat skills (`combat_smuggler_novice` through `combat_smuggler_master`) (`src/.../ContrabandScanSessionImplementation.cpp:804-825`).
- Each skill tier adds a fixed chance: novice (+15), underworld_01-04 (+15 each), master (+20), totaling up to 100% avoidance (`src/.../ContrabandScanSessionImplementation.cpp:827-848`).
- If the random roll is less than the total avoidance chance, `smugglerAvoidedScan` is set true and the scan skips contraband detection entirely (`src/.../ContrabandScanSessionImplementation.cpp:822-824`).

### Jedi Mind Trick (Padawan+)
- Players with `force_title_jedi_rank_02` (Padawan) or higher can attempt a mind trick (`src/.../ContrabandScanSessionImplementation.cpp:615`).
- Base success chance is JEDIMINDTRICKSUCCESSCHANCEBASE (80%) (`src/.../ContrabandScanSession.idl:19`), modified by Jedi rank/master titles (+5 to +20) or `force_discipline_powers_master` (guaranteed 100%) (`src/.../ContrabandScanSessionImplementation.cpp:652-665`).
- On success, the scanner stops and leaves; on failure, it proceeds to jediDetect.

### Jedi Detection Resistance
- After a failed mind trick, `jediDetect()` checks if the player avoids detection using JEDIAVOIDDETECTIONBASECHANCE (80%) (`src/.../ContrabandScanSession.idl:22`), reduced by Jedi rank/master titles (-5 to -15) (`src/.../ContrabandScanSessionImplementation.cpp:667-677`).
- Rebels scanning dark jedi always detect them; light-side Jedi avoid detection more easily.

### Faction Rank Detection
- Detection chance = BASEFACTIONDETECTIONCHANCE (10%) + RANKDETECTIONCHANCEMODIFIER (3) × player's faction rank + `force_persuade` skill mod (`src/.../ContrabandScanSessionImplementation.cpp:537`).
- Players with OVERT status or rank ≥ RECOGNIZEDFACTIONRANK (9) are always recognized and allowed to leave without contraband check (`src/.../ContrabandScanSession.idl:16`, `src/.../ContrabandScanSessionImplementation.cpp:542-561`).
- Opposite-faction players detected this way get their status raised (COVERT or OVERT), and Lambda reinforcements are called, starting combat (`src/.../ContrabandScanSessionImplementation.cpp:562-593`).

### Contraband Detection & Fines
- After SCANTIME (10 iterations = 10 seconds) of scan delay, `performScan()` calls `gcwManager->countContrabandItems(player)` (`src/.../ContrabandScanSessionImplementation.cpp:455`).
- If contraband items > 0 and smuggler didn't avoid: fine is numberOfContrabandItems × `getCrackdownContrabandFineCredits()` (value not in these files) (`src/.../ContrabandScanSessionImplementation.cpp:421`).
- A SUI window appears with "@imperial_presence/contraband_search:imp_fine_title" and text showing the credit amount (`src/.../ContrabandScanSessionImplementation.cpp:427-435`).
- **If player accepts**: Credits are deducted from cash first, then bank if needed; TransactionLog entries use TrxCode::FINES (`src/.../ContrabandScanSessionImplementation.cpp:768-779`).
- **If player refuses or times out** (WAITFORPAYFINEANSWERTIMEOUT = 60 seconds): faction standing is decreased by `getCrackdownContrabandFineFactionPoints()` (value not in these files) (`src/.../ContrabandScanSessionImplementation.cpp:755`, `src/.../ContrabandScanSession.idl:20`).
- If player lacks enough credits even after cash+bank, no fine is paid but the scan ends (`src/.../ContrabandScanSessionImplementation.cpp:781-785`).

### Timings
- TASKDELAY = 2000ms between state transitions (`src/.../ContrabandScanSession.idl:12`).
- SCANTIME = 10 iterations (20 seconds total) before contraband check (`src/.../ContrabandScanSession.idl:14`, TASKDELAY × 10).
- WAITFORPAYFINEANSWERTIMEOUT = 60 iterations (120 seconds) for fine SUI response (`src/.../ContrabandScanSession.idl:20`).
- TIMETORETURNFORSCAN = 10 iterations (20 seconds) if player moves out of range/LOS during scan (`src/.../ContrabandScanSession.idl:15`).

### Messages the Player Sees
- **System messages** (via `sendSystemMessage`): "dismount_imperial"/"dismount_rebel", "probe_scan_positive" (contraband found), "probe_scan_negative" (clean), "discovered_imperial"/"discovered_rebel" (opposite faction detected), "ran_away_imperial"/"ran_away_rebel" (timeout/escape).
- **Chat messages** from scanner: scan greetings, fines, accusations, and farewells using StringId keys under "@imperial_presence/contraband_search:" (`src/.../ContrabandScanSessionImplementation.cpp:203-213`).
- **SUI window**: Fine prompt with yes/no buttons (`src/.../ContrabandScanSessionImplementation.cpp:425-438`).

## 3. What a Bot Test Should Check

### Setup Needed
- An AI agent (AiAgent) scanner with FACTIONIMPERIAL or FACTIONREBEL (or ensure `currentWinningFaction` is set).
- A player creature with known state: not in combat, not dead/incapacitated, optionally with smuggler skills or Jedi titles.
- Player must carry items that `countContrabandItems()` recognizes (item criteria not defined in these files).

### Observable Results to Verify
1. **Scan initiation**: Confirm the 1/12 chance by running multiple scans; verify cooldowns "crackdown_scan" are set on both player and scanner (`src/.../ContrabandScanSessionImplementation.cpp:65-68`).
2. **Dismount & greeting**: Player dismounts if riding; system message received (`src/.../ContrabandScanSessionImplementation.cpp:517-524`).
3. **Smuggler avoidance**: Player with sufficient smuggler skills should receive "@base_player:smuggler_scan_success" and no further scan messages (`src/.../ContrabandScanSessionImplementation.cpp:473-474`).
4. **Jedi mind trick**: Padawan+ player should see mind-trick chat; on success, "probe_scan_done" system message and scanner leaves (`src/.../ContrabandScanSessionImplementation.cpp:609-714`).
5. **Faction detection**: Opposite-faction player should receive "discovered_imperial"/"discovered_rebel", status change to COVERT/OVERT, and Lambda shuttle combat (`src/.../ContrabandScanSessionImplementation.cpp:562-593`).
6. **Contraband fine**: If contraband found, SUI window appears with correct credit amount; accepting deducts from cash/bank with TransactionLog FINES entries; refusing/timing out decreases faction standing (`src/.../ContrabandScanSessionImplementation.cpp:415-796`).
7. **Reinforcements**: Lambda shuttle spawns at nearest valid spawn point, starting combat (`src/.../ContrabandScanSessionImplementation.cpp:850-887`).

## 4. Likely Reasons a Test Sees No Effect

- The random SCANINITIATECHANCE (1 in 12) means most attempts won't initiate a scan; many repetitions needed (`src/.../ContrabandScanSession.idl:11`).
- Prerequisites not met: scanner or player is dead, incapacitated, feigning death, or in combat (`src/.../ContrabandScanSessionImplementation.cpp:350`).
- Player has sufficient smuggler skills to avoid detection entirely (`src/.../ContrabandScanSessionImplementation.cpp:827-848`).
- Player is OVERT or rank ≥ 9, causing early termination without contraband check (`src/.../ContrabandScanSessionImplementation.cpp:542-561`).
- `countContrabandItems()` returns 0 because the player's inventory doesn't contain recognized contraband items (item criteria not in these files).
- Player is too far (>20m) or out of line-of-sight, triggering AVOIDINGSCAN state and timeout (`src/.../ContrabandScanSessionImplementation.cpp:366`, `src/.../ContrabandScanSession.idl:15`).
- GCWManager not initialized or `currentWinningFaction` is 0, causing early return in `initializeSession()` (`src/.../ContrabandScanSessionImplementation.cpp:55-57`, `src/.../GCWManagerImplementation.cpp.lines-3432-3438:3436`).

## 5. Open Questions

- **What counts as contraband?** The function `gcwManager->countContrabandItems(player)` is called but its implementation is not in these files (`src/.../ContrabandScanSessionImplementation.cpp:455`).
- **Fine credit amount and faction point penalty values**: `getCrackdownContrabandFineCredits()` and `getCrackdownContrabandFineFactionPoints()` are referenced but their return values are not in these files (`src/.../ContrabandScanSessionImplementation.cpp:421`, `src/.../ContrabandScanSessionImplementation.cpp:755`).
- **How is the scan triggered?** The entry point `startContrabandScanSession()` exists in GCWManagerImplementation (`src/.../GCWManagerImplementation.cpp.lines-3432-3438:3432`), but what calls it (player interaction, NPC AI behavior, zone event) is not shown.
- **Cooldown values**: `getCrackdownPlayerScanCooldown()` and `getCrackdownScannerCooldown()` return values are not in these files (`src/.../ContrabandScanSessionImplementation.cpp:65-68`).
- **Jedi mind trick chat messages**: The exact StringId keys for mind-trick responses depend on external `.str` files not included here.
