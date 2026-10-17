# Findings: run18-early

16 Oct, 10:25 PM to 10:39 PM (14 min), 1,700 bots: marksman 450, entertainer 447, brawler 439, explorer 200, scout 84, medic 80.
Source: `botpop-launch.jsonl`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.
Compared with: run13.
Final logout left out: no boundary found (0 rows).

**5 FAIL, 1 WATCH, 6 PASS.**

## FAIL

- **Missions by role.** marksman: 0 of 370 missions succeeded (0%) (run13: 0%). Under 10%.
- **Missions by role.** brawler: 13 of 359 missions succeeded (4%) (run13: 46%). Under 10%.
- **Missions by role.** scout: 0 of 68 missions succeeded (0%) (run13: 0%). Under 10%.
- **Deaths by level gap.** Killers 8 or more levels above the bot: 47 deaths (26.7% of known) (run13: 96). Worst: giant_worrt (level 13, tatooine) 10; scyk (level 12, tatooine) 5; greater_shaupaut (level 14, naboo) 5; greater_desert_womp_rat (level 22, tatooine) 4; rogue_bageraset (level 13, corellia) 4. The spawn level gate should stop these.
- **Routes.** 10 BotPop stats lines: 0 path lookups failed, 41,473 routes planned, 16,328 with no route (run13: 0); legs stopped instead of a straight-line fallback 34,000 (82% of routes: no start 2,252, no end 799, no path 0, partial 30,949, unloaded mesh 0; ends snapped 3,341).

## WATCH

- **Training.** 8 of 1,700 bots (0%) were refused a box for credits at least once (run13: 452); 13 distinct bot/box pairs; median shortfall 25 credits. Most refused: combat_marksman_support_01 4, outdoors_scout_movement_01 3, combat_brawler_2handmelee_01 2, combat_marksman_carbine_01 2, outdoors_scout_harvest_01 2. Worst roles: brawler 1%, marksman 1%, entertainer 0%.

## PASS

- **Mission lairs (lair_check rows).** ranged: 259 lair attempts, 261 checks; line of sight false 0%, not attackable 0%, beyond weapon range 0%; damage never rose in 0 of 2 attempts with two or more checks (0%); median distance 6 m; weapons rifle_cdef 169, pistol_cdef 54, carbine_cdef 38 (run13: - never rose).
- **Mission lairs (lair_check rows).** melee: 226 lair attempts, 233 checks; line of sight false 0%, not attackable 0%, beyond weapon range 96%; damage never rose in 2 of 5 attempts with two or more checks (40%); median distance 6 m; weapons unknown_weapon 217, knife_survival 14, axe_heavy_duty 2 (run13: - never rose).
- **Deaths by level gap.** 185 deaths (0.495 per bot-hour (run13: 0.36)), killer level known for 176; median gap (killer minus bot) 5.0 (run13: 4). Share by gap: <= 0 2%, 1-2 9%, 3-4 26%, 5-7 36%, 8-11 19%, 12+ 7%.
- **Travel.** 0 trips attempted, 72 done (bots' own counters; server counter 72) (run13: 0). Routes: none. Teleport only: shuttles and tickets untested.
- **Server errors (core3.log).** 1 ERROR lines during the run, 1 kinds; 0 kinds not seen before the run started (0 lines) (run13: 2).
- **Server ticks.** 12 server rows at the full 1,700 bots: tick median 1.0 ms (run13: 3.8), worst 4.0 ms (run13: 2108.0), passes skipped 0 (run13: 153); RSS 5071 to 6825 MB. Ramp-up tick average peaked at 95.07 ms. Bot steps 720.6 ms of CPU per second (median; worst 1103.17) (run13: 2993.8). PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.

PASS means the number is inside the line drawn here, not that the feature was tested in game. Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.
