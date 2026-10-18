# Local model: report-digest (draft)

Written by the local model through `tools/agents/local/local_jobs.py`; 6 input lines. A local model's draft: check each item before acting on it.

## run18

4 FAIL, 2 WATCH, 6 PASS

- FAIL: Missions by role. marksman: 8 of 515 succeeded (2%); 380 aborted after finding lair.
- FAIL: Missions by role. scout: 4 of 100 succeeded (4%); 74 aborted after finding lair.
- FAIL: Deaths by level gap. Killers 8+ levels above: 192 deaths (25.6%) vs run13: 96.
- FAIL: Routes. 591,623 planned; 263,083 with no route; legs stopped instead of fallback.
- WATCH: Training. 122 bots (7%) refused box for credits at least once (run13: 452).
- WATCH: Server ticks. 63 rows at full load; tick median 1.0 ms (run13: 3.8 ms).
- Change: 1,700
- Change: run13
- Change: 0

## run18-early

FAIL, WATCH, PASS

- FAIL: Missions by role. marksman: 0 of 370 missions succeeded (0%) (run13: 0%). Under 10%.
- FAIL: Missions by role. brawler: 13 of 359 missions succeeded (4%) (run13: 46%). Under 10%.
- FAIL: Missions by role. scout: 0 of 68 missions succeeded (0%) (run13: 0%). Under 10%.
- FAIL: Deaths by level gap. Killers 8 or more levels above the bot: 47 deaths (26.7% of known) (run13: 96). Worst: giant_worrt (level 13, tatooine) 10; scyk (level 12,
- FAIL: Routes. 10 BotPop stats lines: 0 path lookups failed, 41,473 routes planned, 16,328 with no route (run13: 0); legs stopped instead of a straight-line fallback 3
- WATCH: Training. 8 of 1,700 bots (0%) were refused a box for credits at least once (run13: 452); 13 distinct bot/box pairs; median shortfall 25 credits. Most refused: 
- Change: 47
- Change: 96
- Change: 34,000

## run19

FAIL, WATCH, PASS

- FAIL: Missions by role. marksman: 17 of 552 succeeded (3%).
- FAIL: Missions by role. scout: 4 of 72 succeeded (6%).
- FAIL: Deaths by level gap. Killers 8+ levels above: 18 deaths.
- FAIL: Routes. 487,047 routes planned; 217,009 with no route.
- FAIL: Server ticks. Worst tick 1148.0 ms; passes skipped 0.
- WATCH: Training. 112 of 1,700 bots refused a box for credits.
- Change: run13
- Change: 59 min
- Change: 1,700

## run20

3 FAIL, 2 WATCH, 7 PASS

- FAIL: marksman: 43 of 464 missions succeeded (9%); 201 aborted after finding the lair (run13: 0%). Under 10%.
- FAIL: Killers 8 or more levels above the bot: 161 deaths (16.9% of known) (run13: 96). Worst: womp_rat...
- FAIL: 27 BotPop stats lines: 0 path lookups failed, 62,494 routes planned, 33,696 with no route (run13: 0)
- WATCH: 113 of 1,700 bots (7%) were refused a box for credits at least once (run13: 452); 144 distinct bot/box pairs
- WATCH: 26 server rows at the full 1,700 bots: tick median 1.0 ms (run13: 3.8), worst 5.0 ms (run13: 2108.0)
- Change: 43
- Change: 96
- Change: 161

## run21

FAIL, WATCH, PASS

- FAIL: Missions by role. marksman: 9 of 296 missions succeeded (3%) (run13: 0%). Under 10%.
- FAIL: Missions by role. scout: 2 of 55 missions succeeded (4%) (run13: 0%). Under 10%.
- FAIL: Deaths by level gap. Killers 8 or more levels above the bot: 76 deaths (24.1% of known) (run13: 96).
- FAIL: Routes. legs stopped instead of a straight-line fallback 28,675 (61% of routes: no start 16,857, no end 1,546, no path 0, partial 10,272, unloaded mesh 0; ends 
- FAIL: Server ticks. 19 server rows at the full 1,700 bots: tick median 1.0 ms (run13: 3.8), worst 1134.0 ms (run13: 2108.0), passes skipped 1 (run13: 153); RSS 5149 t
- WATCH: Travel. No travel attempted. BotPop travel also teleports (switchZone), so shuttles and tickets stay untested either way.
- WATCH: Training. 189 of 1,700 bots (11%) were refused a box for credits at least once (run13: 452); 331 distinct bot/box pairs; median shortfall 25 credits.
- Change: 76
- Change: 28,675
- Change: 1

## run22

0 FAIL, 6 WATCH, 2 PASS

- WATCH: Missions by role: No missions taken.
- WATCH: Mission lairs: No lair_check rows found.
- WATCH: Deaths by level gap: No deaths logged.
- WATCH: Travel: No travel attempted.
- WATCH: Routes: 4 with no route; legs stopped on 5% of routes.
- WATCH: Server ticks: Worst tick 859.0 ms, passes skipped 0.
- Change: run13
- Change: 28044
- Change: 465.1

