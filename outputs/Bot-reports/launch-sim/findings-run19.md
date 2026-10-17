# Findings: run19

16 Oct, 11:32 PM to 12:31 AM (59 min), 1,700 bots: marksman 454, brawler 452, entertainer 446, explorer 200, medic 77, scout 71.
Source: `botpop-launch.jsonl`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.
Compared with: run13.
Final logout left out: no boundary found (0 rows).

**5 FAIL, 1 WATCH, 6 PASS.**

## FAIL

- **Missions by role.** marksman: 17 of 552 missions succeeded (3%); 407 aborted after finding the lair (run13: 0%). Under 10%.
- **Missions by role.** scout: 4 of 72 missions succeeded (6%); 60 aborted after finding the lair (run13: 0%). Under 10%.
- **Deaths by level gap.** Killers 8 or more levels above the bot: 18 deaths (5.0% of known) (run13: 96). Worst: garyns_prowler (level 11, rori) 6; womp_rat (level 10, tatooine) 4; swamp_rat (level 10, rori) 2; narmle_militia_grenadier (level 11, rori) 2; sentry_hermit_spider (level 10, naboo) 2. The spawn level gate should stop these.
- **Routes.** 56 BotPop stats lines: 0 path lookups failed, 487,047 routes planned, 217,009 with no route (run13: 0); legs stopped instead of a straight-line fallback 463,215 (95% of routes: no start 25,935, no end 9,397, no path 0, partial 427,883, unloaded mesh 0; ends snapped 30,386).
- **Server ticks.** 57 server rows at the full 1,700 bots: tick median 1.0 ms (run13: 3.8), worst 1148.0 ms (run13: 2108.0), passes skipped 0 (run13: 153); RSS 5117 to 7087 MB. Ramp-up tick average peaked at 106.07 ms. Bot steps 924.4 ms of CPU per second (median; worst 1977.04) (run13: 2993.8). PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.

## WATCH

- **Training.** 112 of 1,700 bots (7%) were refused a box for credits at least once (run13: 452); 181 distinct bot/box pairs; median shortfall 125 credits. Most refused: combat_brawler_unarmed_02 43, outdoors_scout_movement_01 42, combat_marksman_support_01 28, outdoors_scout_harvest_01 25, combat_marksman_carbine_02 8. Worst roles: brawler 15%, scout 14%, marksman 6%.

## PASS

- **Missions by role.** brawler: 95 of 586 missions succeeded (16%); 377 aborted after finding the lair (run13: 46%).
- **Mission lairs (lair_check rows).** ranged: 547 lair attempts, 1,022 checks; line of sight false 0%, not attackable 0%, beyond weapon range 0%; damage never rose in 84 of 391 attempts with two or more checks (21%); median distance 6.0 m; weapons rifle_cdef 584, pistol_cdef 281, carbine_cdef 157 (run13: - never rose).
- **Mission lairs (lair_check rows).** melee: 515 lair attempts, 993 checks; line of sight false 0%, not attackable 0%, beyond weapon range 95%; damage never rose in 49 of 348 attempts with two or more checks (14%); median distance 6 m; weapons unknown_weapon 882, knife_survival 81, axe_heavy_duty 22, lance_staff_wood_s1 8 (run13: - never rose).
- **Deaths by level gap.** 366 deaths (0.222 per bot-hour (run13: 0.36)), killer level known for 360; median gap (killer minus bot) 5.0 (run13: 4). Share by gap: <= 0 9%, 1-2 3%, 3-4 37%, 5-7 46%, 8-11 5%, 12+ 0%.
- **Travel.** 0 trips attempted, 2,239 done (bots' own counters; server counter 2,220) (run13: 0). Routes: none. Teleport only: shuttles and tickets untested.
- **Server errors (core3.log).** 3 ERROR lines during the run, 2 kinds; 0 kinds not seen before the run started (0 lines) (run13: 2).

PASS means the number is inside the line drawn here, not that the feature was tested in game. Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.
