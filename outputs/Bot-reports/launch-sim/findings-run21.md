# Findings: run21

17 Oct, 1:02 AM to 1:22 AM (20 min), 1,700 bots: entertainer 460, brawler 449, marksman 447, explorer 200, scout 80, medic 64.
Source: `botpop-launch.jsonl`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.
Compared with: run13.
Final logout left out: no boundary found (0 rows).

**5 FAIL, 2 WATCH, 5 PASS.**

## FAIL

- **Missions by role.** marksman: 9 of 296 missions succeeded (3%) (run13: 0%). Under 10%.
- **Missions by role.** scout: 2 of 55 missions succeeded (4%) (run13: 0%). Under 10%.
- **Deaths by level gap.** Killers 8 or more levels above the bot: 76 deaths (24.1% of known) (run13: 96). Worst: womp_rat (level 10, tatooine) 60; swamp_rat (level 10, rori) 6; garyns_prowler (level 11, rori) 6; highwayman (level 10, tatooine) 4. The spawn level gate should stop these.
- **Routes.** 20 BotPop stats lines: 0 path lookups failed, 46,840 routes planned, 22,674 with no route (run13: 0); legs stopped instead of a straight-line fallback 28,675 (61% of routes: no start 16,857, no end 1,546, no path 0, partial 10,272, unloaded mesh 0; ends snapped 5,974).
- **Server ticks.** 19 server rows at the full 1,700 bots: tick median 1.0 ms (run13: 3.8), worst 1134.0 ms (run13: 2108.0), passes skipped 1 (run13: 153); RSS 5149 to 7338 MB. Ramp-up tick average peaked at 95.95 ms. Bot steps 1131.9 ms of CPU per second (median; worst 2014.47) (run13: 2993.8). PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.

## WATCH

- **Travel.** No travel attempted. BotPop travel also teleports (switchZone), so shuttles and tickets stay untested either way.
- **Training.** 189 of 1,700 bots (11%) were refused a box for credits at least once (run13: 452); 331 distinct bot/box pairs; median shortfall 25 credits. Most refused: outdoors_scout_movement_01 83, combat_brawler_unarmed_02 82, outdoors_scout_harvest_01 58, combat_marksman_support_01 37, combat_brawler_2handmelee_01 20. Worst roles: brawler 25%, marksman 15%, scout 12%.

## PASS

- **Missions by role.** brawler: 65 of 328 missions succeeded (20%) (run13: 46%).
- **Mission lairs (lair_check rows).** ranged: 255 lair attempts, 395 checks; line of sight false 0%, not attackable 0%, beyond weapon range 0%; damage never rose in 27 of 113 attempts with two or more checks (24%); median distance 6 m; weapons pistol_cdef 173, rifle_cdef 170, carbine_cdef 52 (run13: - never rose).
- **Mission lairs (lair_check rows).** melee: 235 lair attempts, 389 checks; line of sight false 0%, not attackable 0%, beyond weapon range 1%; damage never rose in 6 of 103 attempts with two or more checks (6%); median distance 4 m; weapons unknown_weapon 345, knife_survival 29, axe_heavy_duty 15 (run13: - never rose).
- **Deaths by level gap.** 315 deaths (0.574 per bot-hour (run13: 0.36)), killer level known for 315; median gap (killer minus bot) 5 (run13: 4). Share by gap: <= 0 5%, 1-2 15%, 3-4 30%, 5-7 27%, 8-11 24%, 12+ 0%.
- **Server errors (core3.log).** 1 ERROR lines during the run, 1 kinds; 0 kinds not seen before the run started (0 lines) (run13: 2).

PASS means the number is inside the line drawn here, not that the feature was tested in game. Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.
