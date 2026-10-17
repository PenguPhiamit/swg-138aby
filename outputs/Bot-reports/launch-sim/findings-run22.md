# Findings: run22

17 Oct, 2:25 AM to 2:27 AM (2 min), 500 bots: entertainer 122, brawler 122, marksman 119, explorer 100, medic 20, scout 17.
Source: `botpop-launch.jsonl`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.
Compared with: run13.
Final logout left out: 2:27 AM (28044 rows).

**0 FAIL, 6 WATCH, 2 PASS.**

## WATCH

- **Missions by role.** No missions taken.
- **Mission lairs (lair_check rows).** No lair_check rows: this run predates dev 665bea04, or no bot fought a mission lair.
- **Deaths by level gap.** No deaths logged.
- **Travel.** No travel attempted. BotPop travel also teleports (switchZone), so shuttles and tickets stay untested either way.
- **Routes.** 1 BotPop stats lines: 0 path lookups failed, 464 routes planned, 4 with no route (run13: 0); legs stopped instead of a straight-line fallback 23 (5% of routes: no start 0, no end 4, no path 0, partial 19, unloaded mesh 0; ends snapped 35).
- **Server ticks.** 1 server rows at the full 500 bots: tick median 207.5 ms (run13: 3.8), worst 859.0 ms (run13: 2108.0), passes skipped 0 (run13: 153); RSS 4917 to 4917 MB. Ramp-up tick average peaked at 207.54 ms. Bot steps 465.1 ms of CPU per second (median; worst 465.13) (run13: 2993.8). PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.

## PASS

- **Training.** 0 of 500 bots (0%) were refused a box for credits at least once (run13: 452); 0 distinct bot/box pairs; median shortfall None credits. Most refused: none. Worst roles: brawler 0%, entertainer 0%, explorer 0%.
- **Server errors (core3.log).** 547 ERROR lines during the run, 1 kinds; 0 kinds not seen before the run started (0 lines) (run13: 2).

PASS means the number is inside the line drawn here, not that the feature was tested in game. Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.
