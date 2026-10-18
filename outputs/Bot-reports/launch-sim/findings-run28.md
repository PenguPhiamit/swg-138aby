# Findings: run28

17 Oct, 9:55 AM to 11:03 AM (68 min), 200 bots: marksman 65, brawler 59, entertainer 57, medic 10, scout 9.
Source: `botpop-launch.jsonl`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.
Compared with: run13.
Final logout left out: no boundary found (0 rows).

**4 FAIL, 2 WATCH, 6 PASS.**

## FAIL

- **Missions by role.** marksman: 11 of 115 missions succeeded (10%); 87 aborted after finding the lair (run13: 0%). Under 10%.
- **Deaths by level gap.** Killers 8 or more levels above the bot: 28 deaths (11.5% of known) (run13: 96). Worst: womp_rat (level 10, tatooine) 20; garyns_prowler (level 11, rori) 4; swamp_rat (level 10, rori) 2; highwayman (level 10, tatooine) 2. The spawn level gate should stop these.
- **Training.** 116 of 200 bots (58%) were refused a box for credits at least once (run13: 452); 267 distinct bot/box pairs; median shortfall 250.0 credits. Most refused: outdoors_scout_movement_01 59, outdoors_scout_harvest_01 47, combat_brawler_unarmed_02 36, combat_marksman_pistol_02 28, combat_marksman_support_01 22. Worst roles: scout 89%, brawler 86%, marksman 77%.
- **Routes.** 67 BotPop stats lines: 0 path lookups failed, 25,989 routes planned, 13,700 with no route (run13: 0); legs stopped instead of a straight-line fallback 20,733 (80% of routes: no start 9,505, no end 1,221, no path 0, partial 10,007, unloaded mesh 0; ends snapped 2,662).

## WATCH

- **Missions by role.** scout: 2 of 18 missions succeeded (11%); 11 aborted after finding the lair (run13: 0%). Too few missions to judge (under 20).
- **Server ticks.** 67 server rows at the full 200 bots: tick median 0.2 ms (run13: 3.8), worst 17.0 ms (run13: 2108.0), passes skipped 1 (run13: 153); RSS 4646 to 6243 MB. Ramp-up tick average peaked at 15.57 ms. Bot steps 81.3 ms of CPU per second (median; worst 112.5) (run13: 2993.8). PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.

## PASS

- **Missions by role.** brawler: 43 of 123 missions succeeded (35%); 54 aborted after finding the lair (run13: 46%).
- **Mission lairs (lair_check rows).** ranged: 112 lair attempts, 258 checks; line of sight false 0%, not attackable 0%, beyond weapon range 0%; damage never rose in 11 of 73 attempts with two or more checks (15%); median distance 6.0 m; weapons pistol_cdef 192, carbine_cdef 51, rifle_cdef 15 (run13: - never rose).
- **Mission lairs (lair_check rows).** melee: 111 lair attempts, 249 checks; line of sight false 0%, not attackable 0%, beyond weapon range 2%; damage never rose in 6 of 67 attempts with two or more checks (9%); median distance 4 m; weapons unknown_weapon 225, axe_heavy_duty 18, lance_staff_wood_s1 4, knife_survival 2 (run13: - never rose).
- **Deaths by level gap.** 244 deaths (1.084 per bot-hour (run13: 0.36)), killer level known for 244; median gap (killer minus bot) 5.0 (run13: 4). Share by gap: <= 0 4%, 1-2 7%, 3-4 32%, 5-7 46%, 8-11 11%, 12+ 0%.
- **Travel.** 0 trips attempted, 344 done (bots' own counters; server counter 343) (run13: 0). Routes: none. Teleport only: shuttles and tickets untested.
- **Server errors (core3.log).** 1,185 ERROR lines during the run, 4 kinds; 0 kinds not seen before the run started (0 lines) (run13: 2).

PASS means the number is inside the line drawn here, not that the feature was tested in game. Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.
