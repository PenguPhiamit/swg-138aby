# Gambling Terminals Report

## 1. Short Answer

The gambling system supports two games: slots and roulette; sabacc is declared but commented out. Slots use a single-player weighted random digit roll (values 0–7) with a fixed payout schedule, while roulette allows up to four players to bet on numbers 0–36, 00, odd/even, high/low, red/black using the `/bet` command. Bets are validated against min/max limits and distance (25 units), then deducted from cash credits. The game cycle runs via scheduled GamblingEvent tasks with countdown timers for roulette and sequential digit reveals for slots. Payout calculation is marked native but its implementation is not in these files, which is a key gap.

## 2. How It Works

### Games Available
- **Slots** (`SLOTMACHINE = 1`): Single-player; only one player can join at a time (GamblingTerminal.idl line 57; GamblingTerminalImplementation.cpp line 61).
- **Roulette** (`ROULETTEMACHINE = 0`): Multi-player; up to four players allowed (GamblingTerminal.idl line 56; GamblingTerminalImplementation.cpp line 84).
- **Sabacc**: Declared as `SABACC = 2` but commented out in GamblingTerminal.idl line 59.

### Joining Conditions
- Player must be within 20 units of the terminal (GamblingTerminalImplementation.cpp lines 68, 91).
- Player cannot be incapacitated, in combat, swimming, riding a mount, dead, or meditating (line 36).
- Slot machines reject join if `playersWindows.size() > 0` (line 61); roulette rejects if `>= 4` (line 84).
- If already playing elsewhere, the message "You are already playing at a gambling terminal." is sent (line 53).

### Slots: Bets and Spins
- **Window**: A `SuiSlotMachineBox` is created showing Current Bet, Max Bet, Cash Balance, Bank Balance, Total Money (GamblingManagerImplementation.cpp lines 97–101).
- **Buttons**: Cancel (Quit or Spin), Other (Bet One), Ok (Bet Max) (lines 104–109).
- **Betting**: "Bet One" adds 1 credit; "Bet Max" fills to terminal max; if a bet already exists, Bet Max adds the difference (lines 330–336).
- **Auto-spin**: When `amount >= terminal->getMaxBet()`, `startGame()` is called immediately (line 449).
- **Slot weights**: Values [79, 22, 18, 16, 10, 7, 5, 4] total 161; `rollSlotDigit()` returns index 0–7 via weighted random (lines 281–307).
- **Payout schedule** (displayed in a separate payout window): *1|2|3 → base:2 max:6; 000 → base:4 max:12; 111 → base:50 max:150; 222 → base:75 max:225; 333 → base:100 max:300; 444 → base:250 max:750; 555 → base:500 max:1500; 666 → base:1000 max:3000; 777 → base:1500 max:5000 (lines 203–211).
- **Game messages**: During play, the terminal sends "Slot Machine Pay Line" followed by rolling digit reveals: first digit, then second, then third (lines 316–345).

### Roulette: Bets and Spins
- **Window**: A `SuiListBox` shows current bets with a prompt explaining `/bet <amount> <target>` syntax (lines 126–127).
- **Valid targets**: Numbers 0–36, "00", "odd", "even", "high", "low", "red", "black" (GamblingManager.idl lines 124–168).
- **Red numbers**: 1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36 (lines 103–121).
- **Betting**: Uses `/bet` command; amount is validated against max allowed bet (remaining to reach terminal max), cash balance, distance (25 units), and min bet (lines 457–488).
- **Countdown timers**: Roulette uses `rouletteTimer` values [30, 30, 30, 10, 5, 5, 5, 5, 10, 5, 5, 2] for game phase durations (GamblingManager.idl lines 76–89).
- **Game messages**: Countdown announcements at 120, 90, 60, 30, 20, 15, 10, 5 seconds ("prose_starting_in"); "wheel_spin" when wheel starts; "prose_wheel_slow" showing first random number (lines 446–471); final result via "prose_result_same" or "prose_result_change" (lines 472–501).

### Betting Limits
- Default `minBet = 1`, `maxBet = 10000` (GamblingTerminal.idl lines 93–94).
- **Slots**: `maxBet` is overridden to 3 in `loadTemplateData()` for SLOTMACHINE (line 234). This appears unusually low and may be a bug or placeholder.
- **Roulette**: `maxBet` remains 10000.

### Game States
- Slot states: NOGAMERUNNING(0), GAMESTARTING(1), GAMESTARTED(2), TWOLEFT(3), ONELEFT(4), END(5), SLOTGAMEENDED(6) (GamblingTerminal.idl lines 66–72).
- Roulette states: NOGAMERUNNING(0) through WHEELPAYOUT(12) (lines 66, 74–85).
- Betting allowed only when `state < GAMESTARTING` for slots; `NOGAMERUNNING < state < WHEELSTART` for roulette (GamblingTerminal.idl lines 290–297).

### Leaving
- Cancel button or radial menu option triggers `leaveTerminal()`, which closes menus, removes player from tracking, and calls `stopGame()` (GamblingTerminalImplementation.cpp lines 225–258).
- If a player leaves the 32-unit force-close distance, the SUI window is closed automatically (lines 111, 164).

## 3. What a Bot Test Should Check

### Setup Required
- Position the bot character within 20 units of a gambling terminal object.
- Ensure the bot is not incapacitated, in combat, swimming, riding, dead, or meditating.
- Have sufficient cash credits (bets are deducted from cash, not bank).

### Observable Results to Verify

**Slots:**
1. Radial menu shows "Join Station" when not playing; changes to "Leave Station" after joining (GamblingTerminal.idl line 249).
2. SUI window appears with title "@gambling/game_n:slot_standard" and five menu items (lines 94–101).
3. Pressing "Bet One" adds 1 credit; pressing "Bet Max" fills to max bet (3 for slots) (lines 330–336).
4. When bet reaches max, game auto-starts and the terminal sends "Slot Machine Pay Line" messages showing rolling digits (lines 449, 316–345).
5. After game ends, player can rejoin if state is SLOTGAMEENDED (line 124).

**Roulette:**
1. SUI window appears with title "@gambling/game_n:roulette" and betting instructions (lines 131–132).
2. `/bet <amount> <target>` command places bet; system message "prose_bet_placed" confirms (line 483).
3. Menu refreshes to show updated total bet (lines 142–158).
4. Countdown messages appear at intervals (lines 382–445).
5. Wheel spin and result messages are broadcast to all players at the table (lines 446–501).

**Both:**
- System messages for joining ("prose_player_join"), leaving ("prose_player_leave"), and out-of-range errors (lines 293, 302, 71).
- Terminal state changes observable via `getState()` calls.
- Player's cash credits decrease when betting; winnings should increase after payout (though payout logic is native and not visible here).

## 4. Likely Reasons a Test Sees No Effect

- **Distance**: Player must be within 20 units to join, 25 units to bet (lines 68, 91, 404, 465).
- **Terminal capacity**: Slots accept only one player; roulette accepts four (lines 61, 84).
- **Invalid posture**: Incapacitated, combat, swimming, riding, dead, or meditating states block join (line 36).
- **Already playing**: "You are already playing at a gambling terminal." message prevents re-entry (line 53).
- **Insufficient cash**: "player_broke" message if cash < bet amount (lines 402, 462).
- **Bet below minimum**: "bet_below_min" message with terminal minBet value (lines 407–410, 468–471).
- **Bet above maximum**: "bet_above_max" message with terminal maxBet value (lines 398–401, 457–461).
- **Native implementations missing**: Functions like `calculateOutcome`, `stopGame`, and `leaveTerminal` are declared native in GamblingManager.idl but their C++ implementations are not in the provided files. If these are not compiled or linked correctly on the server, game outcomes will not process.

## 5. Open Questions

- **Payout calculation**: The `calculateOutcome(GamblingTerminal terminal)` function is declared native in GamblingManager.idl line 375 but its implementation is not in any provided file. This is critical for verifying win/loss amounts.
- **Skill modifiers**: No skill-based modifiers appear in these files. It is unclear if gambling uses any player skills (e.g., Deception, Performance) or if payouts are purely random.
- **Sabacc**: Declared as `SABACC = 2` in GamblingTerminal.idl line 59 but commented out. The implementation file for sabacc terminals and game logic is missing.
- **Slot max bet of 3**: Slots have `maxBet = 3` hardcoded in loadTemplateData() (GamblingTerminal.idl line 234), which seems intentionally low or possibly a bug. It is unclear if this is intentional design or an error.
- **Roulette payout multipliers**: The code shows bet targets and result messages but does not reveal the payout table (e.g., straight-up pays 35:1, red/black pays 2:1). This logic is likely in the missing `calculateOutcome` implementation.
- **GamblingSlotPayoutSuiCallback**: Included in GamblingManagerImplementation.cpp line 21 but its header file is not provided; the payout window callback behavior is unknown.
