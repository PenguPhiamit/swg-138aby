# BotPop social play: what players did together, and how the bots get there

Claude (Opus 5.5), 17 Oct 2026. This is the design (Part 1) plus stage 1, groups (Part 2:
[`botpop-groups.patch`](botpop-groups.patch)). Core3 was read in WSL, read-only, at Core3-dev `07d9f61e`. Nothing
was built, run or deployed.

Why this exists:
- **Owner, 17 Oct, 1:10 AM:** "in the old days we would do faction missions and join large groups to get better
  missions, i think the bots are missing alot of the player nuance, are they forming guilds? working together like
  the game needs?"
- **Owner, 17 Oct, about 5:35 AM** (playing on the test galaxy with 300 bots in mode all, relayed by the real-client
  session): "the bots are moving correct lanes and such but, 1 their nowhere near looking like an actual population the
  way their moving. and im concerned their not progressing/ building guilds and cities and working together".

Where BotPop stands today: every bot plays alone. There is no group, guild or faction code. Bots take only DESTROY
missions, from general terminals, at up to their level + 2 (`Core3.BotPopMissionAbove`). Entertainers dance and medics
heal, but nobody tips or buys a buff, and crafters don't exist.

## 1. What pre-CU players did together, and the Core3 system behind each

"Read" means I read the Core3 code on 17 Oct. "Not read" means the system's name is known but its details were not
checked.

| Players did | Core3 system | What it takes | Read? |
|---|---|---|---|
| **Hunting groups**: up to 20 in a group, one leader, invite and accept | `GroupManager` (`managers/group/GroupManager.cpp`). `/invite` sets the target's inviter ID (`inviteToGroup`, inviter locked, target cross-locked). `/join` runs `joinGroup` in a task with no locks held. `/disband` and `/leavegroup` | Nothing beyond the commands. None of the four has a character ability, so every player can use them | Read |
| **Group missions**: a group takes harder, better-paid destroy missions | `MissionManager::getRandomLairSpawn` and `randomizeGenericDestroyMission` use `GroupObject::getGroupLevel` instead of the player's level when the taker is grouped (lines 866-873 and 1910-1918). The group level is the highest member's level plus a fifth of each other member's (`calculateGroupLevel`). The payout (`MissionObjective::awardReward`) is the reward divided by the number of players in the group, paid to each player member within 128 m of the mission spot | The leader is grouped *before* asking the terminal for missions | Read |
| **Group XP**: share a kill and get a bonus | `PlayerManager::disseminateExperience`. Each attacker within 80 m gets experience in proportion to its damage, times `groupExpMultiplier` = 1.2 if grouped (`player_manager.lua:57`). A squad leader also gets squad leader experience | Being in the same group | Read |
| **Group loot** | `GroupManager` loot rules: free for all, master looter, lottery, random (`createLottery`, `doRandomLoot`, `transferLoot`) | The leader sets the rule (the default is free for all) | Read |
| **Factions**: Imperial or Rebel recruiters, faction points, ranks, covert and overt | Faction and status on every creature (`Factions.h`, `FactionStatus.h`). `FactionManager`: standing awards, rank costs and caps. Joining and ranks go through the recruiter's conversation (screenplay) | A recruiter conversation, or the server calls it makes. Standing from kills of the other side's NPCs | Partly read (recruiter flow not read) |
| **Faction missions** | The same destroy missions from Imperial or Rebel terminals. A covert or overt member of that side gets the factional lair list (`getRandomLairSpawn`, lines 1862-1880) and faction points on completion (`MissionObjective`, line 144: `increaseFactionStanding`). Anyone else gets the neutral list | Joined a side, covert or overt | Read |
| **GCW bases**: player bases, battles | `GCWManager`, faction bases (structures), the base terminals | Overt players, base deeds, an enemy side | Not read |
| **Guilds**: registry, tag, chat, elections, guild wars | `GuildManager`. A guild is created from a **guild terminal**, which stands in a **guild hall**: a player structure that a player owns (`sendGuildCreateNameTo(player, GuildTerminal*)`). Sponsorship, member titles, elections and wars are all terminal menus | A placed guild hall (an architect's deed), so the same structure questions as cities | Read (creation path) |
| **Player cities** | City regions, mayor, election, upkeep | See [`bot-cities-plan.md`](../bot-cities-plan.md) (probes P1-P3) | Covered there |
| **Entertainer buffs**: watch a dancer or musician for a mind buff; image design | `EntertainingSession` (the buff after watching) | Watching for long enough; the buff check | Read (session only). The squad's "gets the dance buff after 70 s" check still fails (test plan, item 22) |
| **Medic and doctor buffs** | Doctor enhancements in a hospital cell (`MedicalAnywhere = true` on test) | A doctor, a patient who asks, payment by tip or trade | Not read in depth |
| **Tipping** | `TipCommand` (`/tip`): cash at once, or bank with a confirmation box | Two characters near each other | Read (it exists) |
| **Crafters selling** | Vendors, the bazaar, crafting sessions | Crafting professions, which BotPop doesn't have | Not read |

## 2. What BotPop should copy, in order

Both purposes count:
- **(1) Scale tests and data.** Each system works with hundreds of users at once, and the logs give its numbers.
- **(2) A lived-in world.** A smaller population that looks like players.

| Stage | What bots do | (1) What it tests and measures | (2) What a player sees | Needs |
|---|---|---|---|---|
| **S1 Groups** (patch here) | Hunters at the same terminal group (2-5), take a group-level mission, travel and fight together, then break up | Group create, join and leave under load; group-level missions; the payout split; the 1.2 XP bonus | Bots running in groups of 3-5 to a lair; group names in the list | Nothing new |
| **S2 Support economy** | Hunters tip the dancer they watched and the medic who healed them; medics heal for a tip; later, doctors buff | `/tip` at scale; the dance buff (still failing for the squad); credits moving between bots | Dancers with crowds who tip; medics busy in town | S1 only for grouped hunters' rests |
| **S3 Factions** | Some bots join a side through a recruiter, go covert (overt only with the owner's OK), take faction missions from faction terminals in groups, earn points, buy ranks | Faction join, faction missions, faction points, rank costs; whether faction NPCs treat bots right | Imperial and Rebel bots in uniform at bases | Owner questions Q1 and Q3; [`Fable-factions/README.md`](../../Fable-factions/README.md) Option A (era names for the two GCW sides) |
| **S4 Guilds** | A bot with a guild hall founds a guild; group members who play together often join it; guild chat, elections | Guild create, sponsor, accept, elections, guild-hall upkeep with transient owners | Guild tags over bots' heads | A placed guild hall: the same transient-owner problem as bot cities' probe P1. Owner question Q2 (names) |
| **S5 Cities** | Guilds settle a disposable town | All of [`bot-cities-plan.md`](../bot-cities-plan.md) | Bot towns | That plan's P1-P3 first |
| **S6 GCW** | Overt groups at bases, base battles | Overt PvP flags, the base system | Battles | Owner decides; only on test |

**Recommendation:** S1, then S2, then S3, in that order. S1 is ready to build. S2 is small and shows a lot to a
player in town. S3 waits on two owner answers. S4 and S5 wait on bot-cities probe P1 (structures owned by transient
characters), so they come after that probe, not before.

**The owner's movement point** (5:35 AM: "nowhere near looking like an actual population the way their moving")
isn't a social feature, and it needs its own look. Today every bot walks the same way at a steady 5 m/s and stops
dead. S1 helps a little, because groups travel together. Other things to try: idling and emoting in town, varied
speeds, running only in combat, sitting near the terminal and the cantina, and following roads between towns. I
propose it as a separate task.

## 3. How this fits the existing plans

- **[`Fable-factions/README.md`](../../Fable-factions/README.md):**
  - S3 uses Option A: the two GCW sides keep Core3's machinery, with the Triumvirate and Krayt's holdouts as their era
    meanings.
  - Bots don't join the seven new standing-only sides until that data exists. Then they gain standing by killing
    those NPCs, which needs no new code.
  - A third GCW side (Option C) is out of scope.
- **[`bot-cities-plan.md`](../bot-cities-plan.md):** S4 and S5 depend on its P1 (maintenance on structures owned by
  transient characters). A guild hall is such a structure. Guild names follow its Q12 (our own 138-139 ABY lists,
  normal uniqueness checks).
- **[`functional-test-plan.md`](../functional-test-plan.md), item 21** (groups, guilds, mail, friends). Its gaps are
  "no check of group XP split, guilds". S1's rows check the XP split and the payout split at scale. Guilds come
  with S4. Item 22 (the dance buff) is S2's first check.
- **[`server-side-bots.md`](../server-side-bots.md):** groups need every member acting every second, which means
  mode **all**. In throttled mode a member that isn't in the active set never accepts or follows; it gives up after
  60 s with `group_end` reason "never joined". A small lived-in population would need group members kept in the
  active set together (a later change).

## 4. What each stage logs to `botpop-launch.jsonl`, and the pass/fail lines

Rows already in S1's patch:

| Row | Fields | Written when |
|---|---|---|
| `group_form` | `gid` (the leader's object ID), `invited`, `lvl`, `lvls`, `seekers` | The leader sends its invites |
| `group_join` | `secs` (since the invite), `lvl`, `gid`, `gsize` | A member is in the Core3 group |
| `group_ready` | `invited`, `joined`, `secs`, `glvl` (BotPop's group level) | The leader is ready to take missions |
| `group_alone` | `secs`, `seekers`, `lvl` | A seeker waited `Core3.BotPopGroupWait` seconds and goes alone |
| `group_share` | `paid` (bank change), `reward`, `mlvl`, `dist` (from the mission spot), `gid`, `gsize` | A member sees the leader's mission paid |
| `group_end` | `grole`, `reason`, `gsize`, `done`, `mins` | The bot leaves or disbands |
| `mission_take` (changed) | Adds `own_lvl`, `core_lvl` (the level Core3 made the mission for), `gid`, `grole`, `gsize`. For a leader, `lvl` is now the group's level | |
| `mission_done` (changed) | For a leader: `near` (members within 128 m), `gid`, `gsize` | |
| `kill` (changed) | `tid` (the creature's ID), `xp` (combat_general since the bot's first shot), group fields | |
| `snap`, `mission_none` (changed) | Group fields | |
| `server` (changed) | `groups`, `group_missions_done` | |

Proposed `botpop_findings.py` lines (section "Groups"). They are not written into the tool yet:

- **Forming:** groups formed ÷ bots who looked for one. PASS ≥ 50%. WATCH 20-50%. FAIL < 20%, or no `group_form`
  rows at all while `Core3.BotPopGroups` > 0.
- **Joining:** `group_join` ÷ invites sent. PASS ≥ 90%. FAIL < 70% (the invite or join path is broken).
- **Group level:** on leaders' `mission_take` rows, `core_lvl` against `lvl`. PASS when the median difference is
  within 2. FAIL when `core_lvl` sits near the leader's `own_lvl`, which would mean Core3 didn't use the group's level.
- **Payout split:** on `group_share` rows with `dist` < 128, `paid` ÷ (`reward` ÷ `gsize`). PASS when the median is
  0.9-1.1. FAIL outside 0.5-1.5. Members over 128 m away should get 0 (WATCH if they don't).
- **XP bonus:** for creatures killed by both grouped and solo bots at the same level, the sum of `xp` per `tid` for
  grouped kills ÷ the median solo `xp`. PASS at 1.1-1.35 (expected 1.2). WATCH otherwise. Caveat: if Core3 awards
  the experience after BotPop's kill row, some rows read 0; the line uses medians and reports the count of zeros.
- **Group missions:** finished ÷ taken, grouped against solo at the same `mlvl`. WATCH if grouped is lower (the
  members aren't helping).
- **Break-ups:** count by `group_end` reason. WATCH if "never joined" or "leader gone" is over 20%.

Later stages:

- **S2:**
  - Rows: `tip` (to, amount, cash or bank, why), `buff` (from, kind, duration).
  - PASS when tips land (the receiver's credits rise by the amount) and a watching bot gets the dance buff in ≥ 90%
    of rests over 70 s.
- **S3:**
  - Rows: `faction_join` (side, status), `faction_mission_take` and `faction_mission_done` (points before and after),
    `rank_buy`.
  - PASS when points rise by the mission's award, and bots of one side are never attacked by their own side's NPCs.
- **S4:**
  - Rows: `guild_create`, `guild_sponsor`, `guild_join`, `guild_upkeep`.
  - PASS when guild halls survive maintenance while their owner is online, and leave no orphan rows after logout
    (bot-cities P1's checks).

## 5. Stage 1 in detail: [`botpop-groups.patch`](botpop-groups.patch)

**Apply:** `git apply --check` passes against Core3-dev `07d9f61e`. The changes are:
- one new file, `BotPopGroups.h`;
- small hooks in `BotPopLaunch.h` (LaunchState fields), `BotPopManager.h` (shared maps, declarations, config text,
  logout clean-up, server row) and `BotPopLaunchBrain.h` (the terminal, the member step, the level filter, the rows,
  trips).

**Off by default:** `Core3.BotPopGroups = 0`. Settings:

```lua
Core3.BotPopGroups = 50          -- percent of hunters (brawler, marksman, scout) that look for a group
Core3.BotPopGroupMax = 5         -- 2 to 5
Core3.BotPopGroupWait = 90       -- seconds at the terminal before going alone
Core3.BotPopGroupMissions = 3    -- missions before the group breaks up
```

**How it plays:**
1. A hunter that wants a group reaches its city's general mission terminal and joins that terminal's queue.
2. The first in the queue leads, once the group would be full or a third of the wait has passed with someone else
   there. It picks up to four others within 10 levels of it and sends each one a `/invite`.
3. A picked bot sees the invite (`getGroupInviterID`) and sends `/join`.
4. When everyone has joined, or after 60 s, the leader asks for the mission list. Core3 makes the missions at the
   group's level. BotPop's own filter uses the group's level (Core3's formula over the members' combat levels) plus
   `Core3.BotPopMissionAbove`.
5. Members take on, in order: the leader's lair (attacking it as the leader does, 6 m for ranged and 4 m for melee),
   then whatever the leader is fighting within 80 m, then the leader's heels (12 m away at most).
6. A hurt member still goes to town to rest, as before. It isn't paid if it is more than 128 m away when the lair
   dies. That is what Core3 does, and the share row records it.
7. The leader disbands the group after the set number of missions, after 45 minutes, or before any trip. Grouped bots
   don't start trips of their own.

**Locks (checked against C60's rules):**
- **Group changes:** every change to a Core3 group goes through the stock commands (`invite`, `join`, `disband`,
  `leavegroup`) on the bot's own command queue. So `GroupManager` runs with exactly the locks it takes for a player.
- **What a step reads:**
  - its own bot's group fields, under the bot's lock;
  - other bots' and creatures' positions, unlocked (as the medics' patient search already does);
  - BotPop's plans, under `launchShared`. A step takes it after its bot's lock and never locks anything else while
    holding it.
  - A step never locks a group or another creature.
- **The stock mixed order is safe:**
  - The mission list locks the leader, then the group: a plain `Locker(group)` in `getRandomLairSpawn`.
  - `GroupObject::disband` and `joinGroup` lock the group, then a member, with engine3's cross-lock `Locker(member,
    group)`.
  - That cross-lock tries the member's lock and, if it is taken, releases the group, yields and tries again
    (`ReadWriteLock::wlock(ReadWriteLock*)`). So the two orders can't deadlock. This is the same for players, and
    BotPop adds no new lock order.
- **Logout:** `PlayerObject::unload` (called by `ClientlessLogin::logout`) takes the bot out of its group with
  `leaveGroup`. `launchGroupForget` then removes it from BotPop's maps; it runs after the bot's lock is released.

**Not checked or untested:**
- **Compile (checked):** clang++ 19 `-fsyntax-only` ran with `CommandConfigManager.cpp`'s flags from
  `build/dev/compile_commands.json`, with the patched headers in an overlay folder first on the include path. It gave
  no errors. A planted `#error` in the overlay copy did fire, so the patched files were the ones compiled. This is
  not a link or a full build.
- **Group level:** whether Core3's `CreatureObject::getLevel()` for a bot matches BotPop's combat level. If it
  doesn't, `core_lvl` shows it.
- **Experience timing:** whether the experience lands before the kill row.
- **Several invites at once:** whether queuing several `/invite`s in one step works, or the queue drops some. If any
  are dropped, the joining line shows it.
- **Live use:** nothing was built or run.

## Questions for the owner

These are on the board under "Questions for the owner" (17 Oct).
