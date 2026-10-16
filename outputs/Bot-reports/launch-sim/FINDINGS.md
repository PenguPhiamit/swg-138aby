# Launch simulation: findings

15 Oct 2026, Claude. Owner: "set the bots up to simulate a brand new galaxy and see how far they can get. only the server bots so we can have max coverage. collect whatever data you think may be relevant to any of our roadmap points."

**What ran:** 1,500 server-side bots (`/botpop launch`, dev `024a4bdc` and `cbb8fc10`). They are brand-new characters spread over the 18 player cities of Tatooine, Corellia, Naboo, Talus and Rori, about 83 per city, in five roles:
- Brawler, Marksman and Scout hunt: wildlife and hostile NPCs at their level, loot (Scouts harvest), rest in town when hurt, widen their ground, move planets when nothing is left.
- Medics heal in town; Entertainers dance.

They train every box the server's rules allow. Credits are counted, not charged. The world is the existing test galaxy, not a wiped one.

| Run | When | Length | What changed |
|---|---|---|---|
| 1 | 17:09–17:27 | 18 min | first try; a combat loop stalled most hunters |
| 2 | 17:33–20:18 | 2 h 46 min | loop fixed |
| 3 | 20:22–21:44 | 79 min | whole skill tree, junk dealer, town crowd, 10 s positions for the map |

Numbers: [run 1](numbers-run1.md), [run 2](numbers-run2.md), [run 3](numbers-run3.md); per-15-minute pacing, outliers and depletion in [analysis.json](analysis.json) (`tools/bots/botpop_analysis.py`). Raw event logs: `/opt/swg/agent/logs/botpop-launch-run{1,2,3}.jsonl` (14, 133, 64 MB). Host samples: `host-*.jsonl` here.

## 1. Capacity (ambient adventurers B3, friends' launch)

- **1,500 bots that each count as a player ("all" mode) ran 2 h 46 min without a crash:** about 8 of 12 cores, ticks 3–4 ms, a few skipped bot passes (48 in run 2, 5 in run 3). This is beyond milestone 1 of `Documentation-support/server-side-bots.md` (1,000 bots for 30 minutes).

| Bots | Cores | Server memory |
|---|---|---|
| 300 | 4.5 | 4.7 GB |
| 1,000 | 7 | 5.4 GB |
| 1,500 | 8 | 5.7 GB at the start |

- **Memory creeps:**
  - run 2: 5.0 → 7.5 GB in 2 h 46 min (about 0.9 GB/h);
  - run 3: 4.7 → 6.9 GB in 79 min (about 1.6 GB/h).

  The cause is not measured yet. The likely candidates are the creatures and lairs that spawn around 1,500 player-like observers as they spread out, and corpses. Measure this before any long live test.
- **A clean shutdown with 1,500 bots online did not finish in time:** the test galaxy was stopped by force. Despawn the bots before stopping (`botpop despawn all`).
- **Server log noise:** the error lines are loot items' missing base templates, about 11,000 lines an hour at this kill rate (for example `retrieve_quest_base.lua`, `loot_base.lua`). They are harmless, but they bury real errors.

## 2. How fast a new character progresses (sandbox XP; the month's pacing)

A first-tier box (`_01`) costs 1,000 XP and a second-tier box (`_02`) 5,000.

| Role | First box (median) | Boxes per bot at 30 min | at 60 min | at 75 min |
|---|---|---|---|---|
| Brawler | 5 min | 2.1 | 3.3 | 3.6 |
| Medic (town crowd) | 23 min | 0.9 | 2.1 | 2.4 |
| Marksman | 19 min | 0.7 | 1.6 | 2.1 |
| Entertainer | 9 min | 1.0 | 2.0 (`dance_02` for all) | 2.0 |
| Scout | 42 min | 0.1 | 0.4 | 0.6 |

- **Unarmed is the fastest way to level:** a median of 18 s per kill, against 32–43 s with any starting weapon (17,800 unarmed kills in run 2). Brawler is therefore the quickest start.
- **Nobody reached a master box, and no bot reached combat level 7.** Median combat levels were 2–3. A run of 4–8 hours (overnight) is needed to see the third and fourth tiers and masters.
- **Scouts stall:** their next boxes need trapping or exploration experience, which the bots can't earn. This is a gap in the bots, not in the game.

## 3. Economy (phase 1 baseline: loot, missions)

- **Hunting earns almost nothing:** 0.3 credits per kill, about 3.7 credits per bot per hour. All 1,500 bots together held 14,854 credits after 2 h 46 min (run 2) and 7,140 after 79 min (run 3).
- **Training would have cost 731,500 credits in run 2 and 945,500 in run 3**, at 250 credits per first-tier box after the sandbox's ×0.25. Only 5 of run 3's 3,280 boxes were affordable when trained.
- **A junk dealer doesn't help:** wildlife drops almost no items (3 sales in run 3).
- **So a new character's money has to come from missions** (the real pre-CU income), from a starting purse, or from cheaper training. The bots don't run missions yet; that is their biggest gap for this question. Owner decision: the starter economy (mission rewards, starting credits, training cost).

## 4. Danger: where new characters die (creature levels and spawns)

About 0.8–1 deaths per bot per hour. Share of fights that end in a death, by planet:

| Planet | Death share |
|---|---|
| Tatooine | 0–2% (the gentle start) |
| Corellia | 2–13% |
| Naboo | 10–19% |
| Rori | 12–21% |
| Talus | Nashal 38%, Dearic 54% |

**Outlier spawns near starting cities:** creatures 8 or more levels above the bot that killed new characters 350–1,000 m from the city. There were 1,011 such deaths in run 2 and 385 in run 3. Worth a spawn review: move them, or keep them as a deliberate warning.

| Creature (level) | Near | Typical distance |
|---|---|---|
| dragonet (29) | Mos Entha, Tatooine | 700–830 m |
| greater desert womp rat (22) | Anchorhead, Tatooine | 490–590 m |
| savage humbaba (24), devil gulginaw (18), foaming vynock (14) | Dearic and Nashal, Talus | 540–710 m |
| spineflap soldier (14), spineflap guard (18) | Moenia, Keren and Kaadara, Naboo | 510–710 m |
| mauler (16), mauler apprentice (12) | Moenia, Keren and Kaadara, Naboo | 600–810 m |
| nightspider poison spitter (11), swamp rat (10) | Restuss, Rori; Moenia and Theed, Naboo | 360–950 m |
| corellian butterfly warrior (14), rogue bageraset (13), noxious vrelt scavenger (10) | Kor Vella and Bela Vistal, Corellia | 550–1,060 m |

- The deadliest creature overall is the nightspider (level 7, Naboo and Rori): 288 deaths in run 2.
- Creatures that attack first: kreetle swarms, howling plumed rasps, nightspider poison spitters, spineflap soldiers.

## 5. Spawn supply around cities (density and respawn)

- **Every city's bots ran out of creatures within 400 m in 5–10 minutes** and had to widen their ground. That is expected with about 83 hunters per city.
- **Kills per 15 minutes held steady** around Kor Vella (about 600), Mos Espa, Bestine and Mos Eisley. The 500 m squares around Kor Vella (-4,000 to -3,500, 2,500 to 3,000) and south of Anchorhead were the busiest hunting grounds, with up to 1,800 kills each.
- **They collapsed elsewhere:**

| City | Kills per 15 min, first → last |
|---|---|
| Coronet | 187 → 20 |
| Kaadara | 448 → 25 |
| Nashal | 154 → 34 |
| Tyrena | 137 → 34 |
| Dearic | 78 → 32 |

  Bots began leaving those planets after 40–60 minutes.
- **For a small friends' launch this does not matter. For hundreds of ambient bots it does:** cap bots per city, raise respawn or density where it collapses, or send ambient bots to wider areas.

## 6. Medics and entertainers (social professions)

- **When hurt hunters, medics and dancers meet in the middle of town,** everyone gains:
  - 2,659 of 2,661 rests watched a dancer (run 2: 319 of 6,311);
  - medics healed 109 times per hour each (run 2: 15) and trained 2.4 boxes in 75 minutes (run 2: 0.66 in 165).
- **Medic progression depends entirely on hurt players coming to them:** a town hub (cantina, hospital) matters for these professions.
- Entertainers reach `dance_02` in about an hour. Their cheapest next box needs image-designer XP, which the bots can't earn, so they slow down after that.

## 7. Travel and coverage (planets, Ossus and Hoth, bots mapping B6)

- **Bots moved planets only because hunting ran dry:** 187 or more moves in run 2, 77 in run 3, mostly away from Corellia, Rori and Talus.
- **No bot reached the combat level (7) for the tier-1 outposts** (Dantooine, Lok, Yavin 4), so Ossus and Hoth were never visited. The progression-based simulation will not map Ossus.
- **Week 2's "bots map Ossus" (B6) needs its own launch spot:** for example `botpop launch N ossus` starting at Knossa. This is a small change.
- **Coverage:** bots stood in about 11,000 of the five planets' 100 m squares (22% of Corellia).

## 8. What the bots don't do yet (so the data is silent on it)

- Missions, crafting (Artisans were left out), surveying, trapping and camps, music, image design.
- Groups.
- Shuttles: a planet move is a jump, not a ticket.
- Buildings and dungeons, factions and PvP, chat.

The first two to add are **missions**, for the economy question, and **a longer overnight run**, for masters and memory.

## Recommendations by roadmap item

1. **Phase 1 baseline / owner decision:** the starter economy (missions, starting credits, training cost). Missions for the server bots next, reusing C9's mission scenario as the reference.
2. **Spawn review:** the outlier spawns in section 4 and the collapsing cities in section 5, as one review item for GPT (data in [analysis.json](analysis.json)).
3. **Ambient adventurers (B3, week 4):** capacity is proven. Before live, measure the memory creep, and decide the mode (throttled for live) and a per-city cap.
4. **Bots map Ossus (B6, week 2):** add a Knossa launch spot.
5. **Operations:** despawn before shutdown; quiet the loot-template log noise.
6. **Next simulation:** missions, then an overnight run of 4–8 hours.
