# Pacing review: how long to master a profession on this server

15 Oct 2026, Claude (Sonnet). Source: the launch simulation's event logs (`/opt/swg/agent/logs/botpop-launch-run2.jsonl`, `-run3.jsonl`), the client skill tree (`datatables/skill/skills.iff`) and Core3's XP code and config. Nothing under `/opt/swg` was written; the skill table was extracted to a temporary folder outside the repo.

Labels used below: **[M]** measured in the simulation, **[C]** read from the game data, config or source, **[E]** my estimate (assumptions stated), **[?]** not known.

## Summary

1. **XP multiplier [C].** Regular XP is **5.0x**: `globalExpMultiplier = 5.0` in `scripts/managers/player_manager.lua` (stock Core3 is 1.0, per `Documentation-support/tracked-source-changes.patch`). `config.lua` and `config-local.lua` have no regular-XP key; `config-local.lua` only sets `Core3.Sandbox.JediXpMultiplier = 2.0`, `SkillPoints = 1000` and `TrainingCostMultiplier = 0.25`. The bots' rates below already include the 5x.
2. **Measured rates [M], run 3, per bot-hour online (spent + unspent XP):**

   | Role | Main XP | XP per hour |
   |---|---|---|
   | Entertainer | dance | 7,097 |
   | Medic | medical | 3,561 (with a busy town; 484 in run 2's thin crowd) |
   | Brawler | own weapon line, while wielded | unarmed about 11,100; one-hand about 3,200; two-hand about 2,200; polearm about 1,600 |
   | Marksman | own weapon line, while wielded | pistol about 2,700; carbine about 2,100; rifle about 2,000 |
   | Scout | scout | 769 |

3. **Hours to master [E].**

   | Profession | Hours | Remaining gap |
   |---|---|---|
   | Brawler | 108-134 at the bots' constant rates; about 16-20 if the player moves up to higher-level creatures | none |
   | Marksman | 110-139 constant; about 16-20 level-scaled | none |
   | Medic | 26-30 for medical XP with a busy hub; 160-190 with thin demand | crafting tree not measured |
   | Entertainer | about 19 for dance and music (music assumed equal to dance) | image design and healing not measured |
   | Scout | 81-98 for scout XP (41-49 level-scaled) | trapping and camp not measured |

4. **Bottleneck boxes the bots could not earn [M]:** scout trapping (`outdoors_scout_tools_*`) and camp (`outdoors_scout_camp_*`), medic crafting (`science_medic_crafting_*`), entertainer image design (`social_entertainer_hairstyle_*`), entertainer healing (`social_entertainer_healing_*`) and entertainer music (`social_entertainer_music_*`; the bots simply never play an instrument). Brawler and marksman have no blocked box.
5. **No casual-player timeline exists in the project docs.** What the docs do confirm is the XP-to-master figures for Entertainer (they match the table exactly). Section 6 gives the multiplier arithmetic and what to measure before changing anything.

## 1. Method

- **Earned XP = unspent XP in the snapshot + XP spent on boxes so far** (the `train` rows' `xp_cost`, matched by timestamp). The earlier `numbers-run3.md` table counts unspent XP only, which hides everything already spent (for example brawler unarmed: 369 an hour unspent against 2,817 earned; dance 2,373 against 7,097; medical 778 against 3,561).
- **Time.** All 1,500 bots spawned within 0.01 min of the launch in run 3 (0.12 min in run 2), so `min` is minutes since launch for every bot. Run 3 gave each bot about 1.28 h (75-78 min); run 2 about 2.73 h.
- **Rates are per bot-hour online**, including walking, resting and waiting. Brawlers and marksmen spent 44% of the time fighting, scouts 28%, medics 88% idle (waiting for patients), entertainers 98% dancing [M].
- **Weapon lines** (brawler, marksman) were measured two ways: per hour online, and per hour with that weapon in hand (snapshot intervals where the weapon did not change). The bots hold the weapon of the cheapest open box, so a line's per-online-hour figure depends on how long the bot stayed on it.
- **Run 2 is a cross-check, not the source.** Its bots trained only first-tier boxes, so unspent XP reached the 10,000 cap of the first-tier box (dance after about 80 min, unarmed, pistol, medical) and the later windows under-count.

## 2. Experience earned per hour (measured)

### 2.1 By role and type, run 3 (78 min, spent + unspent)

| Role | XP type | Pooled per bot-hour | Median bot | 10th-90th percentile | Bots earning it |
|---|---|---|---|---|---|
| Brawler (292) | combat_meleespecialize_unarmed | 2,817 | 1,514 | 885-5,254 | 292 |
| | combat_meleespecialize_onehand | 1,651 | 1,015 | 805-4,238 | 286 |
| | combat_meleespecialize_twohand | 876 | 885 | 0-1,150 | 262 |
| | combat_meleespecialize_polearm | 519 | 697 | 0-954 | 205 |
| | combat_general | 580 | 393 | 217-1,092 | 292 |
| Marksman (274) | combat_rangedspecialize_pistol | 2,311 | 2,428 | 1,059-3,113 | 273 |
| | combat_rangedspecialize_rifle | 383 | 124 | 0-920 | 145 |
| | combat_rangedspecialize_carbine | 247 | 0 | 0-903 | 90 |
| | combat_general | 289 | 264 | 104-508 | 273 |
| Scout (285) | scout | 769 | 631 | 94-1,664 | 260 |
| | combat_general | 190 | 192 | 0-379 | 242 |
| | trapping, camp | 0 | 0 | 0 | 0 |
| Medic (339) | medical | 3,561 | 3,145 | 1,008-5,590 | 339 |
| | crafting_medicine_general, combat_general | 0 | 0 | 0 | 0 |
| Entertainer (310) | dance | 7,097 | 7,053 | 7,005-7,400 | 308 |
| | music, imagedesigner, entertainer_healing | 0 | 0 | 0 | 0 |

The weapon-line medians are low for lines the bot only visited late (rifle, carbine, polearm), because the median counts bots that never wielded that weapon. The per-weapon table below is the one to use for line speed.

### 2.2 Weapon lines, per hour with the weapon in hand (run 3)

| Line | Pooled XP per hour wielded | Median bot (10th-90th percentile) | Kills per hour wielded | Hours observed |
|---|---|---|---|---|
| Brawler unarmed | 12,680 | 11,135 (1,293-17,789) | 34 | 54 |
| Brawler one-hand | 3,882 | 3,181 (734-9,587) | 20 | 133 |
| Brawler two-hand | 3,120 | 2,185 (671-4,707) | 17 | 79 |
| Brawler polearm | 1,874 | 1,631 (0-3,248) | 15 | 85 |
| Marksman pistol | 2,724 | 2,694 (1,068-5,816) | 18 | 279 |
| Marksman carbine | 3,131 | 2,068 (938-3,320) | 22 | 21 |
| Marksman rifle | 2,552 | 1,961 (498-3,214) | 19 | 41 |

- **Unarmed is 3-5x faster than any weapon line.** This is the same effect as `FINDINGS.md` section 2 (18 s a kill against 32-43 s). It looks like an unarmed damage outlier worth a balance look; it makes the brawler's first line almost free.
- **combat_general is 10% of the combat XP [C, confirmed by M].** `PlayerManagerImplementation.cpp:2186` awards it at `localMultiplier 0.1`; measured ratio to the wielded line is 9.8-10.0% for the three marksman weapons.
- **Per-kill XP [M/C].** A target's template `baseXp` times the damage share, times 5 (capped at player level x 300 before the multiplier). Median weapon XP per kill by target level in run 3 (brawlers): level 3 about 145, level 5 about 220, level 6 about 265, level 7 about 245 (marksmen 125-215). That is 35-50% of 5x the template value (level 5 dwarf nuna: 85 x 5 = 425; level 6 gorg: 113 x 5 = 565), because about 83 bots share each city's creatures.
- **Windows (run 3), pooled XP per hour.** Dance 7,071 / 7,108 / 7,113 (0-25 / 25-50 / 50-80 min), flat. Scout 720 / 864 / 727, flat. Medical 2,936 / 3,969 / 3,786. Brawler unarmed 3,499 / 2,392 / 2,556 and marksman pistol 3,153 / 2,136 / 1,657 fall as the bots' nearest creatures thin out.

### 2.3 Run 2 cross-check (first 80 min, before the caps bite)

| Role / type | Run 2 | Run 3 |
|---|---|---|
| Entertainer dance | 7,017 / 7,036 / 7,046 | 7,071 / 7,108 / 7,113 |
| Scout scout | 659 / 704 / 683 | 720 / 864 / 727 |
| Brawler unarmed | 3,636 / 3,675 / 3,577 | 3,499 / 2,392 / 2,556 |
| Marksman pistol | 3,196 / 2,191 / 1,275 | 3,153 / 2,136 / 1,657 |
| Medic medical | 447 / 377 / 430 | 2,936 / 3,969 / 3,786 |

All rows reproduce except the medic. The medic difference is the town hub: heals per medic-hour were 111 in run 3 against about 15 in run 2, at about 32 XP per heal. **A medic's XP is set by how many hurt players reach them, not by the medic.**

### 2.4 What the numbers mean for each role

- **Dance XP is independent of the crowd** in this range (same in the thin-crowd run 2 and the busy run 3). Core3 awards `(flourishXp + performance base XP) x (1 + audience/50 + applause/100 + group bonus)` per tick, and the bots flourish every 6-10 s [C]. A player who flourishes rarely would earn less; one with a 50-person audience up to twice as much.
- **Scout XP comes from `harvestcorpse` only** (XP = creature level x 5 + 19, then x5, per successful harvest) [C]. Measured: 57.6 XP per harvest command the bot issued. A level-4 target should pay about 195 per harvest, so only about 1 command in 3-4 paid. The bot picks one of three harvest types at random, so most commands hit a type the corpse lacks (inferred, not checked). **A human who picks the right type could earn about 3-4x the measured scout rate.**
- **Scouts hunt slowly**: 12.4 kills an hour against 17.6 (brawler) and 16.3 (marksman), and died most often (1.9 an hour against 1.1-1.5). Deaths cost time only; XP is not lost.

## 3. The skill trees (client `skills.iff`) and the XP settings

### 3.1 Config [C]

| Setting | Value | Where |
|---|---|---|
| `globalExpMultiplier` | **5.0** (stock 1.0) | `scripts/managers/player_manager.lua` line 60: same in `/opt/swg/Core3`, `Core3-dev` and `testgalaxy` |
| `groupExpMultiplier` | 1.2 (the bots never group) | same file, line 57 |
| `Core3.Sandbox.JediXpMultiplier` | 2.0, applies to `jedi_general` only | `config-local.lua`, live and test |
| `Core3.Sandbox.SkillPoints` | 1,000 (a profession costs 77 points, so 12 professions fit) | `config-local.lua` |
| `Core3.Sandbox.TrainingCostMultiplier` | 0.25 on credits, not on XP | `config-local.lua`, `Skill.h:315` |
| Regular-XP keys in `config.lua` / `config-local.lua` | none | both files |

`awardExperience` multiplies a positive amount by species modifier x food buff x local multiplier x `globalExpMultiplier` (`PlayerManagerImplementation.cpp:2631`). The bots' species were random, so the measured rates include an average species mix. The multiplier can be changed live with `/server playermanager setxpmodifier <value>` (admin; it lasts until restart) [C].

### 3.2 Boxes: XP cost per tier (I / II / III / IV), the XP type, and its total

Source: `datatables/skill/skills.iff`. The five professions' rows are identical in the base archives and in the test galaxy's `local_planets.tre`, which adds only a Botanist profession and the Chiss species. Master boxes cost no XP.

**Brawler** (master needs `unarmed_04`, `1handmelee_04`, `2handmelee_04`, `polearm_04`)

| Tree | XP type | I | II | III | IV | Total | XP caps while owning I / II / III / IV |
|---|---|---|---|---|---|---|---|
| unarmed | combat_meleespecialize_unarmed | 1,000 | 5,000 | 15,000 | 70,000 | 91,000 | 10k / 30k / 140k / 200k |
| 1handmelee | combat_meleespecialize_onehand | 1,000 | 5,000 | 15,000 | 70,000 | 91,000 | same |
| 2handmelee | combat_meleespecialize_twohand | 1,000 | 5,000 | 15,000 | 70,000 | 91,000 | same |
| polearm | combat_meleespecialize_polearm | 1,000 | 5,000 | 15,000 | 70,000 | 91,000 | same |
| | | | | | | **364,000** | |

**Marksman** (master needs `rifle_04`, `pistol_04`, `carbine_04`, `support_04`)

| Tree | XP type | I | II | III | IV | Total | Caps |
|---|---|---|---|---|---|---|---|
| rifle | combat_rangedspecialize_rifle | 1,000 | 5,000 | 15,000 | 70,000 | 91,000 | 10k / 30k / 140k / 200k |
| pistol | combat_rangedspecialize_pistol | 1,000 | 5,000 | 15,000 | 70,000 | 91,000 | same |
| carbine | combat_rangedspecialize_carbine | 1,000 | 5,000 | 15,000 | 70,000 | 91,000 | same |
| support | **combat_general** | 300 | 2,250 | 6,000 | 22,000 | 30,550 | 170k |
| | | | | | | **303,550** | |

**Scout** (master needs `movement_04`, `tools_04`, `harvest_04`, `camp_04`)

| Tree | XP type | I | II | III | IV | Total | Caps |
|---|---|---|---|---|---|---|---|
| movement | scout | 1,000 | 5,000 | 10,000 | 15,000 | 31,000 | 10k / 20k / 30k / 30k |
| harvest | scout | 1,000 | 5,000 | 10,000 | 15,000 | 31,000 | same |
| tools | **trapping** | 1,000 | 5,000 | 10,000 | 15,000 | 31,000 | same |
| camp | **camp** | 1,000 | 5,000 | 10,000 | 20,000 | 36,000 | 10k / 20k / 40k / 40k |
| | | | | | | **129,000** (scout XP 62,000) | |

**Medic** (master needs `injury_04`, `injury_speed_04`, `ability_04`, `crafting_04`)

| Tree | XP type | I | II | III | IV | Total | Caps |
|---|---|---|---|---|---|---|---|
| injury | medical | 1,000 | 5,000 | 10,000 | 15,000 | 31,000 | 10k / 20k / 30k / 30k |
| injury_speed | medical | 1,000 | 5,000 | 10,000 | 15,000 | 31,000 | same |
| ability | medical | 1,000 | 5,000 | 10,000 | 15,000 | 31,000 | same |
| crafting | **crafting_medicine_general** | 500 | 1,000 | 3,000 | 6,000 | 10,500 | 2k / 6k / 12k / 17.5k |
| | | | | | | **103,500** (medical XP 93,000) | |

**Entertainer** (master needs `hairstyle_04`, `music_04`, `dance_04`, `healing_04`)

| Tree | XP type | I | II | III | IV | Total | Caps |
|---|---|---|---|---|---|---|---|
| hairstyle (image design) | **imagedesigner** | 1,000 | 5,000 | 10,000 | 15,000 | 31,000 | 10k / 20k / 30k / 30k |
| music | **music** | 1,000 | 5,000 | 15,000 | 45,000 | 66,000 | 10k / 30k / 90k / 150k |
| dance | dance | 1,000 | 5,000 | 15,000 | 45,000 | 66,000 | same |
| healing | **entertainer_healing** | 1,000 | 5,000 | 10,000 | 25,000 | 41,000 | 10k / 20k / 50k / 75k |
| | | | | | | **204,000** | |

(The Entertainer figures match `Systems-baseline/precu-reference.md` line 285: 66k dancing, 66k musicianship, 41k entertainer, 31k image design.)

Bold types are the ones the bots never earned. Other fixed costs, per profession [C]:
- Skill points 77 (novice 15, tiers 2 / 3 / 4 / 5 each, master 6).
- Credits: 45,100 in the client table, 11,275 at the sandbox's x0.25 (novice 25, each tier 250 / 500 / 750 / 1,000 per tree, master 1,250). New characters are documented to start with 10,000 cash and 100,000 bank (`SWG-project-record.md` line 79; not checked here), so credits do not gate the first profession, but they do gate a second one for a character without income. The simulation did not charge credits.
- A type with no owned box has a default XP cap of mostly 2,000 (`xp_limits.iff`; combat_general 170,000, crafting_medicine_general 1,000). XP above the cap is lost, so a player has to spend as they go. Run 2 shows it happening.

## 4. Hours to master

Two scenarios, both from the measured run 3 rates. Neither is a prediction.

- **A, constant bot rate [E].** The rate measured at level 5-7 targets holds for every tier. This is an upper bound for combat, because the bots hunted creatures of level 5.4 on average and never got past tier 2.
- **B, level-scaled [E].** Combat XP per kill follows the creature's template `baseXp`, which grows steeply with level (median raw `baseXp`: level 6 = 113, level 10 = 356, level 14 = 714, level 18 = 1,257, level 22 = 2,006; read from the mobile templates). Assumptions: the player hunts level 10 / 14 / 18 creatures for tiers II / III / IV (level about 5 for tier I, as measured); each level adds 4.5 s to the kill (the measured slope); the loop overhead (about 18 kills an hour) and the damage-share loss (35-50% of the full XP) stay as measured. Rate multipliers: 1.0 / 2.9 / 5.5 / 8.9 for tiers I-IV. This is optimistic: a higher-level hunter also dies more and needs better gear.

Rates used: the median bot (first number) and the pooled value (in brackets).

### 4.1 Brawler and marksman: every box is earnable

| Line | Rate used (XP per h) | A: hours | B: hours |
|---|---|---|---|
| Brawler unarmed | 11,135 (12,680) | 8.2 (7.2) | 1.2 (1.0) |
| Brawler one-hand | 3,181 (3,882) | 28.6 (23.4) | 4.2 (3.4) |
| Brawler two-hand | 2,185 (3,120) | 41.6 (29.2) | 6.1 (4.3) |
| Brawler polearm | 1,631 (1,874) | 55.8 (48.6) | 8.2 (7.1) |
| **Brawler total** | | **134 (108)** | **20 (16)** |
| Marksman pistol | 2,694 (2,724) | 33.8 (33.4) | 4.9 (4.9) |
| Marksman carbine | 2,068 (3,131) | 44.0 (29.1) | 6.4 (4.2) |
| Marksman rifle | 1,961 (2,552) | 46.4 (35.7) | 6.8 (5.2) |
| Marksman support (combat_general) | 10% of the weapon XP: 27,300 of the 30,550 needed arrives by itself; the rest is 32,500 more weapon-XP of hunting | +14 (+12) | +2 |
| **Marksman total** | | **139 (110)** | **20 (16)** |

At 7 hours a week (a casual player), scenario A is 15-20 weeks and B is 2-3 weeks; at 20 hours a week, 5-7 weeks and about 1 week.

### 4.2 Medic, entertainer, scout: the rate is set by the activity, not the level

| Profession / XP type | Needed | Rate | Hours |
|---|---|---|---|
| Medic, medical | 93,000 | **[M]** 3,561 (median 3,145) in run 3 with a busy hub | 26-30 |
| Medic, medical | 93,000 | **[M]** 484 (median earner 583) in run 2 with a thin crowd | 160-192 |
| Medic, crafting_medicine_general | 10,500 | **[E]** about 400 XP per craft (median medicine schematic: 80 raw x 5), so about 26 crafts | a few hours; not measured |
| Entertainer, dance | 66,000 | **[M]** 7,053-7,097 | 9.3-9.4 |
| Entertainer, music | 66,000 | **[E]** same function and flourish rate as dance | about 9.4 |
| Entertainer, imagedesigner | 31,000 | **[E]** per session: 500 (cosmetic) / 1,500 (body) / 10,000 (stat migration, per the pre-CU reference); half on yourself | about 62 cosmetic sessions on another player; not measured |
| Entertainer, entertainer_healing | 41,000 | **[?]** comes from buffs and wound or battle-fatigue healing of patrons; bots earned 0 | unknown |
| Scout, scout (movement + harvest) | 62,000 | **[M]** 769 pooled (631 median) | 81-98; level-scaled **[E]** 41-49; **[E]** about 3-4x faster again if every harvest command paid |
| Scout, trapping | 31,000 | **[C]** a successful trap pays creature level x 15 x 5, so 31,000 is about 83 level-5 or 41 level-10 trap kills; the bots never trap | **[?]** (needs crafted traps) |
| Scout, camp | 36,000 | **[?]** paid when a camp despawns from a per-camp template value I did not find; fishing also pays camp XP | **[?]** |

Mastery-time summary, in hours of play, with what is missing:

| Profession | Measured part | Not measured | Total |
|---|---|---|---|
| Brawler | 108-134 (A), 16-20 (B) | nothing | 16-134 |
| Marksman | 110-139 (A), 16-20 (B) | nothing | 16-139 |
| Medic | 26-30 (hub) or 160-192 (thin) | crafting, about 26 crafts | 30-200 |
| Entertainer | 9.4 dance, about 9.4 music | image design (about 62 sessions), healing | at least 19 |
| Scout | 41-98 scout XP | trapping, camp | at least 41-98 |

### 4.3 Which boxes block each profession

| Profession | Blocked trees (bots earned 0) | Share of the tree's XP | What earns it |
|---|---|---|---|
| Scout | tools (trapping), camp | 67,000 of 129,000 (52%) | throw traps at creatures (level x 15 x 5 per success); owning and using a camp |
| Medic | crafting | 10,500 of 103,500 (10%) | crafting medicine (stimpacks and the like) |
| Entertainer | hairstyle (image design), healing, music | 138,000 of 204,000 (68%) | image design sessions with another player; wound and battle-fatigue healing by buffing patrons; playing an instrument |
| Brawler, marksman | none | 0% | hunting |

What the bots reached in 78 min [M]: brawler `unarmed_01` at 4.6 min (median), `1handmelee_01` 19, `2handmelee_01` 31, `polearm_01` 45, `unarmed_02` 56; marksman `pistol_01` 21, `support_01` 44, `rifle_01` 53, `carbine_01` 63; medic `injury_01` 24, `injury_speed_01` 35, `ability_01` 44; entertainer `dance_01` 8.6, `dance_02` 51 (dance_03 would be at about 3.0 h and dance_04 at about 9.4 h **[E]**); scout `movement_01` 45 (127 of 285 bots) and `harvest_01` 62 (37 bots). No bot owned a third-tier box. Nothing above tier II was observed, so tiers III and IV rest on the scenarios above.

## 5. Pre-CU comparison

- **The docs hold no casual-player time-to-master.** I searched `Documentation-support`, `Systems-baseline/precu-reference.md`, the roadmap, the handoff and `Agent/knowledge-sources.md`. They give the XP-to-master tables (which the datatable reproduces exactly for Entertainer), the sandbox's 5x XP and the stock multiplier of 1.0. `SWG-professions-and-gameplay-reference.md` says exact thresholds were deliberately left to be read from the loaded tables, which this review now does.
- **What follows from that.** The XP costs are the pre-CU costs, so the server's pace differs from pre-CU only through the multiplier (5x) and the sandbox's cheaper training (x0.25 credits, 1,000 skill points). At the stock 1.0 the same play would take 5x longer: combat masters 540-670 h (A) or 80-100 h (B), medic hub 130-150 h, dance plus music about 95 h.
- **My recollection, which I could not verify and which is not from the docs:** the community usually spoke of roughly 100 hours or more to master a single combat profession at the stock rate. If that is right, scenario B at 1x (80-100 h) is about what pre-CU felt like, and A overstates it. Treat this as an unchecked hint, not as a benchmark. The owner's own target pace is the real input.

## 6. Does the pace look right, and what to change

**What the data supports**
1. **The global 5x is a blunt tool for uneven professions.** Combat XP per kill grows steeply with creature level, while heal XP, dance flourishes and harvest XP do not. Raising the global multiplier to speed up scouts or medics would make combat masters nearly instant (B at 10x: about 10 h).
2. **Combat looks fine to fast at 5x, if scenario B is close; slow for a casual if A is.** A and B differ 7x. Only a run that reaches tiers III and IV can say which; `FINDINGS.md` already recommends an overnight run (4-8 h). The bots would also need to hunt higher-level creatures as they level, which they currently do (`launchFindTarget` allows level + 4 + level/2).
3. **Medic is the outlier that depends on population.** A small friends' server will have far fewer hurt players than the bots' 1,500-strong town, so the thin-demand figure (about 480 XP an hour, 160-190 h) is the realistic one. Medics will feel the slowest of the five unless they can earn from something else.
4. **Entertainer dance and music are fast** (about 9 h each at 5x); the long poles are image design (needs a second player) and healing.
5. **Scout is slow on measured scout XP** (81-98 h for 62,000, plus trapping and camp), partly an artefact of the random harvest type. Re-measure with the right type before touching the scout rate.

**Suggested multipliers** (formula: new multiplier = 5 x current hours / target hours, applied only to the XP type in question). For a target of 70 hours (10 weeks at 7 h a week, 3.5 weeks at 20 h):

| Case | Current hours | Multiplier for 70 h |
|---|---|---|
| Combat, scenario A | 110-139 | about 8-10 |
| Combat, scenario B | 16-20 | about 1.1-1.4 (slower, not faster) |
| Medic, thin demand | 160-192 | about 11-14 |
| Medic, hub | 26-30 | about 2 (slower) |
| Scout XP, measured | 81-98 | about 6-7; about 1.5-2 if the harvest-type fix holds |
| Dance and music | about 19 | about 1.4 (slower) |

Recommendation, in this order:
1. **Leave `globalExpMultiplier` at 5.0 for now.** The data cannot say whether combat is too slow or too fast, and the only wrong direction is a big change before the overnight run.
2. **Run the overnight run** (4-8 h, `botpop launch` with the whole tree) and add to the bots: trapping, camps, medicine crafting, image design, music and (if feasible) entertainer buffs, and a correct harvest type. That turns every [E] and [?] above into [M] and tests scenario B.
3. **If the thin-demand medic or the scout stay slow, use a per-type multiplier**, not the global one. It needs a small code change (a per-type table in `awardExperience`; today only `jedi_general` has its own multiplier), made by the server-lock holder and cross-reviewed. Candidates: `medical` x3-5, `scout` x2 (only if the harvest-type fix does not close the gap).
4. **While testing, `/server playermanager setxpmodifier` changes the global value live** without a restart, so a human test session can try 3, 5 and 10 and read the same XP-per-hour numbers.

## 7. Caveats and open questions

- **Short horizon.** 78 minutes; tiers III and IV, the master box and the 70,000-XP boxes were never reached. Scenario B is a model, not data.
- **Bot behaviour is not a casual player.** The bots never rest in a bank, never travel by shuttle, never group, flourish every 6-10 s, hold the weapon of the cheapest open box, and share kills with about 83 others per city. A solo player in a quiet area would get more per kill (up to 2x) and, early on, find fewer creatures.
- **Species mix.** Species XP modifiers (`xpBonusList`) were not broken out.
- **Unarmed outlier.** Brawler unarmed at 3-5x the other lines makes the first brawler line cheap; worth a balance check.
- **`harvests` counts commands, not successes** (`BotPopLaunchBrain.h:455`), so the scout rate cannot be split into per-success XP without a log change.
- **Camp XP** comes from per-camp template values I did not locate.
- **Credits** were counted, not charged; a real character needs 11,275 credits per profession at the sandbox's x0.25.
- **Analysis scripts** are in the session's temporary folder, not in the repo (loader, rate analysis, model). I can turn them into `tools/bots/pacing_review.py` if wanted.
