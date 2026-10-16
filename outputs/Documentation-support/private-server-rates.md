# How private SWG servers set rates, XP and economy (research, 15 Oct 2026)

Owner's question (15 Oct): "check how most private servers configure their rates, exp, etc".
Scope: public web pages only (no logins, no downloads, no contact). Names of real people are left out; server names are used.
Every number below has a source number in [brackets] (list at the end). Each source is tagged:

- **official** = the server's own site, wiki or staff announcement
- **community** = a fan or player wiki
- **press** = a news site
- **claim** = a player's statement or a search-engine snippet that I could not open

"Retrieved" is 15 Oct 2026 for every page. Where a page shows its own date, that date is given; many wiki pages show none.

## 1. Summary

**Honest limit first.** Most servers do not publish multipliers on pages a stranger can read. Of the ten or so servers I tried, I found real numbers for only four (Awakening, Revelation, Restoration, Sentinels Republic). SWGEmu's own forum (Finalizer) sits behind a Cloudflare challenge, which I did not try to get past, and Reddit and Discord are not readable here. So "most servers use X" cannot be proved; this is what the evidence supports.

**Typical ranges seen**

| Setting | What the evidence shows | Strength |
|---|---|---|
| Combat XP | Stock SWGEmu code is 1.0x. Awakening (pre-CU): base 1x, running 2x since at least 2023, 2.5x in May 2026, 3x as a donation reward. Revelation (pre-CU based): 1.5x. Restoration (CU/NGE): 2x on its wiki, "5x" in newer posts. Sentinels Republic: "many XP types five-fold" (2019). | Medium. Two official, one community wiki, one press. |
| Crafting, entertainer, medical, scout, survey XP | Revelation boosts these most: crafting 5x, entertainer 5x, medical 3x, scout 3x, survey 10x. Restoration crafting 2x. | Low (one server gives the full table). |
| Jedi XP | Restoration 1x (its wiki lists Jedi as unboosted). Ours: 2x. | Low. |
| Group XP | Stock Core3 1.2x; Revelation 1.25x; Finalizer adds "group XP for similarly skilled players" (no figure); Empire in Flames: grouping with a droid doubles XP. | Medium. |
| Mission pay | Restoration multiplies by type: 5x (music, dance, crafting, survey), 4x (factional destroy), 3x (escort), 2.5x (NPC destroy), 2x (recon, delivery), 1.5x (creature destroy, NPC bounty). Revelation "raises" entertainer and scout missions (no figure). | One official source. |
| Active missions at once | Stock is 2. Empire in Flames: 6 (May 2021). Ours: 6. | Medium. |
| Skill points | 250 on Infinity, Restoration and stock; Awakening publishes none. Revelation keeps 250 but cuts costs (novice boxes 15 to 10 SP, entertainer tree free). | High. |
| Training credit cost | Revelation: base-profession training costs 50% fewer credits. No other server publishes a figure. | Low. |
| Jedi unlock | Infinity: village in four phases of 3 days each, after five mastered professions plus badges. Restoration: 145 Jedi unlocked about three months after the first (29 Feb 2024). Awakening, Revelation, Genesis: custom unlocks (no numbers). | Medium. |
| Harvest, craft, resources | Restoration harvesters +50% vs Live. Revelation: bigger hoppers, better BER, resource container up to 1,000,000, +25% creature harvesting, +50% milk, more random resource spawns. No server publishes crafting-time or factory-time changes. | Medium. |
| Starting credits | **Nothing found** for any other server. Stock Core3 is 100 cash and 1,000 bank. | Gap. |
| Junk dealer, loot credits | **Nothing published.** Revelation raises loot chances on selected mobs. Legends says it cut "easy credit gains from AFK grinding" (2023, no figure). | Gap. |

**Read of the field.** The big, long-running servers that stay close to pre-CU (Awakening, SWGEmu) keep the base at 1x and add a modest boost (2x to 3x) or event weekends. Smaller custom servers (Revelation, Sentinels Republic) boost much harder, and boost the slow XP types (crafting, entertainer, survey) hardest. Credits are protected on the big servers (credit sinks on Restoration, anti-AFK work on Legends); mission pay is where the boosts show up.

**What fits a small friends' server.** (Suggestions for the owner to decide; nothing here is changed.)

- Combat XP: 2x to 5x is in range. Our 5x is at the top of what is published.
- Support and crafting XP: with few players, everyone has to supply the group (a doctor, an entertainer, a crafter, a surveyor). Revelation's pattern (boost those XP types 3x to 10x, combat only 1.5x) is the one that fits. Core3 has only one global multiplier today, so this needs a small code change like the one we already made for Jedi XP.
- Group XP: 1.2x is stock; 1.25x to 2x is within what others do and helps a handful of friends who play together.
- Mission pay: Restoration's per-type table is the best model. Raise the social and crafting missions most.
- Skill points and training cost: 250 SP is the norm everywhere. Our 1000 SP and 0.25x training cost fit a test sandbox, not a launch; Revelation's cuts (15 to 10 SP per novice box, -50% credits) are the published middle ground.
- Jedi unlock: 3 to 7 days per village phase is within range (Infinity 3, ours 7, stock 21).
- Starting credits: no comparison exists; ours (10,000 cash, 100,000 bank) is a judgement call.

## 2. Our current settings (read only, 15 Oct 2026)

Files read, inside WSL as `swgemu`: `/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/conf/config-local.lua`, `/opt/swg/Core3-dev/MMOCoreORB/bin/conf/config.lua`. No secrets were printed. The rate knobs mostly live in the Lua scripts, not the conf files, so I also read the scripts and our own git history for the stock values (commit 4357970d "Sandbox profile", 13 Oct, and 41764180, 15 Oct).

| Setting | Ours | Stock Core3 | Where it is set |
|---|---|---|---|
| Global XP multiplier | 5.0 (all XP types except Jedi) | 1.0 | `scripts/managers/player_manager.lua` (dev tree, test galaxy and the live `/opt/swg/Core3` scripts all read 5.0) |
| Jedi XP multiplier | 2.0 (replaces the global value for `jedi_general`) | no separate setting | `Core3.Sandbox.JediXpMultiplier` in config-local.lua |
| Group XP multiplier | 1.2 | 1.2 | `player_manager.lua` |
| Per-profession XP exceptions | none, except Jedi | none | code change needed |
| Skill points | 1000 | 250 | `Core3.Sandbox.SkillPoints` and `player_creation_manager.lua` |
| Training credit cost | x0.25 | x1 | `Core3.Sandbox.TrainingCostMultiplier` |
| Crafting time | 1 second per craft | stock timers | `Core3.Sandbox.CraftSeconds` |
| Factory time | x0.25 | x1 | `Core3.Sandbox.FactoryTimeMultiplier` |
| Structure maintenance | x0.5 | x1 | `Core3.Sandbox.StructureMaintenanceMultiplier` (and `maintenanceDiscount` 0.5 in `city_manager.lua`) |
| House items | 1000 per lot, 10,000 max | 100 per lot | `Core3.Sandbox.HouseItemsPerLot`, `HouseMaxItems` |
| Starting cash, bank | 10,000, 100,000 | 100, 1,000 | `player_creation_manager.lua` |
| Max active missions | 6 (code default; not set in conf) | 2 | `Core3.MissionManager.MaxActiveMissions`, commit 41764180 (owner, 15 Oct) |
| Mission pay | stock: destroy missions pay 375 x difficulty + up to 15 x difficulty random | same | `scripts/managers/mission/mission_manager.lua` |
| Credit drops | stock formula: max = 0.03 x level^2 + 3 x level + 50; min = half of max + 2 x level | same | `LootManager::calculateLootCredits` |
| Loot quality chances, junk value | stock (junk value modifier 5; exceptional 1 in 100,000; legendary 1 in 1,000,000) | same | `loot_manager.lua` |
| Characters per account | 15 per galaxy (test galaxy), 4 online at once | 10 per galaxy, 2 online | config-local.lua; `player_manager.lua` |
| Jedi village phase length | 7 days | 21 days | `village_jedi_manager_township.lua` (the file's own comment still says "3 weeks") |
| Resource container size, resource deed | 999,999 max, 100,000 deed | 100,000, 30,000 | `ResourceContainer.idl`, `ResourceManager.idl` |
| Travel | shuttle and starport waits 10 s, landing 2 s, landed 600 s | 300/60 s away, 11-14 s landing, 120 s landed | `planet_manager.lua` |
| Run, walk speed (three vehicles) | 30, 10 m/s | stock | vehicle object scripts |
| Cities | citizens per rank {1,2,3,4,5} | {2,4,6,8,10} | `city_manager.lua` |
| Other test-galaxy only | `TameAnything`, `MedicalAnywhere`, `CharacterBuilderEnabled`, JTL on, bot population up to 1,500 | off | config-local.lua |

`config.lua` in the dev tree is the stock file (ports, zones, TRE list); it has no rate settings. Resource spawn timing in `resource_manager.lua` (average shift 7,200,000 ms, spawn throttling 90) was not touched by the Sandbox commit; later commits only add planets and materials to the spawn pools.

## 3. Server by server

Era notes: "pre-CU" = before April 2005 combat upgrade; "CU" = after it; "NGE" = after Nov 2005. Era labels come from the servers' own pages or the press pieces cited.

### SWGEmu: Finalizer (pre-CU, Publish 14.1 base)

- Era: pre-CU. A developer post of Oct 2023 calls it "mostly vanilla Pre-CU at Publish 14.1" plus test additions, including group XP for similarly skilled players, cross-account lots, a guild device, world bosses and a GCW zone [claim: search snippet of the post, mirror not openable] [S1].
- Population: "consistently just above 1000" concurrent in Jan 2022 [press, S2]; 2,352 active accounts in April 2023 [claim: snippet of an admin finance post, not opened] [S1].
- XP, missions, cash: **no figure published on any page I could read.** The official forum returned a Cloudflare challenge, which I did not bypass [S3]. Stock Core3 on public GitHub gives the baseline a stock server starts from: global XP 1.0, group XP 1.2, starting cash 100, bank 1,000, 250 skill points, destroy mission pay 375 x difficulty [S4, S5, S6]. Finalizer's live overrides are unknown.

### SWG Awakening (pre-CU, SWGEmu-based, own Jedi unlock)

- Official, dated staff posts show the XP history [S7 to S10]:
  - 10 Feb 2022: after a rollback the server XP was raised "to 3x the base rate" until the next restart.
  - Oct 2023 and 30 Oct 2024 (anniversaries): "doubled (from the base rate of 1x or 100%)" during the event.
  - 4 May 2023: May 4th event XP "three times the base rate", while "currently in two times boosted XP mode".
  - 8 Oct 2025: "the server's XP rate will jump to 3x XP for everyone (currently 2x)" if the monthly donation goal is met. Hitting the goal gives a server-wide XP boost.
  - 4 May 2026: event XP 3.5x the base rate, "currently 2.5x" because the donation goal was reached.
- So: **base 1x; normal running rate 2x to 2.5x, funded by donations.**
- Accounts: 10 character slots, 2 online at once (FAQ, undated) [S11]. Free, no pay-to-win [S11].
- Jedi: a custom hidden unlock that "no other server" uses [S12]. No numbers.

### SWG Infinity (pre-CU 14.1, SWGEmu-based)

- Self-reported population 800+ weekly active players; Legends 1,000+; Restoration III 400+ (Infinity's own comparison page, 2026, marketing) [S13].
- 250 skill points; mastering one elite profession "around 150 points"; 7 characters per account, 3 online [S14, S15].
- Jedi unlock: master 5 professions (not entertainer, dancer, image designer, musician, politician), 5 easy + 2 hard + 3 Jedi location badges, 3 theme-park badges; the village is "four phases, each three days long"; the Old Man visit takes 10 minutes to 12 hours. "Glowy" status in about a week or a day if rushed [S16].
- XP rate: **not published.** A player says it "generally has boosted XP" (2024, snippet only) [claim, S17].

### SWG Restoration III (CU, Publish 15 combat; NGE content)

- Official wiki, "Last updated: Monday" (no calendar date): Combat XP x2, Crafting XP x2, Jedi XP x1, Quest XP x5. Level-difference bonus +10% per level above, -10% per level below. Grey-con NPCs give 1 XP [S18].
- Official post 26 Jan 2024: "experience gain is already tuned up 500% versus the Live version"; rested points give +50% XP, built by watching an entertainer [S19].
- Official guide 29 May 2025: "experience gain has been boosted 5x"; rested XP +25%; harvester rates +50% over Live; 250 skill points over 32 professions; damage reduced about 20% in 1.1; 2 character slots, a third by quest, a fourth from the Jedi unlock [S20]. The three pages do not agree with each other (2x vs 5x; rested 50% vs 25%), so treat the exact figures as moving.
- Mission pay multipliers (26 Jan 2024): music, dancing, crafting, surveying 5x; factional destroy 4x; escort 3x; NPC destroy 2.5x; creature destroy 1.5x; recon and delivery 2x; NPC bounties 1.5x [S19].
- Credits: Legacy quest rewards 2,500 to 70,000 credits, "over 3 million" for the full chain; the credit ceiling was lowered through chassis dealer changes and the floor is being raised [S19]. The FAQ in the search results says credit sinks were added to limit inflation (snippet) [claim].
- Jedi: first Jedi unlocked 29 Feb 2024; by 26 May 2024, 145 unlocked and 161 more through Phase 1; about 9.6% of weekly active players; a Force ghost loses 500,000 Jedi XP (1,000,000 if killed by a bounty hunter) [S21].
- Population: more than 5,000 accounts in month one and more than 11,000 by end of 2021 (post 29 Jan 2022) [S22].

### SWG Revelation (pre-CU professions, custom; community wiki, undated)

- PvE XP bonuses: grouped 125%; combat 150%; crafting 500%; medical 300%; entertainer 500%; scout 300%; survey 1000%; DNA harvesting 300%; political 200%; image design 300%; merchant 200%; slicing 200%; bounty hunter 250%; creature handler 200%. PvP XP bonus (special forces) 150% [S23].
- Storage: creature pets 4, faction pets 3, droids 6, vehicles 6, lots 10, ships 3. Skill points: novice boxes cost 10 SP instead of 15; the entertainer tree costs 0; dancer and musician are basic professions [S23].
- Training: 50% reduced credit cost for base-profession skill training; some professions' tier 3 and 4 XP requirement cut 50% [S24].
- Other: raised payouts of entertainer and scout missions; battle fatigue max 1500; vendor listing time 60 days; bazaar listing credit fee 20k to 30k; shuttle waits at starports cut to 2 minutes; freelance shuttles; free buffs from NPCs for new players; house storage 250 items per lot [S25].
- Resources and harvesting: all resources auto-uploaded to Galaxy Harvester; milk density +50%; creature harvesting density +25%; random resource spawn count raised; harvester BER and hopper size raised; resource container up to 1 million; harvest range 7 to 12 m; base sampling rate reduced [S25].
- Loot: higher chance of stat-bearing loot, locked containers, selected planets; Krayt dragons 100% loot chance [S25].

### SWG Legends (NGE-based, custom content)

- The largest NGE-era server by its own and rivals' account: 548 online and 1,372 unique accounts in 24 hours on its home page at retrieval; Infinity's comparison says 1,000+ [S26, S13].
- XP: **no standing multiplier published** on the pages I could read. Double-XP weekends run on anniversaries (3 to 6 Mar 2023 [press, S27]; one in Feb 2021 [claim: search snippet of a press piece, not opened]).
- Aug 2026 development update: an Ace Pilot box now shows 100,000 XP needed instead of 7,500,000; an Entertainer XP exploit "gathered at considerably higher than normal rates" was fixed [S28].
- Economy: a 2023 "Health of the Economy" update cut "easy credit gains from AFK grinding" (no figure) [press, S29].

### Empire in Flames (pre-CU base, heavily reworked; post-Endor setting)

- Professions cost no skill points and only one can be active; skills use skill points and mix freely. Crafting moved to a core-based weapon system [S30].
- New player guide, 14 May 2021: terminals let you take **six missions at a time**; "when in a group you receive double the experience", so cheap "grouper" droids are used; crafting "Practice Mode" gives an XP bump; buffs are not needed for normal grinding because of HAM rebalancing; NPC training "can get expensive" [S31].
- Multipliers: **not published.**

### Sentinels Republic (pre-CU based) — rate only

- Press, 20 Mar 2019: "Many of the experience points are increased five-fold", and event phases such as Aurilia run faster. Community about 2,500 [press, S32]. Seven years old and not checked against the server. The project excludes Sentinel's Republic content (AGENTS.md); this entry is the rate number only.

### Others

- SWG Genesis (pre-CU, Nov 2024): developer update lists pre-revamp Jedi skills with a custom unlock; no XP figures found [claim: snippet, S33].
- SWGEmu Basilisk, Attack of the Clones, Aurora, Bloodfin, Reckoning, Tarkin's Revenge, Project Carbonite: no rates found. "Project Carbonite" returned no result at all.
- Revelation's wiki is the only place that publishes a full per-profession table.

## 4. Comparison table

`n/p` = not published on a page I could read.

| Server | Era | Combat XP | Crafting / support XP | Jedi XP | Group XP | Mission pay | Skill points | Training cost | Starting credits | Harvest / craft | Source tag |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Stock Core3 (baseline) | pre-CU | 1.0x | 1.0x | 1.0x | 1.2x | 375 x difficulty (destroy) | 250 | 1x | 100 cash, 1,000 bank | stock | GitHub [S4 to S6] |
| Finalizer | pre-CU | n/p | n/p | n/p | "similarly skilled" bonus, no figure | n/p | n/p | n/p | n/p | n/p | claim [S1] |
| Awakening | pre-CU | 1x base, 2x to 2.5x running, 3x+ events | same multiplier for all types | n/p | n/p | n/p | n/p | n/p | n/p | n/p | official [S7 to S10] |
| Infinity | pre-CU | n/p ("boosted") | n/p | n/p | n/p | n/p | 250 | n/p | n/p | n/p | official / claim [S14, S17] |
| Revelation | pre-CU based | 1.5x | craft 5x, ent 5x, med 3x, scout 3x, survey 10x | n/p | 1.25x | entertainer and scout raised | 250; novice 10 SP | -50% base training | n/p | hopper, BER, container 1M, +25% harvest | community wiki [S23 to S25] |
| Restoration III | CU / NGE | 2x (wiki) or 5x (posts) | crafting 2x | 1x | n/p | 1.5x to 5x by type | 250 | "very large" direct-train fee | n/p | harvesters +50% | official [S18 to S20] |
| Legends | NGE | n/p; double-XP events | n/p | n/p | n/p | n/p | n/a (expertise) | n/p | n/p | n/p | official wiki / press [S26 to S29] |
| Empire in Flames | pre-CU rework | n/p | n/p | n/p | double XP when grouped with a droid | n/p; 6 active missions | professions free, skills use SP | "can get expensive" | n/p | n/p | official guide [S30, S31] |
| Sentinels Republic | pre-CU based | "five-fold" (2019) | n/p | n/p | n/p | n/p | n/p | n/p | n/p | n/p | press [S32] |
| **Ours (sandbox)** | pre-CU | 5x | 5x | 2x | 1.2x | stock; 6 active | 1000 | x0.25 | 10,000 cash, 100,000 bank | craft 1 s, factory x0.25, container 999,999 | local files |

## 5. What I could not reach

- SWGEmu forums (Finalizer rules and Q&A): Cloudflare challenge page; left alone.
- Reddit threads: blocked in the browser pane; the search-engine mirrors failed with certificate or connection errors. Anything taken from a snippet is marked claim.
- Discord announcement pages: not tried (not web pages I could read without an account).
- No server was found that publishes starting credits, junk dealer changes, crafting-time or factory-time changes, or resource spawn rate numbers beyond Revelation's list.
- The "most pre-CU servers use 2x to 5x" line in the brief is **not supported** as a statement about "most": the published pre-CU figures run 1x to 2.5x base on the large servers, 1.5x to 10x by type on Revelation, and 5x on one 2019 press note.

## 6. Sources

Search-engine tool used for discovery; page text read by fetch tool or the browser pane. All retrieved 15 Oct 2026.

- S1: SWGEmu Finalizer developer and finance posts, quoted only through a search-engine snippet (not opened): https://www.swgemu.com/forums/faq.php?faq=basics (FAQ, Cloudflare-blocked on fetch) and mirrors of r/swgemu posts, Oct 2023 and Jun 2023. [claim]
- S2: Finalizer launch and population, press roundup of Dec 2021 (page dated 2 Jan 2022): https://mmofolklorist.com/2022/01/02/star-wars-galaxies-rogue-server-roundup-december-2021/
- S3: SWGEmu forum thread URLs returned a Cloudflare "Just a moment" challenge: https://www.swgemu.com/forums/ (not bypassed).
- S4: Stock Core3 `player_manager.lua` (global XP 1.0, group 1.2, characters online 2), branch unstable: https://github.com/swgemu/Core3/blob/unstable/MMOCoreORB/bin/scripts/managers/player_manager.lua
- S5: Stock Core3 `player_creation_manager.lua` (cash 100, bank 1000, skill points 250): https://github.com/swgemu/Core3/blob/unstable/MMOCoreORB/bin/scripts/managers/player_creation_manager.lua
- S6: Stock Core3 `mission_manager.lua` (destroy reward 375 x difficulty): https://github.com/swgemu/Core3/blob/unstable/MMOCoreORB/bin/scripts/managers/mission/mission_manager.lua
  (S4 to S6 values were read through a summarising fetch tool; our own git history in /opt/swg/Core3-dev, commit 4357970d, shows the same stock values as the lines it replaced, so they are cross-checked.)
- S7: Awakening, "She's Alive!", 10 Feb 2022: https://swgawakening.com/search.php?keywords=multiplier&terms=all&sf=all&sr=posts (forum search, topic "She's Alive!")
- S8: Awakening anniversary and Star Wars Day posts, 4 May 2023, 22 Oct 2023, 30 Oct 2024 (forum search "experience gain"): https://swgawakening.com/search.php?keywords=experience+gain+OR+experience+rate+OR+double+experience&terms=any&sf=all&sr=posts
- S9: Awakening, "Awakening Needs You", 8 Oct 2025: https://swgawakening.com/viewtopic.php?t=11313
- S10: Awakening, "May 4th Star Wars Day 2026", 4 May 2026: https://swgawakening.com/viewtopic.php?t=11341
- S11: Awakening FAQ (undated): https://swgawakening.com/faq
- S12: Awakening home page (Jedi unlock statement; patch 10.0.9 dated 5 Oct 2026): https://swgawakening.com
- S13: Infinity server comparison page (self-reported, 2026): https://www.swginfinity.com/swg-server-comparison
- S14: Infinity FAQ (undated): https://www.swginfinity.com/faq
- S15: Infinity new player guide (undated): https://www.swginfinity.com/new-player-guide
- S16: Infinity Jedi unlock guide (undated): https://www.swginfinity.com/guides/jedi-unlock
- S17: Player comment on Infinity XP (search snippet of an r/swgemu thread, 13 Aug 2024; page not opened) [claim].
- S18: Restoration wiki, New Player Guide ("Last updated: Monday"): https://swgr.org/wiki/new_player_guide/
- S19: Restoration, "New Player Experience" Comlink post, 26 Jan 2024: https://swgr.org/post/swg-restoration-new-player-experience.4986
- S20: Restoration, "New and Returning Player Guide", 29 May 2025: https://swgr.org/post/swgr-new-and-returning-player-guide.4988/
- S21: Restoration, "The Force is Imbalanced: Managing Jedi Population", 26 May 2024: https://swgr.org/post/the-force-is-imbalanced-managing-jedi-population.4975/
- S22: Restoration, "Our 2021 Retrospective and 2022 Plans", 29 Jan 2022: https://swgr.org/post/our-2021-retrospective-and-2022-plans.404
- S23: Revelation wiki, Server Information (community wiki, undated): https://swg-revelation.fandom.com/wiki/Server_Information
- S24: Revelation wiki, Profession Balances (undated): https://swg-revelation.fandom.com/wiki/Profession_Balances
- S25: Revelation wiki, Revelation Features (undated): https://swg-revelation.fandom.com/wiki/Revelation_Features
- S26: Legends home page (live counters at retrieval): https://swglegends.com
- S27: Legends anniversary double-XP weekend, press, 27 Feb 2023: https://massivelyop.com/2023/02/27/star-wars-galaxies-rogue-server-swg-legends-celebrates-seventh-anniversary-with-todays-patch/
- S28: Legends wiki, Development Update 2026-08 (last edited 8 Aug 2026): https://swglegends.com/wiki/index.php?title=Development_Update,_2026-08:_Battle_of_Restuss_2026
- S29: Legends economy update, press roundup of May 2023 (page dated 8 Jun 2023): https://mmofolklorist.com/2023/06/08/star-wars-galaxies-rogue-server-roundup-may-2023/
- S30: Empire in Flames, "Welcome to Empire In Flames": https://www.empireinflames.net/?p=714
- S31: Empire in Flames, New Player Guide and FAQ, 14 May 2021: https://www.empireinflames.net/?p=1467
- S32: Sentinels Republic and others, press, 20 Mar 2019: https://massivelyop.com/2019/03/20/hyperspace-beacon-which-star-wars-galaxies-emulator-should-i-try-first/
- S33: SWG Genesis developer update, 23 Nov 2024 (search snippet of an r/swg post; not opened) [claim].
- Era and server list for the field: https://mmofolklorist.com/2023/01/07/the-best-star-wars-galaxies-server-for-every-player/ (7 Jan 2023)
