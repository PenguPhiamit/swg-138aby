# Findings: run18

16 Oct, 10:25 PM to 11:30 PM (65 min), 1,700 bots: marksman 450, entertainer 447, brawler 439, explorer 200, scout 84, medic 80.
Source: `botpop-launch.jsonl`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.
Compared with: run13.
Final logout left out: no boundary found (0 rows).

**4 FAIL, 2 WATCH, 6 PASS.**

## FAIL

- **Missions by role.** marksman: 8 of 515 missions succeeded (2%); 380 aborted after finding the lair (run13: 0%). Under 10%.
- **Missions by role.** scout: 4 of 100 missions succeeded (4%); 74 aborted after finding the lair (run13: 0%). Under 10%.
- **Deaths by level gap.** Killers 8 or more levels above the bot: 192 deaths (25.6% of known) (run13: 96). Worst: giant_worrt (level 13, tatooine) 43; scyk (level 12, tatooine) 18; greater_shaupaut (level 14, naboo) 18; rogue_bageraset (level 13, corellia) 15; narglatch_hunter (level 12, naboo) 12. The spawn level gate should stop these.
- **Routes.** 61 BotPop stats lines: 0 path lookups failed, 591,623 routes planned, 263,083 with no route (run13: 0); legs stopped instead of a straight-line fallback 566,008 (96% of routes: no start 42,709, no end 4,592, no path 0, partial 518,707, unloaded mesh 0; ends snapped 37,533).

## WATCH

- **Training.** 122 of 1,700 bots (7%) were refused a box for credits at least once (run13: 452); 202 distinct bot/box pairs; median shortfall 225 credits. Most refused: combat_brawler_unarmed_02 38, outdoors_scout_movement_01 33, outdoors_scout_harvest_01 25, combat_marksman_support_01 21, science_medic_injury_speed_01 16. Worst roles: scout 14%, brawler 14%, marksman 6%.
- **Server ticks.** 63 server rows at the full 1,700 bots: tick median 1.0 ms (run13: 3.8), worst 8.0 ms (run13: 2108.0), passes skipped 1 (run13: 153); RSS 5071 to 7048 MB. Ramp-up tick average peaked at 95.07 ms. Bot steps 730.4 ms of CPU per second (median; worst 1287.15) (run13: 2993.8). PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.

## PASS

- **Missions by role.** brawler: 77 of 557 missions succeeded (14%); 333 aborted after finding the lair (run13: 46%).
- **Mission lairs (lair_check rows).** ranged: 494 lair attempts, 881 checks; line of sight false 0%, not attackable 0%, beyond weapon range 0%; damage never rose in 62 of 316 attempts with two or more checks (20%); median distance 6 m; weapons rifle_cdef 451, pistol_cdef 246, carbine_cdef 184 (run13: - never rose).
- **Mission lairs (lair_check rows).** melee: 451 lair attempts, 869 checks; line of sight false 0%, not attackable 0%, beyond weapon range 94%; damage never rose in 34 of 266 attempts with two or more checks (13%); median distance 6 m; weapons unknown_weapon 783, knife_survival 64, axe_heavy_duty 17, lance_staff_wood_s1 5 (run13: - never rose).
- **Deaths by level gap.** 775 deaths (0.426 per bot-hour (run13: 0.36)), killer level known for 751; median gap (killer minus bot) 5 (run13: 4). Share by gap: <= 0 6%, 1-2 9%, 3-4 30%, 5-7 29%, 8-11 19%, 12+ 7%.
- **Travel.** 0 trips attempted, 2,891 done (bots' own counters; server counter 2,851) (run13: 0). Routes: none. Teleport only: shuttles and tickets untested.
- **Server errors (core3.log).** 806 ERROR lines during the run, 3 kinds; 0 kinds not seen before the run started (0 lines) (run13: 2).

PASS means the number is inside the line drawn here, not that the feature was tested in game. Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.
