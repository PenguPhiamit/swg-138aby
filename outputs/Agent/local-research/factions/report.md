# Faction Joining, Status, Points, and Promotion Report

## 1. Short Answer

A player joins a faction by speaking to a recruiter NPC and selecting the join option; this immediately sets their faction affiliation and covert status (status 1). They can later switch between covert (hidden), overt (visible/attackable), and on-leave (inactive) statuses through conversation options, each with timers ranging from 30 seconds to 15 minutes. Faction points are earned through activities and bribes, capped by rank via `getFactionPointsCap()`, and spent to promote ranks. Jedi characters cannot go covert or resign. The bot test must verify status changes, cooldowns, point caps, and system messages at each step.

## 2. How It Works

### Joining a Faction
- The player initiates conversation with a recruiter NPC. The initial screen is determined by the player's current faction and standing (`recruiterConvoHandler.lua:230-276`).
- For neutral players meeting the minimum standing requirement (200, defined in `recruiterScreenplay.lua:8`), the "join_military" option appears (`recruiterConvoHandler.lua:287-301`).
- Selecting join sets the player's faction hash and status to 1 (covert) immediately: `CreatureObject(pPlayer):setFaction(...)` and `setFactionStatus(1)` (`recruiterConvoHandler.lua:36-37`, `144-145`).
- The recruiter's faction is determined by its own faction hash: rebel = 370444368, imperial = 3679112276 (`recruiterScreenplay.lua:10`).

### Status Changes (Covert/Overt/On-Leave)
Three statuses exist: covert (1), overt (2), on-leave (0).

**Going Covert:**
- Jedi characters are blocked: `hasSkill("force_rank_light_novice")` or `hasSkill("force_rank_dark_novice")` prevents it (`recruiterConvoHandler.lua:44-47`, `53-56`).
- Sets `futureFactionStatus(1)` and writes `changingFactionStatus` data flag (`recruiterConvoHandler.lua:49-50`).
- Creates a delayed event after 5 minutes (300,000 ms) to call `handleGoCovert` (`recruiterConvoHandler.lua:51`).
- When complete, `setFactionStatus(1)` is called, which removes the OVERT PVP flag and sends "Your faction affiliation has now been hidden from others." or `@faction_recruiter:covert_complete` (`TangibleObjectImplementation.cpp.lines-176-311:195-200`).

**Going Overt:**
- Similar flow but sets `futureFactionStatus(2)` and uses a 30-second timer (30,000 ms) (`recruiterConvoHandler.lua:39-42`).
- When complete, `setFactionStatus(2)` adds the OVERT flag, applies a "declare_overt_cooldown" of 300 seconds (configurable via GCWManager), and sends "You successfully declare overt faction status. You may now be attacked by opposing faction members." (`TangibleObjectImplementation.cpp.lines-176-311:204-224`).
- Also adds the player to the PVP broadcast chat room if enabled (`TangibleObjectImplementation.cpp.lines-176-311:227-237`).

**Going On-Leave or Resigning:**
- Both set `futureFactionStatus(0)` and use 5-minute timers (`recruiterConvoHandler.lua:52-60`, `62-70`).
- Resignation can also be initiated with a configurable timer (default 15 minutes from `recruiterScreenplay.lua:6`) via pending task instead of immediate event (`recruiterConvoHandler.lua:150-171`).
- On complete, removes OVERT flag and sends resignation message (`TangibleObjectImplementation.cpp.lines-176-311:238-251`).

**Canceling Resignation:**
- Removes the `changingFactionStatus` data and cancels the pending task (`recruiterConvoHandler.lua:205-207`).

### Faction Points (Standing)
- **Earning points:** Through activities (not shown in these files) and bribes. Bribe options require `combat_smuggler_underworld_04` skill and sufficient credits (20,000 or 100,000). A 20k bribe gives 250 points; a 100k bribe gives 1,250 points (`recruiterConvoHandler.lua:101-111`, `recruiterScreenplay.lua:75-90`).
- **Caps:** For faction members, capped by rank via `getFactionPointsCap(player->getFactionRank())` (`PlayerObjectImplementation.cpp.lines-2155-2322:2182`). Non-members cap at 1,000; non-PvP factions cap at 5,000 (`PlayerObjectImplementation.cpp.lines-2155-2322:2174-2185`).
- **Losing points:** `decreaseFactionStanding` applies similar caps and minimum of -5,000 (`PlayerObjectImplementation.cpp.lines-2155-2322:2263-2299`).

### Rank Promotion
- Available if current rank is valid and not highest (`recruiterConvoHandler.lua:354-356`).
- Requires `getRankCost(rank + 1)` points and minimum standing (`recruiterConvoHandler.lua:84-86`, `358-360`).
- If insufficient points, shows "not_enough_points" screen with required amount (`recruiterConvoHandler.lua:87-95`).
- On success, decreases standing by the cost and sets new rank via `setFactionRank(rank)`, which broadcasts the change to nearby players (`CreatureObjectImplementation.cpp.lines-2072-2086:2072-2085`).

### Messages the Player Sees
- Join/covert/overt/resign complete messages as described above.
- Bribe success/failure based on credit checks.
- Promotion confirmation with rank name via `getRankName(rank)` (`recruiterConvoHandler.lua:80`, `94`).
- Jedi restriction messages: `@faction_recruiter:jedi_cant_go_covert` and `@faction_recruiter:jedi_cant_resign` (`recruiterConvoHandler.lua:45`, `54`, `64`).

## 3. What a Bot Test Should Check

### Setup Needed First
- Ensure bot character has no Jedi skills (`force_rank_light_novice` or `force_rank_dark_novice`) if testing covert/resign paths.
- Verify bot is neutral (faction = 0) and has at least 200 faction standing with the target recruiter's faction before attempting to join.
- For bribe tests, ensure bot has `combat_smuggler_underworld_04` skill and sufficient credits (20k or 100k).

### Observable Results to Check
1. **After joining:** 
   - System message confirming covert status.
   - `getFaction()` returns recruiter's faction hash.
   - `getFactionStatus()` returns 1.
   - OVERT PVP flag is not set.

2. **After going overt (30s timer):**
   - System message about being attackable.
   - OVERT PVP flag is set.
   - "declare_overt_cooldown" cooldown exists (check via `hasCooldown`).
   - Player added to PVP broadcast channel if enabled.

3. **After going covert (5min timer):**
   - System message about hidden affiliation.
   - OVERT PVP flag removed.
   - Covert status confirmed.

4. **Faction points:**
   - Standing increases by bribe amount (250 or 1,250) and system message confirms change.
   - Standing does not exceed rank cap (verify via `getFactionPointsCap`).
   - Bribe options only appear when skill and credit requirements are met.

5. **Promotion:**
   - Promotion option appears if rank < max.
   - System message with rank name on confirmation.
   - Faction points decrease by `getRankCost(rank + 1)`.
   - `getFactionRank()` returns new rank, broadcast to nearby players.

6. **Jedi restrictions:**
   - Jedi characters see restriction messages and cannot select covert/resign options.

7. **Resignation cancellation:**
   - Pending task canceled when option selected.
   - `changingFactionStatus` data removed.

## 4. Likely Reasons a Test Sees No Effect

- **Timer not elapsed:** Status changes require waiting for the event/task to fire (30s or 5min). Bot must wait or verify pending state.
- **Jedi skills present:** If bot has `force_rank_light_novice` or `force_rank_dark_novice`, covert and resign options are blocked (`recruiterConvoHandler.lua:44-47`).
- **Insufficient standing:** Joining requires 200 standing (`recruiterScreenplay.lua:8`); promotion requires rank-specific cost.
- **Missing skill/credits for bribes:** `combat_smuggler_underworld_04` and 20k/100k credits required (`recruiterConvoHandler.lua:101-106`).
- **Already at highest rank:** Promotion option suppressed if `isHighestRank(rank)` returns true (`recruiterConvoHandler.lua:354`).
- **Cooldown active:** After going overt, 300s "declare_overt_cooldown" prevents immediate re-declaration (`TangibleObjectImplementation.cpp.lines-176-311:206-217`).
- **Wrong recruiter faction:** Bot must talk to the correct recruiter for the desired faction.

## 5. Open Questions

- **Rank cost table:** The files reference `getRankCost(rank)` and `getFactionPointsCap(rank)` but do not define these functions in the provided snippets. Missing file or function that defines rank progression costs and caps.
- **`isHighestRank(rank)`:** Function name used but not defined in provided files. Need source to determine max rank value.
- **`useCovertOvert()` and `getGCWDiscount()`:** Helper functions called but not defined here; likely in other screenplay or manager files.
- **Faction point earning activities:** These files only show bribe-based earning. Missing documentation on combat, objectives, or other activities that grant points.
- **`handleGoCovert`, `handleGoOvert`, `handleResign`, `handleGoOnLeave`:** Event handlers called by timers but not shown in provided snippets; need to verify they correctly apply status changes.
- **PVP broadcast channel:** Behavior depends on server config `isPvpBroadcastChannelEnabled()`; unclear default behavior (`TangibleObjectImplementation.cpp.lines-176-311:227`).


## ChatGPT's review (2026-10-18 02:27)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) and available `src/` snapshots; no in-game checks. The original draft remains above; corrections below take precedence.

**Holds:** faction hashes/statuses, 200 standing, immediate covert join, 30 s overt and 5 min legacy transitions, separate 15 min configurable resignation, Jedi restrictions, base caps and 20k/100k CASH bribes for 250/1250 hold (recruiterConvoHandler.lua:35-111,125-169; recruiterScreenplay.lua:4-10,75-89; TangibleObjectImplementation.cpp:176-251; PlayerObjectImplementation.cpp:2174-2184). Stored C++ slices and recruiter Lua match current source apart from trailing blank lines.

**Saluki flags:** the bribe prerequisite/value claim IS shown at recruiterConvoHandler.lua:101-111 (the grant helper alone lacks these gates). Its rank objection confuses local variable meaning: accepted_promotion first sets local rank=current+1 then calls getRankCost(rank) (83-84); the menu uses current rank and getRankCost(rank+1) (352-361). Both charge the NEXT rank. The report's expression is correct only with rank explicitly meaning the old rank; it must not be applied to the already-incremented local.

**Corrections/qualifications:**
- Having enough for the cost alone is insufficient: promotion keeps minimum standing 200 after payment (86,97-98,361). The promotion menu also requires sufficient standing, not merely rank<max (354-365).
- Bribes require enough room for the whole award under the rank cap (102,106,110); credits and skill alone do not guarantee the option. Funds are cash, not combined cash/bank (105-111).
- On-leave is not necessarily resignation. handleGoOnLeave retains faction and sets status 0 (recruiterScreenplay.lua:769-780). handleResign additionally clears affiliation/rank in the covert/overt branch (802-827). Their dialogs depend on useCovertOvert.
- A cooldown is created only when OVERT was absent (TangibleObjectImplementation.cpp:204-217); that code by itself does not prove which later transition is blocked.
- Delayed handlers are present in the same recruiterScreenplay at 769-827; they were not absent source. Joining/status text may be raw or a string ID depending on config, so no single English message is universal.

**Limit:** no faction action, bribe or timer test was run.

**Verdict:** Most numeric claims hold; Saluki rank/bribe objections are misleading, but qualify promotion reserve, bribe cap room, cash and on-leave versus resignation.
