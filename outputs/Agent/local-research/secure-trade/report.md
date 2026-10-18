# Trade Mechanic Report for Core3 (pre-CU)

## 1. Short Answer

In Core3, a trade is initiated by one player sending a `BeginTradeMessage` containing the target player's ID to start the session (`src/src/server/zone/packets/trade/BeginTradeMessage.h:8-15`). The receiver must accept via the radial menu; once accepted, both players use the trade window to add items (via `AddItemMessageCallback`, parsing a long object ID at line 22) and credits (via `GiveMoneyMessageCallback`, parsing an int amount at line 24). Each side then clicks "Accept" (`AcceptTransactionMessageCallback` at line 28), followed by "Verify" (`VerifyTradeMessageCallback` at line 27) to confirm the final state. Either party may abort at any time via `AbortTradeMessageCallback`. The server tracks state in a `TradeSession` object with fields for target player, items vector, money amount, and boolean flags for accepted/verified status (lines 14-20 of `TradeSession.idl`).

## 2. How It Works

### Initiation
- **Who starts:** Either player can initiate by sending a `BeginTradeMessage` to the other player's object ID (`BeginTradeMessage.h:8-15`).
- **Message format:** Opcode `0x0E`, followed by short `0x02`, int `0x325932D8`, and long `playerID` (lines 10-14).

### Trade Session State
The server creates a `TradeSession` object per trade with these fields (`TradeSession.idl:14-20`):
- `tradeTargetPlayer` (unsigned long) – the other player's ID.
- `itemsToTrade` (SortedVector<SceneObject>) – items each side adds.
- `verifiedTrade` (boolean) – whether this side clicked "Verify".
- `acceptedTrade` (boolean) – whether this side clicked "Accept".
- `moneyToTrade` (int) – credits offered by this side.

### Adding Items
- Client sends an item-add callback (`AddItemMessageCallback.h:14-48`).
- The callback parses a long ID from the message (line 22).
- It calls `playerMan->handleAddItemToTradeWindow(player, id)` (line 46).
- The server adds the SceneObject to this player's `itemsToTrade` vector (`TradeSession.idl:34-36`).

### Adding Credits
- Client sends a money callback (`GiveMoneyMessageCallback.h:14-51`).
- The callback parses an int amount from the message (line 24).
- It calls `playerMan->handleGiveMoneyMessage(player, money)` (line 45).
- The server sets this player's `moneyToTrade` (`TradeSession.idl:67-69`).

### Accepting the Trade
- Both players must click "Accept" in their trade windows.
- Each sends an `AcceptTransactionMessageCallback` with no arguments (`AcceptTransactionMessageCallback.h:24-36`).
- The server calls `playerManager->handleAcceptTransactionMessage(player)` (line 35).
- This sets the player's `acceptedTrade` flag to true (`TradeSession.idl:63-65`).

### Verifying the Trade
- After accepting, each player clicks "Verify" to confirm the final state.
- Each sends a `VerifyTradeMessageCallback` with no arguments (`VerifyTradeMessageCallback.h:23-46`).
- The server calls `playerMan->handleVerifyTradeMessage(player)` (line 45).
- This sets the player's `verifiedTrade` flag to true (`TradeSession.idl:75-77`).

### Completing or Aborting
- When both sides have `acceptedTrade == true` and `verifiedTrade == true`, the trade completes. The server transfers items and credits (implementation not in provided files).
- Either player may abort at any time by sending `AbortTradeMessageCallback` (`AbortTradeMessageCallback.h:14-42`).
- The server calls `playerMan->handleAbortTradeMessage(player)` (line 40).
- The server clears the entire session via `clearTradeContainer()`, resetting all fields to defaults (`TradeSession.idl:79-86`).

### Conditions, Skill Mods, Timings, and System Messages
The provided files do not contain the implementation of the PlayerManager handler methods (e.g., `handleAddItemToTradeWindow`, `handleGiveMoneyMessage`, `handleAcceptTransactionMessage`, `handleVerifyTradeMessage`, `handleAbortTradeMessage`). Therefore, I cannot cite specific conditions for refusing trades, skill modifiers, numeric thresholds, timing constraints, or system message string IDs from these files alone. (inferred: such logic would be in PlayerManager.cpp or a related implementation file not included in the provided set.)

## 3. What a Bot Test Should Check

### Setup
- Ensure both bot characters are within trade range and have no existing active trade session.
- Have credits and test items in inventory before starting.

### Observable Results to Verify
1. **Initiation:** After sending `BeginTradeMessage` with the target player's ID, confirm the target receives a trade window prompt (system message or SUI window).
2. **Acceptance:** After the target accepts, both players see an open trade window showing empty item slots and credit fields.
3. **Adding Items:** After adding an item via `AddItemMessageCallback` with a valid object ID, confirm the item appears in that player's side of the trade window on both clients.
4. **Adding Credits:** After sending `GiveMoneyMessageCallback` with a credit amount, confirm the credit field updates on both sides and the sender's credit balance decreases.
5. **Accept Button:** After both click "Accept", confirm the "Verify" button becomes active for both players.
6. **Verify Button:** After both click "Verify", confirm the trade completes (items and credits are transferred to final destinations).
7. **Abort:** After either clicks "Abort", confirm the trade window closes, all items return to original inventories, credits restore, and a system message indicates the trade was aborted.

### State Checks
- Verify `TradeSession` fields: `tradeTargetPlayer` matches the other player's ID, `itemsToTrade` contains added objects, `moneyToTrade` matches sent amount, `acceptedTrade` and `verifiedTrade` flags are true when expected.
- Check credit balances before and after to confirm correct transfers.

## 4. Likely Reasons a Test Sees No Effect

1. **Missing PlayerManager implementation:** The handler methods called by the callbacks (`handleAddItemToTradeWindow`, `handleGiveMoneyMessage`, etc.) are not in the provided files. If they are unimplemented or return early, no state changes occur.
2. **Invalid object ID:** `AddItemMessageCallback` checks `if (id == 0) return;` at line 31-32; sending a null/zero ID silently aborts without error.
3. **Null player reference:** All callbacks check `if (player == nullptr) return;` and silently exit if the client is not associated with a valid CreatureObject.
4. **Null zone server or player manager:** Multiple callbacks check for null `zoneServer` or `playerMan` and return early without action.
5. **Trade already in progress:** If a trade session already exists, the server may refuse to start a new one (logic not visible in provided files).
6. **Target not found or out of range:** The target player ID in `BeginTradeMessage` may be invalid or too far away (implementation details not in these files).

## 5. Open Questions

1. **PlayerManager handler implementations:** The actual logic for `handleAddItemToTradeWindow`, `handleGiveMoneyMessage`, `handleAcceptTransactionMessage`, `handleVerifyTradeMessage`, and `handleAbortTradeMessage` is not present. Without these, I cannot cite conditions for refusing trades, skill requirements, numeric checks, or system message string IDs.
2. **Radial menu interaction:** How exactly does a player initiate a trade via radial menu? What radial menu ID triggers the `BeginTradeMessage`? This is not in the provided files.
3. **SUI window details:** What SUI windows are shown to players (prompts, trade window layout)? The callback headers do not define UI elements.
4. **Timing constraints:** Is there a timeout for accepting, verifying, or completing a trade? Not visible in these files.
5. **Completion mechanics:** How does the server actually transfer items and credits when both sides verify? The `TradeSession` tracks state but the transfer logic is not shown.
6. **Error messages:** What system message string IDs are displayed for refused actions (e.g., insufficient credits, invalid item)? These would be in PlayerManager.cpp or a message manager, neither of which is provided.
