# Pre-CU profession reference (what shipped, what was planned, what "complete" means)

Scope: live SWG up to the last pre-Combat-Upgrade build. Publish 14.1 went live on 24 Mar 2005, with hotfixes until 18 Apr 2005. The CU (Publish 15) went live on 27 Apr 2005. SWGEmu also targets 14.1. Jump to Lightspeed (JTL) launched with Publish 11 in Oct 2004.
Anything marked **CU-era** (Publish 15 to 24, 2005) or **NGE** (Nov 2005 onward) is out of scope and listed only for context.

Research date: 2026-10-15. Written in my own words from public sources. No leaked source code or SWG-Source repositories were used.

## How to read this

- **Shipped**: P = Publish, U = an update note between publishes. The date is the live date in SOE's notes.
- **Confidence**: *high* means an SOE patch note says it. *Medium* means a pre-CU player or correspondent guide says it. *Low* means a later wiki, an emulator wiki or my inference.
- Source keys like [P8.1] are listed in full at the end.
- **Main sources**:
  - SOE's own patch notes, mirrored on the SWG Wiki (Fandom) as "Publish N Notes" and "Update Notes" pages.
  - Two pre-CU SOE-forum guides: the *FAQ for Image Designers* (last edited 10 Feb 2005) and the *Guide to Player Cities v1.3* (26 Feb 2005). Both are saved on the Wayback Machine.
- **Later sources**: Fandom profession pages often mix in CU or NGE text, and SWGR (SWG Restoration) is a modern emulator with its own changes. Where these disagree with the 2005 sources, the 2005 sources win.

---

## 1. Image Designer (elite, from Entertainer)

### (a) Shipped in pre-CU

| Item | What it was | When |
|---|---|---|
| Base ID | Novice Entertainer can already image-design, with limited options. The Entertainer tree has an Image Design I–IV branch. Novice Image Designer then needs that branch (SWGR says all four boxes). | Launch (Jun 2003) |
| Skill tree | Novice ID, then four branches of I–IV (Hairstyling, Face, Bodyform, Markings), then Master ID. | Launch |
| Session | The client must be in your group. Target them and use `/imagedesign` (`/image`) or the radial "Image Design" option. The UI looks like character creation. Self-design is allowed and gives half XP. | Launch |
| Hair | More hairstyles per Hairstyling box, plus ID-only hair, frill, lekku, horn and ridge styles. "Bald" can be undone (fixed in P8.1). | Launch / P8.1 |
| Face | Face-feature sliders unlock per Face box. Eye shape and eye angle were fixed in P8.1. Human male freckles were added in P3. | Launch / P3 / P8.1 |
| Body | Fandom: muscle (Body II), height (Body III), weight (Body IV). Master only: skin/fur colour, head size, female torso, age. | Launch |
| Markings | Species-specific markings and tattoos, such as Zabrak tattoos, Twi'lek lekku patterns and Wookiee fur patterns. You cannot add markings to a species that had none at character creation (e.g. Humans). | Launch |
| Species coverage | Mon Cal and Trandoshan options were completed in Aug 2003. Wookiees and Mon Cals have nothing changeable until Image Design II (eye colour). Cross-species hair (e.g. a Wookiee with a 'fro) was an exploit and was disabled. | U 21 Aug 03 |
| Colour palettes | Hair, skin/fur, lips, cosmetics, eyes, markings and tattoos all got more colours in P8.1. Palette size by skill: Novice Entertainer has the old palettes; Novice ID 16×6; any tier-1 box 16×8; tier-2 16×10; tier-3 16×12; tier-4 16×14; Master 16×16 (256 colours). | P8.1 (12 May 04) |
| ID salons ("tents") | Five tents: Theed, Moenia, Coronet, Bestine, Vreni Island (`/find salon`). They were placed in P8 and became active in P8.1. P9 added full decoration and music. Each tent has an Image Modification Booth that halves ID timers. | P8 (27 Apr 04), P8.1, P9 (29 Jun 04) |
| Stat migration | Before P8.1, players could move their own HAM stats. From P8.1, only an Image Designer can do it, in a salon booth. Rules: 10-min timer at first, cut to 4 min on 16 Nov 04. You cannot migrate your own stats. Any wound, even 1 point, makes it fail when the timer ends. Values must stay within the species' stat ranges (auto-corrected at login since Aug 2003). | P8.1; U 16 Nov 04; U 22 Aug 03 |
| Price and secure UI | Designer and client agree a price inside the ID window. The client is charged only when they accept the "after" view. Both see a live before/after preview. | P8.1 |
| Holo-emotes | 16 particle emotes, sold by the ID with 20 charges each, using `/holoemote <name>` and `/holoemote help`. They recharge for about 30–60 s between uses. Unlocks: Hairstyling I Beehive, Brainstorm, Imperial, Rebel; II Bubblehead, Hologlitter, Holonotes, Sparky; III Bullhorns, Champagne, Technokitty, Phonytail; IV Blossom, Butterflies, Haunted, Hearts, plus the "All" pack. | P8.1 |
| Timers (Feb 2005) | Non-master: cosmetic 1 min (30 s in a tent), body 2 min (1 min in a tent). Master: cosmetic 30 s and body 1 min, with no timer in a tent. Stat migration is 4 min, tent only. Timers don't stack; the longest one applies. From P9 a master outside a salon gets half time. From 16 Nov 04 a master working on themselves has no body or cosmetic timer outside a salon. | P9; U 16 Nov 04; [FAQ-ID] |
| 14.1 change | Body and cosmetic timers removed for everyone (stat migration keeps its timer). Each skill box from Novice to Master costs 1 skill point less (16 points total). | P14.1 (24 Mar 05) |
| XP | 100 for a cosmetic change, 300 for a body change, 2,000 for a stat migration. Self-design gives half. A session awards only its highest value. The client must accept. Master Entertainer needs 31,000 Image Design XP. | [FAQ-ID], [W-ENT] |
| Healing | None. ID has no wound or battle-fatigue healing; that belongs to dancing and music. | [FAQ-ID], [W-ID] (by absence) |
| Fees | Set freely by the designer (no NPC fee). About 1k–10k cr per change was typical in 2004. Stat migrations were often charged a set fee, cited as 10k–50k (search snippet of a customer guide). | [MMO-THREAD]; search snippet |

### (b) Planned or promised but not shipped, or only later

- **Player-placeable or craftable ID salons** (city-placeable, made by Architects): the Feb 2005 FAQ says this was "not at this time" but promised for "one day". No later note shows it shipped. *Medium.*
- **NPC-only hairstyles**: some NPC styles, such as Zabrak female horn-and-hair hybrids, were never given to players. This was a standing request. *Medium.*
- **Species or gender change**: never possible in SOE's SWG. The FAQ says ID can't change either. No SOE announcement was found. SWGR (an emulator, not SOE) added a paid species change in Dec 2024. *Medium* that it never shipped; *low* that it was ever planned.
- **Cosmetic overrides ("costume" kits)**: not an ID feature. The NGE's Game Update 6 added an Appearance tab for look-only gear. *NGE.*
- **The NGE (Nov 2005)** folded ID into a single Entertainer. Stat migration disappeared with the HAM stats (SWGR also lists it as removed). Chapter 5 (Feb 2007) gave entertainers "build-a-buff". *NGE.*
- **Open bugs at Feb 2005**, worth testing as "known-good" behaviour:
  - An "already in an ID action" lock-up after someone goes linkdead.
  - The preview showing an old outfit.
  - Zabrak hair colour not showing in the preview.

### (c) Checklist for a complete pre-CU ID

- [ ] ID works on a grouped target and on yourself, from both `/imagedesign` and the radial menu. An ungrouped target is refused.
- [ ] Novice Entertainer gets basic options. Each box in Entertainer Image Design I–IV and the ID tree (Hairstyling, Face, Bodyform, Markings I–IV) unlocks its own options.
- [ ] Master-only options exist and are blocked below Master: skin colour, head size, female torso, age, and the last 32 colours per palette.
- [ ] Palette sizes grow by tier: 16×6, 8, 10, 12, 14, 16.
- [ ] All 10 species are handled. Mon Cal and Trandoshan options are complete. Wookiee and Mon Cal are limited until Image Design II. Markings only for species that have them. Bald can be undone. No cross-species hair.
- [ ] Live before/after preview, revert, and price field. The client is charged only on accept. The designer can cancel at any time.
- [ ] Five salons, findable with `/find salon`, with booth, decoration and music. The tent halves timers. Choose the timer rules for your target build (14.1 has no body or cosmetic timers).
- [ ] Stat migration works only in a salon booth with an ID. Not on yourself. Fails on any wound. Clamped to species ranges. 4-min timer. Non-IDs cannot migrate.
- [ ] 16 holo-emotes, gated by Hairstyling tier, with an "All" pack at Hairstyling IV. 20 charges, a recharge delay, and `/holoemote help` shows charges.
- [ ] XP is 100/300/2,000, half on self, and not stacked within one session.
- [ ] Optional "planned" extra: a city-placeable or craftable salon.

**(d) Confidence:** high for patch-note items; medium for timers, XP and palettes (taken from the 2005 FAQ).
**Sources:** [P3] [P6] [P8] [P8.1] [P9] [U030821] [U030822] [U041116] [P14.1] [FAQ-ID] [W-ID] [W-ENT] [SWGR-ID] [MMO-THREAD]

---

## 2. Politician and player cities

### (a) Shipped in pre-CU

**Launch and timeline**
- Politician and player cities went live in **P4 (13 Nov 2003)**. Founding cities had been cut from the 2003 launch [RPGAMER].
- 20 Nov 03: a city needs 10 citizens to found. Every rank threshold was raised by 5. Outposts can't set taxes.
- P5 (16 Dec 03):
  - City caps doubled.
  - Civic structure cap of 1 + 6 × rank.
  - A city over that cap after demotion pays 75k cr per structure per week.
- P6 (11 Feb 04): citizens can revoke citizenship. Citizens inactive about 6 weeks are dropped (this check was paused on 1 Apr 04). Player-city cloners no longer count for "respawn closest". No camps inside cities.
- P7 (17 Mar 04): city garages (rank 2) with a mayor-set service fee. Mayors can remove militia members who are offline.
- 16 Nov 04:
  - Elections every 3 weeks; maintenance stays weekly.
  - Candidates, including the mayor, may withdraw.
  - Roster changes only in weeks 1–2.
  - Vote XP tripled, and the sitting mayor gets 750 Politician XP a week.
- 25 Jan 05: Politician boxes cost no skill points.

**Profession**
- **Trainers**: capitol buildings on Corellia, Naboo, Tatooine and Rori.
- **XP**: comes from votes and weekly city updates.
- **Skill tree**: Novice, then Fiscal Policy, Martial Policy, Civic Policy and City Customization (each I–IV), then Master.

**What each Politician box unlocks** (from the Feb 2005 guide)

| Box | Unlocks |
|---|---|
| Novice | Place a City Hall deed. Run for mayor. |
| Fiscal I | Register the city on the planetary map (rank 3+, +5k cr/week). |
| Fiscal II | Bank, Shuttleport. |
| Fiscal III / IV | Manufacturing Center / Research Center specialization. |
| Martial I | Recruit militia. |
| Martial II | Cloning Center; Clone Lab specialization. |
| Martial III | Stronghold specialization. |
| Martial IV | Place faction terminals. |
| Civic I | Mission terminals (`/installmissionterminal`). |
| Civic II | Garage; NPC skill trainers (`/recruitskilltrainer`, any trainer except Pilot and Shipwright). |
| Civic III | Entertainment District, Medical Center. |
| Civic IV | Improved Job Market, Sample Rich. |
| City Customization I / II / III / IV | Statues and streetlamps / fountains / small and medium gardens / large and exotic gardens. |
| Master | Nothing notable. This was a top complaint (see b). |

**Founding a city**
- A Politician places a City Hall deed (made by an Architect at Construction IV).
- Allowed planets: Corellia, Dantooine, Lok, Naboo, Rori, Talus, Tatooine.
- At least 1,000 m from other player cities; NPC-city no-build zones apply.
- The city needs 10 declared citizens within 150 m in 24 h, or the City Hall and treasury are destroyed.
- A City Hall can't be redeeded.
- Building style is fixed per planet: Corellian on Corellia and Talus; Tatooine on Tatooine, Lok and Dantooine; Naboo on Naboo, Rori and Dantooine.

**Ranks (2005 values)**

| Rank | Name | Citizens | Radius | New structures |
|---|---|---|---|---|
| 1 | Outpost | 10 | 150 m | Small gardens |
| 2 | Village | 20 | 200 m | Bank, Garage, medium gardens, player-placed Cantina; taxes allowed |
| 3 | Township | 35 | 300 m | Cloning Center, large gardens, player-placed Hospital; specializations; map registration |
| 4 | City | 55 | 400 m | Shuttleport, player-placed Theater |
| 5 | Metropolis | 85 | 450 m | Nothing new |

*Sources disagree.* The P4 launch values were 5 lower at every rank (5/15/30/50/80); the +5 change came on 20 Nov 03. Later wikis (Fandom 2011, MMORPG.com 2008, SWGR) give 5/10/15/30/40, which reflects a later SOE change. Use 10/20/35/55/85 for 14.1.

**City limits**
- Caps per planet (total / rank 3+ / rank 4+): Corellia, Naboo and Tatooine 20 / 15 / 10. Dantooine, Lok, Rori and Talus 50 / 30 / 20.
- Rank moves only one step per weekly update.
- On demotion, civic structures above the new rank or outside the new radius are destroyed. Player-placed Cantinas, Hospitals and Theaters are kept.

**Weekly maintenance (2005 values)**

| Item | Cost per week |
|---|---|
| City Hall | 35k / 60k / 85k / 110k / 135k (ranks 1–5) |
| Bank | 1.5k |
| Cloning Center | 20k |
| Garage | 20k |
| Shuttleport | 25k |
| Gardens | 10k / 20k / 30k (small / medium / large) |
| Each decoration, terminal or trainer | 1k to place, then 1.5k |

- Decoration limit: rank × 10.
- City Hall and Cloning Center each give 250 item slots.
- Unpaid civic structures decay. If the City Hall is lost, the whole city is lost.
- The 2011 Fandom figures (e.g. City Hall 3.5k, specializations 5k–12.5k) are almost exactly one tenth of these. Treat them as a later change.

**City Hall terminals**
- **Voting terminal**: register as a candidate, vote, change your vote, see standings.
- **City Maintenance terminal** (open to everyone): status, citizens, structures, advancement, maintenance and treasury reports, treasury deposit.
- **City Management** (mayor only):
  - Rename the city.
  - Register or unregister it on the map.
  - Zoning on/off.
  - Manage militia.
  - Taxes.
  - Treasury withdrawal (max 50k a day).
  - Specialization.

**Taxes**
- **Property**: a percentage added to the maintenance of every structure in the city.
- **Income**: a flat weekly charge per citizen, capped at 2k. Delinquents are reported to the mayor.
- **Sales**: added to vendor prices. *Bugged in live*: the tax was credited to the merchant, not the city.
- **Travel**: added to shuttle tickets, up to 1k.
- **Garage**: a percentage on repairs.

**Militia** (needs Martial I; the mayor is automatically a member)
- `/grantzoningrights`: lets a player place a structure for 24 h; with zoning on, this is the only way to build.
- `/cityban`: blocks a player from civic structures, the shuttleport and the bank.
- `/citypardon`: lifts a ban.
- A city ban also blocks cloning there (fixed 2 Jun 04).

**Specializations** (rank 3+, one at a time, change at most once a week, take effect at the next update)

| Specialization | Box | Cost per week (2005) | Effect |
|---|---|---|---|
| Clone Lab | Martial II | 80k | Clone insurance −20% |
| Entertainment District | Civic III | 80k | Entertainer healing +10% |
| Improved Job Market | Civic IV | 80k | Mission rewards +20% |
| Manufacturing Center | Fiscal III | 50k | +10% to prototype assembly (fewer failures) |
| Medical Center | Civic III | 80k | Medical healing and buffs +10% |
| Research Center | Fiscal IV | 125k | +15% on the final experimentation roll |
| Sample Rich | Civic IV | 70k | +20% sample yield, +10% chance to find |
| Stronghold | Martial III | 150k | Militia get +50 to defence rolls in PvP inside the city |

- Specializations existed by P8: the 27 Apr 04 notes fix one that failed to apply.
- The SWGANH reverse-engineering wiki gives the same eight with the same costs.
- Later lists add DNA Laboratory, Encore Performance and Outdoor Enhancement, and change several effects (e.g. Entertainment District becomes buff duration). Those are **NGE or emulator**.
- One search snippet mentioned a "Scientific Society" specialization, from a private-server wiki. *Not pre-CU.*

**Player-placed commercial buildings**
- Cantina: Master Musician, Dancer or Chef; 5 lots; rank 2.
- Hospital: Master Doctor or Combat Medic; 3 lots; rank 3.
- Theater: Master Musician or Dancer; 3 lots; rank 4.
- All three are transferable to anyone qualified.

### (b) Planned, requested or later

**Correspondent "Top 5" (Jan 2005)**
SOE's Politician Correspondent listed these as the profession's top issues:
1. Skill point cost. *Fixed* in Jan 2005: boxes became free.
2. No real Master Politician benefit.
3. City management tools: a city ledger, a way to see who owns a structure, a city message of the day, a notice board.
4. More city revenue, such as income from trainers and mission terminals.
5. Better city defences. Players doubted this would come before the GCW revamp.

A separate list asked for:
- A sales-tax fix.
- A "Mayor of" title.
- Shipwright trainers recruitable in cities.
- A higher decoration limit.

None of these shipped before the CU, apart from the skill-point change. *Medium.*

**Other items**
- **City-placeable ID salon**: promised in the ID FAQ, see §1. *Medium.*
- **City vs city combat or sieges**: no SOE announcement was found in the sources checked. *Low.*
- **City factions**: these came in NGE Game Update 15. Cities could align Imperial, Rebel or Neutral, which boosted GCW presence points; there was no city warfare. *NGE.*
- **More civic buildings**: none were added by SOE pre-CU after the P7 garage. Modern emulators (SWG Legends 2024, SWGR) added roads, new buildings and new specializations. *Emulator, not SOE.*

### (c) Checklist for complete pre-CU cities

- [ ] Politician trainers at the four capitols. 14.1 boxes cost 0 skill points. Each box unlocks what the table above says.
- [ ] Founding a city:
  - [ ] Only on the 7 allowed planets, within the planet's cap.
  - [ ] 1,000 m spacing.
  - [ ] 24-hour window to reach 10 citizens, or the hall and treasury are destroyed.
  - [ ] The City Hall can't be redeeded.
  - [ ] Pop-up and email instructions to the founder.
- [ ] Citizenship:
  - [ ] Declaring residence; a 24-hour delay when changing residence.
  - [ ] One city per player.
  - [ ] Revoke citizenship.
  - [ ] Inactive citizens are dropped (decide whether this is on, since it was paused in Apr 2004).
- [ ] Ranks:
  - [ ] Weekly update, one rank step at a time, email to the mayor.
  - [ ] Demotion destroys civic structures above the new rank or outside the radius.
  - [ ] Civic structure cap 1 + 6 × rank, with the 75k over-cap penalty.
  - [ ] Rank-3 and rank-4 caps per planet.
- [ ] All civic structures (City Hall, Bank, Garage, Cloning Center, Shuttleport, gardens and exotic gardens) and the three commercial buildings work at the right rank and box, with the right maintenance and redeed rules.
- [ ] Decorations (rank × 10), mission terminals, faction terminals (Martial IV) and recruited trainers. Each costs 1k to place and 1.5k a week, and only the mayor can remove them.
- [ ] All three City Hall terminals and every menu option, including treasury withdrawal capped at 50k a day and map registration for 5k a week.
- [ ] Five taxes:
  - [ ] Income tax capped at 2k.
  - [ ] Travel fee capped at 1k.
  - [ ] No taxes at Outpost.
  - [ ] Decide whether sales tax goes to the city (intended) or to the seller (the live bug).
- [ ] Three-week elections:
  - [ ] Registration only in weeks 1–2; the mayor must register too; withdrawal allowed.
  - [ ] Most votes wins; a tie keeps the mayor.
  - [ ] Emails to citizens.
  - [ ] Vote XP and the 750/week mayor XP.
- [ ] Militia: Martial I recruitment in City Hall. Zoning toggle. `/grantzoningrights` for 24 h. `/cityban` covers shuttle, bank, garage, civic buildings and cloning. `/citypardon`.
- [ ] All 8 specializations with the 2005 effects and costs. Rank 3+, one at a time, change once a week.
- [ ] Garage service fee. Shuttleport ticket and travel tax. The city shows on the planetary map at rank 3+ when registered.
- [ ] Optional "planned" extras: city ledger, structure-owner lookup, message of the day, revenue from terminals and trainers, a Master Politician perk.

**(d) Confidence:** high for the patch-note timeline; medium for structure costs and box unlocks (taken from the Feb 2005 guide, which a Politician Correspondent endorsed in the thread).
**Sources:** [P4] [U031120] [P5] [P6] [P7] [P8] [U041116] [U050125] [P14] [GUIDE-PC] [TOP5-POL] [ANH] [W-PC] [W-POL] [MMO-CITY] [SWGR-PC] [RPGAMER]

---

## 3. Entertainer, Dancer, Musician

### (a) Shipped in pre-CU

**Skill trees**
- Entertainer: Novice, then Musicianship, Dancing, Image Design and Entertainer Item Use (each I–IV), then Master.
- Dancer: Dancing Techniques, Enhancement, Knowledge and Prop Use, then Master.
- Musician: Musical Techniques, Enhancement and Knowledge, Instrument Use, then Master.
- XP to master Entertainer: 66k Dancing, 66k Musicianship, 41k Entertainer (audience), 31k Image Design.

**Performing**
- `/startdance` and `/startmusic` with named dances and songs.
- Flourishes `/flourish 1–8` give the main XP.
- Bands: `/bandflourish` (whole band; on/off setting saved since P1) and `/changebandmusic`. Group performers earn more XP.
- Dances: Popular, Bunduki, Poplock, Lyrical, Exotic 1–4 and the "2" versions. Formal and Footloose 2 come with Master Entertainer. P1 added more flourishes.
- Songs: Ballad, Swing, Funk, Waltz, Jazz, Virtuoso, Ceremonial, and others.
- Visual effects:
  - Shared by both: colour lights, dazzle, spotlight.
  - Dancer: distract, colour swirl, centre stage, smoke bomb.
  - Musician: fire jet 1 and 2, laser show, ventriloquism, featured solo.
- Large instruments can be placed in the world and played (Ommni Box, Nalargon; P3).
- Musicians at Master can place cantinas and theatres in player cities.

**Buffs (the core service)**
- Watching or listening gives a buff to the mind pool. A 2004 player guide says dancers buff Mind and musicians buff Focus and Willpower.
- P3: a master can raise a stat to up to twice its base value, for up to 2 h.
- Buffs to base and current values were reworked in P5 and U 23 Mar 04.
- From P8 (27 Apr 04) the audience must watch for 2 min first; this was cut to 1 min in P13 (10 Feb 05). P13 also halved the time to apply a buff.
- From 25 Jan 05 a dancer buff and a musician buff can be held at the same time.
- Buff icons came with P6 (Feb 2004).
- Faction perks (P3): +10% to wound and shock healing, +25% to mind buffs.

**Healing**
- Performing heals mind wounds and battle fatigue (shock) for anyone watching or listening. With nobody performing, cantinas and theatres heal slowly on their own.
- P13 increased mind-wound healing; it was toned down again on 24 Feb 05.
- 15 Dec 04: every building that heals battle fatigue can be registered with `/registerWithLocation`.
- City Entertainment District: +10% (see §2).

**Service tools**
- `/watch` and `/listen` (also allowed while sitting from P9), `/stopwatch` and `/stoplisten`.
- `/denyService` (P2) keeps a player from being healed or buffed by your performance.
- Tips with `/tip`.
- Gig missions from mission terminals (P1); their payouts were "substantially increased" on 25 Jan 05.

**Venues**
- NPC cantinas, NPC theatres and hotels.
- Player cantinas and theatres (§2).

**Later additions**
- P11 (21 Oct 04): a theatre-manager quest (audition, then three shows where the audience reacts) that rewards the Theatrical dance and the Western song.
- P8: Droid Engineer modules for music playback and entertainer lighting.
- P14.1: Tumble, Tumble2, Breakdance and Breakdance2 (Dancing Knowledge I–IV), the StarWars4 song (Novice Musician), and no more 15-second wait between songs or dances.
- Holo-emotes come from the Image Designer (§1).

### (b) Planned or later

- **Inspiration buffs** (a bonus to XP, faction and crafting success): the pre-NGE Fandom page describes these, but they arrived in **Publish 23 (Aug 2005, CU-era)**. Don't put them in a 14.1 baseline.
- **Build-a-buff** (custom buffs from points): NGE Chapter 5 "An Entertaining Enterprise" (Feb 2007). *NGE.*
- I found no SOE pre-CU announcement of extra entertainer systems. The 2004–05 complaints were about tips as the main income and AFK buff macros. *Low.*

### (c) Checklist

- [ ] Every dance and song is gated to the right box; flourishes 1–8; band commands; group XP bonus; the full list of visual effects.
- [ ] Placeable instruments; the full instrument set by skill (Slitherhorn and Fizz up to Nalargon, Ommni Box, Mandoviol at Master Entertainer).
- [ ] `/watch` and `/listen` work, including while seated; buff starts after 1 min (14.1 rule); time to apply halved; dancer and musician buffs stack; up to 2× base for up to 2 h; buff icons.
- [ ] Mind-wound and battle-fatigue healing during a performance; passive slow healing in venues; `/registerWithLocation`; faction perk; the city specialization bonus.
- [ ] `/denyService`, `/tip`, entertainer gig missions, and the theatre quest (Theatrical and Western).
- [ ] Droid Engineer playback and lighting modules.
- [ ] The P14.1 dances and song, and no 15-second delay.

**(d) Confidence:** high (patch notes). Medium for the dancer = Mind / musician = Focus and Willpower split (from a player guide).
**Sources:** [P1] [P2] [P3] [P5] [U040323] [P6] [P8] [P9] [P11] [U041215] [U050125] [P13] [U050224] [P14.1] [W-ENT] [W-DAN] [W-MUS] [MMO-THREAD] [CH5]

---

## 4. Creature Handler and Bio-Engineer

### (a) Shipped in pre-CU

**Creature Handler**

*Skill tree:* Novice, then Taming, Training, Empathy and Management (each I–IV), then Master.

*Taming and pets*
- Tame baby creatures at lairs. The tame option appears only with at least a 15% chance (P1). No taming while dead or incapacitated.
- Babies grow into adults over time. XP is based on the adult level.
- P5 (16 Dec 03) restructure:
  - "Control level" removed. The tame-level skill mod caps both the pet level you can tame or call and the total levels you can have out at once.
  - The number of pets you can call is set by a skill mod.
  - XP is split between active pets, and kills of creatures under half the pet's level give 1 XP.
  - A trade-in programme for pets made unusable by the change.
- Storage limit: two stored pets plus a "+stored pets" skill mod. Non-handlers may hold 2 non-aggressive pets up to level 10 and cannot call aggressive pets.

*Commands and training*
- Pets learn commands as spoken phrases.
- Known commands: follow, stay, guard, attack, group, friend, transfer (moved to Master in P5), trick 1 and 2 (heal 20% and 40% of mind; P4), embolden (60 s, +15% HAM; P4), ranged-attack toggle, and others.
- From Nov 2004 a pet answers a command whether or not you say its name first.
- "List commands" on the pet control device (PCD).

*Death and calling*
- Pets never die outright; they lose vitality (stats drop, at most 75%) instead of being death-blowed.
- Pets keep regenerating while stored.
- From P5, incapacitated pets auto-store after 4 min.
- From P9, the owner can revive an incapacitated pet to 1 HAM.
- From P7, pets, mounts and vehicles can be called anywhere outside, after a 15 s call delay and not within 30 s of combat. Camps still work.

*Mounts*
- Introduced in P4 (13 Nov 03): Bol, Brackaset, Kaadu, Carrion Spat, Dewback, Falumpaset. P7 added Bantha and Cu Pa.
- A pet becomes a mount when a Creature Handler trains it ("train as mount" moved to Management IV in P5). Trained mounts can also be bought.
- Bio-Engineers can make mountable pets but can't train them unless they also have Creature Handler skills.
- P14: double-click a mount to mount or dismount. Dead or incapacitated mounts can't be ridden (P9).

*Faction pets* (perk pets): attack only overt targets (P5); Covert targets and turrets fixed in P7.

**Bio-Engineer**

*Skill tree:* Novice, then Cloning, Tissues, DNA Sampling and Techniques (each I–IV), then Master.

*DNA sampling*
- `/sampledna` on live creatures.
- From P3, the success chance depends on your skill versus the creature's level, with consistent aggro and "spook" chances. The creature can't be attacked while it is being sampled.
- Sampling your own pets was allowed in P1 and then disabled in P2.

*Cloning (crafting pets)*
- Uses a DNA template.
- From P5 a pet's stats and level come entirely from the quality of the DNA samples, and the pet resembles its DNA source (rancor DNA gives a rancor-like creature).
- Invalid or over-powered pets are blocked from being called (Jan–Mar 2004).
- Low-level, non-aggressive Bio-Engineer pets can be traded to and tamed by anyone.

*Tissues*
- Crafted components that add skill mods to clothing (they were removed from armour on 20 Nov 03).
- Up to 6 effects per item (P4).
- They can be made in factories and have their own bazaar category (P3).

*Other products*
- Pet medicines, pet food and stims.
- Food additives for chefs: 3 strengths × 4 attributes (P6).
- Fandom also lists stimpacks.

*Lair search (P1)* can give eggs and animal samples.

*In cities:* Bio-Engineer trainers can be recruited from P8.

### (b) Planned or later

- **CU-era Publish 21 (Aug 2005)** "Creature Handler Revamp": pets learn abilities and handlers teach them to other pets. *Not pre-CU.*
- **NGE**: Creature Handler and Bio-Engineer removed. Their role came back as **Beast Master** in Chapter 6 "Masters of the Wild" (2007), with incubation. The "DNA Laboratory" city specialization (3 h less per incubation cycle) belongs to that system. *NGE.*
- Pre-CU complaints: the P5 restructure and balancing "nerfs" (Fandom), and the pet trade-in. I found no SOE source for unshipped pre-CU pet features (such as pet armour or breeding). *Low.*

### (c) Checklist

- [ ] Baby taming at lairs with the 15% rule; growth to adult; tame-level and calls-allowed skill mods; the stored-pet limit; non-handler limits (2 pets, level ≤10, no aggressive pets).
- [ ] Spoken-command training for every command; "list commands"; transfer at Master; friend list; trick and embolden effects.
- [ ] Vitality loss instead of death (cap 75%, at most once per 5 min); auto-store after 4 min when incapacitated; incap recovery; healing in storage.
- [ ] Call rules: 15 s delay, not in combat, not while mounted, camps optional.
- [ ] All 8 mount species; "train as mount" at Management IV; double-click to mount; a Bio-Engineer pet can be trained as a mount by a handler.
- [ ] XP rules (split between pets; low-level kills give 1 XP; adult-level basis).
- [ ] Bio-Engineer: sampling chances and aggro; DNA templates; P5 cloning rules; validity checks; all tissue skill mods on clothing only; 6-effect cap; factory crafting; pet medicines; chef additives.
- [ ] Lair search loot (eggs and samples).

**(d) Confidence:** high (patch notes). Medium for the exact command list.
**Sources:** [P1] [P2] [P3] [P4] [U031120] [P5] [P6] [P7] [U040323] [P8] [P9] [P14] [W-CH] [W-BE] [U]

---

## 5. Merchant

### (a) Shipped in pre-CU

**Skill tree:** Novice, then Advertising, Efficiency, Hiring and Management (each I–IV), then Master. Mastery costs 42 skill points (29 of them for prerequisites).
**XP:** comes from vendor activity (50 per active hour, and 50 per customer interaction at most once per 15 min) and from structure access fees paid.

**Vendors**
- Novice Merchant can place an NPC vendor of a random playable species, as well as terminal and droid vendors.
- A vendor must be initialized after placing (P1), and the player must be in the same building to do it (Jan 2005).
- Maintenance is about 15 cr/h (P4).
- Ad barking and planetary-map registration survive server restarts (P4).
- Vendor categories include pets and medical supplies (P4).
- Items stay for sale for 30 days (P4, Dec 2003).
- Vendors can't be traded (Jul 2003). Buildings with vendors in them can be transferred (Nov 2004).

**Merchant perks**
- Hiring IV lets you dress vendors in clothing (P2).
- Shop signs for player shops (P2 and P3).
- Vendors can be deactivated (P3).
- Merchant tents in three colours (made by Architects and Tailors), placeable with Efficiency IV: Structures (P4).
- Structure access fees count toward XP.

**Vendor and item limits by skill (P10, 31 Aug 04)**

| Box | Vendors | Items |
|---|---|---|
| Artisan Business III | 1 | 100 |
| Artisan Business IV | +1 | +150 |
| Novice Merchant | +1 | +500 |
| Efficiency III | — | +100 |
| Efficiency IV | +1 | +150 |
| Management I, II | +1 each | +500 each |
| Management III, IV | +2 each | +500 each |
| Master Merchant | +2 | +1,000 |

- Example totals: Novice is 3 vendors and 750 items; Management IV is 9 vendors and 2,750 items; Master is 12 vendors.

**Vendor clean-up (P10, Sep 2004)**
- Empty vendors are hidden from the map.
- An empty vendor gets a warning after 14 days and is deleted 14 days after that.
- An unused vendor is deleted after 100 days (the timer was changed from 14 days on 29 Sep 04).
- Owners are warned by email.
- The maintenance cycle no longer stops when a vendor runs out of maintenance funds (Dec 2004).

**Bazaar**
- Bazaar terminals with instant sale and auctions.
- P6 raised the auction "max bid amount" from 3,000 to 6,000 (that is how the note words it).
- An Auction chat channel and `/auction` arrived in Jul 2004.

**Galaxy-wide vendor search (P14.1, 24 Mar 05)**
- Bazaar terminals can search player vendors anywhere.
- Each vendor has a search on/off option in Vendor Control → Status. It is off by default for existing vendors and on for new ones.
- With search off, a vendor works as a private sale point.
- A min/max price filter was added on 8 Apr 05.

**Manufacturing:** factories and factory crates are a crafter (Artisan) feature, not Merchant-only. Droid Engineers can make a Merchant Barker droid module (P8) that repeats an advert and hands out waypoints.

### (b) Planned or later

- **Vendor search** had long been asked for and arrived only in 14.1, so it is *in scope*. Check that your 14.1 build has it.
- **City sales tax** went to the seller instead of the city; this was never fixed pre-CU (§2).
- **NGE**: Merchant was folded into the Trader professions; Chapter 5 (2007) added trader content. *NGE.*

### (c) Checklist

- [ ] All three vendor types; initialize rule; same-building rule; maintenance; barking with its text; map registration and categories; vendor clothing (Hiring IV); shop signs; deactivate.
- [ ] Vendor and item limits exactly as in the table; a player over the limit can't list new items but existing sales keep working.
- [ ] Empty and unused vendor timers and emails; restock gives a fresh 30-day listing; the vendor stays alive when out of maintenance.
- [ ] Merchant tents (Efficiency IV); access fees grant XP.
- [ ] Bazaar instant sale and auctions; Auction chat channel.
- [ ] 14.1 vendor search with per-vendor opt-in and the min/max price filter.

**(d) Confidence:** high (patch notes); medium for the XP figures (Fandom).
**Sources:** [P1] [P2] [P3] [P4] [P6] [P8] [P10] [U040921] [U041116] [U041215] [U050125] [P14.1] [U050408] [W-MER]

---

## 6. Other professions (brief)

| Profession | What defined it in pre-CU | Key dated items | Later (out of scope) | Conf. |
|---|---|---|---|---|
| **Squad Leader** | The only profession that buffs a whole group. Skill trees: Mobility, Strategy, Leadership, Tactics. Group-wide modifiers such as defence and terrain negotiation (not active when ungrouped). Group commands such as `/boostmorale` and rally/retreat-style abilities. XP comes from the group's combat (Oct 2003). | U 22 & 30 Oct 03 | **CU-era P24 (Oct 2005)** revamp | Medium |
| **Smuggler** | Hybrid fighter. Skill trees: Underworld, Slicing, Dirty Fighting, Delinquency. Slices weapons and armour for better stats (sliced items are tagged, P7). Crafts spice. Underworld lets you buy faction points (no artificial cap from P13). Imperial contraband scans with a pass/fail check and a group bonus (P6). `/lastditch` attack (P1). | P1, P6, P7, P13 | **CU-era P19 (Jun 2005)** slicing changes | Medium |
| **Bounty Hunter** | Ranged hybrid. Skill trees: Investigation, Weapons Training, Subjugation, Dirty Tricks. Bounty-terminal missions with seeker and probot droids (charges added in P3). Marks are non-aggressive from P6. **Player-Jedi bounties from P7 (17 Mar 04)**, roughly 35k–250k payouts at Master BH. Requires Exploration IV instead of Master Scout from Jul 2004. | P3, P6, P7, U 6 Jul 04, U 21 Sep 04 | NGE redesign | High |
| **Ranger** | Elite Scout. Skill trees: Wayfaring, Frontiering, Tracking, Advanced Trapping. `/conceal` with planet-specific camouflage kits and `/areatrack` (both P2). Notified when a creature stalks you (P3). Best creature harvester: group harvest bonus 30%, more at Master (Feb 2005). Trapping XP. | P2, P3, U 24 & 25 Feb 05 | Removed in NGE | High |
| **Chef** | Food and drink crafter (skill trees: Entrees, Desserts, Mixology, Cooking). **Fully revamped in P6 (11 Feb 04)**: experiments on filling, flavour, nutrition and quantity; effects beyond stats (skill buffs, protections, foods for entertainers and crafters, e.g. the XP-bonus food Ormachek); drink containers; Bio-Engineer additives; creature milk. Can place a city cantina at Master (2005 guide). | P6, P7 | Folded into Trader (NGE) | High |
| **Shipwright (JTL)** | Crafts starship chassis deeds and components; reverse-engineers components looted in space. Skill trees: Ship Design, Engines, Assembly, Ordnance. Needs JTL and Artisan Engineering IV. Trainers at large starports, not recruitable in cities (a correspondent ask). Factories accept Shipwright schematics (Nov 2004 fix). | P11 (21/26 Oct 04), U 16 Nov 04 | Folded into Trader (NGE) | Medium |

---

## Where sources disagree (summary)

| Topic | 2004–05 source | Later source | Use for 14.1 |
|---|---|---|---|
| City citizen thresholds | 10/20/35/55/85 | 5/10/15/30/40 (Fandom 2011, SWGR, MMORPG 2008) | 10/20/35/55/85 |
| City spacing | 1,000 m | 1,500 m (SWGR) | 1,000 m |
| City structure and specialization costs | e.g. City Hall 35k–135k, Research Center 125k | about one tenth (Fandom 2011) | 2005 figures |
| Entertainment District | entertainer (battle-fatigue) healing +10% | buff duration +30 min and tick +3 (Fandom, SWGR) | +10% healing |
| Improved Job Market | +20% | +15% (SWGR) | +20% |
| Clone Lab | insurance −20% | −50% cloning-sickness cost (Fandom, NGE) | −20% insurance |
| Elections | weekly until 16 Nov 04, then every 3 weeks | — | every 3 weeks |
| Entertainer buff type | mind-pool attribute buffs | "inspiration" XP buffs (Fandom pre-NGE page; really P23, Aug 2005) | mind buffs |
| ID timers | rules as of Feb 2005 | removed in 14.1 for body and cosmetic changes | follow your target build |
| Stat migration | present (P8.1 onward) | removed (SWGR, NGE) | present |

---

## Source list

**SOE patch notes, mirrored on the SWG Wiki** (index: https://swg.fandom.com/wiki/Updates)

| Key | Page | URL |
|---|---|---|
| [P1] | Publish 1, 13 Aug 03 | https://swg.fandom.com/wiki/Publish_1_Notes:_13_August_03 |
| [U030821] | Update, 21 Aug 03 | https://swg.fandom.com/wiki/Update_Notes:_21_August_03 |
| [U030822] | Update, 22 Aug 03 | https://swg.fandom.com/wiki/Update_Notes:_22_August_03 |
| [P2] | Publish 2, 4 Sep 03 | https://swg.fandom.com/wiki/Publish_2_Notes:_4_September_03 |
| [P3] | Publish 3, 8 Oct 03 | https://swg.fandom.com/wiki/Publish_3_Notes:_8_October_03 |
| [P4] | Publish 4, 13 Nov 03 | https://swg.fandom.com/wiki/Publish_4_Notes:_13_November_03 |
| [U031120] | Update, 20 Nov 03 | https://swg.fandom.com/wiki/Update_Notes:_20_November_03 |
| [P5] | Publish 5, 16 Dec 03 | https://swg.fandom.com/wiki/Publish_5_Notes:_16_December_03 |
| [P6] | Publish 6, 11 Feb 04 | https://swg.fandom.com/wiki/Publish_6_Notes:_11_February_04 |
| [P7] | Publish 7, 17 Mar 04 | https://swg.fandom.com/wiki/Publish_7_Notes_for_17_March_04 |
| [U040323] | Update, 23 Mar 04 | https://swg.fandom.com/wiki/Update_Notes:_23_March_04 |
| [P8] | Publish 8, 27 Apr 04 | https://swg.fandom.com/wiki/Publish_8_Notes_for_27_April_04 |
| [P8.1] | Update, 12 May 04 (Publish 8.1, ID makeover) | https://swg.fandom.com/wiki/Update_Notes:_12_May_04 |
| [P9] | Publish 9, 29 Jun 04 | https://swg.fandom.com/wiki/Publish_9_Notes_for_29_June_04 |
| [U040706] | Update, 6 Jul 04 | https://swg.fandom.com/wiki/Update_Notes:_6_July_04 |
| [P10] | Publish 10, 31 Aug 04 | https://swg.fandom.com/wiki/Publish_10_Notes_for_31_August_04 |
| [U040921] | Update, 21 Sep 04 | https://swg.fandom.com/wiki/Update_Notes:_21_September_04 |
| [P11] | Publish 11, 21 Oct 04 | https://swg.fandom.com/wiki/Publish_11_Notes_for_21_October_04 |
| [P11] | Publish 11, 26 Oct 04 | https://swg.fandom.com/wiki/Publish_11_Notes_for_26_October_04 |
| [U041116] | Update, 16 Nov 04 | https://swg.fandom.com/wiki/Update_Notes:_16_November_04 |
| [U041215] | Update, 15 Dec 04 | https://swg.fandom.com/wiki/Update_Notes:_15_December_04 |
| [U050125] | Update, 25 Jan 05 | https://swg.fandom.com/wiki/Update_Notes:_25_January_05 |
| [P13] | Publish 13, 10 Feb 05 | https://swg.fandom.com/wiki/Publish_13_Notes_for_10_February_05 |
| [U050224] | Update, 24 Feb 05 (Publish 13.1) | https://swg.fandom.com/wiki/Update_Notes:_February_24,_2005 |
| [U050225] | Update, 25 Feb 05 | https://swg.fandom.com/wiki/Update_Notes:_February_25,_2005 |
| [P14] | Publish 14, 9 Mar 05 | https://swg.fandom.com/wiki/Publish_14_Notes_for_9_March_05 |
| [P14.1] | Update, 24 Mar 05 (Publish 14.1) | https://swg.fandom.com/wiki/Update_Notes:_March_24,_2005 |
| [U050408] | Update, 8 Apr 05 | https://swg.fandom.com/wiki/Update_Notes:_April_8,_2005 |

Four more dated notes are cited in the text but were not in the link check. Their URLs follow the same pattern and are listed on the index:

| Key | Page | URL |
|---|---|---|
| — | Update, 1 Apr 04 (inactive-citizen check paused) | https://swg.fandom.com/wiki/Update_Notes:_1_April_04 |
| — | Update, 2 Jun 04 (city ban also blocks cloning) | https://swg.fandom.com/wiki/Update_Notes:_2_June_04 |
| — | Update, 29 Sep 04 (unused-vendor timer changed to 100 days) | https://swg.fandom.com/wiki/Update_Notes:_29_September_04 |
| — | Update, 4 Nov 04 (pet commands work without the pet's name) | https://swg.fandom.com/wiki/Update_Notes:_4_November_04 |

**Pre-CU SOE forum threads** (saved via SWGEmu's archive and the Wayback Machine)

| Key | Thread | URL |
|---|---|---|
| [FAQ-ID] | *FAQ for Image Designers*, Kwee and n'Jessi, Dec 2004 (edited 10 Feb 2005) | https://web.archive.org/web/20160909102949/http://swgemu.com/archive/scrapbookv51/data/20070127180239/index.html |
| [GUIDE-PC] | *Guide to Player Cities v1.3*, Khristen, 26 Feb 2005 (endorsed in the thread by the Politician Correspondent) | https://web.archive.org/web/20160909103515/http://swgemu.com/archive/scrapbookv51/data/20070127193158/index.html |
| [TOP5-POL] | *Top 5!*, Politician Correspondent Pappi, Jan 2005 | https://web.archive.org/web/20160909080819/http://swgemu.com/archive/scrapbookv51/data/20070127193212/index.html |

**Wiki profession pages** (often mixed with CU or NGE text)

| Key | Page | URL |
|---|---|---|
| [W-ID] | Image Designer | https://swg.fandom.com/wiki/Image_Designer |
| [W-PC] | Player city (state as of 2011) | https://swg.fandom.com/wiki/Player_city |
| [W-POL] | Politician | https://swg.fandom.com/wiki/Politician |
| [W-ENT] | Entertainer (pre-NGE) | https://swg.fandom.com/wiki/Entertainer_(pre-NGE) |
| [W-DAN] | Dancer | https://swg.fandom.com/wiki/Dancer |
| [W-MUS] | Musician | https://swg.fandom.com/wiki/Musician |
| [W-CH] | Creature Handler | https://swg.fandom.com/wiki/Creature_Handler |
| [W-BE] | Bio-Engineer | https://swg.fandom.com/wiki/Bio-Engineer |
| [W-MER] | Merchant | https://swg.fandom.com/wiki/Merchant |
| Other professions | Squad Leader | https://swg.fandom.com/wiki/Squad_Leader |
| | Smuggler (pre-NGE) | https://swg.fandom.com/wiki/Smuggler_(pre-NGE) |
| | Bounty Hunter (pre-NGE) | https://swg.fandom.com/wiki/Bounty_Hunter_(pre-NGE) |
| | Ranger | https://swg.fandom.com/wiki/Ranger |
| | Chef | https://swg.fandom.com/wiki/Chef |
| | Shipwright (pre-NGE) | https://swg.fandom.com/wiki/Shipwright_(pre-NGE) |

**Secondary and context sources**

| Key | Source | URL |
|---|---|---|
| [ANH] | SWGANH wiki, city specializations (reverse-engineering emulator documentation) | https://wiki.swganh.org/index.php/City_Specializations_(Game_Mechanics) |
| [SWGR-ID] | SWG Restoration wiki, Image Designer (modern emulator; differs from live) | https://swgr.org/wiki/image_designer |
| [SWGR-PC] | SWG Restoration wiki, player cities | https://swgr.org/wiki/player_cities |
| [MMO-CITY] | MMORPG.com city guide (2008) | https://www.mmorpg.com/star-wars-galaxies/guides/city-building-guide-2000116198 |
| [MMO-THREAD] | MMORPG.com thread of 2003–05 reposted guides (ID prices and timers, entertainer buff split) | https://forums.mmorpg.com/discussion/184762/astromechs-friday-features-other-stuff-2003-2005/p6 |
| [CH5] | Chapter 5 launch (NGE) | https://worthplaying.com/article/2007/2/22/news/39996-swg-chapter-5-an-entertaining-enterprise-launched/ |
| [CH5] | Chapter 5 interview | https://www.gamebanshee.com/wu9 |
| [RPGAMER] | 2003 report on features delayed past launch (cities, vehicles, player missions) | https://archive.rpgamer.com/news/Q1-2003/020803c.html (search snippet only) |
| — | SWGEmu targets 14.1 | https://swgemulator.fandom.com/wiki/SWGEmu_Wiki (search snippet only) |
| — | Stat-migration price of 10k–50k: search snippet of the SOE forum thread "A guide for customers and stat migration" | https://www.swgemu.com/archive/scrapbookv51/data/20070127222056/ (not opened; the site shows a bot check) |
