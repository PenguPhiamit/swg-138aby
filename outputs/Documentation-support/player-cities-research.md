# Player cities: what players built, how Core3 runs them, how our bots would build one, and how to push cities toward creativity

16 Oct 2026, 2:10 AM. Claude (Sonnet 5.5), for the owner's 1:30 AM request ("research player cities, notable ones of live servers and private servers and how they develop, and 1. how our bots will do it, and 2. find a way to encourage more creativity in city design"). Research and design only. No code, config, server, bot or board entry was changed, and nothing under `/opt/swg` was written. Core3 facts are from `/opt/swg/Core3-dev` at `8b48a044` (1:03 AM, 16 Oct), read inside WSL; line numbers move, so re-grep before building.

**Labels used for every claim**
- **[code]** read from Core3-dev (`path:line`). **[calc]** my arithmetic from [code] and [measured] numbers. **[measured]** from our launch-simulation reports. **[est]** my estimate. **[untested]** nothing was run.
- Sources: **[official]** published by SOE or by a server's own team; **[community]** player-written, wiki or forum; **[press]** a news or column site; **[archive]** read from an Internet Archive copy. Dates are the source's own where it gave one.

## Summary

1. **Real cities were friend-group and guild cities.** The official SOE list of 3 Feb 2011 [official][archive] names 1,308 cities of rank 2 or higher on 14 servers; 420 were rank 5. The biggest server (Starsider) had 111 of its 110 rank-4-or-higher slots taken, so on big servers the caps, not demand, limited growth. Section 1.1.
2. **Notable cities were notable for a job, not for size:** a role-play hub that outlived the CU and NGE (Black Sands), a guild fortress under base raids (Hero's Legacy), a crafters' research town (Black Sun Ravine, Bantha Cairns), an underworld slum (Pelgo Slums), a guild with three malls and a temple (Elysium). Section 1.3 and 1.4.
3. **What kept them:** a guild or friend group that stays, a site with room and services, regular events, and rules that clear dead cities (live removed citizens inactive for 90 days from 1 May 2009; Infinity cleaned up inactive cities in 2023). **What killed or stalled them:** caps (Legends in 2019: "permanently city-capped" planets), uneven terrain (one Restoration city moved twice), upkeep shocks (Restoration, March 2024), and the end of the servers.
4. **Core3's city system matches the Feb 2005 pre-CU design closely** (upkeep, structure ranks, eight specializations, 24-hour founding window). Our two settings change its feel: citizens per rank {1,2,3,4,5} (stock {2,4,6,8,10}, pre-CU {10,20,35,55,85}) and upkeep ×0.5. A five-character city reaches rank 5 in **4 weekly updates (28 days)**, because rank moves one step per update. Section 2.
5. **Money is the hidden wall at our settings.** Rank 5 hall upkeep alone is 67,500 a week and a "full" town about 240,000, while the highest taxes a 5-citizen city can set raise about 12,700 a week [calc]. A city funds itself only by donation. Section 2.6.
6. **Gaps in Core3** (ranked in 2.11): Clone Lab and Entertainment District do nothing; no `/cityWarn`; city guards and `/unCityBan` are stubs; militia have no force powers; no inactive-citizen purge and no city faction alignment; Hoth and Ossus are missing from `CitiesAllowed`, so founding there likely hits an empty-vector index.
7. **Bots can found and grow cities if they call the city manager directly** (the stock flows open windows, and a window sent to a client-less bot would crash `SuiPageData::sendTo`, which has no null check on the client). The design below: settler roles, a site planner that reuses the Ossus census, a compressed city clock (one simulated week = 6 minutes), transient structures, a quota of at most 30% of each planet's city slots, and a JSONL event stream. Five probes come first (Section 3.12). Section 3.
8. **Three showstoppers to prove first:** the structure maintenance task destroys any structure whose owner has no player name (`StructureMaintenanceTask.cpp`), so bot-owned structures need a plan; the weekly cadence needs compressing; and bots could fill the planets' city caps and lock humans out.
9. **Creativity: what worked.** Contests (a "Galactic Home Show" ran on Legends monthly, on Empire in Flames, Restoration and SWGEmu's Finalizer in 2023; Infinity ran a "Best Dressed City" with a 135-million-credit prize), free-form object placement ("pod-racers built from hundreds of parts"), generous decoration limits (live raised them 50% in 2009), props that stay (Restoration, June 2024), and specializations as identity (Restoration's 2026 refresh). Section 4.
10. **Top ideas for our server, cheapest first:** a Home Show / Best Dressed City contest with a badge; raise the decoration cap and drop decoration upkeep; make all eight specializations real; pre-flattened founding sites; let mayors keep static event-perk props. Bot-seeded example towns come after the bot harness works. Ranked list in 4.3. Owner's questions are at the end.

## 0. Method and limits

- **Read:** Core3-dev city code (`src/server/zone/managers/city/`, `objects/region/CityRegion*`, `StructureManager.cpp`, place-structure sessions, deed components, `bin/scripts/managers/city_manager.lua`, the civic structure templates under `bin/scripts/object/building/player/city/`), the bot code in `src/server/zone/managers/botpop/`, the launch-simulation reports, and our earlier `Systems-baseline/id-politician-gaps.md` (15 Oct), which I re-checked against the tree rather than copying.
- **Web:** public pages only; no logins, downloads or posts. Fandom pages (blocked for the fetch tool) were read in the browser pane, as `AGENTS.md` says.
- **Not read:** the 2007 official manual and the "Advanced Guide" on swgemu.com / swgreckoning.org sit behind a Cloudflare "just a moment" check. I stopped there and did not try to pass it. I used the Internet Archive copies of two forum guides (25 and 26 Feb 2005) instead. MassivelyOP's Felucia article, the Unwinnable retrospective, a 2004 retrospective on when cities arrived (https://archive.rpgamer.com/news/Q2-2004/062804c.html), Legends' spring 2024 newsletter, the SWG wiki's Servers page (server closure dates), Shacknews and a forum repost for the Forces Under Siege update, and the Storyteller launch coverage (Chapter 6, 22 May 2007) were only seen as search snippets or titles; the claims taken from them are marked "search summary" or sit in the "seen only" list at the end.
- **People:** no player, mayor or guild-leader names are used. Guild, city, server and site names are. Press authors are not named.
- **Provenance note.** Legends and Restoration are not on SWGEmu's list of AGPL-compliant servers (the SWGEmu wiki says some servers are "illegally operated source distributions"). I used only their public wiki pages, news posts and dev diaries as evidence of what players did. Nothing of theirs was downloaded and no code or data was looked at. Sentinel's Republic is excluded by the owner and is not used, though it appears in some of the roundups I read.
- **Gaps:** I found no public city documentation for Awakening, and none for Finalizer or Basilisk beyond one guild's recruiting post. The SWGEmu forums are not indexed publicly; the Finalizer/Basilisk Discord is where that evidence would be.

## 1. Notable player cities

### 1.1 What the official list says (3 Feb 2011)

Source: SOE's own "Player Cities" page, "all current player cities ranks 2, 3, 4 and 5 on each galaxy as of February 03, 2011", with name, rank, planet, coordinates (ranks 4 and 5) and founding date. [official][archive: Wayback copy of 9 Feb 2011]. It is a **survivor snapshot**: rank-1 outposts and cities lost before the date are not on it, and the servers had merged in Oct 2009 (Kauri, Corbantis, Intrepid and Kettemoor closed, per the SWG wiki). I counted the page's rows with a script in the browser pane.

| Server | Cities (rank 2+) | Rank 2 | Rank 3 | Rank 4 | Rank 5 | Rank-4+ slots used (cap 110) |
|---|---:|---:|---:|---:|---:|---:|
| Starsider | 226 | 58 | 57 | 17 | 94 | 111 (101%) |
| Flurry | 133 | 18 | 35 | 39 | 41 | 80 (73%) |
| Bria | 124 | 21 | 34 | 27 | 42 | 69 (63%) |
| Europe-FarStar | 121 | 17 | 38 | 19 | 47 | 66 (60%) |
| Europe-Chimaera | 111 | 22 | 32 | 22 | 35 | 57 (52%) |
| Chilastra | 108 | 19 | 26 | 23 | 40 | 63 (57%) |
| Ahazi | 86 | 14 | 26 | 20 | 26 | 46 (42%) |
| Eclipse | 81 | 18 | 23 | 17 | 23 | 40 (36%) |
| Bloodfin | 75 | 21 | 24 | 12 | 18 | 30 (27%) |
| Gorath | 69 | 14 | 23 | 17 | 15 | 32 (29%) |
| Shadowfire | 57 | 9 | 15 | 18 | 15 | 33 (30%) |
| Radiant | 44 | 10 | 14 | 14 | 6 | 20 (18%) |
| Sunrunner | 44 | 5 | 18 | 10 | 11 | 21 (19%) |
| TC Prime | 29 | 2 | 14 | 6 | 7 | 13 (12%) |
| **All 14** | **1,308** | **248** | **379** | **261** | **420** | |

The cap of 110 is 10 each on Corellia, Naboo and Tatooine plus 20 each on Dantooine, Lok, Rori and Talus, from the rank-cap table in the SWG wiki [community] and the 2005 guide [community][archive]. Starsider's count by planet is 10, 10, 10 and 20, 21, 20, 20: every planet full.

What else the list shows:
- **Planets.** Dantooine 273 cities, Lok 227, Naboo 203, Talus 197, Tatooine 164, Rori 136, Corellia 108. The four 50-city planets hold 64% of all cities; Corellia holds 8%. Players went where slots were free.
- **Age.** 477 listed cities were founded 2003-2008 and 831 from 2009 to 3 Feb 2011 (282 in 2009, 496 in 2010, 53 in Jan-Feb 2011). Of the 420 rank-5 cities, 93 were founded before 2005 and 48 of them in 2003. Median founding year of a rank-5 city: 2008. Cities that lasted 7 years existed, but most of the top rank was new.
- **Launch window.** 45 cities share the founding date 13 Nov 2003 and 19 share 16 Dec 2003, the first days of the feature (the first system was live by Nov 2003 [press: 2004 retrospective seen in search results]). Examples still at rank 5 in 2011: New Solah, Intervention, Veritas, Alacio Island (Naboo); Arca Effex (Corellia); Arch Mesa, Mos Nihil, Mos Elsewhere (Tatooine); Crimson Island, Hunter's Rest (Talus).
- **Names show themes.** Of 1,308 names: 75 begin "New" (new homes after a move), 56 contain Dark, Shadow or Black, 45 begin "Mos" (Tatooine pastiche), 16 name a Temple, Jedi, Sith, Academy or Praxeum, 8 are Mandalorian. Guild tags appear in names (LVN, POWER, SICK).

### 1.2 Patterns that matter for our design

1. **Cities were social, not geographic.** Guild pages describe a city as the guild's home; the 2005 guide says outright that a city is "not a solo venture" and that having a goal (role-play, PvP, commerce, crafting) is the way to a lasting city [community][archive].
2. **Slots saturate on a big server.** Starsider was at its cap in 2011. Legends hit the same thing: "way too easy to hold a player city with just a few people and almost no cash", so most planets were "permanently city-capped" and small cities could not grow [press: MassivelyOP, 1 Apr 2019]. The fixes aimed at clearing dead or tiny cities: live removed citizens inactive 90 days (Game Update 8, 12 Mar 2009, from 1 May 2009) [official]; Legends raised the players and characters per rank and the upkeep (Mar 2019); Infinity prepared inactive cities for demolition in March 2023 [press: mmofolklorist roundup].
3. **Services draw crowds, crowds draw shops.** Entertainers and medics work in player cantinas and hospitals; merchants moved into the biggest cities [press: Unwinnable, snippet]. Mos Pelgo's early growth came from "four mini malls" stocked by early vendors plus a shuttle [official: Restoration spotlight, 26 May 2024]. Our own run shows the same effect for bots: 2,659 of 2,661 rests watched a dancer when hurt hunters, medics and dancers met in town [measured: `FINDINGS.md` section 6].
4. **Terrain and object count are the practical limits.** One Restoration city moved twice (three sites in all) because its first site was uneven and limited expansion; another found its mushroom-shaped rocks difficult for planning; the first one's market district is hard on the processor [official: Restoration spotlights]. Restoration put terraforming off to "a future, larger update" [official: dev diary, 24 Aug 2026].
5. **Identity is the retention tool.** Players chose specializations for the guild's trade (Research Center for crafters), named districts, ran Friday role-play nights and anniversary parties [official: Restoration spotlights]. Restoration's 2026 diary says rank 5 was "the city end game", with nothing after it, and wants "cities to be unique".

### 1.3 Live servers (2003-2011): notable cities

| City | Server, planet, era | What made it notable | How it grew | What kept or ended it | Source |
|---|---|---|---|---|---|
| **Black Sands** | Gorath, Tatooine. Founded 29 Mar 2004; rank 4 in Feb 2011 | Role-play and crafting hub; a valley about 3 km north-east of Mos Eisley, near the NPC town's services but outside its lag. The mayor's own claim: "the largest and oldest city on Tatooine" at shutdown | Founded early 2004; "took a couple of months" to become an official city | Outlived the CU and NGE until the Dec 2011 shutdown. The same group re-founded it on Restoration in Sept 2022, at the same spot, three days after choosing that server, with the hall up within two weeks | [official] Restoration spotlight, 26 May 2024; [official][archive] SOE list 2011 |
| **Hero's Legacy** | Starsider, Talus (east of Dearic, Azaki Plains). Founded 27 Apr 2004; rank 5 in Feb 2011 | A guild city: the Heroes of Hope player association used static Anchorhead as its town (shops, tavern shows, flag fights) until official cities began, then "dropped a city hall on Talus" | Houses and structures first built by guild crafters; hunting in the swamps, fishing; PA halls and safehouses added for defence | Imperial players raided it (turrets burned, bases lost); the guild rebuilt. Still rank 5 after 6.8 years | [community] SWG wiki "HERO (PA)"; [official][archive] SOE list |
| **Echo Base** (my match to the guild's "Echo Base City") | Eclipse, Corellia. Founded 2 Jan 2005; rank 4 | Prime city of a rebel and neutral-traders guild of up to 500 members that ran a chain of cities, with **its own militia and leaders separate from the guild** and neutrals welcome | A founder-architect built the first buildings; later cities were added | A match on name and server only; the guild page does not give the rank | [community] SWG wiki "Guild:ECHO"; [official][archive] SOE list |
| **Mandalorian Brotherhood city** | Chilastra, Lok | A role-play guild city made of all its members, hosting a "Dueling Arena" the whole server could watch and bet on | n/a | Which row of the 2011 list it is, is not stated | [community] SWG wiki "Guild:-MB-" |
| **Starsider museum city** | Starsider, last day (15-16 Dec 2011) | A player-built city that held a museum to the server's players: custom weapons on plaques each describing their wielder. The same piece mourns "pod-racers created from hundreds of tiny parts" and "a custom starport" that the object-placement system allowed | n/a | Closed with the servers on 15 Dec 2011 | [press] PC Gamer, 16 Dec 2011 |
| **Launch-window survivors** | Bria, Ahazi, others | Founded 13 Nov or 16 Dec 2003 and still rank 5 in 2011 (list in 1.1) | Founded with the feature | 7+ years: guild backbone, central site | [official][archive] SOE list |
| **Typical shapes** | all | A Dantooine city that was one couple's compound, with friends building for them; a Lok city that was a guild base; criminal hubs; commercial centres; some "haphazard", some "intentionally designed" | n/a | n/a | [press] Engadget, 9 Dec 2011 |

Guinness World Records credits SWG with the first game to let "groups of houses" be formally recognized as cities with player mayors [press: record page, undated].

### 1.4 Private servers (SWGEmu family and others): notable cities and city policy

| City or server | Era | What made it notable or what the server did | Source |
|---|---|---|---|
| **Honour** (+ Honour Outpost) | SWGEmu **Basilisk**, Lok (Metropolis) and Corellia, Jul 2019 | A rebel guild's "well established" city and a second outpost city next to the Corellia rebel base that "recently got a shuttle"; "pretty much self sufficient with our crafters"; raids; recruits by Discord and website | [community] Steam post, 25 Jul 2019 (last edited 16 Sep 2019) |
| **Elysium** | **Infinity**, Talus (-5850, -300), undated page | Metropolis, population 113, Research Center. An Imperial guild's home: three large guild malls, a Dark Jedi temple, medical and cloning centres, a garage, a shuttleport, a cantina. To join you need the guild and one of **3 pre-approved house designs** | [community] SWG wiki "City:Elysium" |
| **Infinity: Best Dressed City** | Infinity, Mar-May 2023 | A faction-based contest, applications in March, winner announced 4 May, **135-million-credit prize**; praised as "a great display of using the game's props and furniture to its fullest". Infinity also readied inactive cities for demolition and added a 6th rank, Megalopolis, in March 2023 | [press] mmofolklorist roundups, Apr and 4 May 2023 |
| **Black Sun Ravine** | **Restoration**, Tatooine (north-central, near Mos Espa). Founded 16 May 2022 | 15 adventurers founded it and nearly all still play there. A valley with remnants of a podrace course; a mall with a museum, a waterfall viewpoint, "Twin Sun Square". Research Centre because the founders are crafters. Hosts cantina crawls and a cross-galaxy race | [official] spotlight, 26 Jan 2024 |
| **Mos Pelgo** and **Pelgo Slums** | Restoration, Tatooine (Valley of the Wind). Mos Pelgo founded late 2021; Pelgo Slums' founding date is not given (spotlight 10 Dec 2024) | Mos Pelgo: a Western main street with staged shootouts, a "Shadow Market" district of very high object density (hard on the processor), moved twice (three sites) before this valley because the first had uneven ground. Pelgo Slums: alleys instead of streets, "a glorious gritty chaotic mess", no medical centre (street surgeons), Improved Job Market because of bounty hunters, founded by people pushed out of the town next door | [official] spotlights, 26 May and 10 Dec 2024 |
| **Bantha Cairns** | Restoration, Tatooine (stone arches north-west of Mos Entha). 17 Jan 2025 | A research town for crafters built around the natural arches with a green "Bantha Star" light system; a renovated cantina with public crafting stations; a "hidden" spaceport. Founded by a few friends from another emulator and grew "far beyond their expectations" | [official] spotlight, 20 Sep 2025 |
| **Stardust** | SWGEmu-based; custom planets | 13 cities listed on 10 of its 12 planets, including its added planets (Chandrila, Lothal, Kaas; Moraband and Nal Hutta are listed with none). Uses stock thresholds {2,4,6,8,10}. Its page says elections are every 3 days (a custom change) | [community] Stardust wiki (undated) |
| **Legends** | Legends (not Core3), 2019-2024 | Raised the characters and accounts per rank in 2019; added Bespin (Cloud City apartments) in 2021 and a new planet, Felucia, "with new houses, player cities" (headline only); a monthly **Galactic Home Show** with themes; a winter 2023-24 revamp of cities with "new specs and deco" (new parks and a landing pad teased in a spring 2024 newsletter, seen only in a search summary) | [press] MassivelyOP 1 Apr 2019, 16 Apr 2021, 11 Mar 2024; [press] mmofolklorist Mar-Jun 2023 |
| **Empire in Flames** | SWGEmu-based, 2023 | "Strict player cities", an "anti-urban-sprawl housing system"; its first Galactic Home Show (June 2023) with a **Home Show winner's badge** | [press] MassivelyOP (search snippet); mmofolklorist May-Jun 2023 |
| **SWGEmu Finalizer / Basilisk** | 2023 | Finalizer's first Galactic Home Show ran during Empire Day, 26 Jun-5 Jul 2023; Core3 added rotate-on-every-axis furniture (Apr 2023) | [press] mmofolklorist Apr and Jul 2023 |
| **Awakening** | 2022 | 8th anniversary in Nov 2022 with paintings and a badge. No public city documentation found | [press] mmofolklorist, Dec 2022 |

### 1.5 The common path from founding to rank 5, pre-CU

Pre-CU rules from the Feb 2005 guide and FAQ [community][archive] (the same numbers are in the SWGANH wiki of 26 Aug 2009 [community]):

1. A **Politician** (Novice box: no skill points) places a City Hall deed that an Architect crafted (Construction IV). It cannot be redeeded. Planets are capped (20 or 50 cities) and the hall must be at least 1,000 m from other cities.
2. **24 hours** to get 10 citizens inside the 150 m radius, each by placing a house and declaring residence, or the hall and treasury are destroyed.
3. **Weekly update.** The city moves up **one rank per update** if it has the citizens (10, 20, 35, 55, 85), so rank 5 is four weeks away at the earliest. If it falls short, it is demoted and civic structures above its rank are destroyed.
4. Each rank unlocks structures (gardens, bank, garage, cantina, cloning, hospital, shuttleport, theater) and a radius (150-450 m). Specializations need rank 3.
5. **Upkeep** comes out of the treasury every week: hall 35k, 60k, 85k, 110k, 135k by rank, plus about 1.5k for each decoration, terminal and trainer. A city that cannot pay decays over about four weeks. Taxes and citizen donations fund it.
6. **Elections** every three weeks; the mayor earns political XP from updates and votes, which is what unlocks the later city powers.

What went wrong in practice: citizens drifting off (demotion), upkeep outrunning a small treasury, a mayor leaving, and the cap. What went right: a guild that kept recruiting, a site near services, and events.

## 2. How Core3 runs a city (and what our settings change)

### 2.1 Our settings against others

| Setting | Pre-CU 2005 [archive] | Late live ~2011 [community] | Core3 stock [code] | **Ours** [code] | Restoration | Legends | Stardust |
|---|---|---|---|---|---|---|---|
| Citizens per rank 1-5 | 10, 20, 35, 55, 85 | 5, 10, 15, 30, 40 | 2, 4, 6, 8, 10 | **1, 2, 3, 4, 5** | wiki 25 Sep 2026: 5, 10, 15, 30, 40; update 1.2.1 (1 Mar 2024): 16, 24, 32, 48, 64 (unresolved); 8-rank refresh planned | accounts/characters: 2/7, 3/14, 5/22, 7/35, 10/50 | 2, 4, 6, 8, 10 |
| Radius, m | 150, 200, 300, 400, 450 | same | same | **same** | same (1.2.1: 250-800) | 150, 200, 300, 425, 500 | same |
| Update | weekly | weekly | 10,080 min | **10,080 min** | weekly | weekly | weekly |
| Election | 3 weeks | 3 weeks | 3 updates | **3 updates** | n/a | n/a | page says 3 days |
| Hall upkeep rank 1 to 5, per week | 35k, 60k, 85k, 110k, 135k | wiki lists 3.5k to 13.5k (a tenth; unresolved) | 35k + 25k x (rank-1) | **x0.5: 17.5k, 30k, 42.5k, 55k, 67.5k** | 1.2.1: 50k x rank | 41k to 201k | n/a |
| Spacing from other cities | 1,000 m | not stated | 1,024 m centre to centre; NPC towns 2 x max(radius, 512) | **same** | 1,500 m | n/a | n/a |
| Cities per planet | 20 (core), 50 (others) | same | same | **same** | same | same | same |
| Founding window | 24 h | 24 h | `NewCityGracePeriod` 1,440 min | **same** | n/a | n/a | n/a |

Sources for stock and ours: `bin/scripts/managers/city_manager.lua` and `git log -p` on it (`4357970d`, the 13 Oct sandbox commit, changed `CitizensPerRank` from {2,4,6,8,10} to {1,2,3,4,5} and `maintenanceDiscount` from 1.0 to 0.5). The file keeps a commented-out {10, 20, 35, 55, 85}: that is the 2005 value.

**"Decorations" means three different things here; do not mix them.**
1. **City decorations:** statues, fountains and street lamps the mayor places outdoors: 10 per rank, 50 at rank 5 (`DecorationsPerRank = 10`).
2. **Items inside buildings:** furniture. Ours: 1,000 per lot, 10,000 maximum (`Core3.Sandbox.HouseItemsPerLot`, `HouseMaxItems`; `BuildingObjectImplementation.cpp:1056-1075`). Civic buildings hold 250.
3. **Event-perk props:** placeable rentals (AT-AT, banners, flags, stages); about 90 deed templates in Core3.

### 2.2 Founding, as Core3 does it

1. **Skill.** `social_politician_novice`: 0 skill points, 100 credits, no prerequisites; gives `place_cityhall`, `manage_taxes` and `grantZoningRights` (`Claude-class-check/professions.json`) [code/data].
2. **Deed.** `object/tangible/deed/city_deed/cityhall_{tatooine,corellia,naboo}_deed`. The three styles are limited to planets by `allowedZones`: Tatooine style on Tatooine, Lok, Dantooine; Naboo style on Naboo, Rori, Dantooine; Corellia style on Corellia and Talus (2005 FAQ; the Tatooine templates confirm their set).
3. **Placing.** `PlaceCityHallComponent::placeStructure` (`objects/tangible/deed/components/PlaceCityHallComponent.cpp:20-62`) checks the planet cap with `isCityRankCapped(planet, OUTPOST)` and "already mayor", then opens a window asking for the name. The window's callback, `PlaceCityHallSuiCallback.h:59-106`, runs the real checks in order:
   - name filter (`NameManager::validateCityName`);
   - `CityManager::validateCityInRange` (`CityManagerImplementation.cpp:350`): no other player city centre within 1,024 m;
   - `PlanetManager::validateClientCityInRange` (`PlanetManagerImplementation.cpp:1165`): no NPC town centre within 2 x max(its region radius, 512) m, so at least 1,024 m, and about 1,672 m from Theed if its radius is the 836 m of our bot table;
   - unique name; then `StructureManager::placeStructureFromDeed` (`StructureManager.cpp:270`) and, if that returns 0, `CityManager::createCity` (`CityManagerImplementation.cpp:196`).
4. **`placeStructureFromDeed`** checks the deed's faction, the planet (`isAllowedZone`), `isBuildingPermittedAt`, no-build zones, footprint overlap with anything within 128 m (`no_room`), city rank, zoning rights, mayor-only for civic structures, unique structures (one per city), the ability named in the template, and lots (`StructureManager.cpp:270-470`). It starts a `PlaceStructureSession` that puts up a construction barricade for 3 seconds per lot and places a temporary no-build circle of 64 m radius (`PlaceStructureSessionImplementation.cpp`). Then `StructureManager::placeStructure` (`:478`) creates the building, sets the owner, adds it to the owner's structures (which is what counts the lots) and sets its height to the ground at the placement point, or to the highest point inside the footprint when the template clears flora. **Core3 does not flatten terrain.**
5. **`createCity`** makes the `CityRegion` (persistent, in the `cityregions` database), sets the mayor, creates a 150 m region, schedules the 24-hour citizen assessment and the first update 7 days away, and mails the mayor.
6. **After construction** `PlaceCityHallComponent::notifyStructurePlaced` (`PlaceCityHallComponent.cpp`) sets the hall, builds a nav mesh (480 m extent, `CityRegionImplementation.cpp:627`), and declares the mayor's residence at the hall.
7. **Citizens.** A citizen is the owner of a declared residence inside the city (`StructureManager::declareResidence`, `:683`, which calls `registerCitizen`; `CityRegionImplementation.cpp:436-473` keeps only owners of residences). When a city grows over existing residences, `notifyEnter` registers their owners too (`:263-303`). The hall counts for the mayor. A player can be a citizen of one city.
8. **Assessment.** After 24 h `assessCitizens` (`:682`) destroys the hall if the citizens are below the rank-1 number. At our settings that number is 1, so a mayor alone passes.
9. **Zoning is on by default** (`CityRegionImplementation.cpp:62`): other players cannot place structures without `/grantZoningRights` (24 hours, mayor and militia; the target must be inside the city, `GrantZoningRightsCommand.h`). The mayor turns it off with `toggleZoningEnabled`.

### 2.3 Ranks, radius and caps at our settings

| Rank | Title | Citizens | Radius | Decorations / trainers / mission terminals (max) | Cities allowed at this rank or higher, core planets / others |
|---|---|---:|---:|---|---|
| 1 | Outpost | 1 | 150 m | 10 / 3 / 3 | 20 / 50 |
| 2 | Village | 2 | 200 m | 20 / 6 / 6 | 20 / 50 |
| 3 | Township | 3 | 300 m | 30 / 9 / 9 | 15 / 30 |
| 4 | City | 4 | 400 m | 40 / 12 / 12 | 10 / 20 |
| 5 | Metropolis | 5 | 450 m | 50 / 15 / 15 | 10 / 20 |

[code] `city_manager.lua:68-100`, `CityManagerImplementation.cpp:737-800, 1257-1358`. Planets in `CitiesAllowed`: Corellia, Naboo, Tatooine (core), Dantooine, Lok, Rori, Talus (others), all 260 slots in total; Dathomir, Endor and Yavin 4 are 0; **Hoth and Ossus are not listed at all**.

How rank moves: `processCityUpdate` runs on each city's timer. It cleans up citizens, gives the mayor 750 political XP, runs the election check, then compares citizens with the current rank's need: fewer means `contractCity` (one rank down, extra structures and decorations destroyed, the registration and specialization dropped below rank 3); enough for the next rank means `expandCity` (**one rank up**; if the planet's cap for that rank is full the city stays and is mailed "City Expansion Capped"). Then it reschedules at **7 days plus a random 0-30 minutes** (the jitter is in minutes: `(interval + random(30)) * 60` seconds, `:800`), charges income tax and pays upkeep. The first update comes exactly 7 days after founding.

### 2.4 Civic structures

| Structure | Rank | Lots | Ability (Politician box) | City upkeep per week, ours (stock) | Notes |
|---|---:|---:|---|---:|---|
| City hall | 0 (it creates the city) | 0 | `place_cityhall` (Novice) | 17.5k-67.5k (35k + 25k x (rank-1)) | unique; cannot be redeeded; holds 250 items |
| Small garden | 1 | 0 | `place_small_garden` (Urban III) | 5,000 (10,000) | five styles per planet; exotic gardens (Dantooine, Dathomir, Endor) need Urban IV |
| Medium garden | 2 | 0 | `place_medium_garden` (Urban III) | 10,000 (20,000) | |
| Bank | 2 | 0 | `place_bank` (Fiscal II) | 750 (1,500) | |
| Garage | 2 | 0 | `place_garage` (Civic II) | 10,000 (20,000) | |
| Cantina | 2 | 5 | `place_cantina` (entertainer masters) | none (owner pays) | citizen-placed; entertainers work here |
| Large garden | 3 | 0 | `place_large_garden` (Urban IV) | 15,000 (30,000) | |
| Cloning facility | 3 | 0 | `place_cloning` (Martial II) | 10,000 (20,000) | unique |
| Hospital | 3 | 3 | `place_hospital` (medic masters) | none | citizen-placed |
| Shuttleport | 4 | 0 | `place_shuttleport` (Fiscal II) | 12,500 (25,000) | unique; also enables the travel tax |
| Theater | 4 | 3 | `place_theater` (entertainer masters) | none | citizen-placed |
| Decoration, mission terminal, skill trainer | any | - | lamp/statue Urban I, fountain Urban II, terminal Civic I, trainer Civic II | 750 each (1,500); 1,000 to place, from the treasury | counts vs the 10/3/3 per rank caps |

[code] templates in `bin/scripts/object/building/player/city/*.lua`, `CityDecorationTask.h:40-130`, `deductCityMaintenance` (`CityManagerImplementation.cpp:845-934`); the ability to Politician box mapping is in `Systems-baseline/id-politician-gaps.md` 2.1.

### 2.5 Specializations (rank 3 or higher; one at a time; change once a week)

| Specialization | Weekly cost, ours (stock) | Effect | Does the server act on it? |
|---|---:|---|---|
| Sample Rich | 35,000 (70,000) | +20 sample size, +10 rate | yes (`ResourceSpawner.cpp`) |
| Manufacturing Center | 25,000 (50,000) | +10 assembly | yes (`SharedLabratory.cpp:146`) |
| Medical Center | 40,000 (80,000) | +10 medical rating | yes |
| Clone Lab | 40,000 (80,000) | `private_spec_cloning` +20 | **no reader: does nothing** |
| Research Center | 62,500 (125,000) | +15 experimentation | yes (`CraftingManagerImplementation.cpp:66`) |
| Improved Job Market | 40,000 (80,000) | +15 mission pay | yes (`MissionManagerImplementation.cpp`) |
| Entertainment District | 40,000 (80,000) | `private_spec_entertainer` +10 | **no reader: does nothing** |
| Stronghold | 75,000 (150,000) | +90 defence for militia | yes (`CombatManager.cpp:2030`) |

[code] `city_manager.lua:186-244`; consumers from `Systems-baseline/id-politician-gaps.md` 2.3, re-checked: no reader for the two. Live later removed Stronghold and added Beast Incubation (DNA Laboratory), Encore Performance and Outdoor Enhancement (+33% decorations and civic structures) in GU8 (12 Mar 2009) [official]. **New specializations need client data too:** the `city_spec_*` abilities come from the client's `skills.iff` and the names from string files.

### 2.6 Taxes, treasury and upkeep

- **Taxes** need rank 2 and the mayor's `manage_taxes` (`CityManagerImplementation.cpp:1846-1943`): income 0-2,000 per citizen per week (taken from the citizen's bank, `TaxPayMailTask`); property 0-50% on top of a citizen's building upkeep; sales 0-20% in vendors and the bazaar; travel 0-500 on tickets from the city shuttleport; garage 0-30% on vehicle repairs. At rank 1 there are no taxes.
- **Treasury.** Anyone can deposit (maximum 100,000,000). The mayor can withdraw 10,000-50,000 once a day. **Gotcha for any caller:** `depositToCityTreasury(city, creature, value)` takes `value` = the cash the depositor has **left**, not the amount deposited (`:617-640`: it subtracts `cash - value`). A bot that passes the amount it wants to give will give something else.
- **Weekly upkeep** (`deductCityMaintenance`, `:845`): hall first, then the other civic structures, decorations, terminals and trainers (750 each at our setting), map registration (2,500), and the specialization. A civic structure that cannot be paid for loses up to 25% of its condition per unpaid week (in proportion to the unpaid share) and is destroyed at 0; an unpaid terminal, trainer or loose decoration is destroyed at once; if the specialization cannot be paid it is dropped; if registration cannot be paid the city is unregistered.
- **Houses.** A citizen's own building pays its upkeep from the owner's bank each week (`StructureMaintenanceTask.cpp`). A small house is 16 credits an hour (ours 8): 1,344 a week. The city's property tax is added on top of that (`StructureMaintenanceTask.cpp`): at 50% the owner pays 672 more a week, and that goes to the city treasury.

**Worked costs at our settings** [calc]:

| City | Weekly upkeep | Highest tax revenue for that many citizens |
|---|---:|---:|
| Rank 1, 1 citizen, hall only | 17,500 | 0 (taxes need rank 2) |
| Rank 3, 3 citizens: hall + bank + garage + cloning + medium garden | 42,500 + 750 + 10,000 + 10,000 + 10,000 = 73,250 | income 3 x 2,000 + property 2 houses x 672 (the mayor lives in the hall) = 7,344 |
| Rank 5, 5 citizens: hall + bank + garage + cloning + shuttleport + one large garden + 50 decorations + 15 terminals + 15 trainers + registration + Research Center | 67,500 + 750 + 10,000 + 10,000 + 12,500 + 15,000 + 37,500 + 11,250 + 11,250 + 2,500 + 62,500 = **240,750** | income 10,000 + property 4 houses x 672 = 12,688 (sales tax adds some if shops exist) |

The first bot-hour income I have is about 50 credits per bot-hour from missions [measured: `numbers-run7-early.md`, run 7], or 8,400 per bot-week if a bot worked every hour. Five such bots could carry rank 1 and 2 (17,500 and 30,000 for the hall), not rank 3 with services. A real group of friends starts with 110,000 credits each and richer income, so for them the same numbers are easy; they matter for bots and for a fully built town.

### 2.7 Elections and the Politician ladder

- Election every `CityVotingCycles = 3` updates (about 3 weeks); registration locks for the last cycle. A candidate must be a citizen with Novice Politician and not the mayor of another city (`:2207-2264`); one registration per 24 hours. The incumbent must register to stand; with no candidates the incumbent stays (`:1118-1255`). A new mayor inherits civic structures, decorations and the specialization cooldown.
- **XP.** The mayor gets 750 political XP at every update and 300 per vote received at an election. The Politician boxes cost political XP only: Fiscal/Martial/Civic/Urban I-IV cost 1,000, 2,500, 5,000 and 10,000 each (`professions.json`). At 750 a week, Fiscal I plus II (3,500) takes about 5 weeks; Urban I-III (8,500) about 12 weeks; all four ladders (4 x 18,500 = 74,000) about 99 weeks [calc]. Each box also costs credits: 1,000, 2,000, 3,000, 4,000 up each ladder, and 5,000 for Master. Cities rank up in 4 weeks, so **the mayor's powers lag the city by months** unless staff force updates (the hall's God-mode "City Hacks" menu: force rank, force update or election).

### 2.8 Militia, bans and law

The mayor and militia can `/grantZoningRights`, `/cityBan` and `/cityPardon`. The text promises militia may "attack visitors for the purposes of law enforcement" (`:1480`) but **no code gives that power** (`id-politician-gaps.md` 2.2). `EnableCityWarn = false` exists in the Lua, with no `/cityWarn` command behind it.

### 2.9 Calendar: what runs in real time

Update 7 days; election 3 weeks; founding window 24 h; specialization cooldown 7 days; treasury withdrawal 24 h; zoning rights 24 h; residence change cooldown 24 h; house upkeep weekly per structure. Nothing here is scaled by the sandbox except upkeep (x0.5).

### 2.10 What Core3 does not have (that live had at the end)

No 90-day inactive-citizen purge (Game Update 8, 1 May 2009), no city faction alignment, banners or invasion (Forces Under Siege, GU15 [press: Shacknews and a patch-note repost]), no Beast Incubation, Encore Performance or Outdoor Enhancement specializations, no Storyteller (the closest thing is the event-perk system, 4.2).

### 2.11 Broken or missing in Core3, ranked for us

1. **Hoth and Ossus cannot found cities safely.** They are not in `CitiesAllowed`; `isCityRankCapped` reads `citiesAllowedPerRank.get(planet)` (empty) and indexes `get(rank-1)` (`CityManagerImplementation.cpp:225-248`). I expect an array-index exception on the deed's first use. [code][untested]
2. **Clone Lab and Entertainment District specializations cost 40,000 a week and do nothing** (2.5).
3. **City-hall flows open windows** (name box, specialization, tax, mission terminal and trainer callbacks): any client-less caller must bypass them (3.2).
4. **Weekly cadence hides the system in tests** (staff can force updates from the hall).
5. **Militia have no powers beyond ban and zoning; `/cityWarn` does not exist; `/unCityBan` and the city guard spawner commands are empty stubs** (`StartCitySpawnerCommand.h`, `StopCitySpawnerCommand.h`); `ai/cityPatrol.lua` exists and 24 mobile scripts use it as a patrol AI, but nothing spawns guards for a player city.
6. **No inactive-citizen purge**: a dead city keeps its slot while its mayor and houses still exist (live's lesson).
7. **Dead settings and mismatches:** `CityVotingDuration` is read by the C++ but does not exist in the Lua (it is unused); the comment says the specialization cooldown is in minutes but the value is milliseconds; the client strings still say "at least 10 citizens" (the server needs 1).
8. **`ShuttleInstallationImplementation.cpp:11-30`**: its own mayor and unique checks are commented out (the general checks cover it).
9. **Source TODOs:** only one in the city manager (`:2320`, a chat refactor) and a "remove" note on `cleanupDuplicateCityStructures` (`CityRegion.idl:820`). The city code is otherwise unmarked, which fits "faithful but little tested".

## 3. Part 1: how our server bots found and grow a city

### 3.1 Goal and scope

Give the launch simulation a **settler** population that behaves like a friend group founding a town: choose a site, place a city hall, bring in citizens with houses, let the weekly update promote the city, run taxes and an election, build the civic structures its rank allows, then decorate and trade. It exists to **measure** (time to each rank, credits, upkeep load, server cost) and, later, to **seed** example towns (Part 2). **Test galaxy only**, behind `isDisposableTestGalaxy()` as `/botpop` is (`BotPopCommand.h`) and a new `Core3.BotPopCities` flag. No code is written here.

### 3.2 Facts from Core3 that shape the design

| # | Fact | Why it matters |
|---|---|---|
| F1 | Citizen = owner of a declared residence inside the radius | Settlers must place a house and call `declareResidence`; nothing else makes a citizen |
| F2 | Rank moves one step per update; updates are 7 days apart (+0-30 min) | Without a clock change, rank 5 takes 4 real weeks; the harness needs a compressed clock |
| F3 | Zoning is on for a new city | The founder must switch it off (or grant rights) before settlers place houses, or they get `no_rights` |
| F4 | Stock flows open windows | `SuiPageData::sendTo` dereferences `getClient()` without a null check (`SuiPageData.cpp:146-158`; also found in `Documentation-support/server-side-bots.md`). Bots must call the manager methods and the inner logic of the callbacks, never `PlaceCityHallComponent::placeStructure` |
| F5 | Civic structures: mayor only, rank gate, ability gate, no lots | The mayor needs the Politician boxes; ability costs are political XP (2.7) |
| F6 | A character has 10 lots; small house 2, large 5, cantina 5, hospital 3, theater 3 | Up to five small houses each; a cantina takes half a character's lots |
| F7 | `StructureMaintenanceTask::run` destroys a structure whose owner has no player name (`getPlayerName(oid)` empty) or no credit object | Bot-owned houses will likely die at their first maintenance run: transient bots have no database row. [untested: probe 1] |
| F8 | `PlaceStructureSession` calls `placeStructure` with the default `persistenceLevel = 1` (`StructureManager.h:64`) | Structures made by the session are persistent even when the owner is not, so they would outlive a restart as orphans |
| F9 | A construction places a 64 m no-build circle for 3 s per lot | Serialize placements within 64 m; the next one waits for `completeSession` |
| F10 | Launch-brain code runs inside one bot's step with the bot locked | City actions lock city, mayor and structures (`Locker clocker(city, mayor)`); run them as queued tasks, as `CityRegion::notifyEnter` does with `executeTask` |
| F11 | Cities are capped per planet (260 slots in all) and the first update is 7 days away | A bot program can fill the planets and lock real players out |
| F12 | Bots die and are replaced after being dead too long (`BotState::replace`) | A mayor must not be replaced; settlers stay in town like medics and entertainers (radius 35 m) |

### 3.3 The cast

Per bot city (default "Standard" town, 5 bots; "Small" 3; "Large" 8 to 12 in M3):

| Role | Count | Skills | Job |
|---|---:|---|---|
| Mayor | 1 | Novice Politician (0 SP, 100 credits). Political boxes by schedule (3.5) | founds, sets zoning and taxes, places civic structures and decorations, registers for election |
| Settler | 2-6 | any launch role (a medic or entertainer is best) | places a house, declares residence, votes, donates, decorates, works in town |
| Entertainer | 1 (of the settlers) | `social_entertainer` | dances in the plaza or cantina (the existing town-hub effect) |
| Medic | 1 (of the settlers) | `science_medic` | heals hurt hunters in the plaza |
| Shopkeeper | optional, M4 | Merchant novice | places a vendor and stocks it |

Settlers are a new launch role next to `BRAWLER ... EXPLORER` in `LaunchState` (BotPopLaunch.h): town-bound, never hunting, never replaced.

### 3.4 Where: site selection

1. **Candidates, offline.** `tools/bots/ossus_census.py` already finds flat 256 m squares from the explorers' ground samples (Ossus: 245 flat squares of 3,472, 4 samples within 4 m). A city needs more than one square: the radius grows from 150 m to 450 m, so the planner wants a **cluster** of 2x2 adjacent flat squares (512 m) as the core of a town meant to reach rank 5, and one square for an outpost. The outer rings (to 450 m) may cross rougher ground, so the server check below scores the share of flat 30 m cells inside each rank's radius. Run the census per planet; keep the top 5 clusters per 2,000 m window.
2. **Verify, server-side**, with the calls the stock flow uses:
   - `TerrainManager::getHighestHeightDifference(x-15, y-15, x+15, y+15) <= 3` for each 30 m lot cell (the event-perk deed uses 15 m over 20 m: `EventPerkDeedImplementation.cpp`);
   - `PlanetManager::isBuildingPermittedAt`, `findObjectInNoBuildZone`, `validateClientCityInRange` (NPC towns), `CityManager::validateCityInRange` (other cities), name checks;
   - not on water, not within 128 m of a lair, camp, POI or another structure's footprint;
   - at least **1,400 m** from any other player city centre (the code needs 1,024; the extra covers a 450 m radius).
3. **Quota.** Bots may use at most **30% of each planet's slots at each rank** (core planets: 6 cities, others: 15), and no bot cities on the planet the owner is testing on. The city report counts the free slots left for people.
4. **Placement coordinates.** Houses are placed on a ring or grid around the hall inside the current radius (150 m at founding), 12 m apart as a minimum, rotated to face the hall; later buildings go in the ring the next rank's radius opens (200 m, 300 m, 400 m).

**Archetypes** (each is a layout recipe plus a decoration palette; names from our own word lists, themed to 138-139 ABY, no real names):

| Archetype | Evidence it is real | Layout |
|---|---|---|
| Crafters' market | Black Sun Ravine, Bantha Cairns, Elysium malls | hall, plaza, ring of shops and houses, Research Center |
| Role-play town | Black Sands, Pelgo | main street with cantina at one end, amphitheater (theater) at the other |
| Guild fortress | Hero's Legacy, Echo Base | tight compound near the hall, turrets/flags as props |
| Hunters' outpost | Honour-style guild satellite | small, near wildlife, a garage and garden |
| Temple camp | "Temple", "Jedi", "Sith" names (16 in the 2011 list) | ruin-themed ring on Ossus, no shuttleport |
| Port town | Elysium (shuttleport, garage), Honour Outpost | shuttleport at the edge, bank and garage on the road |

### 3.5 Order of work (organic against accelerated)

"Week" is a city update. **Organic** uses only what the natural political XP allows; **accelerated** grants the XP or the ability flags on a schedule and logs the grant. Run both and compare.

| Week | City rank (5 citizens) | Mayor does | Settlers do | Gate and organic reality |
|---|---|---|---|---|
| 0 (T+0) | 1 (after the 24-hour assessment) | takes Novice Politician; places the hall (3.9 steps 1-4); turns zoning off | each places a small house (serialized, 6 s each) and declares residence | all organic; citizens reach 5 in minutes |
| 1 | 2 (update 1: 750 XP) | sets income tax and property tax (rank 2) at a low value | one donates to the treasury | taxes need rank 2 and `manage_taxes` (Novice) |
| 2 | 3 (update 2: 1,500 XP) | learns Fiscal I (1,000 XP, then `city_map`); registers for the election (the ballot locks for the last cycle, so by now); places a garden if Urban III is held (accelerated) | place the cantina/hospital if the role has the master ability (accelerated); a settler may register as challenger | Urban III needs 8,500 XP: about week 12 organic |
| 3 | 4 (update 3) | election result arrives with update 3 (roughly; the 0-30 minute jitter can push it across) | vote during weeks 0-3; one settler stands as challenger in 30% of cities | 300 XP per vote received |
| 4 | 5 (update 4) | chooses a specialization (rank 3+; the ability comes from Fiscal III-IV, Martial II-III or Civic III-IV, so accelerated); registers the city on the map (Fiscal I, rank 3) | decorate houses; entertainer dances in the plaza | the city reaches Metropolis; stock structures wait on political XP |
| 5+ | 5 | pays upkeep, places lamps/statues/fountains (Urban I-II) with the schedule | keep donating by a rule (3.6) | upkeep 17.5k-240k; see 3.6 |

### 3.6 Government behaviour

- **Taxes.** Mayor sets income tax by the treasury's runway: if (treasury / weekly upkeep) is under 2, raise income tax in 250 steps up to 2,000; over 4, lower it. Property tax fixed at 10%. The sales tax stays 0 until shops exist.
- **Donations.** Each settler donates `d` percent of its bank at every update where the runway is under 2 (default `d` = 25). Remember the `depositToCityTreasury` argument is the cash left (2.6).
- **Elections.** Mayors register in week 2 (the ballot locks after two updates) so the XP path is recorded. 30% of cities get a challenger (a settler with Novice Politician). Votes: 70% incumbent, 30% challenger, one abstention per city. The result mail and the XP change are logged.
- **Specialization** (rank 3+; the ability comes from the Politician box in brackets, from `professions.json`). By archetype: Crafters' market Research Center (Fiscal IV); Role-play town Entertainment District (Civic III; a real effect only after 2.11 item 2 is fixed, until then log it as a stub); Guild fortress Stronghold (Martial III); Port town Improved Job Market (Civic IV); Temple camp Sample Rich (Civic IV); Hunters' outpost Medical Center (Civic III). Cost 25,000-62,500 a week, so most cities cannot afford one before week 6 without donations.

### 3.7 The compressed clock

The weekly cadence is data. For the **test galaxy copy only** (never live, never the dev tree's shipped file) set in its `city_manager.lua`: `CityUpdateInterval = 6` (minutes), `NewCityGracePeriod = 3`, `OldCityGracePeriod = 6`, `CitySpecializationCooldown = 6 * 60 * 1000`, `TreasuryWithdrawalCooldown = 3 * 60 * 1000`, and keep `CityVotingCycles = 3`. One simulated week is 6 minutes, rank 5 comes at 24-27 minutes, the first election at 18 minutes. Two caveats:
- The jitter `System::random(30)` adds up to **30 minutes**, five times the interval (`CityManagerImplementation.cpp:800`). Either change it to `random(max(1, interval / 6))` (one line) or drive `processCityUpdate` from the harness at fixed times.
- House upkeep (`StructureMaintenanceTask`) stays on real time (weekly). Count it as a computed figure beside the city's treasury.

### 3.8 Decorating and giving life

- **City decorations** (Urban I for lamps and statues, Urban II for fountains): `CityDecorationTask(mayor, object, PLACE)` places at the **mayor's own position**, so the mayor must walk to each spot (`CityDecorationTask.h:64-130`). It takes 1,000 from the treasury and needs the treasury to hold at least that. Palette per archetype from the client's street lamps, statues and fountains (`bin/scripts/object/tangible/furniture/city/`).
- **Inside houses:** furniture goes into cells with `transferObject` and a cell position; keep a **density** knob (0, 25, 100, 500 items per lot) and measure memory per 1,000 items. Our caps are 1,000 per lot and 10,000 per house.
- **Life.** The entertainer dances and the medic heals at the hall's plaza, so hurt hunters rest there: that is the effect the launch simulation already measured (2,659 of 2,661 rests). M4 adds a vendor per shopkeeper and a schedule of events (market day, dance night) as bot behaviours.

### 3.9 Core3 calls the bots need

| Step | Call | Notes |
|---|---|---|
| Create a deed | `zoneServer->createObject(templateCRC, 0)` (used for items at `BotPopManager.h:378`), then `inventory->transferObject` | templates under `object/tangible/deed/city_deed/` and `player_house_deed`; a made deed has 0 surplus maintenance |
| Learn Novice Politician | the launch brain's training code (`BotPopLaunchBrain.h:333-374`), skill name `social_politician_novice` | 100 credits; the starting purse of a bot is 0, so grant credits |
| 1. Check the site | `validateClientCityInRange`, `validateCityInRange`, `validateRegionName`, `validateCityName`, `isCityRankCapped`, `isBuildingPermittedAt` | the order of `PlaceCityHallSuiCallback.h:93-97`; no window |
| 2. Place the hall | `StructureManager::placeStructureFromDeed(bot, deed, x, y, angle)` | returns 0 when a session started |
| 3. Make the city | `CityManager::createCity(bot, name, x, y)` immediately after step 2 returns 0 | the hall's `notifyStructurePlaced` needs the region to exist when construction completes |
| 4. Open the city | `CityManager::toggleZoningEnabled(city, mayor)` (IDL line 199) | the first call turns zoning off |
| 5. Settler houses | `placeStructureFromDeed`, then, when the session ends, `StructureManager::declareResidence(bot, building)` (`:683`) | a house outside the radius is not a citizen's |
| Assess | `CityManager::assessCitizens(city)` | the 24-hour check, compress with 3.7 |
| Advance the clock | `CityManager::processCityUpdate(city)` (IDL line 98) | also reschedules the natural timer |
| Taxes | `CityManager::setTax(city, mayor, index, value)` (`:1915`); 0 income, 1 property, 2 sales, 3 travel, 4 garage | rank 2+ |
| Treasury | `depositToCityTreasury(city, bot, cashLeft)` | argument is cash left |
| Election | `registerForMayoralRace(city, bot)` (`:2207`), `castMayoralVote(city, bot, oid)` (`:2179`) | citizen, Novice Politician, 24 h |
| Specialization | `changeCitySpecialization(city, mayor, key)` (`:404`) | the key is the name in `city_manager.lua` (`@city/city:city_spec_...`); rank 3+ and the spec ability |
| Map | `CityManager::registerCity(city, mayor)` (`:1762`) | rank 3+, `city_map` |
| Civic structures | `placeStructureFromDeed` with the right deed | mayor only, rank and ability gates |
| Decorations | `CityDecorationTask` | at the mayor's position |
| Terminals, trainers | the inner logic of `InstallMissionTerminalSuiCallback.h` and `RecruitSkillTrainerSuiCallback.h:187` | refactor each into a function a bot can call |
| XP and abilities | `PlayerObject::addExperience(trx, "political", n, true)`; skill grants through `SkillManager` | accelerated mode only; log each grant |
| Teardown | `CityManager::destroyCity(city)` (`:1360`) **and** a destroy of every bot-owned structure | `destroyCity` removes the hall, civic structures and decorations, but houses stay as orphans |

Two code additions the plan needs, small: a **bot-owned placement path** that runs the same checks as `placeStructureFromDeed` but ends in `placeStructure(..., persistenceLevel 0)` (F8), and a **city-object variant** that creates the `CityRegion` and its regions non-persistent (`createCity` uses `persistObject(city, 1, "cityregions")`).

### 3.10 What it measures

One JSONL stream beside `log/botpop-launch.jsonl` (`botpop-city.jsonl`), same writer (`SimLog`), plus `tools/bots/botpop_city_report.py`.

| Question | Events and fields | Report |
|---|---|---|
| Time to each rank | `city_found{city,planet,archetype,x,y,mode}`, `city_rank{city,from,to,citizens,simWeek,realMin}` | median real minutes and simulated weeks to ranks 2-5, by archetype and mode |
| Citizens | `citizen_join{city,bot,house}`, `citizen_leave{reason}` | joins per hour, failures by reason (`no_rights`, `no_room`, `not_permitted`, lots) |
| Credits | `treasury{city,balance}` each simulated week, `deposit{bot,amount}`, `tax_paid{kind,amount}`, `upkeep{kind,amount}`, `decay{structure}` | inflow by source, outflow by item, weeks of runway, share of bot income spent on the city |
| Maintenance load | `upkeep_total{city,week,cost,paid}`, `structure_destroyed{reason}` | cost per week against rank, first week a city cannot pay, structures lost |
| Governance | `tax_set`, `candidate`, `vote`, `election{winner,votes}`, `political_xp{from,source}` | elections held, turnover, XP per week |
| Structures | `placed{type,rank,lots,ms}`, `place_fail{type,reason}` | counts by type, fail reasons, placement latency |
| Server cost | per minute from the `[BotPop]` line: pass and step times, RSS, object count; `navmesh{city,ms}`; per-city object count | memory per city and per 1,000 items; pass time with 0, 10, 40 cities; nav-mesh time |
| Site quality | `site{planet,score,flatness,searchMs}` | share of candidates that fail the server checks |

### 3.11 Risks, ranked

1. **Owner and persistence (F7, F8).** Bot-owned structures are destroyed at the first maintenance run or orphaned after a restart. Mitigation: all bot-city objects non-persistent; the test galaxy's restart then removes them; `destroyCity` plus a sweep by owner id for clean-up. Prove it in probe 1.
2. **Clock (F2).** Without 3.7 the system shows nothing in a session. Mitigation as 3.7; `Force City Update` already exists for staff.
3. **Slot grab.** Bots take real players' city slots. Mitigation: the 30% quota, a per-planet allow-list, and `destroyCity` for all bot cities before any human test.
4. **Window flows crash a bot (F4).** Mitigation: call only the manager methods and extracted callback logic; add the one-line null guard in `SuiPageData::sendTo`.
5. **Empty `CitiesAllowed` entry** (2.11 item 1). Do not test on Hoth or Ossus until `CitiesAllowed` lists them and `isCityRankCapped` guards a missing key.
6. **Locks (F10).** Inline calls from a bot step can deadlock with the city and structure locks. Mitigation: queued tasks, lock order city then mayor.
7. **Treasury wall (2.6).** Expect cities to stall at rank 3 or 4. This is a result, not a bug; the donation policy and an `--endow` switch (harness donates to a floor) let a run go further and log it.
8. **Nav mesh and objects.** Every city builds a 480 m nav mesh (`CityRegionImplementation.cpp:627`) and every house adds cells; 40 cities at once could queue a lot of Recast jobs. Start at 5 cities, step to 10, 20 and 40, and stagger founding by 20 s.
9. **Memory.** Memory already creeps 0.9 to 1.6 GB an hour at 1,500 bots (`FINDINGS.md` section 1). Add city objects only after that is understood, and keep an off switch.
10. **Names.** City names come from our own word lists and pass `NameManager`; none from real people or guilds.
11. **Spec effects are partly stubs** (2.11 item 2); the harness records a spec as chosen, not as working.
12. **Political XP shortcut** changes the result. Keep the organic mode as the baseline.

### 3.12 Build plan and probes

- **Probe 0 (half a day, no new code if the harness can run a console command):** from the console, as a god-mode character in the test galaxy: place a hall from a deed in a flat spot on Tatooine, then `Force City Update` from the hall's menu twice; confirm rank, mails, the treasury, and that `destroyCity` leaves no orphans. Learns the stock flow.
- **Probe 1 (1 day):** a transient bot owner. Create a bot, give it a house deed, call `placeStructureFromDeed` with persistence 0 variant, `declareResidence`; log out; wait one maintenance interval (or call the task); see if the structure survives and what the log says (F7).
- **Probe 2 (half a day):** `isCityRankCapped("ossus", 1)` and the same for `hoth`, to see the empty-vector behaviour (2.11 item 1).
- **Probe 3 (half a day):** `depositToCityTreasury` argument semantics, `setTax` at rank 1 and 2, `toggleZoningEnabled`.
- **Probe 4 (half a day):** the compressed-clock values on a scratch copy; confirm the jitter and the election timing.
- **M1 (3-5 days):** `SETTLER` role, site planner (offline picker plus server check), one Standard city per planet, events and the report. Hypotheses to test: H1, five bots reach rank 5 at update 4; H2, treasury goes negative before rank 3 without donations; H3, nav mesh is under N ms per city.
- **M2 (3-4 days):** taxes, donations, election, specialization, map registration, accelerated mode, the other five archetypes.
- **M3 (2-3 days):** scale to 10, 20 and 40 cities across planets with the quota; server-cost curves.
- **M4 (4-6 days):** decorations, furniture density, shops, events; the persistent "town keeper" mode for Part 2 (4.3 item 9).

Estimates are [est]. Claude builds, ChatGPT reviews, per `AGENTS.md`; the test galaxy and its restarts follow the server lock.

## 4. Part 2: encouraging creativity in city design

### 4.1 What pushed players to build distinctive cities (evidence)

| Mechanic | Where, when | Effect | Source |
|---|---|---|---|
| **Contests with a prize or badge** | Legends monthly Galactic Home Show with themes (2023); Empire in Flames first show Jun 2023 (winner's badge); Restoration GCW-themed show, 5-million prize (Jul 2023); Finalizer first show 26 Jun-5 Jul 2023; Infinity Best Dressed City, 135-million prize (May 2023) | entries use "props and furniture to its fullest"; winners publicised; repeatable and cheap | [press] mmofolklorist Mar-Jul 2023 |
| **Free-form object placement** | live "advanced object manipulation system": sculptures, pod-racers from hundreds of parts, a custom starport; decorators wrote macros for the slow slash commands | the engine of creativity: renaming crafted items to reuse them (a painting as a shower tile) | [press] PC Gamer 16 Dec 2011; Engadget 9 Dec 2011 |
| **Better tools** | SWGEmu added rotate on every axis (Apr 2023); Core3 `/rotateFurniture` with yaw, pitch or roll; Restoration Storyteller blueprints save a scene to redeploy; a community city-map planner existed on live | lowers the cost of a good layout | [press] mmofolklorist Apr 2023; [code] `RotateFurnitureCommand.h`; [community] Restoration wiki; SWG wiki links |
| **Decoration limits that grow** | live Game Update 8: base decorations and civic structures +50%; Outdoor Enhancement specialization +33%; Restoration June 2024: decorations and gardens lost city upkeep, props placed in a city stopped expiring, 3-million-credit payout to compensate | caps and upkeep were the brakes on creativity; backlash when upkeep rose | [official] Game Update 8 notes; Restoration 1.2.1 (1 Mar 2024) and 1.2.3 (10 Jun 2024) |
| **Props that persist** | Storyteller (Chapter 6, 22 May 2007, tokens at theatre vendors; static props, effects, NPCs); Restoration: static props in a city no longer expire (1.2.3), mayors and militia can remove them; Storyteller items last 8 extra hours in a city, "Encore Performance" specialization 12 more | stage dressing, event sets, fake landmarks | [press] Shacknews and Engadget coverage via search; [official] Game Update 8; Restoration notes |
| **Specializations as identity** | live 9 specializations; Restoration refresh: ~25 planned, major and minor, "forcing trade-offs" so every city differs | the city says what it is for | [official] Restoration dev diary, 24 Aug 2026 |
| **New planets with their own cities** | Legends Bespin (Cloud City apartments), Felucia; Stardust's added planets (one city each) | new ground and new styles | [press] MassivelyOP; [community] Stardust wiki |
| **House-style limits** | Elysium: 1 of 3 pre-approved houses; Empire in Flames: anti-sprawl housing | a shared look | [community] SWG wiki; [press] MassivelyOP |
| **Recognition** | Restoration "Player City Spotlight" posts (at least eight in 2024-25; I read five); SOE's public city list; badges for events | pride and visitors | [official] swgr.org; [official][archive] SOE list |
| **Terrain** | the planners' constant complaint; terraforming deferred | cities move or accept ugly ground | [official] Restoration spotlights and diary |

What did **not** work or backfired: raising upkeep and thresholds without warning (Restoration 1.2.1, "took some players by surprise", apology and payout); relying on thresholds alone to clear dead cities (Legends 2019: "not entirely clear" it would change much); Stronghold (removed on live in 2009).

### 4.2 What our server already has

- About 90 **event-perk** deeds (91 carry a perk type: 40 static props, 24 theater sets, 20 honour guards, 4 games, 2 recruiters, 1 NPC actor; examples: an AT-AT and AT-ST, banners, flags, stages), sold by the event promoter and perk vendor (`bin/scripts/screenplays/events/eventPromoter.lua`, `eventPerkData.lua`, `mobile/misc/event_perk_vendor.lua`), with timers (`generatedTimeToLive`), a terrain check (height difference over 15 m across a 20 m box is refused), zoning checks in cities and "no more than 3 within 32 m". This is a Storyteller-lite.
- `/moveFurniture`, `/rotateFurniture` (yaw, pitch, roll), `/vertFurniture`, item move/rotate, 1,000 items per lot.
- 55 garden building templates, 6 statues, 16 street lamps and 7 fountains for cities (`bin/scripts/object/tangible/furniture/city/`).
- `/grantBadge` for staff (`GrantBadgeCommand.h`) and the server's badge list (`Badges.h`); check it for unused IDs before reusing one.

### 4.3 Ranked ideas for our small friends' server

Rank order is value for a few friends per unit of effort. Cost: **S** under 1 day, **M** 2-5 days, **L** over a week [est]. "Client" means a change to client files (our test archive), which the owner has already used for Hoth terrain.

| # | Idea | Needs | Cost | Why it should work here | Risk |
|---:|---|---|---|---|---|
| 1 | **Home Show and Best Dressed City contests**, monthly, with themes (138-139 ABY: "Imperial Remnant", "Jedi in hiding", "Frontier"), a credit prize and an existing badge | staff process; screenshot rules; `/grantBadge` with an existing unused badge ID (new badge text needs a client string file); Discord posting (C17, after the owner's go) | S | Five servers ran it in 2023; it needs no code; a small server can judge by hand | judging fairness; the owner's Discord approval |
| 2 | **Raise decoration freedom:** `DecorationsPerRank` 10 to 30, decoration/terminal/trainer upkeep to 0 (a config key replacing the hard-coded 1,500 in `CityManagerImplementation.cpp:889, 895, 900` and the report at `:2050, 2064, 2074`), placement cost 1,000 to 100 (a constant in `CityDecorationTask.h`) | Lua; about 10 lines of C++; `maintenanceDiscount` is shared with structures so a separate key is cleaner | S | live raised caps by 50%; Restoration removed upkeep after backlash; our rank-5 decoration upkeep is 37,500 a week, 15% of a full town's bill | cap hit by many props: object count |
| 3 | **Make all eight specializations real:** read `private_spec_cloning` (cheaper clone or shorter sickness) and `private_spec_entertainer` (buff strength or duration) | about 10 lines each, in `PlayerManagerImplementation::sendPlayerToCloner` and the entertaining session | S | currently two of eight cost 40,000 a week and do nothing; identity needs choices that work | untested effect sizes |
| 4 | **Pre-flattened founding sites:** 6 to 10 curated plateaus per planet, each with a waypoint and a one-line brief, using the bots' flat-square census and a terrain flatten layer (the owner's client already loads edited Hoth terrain from the test archive) | terrain edit per site (client and server read the same terrain), Lua waypoints, the census (exists) | M | the planners' main complaint was ground (Mos Pelgo moved twice); Core3 does not flatten | client file work; every site needs checking against NPC no-build zones |
| 5 | **Mayor-pinned static props** (Restoration 1.2.3): a mayor or militia member can mark a static event-perk prop in the city as permanent, free of rental time, up to a props cap; the mayor can remove them | C++ small (an `EventPerk` flag and a per-city counter); Lua list of allowed props | S-M | stage sets and a landmark without upkeep; reuses 40 existing static props | exploitation as free decor; keep a cap |
| 6 | **Rank rewards that are visible, not powerful:** rank 3 a banner and flag set; rank 4 a plaza prop slot; rank 5 one "landmark" slot beyond the decoration cap (pick one from a short list of large client props) | Lua list; C++ small for the slot | M | with ranks reached in four weeks, rank 5 would otherwise be "the end game" (Restoration's complaint); a landmark becomes the city's signature | the large props must exist in the client data (check the list first) |
| 7 | **Spotlight and gallery:** a "City of the month" post and a screenshots channel; register cities on the planetary map at rank 3 (exists) | staff time; Discord | S | recognition drove Restoration's series; visitors are the reward | Discord approval |
| 8 | **City-ready Ossus and Hoth:** add both to `CitiesAllowed` (with a small cap, 3 to 5), fix the empty-key index, and place flat plateaus at the census sites | Lua; C++ small guard; Ossus census | S-M | Legends' new planets were headline content; Ossus is the next planet | probe 2 first |
| 9 | **Bot-seeded example towns** (Part 1 archetypes) built by a persistent staff "Town Keeper" character, in the test galaxy first, as examples to visit and copy | the bot harness (3.12 M1-M3); a persistent-owner mode; a clean-up list | M-L | new players see six distinct designs before they place a house; shops and a cantina give life | persistence (F7); a town of bots must not block human slots |
| 10 | **Bots fill shops and give a city life:** vendor bots with stock priced from a table, entertainers and medics at the plaza, scheduled events | M4; vendor placement from `VendorManager`; stock from loot and junk | M | merchants gather in busy cities; our hub effect is measured | unbalanced prices; economy noise |
| 11 | **Mayor's style rule:** a city may limit the house styles it allows (Elysium's three pre-approved houses; Empire in Flames' anti-sprawl) | C++ small in the zoning check; a per-city Lua whitelist | M | gives a mayor a tool to keep a theme | friction between friends |
| 12 | **Blueprints and a web planner:** save a layout of decorations and redeploy it (Storyteller blueprint idea); a web city map maker using real footprints | in-game version L (C++); web tool S-M (Python or JS, uses template footprints) | S (web) / L (in game) | cuts the cost of a good layout; the web tool helps bots and people | scope |
| 13 | **New civic structures:** a park, a landing pad (Legends' newsletter, spring 2024), a library or observatory themed to the setting | Lua templates plus existing client meshes; new meshes via the asset pipeline (Fable) | M-L | more things to build for the same rank | client art rights; check each asset |
| 14 | **City guards:** make `/startCitySpawner` spawn `cityPatrol` guards at rank 3+ | C++ plus Lua | M | atmosphere; was in live design (stub here) | spawn load |
| 15 | **Terraforming** | client terrain runtime edits | L | Restoration deferred it too | out of reach now |

**Where the bots help** (ideas 9, 10 and parts of 1, 4, 6): seed varied example towns; fill shops; keep plazas busy with dancers and medics; test the cap and upkeep settings before humans meet them (the treasury wall in 2.6 is the first case); and measure the cost of 10,000 decorations before the owner raises the cap.

### 4.4 A suggested first month

1. Week 1 (no code): contest rules, a prize, a badge choice; ideas 1 and 7 written up for the owner's Discord decision.
2. Week 1-2 (small): ideas 2 and 3 (about 40 lines in all) and idea 8's Lua and guard, after probe 2.
3. Week 2-3: bot probes 0-4 and M1; idea 4 for the first two sites on Tatooine and Rori.
4. Week 4: idea 5 and idea 6 design; M2; decide idea 9 from the bots' data.

## Owner's questions

1. **Persistence for bot cities.** Should bot cities be disposable (non-persistent; gone at every restart, recommended for the simulation) and the persistent example towns come later from a staff "Town Keeper" character, or do you want persistent bot towns from the start?
2. **Clock.** May I set a compressed city clock (one simulated week = 6 minutes) in the **test galaxy's copy** of `city_manager.lua` only, never on the live galaxy, and change the update jitter line? The alternative is to drive updates from the harness.
3. **Slot share.** What share of each planet's city slots may bots use (I propose at most 30%), and on which planets (not the one you are testing on)?
4. **Political XP shortcut.** Is it acceptable to grant political XP or ability flags to bot mayors in an "accelerated" run, with the natural run kept as the baseline? Both are logged.
5. **Treasury.** Cities at our settings cannot pay their upkeep from taxes. Do you want (a) the bots to donate and the harness to top up a floor, (b) a lower `maintenanceDiscount` on the test galaxy, or (c) to leave the numbers alone and treat the stall as the finding? And is 0.5 the number you want for the friends' server?
6. **Contests.** Do you want a monthly Home Show / Best Dressed City, and what prize (credits, an existing badge)? Posting needs your Discord go.
7. **Decoration cap.** Raise `DecorationsPerRank` from 10 (to 30?) and make decoration upkeep 0? Idea 2.
8. **Specializations.** May I make Clone Lab and Entertainment District work (idea 3)? What effect size do you prefer?
9. **Hoth and Ossus.** Should they allow player cities, how many (3 to 5?), and can I add the guard for the missing `CitiesAllowed` key first?
10. **Founding sites.** May I edit planet terrain files in the test archive to flatten 6 to 10 curated sites (idea 4), starting with Tatooine and Rori?
11. **Props.** Do you want mayors to be able to keep static event-perk props (idea 5) and with what cap?
12. **Setting.** Should bot towns follow the 138-139 ABY setting (names and themes from our own lists) or be neutral?
13. **Provenance.** Are you comfortable with me citing Legends and Restoration's public wiki and news pages as evidence (they are not on SWGEmu's AGPL-compliant list)? I used nothing else from them. Sentinel's Republic was left out as you asked.

## Sources

**Official (SOE, 2004-2011), via the Internet Archive**
- SOE "Player Cities" list as of 3 Feb 2011 (Wayback copy of 9 Feb 2011): https://web.archive.org/web/20110209215313/http://starwarsgalaxies.station.sony.com/en_US/players/content.vm?resource=player_cities&page=Player%20Cities
- Game Update 8 publish notes, 12 Mar 2009 (SWG wiki mirror): https://swg.fandom.com/wiki/Game_Update_8

**Community, live era**
- Guide to Player Cities v1.3, posted 26 Feb 2005 on the official forums (archived 2016): https://web.archive.org/web/20160909103515/http://swgemu.com/archive/scrapbookv51/data/20070127193158/index.html
- Politician and Player City FAQ, 25 Feb 2005 (archived 2016): https://web.archive.org/web/20160909061412/http://swgemu.com/archive/scrapbookv51/data/20070127193144/index.html
- SWG wiki, "Player city" (note "Updated March 2011"): https://swg.fandom.com/wiki/Player_city
- SWG wiki, "HERO (PA)": https://swg.fandom.com/wiki/HERO_(PA); "Guild:ECHO": https://swg.fandom.com/wiki/Guild:ECHO; "Guild:-MB-": https://swg.fandom.com/wiki/Guild:-MB-; "City:Elysium" (Infinity): https://swg.fandom.com/wiki/City:Elysium
- SWGANH wiki, "City Ranks (Game Mechanics)", last modified 26 Aug 2009: http://wiki.swganh.org/index.php/City_Ranks_(Game_Mechanics)

**Press**
- Guinness World Records, "First player-managed cities in an MMORPG": https://www.guinnessworldrecords.com/world-records/88111-first-player-managed-cities-in-an-mmorpg
- Engadget (Massively), "Some Assembly Required: SWG housing extravaganza", 9 Dec 2011: https://www.engadget.com/2011-12-09-some-assembly-required-swg-housing-extravaganza.html
- Engadget, "The Game Archaeologist and the Star of the Galaxies: The players (part 2)", 15 Jun 2010: https://www.engadget.com/2010-06-15-the-game-archaeologist-and-the-star-of-the-galaxies-the-players.html
- PC Gamer, "Inside the final hours of Star Wars: Galaxies", 16 Dec 2011: https://www.pcgamer.com/the-end-of-star-wars-galaxies/
- MassivelyOP, Legends city update, 1 Apr 2019: https://massivelyop.com/2019/04/01/star-wars-galaxies-legends-emulator-put-out-a-huge-march-update-trying-to-fix-player-cities/
- MassivelyOP, Bespin date, 16 Apr 2021: https://massivelyop.com/2021/04/16/star-wars-galaxies-legends-bespin-city-in-the-clouds/
- MassivelyOP, "Cloud City apartments and player cities on Star Wars Galaxies Legends", 11 Mar 2024: https://massivelyop.com/2024/03/11/working-as-intended-cloud-city-apartments-and-player-cities-on-star-wars-galaxies-legends/
- mmofolklorist, Rogue server roundups: Nov-Dec 2022 https://mmofolklorist.com/2022/12/11/star-wars-galaxies-rogue-server-roundup-november-december-2022/ ; Mar 2023 https://mmofolklorist.com/2023/04/star-wars-galaxies-rogue-server-roundup-march-2023/ ; Apr 2023 (4 May) https://mmofolklorist.com/2023/05/04/star-wars-galaxies-rogue-server-roundup-april-2023 ; May 2023 (8 Jun) https://mmofolklorist.com/2023/06/08/star-wars-galaxies-rogue-server-roundup-may-2023/ ; Jun 2023 (5 Jul) https://mmofolklorist.com/2023/07/05/star-wars-galaxies-rogue-server-roundup-june-2023/
- Seen only as search snippets or titles (not opened): Unwinnable retrospective (https://unwinnable.com/?p=35045); MassivelyOP Felucia headline (https://massivelyop.com/?p=239683); a 2004 retrospective on when cities arrived (https://archive.rpgamer.com/news/Q2-2004/062804c.html); Shacknews (https://www.shacknews.com/article/62108/star-wars-galaxies-forces-under) and a forum repost for the Forces Under Siege / Game Update 15 city alignment; the Storyteller launch coverage of 22 May 2007 (Shacknews, Engadget); Legends' spring 2024 newsletter; the SWG wiki "Servers" page (https://swg.fandom.com/wiki/Servers) for the Oct 2009 closures; a MassivelyOP piece on Empire in Flames (https://massivelyop.com/?p=340022) for "strict player cities" and the anti-sprawl housing.

**Private servers (public pages)**
- Restoration wiki, "Player Cities" (updated 25 Sep 2026): https://swgr.org/wiki/player_cities ; "Storyteller": https://swgr.org/wiki/storyteller
- Restoration Update 1.2.1, 1 Mar 2024: https://swgr.org/post/update-1-2-1.2660/ ; Update 1.2.3, 10 Jun 2024: https://swgr.org/post/update-1-2-3-skyward-bound.3231/ ; Developer Diary "Player City Refresh", 24-25 Aug 2026: https://swgr.org/post/player-city-refresh.7513/
- Restoration spotlights: Black Sun Ravine 26 Jan 2024 https://swgr.org/post/player-city-spotlight-black-sun-ravine.4961 ; Black Sands 26 May 2024 https://swgr.org/post/player-city-spotlight-black-sands.4960/ ; Mos Pelgo 26 May 2024 https://swgr.org/post/player-city-spotlight-mos-pelgo.4963/ ; Pelgo Slums 10 Dec 2024 https://swgr.org/post/player-city-spotlight-pelgo-slums.4964 ; Bantha Cairns 20 Sep 2025 https://swgr.org/post/player-city-spotlight-bantha-cairns.5245
- SWG Legends wiki, "Player city": https://swglegends.com/wiki/index.php?title=Player_city
- Stardust wiki, "Player Cities": https://stardust-swg.fandom.com/wiki/Player_Cities
- SWGEmu wiki, "Servers": https://swgemulator.fandom.com/wiki/Servers
- Steam discussion, Basilisk guild recruiting post, 25 Jul 2019: https://steamcommunity.com/app/24170/discussions/0/3428846977635816013

**Our files**
- `Systems-baseline/id-politician-gaps.md` (15 Oct), `Claude-class-check/professions.json`, `Bot-reports/launch-sim/FINDINGS.md`, `economy-review.md`, `numbers-run7-early.md`, `ossus-census.md`, `tools/bots/ossus_census.py`, `Documentation-support/server-side-bots.md`, `precu-player-builds.md`.
- Core3-dev `8b48a044`: `bin/scripts/managers/city_manager.lua`; `src/server/zone/managers/city/CityManagerImplementation.cpp`; `objects/region/CityRegionImplementation.cpp`; `managers/structure/StructureManager.cpp`; `objects/player/sessions/PlaceStructureSessionImplementation.cpp`; `objects/tangible/deed/components/PlaceCityHallComponent.cpp`; `objects/player/sui/callbacks/PlaceCityHallSuiCallback.h`; `managers/city/CityDecorationTask.h`; `objects/structure/events/StructureMaintenanceTask.cpp`; `managers/planet/PlanetManagerImplementation.cpp`; `managers/botpop/*`; civic templates under `bin/scripts/object/building/player/city/`.
