# How real pre-CU players built characters, and training orders for the launch simulation's bots

16 Oct 2026, Claude (Sonnet). For the multiclass feature of the launch simulation's server bots (owner, 16 Oct, 1 AM: "multiclass like real pre-CU players", four styles, half the bots on 1,000 skill points, half on 250). Nothing under `/opt/swg` was touched. The skill table was read with `tools/owner_content/swg_client_data.py` (reads the client archives in memory; I dumped the 1,068 rows to a temporary folder outside the repo).

Labels: **[C]** read from the client skill data (`datatables/skill/skills.iff`, `xp_limits.iff`, `skl_n.stf`), **[S]** stated by a public source (section 7), **[M]** measured in the launch simulation (`Bot-reports/launch-sim/pacing-review.md`), **[E]** my estimate, **[?]** not known.

## Summary

1. **Every real build was "a few masters plus novice dips inside 250 points".** The cap was fixed at 250, skills could be surrendered and re-bought at any time, and a Novice Marksman box cost 15 points [S1, C]. Players therefore kept a base profession (77 points to master) or an elite profession (63 more) and spent what was left on novice boxes of other professions [S2, S3].
2. **The templates players actually named, with their cost in this server's table [C]:** Smuggler + Pistoleer + Teras Kasi Artist 247; Ranger + Rifleman 232; any melee master + Doctor 232 (Doctor needs Master Medic here); Bounty Hunter + Pistoleer or Carbineer 232; Rifleman + Combat Medic 246; Dancer + Musician + Image Designer 244. Each is a combination of two or three of the six base professions plus elite boxes. Table in section 2.
3. **The owner's four styles are the base halves of those templates.** Hunter (Marksman + Scout, 154 points) is the front end of Ranger + Rifleman. Tank (Brawler + Medic, 154) is the front end of Teras Kasi / Fencer / Swordsman / Pikeman + Doctor. Support (Entertainer + Medic, 154) is the front end of a Doctor + Dancer / Musician buff pair; this one is the least well documented (section 6). The Sampler is the "novice dip" habit taken to its end.
4. **Elite professions are out of reach for the first 10-20 hours**, and probably for the whole simulation: the first elite box (`combat_rifleman_novice`) costs 125,000 XP of rifle type, and every later rifleman weapon box 175,000 to 450,000 (its support line 60,000 to 150,000 of `combat_general`) [C]. The orders below stay inside the six base professions.
5. **In the first 20 hours the point budget does not bind.** A bot on 250 points will have spent about 60-105 points by hour 20 [E]. The two variants differ in how many novice boxes are bought up front and how far the tail goes, so the 250 lists end with 23-24 points unspent, deliberately.
6. **The one rule that matters more than list order: XP above a type's cap is lost.** A type with no owned box caps at 2,000 XP (`combat_general` 170,000, `crafting_general` and `crafting_medicine_general` 1,000) [C]. Buy the first box of a type as soon as 1,000 XP (300 for `combat_marksman_support_01`, 500 for crafting boxes) is banked, even if the list says later.

## 1. The rules the builds had to live with [C]

Costs are the client table's, the same as the pacing review's section 3; the sandbox charges 0.25x of the credit figures.

| Box | Skill points | XP (combat weapon lines) | XP (medic, scout, entertainer lines) | Credits (client / sandbox) |
|---|---:|---:|---:|---|
| Novice (any base profession) | 15 | 0 | 0 | 100 / 25 |
| Line box I | 2 | 1,000 | 1,000 | 1,000 / 250 |
| Line box II | 3 | 5,000 | 5,000 | 2,000 / 500 |
| Line box III | 4 | 15,000 | 10,000 (dance and music 15,000) | 3,000 / 750 |
| Line box IV | 5 | 70,000 | 15,000 (dance and music 45,000) | 4,000 / 1,000 |
| Master | 6 | 0 | 0 | 5,000 / 1,250 |
| **Base profession, everything** | **77** | 364,000 (Brawler), 303,550 (Marksman) | 129,000 (Scout), 103,500 (Medic), 204,000 (Entertainer) | 45,100 / 11,275 |

- Each base profession has four lines and costs 15 + 4 x (2+3+4+5) + 6 = 77 points. `combat_marksman_support` is the cheap line (300 / 2,250 / 6,000 / 22,000 XP of `combat_general`, which arrives by itself as 10% of all combat XP [M]).
- Elite professions: 63 points each (novice 6, lines 5+4+3+2 x 4, master 1) on top of their prerequisites, which are boxes of the base professions: Rifleman, Pistoleer, Carbineer, Teras Kasi Artist (`combat_unarmed`), Fencer (`combat_1hsword`), Swordsman (`combat_2hsword`) and Pikeman (`combat_polearm`) need the matching `_04` weapon box; Doctor needs **Master Medic**; Ranger needs **Master Scout**; Creature Handler needs `outdoors_scout_movement_04` and `harvest_04`; Combat Medic needs `combat_marksman_support_04` and Master Medic; Bounty Hunter needs Master Marksman and `outdoors_scout_movement_04`; Smuggler needs `combat_marksman_pistol_04` and `combat_brawler_unarmed_04`. Resulting masters: Rifleman 92, Creature Handler 106, Smuggler 121, Doctor 140, Ranger 140, Bounty Hunter 169 points including prerequisites.
- The Fandom pre-NGE Doctor page says 106 points with Medical Support IV and Augmentation IV as prerequisites; that is the later (post-CU) tree. This server's client has the original tree (Medic lines First Aid, Diagnostics, Pharmacology, Organic Chemistry), where Doctor needs the whole Master Medic. The point totals below come from the table, not from the sources.

## 2. Documented templates

Points are the closure of the named masters in `skills.iff` [C], so they include prerequisites. "Partial" means the poster gave a partial line in grid notation (for example "Medic 2400"), so only a lower bound is computed. Source tags are in section 7. Posts are recollections, many from after the Combat Upgrade; where a poster said pre-CU I say so.

| Template (professions and boxes) | Points [C] | Used for | Source |
|---|---:|---|---|
| Smuggler + Pistoleer + Teras Kasi Artist (masters) | 247 | PvP duels and a first template while learning the game; the most repeated triple, named by several posters in both threads. It fits the 250 cap with 3 points spare, which is a good sign the table matches the pre-CU rules | S3, S4 |
| Ranger + Rifleman (masters); 18 spare = Novice Medic | 232 | Hunting for hides and meat, resource sales, solo PvE | S3, S5 |
| Master Rifleman + some Medic + Creature Handler | 198 + medic boxes | Solo hunts and early PvP, early pre-CU | S4 |
| **Owner's build:** Master Creature Handler + Master Rifleman + Master Marksman | 246 | Pet play data for the project | project docs (`SWG-handoff-archive.md`) |
| Teras Kasi Artist + Doctor (masters) | 232 | A money maker through combat and buffing; solo PvE | S5 (excerpt), S4 |
| Swordsman + Doctor; Fencer + Doctor; Pikeman + Doctor | 232 each | PvE favourites (buff, heal, cure your own states; weak defences); Fencer + Doctor and Rifleman + Doctor also named for group PvP | S5 (excerpt), S4, S3 |
| Rifleman + Doctor | 232 | Best group-PvP template on the emulator (14.1 era) | S4 |
| Rifleman + Combat Medic; Doctor + Combat Medic + Rifles IV | 246 each | PvP: poisons, Jawa ion rifle, mind damage | S3 |
| Bounty Hunter + Pistoleer; Bounty Hunter + Carbineer | 232 each | PvP, hunting Jedi; casual multi-profession | S3, S4 |
| Teras Kasi Artist + Rifleman + Fencer | 261 | Early strong PvP build; third master must have been partial | S4 |
| Fencer + Pistoleer ("dodge stack"); Rifleman + Pikeman | 184 each + partials | PvP before the defence cap; mind-attack combination | S4 |
| Teras Kasi Artist + Master Tailor + Novice Scout | 199 | Harvesting, tanking groups, crafting | S4 |
| Teras Kasi + Swordsman + Brawler + Medic 2400 | partial | Solo hunting of high-end creatures | S4 |
| Bounty Hunter + Pistoleer + Smuggler + Novice Medic; Master Bounty Hunter + Carbineer + Novice Entertainer | partial | PvP duels (the second one used the novice entertainer to dance over defeated players) | S4 |
| Artisan + Pistoleer (novice) + Medic, Scout, Merchant, Musician | 199+ | Crafting and utility, with several novice dips | S3 |
| Armorsmith + Weaponsmith + Merchant (any three elite crafters; leftovers on two vendors from Artisan Business) | 232 | Crafting | S7 (Restoration, outdated page) |
| Master Rifleman + Droid Engineer | 184 | Hunting plus crafting droids, pre-CU | S4 |
| Dancer + Musician (+ Image Designer, or + Master Entertainer) | 183 (+ 61 = 244; or 203) | Social: 20-point inspiration buffs, entertainment; leftovers on Artisan survey and Merchant for vendors | S7, S3 |

Observations that matter for the bots:
- **Novice dips were normal.** Posters list Novice Scout (a starter guide says it costs nothing until the points are needed back, and every corpse can then be harvested [S9]), Novice Medic (self-heals of 300-500, said to be enough for solo hunting at that level [S8]), Novice Entertainer, Novice Artisan, Novice Commando.
- **Medic was the common second profession.** Doctor or Medic appears in about a third of the posted templates (S3: about 6 of 21); the stated reason is self-healing and buffs, and that it is cheap for melee characters [S5, S7].
- **Players mastered fast on live servers, with buffs and missions.** One guide claims 1-3 days per combat profession and about one hour per weapon line with doctor buffs and high-level lair missions; treat that as a boast, not a benchmark [S8]. On this server the pacing review's rates apply.

## 3. How real players ordered the first boxes

From the guides that describe the grind (S8, plus excerpts of S5); the order is the same in all of them.

- **Combat (Marksman, Brawler).** Buy the novice, then do the first line box on newbie spawns outside a city with the novice special on a looping macro; use buffs for the middle levels; finish a line with lair missions. A starter guide advises the first four boxes on easy city destroy missions without buffs [S9]. One weapon line at a time, because XP is earned only for the weapon you hold. Marksman: rifle line first for hunters (headshot, single pulls), pistol or carbine for PvP builds.
- **Medic.** Pharmacology (here `science_medic_ability`) first, because better stimpacks heal more per use and so give more XP per heal; then First Aid (`injury`), then Diagnostics (`injury_speed`); Organic Chemistry (`crafting`) is earned by crafting practice-mode medicine, not healing. XP came from healing other players in cantinas, hospitals, camps and groups [S8].
- **Scout.** Hunting (`harvest`) and Exploration (`movement`) from harvesting corpses; Trapping (`tools`) from thrown traps at mid-level creatures; Survival (`camp`) from crafting and disbanding camps.
- **Entertainer.** Dance and music from flourishes in a cantina, with a bonus per other performer in the group; image design needs a customer; entertainment healing comes from healing patrons' wounds and fatigue in a cantina [S8].
- **Artisan.** Surveying and sampling for `survey`; crafting practice mode for the rest [S8].

## 4. The four styles

### Common rules for all lists

1. Walk down the list. Buy a box when the character has the points, the credits and the XP of that box's type. **Skip a box that cannot be afforded yet; do not wait on it.**
2. **XP cap rule (overrides the order):** if a bot has banked 1,000 XP (300 for `combat_marksman_support_01`, 500 for crafting boxes) of a type it owns no box of, buy that type's first box now. Otherwise XP above 2,000 is lost.
3. Boxes the launch simulation could not earn [M] sit last in their tier and in the 250 lists: scout `tools` and `camp`, entertainer `hairstyle`, `healing` and `music`, medic `crafting`. Artisan lines were not measured [?]. They are in the lists because the masters need them; a bot that cannot earn the XP simply never reaches them.
4. Masters come last; they cost 0 XP and 6 points once all four `_04` boxes are owned.
5. Hours are **[E]** from the measured rates: dance 7.1k XP per hour; unarmed 11k, one-hand 3.2k, two-hand 2.2k, polearm 1.6k; pistol 2.7k, carbine 2.1k, rifle 2.0k (wielded, constant-rate scenario A, which overstates the time at high tiers if the bot moves to tougher creatures: the level-scaled scenario B is 5-7x faster); medical 3.5k with a busy hub, 0.5k with a thin one; scout 0.77k; `combat_general` 10% of weapon XP.
6. The 250 variant is the longest sensible list that fits 250 points. The 1,000 variant buys all six base novices first (90 points, 150 credits in the sandbox), then follows the same order, then finishes every base profession (462 points, all six masters). Elite boxes are in neither: Rifleman 125,000+ XP per box.

### 4.1 Hunter: Marksman + Scout

Basis: Ranger + Rifleman (232) and Bounty Hunter + Scout (217) templates; hunters harvested hides and meat, pulled single creatures with the rifle, and kept Novice Medic for self-healing (S3, S4, S5). **250 total: 226 points**, 24 spare. The tail adds pharmacology and first aid (medic, 28 points) and Artisan surveying (29) the way real hunters dipped for self-heal and resource sales.

| # | Box | Pts | XP gate (cumulative, type) | Hour [E] |
|---:|---|---:|---|---|
| 1-3 | `combat_marksman_novice`, `outdoors_scout_novice`, `science_medic_novice` | 45 | none | 0 |
| 4 | `combat_marksman_rifle_01` | 2 | 1,000 rifle | 0.5 |
| 5 | `combat_marksman_support_01` | 2 | 300 combat_general | 1.5 |
| 6-7 | `outdoors_scout_harvest_01`, `movement_01` | 4 | 1,000 / 2,000 scout | 2-4 (harvest every corpse) |
| 8-9 | `combat_marksman_rifle_02`, `support_02` | 6 | 6,000 rifle; 2,550 general | 3; 13 |
| 10-11 | `outdoors_scout_harvest_02`, `movement_02` | 6 | 7,000 / 12,000 scout | 12-20 |
| 12 | `combat_marksman_rifle_03` | 4 | 21,000 rifle | 10 |
| 13-15 | `support_03`, `harvest_03`, `movement_03` | 12 | 8,550 general; 22,000 / 32,000 scout | 40+ |
| 16-19 | `rifle_04`, `support_04`, `harvest_04`, `movement_04` | 20 | 91,000 rifle (46 h A, 7 h B) | 40+ |
| 20-28 | pistol and carbine lines interleaved, `combat_marksman_master` | 34 | 91,000 each | later |
| 29-36 | `science_medic_ability` 1-4, `injury` 1-4 (medical: bots only earn it by healing others) | 28 | 31,000 each | n/a for a hunter |
| 37-41 | `crafting_artisan_novice`, `crafting_artisan_survey` 1-4 | 29 | survey: 500 / 3,000 / 8,000 / 18,000 | [?] |
| 42-50 | scout `tools` and `camp` 1-4, `outdoors_scout_master` | 34 | trapping and camp XP: [M] none earned | never in the sim |

Expected by hour 20 [E]: three novices, `rifle_01-03`, `support_01-02`, `harvest_01-02` and `movement_01-02` maybe; about 65 points.

### 4.2 Tank: Brawler + Medic

Basis: melee master + Doctor (232) in at least six of the named templates, the stated reason being that a brawler's own stats do not depend on a ranged weapon, so healing is the cheap add (S4, S5, S7). Unarmed first: it is the Teras Kasi prerequisite, carries Center of Being, and levels 3-5x faster in the simulation [M]. Pharmacology and First Aid before Diagnostics, as players did (S8). **250 total: 226 points**: Master Brawler + Master Medic (154) + Marksman novice, rifle and support lines (43; the Teras Kasi + Rifleman pairing) + Scout novice and harvest (29; the "Novice Scout for harvesting" dip).

| # | Box | Pts | XP gate (cumulative, type) | Hour [E] |
|---:|---|---:|---|---|
| 1-2 | `combat_brawler_novice`, `science_medic_novice` | 30 | none | 0 |
| 3 | `combat_brawler_unarmed_01` | 2 | 1,000 unarmed | 0.1 |
| 4-5 | `science_medic_ability_01`, `injury_01` | 4 | 1,000 / 2,000 medical | 0.3-4 (needs patients) |
| 6 | `unarmed_02` | 3 | 6,000 unarmed | 0.5 |
| 7-8 | `ability_02`, `injury_02` | 6 | 7,000 / 12,000 medical | 2-24 |
| 9 | `unarmed_03` | 4 | 21,000 unarmed | 2 |
| 10-11 | `ability_03`, `injury_03` | 8 | 22,000 / 32,000 medical | 6-64 |
| 12 | `unarmed_04` (Teras Kasi Fundamentals) | 5 | 91,000 unarmed | 8 |
| 13-14 | `ability_04`, `injury_04` | 10 | 47,000 / 62,000 medical | later |
| 15-18 | `science_medic_injury_speed_01-04` | 14 | 63,000 to 93,000 medical | later |
| 19-31 | `1handmelee`, `2handmelee`, `polearm` lines interleaved, `combat_brawler_master` | 48 | 91,000 each; 28 h (one-hand), 41 h (two-hand), 56 h (polearm) [A] | after hour 10; tier I-II by hour 20 |
| 32-45 | `combat_marksman_novice`, `rifle_01-04`, `support_01-04`, `outdoors_scout_novice`, `harvest_01-04` | 72 | see Hunter | later |
| 46-50 | `science_medic_crafting_01-04`, `science_medic_master` | 20 | crafting_medicine_general 500 to 10,500 | never in the sim |

Expected by hour 20 [E]: `unarmed_01-04` (hour 8), `ability_01`, `injury_01` (more with a busy hub), tier I-II of the other three weapon lines; about 65 points.

### 4.3 Support: Entertainer + Medic

Basis: the Doctor + Dancer / Musician pairing. Players queued for doctor buffs and entertainer buffs before hunting, doctors earned credits selling buffs, and the social core was Master Dancer + Master Musician, then Image Designer and Master Entertainer or Artisan survey and merchant boxes for vendors (S7, S8). **Honest caveat:** no source names "Entertainer + Medic" as a two-master template; I am inferring it from the base halves (section 6). Dance first: it is the fastest XP in the simulation [M]. **250 total: 226 points**: Master Entertainer + Master Medic (154) + Artisan novice, survey and business (43; vendors and sampling, S7) + Scout novice and harvest (29).

| # | Box | Pts | XP gate (cumulative, type) | Hour [E] |
|---:|---|---:|---|---|
| 1-2 | `social_entertainer_novice`, `science_medic_novice` | 30 | none | 0 |
| 3 | `social_entertainer_dance_01` | 2 | 1,000 dance | 0.15 |
| 4-6 | `science_medic_ability_01`, `injury_01`, `injury_speed_01` | 6 | 1,000 / 2,000 / 3,000 medical | 0.3-6 |
| 7 | `dance_02` | 3 | 6,000 dance | 0.85 |
| 8-10 | `ability_02`, `injury_02`, `injury_speed_02` | 9 | 8,000 / 13,000 / 18,000 medical | 2-36 |
| 11 | `dance_03` | 4 | 21,000 dance | 3 |
| 12-14 | `ability_03`, `injury_03`, `injury_speed_03` | 12 | 28,000 / 38,000 / 48,000 medical | 8-96 |
| 15 | `dance_04` | 5 | 66,000 dance | 9.3 |
| 16-18 | `ability_04`, `injury_04`, `injury_speed_04` | 15 | 63,000 / 78,000 / 93,000 medical | later |
| 19-27 | artisan novice, `survey` 1-4, `business` 1-4 (interleaved) | 43 | survey 500 to 18,000; business 500 to 10,500 | [?] |
| 28-32 | `outdoors_scout_novice`, `harvest_01-04` | 29 | 31,000 scout | later |
| 33-50 | `music` 1-4, `healing` 1-4, `hairstyle` 1-4, medic `crafting` 1-4, both masters | 68 | music/healing/image-design/crafting XP | never in the sim [M] |

Expected by hour 20 [E]: `dance_01-04` by hour 9.3, then about 10 hours of medic work: with a busy hub roughly two medic lines to tier III, with a thin crowd tier I-II of one or two.

### 4.4 Novice sampler

Basis: the habit of buying novice boxes to get their abilities, then spending real XP in one place: Novice Medic for heals, Novice Scout for corpse harvesting, Novice Artisan for survey and a crafting kit, Novice Entertainer for dance and music, one deep profession (S3, S4, S8, S9). Deep profession: **Marksman, rifle line first**. A bot that should go deep in Brawler instead swaps lines one for one: rifle -> unarmed, support -> `1handmelee`, pistol -> `2handmelee`, carbine -> `polearm` (identical costs; unarmed levels 3-5x faster than the others [M]). **250 total: 227 points**: six novices (90), Master Marksman (62 more, 152), then tier I and II of the eleven other earnable lines (55) and tier III of five (20).

| # | Box | Pts | Note |
|---:|---|---:|---|
| 1-6 | `science_medic_novice`, `outdoors_scout_novice`, `crafting_artisan_novice`, `social_entertainer_novice`, `combat_brawler_novice`, `combat_marksman_novice` | 90 | all at hour 0, 150 credits in the sandbox |
| 7-14 | `rifle_01`, `support_01`, `rifle_02`, `support_02`, `rifle_03`, `support_03`, `rifle_04`, `support_04` | 28 | same gates as the Hunter; rifle_03 around hour 10 |
| 15-23 | pistol and carbine lines interleaved, `combat_marksman_master` | 34 | later |
| 24-50 | tier I and II of scout harvest and movement, medic ability, injury and injury_speed, dance, unarmed, one-hand, two-hand, polearm, artisan survey; tier III of harvest, ability, injury, dance, unarmed | 75 | **bought out of order by the XP cap rule** as soon as incidental XP of that type reaches 1,000 (scout XP from harvesting, medical XP from heals, dance if the bot dances) |

Expected by hour 20 [E]: six novices, `rifle_01-03`, `support_01-02`, plus the tier I boxes of whichever other XP types the bot happened to earn; about 100-110 points.

## 5. Notes for the feature

- **Credits.** The sandbox's whole 250-point list costs about 23,000-30,000 credits (x0.25); the 1,000-point full base set 67,650. New characters start with 10,000 cash and 100,000 in the bank (`SWG-project-record.md`, not rechecked here), so credits gate nothing in the first 20 hours.
- **Respec.** Real players surrendered skills freely. The lists never surrender; a bot that wants a different style needs a fresh character.
- **Start.** In Core3 a new character is created with the novice box of its starting profession (15 points; not verified on this server). Every list opens with novices, so the buying code should skip boxes already owned.
- **Elite extension, optional.** For long runs, append after the base masters: `combat_rifleman_novice` (6 points, 125,000 rifle XP, needs `combat_marksman_rifle_04`), `outdoors_ranger_novice` (needs Master Scout), `combat_unarmed_novice` (needs `combat_brawler_unarmed_04`), `science_doctor_novice` (6 points, 11,250 medical XP, needs Master Medic; the first line boxes are 15,000 XP each). Only Doctor's first boxes are within reach in the simulation's time frame, and Master Medic needs the medic crafting line that the bots cannot yet earn.

## 6. What is uncertain

- **Era.** The community threads mix pre-CU, post-CU (Combat Upgrade) and sometimes NGE recollections, and they use grid notation I could not fully decode. The point totals come from this server's table, not from the posts. The Fandom pre-NGE pages and the Restoration wiki (a Combat Upgrade based server with changed trees: Master Brawler there is 72 points) describe different trees from this client's table.
- **Entertainer + Medic** is not a named template in what I could read; Support rests on the doctor-plus-buffs pattern and the social core.
- **The SWGEmu forum archive of the old official forums** (2007-2008 template guides) is behind a bot check that I did not bypass. I know those threads only from search-result excerpts, so S5 is second hand: the template names there are reliable, the details are not.
- **Hours.** All hour figures are estimates from the pacing review's rates and carry its caveats (constant rate overstates, level-scaled understates, medic depends on patients, scout rate depends on the harvest type).
- **Medical XP for the Tank and Hunter.** I did not check whether self-heals earn medical XP in Core3; the lists assume only healing other players does.
- **Artisan lines** were not measured in the simulation.
- **Numbers in S8** (days to master, XP per hour) are the author's claims about the live game.

## 7. Sources

No names of people are given. Community material is cited for the facts it states; nothing was copied.

- **S1, community wiki.** SWG Wiki (Fandom), "Skill points" (pre-NGE, marked historical): 250 points, four branches of four boxes plus Novice and Master, Novice Marksman 15 points, surrender and re-buy. Read 16 Oct 2026 in the browser pane (undated page).
- **S2, community wiki.** SWG Wiki (Fandom), "Professions (pre-NGE)" and "Doctor": base, elite and hybrid profession list; the Doctor page's later-tree prerequisites. Read 16 Oct 2026.
- **S3, community forum.** An MMORPG.com forum thread asking players to post their pre-CU templates (21 entries); undated in the copy I read. Counts: Pistoleer in about ten, Rifleman six, Medic or Doctor six, Bounty Hunter five, Teras Kasi five, Ranger four, Smuggler four.
- **S4, community forum.** A Wanderhomies thread "Favorite SWG Template and why?" (three pages, undated), pre-CU, post-CU and NGE recollections with era and use stated.
- **S5, archive (second hand).** The SWGEmu archive of the old official forums (archive stamps 27-30 Jan 2007): threads on Teras Kasi template guides, "Template Questions answered" (Swordsman), a PvE template guide, "Ranger Templates: Pros/Cons", "Master Rifleman/Master Doctor PVP guide", "Rifleman FAQ" and Doctor and Brawler guides (archive stamp 8 Jan 2008). Pages blocked by a bot check; excerpts via search results only.
- **S7, community wiki (Restoration).** swgr.org wiki: "Build Tips - Outdated", Brawler, Medic, Entertainer, Doctor (a Combat Upgrade based server with modified trees; outdated page, Entertainer page mentions a January 2025 patch). Read 16 Oct 2026.
- **S8, community guide (archive).** "All In One Strategy Guide" posted on EQSanctum's SWGEmu guides board, 3 April 2016, a copy of a live-game player guide of the Publish 10 era: profession choice, medic and scout grinding, combat grinding, crafting-only methods. Read 16 Oct 2026.
- **S9, community forum (via search excerpt).** The r/swgemu thread "A starter's guide for starters", 20 Jul 2012: novice scout dip, destroy missions for the first four combat boxes, medic and artisan tips. Its mirror site failed a certificate check, so I know it from search-result excerpts only.
- **Official / project.** Core3 stock settings: 250 skill points (via `Documentation-support/private-server-rates.md`); this server's `datatables/skill/skills.iff`, `xp_limits.iff` and `string/en/skl_n.stf` (read in memory with `tools/owner_content/swg_client_data.py`); `Bot-reports/launch-sim/pacing-review.md`; `Documentation-support/creature-handler-top-tier-plan.md` and `creature-handler-build-probe.json` (the owner's pet build and its points).

## 8. Machine-readable training orders

Keys are the four styles. Each list is in buying order and satisfies the table's prerequisites (checked by script: no unknown boxes, no box before its requirement, 250 lists 226-227 points, 1,000 lists 462 points). Apply the rules in section 4 ("Common rules").

```json
{
  "hunter": {
    "250": [
      "combat_marksman_novice", "outdoors_scout_novice", "science_medic_novice",
      "combat_marksman_rifle_01", "combat_marksman_support_01", "outdoors_scout_harvest_01",
      "outdoors_scout_movement_01", "combat_marksman_rifle_02", "combat_marksman_support_02",
      "outdoors_scout_harvest_02", "outdoors_scout_movement_02", "combat_marksman_rifle_03",
      "combat_marksman_support_03", "outdoors_scout_harvest_03", "outdoors_scout_movement_03",
      "combat_marksman_rifle_04", "combat_marksman_support_04", "outdoors_scout_harvest_04",
      "outdoors_scout_movement_04", "combat_marksman_pistol_01", "combat_marksman_carbine_01",
      "combat_marksman_pistol_02", "combat_marksman_carbine_02", "combat_marksman_pistol_03",
      "combat_marksman_carbine_03", "combat_marksman_pistol_04", "combat_marksman_carbine_04",
      "combat_marksman_master", "science_medic_ability_01", "science_medic_injury_01",
      "science_medic_ability_02", "science_medic_injury_02", "science_medic_ability_03",
      "science_medic_injury_03", "science_medic_ability_04", "science_medic_injury_04",
      "crafting_artisan_novice", "crafting_artisan_survey_01", "crafting_artisan_survey_02",
      "crafting_artisan_survey_03", "crafting_artisan_survey_04", "outdoors_scout_tools_01",
      "outdoors_scout_camp_01", "outdoors_scout_tools_02", "outdoors_scout_camp_02",
      "outdoors_scout_tools_03", "outdoors_scout_camp_03", "outdoors_scout_tools_04",
      "outdoors_scout_camp_04", "outdoors_scout_master"
    ],
    "1000": [
      "combat_marksman_novice", "outdoors_scout_novice", "science_medic_novice",
      "combat_brawler_novice", "social_entertainer_novice", "crafting_artisan_novice",
      "combat_marksman_rifle_01", "combat_marksman_support_01", "outdoors_scout_harvest_01",
      "outdoors_scout_movement_01", "combat_marksman_rifle_02", "combat_marksman_support_02",
      "outdoors_scout_harvest_02", "outdoors_scout_movement_02", "combat_marksman_rifle_03",
      "combat_marksman_support_03", "outdoors_scout_harvest_03", "outdoors_scout_movement_03",
      "combat_marksman_rifle_04", "combat_marksman_support_04", "outdoors_scout_harvest_04",
      "outdoors_scout_movement_04", "combat_marksman_pistol_01", "combat_marksman_carbine_01",
      "combat_marksman_pistol_02", "combat_marksman_carbine_02", "combat_marksman_pistol_03",
      "combat_marksman_carbine_03", "combat_marksman_pistol_04", "combat_marksman_carbine_04",
      "combat_marksman_master", "science_medic_ability_01", "science_medic_injury_01",
      "science_medic_ability_02", "science_medic_injury_02", "science_medic_ability_03",
      "science_medic_injury_03", "science_medic_ability_04", "science_medic_injury_04",
      "crafting_artisan_survey_01", "crafting_artisan_survey_02", "crafting_artisan_survey_03",
      "crafting_artisan_survey_04", "outdoors_scout_tools_01", "outdoors_scout_camp_01",
      "outdoors_scout_tools_02", "outdoors_scout_camp_02", "outdoors_scout_tools_03",
      "outdoors_scout_camp_03", "outdoors_scout_tools_04", "outdoors_scout_camp_04",
      "outdoors_scout_master", "combat_brawler_1handmelee_01", "combat_brawler_2handmelee_01",
      "combat_brawler_polearm_01", "combat_brawler_unarmed_01", "crafting_artisan_business_01",
      "crafting_artisan_domestic_01", "crafting_artisan_engineering_01", "science_medic_injury_speed_01",
      "social_entertainer_dance_01", "science_medic_crafting_01", "social_entertainer_hairstyle_01",
      "social_entertainer_healing_01", "social_entertainer_music_01", "combat_brawler_1handmelee_02",
      "combat_brawler_2handmelee_02", "combat_brawler_polearm_02", "combat_brawler_unarmed_02",
      "crafting_artisan_business_02", "crafting_artisan_domestic_02", "crafting_artisan_engineering_02",
      "science_medic_injury_speed_02", "social_entertainer_dance_02", "science_medic_crafting_02",
      "social_entertainer_hairstyle_02", "social_entertainer_healing_02", "social_entertainer_music_02",
      "combat_brawler_1handmelee_03", "combat_brawler_2handmelee_03", "combat_brawler_polearm_03",
      "combat_brawler_unarmed_03", "crafting_artisan_business_03", "crafting_artisan_domestic_03",
      "crafting_artisan_engineering_03", "science_medic_injury_speed_03", "social_entertainer_dance_03",
      "science_medic_crafting_03", "social_entertainer_hairstyle_03", "social_entertainer_healing_03",
      "social_entertainer_music_03", "combat_brawler_1handmelee_04", "combat_brawler_2handmelee_04",
      "combat_brawler_polearm_04", "combat_brawler_unarmed_04", "crafting_artisan_business_04",
      "crafting_artisan_domestic_04", "crafting_artisan_engineering_04", "science_medic_injury_speed_04",
      "social_entertainer_dance_04", "science_medic_crafting_04", "social_entertainer_hairstyle_04",
      "social_entertainer_healing_04", "social_entertainer_music_04", "combat_brawler_master",
      "crafting_artisan_master", "science_medic_master", "social_entertainer_master"
    ]
  },
  "tank": {
    "250": [
      "combat_brawler_novice", "science_medic_novice", "combat_brawler_unarmed_01",
      "science_medic_ability_01", "science_medic_injury_01", "combat_brawler_unarmed_02",
      "science_medic_ability_02", "science_medic_injury_02", "combat_brawler_unarmed_03",
      "science_medic_ability_03", "science_medic_injury_03", "combat_brawler_unarmed_04",
      "science_medic_ability_04", "science_medic_injury_04", "science_medic_injury_speed_01",
      "science_medic_injury_speed_02", "science_medic_injury_speed_03", "science_medic_injury_speed_04",
      "combat_brawler_1handmelee_01", "combat_brawler_2handmelee_01", "combat_brawler_polearm_01",
      "combat_brawler_1handmelee_02", "combat_brawler_2handmelee_02", "combat_brawler_polearm_02",
      "combat_brawler_1handmelee_03", "combat_brawler_2handmelee_03", "combat_brawler_polearm_03",
      "combat_brawler_1handmelee_04", "combat_brawler_2handmelee_04", "combat_brawler_polearm_04",
      "combat_brawler_master", "combat_marksman_novice", "combat_marksman_rifle_01",
      "combat_marksman_support_01", "combat_marksman_rifle_02", "combat_marksman_support_02",
      "combat_marksman_rifle_03", "combat_marksman_support_03", "combat_marksman_rifle_04",
      "combat_marksman_support_04", "outdoors_scout_novice", "outdoors_scout_harvest_01",
      "outdoors_scout_harvest_02", "outdoors_scout_harvest_03", "outdoors_scout_harvest_04",
      "science_medic_crafting_01", "science_medic_crafting_02", "science_medic_crafting_03",
      "science_medic_crafting_04", "science_medic_master"
    ],
    "1000": [
      "combat_brawler_novice", "science_medic_novice", "combat_marksman_novice",
      "outdoors_scout_novice", "social_entertainer_novice", "crafting_artisan_novice",
      "combat_brawler_unarmed_01", "science_medic_ability_01", "science_medic_injury_01",
      "combat_brawler_unarmed_02", "science_medic_ability_02", "science_medic_injury_02",
      "combat_brawler_unarmed_03", "science_medic_ability_03", "science_medic_injury_03",
      "combat_brawler_unarmed_04", "science_medic_ability_04", "science_medic_injury_04",
      "science_medic_injury_speed_01", "science_medic_injury_speed_02", "science_medic_injury_speed_03",
      "science_medic_injury_speed_04", "combat_brawler_1handmelee_01", "combat_brawler_2handmelee_01",
      "combat_brawler_polearm_01", "combat_brawler_1handmelee_02", "combat_brawler_2handmelee_02",
      "combat_brawler_polearm_02", "combat_brawler_1handmelee_03", "combat_brawler_2handmelee_03",
      "combat_brawler_polearm_03", "combat_brawler_1handmelee_04", "combat_brawler_2handmelee_04",
      "combat_brawler_polearm_04", "combat_brawler_master", "combat_marksman_rifle_01",
      "combat_marksman_support_01", "combat_marksman_rifle_02", "combat_marksman_support_02",
      "combat_marksman_rifle_03", "combat_marksman_support_03", "combat_marksman_rifle_04",
      "combat_marksman_support_04", "outdoors_scout_harvest_01", "outdoors_scout_harvest_02",
      "outdoors_scout_harvest_03", "outdoors_scout_harvest_04", "science_medic_crafting_01",
      "science_medic_crafting_02", "science_medic_crafting_03", "science_medic_crafting_04",
      "science_medic_master", "combat_marksman_carbine_01", "combat_marksman_pistol_01",
      "crafting_artisan_business_01", "crafting_artisan_domestic_01", "crafting_artisan_engineering_01",
      "crafting_artisan_survey_01", "outdoors_scout_movement_01", "social_entertainer_dance_01",
      "outdoors_scout_camp_01", "outdoors_scout_tools_01", "social_entertainer_hairstyle_01",
      "social_entertainer_healing_01", "social_entertainer_music_01", "combat_marksman_carbine_02",
      "combat_marksman_pistol_02", "crafting_artisan_business_02", "crafting_artisan_domestic_02",
      "crafting_artisan_engineering_02", "crafting_artisan_survey_02", "outdoors_scout_movement_02",
      "social_entertainer_dance_02", "outdoors_scout_camp_02", "outdoors_scout_tools_02",
      "social_entertainer_hairstyle_02", "social_entertainer_healing_02", "social_entertainer_music_02",
      "combat_marksman_carbine_03", "combat_marksman_pistol_03", "crafting_artisan_business_03",
      "crafting_artisan_domestic_03", "crafting_artisan_engineering_03", "crafting_artisan_survey_03",
      "outdoors_scout_movement_03", "social_entertainer_dance_03", "outdoors_scout_camp_03",
      "outdoors_scout_tools_03", "social_entertainer_hairstyle_03", "social_entertainer_healing_03",
      "social_entertainer_music_03", "combat_marksman_carbine_04", "combat_marksman_pistol_04",
      "crafting_artisan_business_04", "crafting_artisan_domestic_04", "crafting_artisan_engineering_04",
      "crafting_artisan_survey_04", "outdoors_scout_movement_04", "social_entertainer_dance_04",
      "outdoors_scout_camp_04", "outdoors_scout_tools_04", "social_entertainer_hairstyle_04",
      "social_entertainer_healing_04", "social_entertainer_music_04", "combat_marksman_master",
      "crafting_artisan_master", "outdoors_scout_master", "social_entertainer_master"
    ]
  },
  "support": {
    "250": [
      "social_entertainer_novice", "science_medic_novice", "social_entertainer_dance_01",
      "science_medic_ability_01", "science_medic_injury_01", "science_medic_injury_speed_01",
      "social_entertainer_dance_02", "science_medic_ability_02", "science_medic_injury_02",
      "science_medic_injury_speed_02", "social_entertainer_dance_03", "science_medic_ability_03",
      "science_medic_injury_03", "science_medic_injury_speed_03", "social_entertainer_dance_04",
      "science_medic_ability_04", "science_medic_injury_04", "science_medic_injury_speed_04",
      "crafting_artisan_novice", "crafting_artisan_survey_01", "crafting_artisan_business_01",
      "crafting_artisan_survey_02", "crafting_artisan_business_02", "crafting_artisan_survey_03",
      "crafting_artisan_business_03", "crafting_artisan_survey_04", "crafting_artisan_business_04",
      "outdoors_scout_novice", "outdoors_scout_harvest_01", "outdoors_scout_harvest_02",
      "outdoors_scout_harvest_03", "outdoors_scout_harvest_04", "social_entertainer_music_01",
      "social_entertainer_healing_01", "social_entertainer_hairstyle_01", "social_entertainer_music_02",
      "social_entertainer_healing_02", "social_entertainer_hairstyle_02", "social_entertainer_music_03",
      "social_entertainer_healing_03", "social_entertainer_hairstyle_03", "social_entertainer_music_04",
      "social_entertainer_healing_04", "social_entertainer_hairstyle_04", "science_medic_crafting_01",
      "science_medic_crafting_02", "science_medic_crafting_03", "science_medic_crafting_04",
      "social_entertainer_master", "science_medic_master"
    ],
    "1000": [
      "social_entertainer_novice", "science_medic_novice", "combat_marksman_novice",
      "combat_brawler_novice", "outdoors_scout_novice", "crafting_artisan_novice",
      "social_entertainer_dance_01", "science_medic_ability_01", "science_medic_injury_01",
      "science_medic_injury_speed_01", "social_entertainer_dance_02", "science_medic_ability_02",
      "science_medic_injury_02", "science_medic_injury_speed_02", "social_entertainer_dance_03",
      "science_medic_ability_03", "science_medic_injury_03", "science_medic_injury_speed_03",
      "social_entertainer_dance_04", "science_medic_ability_04", "science_medic_injury_04",
      "science_medic_injury_speed_04", "crafting_artisan_survey_01", "crafting_artisan_business_01",
      "crafting_artisan_survey_02", "crafting_artisan_business_02", "crafting_artisan_survey_03",
      "crafting_artisan_business_03", "crafting_artisan_survey_04", "crafting_artisan_business_04",
      "outdoors_scout_harvest_01", "outdoors_scout_harvest_02", "outdoors_scout_harvest_03",
      "outdoors_scout_harvest_04", "social_entertainer_music_01", "social_entertainer_healing_01",
      "social_entertainer_hairstyle_01", "social_entertainer_music_02", "social_entertainer_healing_02",
      "social_entertainer_hairstyle_02", "social_entertainer_music_03", "social_entertainer_healing_03",
      "social_entertainer_hairstyle_03", "social_entertainer_music_04", "social_entertainer_healing_04",
      "social_entertainer_hairstyle_04", "science_medic_crafting_01", "science_medic_crafting_02",
      "science_medic_crafting_03", "science_medic_crafting_04", "social_entertainer_master",
      "science_medic_master", "combat_brawler_1handmelee_01", "combat_brawler_2handmelee_01",
      "combat_brawler_polearm_01", "combat_brawler_unarmed_01", "combat_marksman_carbine_01",
      "combat_marksman_pistol_01", "combat_marksman_rifle_01", "combat_marksman_support_01",
      "crafting_artisan_domestic_01", "crafting_artisan_engineering_01", "outdoors_scout_movement_01",
      "outdoors_scout_camp_01", "outdoors_scout_tools_01", "combat_brawler_1handmelee_02",
      "combat_brawler_2handmelee_02", "combat_brawler_polearm_02", "combat_brawler_unarmed_02",
      "combat_marksman_carbine_02", "combat_marksman_pistol_02", "combat_marksman_rifle_02",
      "combat_marksman_support_02", "crafting_artisan_domestic_02", "crafting_artisan_engineering_02",
      "outdoors_scout_movement_02", "outdoors_scout_camp_02", "outdoors_scout_tools_02",
      "combat_brawler_1handmelee_03", "combat_brawler_2handmelee_03", "combat_brawler_polearm_03",
      "combat_brawler_unarmed_03", "combat_marksman_carbine_03", "combat_marksman_pistol_03",
      "combat_marksman_rifle_03", "combat_marksman_support_03", "crafting_artisan_domestic_03",
      "crafting_artisan_engineering_03", "outdoors_scout_movement_03", "outdoors_scout_camp_03",
      "outdoors_scout_tools_03", "combat_brawler_1handmelee_04", "combat_brawler_2handmelee_04",
      "combat_brawler_polearm_04", "combat_brawler_unarmed_04", "combat_marksman_carbine_04",
      "combat_marksman_pistol_04", "combat_marksman_rifle_04", "combat_marksman_support_04",
      "crafting_artisan_domestic_04", "crafting_artisan_engineering_04", "outdoors_scout_movement_04",
      "outdoors_scout_camp_04", "outdoors_scout_tools_04", "combat_brawler_master",
      "combat_marksman_master", "crafting_artisan_master", "outdoors_scout_master"
    ]
  },
  "sampler": {
    "250": [
      "science_medic_novice", "outdoors_scout_novice", "crafting_artisan_novice",
      "social_entertainer_novice", "combat_brawler_novice", "combat_marksman_novice",
      "combat_marksman_rifle_01", "combat_marksman_support_01", "combat_marksman_rifle_02",
      "combat_marksman_support_02", "combat_marksman_rifle_03", "combat_marksman_support_03",
      "combat_marksman_rifle_04", "combat_marksman_support_04", "combat_marksman_pistol_01",
      "combat_marksman_carbine_01", "combat_marksman_pistol_02", "combat_marksman_carbine_02",
      "combat_marksman_pistol_03", "combat_marksman_carbine_03", "combat_marksman_pistol_04",
      "combat_marksman_carbine_04", "combat_marksman_master", "outdoors_scout_harvest_01",
      "outdoors_scout_movement_01", "science_medic_ability_01", "science_medic_injury_01",
      "science_medic_injury_speed_01", "social_entertainer_dance_01", "combat_brawler_unarmed_01",
      "combat_brawler_1handmelee_01", "combat_brawler_2handmelee_01", "combat_brawler_polearm_01",
      "crafting_artisan_survey_01", "outdoors_scout_harvest_02", "outdoors_scout_movement_02",
      "science_medic_ability_02", "science_medic_injury_02", "science_medic_injury_speed_02",
      "social_entertainer_dance_02", "combat_brawler_unarmed_02", "combat_brawler_1handmelee_02",
      "combat_brawler_2handmelee_02", "combat_brawler_polearm_02", "crafting_artisan_survey_02",
      "outdoors_scout_harvest_03", "science_medic_ability_03", "science_medic_injury_03",
      "social_entertainer_dance_03", "combat_brawler_unarmed_03"
    ],
    "1000": [
      "science_medic_novice", "outdoors_scout_novice", "crafting_artisan_novice",
      "social_entertainer_novice", "combat_brawler_novice", "combat_marksman_novice",
      "combat_marksman_rifle_01", "combat_marksman_support_01", "combat_marksman_rifle_02",
      "combat_marksman_support_02", "combat_marksman_rifle_03", "combat_marksman_support_03",
      "combat_marksman_rifle_04", "combat_marksman_support_04", "combat_marksman_pistol_01",
      "combat_marksman_carbine_01", "combat_marksman_pistol_02", "combat_marksman_carbine_02",
      "combat_marksman_pistol_03", "combat_marksman_carbine_03", "combat_marksman_pistol_04",
      "combat_marksman_carbine_04", "combat_marksman_master", "outdoors_scout_harvest_01",
      "outdoors_scout_movement_01", "science_medic_ability_01", "science_medic_injury_01",
      "science_medic_injury_speed_01", "social_entertainer_dance_01", "combat_brawler_unarmed_01",
      "combat_brawler_1handmelee_01", "combat_brawler_2handmelee_01", "combat_brawler_polearm_01",
      "crafting_artisan_survey_01", "outdoors_scout_harvest_02", "outdoors_scout_movement_02",
      "science_medic_ability_02", "science_medic_injury_02", "science_medic_injury_speed_02",
      "social_entertainer_dance_02", "combat_brawler_unarmed_02", "combat_brawler_1handmelee_02",
      "combat_brawler_2handmelee_02", "combat_brawler_polearm_02", "crafting_artisan_survey_02",
      "outdoors_scout_harvest_03", "science_medic_ability_03", "science_medic_injury_03",
      "social_entertainer_dance_03", "combat_brawler_unarmed_03", "crafting_artisan_business_01",
      "crafting_artisan_domestic_01", "crafting_artisan_engineering_01", "outdoors_scout_camp_01",
      "outdoors_scout_tools_01", "science_medic_crafting_01", "social_entertainer_hairstyle_01",
      "social_entertainer_healing_01", "social_entertainer_music_01", "crafting_artisan_business_02",
      "crafting_artisan_domestic_02", "crafting_artisan_engineering_02", "outdoors_scout_camp_02",
      "outdoors_scout_tools_02", "science_medic_crafting_02", "social_entertainer_hairstyle_02",
      "social_entertainer_healing_02", "social_entertainer_music_02", "combat_brawler_1handmelee_03",
      "combat_brawler_2handmelee_03", "combat_brawler_polearm_03", "crafting_artisan_business_03",
      "crafting_artisan_domestic_03", "crafting_artisan_engineering_03", "crafting_artisan_survey_03",
      "outdoors_scout_movement_03", "science_medic_injury_speed_03", "outdoors_scout_camp_03",
      "outdoors_scout_tools_03", "science_medic_crafting_03", "social_entertainer_hairstyle_03",
      "social_entertainer_healing_03", "social_entertainer_music_03", "combat_brawler_1handmelee_04",
      "combat_brawler_2handmelee_04", "combat_brawler_polearm_04", "combat_brawler_unarmed_04",
      "crafting_artisan_business_04", "crafting_artisan_domestic_04", "crafting_artisan_engineering_04",
      "crafting_artisan_survey_04", "outdoors_scout_harvest_04", "outdoors_scout_movement_04",
      "science_medic_ability_04", "science_medic_injury_04", "science_medic_injury_speed_04",
      "social_entertainer_dance_04", "outdoors_scout_camp_04", "outdoors_scout_tools_04",
      "science_medic_crafting_04", "social_entertainer_hairstyle_04", "social_entertainer_healing_04",
      "social_entertainer_music_04", "combat_brawler_master", "crafting_artisan_master",
      "outdoors_scout_master", "science_medic_master", "social_entertainer_master"
    ]
  }
}
```
