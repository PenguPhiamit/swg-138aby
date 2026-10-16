# Our cut and custom content, ranked

Claude (Opus 5.5), 16 Oct 2026, taking over the content-design job Fable had queued (owner, 16 Oct). The owner asked
(15 Oct, about 11:00 PM) for "a ranked list of all our cut and custom content, plus a galaxy-wide faction plan with more
than two sides mapped onto Core3". The faction plan is [`../Fable-factions/README.md`](../Fable-factions/README.md).

This is the map the owner picks from, not a design dump. After the owner's pick, the next two or three items are designed
each night in the order they can be built. Nothing counts until it is built and tested.

Research and design only. Nothing under `/opt/swg` was written: the reads were inside WSL, as swgemu, from a script file
in my temp folder. Nothing was built, downloaded or run in a client. The client archives (`SWG-client/*.tre`, 77 files)
were read with `tools/swgfmt` only, and two faction tables were extracted to a temp folder outside the repo.

## How to read it

- **Kind.** *Cut* means it comes from SOE's own client files: never shipped, never finished, or later SOE content that a
  pre-CU galaxy never had. *Custom* means it is ours, or community work we adapt. Its catalogue rating and credit are in
  `source` in `backlog.json`.
- **Size** (Claude's build time; the owner's checks come on top): **S** about a day, **M** 2-3 days, **L** about a week,
  **XL** several weeks.
- **Order.** Value to a small friends' server (1-5) divided by cost (S=1, M=2, L=4, XL=8), plus a bonus for each item it
  unblocks. That gives `score` in the JSON. The rank then puts first what can be built today with no open decision, and
  the owner's approved month route (`SWG-roadmap.md`) breaks ties. The faction foundation has the top score but ranks
  4th, because the owner picks its option first.
- **Every field for every item** (what exists with paths, what it needs by kind, dependencies, decisions made and open)
  is in [`backlog.json`](backlog.json). The tables below are the summary, one row per item.

## In flight, not ranked

These are built and wait in the release lane, not on design:
- **Playable Hutt** (SP-01). The owner is testing it. A crash on the creation screen was fixed at 4:21 PM on 16 Oct
  (h `a07b46e`; archive `6ff21312` on the server and the client). Checklist: `Documentation-support/hutt-c54.md`.
- **World boss rotation and the big game hunter** (FW-06, dev `bda2c0dd`). Waits for review and the owner's OK.

Content that is built with nothing left to do (Hoth v1, Ossus O5, Chiss, Echo Base E0, the six-mission setting, the XP
multipliers, the six Ossus creatures) is not listed.

## Top 15, in order

**1. Ossus O7 build: craters, scorch, glass pan, two settlement fields, 16 places placed** (PL-01; custom, M, staged; era: core: the 130 ABY massacre scars and the 130-139 occupation)
- Exists: Fable-ossus/o6/README.md (design); Fable-ossus/o7-build/ (statics.json 295 objects, terrain.json 14 layers, poi-placements.json, checks; C53 `3f64720`, ALL CHECKS PASS); dev `2ada3784` (O5 first look on the test galaxy).
- Still needs: Lua: none for the statics (all 89 server templates exist in dev); client tables: rebuild ossus.trn and ossus.ws, region labels (stage_env.py), rebuild the archive chain on top of the C54 Hutt archive; testing: owner client visit (craters, three flatland caves, pier, bridge); bot walk of the 16 places.
- Depends on nothing; unblocks PL-02, DR-02, DR-03, PR-02.
- Owner decisions made: craters 2-4 m (floors 2 m for 4 and 5), Westmarch and Knossa Fields only, garrison on the benchland rim guarding the dig, POI 7 held, POI 17 in the foothills (owner 15 Oct 23:15 and 16 Oct 05:40). Open: none before the build; the look after the client visit.
- Why here: Designed, staged, every decision answered: only Claude's build and the owner's look stand between it and done.

**2. Hoth leftovers: the owner's 15 Oct answers** (PL-05; custom, M, answered, not built; era: fair: an Outer Rim world; Echo Base is a 3 ABY ruin)
- Exists: Fable-hoth-batchA/, Fable-hoth-batchB/ (ice-cave den option 1), Fable-hoth-batchC/; dev `c5f1ae06`, `69eb77fe`, `de1b679a`, `dd16bcff`, `54a33063`.
- Still needs: Lua: density 1024; glacial rancor in a fixed den with respawn, pale blue (Chiss palette); quest badge + rare-decor roll; starport artisan and entertainer terminals; camp delivery points and junk dealer; recruiters at the starport only; client tables: mynock ice-cave building + one flatten layer in hoth.trn; map names for areas, camps and dens; testing: GPT's C23 Hoth acceptance; owner look at the den.
- Depends on nothing; unblocks DR-01, FW-05.
- Owner decisions made: all of Q4 (15 Oct 15:30-16:10) and the ice-cave den (14 Oct set, Q9 option 1). Open: none.
- Why here: Fully answered and cheap; closes Hoth's content for the release gate (C24).

**3. Nal Hutta first look (Bilbousa)** (PL-03; custom, S, designed; era: good: the kajidics' council world, unchanged through Krayt's years)
- Exists: terrain/hutta.trn and snapshot/hutta.ws in SWG-client/mtg_planets.tre (verified today); Fable-species/s7-hutt/README.md section 8 (first-look steps); planet CRC rows hutta/nalhutta already in the installed table.
- Still needs: Lua: zone on the test galaxy, planet_manager block (GCW off), hutta_regions.lua (edge strips, Bilbousa CITY+NOSPAWN); client tables: hutta_region_names.stf, planet name, travel rows (Tatooine <-> Nal Hutta), loading strings, credit line; testing: owner lands and walks Bilbousa.
- Depends on nothing; unblocks PL-04.
- Owner decisions made: first look in the same restart as the Hutt check (owner 15 Oct 23:15); not built yet. Open: fares and route.
- Why here: Owner asked for it with the Hutt check; small; gives the Hutt and the cartel faction a home.

**4. Faction foundation (Option A): era meaning for the two GCW sides and seven NPC standing factions** (FW-01; custom, M, designed in outline; era: core)
- Exists: Fable-factions/README.md; Core3 loads scripts/custom_scripts/managers/faction_manager.lua after the stock file (absent today); local_planets.tre already ships a 95-key faction name table.
- Still needs: design: the exact table, standing sources and rewards; Lua: one data file plus standing gates in screenplays; client tables: faction name rows; optional relabel of the GCW names; testing: bot kill checks standing deltas; -3000/+3000 aggression; vendor gate.
- Depends on nothing; unblocks PL-02, PL-04, DR-01, DR-03, FW-05, FW-02.
- Owner decisions made: none recorded. Open: the option and the questions at the end of Fable-factions/README.md.
- Why here: Unblocks six items and is mostly data in our own file.

**5. Ossus people: NPCs, conversations and first missions at the places** (PL-02; custom, L, designed in outline; era: core)
- Exists: Fable-ossus/o7-build/poi-placements.json (npc_points with stock mobile candidates); Fable-ossus/inspiration.md, Fable-ossus/o6/README.md section 3; Local-model-ossus-npcs/ (local model drafts, unreviewed).
- Still needs: design: rosters, dialogue, standing gates, 3-5 starter missions (Ysanna highland hunt, the pilot's part errand, the memorial-road walk and badge); art: none (stock bodies; Sith troopers as hued stock troopers); Lua: mobiles with the new faction strings, one screenplay per place, conversations; client tables: our strings, one badge row; testing: bots visit each place; standing deltas; owner visit.
- Depends on PL-01, FW-01; unblocks DR-02, DR-03, CR-02.
- Owner decisions made: Imperial (Krayt) garrison yes; rare hidden Jedi met in the sanctuary under the ruins (owner 15 Oct 14:24). Open: what meeting a hidden Jedi gives a player; whether hidden Jedi can be attacked.
- Why here: Turns the built planet into a place with sides; needs the faction foundation (rank 4) first.

**6. Nautolan and Togruta, plus Chiss name tables and a real Chiss profile** (SP-02; custom, S, staged; era: good)
- Exists: Fable-species/s6/ (patch, provenance, archive on the old chain); dev has no chiss.lua name table yet (checked today).
- Still needs: design: name tables and attribute profiles for three species; Lua: re-base the S6 patch on today's dev; client tables: rebuild the archive chain; testing: owner creates each.
- Depends on SP-01; unblocks SP-03.
- Owner decisions made: order Chiss, Nautolan, Togruta, then Hutt; our own name tables and real profiles (owner 14 Oct). Open: none.
- Why here: Staged and cheap; finishes what the owner already ordered.

**7. Resource follow-ups and consumers (all answered)** (PR-01; custom, S, answered, not built; era: good)
- Exists: Fable-resources3/lore/lore-materials.md; Fable-resources3/names/README.md.
- Still needs: design: recipe stats for lumni-spice; the GemDiver trader's stock; Lua: adegan tiers, Ossus solar PE 500-1000, flora names, Smuggler lumni-spice schematic, corusca trader on Yavin 4; client tables: resource names; testing: survey, craft, buy.
- Depends on nothing; unblocks DR-03.
- Owner decisions made: real adegan tiers; flora names yes; solar PE 500-1000; lumni-spice recipe; corusca from a trader; beskar waits for Mandalore (15 Oct). Open: none.
- Why here: Five answered changes in one small batch.

**8. Client patch kit for friends (local_planets.tre delivery and rollback)** (QL-01; custom, M, partial; era: n/a)
- Exists: Fable-live-client/README.md; roadmap week 2: a release blocker.
- Still needs: client tables: installer, version check, rollback; testing: a friend's PC.
- Depends on nothing; unblocks nothing listed.
- Owner decisions made: none recorded. Open: how friends get it.
- Why here: Without it no friend sees any custom planet or species; needed before the friends' playtest (route week 4).

**9. Photo studio on an SOE test terrain** (PL-07; cut, M, designed; era: n/a (test galaxy only))
- Exists: Fable-studio/README.md (design; the four terrains read from data_other_00); Core3 lists the test zones commented out in config.lua.
- Still needs: Lua: test-only zone, no spawns, fixed noon, clear weather; client tables: planet CRC row, a shader family (none of the four has one), environment row; testing: one standard shot set with Universal Modder.
- Depends on nothing; unblocks SP-03, SP-04, HC-06.
- Owner decisions made: approved for week 2 (owner 15 Oct). Open: which terrain (Fable leaned to a fixed one; Claude picks).
- Why here: Every species, gear and prop review after this gets a repeatable picture.

**10. Echo Base E1-E5: shell, outside, inside, missions, names** (DR-01; cut, L, E0 built; era: fair: a 3 ABY ruin reused)
- Exists: dev `8f2072e7` (E0); Fable-echo-base/README.md; Fable-hoth-guide/echo-base-plan.md; Owner-test-list.md item 4.
- Still needs: design: story: who holds it (Fable-factions proposes a Triumvirate relay under holdout attack); Lua: rooms roster, elevators, missions; client tables: names; testing: owner's E0 look first; bots inside 33 cells.
- Depends on PL-05, FW-01; unblocks FW-05.
- Owner decisions made: none recorded. Open: E0 result; who holds it; a GCW HQ at the base or not.
- Why here: Hoth's big set piece; waits on the owner's E0 look.

**11. Collections first: Ossus lost-library fragments and the memorial road, plus the backport loot wiring** (PR-02; custom, M, answered; era: good)
- Exists: Fable-backport/README.md section 8; Fable-ossus/o6/README.md POIs 4 and 12.
- Still needs: design: the collection list; C++: maybe collection plumbing; Lua: collection items, loot groups (NGE junk and collection loot), 13 wearables for new species; client tables: collection strings; testing: bots collect; owner.
- Depends on PL-01; unblocks nothing listed.
- Owner decisions made: collections first (14 Oct set Q4); wire NGE junk and collection loot; extend the 13 wearables (Q6). Open: none.
- Why here: First clean-room system the owner chose, with Ossus as its first set.

**12. Crew vendor: hire an escort crew** (QL-02; custom, M, escort built; era: fine (Mandalorian and cartel hirelings fit 138 ABY))
- Exists: tools/bots/escort.py, scenarios/forn-escort.py; Dax Venn broker (live) as the model.
- Still needs: design: vendor, prices, limits; C++: maybe; Lua: vendor NPC; testing: owner runs a dungeon with a crew.
- Depends on nothing; unblocks nothing listed.
- Owner decisions made: owner 15 Oct: escort leads into the crew vendor and solo features. Open: none.
- Why here: Biggest solo-play win for a small server.

**13. Krayt raid 'Nihl's Hold' with the Echo of Krayt secret boss** (DR-03; custom, L, draft; era: excellent: Nihl in 138-139; the Echo is our invention)
- Exists: Documentation-support/krayt-raid-design.md; Ossus POI 14 Sith post as the lead-in.
- Still needs: design: finish the draft (owner questions 1-5); art: hued stock bodies first; C++: maybe phase logic helpers; Lua: templates, phases, key, loot, yorik coral class; client tables: loot names; testing: bots fight it; Doctors cure the DoT.
- Depends on FW-01, PL-02; unblocks FW-04.
- Owner decisions made: make Krayt a raid boss, main boss a successor, secret boss behind a loot key (owner 14-15 Oct). Open: location, key, size, mechanics (draft section 7).
- Why here: The owner's endgame ask; interim on Ossus keeps it cheap.

**14. Species wave 2: Bith, Gran, Devaronian, Weequay, Nikto, Aqualish, Quarren, Ishi Tib, Gotal, Talz (+ Nightsister and Singing Mountain witch options)** (SP-03; custom, M, in client; era: good (galaxy-wide species))
- Exists: player templates in mtg_patch_023 (verified today); Content-catalogue/newspecies-original.zip.
- Still needs: design: names and profiles per species; Lua: races, creation, ID tables; client tables: creation tables; testing: owner creates each; clothing checks.
- Depends on SP-02, PL-07; unblocks nothing listed.
- Owner decisions made: no hybrid species until all regular species are in (owner 14 Oct). Open: order.
- Why here: Big creation-screen variety for little cost once S6 proves the method.

**15. Battlefront-style Hoth conquest pilot (PvE first)** (FW-05; custom, L, designed; era: good: Triumvirate vs holdouts on Hoth)
- Exists: Documentation-support/bf2-battles-and-ai-for-swg.md.
- Still needs: design: sides from FW-01; C++: match controller, scoped attackability, AI goal adapter; Lua: screenplay, posts; testing: bot-only matches, then the owner.
- Depends on FW-01, PL-05, DR-01; unblocks FW-02.
- Owner decisions made: Battlefront-style battles in week 4 (owner 15 Oct). Open: none.
- Why here: Owner's week-4 item and the first place the faction plan becomes a fight.

## The three I would design next

Items 1-3 are already designed (Ossus O7 is staged, the Hoth answers are complete, Nal Hutta's first-look steps are in
S7 section 8), so they need only Claude's build. The next design work is therefore items 4-6:

1. **The faction foundation's data (FW-01)**, if the owner picks Option A in the faction plan. It covers the exact table
   (keys, enemies, allies, adjust factors), where standing comes from and what it opens, and the strings. Every later
   Ossus, Nal Hutta, Echo Base and raid item reads from it.
2. **Ossus people (PL-02).** Rosters, conversations, the first three to five missions, and the standing gates at the
   garrison, the sanctuary, the Ysanna camp and stone circle, the hamlet, the adit and the Hutt field. It uses item 1 and
   fills the places O7 builds.
3. **Species facts for Nautolan, Togruta and Chiss (SP-02).** Our own name tables and real attribute profiles, which the
   owner asked for on 14 Oct and which Chiss still lacks (dev has no `chiss.lua` name table). With them, the staged S6
   patch can be rebased and built.

## Questions for the owner (this list)

1. **The order.** Build 1-3 now and design 4-6 next, as above? *Default: Claude does this unless you object.*
2. **The third planet** (route, week 3). Kashyyyk (cheapest: terrain, buildings and 338 creatures already in the client),
   Mustafar, or a clean-room Nar Shaddaa or Taris after the Dantooine pilot? *Recommended: Kashyyyk first, Nar Shaddaa
   later as the cartel city. Default: Kashyyyk.*
3. **The decor packs** (HC-04). They are rated P with credit, but their author also made the D20 RP total conversion you
   excluded. The packs are separate releases. Use them? *Recommended: yes, with credit. Default: held until you say yes.*

## All items by theme

### Planets

| # | Item | Kind | Size | Status: what exists | Still needs | Era fit | Depends on | Why this place |
|---|---|---|---|---|---|---|---|---|
| 1 | **Ossus O7 build: craters, scorch, glass pan, two settlement fields, 16 places placed** (PL-01) | custom | M | staged: Fable-ossus/o6/README.md (design) (+2 more) | client tables, testing | core: the 130 ABY massacre scars and the 130-139 occupation | - | Designed, staged, every decision answered: only Claude's build and the owner's look stand between it and done. |
| 2 | **Hoth leftovers: the owner's 15 Oct answers** (PL-05) | custom | M | answered, not built: Fable-hoth-batchA/, Fable-hoth-batchB/ (ice-cave den option 1), Fable-hoth-batchC/ (+1 more) | Lua, client tables, testing | fair: an Outer Rim world; Echo Base is a 3 ABY ruin | - | Fully answered and cheap; closes Hoth's content for the release gate (C24). |
| 3 | **Nal Hutta first look (Bilbousa)** (PL-03) | custom | S | designed: terrain/hutta.trn and snapshot/hutta.ws in SWG-client/mtg_planets.tre (verified today) (+2 more) | Lua, client tables, testing | good: the kajidics' council world, unchanged through Krayt's years | - | Owner asked for it with the Hutt check; small; gives the Hutt and the cartel faction a home. |
| 5 | **Ossus people: NPCs, conversations and first missions at the places** (PL-02) | custom | L | designed in outline: Fable-ossus/o7-build/poi-placements.json (npc_points with stock mobile candidates) (+2 more) | design, Lua, client tables, testing | core | PL-01, FW-01 | Turns the built planet into a place with sides; needs the faction foundation (rank 4) first. |
| 9 | **Photo studio on an SOE test terrain** (PL-07) | cut | M | designed: Fable-studio/README.md (design; the four terrains read from data_other_00) (+1 more) | Lua, client tables, testing | n/a (test galaxy only) | - | Every species, gear and prop review after this gets a repeatable picture. |
| 16 | **Dantooine Jedi Enclave ruins (clean-room pilot)** (PL-08) | custom | L | approved, not designed: owner 15 Oct: pilot before a KOTOR clean-room planet (+1 more) | design, art, Lua, client tables, testing | good: an ancient ruin in 138 ABY | - | Owner's week-3 pilot; proves the clean-room method before a whole planet. |
| 17 | **Nal Hutta as the Hutt home: palatial Bilbousa, kajidic seats, Hutt vendors, smuggler terminals, swamp spawns** (PL-04) | custom | L | idea: Fable-species/s7-hutt/README.md sections 1 and 8 (concept) | design, art, Lua, client tables, testing | good | PL-03, FW-01 | The playable Hutt's reason to go home; after the first look proves the planet. |
| 20 | **Third planet through the playbook: Kashyyyk** (PL-09) | cut | L | assets in client: MTG kashyyyk.trn + 7 sub-terrains and snapshots (verified today) (+1 more) | design, Lua, client tables, testing | good (the Wookiee homeworld; check its Legacy status) | PL-01, PL-03 | Cheapest third planet: terrain, buildings and mobiles already exist. |
| 23 | **Galactic map rework: planets where they really are** (PL-20) | custom | M | researched: Documentation-support/planets-lore-and-coordinates.md and .json (C14) (+1 more) | design, art, Lua, client tables, testing | n/a | - | Owner asked; do it once the planet list settles. |
| 30 | **Korriban (Moraband)** (PL-11) | custom | L | assets in client: MTG moraband.trn and snapshot | design, Lua, client tables, testing | good: Krayt's stasis room is canon here | FW-01 | Best long-term home for the One Sith and raid option B. |
| 31 | **Mandalore** (PL-12) | custom | L | assets in client: MTG mandalore.trn and snapshot | design, Lua, client tables, testing | good: Mandalorian clans as mercenaries | FW-01 | Unlocks beskar and the Mandalorian standing line. |
| 40 | **Mustafar** (PL-10) | cut | L | assets in client: MTG mustafar.trn and snapshots (+1 more) | design, Lua, client tables, testing | fair (a mining world) | PL-09 | Second expansion world once the playbook is quick. |
| 43 | **Nar Shaddaa (clean room)** (PL-19) | custom | XL | idea: owner 15 Oct: Nar Shaddaa or Taris after the Dantooine pilot | design, art, Lua, client tables, testing | excellent: the Hutts' open market by 130 ABY (Legends) | PL-08, FW-01 | Best cartel planet, but a whole city to build. |
| 44 | **Coruscant** (PL-15) | custom | XL | assets in client: MTG coruscant.trn and snapshot | design, art, Lua, client tables, testing | excellent: the Triumvirate's capital, rebuilding after 138 | FW-01 | Right place, wrong cost: sparse terrain needs a city built. |
| 45 | **Taanab** (PL-13) | cut | L | assets in client: terrain/taanab.trn in data_other_00 and MTG (+1 more) | design, Lua, client tables, testing | good (an agricultural world) | PR-07 | SOE's own unfinished world; best paired with farming. |
| 54 | **Dromund Kaas** (PL-14) | custom | L | assets in client: MTG kaas.trn and snapshot | design, Lua, client tables, testing | fair (Sith relics) | FW-01 | Overlaps Korriban; later. |
| 62 | **Zeltros** (PL-18) | custom | M | downloaded, not installed: Content-catalogue/zeltros_client.zip, zeltros_server.zip | Lua, testing | fair | - | Exploration-only world under a non-commercial licence. |
| 63 | **Chandrila** (PL-16) | custom | L | assets in client: MTG chandrila.trn and snapshot | Lua, client tables, testing | fair | - | Little story pull in 138-139. |
| 67 | **Space stations (Tansarii Point; the others)** (PL-06) | cut | L | rights unclear: Content-catalogue/SWG-content-catalogue.md, stations rows | nothing new | fair | - | Rights and availability unresolved. |
| 68 | **Jakku** (PL-17) | custom | L | assets in client: MTG jakku.trn and snapshot | Lua, client tables, testing | weak (almost no Legends presence) | - | Weak era fit. |
| 71 | **SOE developer terrains and Otoh Gunga** (PL-21) | cut | XL | in client: umbra, 09, 10, 11, rivertest, floratest, watertabletest, godclient_test, cinco_city_test_m5, runtimerules, an Endor dev terrain, otoh_gunga (all verified today) | nothing new | n/a | - | Test data, not places; only the studio (PL-07) uses one. |

### Species

| # | Item | Kind | Size | Status: what exists | Still needs | Era fit | Depends on | Why this place |
|---|---|---|---|---|---|---|---|---|
| 6 | **Nautolan and Togruta, plus Chiss name tables and a real Chiss profile** (SP-02) | custom | S | staged: Fable-species/s6/ (patch, provenance, archive on the old chain) (+1 more) | design, Lua, client tables, testing | good | SP-01 | Staged and cheap; finishes what the owner already ordered. |
| 14 | **Species wave 2: Bith, Gran, Devaronian, Weequay, Nikto, Aqualish, Quarren, Ishi Tib, Gotal, Talz (+ Nightsister and Singing Mountain witch options)** (SP-03) | custom | M | in client: player templates in mtg_patch_023 (verified today) (+1 more) | design, Lua, client tables, testing | good (galaxy-wide species) | SP-02, PL-07 | Big creation-screen variety for little cost once S6 proves the method. |
| 21 | **Hutt gear (level 2): ten items rigged to hutt.skt** (SP-04) | custom | L | designed: Fable-species/s7-hutt/README.md section 3 | art, Lua, client tables, testing | good | SP-01, PL-07 | Gives Hutt players something to wear; art-heavy. |
| 46 | **Hutt animations (level 3) and a working .ans exporter** (SP-05) | custom | XL | designed: Fable-species/s7-hutt/README.md section 4; export_ans.py stub in the add-on | art, client tables, testing | good | SP-04 | Unlocks chairs and mounts for Hutts and new creature moves; hardest art. |
| 69 | **Zeltron** (SP-06) | custom | M | held by the owner: Fable-species/README.md S1 | nothing new | good | - | Held. |
| 70 | **Thirteen species only another server ever made playable (Cerean, Duros, Kel Dor, Mirialan and others)** (SP-07) | custom | L | blocked: Content-catalogue/SWG-content-catalogue.md species rows | nothing new | good | - | Blocked on rights. |
| in flight | **Playable Hutt (finish: restart, owner's floater checks, fixes)** (SP-01) | custom | S | built; the owner is testing it: Fable-species/s7-hutt/ (+3 more) | testing | good | - | In flight: integration lane, not new design. |

### Factions and war

| # | Item | Kind | Size | Status: what exists | Still needs | Era fit | Depends on | Why this place |
|---|---|---|---|---|---|---|---|---|
| 4 | **Faction foundation (Option A): era meaning for the two GCW sides and seven NPC standing factions** (FW-01) | custom | M | designed in outline: Fable-factions/README.md (+2 more) | design, Lua, client tables, testing | core | - | Unblocks six items and is mostly data in our own file. |
| 15 | **Battlefront-style Hoth conquest pilot (PvE first)** (FW-05) | custom | L | designed: Documentation-support/bf2-battles-and-ai-for-swg.md | design, C++, Lua, testing | good: Triumvirate vs holdouts on Hoth | FW-01, PL-05, DR-01 | Owner's week-4 item and the first place the faction plan becomes a fight. |
| 34 | **Contested zones and guild-war allegiances (Option B pieces)** (FW-02) | custom | M | idea: Core3: PVPAREA region flag, guild wars, duels and bounty TEFs (read today) | design, C++, Lua, testing | good | FW-01 | Three-way fights without new faction code, once there are players to fight. |
| 35 | **Darth Wredd's insurgency: Sith hunting Sith (139 ABY world event)** (FW-04) | custom | M | idea: Fable-factions/README.md (Legends check) | design, Lua, client tables, testing | excellent (139 ABY) | FW-01, DR-03 | A server event that moves the year forward when the owner wants. |
| 55 | **Covert detector (GCW base perk) check** (FW-07) | cut | S | in client: object/installation/faction_perk/covert_detector/shared_detector_base.iff (dormant) (+1 more) | testing | fine | - | Probably already works; a check, not a build. |
| 61 | **A third GCW banner (Option C)** (FW-03) | custom | XL | idea: Fable-factions/README.md, Option C | design, art, C++, Lua, client tables, testing | good | FW-01, FW-02 | True three-way PvP; large and risky for a handful of friends. |
| in flight | **World boss rotation and the big game hunter** (FW-06) | custom | S | built, waiting for review and OK: dev `bda2c0dd` | testing | fine | - | In flight: release lane. |

### Creatures

| # | Item | Kind | Size | Status: what exists | Still needs | Era fit | Depends on | Why this place |
|---|---|---|---|---|---|---|---|---|
| 19 | **Tames discussion: rare and endgame pets, wild vs BE, control budget** (CR-03) | custom | S | open discussion: Agent/to-claude.md (owner asked to discuss tames) (+1 more) | design | n/a | - | Cheap and unblocks the voxyn line. |
| 26 | **Tauntaun riding (its own test batch)** (CR-01) | custom | M | answered: Fable-hoth-batchC/README.md Q5 (+1 more) | Lua, client tables, testing | good | PL-05 | Fun on Hoth; separate risk from the rest. |
| 29 | **Voxyn tame line grown by Nei Rin's Shapers, and the Vong project fields (Ossus POI 7)** (CR-02) | custom | L | decided, not designed: Documentation-support/starcraft-inspiration-vong-gree.md (art direction) (+1 more) | design, art, Lua, client tables, testing | invented, flagged as such | PL-02, CR-03 | Owner wants it; waits on the tames talk. |
| 48 | **Ossus native fauna wave 2** (CR-04) | custom | M | idea: dev `80b66e65` (six reviewed creatures) | design, art, Lua, client tables, testing | core | PL-01 | After the people; levels are shelved. |
| 50 | **Morag encounter (Endor)** (CR-05) | cut | M | in client: SWG-feature-register.md F58 | design, Lua, testing | fine | - | Small cut-content restoration on a stock planet. |
| 65 | **Legends oddities: Killik hive, Starweird anomaly** (CR-06) | custom | L | ideas on file: Documentation-support/starcraft-inspiration-vong-gree.md | design, art | good (Killiks still exist in 138 ABY; check) | - | Ideas only. |

### Dungeons and raids

| # | Item | Kind | Size | Status: what exists | Still needs | Era fit | Depends on | Why this place |
|---|---|---|---|---|---|---|---|---|
| 10 | **Echo Base E1-E5: shell, outside, inside, missions, names** (DR-01) | cut | L | E0 built: dev `8f2072e7` (E0) (+3 more) | design, Lua, client tables, testing | fair: a 3 ABY ruin reused | PL-05, FW-01 | Hoth's big set piece; waits on the owner's E0 look. |
| 13 | **Krayt raid 'Nihl's Hold' with the Echo of Krayt secret boss** (DR-03) | custom | L | draft: Documentation-support/krayt-raid-design.md (+1 more) | design, art, C++, Lua, client tables, testing | excellent: Nihl in 138-139; the Echo is our invention | FW-01, PL-02 | The owner's endgame ask; interim on Ossus keeps it cheap. |
| 22 | **Ossus vaults and the Jedi path: pilgrimage stones to the sanctuary, the library vault** (DR-02) | custom | M | idea: Fable-ossus/inspiration.md section 5 (+1 more) | design, Lua, client tables, testing | core (Nei Rin kept Jedi relics under the temple, 130-137 ABY) | PL-02 | The Jedi thread of Ossus; after the people exist. |
| 37 | **Hoth wampa bosses: per-player reward** (DR-05) | custom | S | answered: later: Fable-hoth-caves/README.md | design, Lua, testing | fine | PL-05 | Owner said later. |
| 51 | **Old-AI dungeon and event ports** (DR-04) | custom | L | researched: SWG-feature-register.md F44 | Lua, testing | mixed | - | Module by module, after our own content. |
| 60 | **Zonama Sekot rotating raid** (DR-07) | custom | XL | idea: SWG-feature-register.md F94 | design, art, Lua, client tables, testing | good | DR-03 | Big; after the first raid. |
| 66 | **Damutek dungeon (Vong)** (DR-06) | custom | L | parked by the owner: Documentation-support/starcraft-inspiration-vong-gree.md | nothing new | good | CR-02 | Parked. |

### Professions and crafting

| # | Item | Kind | Size | Status: what exists | Still needs | Era fit | Depends on | Why this place |
|---|---|---|---|---|---|---|---|---|
| 7 | **Resource follow-ups and consumers (all answered)** (PR-01) | custom | S | answered, not built: Fable-resources3/lore/lore-materials.md (+1 more) | design, Lua, client tables, testing | good | - | Five answered changes in one small batch. |
| 11 | **Collections first: Ossus lost-library fragments and the memorial road, plus the backport loot wiring** (PR-02) | custom | M | answered: Fable-backport/README.md section 8 (+1 more) | design, C++, Lua, client tables, testing | good | PL-01 | First clean-room system the owner chose, with Ossus as its first set. |
| 24 | **Resource and recipe board terminal** (PR-04) | custom | M | idea: SWG-feature-register.md F38 | design, Lua, testing | n/a | - | Helps every crafter on a small server. |
| 41 | **Five new professions from the owner's book, Archaeologist first** (PR-05) | custom | XL | mapped: Content-catalogue/owner-SWG-SW5E/README.md | design, art, C++, Lua, client tables, testing | good (Archaeologist fits the Ossus dig) | PR-02 | Large; Archaeologist pairs with the library collection. |
| 42 | **Farming: a planter, plus SOE's cut crop containers and flora components** (PR-07) | cut | L | in client / researched: Content-catalogue/dormant-client-objects.md (38 resource containers, chemistry components) (+1 more) | design, art, C++, Lua, client tables, testing | good | PR-05 | SOE left crop containers behind; farming gives them a use. |
| 47 | **New materials and consumables from the owner's book** (PR-06) | custom | L | mapped: SWG-feature-register.md F88-F89 | Lua, client tables, testing | good | PR-05 | Only worth it with the professions that use them. |
| 49 | **Chef and BE cut components, clothing and hair dyes** (PR-08) | cut | M | in client: Content-catalogue/dormant-client-objects.md (food bases, bio food components, dye_clothing, dye_hair) | design, Lua, testing | fine | - | Real cut items; check they are not aliases first. |
| 52 | **Official cut designs: player contracts, crafter usage XP, theatre** (PR-10) | cut | L | researched: Documentation-support/SWG-official-plans-cut-content-and-backports.md | design, C++, Lua | n/a | - | Interesting systems, none started. |
| 56 | **JTL cut components: mass reduction kits, retro thrusters, TIE and Z-95 reactors** (PR-03) | cut | M | in client: Content-catalogue/dormant-client-objects.md | Lua, testing | fine | - | Needs JTL acceptance first. |
| 59 | **Darksaber and Ghostfire sabers** (PR-09) | custom | L | researched: Documentation-support/darksaber-ghostfire-feasibility.md | art, client tables, testing | fair (a Mandalorian heirloom) | PL-12 | Art risk and rights gates. |

### Housing and cities

| # | Item | Kind | Size | Status: what exists | Still needs | Era fit | Depends on | Why this place |
|---|---|---|---|---|---|---|---|---|
| 18 | **City fixes from the owner's answers: Clone Lab, Entertainment District, 30 decorations per rank, no decoration upkeep, 10 event props, era names** (HC-01) | custom | M | answered: Documentation-support/player-cities-research.md (+1 more) | C++, Lua, testing | n/a | - | Makes cities worth founding for friends. |
| 27 | **Bot cities M1: one disposable town** (HC-02) | custom | L | planned: Documentation-support/bot-cities-plan.md | C++, testing | n/a | HC-01 | Living towns, but a test feature first. |
| 28 | **SOE's cut city building styles: Corellia, Naboo and Tatooine banks, capitols, cloners, hospitals, theatres** (HC-03) | cut | M | in client: Content-catalogue/dormant-client-objects.md (SOE examples) | Lua, testing | fine | HC-01 | Real cut content: city buildings that look local. |
| 38 | **Decor packs rated P (torch, kitchen, wall, Naboo structure, lamp; light megapack after a redistribution check)** (HC-04) | custom | M | downloaded: Content-catalogue/*.zip (inspected, not installed) | Lua, client tables, testing | fine | - | Decor for houses; one owner check first. |
| 39 | **A landed freighter you can walk into (SOE's cut test_falcon building)** (HC-06) | cut | S | in client: object/building/general/shared_test_falcon.iff, appearance/thm_all_test_falcon.pob (patch_05, verified today) | design, Lua, testing | good as a generic freighter (not the Falcon itself) | PL-07 | A fun cut interior for little work. |
| 57 | **Monthly Home Show / Best Dressed City** (HC-05) | custom | S | answered: Documentation-support/bot-cities-plan.md | design | n/a | HC-01 | Needs players first. |
| 64 | **Kajidic palaces as player-city sites on Nal Hutta** (HC-07) | custom | L | idea: Fable-species/s7-hutt/README.md section 1 | nothing new | good | PL-04, HC-01 | Much later. |

### Quality of life

| # | Item | Kind | Size | Status: what exists | Still needs | Era fit | Depends on | Why this place |
|---|---|---|---|---|---|---|---|---|
| 8 | **Client patch kit for friends (local_planets.tre delivery and rollback)** (QL-01) | custom | M | partial: Fable-live-client/README.md (+1 more) | client tables, testing | n/a | - | Without it no friend sees any custom planet or species; needed before the friends' playtest (route week 4). |
| 12 | **Crew vendor: hire an escort crew** (QL-02) | custom | M | escort built: tools/bots/escort.py, scenarios/forn-escort.py (+1 more) | design, C++, Lua, testing | fine (Mandalorian and cartel hirelings fit 138 ABY) | - | Biggest solo-play win for a small server. |
| 25 | **Ambient adventurers v1** (QL-03) | custom | L | planned: SWG-roadmap.md Phase 6 | Lua, testing | n/a | - | Makes towns feel lived in. |
| 32 | **POI waypoints and vendor/bazaar search waypoints** (QL-05) | custom | M | idea: SWG-feature-register.md | Lua | n/a | - | Quality of life on stock planets. |
| 33 | **Read-only TRE v6 reader for the disc's later patches** (QL-07) | custom | M | answered: Fable-backport/README.md section 8 Q4 | client tables, testing | n/a | - | Opens patches 18-33 to clean-room backports. |
| 36 | **HoloNet terminal with Triumvirate bulletins** (QL-04) | custom | S | idea: SWG-feature-register.md F41, F74 | design, Lua | good | FW-01 | Cheap way to tell the era's story. |
| 53 | **Multi-passenger vehicles** (QL-06) | custom | M | downloaded: Content-catalogue/multipassenger.zip | C++, client tables, testing | fine | - | Fun with friends; needs a port. |
| 58 | **Owner developer datapad** (QL-08) | custom | M | idea: SWG-feature-register.md F37 | Lua | n/a | - | Staff tool; nice, not urgent. |

## What the client holds that never shipped (survey, 16 Oct)

I indexed all 77 client archives with `tools/swgfmt`: 202,978 distinct entry names. Counts are file definitions, not
finished features.

- **Terrains.** The stock client has SOE's test terrains (`09`, `10`, `11`, `character_farm`, `simple`, `creature_test`,
  `test_wearables`, `floratest`, `rivertest`, `watertabletest`, `godclient_test`, `cinco_city_test_m5`, `runtimerules`
  and a developer's Endor test). It also has three unfinished worlds: `taanab.trn` (62.5 KB, also restored by MTG),
  `otoh_gunga.trn` (11.8 KB) and `umbra.trn` (1.5 KB). MTG adds Hoth, Nal Hutta (`hutta`), Dromund Kaas, Mandalore,
  Korriban (`moraband`), Chandrila, Coruscant, Jakku, Mustafar, Kashyyyk with seven sub-terrains, and `dungeon2`. Our
  `local_planets.tre` adds `ossus`.
- **Objects.** `Content-catalogue/dormant-client-objects.md` lists 131 SOE object definitions with no server template:
  - 15 player-city buildings in Corellia, Naboo and Tatooine styles (HC-03);
  - 38 resource containers, including crops: corn, wheat, rice, oats, beans, tubers, fruit and vegetables (PR-07);
  - Chef and BE food components, clothing and hair dyes, and flora chemistry parts (PR-07, PR-08);
  - JTL kits and reactors (PR-03);
  - a covert detector base (FW-07);
  - a walk-in freighter test building (HC-06);
  - a painting schematic.

  It lists 13,496 MTG-only definitions too, mostly later SOE content: 1,834 mobiles, 644 collection items, 338 Kashyyyk
  and Mustafar mobiles, 379 trading-card items and 222 Storyteller props.
- **Species.** There are 40 player templates. Twenty are stock (the ten original species, both genders). The other twenty
  come from the MTG species package: Aqualish, Bith, Chiss and Hutt in both genders; Devaronian, Gotal, Gran, Ishi Tib,
  Nautolan, Nikto, Quarren, Talz and Weequay male; Togruta, the Nightsister and the Singing Mountain witch female.
- **Factions.** The stock client names 78 NPC factions. Our `local_planets.tre` already ships a 95-name merged table, so
  new factions are new rows there (the faction plan).
- **Not usable without permission.** These catalogue A, U and X rows are listed as blocked and never imported: another
  server's planets and stations, another server's species art, and two scripts marked proprietary.

## Rules this list keeps

- No player cities on Hoth or Ossus, and no terrain edits for founding sites (owner, 16 Oct, Q9 and Q10). The Ossus
  fields are for houses.
- Sentinel's Republic and the D20 RP total conversion are excluded. No SWG Legends or SWG Restoration pages are cited
  (owner, 16 Oct, Q13).
- No hybrid species until all the regular species are in. Zeltron is held.
- Stock or catalogue-approved art only. Clean-room places use public descriptions and SWG's own art, never KOTOR's or
  StarCraft's files.
- Creature levels: Hoth keeps its endgame levels; Ossus keeps 6-19 (the ladder is shelved).
- Community planets keep the creator credit their catalogue row asks for (Nal Hutta, Kashyyyk and the rest) before
  anything leaves this PC.

## Checked, and not checked

Checked today:
- the archive index and the terrain, snapshot and player-template lists (`tools/swgfmt`);
- the faction tables (`datatables/player/pvp_factions.iff`, `datatables/faction/rank.iff`, `faction_names.stf`),
  extracted to a temp folder;
- Core3-dev read-only at `a8ece12b`: the faction manager, the name tables and the dev log, to see what is built (Nal Hutta
  and S6 are not; the Hoth answers of 15 Oct are not).

Not checked:
- anything in a client or on a galaxy;
- whether the dormant objects are aliases of live ones;
- per-file rights beyond the catalogue's rows.

Sizes and values are my estimates.
