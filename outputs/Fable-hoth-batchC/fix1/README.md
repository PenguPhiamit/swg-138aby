# Batch C fix1: Quartermaster Vell wanders off his spot

Fable, 14 Oct 2026. Read-only diagnosis of Core3-dev (92d99dba) and the two Esk runs; one line patch staged with
the self-tested applier (`apply.sh --selftest` passes, `--check` against dev: 1 patch, 0 refused; `work/`).

## What happened

- Esk's 09:43 run found Vell at (48.6, -2001.2), the 09:48 run at (62.2, -2028.7); the spawn spot is (44, -2010).
  One NPC (one oid), moving: a wandering AI, not a second spawn. The quest NPC template has `optionsBitmask =
  AIENABLED + CONVERSABLE` like the stock givers; the theme-park framework spawns it with `spawnMobile(...)` and
  leaves the AI's default idle behaviour, which for an agent with no `STATIC` flag is `PATROLLING`
  (`AiAgentImplementation.cpp:3699`: `if (creatureBitmask & ObjectFlag::STATIC || homeLocation.getCell() != nullptr)
  PATHING_HOME else PATROLLING`). Vell is outdoors (no cell) and had no flag, so he patrols.
- The first time, the bot walked to where Vell had been and talked after he had moved out of conversation range,
  so the server sent nothing (the C++ path is silent there: `AiAgent::sendConversationStartTo` checks range before
  it creates the observer). The second time he was in range and the conversation came through with `npc_1_1`,
  `player_1_1`, `player_2_1`, so the template registration (`mission_giver_conv.lua:477`), the handler object,
  the screens and the string lookups all work. `getNpcNumber` was not the problem: it falls back to 1 when the NPC
  is off its spawn point, and Vell is NPC 1.

## The fix (what stock does)

`ThemeParkLogic:spawnNpcs` applies `AiAgent(pNpc):addObjectFlag(AI_STATIC)` when the giver's `spawnData` has
`flags = AI_STATIC` (the stock task `tasks/dantooine/luthik_uwyr.lua` does this; `AI_STATIC = ObjectFlag::STATIC`,
set in `DirectorManager.cpp:783`). With the flag the idle tree is `wanderStatic` (`ai/static.lua`) and any move
ends in `PATHING_HOME`, so the NPC stays on, or returns to, (44, -2010). `patches.tsv` replaces Vell's `spawnData`
line in `screenplays/tasks/hoth/scavenger_quartermaster.lua` with the same line plus `flags = AI_STATIC`.

Ria Baxx, Thane Korro and Doro Kett are not spawned from `spawnData`: the framework spawns them per mission
(`ThemeParkLogic:spawnNpc`, random heading, no flag), exactly as the stock targets such as `talia_reede`. They can
drift a few metres from the waypoint like stock targets do; Korro must move (he fights). Left as stock.

## How to verify with a bot

After `apply.sh` and a test-galaxy restart: (1) search near (44, -2010) for `hoth_quartermaster_vell` / "Quartermaster
Vell" and record the position; (2) wait 120 s and search again: the position should stay within about 3 m of
(44, -2010) (before the fix he was 10 m and 26 m away); (3) walk to within 3 m and talk: expect `npc_1_1` with options
`player_1_1`..`player_5_1`; choose `player_1_1` (accept) and expect a waypoint named `waypoint_name_1` ("Ria Baxx");
(4) optional: after a minute, talk again and expect `npc_work_1`.

## The salvage detail's props

By design it has none of ours: batch B's table lists "salvage_detail (-100, -1960): props none (MTG's debris is
there)", three salvage techs and two snowtroopers. The debris is MTG's snapshot, not `object/static/structure/`
spawned by us, and it stands 60-100 m away: `transport_debris_01/02` at (-80, -1900)/(-80, -1890) (60-70 m north),
the `lucky_despot_debris_*` pieces at (-85..-125, -2045..-2055) (85-100 m south) with two camp tents and a campfire,
`sandcrawler_debris_01/02` at (0..3, -1944..-1950) (100 m east). So "5 NPCs, 0 props within 40 m" is the expected
result; a 100 m search radius finds the wreck. If the detail should have its own crates, that is a batch B follow-up
(the camp stager places `bunker_crate_style_01` at the other camps).
