# Report: Tells, Mail, Friends and Ignore Mechanics

## 1. Short Answer

Tells to offline players fail silently with an "IM_OFFLINE" message; tells to ignored players return "IM_IGNORED". In-game mail is always delivered (to online players immediately, to offline players in a pending queue), with a body size limit of PM_MAXSIZE. The friends list caps at 1000 entries and cannot include god-mode players. `/findfriend` only works if the target has you on their friend list and does not ignore you; it creates a waypoint at their location. Adding/removing ignores is straightforward, but ignored players block tells and can cause mail to be destroyed (in one code path). God mode bypasses all ignore checks.

## 2. How It Works

### Tells (Instant Messages)
- **Muted sender**: If the sender's `PlayerObject` is muted, they receive a system message about chat being disabled by Customer Support and the tell is rejected (`ChatManagerImplementation.cpp.lines-1462-1563:1482-1491`).
- **Invalid recipient name**: If no player exists with that name, the sender sees "There is no person by the name '%TU' in this Galaxy." and receives a `NOAVATAR` acknowledgment (`ChatManagerImplementation.cpp.lines-1462-1563:1507-1517`).
- **Offline recipient**: If the receiver's `CreatureObject` is not loaded (not online), the sender sees an "IM_OFFLINE" message. The server does not distinguish between "player doesn't exist" and "player is offline" in this path (`ChatManagerImplementation.cpp.lines-1462-1563:1521-1527`).
- **Recipient ignores sender**: If the receiver's `PlayerObject` reports `isIgnoring(sender)` as true (and sender is not god mode), the sender sees an "IM_IGNORED" message (`ChatManagerImplementation.cpp.lines-1462-1563:1529-1544`).
- **Message too long**: If `text.length() > IM_MAXSIZE`, the sender sees an "IM_TOOLONG" message (`ChatManagerImplementation.cpp.lines-1462-1563:1548-1553`). The exact value of `IM_MAXSIZE` is not defined in these files.
- **Success**: On success, the formatted message is sent to the receiver via `ChatInstantMessageToClient`, and the sender receives an `IM_SUCCESS` acknowledgment (`ChatManagerImplementation.cpp.lines-1462-1563:1555-1561`).

### In-Game Mail
- **Mail creation**: Multiple `sendMail` overloads exist. All create a `PersistentMessage` object, set sender/subject/body/receiver fields, and persist it via `ObjectManager::instance()->persistObject(mail, 1, "mail")` (`ChatManagerImplementation.cpp.lines-1783-2052:1800`, `1872`, `1944`, `1955`).
- **Body size limit**: One overload checks `body.length() > PM_MAXSIZE` and returns `IM_TOOLONG` if exceeded (`ChatManagerImplementation.cpp.lines-1783-2052:1826-1827`). The exact value of `PM_MAXSIZE` is not defined in these files.
- **Recipient validation**: Mail to a non-existent player name logs an error and returns early (`ChatManagerImplementation.cpp.lines-1783-2052:1788-1791`, `1823-1824`, `1908-1909`).
- **Online recipient**: If the receiver is online, their `PlayerObject` gets the mail added to its persistent message list via `addPersistentMessage()`, and if they are currently online, the mail is sent immediately (`ChatManagerImplementation.cpp.lines-1783-2052:1813-1816`, `1894-1899`, `1956-1961`).
- **Offline recipient**: If the receiver is offline, the mail's object ID is added to a `PendingMessageList` keyed by receiver object ID (`ChatManagerImplementation.cpp.lines-1783-2052:1804-1807`, `1881-1883`, `1945-1947`).
- **Ignore check on mail delivery**: In two overloads, if the receiver is online and their `PlayerObject` ignores the sender (and sender is not god mode), the mail is destroyed from the database and removed (`ChatManagerImplementation.cpp.lines-1783-2052:1888-1891`, `1952-1953`). In one overload, no ignore check is performed before adding to pending messages (`ChatManagerImplementation.cpp.lines-1783-2052:1793-1819`).
- **Mail status constants**: `NEW = 0x4E`, `READ = 0x52`, `UNREAD = 0x55` (`PersistentMessage.idl:31-33`).
- **Loading mail on login**: When a player logs in, `loadMail()` checks pending messages and sends all persistent messages from the database to the player (`ChatManagerImplementation.cpp.lines-1783-2052:1968-1989`).
- **Reading mail**: `handleRequestPersistentMsg()` sets status to 'R' (READ) and sends the mail with body (`ChatManagerImplementation.cpp.lines-1783-2052:2021-2022`).
- **Deleting mail**: `deletePersistentMessage()` removes the object ID from the player's list and destroys it from the database (`ChatManagerImplementation.cpp.lines-1783-2052:2025-2051`).

### Friends List
- **Adding a friend** (`AddFriendCommand.h`):
  - Fails if target is on your ignore list, with message key `"friend_fail_is_ignored"` (`AddFriendCommand.h:36-42`).
  - Fails if already a friend, with message key `"friend_duplicate"` (`AddFriendCommand.h:44-50`).
  - Fails if friend list size >= 1000, with message "You have too many friends!" (`AddFriendCommand.h:52-56`).
  - Cannot add god-mode players (unless you are also god mode) (`AddFriendCommand.h:59-68`).
  - Fails if name doesn't exist, with message key `"friend_not_found"` (`AddFriendCommand.h:71-79`).
  - On success, calls `ghost->addFriend(name)` (`AddFriendCommand.h:81`).
- **Removing a friend** (`RemoveFriendCommand.h`): Simply calls `ghost->removeFriend(arguments.toString())` with no validation or message (`RemoveFriendCommand.h:28`).

### `/findfriend` Command
- Only works if the target player has you on their friend list (`FindFriendCommand.h:55-61`).
- Only works if the target does not ignore you (`FindFriendCommand.h:63-69`).
- Only works if the target is online and has a valid zone (`FindFriendCommand.h:44-79`).
- On success, creates a `WaypointObject` at the target's location (or their parent building if in a cell), sets it as `SPECIALTYPE_FINDFRIEND`, and adds it to your waypoint list (`FindFriendCommand.h:97-107`).
- Sends "Unable to locate %TU" on any failure (`FindFriendCommand.h:45-78`).
- Sends "The friend waypoint has been updated to the location of %TU." on success (`FindFriendCommand.h:109-112`).

### Ignore List
- **Adding an ignore** (`AddIgnoreCommand.h`):
  - Fails if already ignored, with message key `"ignore_duplicate"` (`AddIgnoreCommand.h:35-41`).
  - Fails if name doesn't exist or is self, with message key `"ignore_not_found"` (`AddIgnoreCommand.h:45-54`).
  - On success, calls `ghost->addIgnore(name, true)` (`AddIgnoreCommand.h:56`).
- **Removing an ignore** (`RemoveIgnoreCommand.h`): Simply calls `ghost->removeIgnore(arguments.toString())` with no validation or message (`RemoveIgnoreCommand.h:28`).

### Timings
- Mail delivery to online players happens asynchronously via `Core::getTaskManager()->executeTask()` on the "slowQueue" (`ChatManagerImplementation.cpp.lines-1783-2052:1819`, `1901`, `1963`). There is no guaranteed timing for when this executes.
- Tells are processed synchronously in `handleChatInstantMessageToCharacter`.

## 3. What a Bot Test Should Check

### Setup
- Two bot accounts (Bot A and Bot B).
- Ensure both bots can log in/out and have valid player objects.
- For tell tests: one bot should be offline (logged out) or have the other on their ignore list.
- For mail tests: send mail from online to offline recipient and vice versa.
- For friends tests: add/remove friends, test `/findfriend` with mutual and non-mutual friendships.
- For ignore tests: add the other bot to your ignore list and verify tells/mail are blocked.

### Observable Results to Check

**Tells:**
- System message received by sender when recipient is offline (IM_OFFLINE).
- System message received by sender when recipient ignores them (IM_IGNORED).
- System message for invalid name ("There is no person by the name '%TU' in this Galaxy.").
- No system message (or IM_SUCCESS) when tell succeeds to online player.
- Verify tell does not appear in receiver's chat if they are offline or ignoring.

**Mail:**
- Mail body size limit: send mail with body > PM_MAXSIZE and verify rejection (IM_TOOLONG).
- Mail to offline player: check that mail appears in their inbox after login (via `loadMail()`).
- Mail to online player: check immediate delivery.
- Mail from ignored sender: check if mail is destroyed or delivered (depends on code path).
- Mail status transitions: NEW -> UNREAD/READ after reading.

**Friends:**
- Friend list size limit at 1000.
- Cannot add god-mode players.
- Cannot add already-added friends (duplicate message).
- Cannot add ignored players.
- `/findfriend` success: waypoint appears at target's location, system message confirms.
- `/findfriend` failure: "Unable to locate %TU" when not mutual friends or when target ignores you.

**Ignore:**
- Adding ignore: verify duplicate check and invalid name check.
- Removing ignore: no feedback message expected.
- Verify tells are blocked to ignored players.
- Verify mail behavior with ignores (inconsistent across code paths).

## 4. Likely Reasons a Test Sees No Effect

- **Async mail delivery**: Mail is sent via `slowQueue` task execution; tests may check results before the task runs. Need to wait or force task processing.
- **God mode bypass**: If either bot has god mode enabled, ignore checks are skipped (`ChatManagerImplementation.cpp.lines-1462-1563:1529`, `1888`, `1952`).
- **Pending mail not loaded**: Offline player's pending mail only loads on login via `loadMail()`; tests that don't log out/in won't see it.
- **FindFriend requires mutual friendship**: `/findfriend` silently fails if the target doesn't have you as a friend; test setup must ensure bidirectional friendship.
- **Message constants undefined**: `IM_MAXSIZE` and `PM_MAXSIZE` values are not in these files; tests may use wrong thresholds.
- **No error messages on remove**: `RemoveFriendCommand` and `RemoveIgnoreCommand` send no feedback; tests cannot confirm removal succeeded without checking the list state.

## 5. Open Questions

- **IM_MAXSIZE and PM_MAXSIZE values**: Not defined in these files; need to find where these constants are declared.
- **PendingMessageList implementation**: The class `PendingMessageList` and its `addPendingMessage()` method are referenced but not included; unclear how pending mail is stored or retrieved.
- **PlayerObject methods**: `isIgnoring()`, `hasFriend()`, `addFriend()`, `removeFriend()`, `addIgnore()`, `removeIgnore()`, `addPersistentMessage()`, `getPersistentMessages()`, `checkPendingMessages()` are all called but their implementations are not in these files.
- **ChatOnSendInstantMessage message types**: The exact string IDs or ispi keys for IM_OFFLINE, IM_IGNORED, IM_TOOLONG, IM_SUCCESS, and NOAVATAR are not defined here.
- **StringIdChatParameter keys**: Message keys like `"friend_fail_is_ignored"`, `"friend_duplicate"`, `"friend_not_found"`, `"ignore_duplicate"`, `"ignore_not_found"`, and `"@ui_cmnty:friend_location_failed"` reference external string tables not included.
- **God mode detection**: `hasGodMode()` implementation is not shown; unclear how god mode is set or cleared.
- **Mail persistence storage**: The database schema for "mail" objects in `ObjectManager` is not defined here.

## ChatGPT's review (2026-10-18 22:31)

Checked Saluki lead, supplied snapshots and current Core3-dev 9d08e265, including delegated PlayerObject methods. Source only.

**Holds:** tell mute/invalid/ignore/length gates, asynchronous mail and pending-ID path, 1000 friend cap and findfriend's target-permission/zone checks. Saluki is wrong that a zone check is missing: FindFriendCommand.h:71-79 explicitly rejects a null zone.

**Corrections:**
- IM_OFFLINE/IM_IGNORED/IM_SUCCESS are protocol acknowledgment codes (ChatOnSendInstantMessage), not guaranteed literal system-message text (ChatManagerImplementation.cpp:1507-1561). Invalid names are distinguished by NOAVATAR before receiver lookup. An existing loaded but offline recipient is also checked explicitly (1532).
- findfriend requires **the target to list the requester**, not mutual friendship, and no isOnline check is explicit in this command (FindFriendCommand.h:42-79). It does return a failure message, not silently fail. Test permission direction separately.
- IM_MAXSIZE=255 and PM_MAXSIZE=4000 are defined (src/server/chat/ChatManager.idl:99-100). Plain internal sendMail lacks the same checks as the client-facing overload; mail is neither always delivered nor universally ignore-filtered (ChatManagerImplementation.cpp:1783-1819,1888-1891). Null loaded receiver versus isOnline are separate states.
- Remove commands delegate to methods that **do** send feedback: friend_not_found/friend_removed and ignore_not_found/ignore_removed (PlayerObjectImplementation.cpp:1462-1518,1627-1657). The test's no-feedback expectation is false.
- God bypass is based on the **sender's** godMode in tell/mail paths, not either bot, and findfriend has no such bypass (ChatManagerImplementation.cpp:1529,1888; FindFriendCommand.h:55-69). Reading mail sets READ; don't infer a NEW-to-UNREAD transition merely from declared constants.

Verdict: Useful protocol outline after correcting friendship direction, delegated feedback, constants, sender-only bypass and mail/ack guarantees; gameplay untested.
