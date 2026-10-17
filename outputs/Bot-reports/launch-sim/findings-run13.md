# Findings: run13

16 Oct, 4:02 PM to 7:15 PM (193 min), 1,700 bots: brawler 457, entertainer 454, marksman 442, explorer 200, medic 78, scout 69.
Source: `botpop-launch.jsonl.1955.old`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.
Compared with: nothing (no earlier findings file).
Final logout left out: 7:15 PM (5421 rows).

**3 FAIL, 6 WATCH, 2 PASS.**

## FAIL

- **Missions by role.** marksman: 2 of 3,087 missions succeeded (0%); 2,676 aborted after finding the lair. Under 10%.
- **Missions by role.** scout: 1 of 489 missions succeeded (0%); 434 aborted after finding the lair. Under 10%.
- **Server ticks.** 190 server rows at the full 1,700 bots: tick median 3.8 ms, worst 2108.0 ms, passes skipped 153; RSS 5161 to 8602 MB. Ramp-up tick average peaked at 262.08 ms. Bot steps 2993.8 ms of CPU per second (median; worst 4571.32). PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.

## WATCH

- **Mission lairs (lair_check rows).** No lair_check rows: this run predates dev 665bea04, or no bot fought a mission lair.
- **Deaths by level gap.** Killers 8 or more levels above the bot: 96 deaths (4.9% of known). Worst: womp_rat (level 10, tatooine) 32; vicious_squall (level 12, rori) 8; rogue_bageraset (level 13, corellia) 6; narglatch_hunter (level 12, naboo) 5; rogue_falumpaset (level 18, naboo) 4.
- **Travel.** No travel attempted. BotPop travel also teleports (switchZone), so shuttles and tickets stay untested either way.
- **Training.** 452 of 1,700 bots (27%) were refused a box for credits at least once; 985 distinct bot/box pairs; median shortfall 25.0 credits. Most refused: science_medic_injury_speed_01 166, science_medic_injury_01 136, combat_brawler_unarmed_02 114, science_medic_ability_01 112, social_entertainer_dance_02 89. Worst roles: entertainer 46%, brawler 34%, scout 22%.
- **Routes.** 191 BotPop stats lines: 0 path lookups failed (this build logs no route counts). No fallback counters in the stats line (they come with the no-fallback patch), so fallbacks are not counted.
- **Server errors (core3.log).** 851 ERROR lines during the run, 3 kinds; 2 kinds not seen before the run started (850 lines). New: 849x [ZoneClientSession <ip>] ERROR - bool engine::service::proto::BaseClient::handleNetStatusRequest(Packet *) <ip; 1x [PlayerManager] ERROR - decreaseOnlineCharCount missing account # in onlineZoneClientMap.

## PASS

- **Missions by role.** brawler: 1,946 of 4,243 missions succeeded (46%); 1,999 aborted after finding the lair.
- **Deaths by level gap.** 1,963 deaths (0.36 per bot-hour), killer level known for 1,949; median gap (killer minus bot) 4. Share by gap: <= 0 3%, 1-2 10%, 3-4 44%, 5-7 39%, 8-11 4%, 12+ 1%.

PASS means the number is inside the line drawn here, not that the feature was tested in game. Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.
