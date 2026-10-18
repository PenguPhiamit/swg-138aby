# Report: Bank Terminal and /tip Mechanics

## 1. Short Answer

Cash tips use `/tip [player] <amount>` within 190 m, deduct cash immediately, and send system messages to both players with no fee. Bank tips use `/tip [player] <amount> bank` (or target offline) and show a confirmation window warning of a 5 % surcharge unless both characters share the same account, in which case there is no fee; the transfer executes only on confirmation. The bank terminal lets you join/quit a planet-bound bank, deposit/withdraw cash or bank credits individually via an SUI box (8 m range), or deposit/withdraw all instantly with no fee. Bank deposits through the terminal require being on the planet where you joined your bank.

## 2. How It Works

### Cash /tip
- **Syntax:** `/tip [playername] <amount>` (no "bank" keyword) `TipCommand.h:143-181`
- **Target resolution:** First argument is player name; if it parses as zero, the code looks up a player by that name. If no target argument is given, the command falls back to the look-at target. `TipCommand.h:161-201`
- **Distance check:** Target must be within 190 m of the sender. `TipCommand.h:23`
- **Funds check:** Sender's cash (`getCashCredits`) must be ≥ amount. `TipCommand.h:31-38`
- **Ignore check:** Target's ghost must not ignore the sender's first name. `TipCommand.h:41-46`
- **Execution:** Cash is subtracted from sender and added to target atomically inside a locker. `TipCommand.h:51-56`
- **Messages (sender):** `"You successfully tip %DI credits to %TT."` `TipCommand.h:63-66`
- **Messages (receiver):** `"%TT tips you %DI credits."` `TipCommand.h:58-61`
- **No fee** is applied for cash tips.

### Bank /tip (wire transfer)
- **Syntax:** `/tip [playername] <amount> bank` or target is offline. `TipCommand.h:221-224`
- **Funds check:** Sender's bank credits (`getBankCredits`) must be ≥ amount. `TipCommand.h:81-88`
- **Ignore check:** Same as cash tip. `TipCommand.h:91-94`
- **Confirmation window:** A `SuiMessageBox` with title `"Confirm Bank Transfer"` is shown. `TipCommand.h:96-118`
  - Default prompt: `"A surcharge of 5% will be added to your requested bank-to-bank transfer amount. Would you like to continue?"` `TipCommand.h:102`
  - If `Core3.SameAccountTipsAreFree` is true and both players share the same account ID, the prompt changes to `"You are transferring credits to another character on your account, there will be no fee for this transaction. Would you like to continue?"` `TipCommand.h:104-110`
- **Actual transfer:** The server-side callback (`TipCommandSuiCallback`, not in these files) executes the transfer only when the player presses OK. (inferred)
- **Messages after confirmation:** Same prose as cash tip but for bank credits, though the exact string IDs are reused from `performTip` via the callback. (inferred)

### Bank Terminal — Join / Quit
- **Join bank:** Selecting "Join Bank" sets the player's bank location to the current planet's zone name. The slotted bank object is sent to the player and a success message appears. `BankTerminalMenuComponent.cpp:77-95`
- **Quit bank:** Removes the bank slot if its container is empty; otherwise shows `"bank_not_empty"`. Bank location is cleared regardless. `BankTerminalMenuComponent.cpp:98-119`

### Bank Terminal — Deposit / Withdraw (individual)
- **Radial menu option:** "Deposit/Withdrawal" (radial ID 68). `BankTerminalMenuComponent.cpp:23`
- **SUI box:** Opens a `SuiBankTransferBox` pre-filled with current cash and bank balances. `BankTerminalMenuComponent.cpp:66-74`
- **Range check:** Player must be within 8 m of the bank terminal when confirming. `BankTerminalSuiCallback.h:41-48`
- **Transfer function:** Calls `player->transferCredits(cash, bank)` with the two input values. `BankTerminalSuiCallback.h:50`
- **Success message:** `"@base_player:bank_success"` (string ID; exact text not in these files). `BankTerminalSuiCallback.h:52`

### Bank Terminal — Deposit / Withdraw All
- **Deposit all:** Available when cash > 0. Deposits entire cash balance to bank instantly, no fee. `BankTerminalMenuComponent.cpp:130-142`
- **Withdraw all:** Available when bank credits > 0. Withdraws entire bank balance to cash instantly, no fee. `BankTerminalMenuComponent.h:143-155`

### Bank Terminal — Deposit (open container)
- Selecting "Deposit" opens the slotted bank container if the player is on their registered bank planet or if `GLOBALSAFETYDEPOSIT` is true; otherwise shows `"@newbie_tutorial/system_messages:bank_info_2"` (inferred as a generic bank-info message). `BankTerminalMenuComponent.cpp:121-129`

## 3. What a Bot Test Should Check

### Setup
1. Two bot characters on the same planet, within 8 m of a bank terminal and/or within 190 m of each other.
2. Both bots have non-zero cash and/or bank credits (verify via `getCashCredits()` / `getBankCredits()`).
3. For bank-tip tests: ensure both bots are online so the cash-tip path is taken, or make one offline to force the bank-tip path.

### Cash tip checks
- Send `/tip <other_bot> 100` and verify:
  - Sender's cash decreases by exactly 100.
  - Receiver's cash increases by exactly 100.
  - Both bots receive system messages matching the prose IDs `prose_tip_pass_self` and `prose_tip_pass_target`.
- Verify rejection when sender has insufficient cash (e.g., tip 999999 with only 500 cash).
- Verify rejection when distance > 190 m.

### Bank tip checks
- Send `/tip <other_bot> 100 bank` and verify:
  - A confirmation SUI box appears on the sender with title `"Confirm Bank Transfer"` and the appropriate prompt (5 % surcharge or no-fee message if same account).
  - Pressing Cancel leaves balances unchanged.
  - Pressing OK deducts from sender's bank credits, adds to receiver's cash (or bank, depending on implementation), and both receive success messages.
- Verify insufficient-bank-funds rejection.

### Bank terminal checks
- **Join/Quit:** Join a bank, verify `getBankLocation()` returns the current planet name; quit, verify it returns empty string.
- **Deposit/Withdraw SUI:** Open the deposit/withdraw box, enter amounts, confirm within 8 m, and verify balances update correctly. Verify out-of-range rejection (> 8 m).
- **Deposit all / Withdraw all:** Execute each and verify full transfer with no fee.
- **Open container:** Deposit (open bank) when on registered planet succeeds; when off-planet shows the bank-info message.

## 4. Likely Reasons a Test Sees No Effect

- Distance too great: cash tip requires ≤ 190 m; terminal SUI requires ≤ 8 m `TipCommand.h:23`, `BankTerminalSuiCallback.h:41`.
- Insufficient funds: cash or bank balance below the requested amount. `TipCommand.h:32`, `TipCommand.h:82`.
- Target ignoring sender: tip is silently rejected. `TipCommand.h:44-45`, `TipCommand.h:92-93`.
- Bank terminal on wrong planet for deposit: player must be on the planet where they joined their bank. `BankTerminalMenuComponent.cpp:122-127`.
- SUI not confirmed: bank tips require pressing OK in the confirmation window; cancel or timeout aborts the transfer. `TipCommand.h:96-118`.
- Target offline for cash tip: forces bank-tip path instead, which requires confirmation. `TipCommand.h:221-224`.

## 5. Open Questions

- **`TipCommandSuiCallback` implementation:** The actual bank-to-bank transfer logic (including the 5 % surcharge calculation and whether it adds to receiver's cash or bank) is in `TipCommandSuiCallback.h`, which is not provided here.
- **`transferCredits` implementation:** The exact behavior of `player->transferCredits(cash, bank)` (whether it handles both directions atomically, logs transactions, etc.) is not visible in these files.
- **`GLOBALSAFETYDEPOSIT` flag:** Its definition and effect on cross-planet deposits are unclear without the header where it is declared.
- **Transaction log details:** The `TransactionLog` constructor parameters (e.g., what `TrxCode::PLAYERTIP` vs `TrxCode::BANK` encode) are not documented in these files.
- **String ID texts:** Several messages use string IDs (`@base_player:bank_success`, `@newbie_tutorial/system_messages:bank_info_2`) whose actual displayed text is not in the source.
