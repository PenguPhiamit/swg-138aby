# Findings: run27

17 Oct, 7:37 AM to 9:53 AM (136 min), 200 bots: brawler 63, entertainer 58, marksman 56, scout 13, medic 10.
Source: `botpop-launch.jsonl`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.
Compared with: run13.
Final logout left out: no boundary found (0 rows).

**4 FAIL, 1 WATCH, 7 PASS.**

## FAIL

- **Deaths by level gap.** Killers 8 or more levels above the bot: 50 deaths (10.9% of known) (run13: 96). Worst: garyns_prowler (level 11, rori) 15; swamp_rat (level 10, rori) 10; womp_rat (level 10, tatooine) 7; black_sun_initiate (level 17, talus) 4; black_sun_smuggler (level 19, talus) 3. The spawn level gate should stop these.
- **Training.** 172 of 200 bots (86%) were refused a box for credits at least once (run13: 452); 424 distinct bot/box pairs; median shortfall 250.0 credits. Most refused: outdoors_scout_movement_01 74, social_entertainer_dance_02 53, outdoors_scout_harvest_01 52, combat_marksman_pistol_02 39, combat_brawler_unarmed_02 30. Worst roles: marksman 93%, entertainer 91%, brawler 83%.
- **Routes.** 135 BotPop stats lines: 0 path lookups failed, 93,256 routes planned, 64,283 with no route (run13: 0); legs stopped instead of a straight-line fallback 85,232 (91% of routes: no start 53,046, no end 1,237, no path 0, partial 30,949, unloaded mesh 0; ends snapped 9,180).
- **Server ticks.** 135 server rows at the full 200 bots: tick median 0.2 ms (run13: 3.8), worst 7365.0 ms (run13: 2108.0), passes skipped 14 (run13: 153); RSS 4618 to 6285 MB. Ramp-up tick average peaked at 142.51 ms. Bot steps 93.5 ms of CPU per second (median; worst 394.06) (run13: 2993.8). PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.

## WATCH

- **Server errors (core3.log).** 5,213 ERROR lines during the run, 4 kinds; 1 kinds not seen before the run started (1 lines) (run13: 2). New: 1x [ZoneClientSession <ip>] ERROR - bool engine::service::proto::BaseClient::handleNetStatusReques.

## PASS

- **Missions by role.** brawler: 121 of 269 missions succeeded (45%); 93 aborted after finding the lair (run13: 46%).
- **Missions by role.** marksman: 22 of 173 missions succeeded (13%); 122 aborted after finding the lair (run13: 0%).
- **Missions by role.** scout: 7 of 36 missions succeeded (19%); 28 aborted after finding the lair (run13: 0%).
- **Mission lairs (lair_check rows).** ranged: 192 lair attempts, 430 checks; line of sight false 0%, not attackable 0%, beyond weapon range 0%; damage never rose in 22 of 134 attempts with two or more checks (16%); median distance 6.0 m; weapons pistol_cdef 303, carbine_cdef 95, rifle_cdef 31, unknown_weapon 1 (run13: - never rose).
- **Mission lairs (lair_check rows).** melee: 234 lair attempts, 536 checks; line of sight false 0%, not attackable 0%, beyond weapon range 0%; damage never rose in 6 of 158 attempts with two or more checks (4%); median distance 4.0 m; weapons unknown_weapon 444, lance_staff_wood_s1 46, knife_survival 28, axe_heavy_duty 18 (run13: - never rose).
- **Deaths by level gap.** 458 deaths (1.013 per bot-hour (run13: 0.36)), killer level known for 458; median gap (killer minus bot) 5.0 (run13: 4). Share by gap: <= 0 5%, 1-2 10%, 3-4 29%, 5-7 44%, 8-11 8%, 12+ 3%.
- **Travel.** 0 trips attempted, 762 done (bots' own counters; server counter 761) (run13: 0). Routes: none. Teleport only: shuttles and tickets untested.

PASS means the number is inside the line drawn here, not that the feature was tested in game. Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.
