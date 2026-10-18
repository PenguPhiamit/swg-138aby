# NPC Conversation Mechanic Report

## 1. Short Answer

An NPC conversation starts when a player initiates it via radial menu or command, which triggers the server to create a `ConversationSession` and send the initial screen (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:108-114). Each screen contains dialog text and options; each option links to another screen by ID (src/server/zone/objects/creature/conversation/ConversationScreen.h:26, 39-41). When a player selects an option, the server looks up the linked screen in the conversation template (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:198-204), optionally runs Lua handlers to modify it (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:208-235), and sends the result as packets to the player (src/server/zone/objects/creature/conversation/ConversationScreen.h:178-234). A conversation ends when a screen has `stopConversation` set to true, which sends a `StopNpcConversation` packet and notifies observers (src/server/zone/objects/creature/conversation/ConversationScreen.h:214-227), or when the player manually stops it or moves out of range (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:88-107, 62-87). A bot can drive a conversation by sending option selections and checking system messages or session state for the expected screen ID.

## 2. How It Works

### Starting a Conversation
- The player initiates a conversation (radial menu or command), which fires an `ObserverEventType::STARTCONVERSATION` event (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:20).
- The observer cancels any existing session and creates a new one via `createConversationSession`, storing it in the player's active sessions keyed by `SessionFacadeType::CONVERSATION` (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:111-114, 146-148).
- A position observer is registered to detect if the player moves away (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:116, 150-152).

### Getting the Next Screen
- When an option is selected (`ObserverEventType::SELECTCONVERSATION`), `getNextConversationScreen` is called (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:129, 180).
- If there is a previous screen in the session, it uses that screen's `getOptionLink(selectedOption)` to look up the linked screen ID from the conversation template (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:193-204, src/server/zone/objects/creature/conversation/ConversationScreen.h:158-167).
- If no previous screen exists (first selection), it returns the template's initial screen via `getInitialScreen()` (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:203).

### Lua Screen Handlers
- For Lua-based conversations, `runScreenHandlers` loops while a handler modifies the screen (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:212-235).
- If a handler exists for the current screen ID, it calls `handleScreen`; if the handler returns `nullptr`, the handler's `getNextScreenId()` is used to fetch the next screen and the loop continues (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:214-227).
- Lua conversations delegate `getNextConversationScreen` and `runScreenHandlers` to `DirectorManager.instance()` (src/src/server/zone/objects/creature/conversation/LuaConversationObserver.idl:21-32).

### Sending Screens to the Player
- `sendConversationScreenToPlayer` calls `conversationScreen->sendTo(player, npc)` (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:240).
- `ConversationScreen::sendTo` sends an `NpcConversationMessage` packet with the NPC's dialog text, then a `StringList` packet with all option texts (src/server/zone/objects/creature/conversation/ConversationScreen.h:178-199).
- If the screen has non-empty `animation` or `playerAnimation` fields, corresponding doAnimation calls are made on the NPC and player (src/server/zone/objects/creature/conversation/ConversationScreen.h:203-209).
- The current screen is saved in the session via `setLastConversationScreen` for future lookups (src/server/zone/objects/creature/conversation/ConversationScreen.h:229-233).

### Ending a Conversation
- If a screen's `stopConversation` flag is true, it sends a `StopNpcConversation` packet to the player and notifies observers with `STOPCONVERSATION` (src/server/zone/objects/creature/conversation/ConversationScreen.h:214-227).
- For ship AI agents, instead of immediate stop it schedules a `SpaceCommTimerTask` after 3000ms (src/server/zone/objects/creature/conversation/ConversationScreen.h:215-220).
- The player can also manually end the conversation, which triggers `STOPCONVERSATION` and calls `cancelConversationSession` to drop the session and position observer (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:88-107, 154-178).
- If the player moves out of range during a conversation, `POSITIONCHANGED` triggers `cancelConversationSession` (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:62-87).

### Conversation Template Types
- `ConversationManager::getConversationObserver` creates observers based on template type: Normal, DeliverMission, InformantMission, Lua, or Personality (src/src/server/zone/managers/conversation/ConversationManager.cpp:36-55).
- Lua conversations use `LuaConversationObserver`, which delegates screen logic to DirectorManager (src/src/server/zone/objects/creature/conversation/LuaConversationObserver.idl:21-32).

## 3. What a Bot Test Should Check

### Observable Results
- **System messages**: The player should receive an `NpcConversationMessage` packet with the NPC's dialog text, followed by a `StringList` packet containing the option texts (src/server/zone/objects/creature/conversation/ConversationScreen.h:198-199). A bot can check these packets or any system chat messages displayed to the player.
- **Session state**: The player should have an active session with `SessionFacadeType::CONVERSATION` after starting (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:147). The session's `lastConversationScreen` should be updated after each screen is sent (src/server/zone/objects/creature/conversation/ConversationScreen.h:232).
- **StopNpcConversation packet**: When a conversation ends via `stopConversation=true`, the player receives a `StopNpcConversation` packet (src/server/zone/objects/creature/conversation/ConversationScreen.h:222, src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:248).
- **Animations**: If the screen specifies animations, both NPC and player should play them (src/server/zone/objects/creature/conversation/ConversationScreen.h:203-209). A bot can verify these via creature state queries.

### Required Setup
- The NPC must have a valid conversation template registered in `CreatureTemplateManager` with the correct CRC (src/src/server/zone/managers/conversation/ConversationManager.cpp:30, src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:252-254).
- The player must be within conversation range of the NPC (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:71, 81).
- For Lua conversations, the `DirectorManager` must have the appropriate Lua class handler and screen scripts loaded (src/src/server/zone/objects/creature/conversation/LuaConversationObserver.idl:24, 31).

## 4. Likely Reasons a Test Sees No Effect

- **Missing conversation template**: If `CreatureTemplateManager::instance()->getConversationTemplate(conversationTemplateCRC)` returns `nullptr`, `getConversationObserver` returns null and no observer is created (src/src/server/zone/managers/conversation/ConversationManager.cpp:32-34).
- **Wrong CRC**: The NPC's conversation template CRC must match what the client sends; a mismatch means the wrong or no observer is found.
- **Player out of range**: If the player moves beyond the NPC's conversation range, `POSITIONCHANGED` triggers `cancelConversationSession`, ending the conversation (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:71-83).
- **Lua handler errors**: If a Lua screen handler throws an exception or returns unexpectedly, the loop in `runScreenHandlers` may exit without sending a screen (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:219-226).
- **No linked screen**: If an option's `linkedScreenID` is empty or points to a non-existent screen, `getScreen` returns null and the conversation ends silently (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:200, 223-226).
- **DEBUG_MODE enabled**: If `CreatureTemplateManager::DEBUG_MODE` is true, `getConversationObserver` returns nullptr instead of creating an observer (src/src/server/zone/managers/conversation/ConversationManager.cpp:25-26).

## 5. Open Questions

- **How does the client initiate a conversation?** The files show server-side handling of `STARTCONVERSATION` events but not how the radial menu or command triggers them on the server (no client-side code in src/).
- **What is the exact format of option selection packets?** The server receives `selectedOption` as `arg2` in observer events (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:38, 51), but the packet structure from the client is not defined in these files.
- **How are Lua scripts loaded and associated with templates?** `LuaConversationObserver.idl` delegates to `DirectorManager.instance()` (src/src/server/zone/objects/creature/conversation/LuaConversationObserver.idl:24, 31), but the DirectorManager source is not included in the listed files.
- **What is the ConversationTemplate structure?** The template stores screens and provides `getInitialScreen()` and `getScreen(screenId)` (src/server/zone/objects/creature/conversation/ConversationObserverImplementation.cpp:188, 200, 203), but its full definition is not in the provided files.
- **How does the radial menu populate conversation options?** The client-side logic for building and displaying the radial menu with NPC conversation options is not present in these server-side files.
