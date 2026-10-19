# Badge System Report

## 1. Short Answer

Badges are awarded through three main paths: entering a `BadgeActiveArea` grants the area's badge if the player lacks it; the server automatically checks total and exploration-badge counts after every award and grants accumulation milestones at fixed thresholds (5, 10, 25, 50, 75, 100, 125 total badges; 10, 20, 30, 40, 45 exploration badges); event badges are granted via the same `awardBadge` function but their trigger sources are not in these files. Each award sends a localized system message (using `badge_n` with either `prose_hasbadge` or `prose_grant`), optionally plays a music file if the badge defines one, and fires a `BADGEAWARDED` observer event. Badges are stored as bitmasks in five `uint32` slots plus per-type counters, so a test can query ownership via `hasBadge()`, bitmask getters, or type/total counts on the player's `PlayerObject`.

## 2. How It Works

### Conditions and triggers
- **Exploration-area badges**: When a player enters a `BadgeActiveArea`, the area calls `ghost.hasBadge(areaBadge)` and, if false, calls `ghost.awardBadge(areaBadge)` (BadgeActiveArea.idl lines 22-32). The badge is granted only once per player.
- **Accumulation badges (total count)**: After every successful award, `awardBadge` checks `ghost.getNumBadges()` and grants milestone badges at counts 5, 10, 25, 50, 75, 100, 125 using keys `"count_5"`, `"count_10"`, etc. (PlayerManagerImplementation.cpp.lines-2510-2593 lines 2545-2569).
- **Accumulation badges (exploration count)**: If the just-awarded badge has type `Badge::EXPLORATION`, the code checks `ghost->getBadgeTypeCount(static_cast<uint8>(Badge::EXPLORATION))` and grants milestones at 10, 20, 30, 40, 45 exploration badges using keys `"bdg_exp_10_badges"`, etc. (lines 2571-2591).
- **Event/content/other badges**: Granted via the same `awardBadge` function; their trigger sources are not in these files (inferred).

### Badge data and types
- Badge definitions are loaded from `datatables/badge/badge_map.iff` at server startup (BadgeList.cpp lines 46-70). Each row provides INDEX, KEY, MUSIC, CATEGORY, SHOW, and TYPE columns (Badge.cpp lines 19-35).
- Valid TYPE strings parsed by `getTypeFromString`: `"accumulation"`, `"interest"`, any string containing `"exploration"`, `"master"`, `"events"`, `"content"` (Badge.cpp lines 38-60).

### Storage structure
- The player's `PlayerObject` holds a `Badges` object with:
  - `badgeBitmask[5]`: five `uint32` values; each bit represents one badge index (supports up to 160 badges) (Badges.h lines 19, 111-127).
  - `badgeTypeCounts[6]`: per-type counters (Badges.h lines 20, 125).
  - `badgeTotal`: total badge count (Badges.h line 21).

### Messages, sounds, and XP
- **System message**: Built with `StringIdChatParameter("badge_n", "")` and set to either `"prose_hasbadge"` (if already owned) or `"prose_grant"` (if newly awarded), then sent via `player->sendSystemMessage(stringId)` (lines 2522-2535).
- **Music**: If `badge->getHasMusic()` is true, a `PlayMusicMessage` with `badge->getMusic()` is sent to the player (lines 2537-2541).
- **XP**: Not visible in these files; likely defined elsewhere or absent (inferred).

### Observer event
- After granting, the server fires `ObserverEventType::BADGEAWARDED` with the player and badge ID as parameters (line 2543).

## 3. What a Bot Test Should Check

### Observable results
1. **System message**: Verify the chat parameter resolves to the expected prose key (`prose_grant` for first award, `prose_hasbadge` for duplicate) under the `badge_n` category.
2. **Music playback**: If testing a badge with non-"NONE" music, check that a `PlayMusicMessage` is received on the client side.
3. **Badge ownership**: Query the player's `PlayerObject` (slotted as `"ghost"` on `CreatureObject`) and call:
   - `hasBadge(badgeId)` to confirm the specific badge is set.
   - `getNumBadges()` to verify total count increased by 1.
   - `getTypeCount(type)` to verify the correct type counter incremented.
4. **Accumulation triggers**: After reaching a milestone count, verify the corresponding `"count_N"` or `"bdg_exp_M_badges"` badge appears in ownership and that its system message/music also fire.

### Required setup
- Ensure the player character is logged in and has a valid `PlayerObject` ghost slot.
- For area tests: place or trigger entry into a `BadgeActiveArea` with a known `areaBadge` value.
- For direct award tests: use the server console command `/grantBadge [badgeId]` (GrantBadgeCommand.h lines 18-163) or invoke `awardBadge` programmatically if accessible.
- To read badges remotely, use `/requestBadges <targetCreatureId>` which calls `playerObject->sendBadgesResponseTo(creature)` (RequestBadgesCommand.h lines 38-39); the response format is not in these files (inferred).

## 4. Likely Reasons a Test Sees No Effect

1. **Badge already owned**: `hasBadge` returns true, so `awardBadge` sends only the `"prose_hasbadge"` message and skips music/event logic (lines 2527-2531).
2. **Null badge key/index**: If `BadgeList::instance()->get(badgeId)` returns nullptr, the function logs an error and returns without awarding anything (lines 2517-2520).
3. **Area not triggering**: The player may not be entering a `BadgeActiveArea` zone, or the area's `areaBadge` is 0/unset.
4. **Timing/ordering**: Accumulation badges are granted synchronously after the primary award; if the test checks counts before the function completes, it may miss them.
5. **Ghost slot missing**: If `playerCreature->getSlottedObject("ghost")` returns null, badge queries or `/requestBadges` will fail silently (RequestBadgesCommand.h lines 36-39).
6. **Badge type mismatch**: Exploration accumulation checks only fire when the awarded badge's type is `Badge::EXPLORATION`; other types won't trigger exploration milestones.

## 5. Open Questions

1. **XP rewards**: None of these files show XP being granted; the datatable columns (INDEX, KEY, MUSIC, CATEGORY, SHOW, TYPE) do not include an XP field (Badge.cpp lines 19-35). The XP logic is likely in another file or absent.
2. **`/requestBadges` response format**: `sendBadgesResponseTo()` is declared but not defined here; the client message structure is unknown.
3. **Event badge triggers**: No source code in these files shows what game events call `awardBadge` for EVENT-type badges (Badge.h line 19).
4. **`PlayerObject::awardBadge` wrapper**: The `Badges::setBadge` method updates bitmasks and counters, but the path from `PlayerObject` to this class (e.g., whether `PlayerObject` delegates to its internal `Badges` object) is not shown in these files.
5. **Maximum badge index**: The bitmask supports 160 badges (5 × 32 bits), but it is unclear if the datatable or game design enforces a lower limit.

## ChatGPT's review (2026-10-18 22:31)

Checked matching badge/area/command snapshots and current Core3-dev 9d08e265; no Saluki disputed lead for this report. Source only.

**Holds:** five uint32 masks and six type counters, 0-159 representable indices, data-driven music/type, direct-award duplicate guard, BADGEAWARDED observer and the listed exact total/exploration milestone cases (Badges.h:104-127; PlayerManagerImplementation.cpp:2516-2591; BadgeActiveArea.idl:22-31).

**Corrections and test limits:**
- Re-entering a BadgeActiveArea with an owned badge is **silent** because the area skips awardBadge; prose_hasbadge is a direct duplicate-award result (BadgeActiveArea.idl:29-30 versus PlayerManagerImplementation.cpp:2527-2530).
- A primary award can recursively award accumulation badges and increase total by more than one (2545-2586). Assert the complete delta at milestone boundaries, not always +1. Threshold checks are equality switch cases, not a generic catch-up for every already-passed threshold.
- Badge index zero is not inherently invalid: Badges::setBadge rejects bitmaskNumber outside 0..4, not badgeId==0 (109-120). Only absence from BadgeList proves a null-definition failure (PlayerManagerImplementation.cpp:2517-2520).
- getTypeCount belongs to the internal Badges helper; the PlayerObject-facing call shown in the award path is getBadgeTypeCount (2572). These C++/IDL APIs are not evidence the bot MCP exposes them.
- /grantBadge is an in-game administrative queue command with a target/area syntax (GrantBadgeCommand.h:18-50), not a server-console syntax guarantee. No direct grants or game commands were executed for this review. Prefer natural area entry to test the exploration trigger.
- No XP award is present in this award path; unrelated badge observers/content may have separate rewards. Their absence from this excerpt does not establish a global no-XP rule.

Verdict: Badge storage/award mechanics largely supported; qualify duplicate-area silence, recursive count deltas, index zero and test API/command assumptions; gameplay untested.
