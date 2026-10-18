# Findings: run29

17 Oct, 11:05 AM to 1:15 PM (130 min), 600 bots: entertainer 189, marksman 185, brawler 171, scout 29, medic 26.
Source: `botpop-launch.jsonl`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.
Compared with: run13.
Final logout left out: no boundary found (0 rows).

**3 FAIL, 2 WATCH, 7 PASS.**

## FAIL

- **Deaths by level gap.** Killers 8 or more levels above the bot: 195 deaths (23.2% of known) (run13: 96). Worst: womp_rat (level 10, tatooine) 118; highwayman (level 10, tatooine) 30; garyns_prowler (level 11, rori) 16; swamp_rat (level 10, rori) 13; scyk (level 12, tatooine) 6. The spawn level gate should stop these.
- **Routes.** 130 BotPop stats lines: 0 path lookups failed, 78,675 routes planned, 44,778 with no route (run13: 0); legs stopped instead of a straight-line fallback 63,292 (80% of routes: no start 31,225, no end 4,724, no path 0, partial 27,343, unloaded mesh 0; ends snapped 6,953).
- **Server ticks.** 42 server rows at the full 600 bots: tick median 0.6 ms (run13: 3.8), worst 154.0 ms (run13: 2108.0), passes skipped 13 (run13: 153); RSS 6359 to 6748 MB. Ramp-up tick average peaked at 40.71 ms. Bot steps 91.8 ms of CPU per second (median; worst 1629.86) (run13: 2993.8). PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.

## WATCH

- **Deaths by level gap.** 840 deaths (1.176 per bot-hour (run13: 0.36)), killer level known for 840; median gap (killer minus bot) 6.0 (run13: 4). Share by gap: <= 0 5%, 1-2 9%, 3-4 21%, 5-7 42%, 8-11 23%, 12+ 0%.
- **Training.** 263 of 600 bots (44%) were refused a box for credits at least once (run13: 452); 599 distinct bot/box pairs; median shortfall 250 credits. Most refused: outdoors_scout_movement_01 104, outdoors_scout_harvest_01 70, combat_marksman_support_01 61, combat_brawler_unarmed_02 57, social_entertainer_dance_02 56. Worst roles: marksman 59%, brawler 48%, scout 34%.

## PASS

- **Missions by role.** brawler: 193 of 441 missions succeeded (44%); 155 aborted after finding the lair (run13: 46%).
- **Missions by role.** marksman: 65 of 400 missions succeeded (16%); 269 aborted after finding the lair (run13: 0%).
- **Missions by role.** scout: 16 of 64 missions succeeded (25%); 35 aborted after finding the lair (run13: 0%).
- **Mission lairs (lair_check rows).** ranged: 415 lair attempts, 963 checks; line of sight false 0%, not attackable 0%, beyond weapon range 0%; damage never rose in 36 of 293 attempts with two or more checks (12%); median distance 6 m; weapons pistol_cdef 608, carbine_cdef 209, rifle_cdef 138, lance_staff_wood_s1 4, unknown_weapon 4 (run13: - never rose).
- **Mission lairs (lair_check rows).** melee: 388 lair attempts, 834 checks; line of sight false 0%, not attackable 0%, beyond weapon range 0%; damage never rose in 17 of 256 attempts with two or more checks (7%); median distance 4.0 m; weapons unknown_weapon 750, axe_heavy_duty 42, knife_survival 23, lance_staff_wood_s1 19 (run13: - never rose).
- **Travel.** 0 trips attempted, 1,112 done (bots' own counters; server counter 1,113) (run13: 0). Routes: none. Teleport only: shuttles and tickets untested.
- **Server errors (core3.log).** 14,570 ERROR lines during the run, 1 kinds; 0 kinds not seen before the run started (0 lines) (run13: 2).

PASS means the number is inside the line drawn here, not that the feature was tested in game. Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.
