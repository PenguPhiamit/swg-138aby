# Pre-CU professions and gameplay: reference for Claude

Prepared 13 October 2026 by ChatGPT after C7 run `20261013-201324`. This is a profession coverage map and test-design reference, not a claim that every profession has passed here. Read with [knowledge sources](../Agent/knowledge-sources.md), [C7 report](../Agent/reports/2026-10-13-C7-one-round.md) and [feature register](../SWG-feature-register.md).

## Which game are we documenting?

Our server is SWGEmu **pre-CU**, with local sandbox additions. Historical pre-CU, beta, CU, NGE and custom-server advice must be kept separate. An archive dated 2007 can preserve a 2004 post; an archived 2005 patch page can include CU changes. A profession proposal is not implemented behavior. Guides from 2003 can predate substantial pre-CU revisions.

Use this authority order: observed event plus current local implementation; the client skill/schematic tables actually loaded; pinned upstream source; dated official notes/manual; dated player tests; modern community walkthroughs. A passing command acknowledgement is not proof of a buff, resource receipt or completed mission.

`SkillManager.cpp` loads `datatables/skill/skills.iff`, builds prerequisite relationships and command abilities, and uses `Core3.Sandbox.SkillPoints` with default 250. We did not extract that IFF this session. Therefore **exact box prerequisites, XP thresholds, training fees, certification lists and schematic costs below are deliberately not invented**. Source them from the loaded tables and current trainer before encoding assertions. `scripts/managers/skill_manager.lua` enables apprenticeship; it is not the profession table.

Primary implementation: [SkillManager](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/managers/skill/SkillManager.cpp). Local inspected revision: dev `5aadc8b9`; public links use the project's upstream pin `403893d9`, so compare local changes. Skills are mixed within the point budget; a profession title does not automatically grant every useful box. Gear certification is separate from possessing the item. Character combat level is not a substitute for inspecting skills, HAM, weapon/armor and target difficulty.

## Complete profession coverage map

Each row gives the profession's role and the smallest useful functional check. Family names are orientation, **not exact novice prerequisites**. Specialized mechanics remain untested unless the C7 section says otherwise. The overall historical profession roster is also recorded by the project in its [official status list](https://archive.swgemu.com/forums/showthread.php?mode=threaded&p=741953); its old completion percentages must not be used as current status.

### Six starting professions

| Profession | Purpose / main loop | Minimal meaningful test |
|---|---|---|
| Artisan | Survey/sample resources and craft basic goods | Find concentration, sample, verify resource quantity, craft a prototype, relog |
| Brawler | Melee combat with unarmed/one-hand/two-hand/polearm branches | Certified weapon or unarmed attack; verify damage, relevant XP and recovery |
| Marksman | Pistol/rifle/carbine combat and ranged support | Correct weapon, range/LOS, attack, appropriate XP |
| Medic | Heal damage/wounds and craft medicine | Injured willing target, valid medicine, actual HAM/wound improvement and charge use |
| Scout | Wilderness navigation, traps, harvesting and camps | Fresh eligible animal corpse, harvest resource receipt; valid camp placement |
| Entertainer | Dance/music, audience healing and basic appearance services | Audience watches/listens, verify a healing effect rather than animation alone |

Historical orientation: [official starting-profession manual preserved at Reckoning](https://swgreckoning.org/archive/data/20070128130746/manual_printview_005.html). The launch-era manual includes obsolete details such as usage-based crafting XP; current source/data and observation override those specifics.

### Combat specializations and hybrids

| Profession | Family / purpose | Minimal meaningful test |
|---|---|---|
| Rifleman | Marksman; specialized rifles | Certified rifle plus learned special; damage/state and weapon-specific XP |
| Carbineer | Marksman; specialized carbines | Carbine special with range/LOS checks; effect on target |
| Pistoleer | Marksman; specialized pistols | Pistol special and relevant certification; damage/resource cost |
| Teras Kasi Artist | Brawler; unarmed fighting and meditation | Unarmed special; separately test meditation recovery with known damage/state |
| Fencer | Brawler; one-handed melee | One-hand special against weak target; verify weapon class and effect |
| Swordsman | Brawler; two-handed melee | Certified two-hand weapon and special; do not assume Master Brawler certifies every sword |
| Pikeman | Brawler; polearms | Polearm special and target state/damage |
| Bounty Hunter | Hybrid combat/tracking; bounty missions and investigative equipment | Actual bounty terminal contract, tracking workflow, authorized NPC target and payout |
| Commando | Hybrid combat; heavy weapons and explosives | Correct certified heavy weapon/ammunition; bounded damage test, including area safety |
| Smuggler | Hybrid combat/underworld utility, slicing and spice | Valid sliceable owned item and tools; compare actual stat change; spice effect then downside separately |
| Squad Leader | Hybrid combat/scouting; group support | Form real group, apply learned support ability, measure recipient effect and duration |
| Combat Medic | Hybrid medical/ranged combat; ranged healing and medical DoTs | Valid ranged medicine/target/range; heal or poison/disease state evidence, cure and consumption |

Combat reference: [CombatManager](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/managers/combat/CombatManager.cpp). Inspect the specific command and weapon template before asserting range, HAM costs, armor piercing, resistances or cooldowns. A `fight` result saying target disappeared is weaker than a verified corpse.

### Wilderness, medical and social specializations

| Profession | Family / purpose | Minimal meaningful test |
|---|---|---|
| Ranger | Scout; advanced tracking, concealment, harvesting and camps | Track an ordinary target; verify actual harvest yield and permitted camp services |
| Creature Handler | Scout; tame/train/manage pets | Eligible tameable creature and skill cap; tame, name/train, store/call; verify persistence |
| Doctor | Medic; advanced treatment, enhancements, cures and revival | Medical-rated site/droid, appropriate enhancement pack, actual max-stat gain; later cures/revival |
| Bio-Engineer | Medic/Scout hybrid; DNA, biological products and pet creation | Valid DNA sampling, components and schematic; produced pet/item stats, not just a sample message |
| Dancer | Entertainer; advanced dance and Mind enhancement | Eligible audience/site, watch and performance; stop watching and measure recipient Mind effect |
| Musician | Entertainer; instruments/music and Focus/Willpower enhancement | Compatible instrument, listen and performance; stop listening and measure secondary Mind effects |
| Image Designer | Entertainer; appearance and stat migration | Two consenting characters, supported session/UI, before/after appearance or stat allocation |

Dancer and Musician buffs are different from Doctor Health/Action enhancements. Medical healing is also distinct from healing wounds or battle fatigue. An animation, successful `/startdance`, or a generic healing line does not prove a recipient buff.

### Production, economy and civic professions

| Profession | Purpose | Minimal meaningful test |
|---|---|---|
| Architect | Buildings, installations and furnishings | Craft one deed; authorized placement, maintenance/storage, redeed behavior |
| Armorsmith | Armor and its components | Assemble one piece with suitable resources; examine resistances/encumbrance and wearability |
| Weaponsmith | Weapons/components | Craft and examine damage/speed/cost/certification; actual equipped use |
| Chef | Food/drink and temporary effects | Craft consumable, consume, verify effect/fullness/duration |
| Tailor | Clothing and wearables/customization | Craft/customize/equip item; appearance and persistence; attachments separately |
| Droid Engineer | Droids and functional modules | Craft deed, activate/control device, call/store droid, test an installed module |
| Merchant | Vendors, sales and economy services | Create permitted vendor, list owned item, second-character purchase, credits/item transfer |
| Shipwright | JTL chassis/components and component reverse engineering | Craft component, install within ship limits; analyze matching eligible loot components separately |
| Politician | Player-city governance, civic structures and services | Dedicated disposable city/citizen setup; rank/permissions/tax/services/election checks |

Crafting reference: [CraftingManager](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/managers/crafting/CraftingManagerImplementation.cpp). Crafting follows tool → offered schematic → ingredient slots → assembly → optional experimentation/customization → prototype or manufacturing schematic. Use the correct specialized tool/station and actual schematic resource classes. Resource quality weights differ by recipe. Factory output additionally depends on manufacturing schematic, exact input requirements, capacity and maintenance. No single generic crafting XP recipe is valid for every profession.

### Jedi, Force-sensitive skills and pilots

| Track | Purpose | Testing caveat |
|---|---|---|
| Jedi | Force/saber progression and related unlock/trial systems | Determine our configured unlock path first; old holocron guides and later Village rules differ. No blanket progression claims or new balance changes |
| Force-sensitive branches | Supporting progression/skills, not an ordinary starter profession | Separate from Jedi unlock, and inspect the actual Village/conversion implementation |
| Rebel Pilot | JTL faction-linked flight progression | Trainer eligibility, ship certifications, space missions/XP and actual launch/land |
| Imperial Pilot | JTL faction-linked flight progression | Same core loop, faction/ship restrictions differ |
| Privateer Pilot | JTL neutral/branch-specific flight progression | Track-specific trainer/mission chain and certification |

Pilot progression is separate from the usual ground skill-point build. Existing JTL assets/settings do not prove flight or every quest chain works. Shipwright's in-game component reverse engineering is unrelated to UM's binary reverse-engineering workflow. [Preserved official JTL quick start](https://www.swgemu.com/archive/scrapbookv51/data/20070130131956/index.html) was search-index readable; direct replay was not accessible in this pass.

## Immediate corrections for the C7 squads

### Aurek: Doctor, dancer, musician, ranger and fighters

Current training is **partial**, not five master professions: Aurek Master Marksman + Novice Rifleman; Jesh Master Brawler + Novice Swordsman; Tamsin Novice Doctor + `science_doctor_wound_02`; Sela Novice Dancer + Novice Musician; Oren Novice Ranger. The helper supplies prerequisites for the requested boxes, but that still does not mean mastery. `groups.json` is the current configuration, not an example of natural trainer progression.

`HealEnhanceCommand.h` checks a medical rating excluding the city-only bonus. If that rating <=0, the exact observed response is `@healing_response:must_be_near_droid`. A client building without the required structure medical rating can also refuse despite another rating. It also checks valid medicine, treatment cooldown, combat and target validity. **Town staging was never sufficient.** Next attempt needs a mapped hospital, eligible camp or surgical droid. Measure before/after max HAM and medicine charges; an existing equivalent buff may refresh without increasing the max, so duration/list support is needed for refresh assertions.

Source: [HealEnhanceCommand](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/objects/creature/commands/HealEnhanceCommand.h), inspected local lines 81–119. No repeat game attempt made after the single round.

Entertainer source uses performance healing/buff skills and recipient sessions: [EntertainingSessionImplementation](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/objects/player/sessions/EntertainingSessionImplementation.cpp). Current code includes a duration accumulator cap of 120 minutes + 10 seconds and a base strength cap of 125% before certain faction adjustments. These are internal caps, not a guarantee every novice can grant those values. Historical guides disagree on song/instrument/flourish effects; verify the implementation and measure duration. Camp creation must succeed before treating its healing/crafting services as present.

### Besh: artisans, Scout and guard

Varo is a starter Marksman with basic gear and **no extra training row**. Pell's extra box is Scout camp I. Previously supplying armor did not establish guard survivability; this round Varo died during the patrol before any harvest attempt. Shorten the route, identify local weak prey, and verify a certified weapon and actual combat abilities. Do not repeat long desert patrols as a harvest test.

`HarvestCorpseCommand.h` validates player/creature, selects a resource type actually available on the animal, requires harvest eligibility and death, rejects DNA-death state, then calls CreatureManager harvest. `CreatureManagerImplementation.cpp` checks rights and calculates yield with `creature_harvesting`. A corpse is not universally meat+hide+bone, and a harvest command can return success without giving the assumed resource if the scenario skipped essential conditions. Confirm corpse eligibility, resource type and quantity before/after. Existing-stack merging makes new-container-only assertions incomplete.

Sources: [HarvestCorpseCommand](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/objects/creature/commands/HarvestCorpseCommand.h), [CreatureManager](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/managers/creature/CreatureManagerImplementation.cpp). Inspect `canHarvestMe` and live skill mods before changing training; this round never established that Pell lacked the command.

Survey/sample: tool class, selected resource, concentration, range/posture, interruptions, success, quantity and surveying XP are separate checks. [ResourceManager](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/managers/resource/ResourceManagerImplementation.cpp). A no-resource result can be correct for that location or resource, rather than a failure of the entire gathering system.

### Cresh, Dorn and Esk

- Cresh completed ticket purchase and both shuttle legs. Mission testing needs an actual discovered terminal; search indoors and store coordinates/cell. Confirm offered mission → accepted datapad entry → objective completion → credit delta. Mission acceptance alone is not completion.
- Dorn verified spatial chat, leash/menu behavior and broker conversation. Hiring, combat assist, persistence and dismissal are separate from opening broker options. `/tell` still lacks body support. Do not classify it as a server-wide chat bug.
- Esk verified cantina entry/return, town routes and plateau height. Longer/other-city/private-interior routes, transitions during leash, mounts and disconnected terrain remain separate coverage.

## Recoverable documentation library

No attachments or full copyrighted manuals were downloaded. Links are reading references. Access status below reflects this session; search-index visibility is weaker than a full-page revalidation.

| Source | Era / credibility | Use and limitations | Access this pass |
|---|---|---|---|
| [Official starting-profession manual](https://swgreckoning.org/archive/data/20070128130746/manual_printview_005.html) | Launch-era official manual, replay timestamp 20070128130746 | Starter roles; some launch mechanics obsolete | Full page readable |
| [Official skills/manual section](https://swgreckoning.org/archive/data/20070128130746/manual_printview_010.html) | Official historical manual | Skill structure lead | Search text readable; opened page incomplete (11 lines) |
| [Musician buff FAQ 1.5](https://swgreckoning.org/archive/data/20070126144715/index.html) | First-hand Musician Correspondent, historical pre-CU; replay 20070126144715 | Focus/Willpower vs dancer Mind, watch/listen/stop workflow; explicit uncertainty about several mechanics | Full page readable |
| [Hard numbers on buffs](https://swgreckoning.org/archive/data/20070127171115/index.html) | Player experiments, original May 2004; later community-team reply | Flourish/timing hypotheses, not universal current assertions | Full page readable |
| [Timzai Doctor guide](https://swgreckoning.org/archive/data/20071216103635/guides_135.html) | Explicit **beta** patch 45577.15; page edited 2004 | Historical role orientation; unsuitable for exact present formulas | Search-index text |
| [Ranger: Novice to Master](https://swgreckoning.org/archive/data/20071216103635/guides_158.html) | Brisc Rubal, Aug 2003; explicitly changing mechanics | Tracking/camp/harvest history; old fees/coordinates not current truth | Search-index text; direct fetch failed |
| [Guide to Tailoring](https://www.swgemu.com/archive/scrapbookv51/data/20080108200838/tailor_guide.html) | Historical player crafting account; some claims explicitly unverified | Tools/stations, assembly, prototype vs manufacturing schematic | Rich search-index text; direct replay failed |
| [Tailoring FAQ](https://www.swgemu.com/archive/scrapbookv51/data/20070127213347/index.html) | Historical official-forum player FAQ | Recipe/resource/experiment lead | Search-index text |
| [Player Cities 1.3](https://www.swgemu.com/archive/scrapbookv51/data/20070127193158/index.html) | Dated Feb 26 2005 pre-CU player guide | City ranks, services, taxes and trainer exceptions | Search-index text; direct replay failed |
| [JTL getting started](https://www.swgemu.com/archive/scrapbookv51/data/20070130131956/index.html) | Preserved official feature | Pilot trainers, certifications and shipwright orientation | Search-index text; alternate replay failed |
| [New player discussion](https://www.swgemu.com/archive/scrapbookv51/data/20070210174828/message.html) | Oct/Nov 2004 replies with later signatures mixed in | Travel, ships and beginner workflow | Previously indexed; not revalidated whole page |
| [Official 2004 publish archive](https://swgreckoning.org/archive/data/20070126114830/content_002.html) | Dated official patch notes | Check when a historical feature was introduced | Search-index text |
| [Official 2005 publish archive](https://swgreckoning.org/archive/data/20070126114830/content_001.html) | Mixed pre-CU/CU periods | Version boundaries; do not import later combat/respec rules | Search-index text |
| [SWGEmu 2009 medical update](https://archive.swgemu.com/forums/archive/index.php/t-19685.html) | Primary emulator development history | Historical implementation evidence, not present test results | Search-index text |
| [SWGEmu profession/status roster](https://archive.swgemu.com/forums/showthread.php?mode=threaded&p=741953) | Primary old project checklist | Coverage checklist only, not present completeness | Search-index text |
| [Infinity Warren walkthrough](https://www.swginfinity.com/guides/the-warren) | Server-published modern pre-CU guide | Dungeon orientation; custom details differ | Previously checked in knowledge-sources, not reopened this pass |

Do not use the old holocron grinding guides, Ranger revamp proposals or anonymous forum numbers as executable specifications. Do not follow advice to deliberately harm other characters just to grind healing XP. Use consenting disposable test characters and safe objectives.

## Next documentation/tests for Claude

1. Extract the **loaded** skill IFF into a local structured inventory: profession, box, prerequisite, XP, points, fees, commands, skill mods and certifications; compare server grants with ordinary trainer learning. Owned client data stays private.
2. Add medical-site mapping, quantity/charges, buff list/duration and secondary HAM/wounds to body observations before stronger profession assertions.
3. Make a tiny safe fresh-kill/harvest case before expanding patrols; make one craft/experiment/relog case before factories and economy.
4. Add a per-profession notebook with observed actions and exact version. The coverage map is complete; detailed current per-box/formula validation is still open work.

Research method: Universal Modder `game-research-websearch`; varied queries for archived Doctor/Ranger/Dancer/Musician/crafting/city/Shipwright guides, official manuals and project implementation. One Wayback CDX request for the old manual URL failed through the web tool; no repeated hammering. Working Reckoning/SWGEmu replays retained with their archive IDs. No content imported, new service installed, paid call made, or outbound message sent to Claude; this shared file is the handoff.
