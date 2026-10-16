# Run 8: styles, point budgets and watchdog

16 Oct 2026, 1:13 AM to 3:59 AM Pacific. Active-run checkpoint, not the finished night.

Source: the same event-log prefix as `analysis.json` and [numbers-run8.md](numbers-run8.md), read in WSL as swgemu. Run 8 is auto-discovered as `r16-0113`; the first spawn is at 1:13 AM (the board rounds it to about 1:20 AM). No server writes, bot commands or restarts. The standard report was regenerated from that fixed prefix to prevent its second live read extending the window.

Rows below group bots by their spawn `style` and `sp` labels, retaining all their later events. Explorers are separate. Boxes means train events, including novice purchases; XP column is medical XP still banked at the last snapshot, not lifetime earned. Mission outcomes use the standard tool's matching and payment accounting. Bot-hours run from each spawn to the shared endpoint, so later spawning is allowed for.

| Style | SP label | Bots | Bot-hours | Kills | Deaths | Missions taken / success / pending | Training boxes | Training paid | Latest boxes median | Medical XP median |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| hunter | 1000 | 188 | 519.9493 | 1690 | 124 | 1131 / 3 / 160 | 388 | 54700 | 2.0 | 0.0 |
| hunter | 250 | 187 | 517.1836 | 1558 | 115 | 1123 / 4 / 157 | 341 | 43175 | 2 | 0 |
| sampler | 1000 | 188 | 519.953 | 2003 | 297 | 745 / 173 / 82 | 1314 | 138250 | 7.0 | 146.5 |
| sampler | 250 | 187 | 517.1868 | 2055 | 307 | 798 / 171 / 90 | 1318 | 141875 | 7 | 130 |
| support | 1000 | 188 | 519.9421 | 0 | 3 | 0 / 0 / 0 | 617 | 154950 | 3.0 | 322.5 |
| support | 250 | 187 | 517.177 | 0 | 0 | 0 / 0 / 0 | 613 | 153425 | 3 | 335 |
| tank | 1000 | 188 | 519.9459 | 5977 | 80 | 1667 / 962 / 124 | 577 | 176450 | 3.0 | 0.0 |
| tank | 250 | 187 | 517.1802 | 6726 | 117 | 1715 / 1045 / 122 | 617 | 200175 | 4 | 0 |
| unlabeled | unlabeled | 200 | 550.0293 | 0 | 0 | 0 / 0 / 0 | 0 | 0 | 0.0 | 0.0 |

Coverage: 1700 spawn identities; 1700 with a snapshot. Logout exclusion: {'cutoff_ms': None, 'reason': None, 'excluded_rows': 0, 'excluded_mission_gone': 0, 'note': 'No despawn marker, mission_gone burst or event/host logout boundary detected; use --until-ms if the final logout is not sampled.'}.

**Point-cap caution:** `sp` is the assigned budget label, not demonstrated consumption. Latest snapshots with `sp_left` greater than their `sp` label: 748. This needs source/runtime checking before any claim that 250 versus 1,000 caps are enforced. Do not interpret different style outcomes as a controlled balance test: weapon choice, city, activity and initial skills also differ.

**Healing:** Core3 awards no medical XP for self-healing. Heal counts alone do not establish medical progression; bots should heal injured allies, and the next check should distinguish self from other and XP actually awarded. Use the researched [buying orders](../../Documentation-support/precu-player-builds.md), including XP-cap priority and skipping unaffordable boxes.

## Watchdog

Read `/var/tmp/swg-bots/watchdog.log` without changing it. Times below are Pacific on the night of 15–16 Oct; MB are the log's units.

| Time | Available MB | core3 MB |
|---|---:|---:|
| 1:20 AM | 9584 | 5924 |
| 1:30 AM | 8003 | 7491 |
| 1:40 AM | 7734 | 7763 |
| 1:50 AM | 7618 | 7895 |
| 2:00 AM | 7382 | 8110 |
| 2:10 AM | 7345 | 8130 |
| 2:20 AM | 7182 | 8306 |
| 2:30 AM | 6946 | 8443 |
| 2:40 AM | 6937 | 8449 |
| 2:50 AM | 6889 | 8502 |
| 3:00 AM | 6785 | 8599 |
| 3:10 AM | 6766 | 8591 |
| 3:20 AM | 6757 | 8635 |
| 3:30 AM | 6694 | 8688 |
| 3:40 AM | 6748 | 8683 |
| 3:50 AM | 6646 | 8759 |

Run-8 samples: 16; minimum available 6,646 MB; core3 5,924 to 8,759 MB. No threshold/despawn message appears in the captured log. The earlier 1:11 AM entry says `watchdog: core3 not running`; it precedes run 8 and does not state a cause. Sampling every ten minutes cannot exclude a shorter dip. These samples show memory growth, not its cause or a proven leak.

The earlier logged samples run from 10:50 PM (7,758 MB available, core3 7,718 MB) through 1:10 AM (6,744 / 8,606 MB). They include earlier runs and must not be fitted as run-8 growth. The 2 GB watchdog remains a safety threshold, not a forecast.
