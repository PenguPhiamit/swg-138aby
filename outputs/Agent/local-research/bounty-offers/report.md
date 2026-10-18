# Report: why a bounty terminal offered Brask no bounty mission

Written by Claude, 18 Oct 2:14 AM. The local model (qwen3.6 on Microverse) wrote no report: it read the files, then
thought for about 200,000 characters without answering (agent-log.jsonl, step 3). This report is from the code in
`src/` and run 3's own record, `Bot-reports/Forn/20261017-232839-forn-missions.json`.

## 1. Short answer

**The server refused every list request because Brask was more than 6 m from the terminal.**

- His 93 system messages after the step-up were all `@radial_out_of_range_prose:ui_radial` ("%TT is too far away to 'List Missions'"), sent at MissionManagerImplementation.cpp:170-175.
- A refused request returns before `populateMissionList`, so his mission bag kept the offers from earlier lists at other terminals: dancer 6, destroy 6, musician 6, recon 4 (check 9 of the report).
- That is why "no bounty mission fits". Range *is* the cause.
- The walk to the terminal reported `arrived: true` with "could not reach the destination; stopped at the end of the last path" after 2.4 s (check 3). The one step-up walk (missions.py, `bounty()`) did not close the gap either.

## 2. How it works (from the code)

- **The bounty list needs three things** (MissionManagerImplementation.cpp:165-200):
  - the player within 6 m of the terminal (170-175);
  - the `combat_bountyhunter_novice` skill (178-183, else `@mission/mission_generic:not_bounty_hunter_terminal`). Brask's agentskill grant succeeded (events, t 10.8);
  - the list cooldown, `Core3.MissionManager.ListRequestCooldown`, 1400 ms by default (194-200).
- **With these met, each list fills slots 0-9 of the mission bag with bounty missions** (762-786).
  - Every slot's type is cleared first (774), so slots past 9 come back empty.
  - Nothing else in `randomizeGenericBountyMission` can leave a slot without a bounty once the novice skill is there (1078-1275).
  - Level 1 is the default. It is level 2 with `combat_bountyhunter_investigation_01`, and level 3 with `_03` (1090-1097).
  - Player bounties are possible only at level 3 (1104-1110).
- **An NPC target's start point** is `getRandomSpawnPoint` on the hunter's own planet (1201-1207, 1992-2007). At level 3 it may be on a random bounty planet.
  - So a target within 4 km is a matter of luck and may take several lists, as the scenario's comment says.

## 3. What the test should do

- **Before listing:** check the distance to the terminal, and walk again until it is under 6 m. The terminal is outdoors, 182 m from the start.
- **After each list:** treat `@radial_out_of_range_prose` (or `not_bounty_hunter_terminal`) as a refused list, not an empty one.
- **Expect** 10 bounty offers per accepted list at a bounty terminal.

## 4. Open

- Why the path stopped short of this terminal. The bot body's path log for that walk would show it.
