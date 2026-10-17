# Findings: run20

17 Oct, 12:33 AM to 1:00 AM (28 min), 1,700 bots: brawler 458, marksman 454, entertainer 452, explorer 200, medic 69, scout 67.
Source: `botpop-launch.jsonl`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.
Compared with: run13.
Final logout left out: no boundary found (0 rows).

**3 FAIL, 2 WATCH, 7 PASS.**

## FAIL

- **Missions by role.** marksman: 43 of 464 missions succeeded (9%); 201 aborted after finding the lair (run13: 0%). Under 10%.
- **Deaths by level gap.** Killers 8 or more levels above the bot: 161 deaths (16.9% of known) (run13: 96). Worst: womp_rat (level 10, tatooine) 106; garyns_prowler (level 11, rori) 16; swamp_rat (level 10, rori) 15; highwayman (level 10, tatooine) 8; black_sun_initiate (level 17, talus) 2. The spawn level gate should stop these.
- **Routes.** 27 BotPop stats lines: 0 path lookups failed, 62,494 routes planned, 33,696 with no route (run13: 0); legs stopped instead of a straight-line fallback 46,457 (74% of routes: no start 15,871, no end 10,109, no path 0, partial 20,477, unloaded mesh 0; ends snapped 8,485).

## WATCH

- **Training.** 113 of 1,700 bots (7%) were refused a box for credits at least once (run13: 452); 144 distinct bot/box pairs; median shortfall 25.0 credits. Most refused: combat_brawler_unarmed_02 51, combat_marksman_support_01 34, outdoors_scout_movement_01 18, combat_brawler_2handmelee_01 17, outdoors_scout_harvest_01 13. Worst roles: brawler 18%, marksman 6%, scout 3%.
- **Server ticks.** 26 server rows at the full 1,700 bots: tick median 1.0 ms (run13: 3.8), worst 5.0 ms (run13: 2108.0), passes skipped 3 (run13: 153); RSS 5162 to 7559 MB. Ramp-up tick average peaked at 99.98 ms. Bot steps 1312.3 ms of CPU per second (median; worst 2013.46) (run13: 2993.8). PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.

## PASS

- **Missions by role.** brawler: 148 of 528 missions succeeded (28%); 175 aborted after finding the lair (run13: 46%).
- **Missions by role.** scout: 8 of 68 missions succeeded (12%); 31 aborted after finding the lair (run13: 0%).
- **Mission lairs (lair_check rows).** ranged: 484 lair attempts, 1,226 checks; line of sight false 0%, not attackable 0%, beyond weapon range 0%; damage never rose in 73 of 386 attempts with two or more checks (19%); median distance 6.0 m; weapons pistol_cdef 574, rifle_cdef 450, carbine_cdef 202 (run13: - never rose).
- **Mission lairs (lair_check rows).** melee: 470 lair attempts, 1,166 checks; line of sight false 0%, not attackable 0%, beyond weapon range 2%; damage never rose in 21 of 330 attempts with two or more checks (6%); median distance 4.0 m; weapons unknown_weapon 975, knife_survival 95, axe_heavy_duty 76, lance_staff_wood_s1 20 (run13: - never rose).
- **Deaths by level gap.** 952 deaths (1.25 per bot-hour (run13: 0.36)), killer level known for 952; median gap (killer minus bot) 5.0 (run13: 4). Share by gap: <= 0 1%, 1-2 7%, 3-4 26%, 5-7 49%, 8-11 16%, 12+ 1%.
- **Travel.** 0 trips attempted, 190 done (bots' own counters; server counter 186) (run13: 0). Routes: none. Teleport only: shuttles and tickets untested.
- **Server errors (core3.log).** 1 ERROR lines during the run, 1 kinds; 0 kinds not seen before the run started (0 lines) (run13: 2).

PASS means the number is inside the line drawn here, not that the feature was tested in game. Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.
