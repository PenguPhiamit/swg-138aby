# BotPop social play: stage 1, groups (work in progress)

Claude, 17 Oct 2026. **Unfinished.** The usage limit cut this session short, so this page is only a hand-over note. The full design (factions, guilds, buffs, tipping, crafters, the ordering, and the pass/fail lines for botpop_findings.py) has **not** been written yet.

## What is here

`botpop-groups.patch` applies to Core3-dev `07d9f61e`. `git apply --check` passes. It has **not** been compiled (the syntax-only clang++ check was not run), built or run.

- The new file `BotPopGroups.h` is where groups form. Hunters with `wantsGroup` set (`Core3.BotPopGroups`, a percentage; 0 = off) queue at their city's mission terminal. The first in the queue invites up to 4 others within 10 levels, using the stock `invite` command. The others accept with `join`. The leader takes the mission once everyone has joined, or after 60 s.
- Missions are filtered at the group's level, using Core3's formula: the highest level plus a fifth of each other member's level. The `mission_take` row logs `lvl`, `own_lvl` and `core_lvl`. `core_lvl` is the difficulty display minus the lair's level, which is the group level Core3 actually used.
- Members accept the invite, then go to the leader's lair, then the leader's target, then follow the leader. Each member logs `group_share` rows: paid, reward, distance. These check the payout split: Core3 divides the reward by the number of players in the group and pays only those within 128 m.
- `kill` rows now log `tid` (the target) and `xp` (combat_general gained). Summing these per `tid` checks the group XP bonus (×1.2 per member, split by damage).
- New rows: `group_form`, `group_ready`, `group_join`, `group_share`, `group_alone`, `group_end`. The `server` row gains `groups` and `group_missions_done`.
- The group breaks up after `Core3.BotPopGroupMissions` missions (default 3), after 45 minutes, or before a trip. A grouped bot does not take trips on its own.

## Locking (reviewed while writing)

- Every change to a Core3 group goes through the stock commands (invite, join, disband, leavegroup) on the bot's own command queue.
- A step never locks a group or another creature. It reads only its own bot's group fields and the shared plans, which are protected by `launchShared` (taken after the bot's lock and never held while locking anything else).
- The stock group code crosses lock orders: the mission list locks creature then group, and disband locks group then creature. That cannot deadlock, because engine3's cross-lock `Locker(a, b)` releases `b` and retries.
- On logout, `PlayerObject::unload` already takes a bot out of its group. `launchGroupForget` then cleans BotPop's shared maps.

## Still to do

1. Run the syntax-only compile with the flags from `build/dev/compile_commands.json` (the CommandConfigManager.cpp entry). Put an overlay `-I` folder holding the patched botpop headers first on the include path.
2. Write the full design (Part 1 of the brief).
3. Add the owner questions to SWG-handoff.md: factions beyond Imperial and Rebel, bot guild names, whether bots go overt.
4. Groups need `Core3.BotPopMode = "all"`. In throttled mode, members that aren't acting won't join or follow.
