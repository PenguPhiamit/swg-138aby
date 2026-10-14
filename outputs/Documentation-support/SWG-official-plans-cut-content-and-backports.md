# Official plans, cut systems and legitimate backport leads

Research pass: 13 October 2026, ChatGPT, using Universal Modder's archive-aware research method. Scope: public developer statements, legitimate release posts and already recorded owned-client inventories. **No assets downloaded, imports made or gameplay rules changed.** This is a bounded first evidence pass, not a claim to have found every cancelled feature.

Central decision list: [SWG-feature-register.md](../SWG-feature-register.md). Existing object evidence: [dormant client objects](../Content-catalogue/dormant-client-objects.md). A missing server template is only a lead: aliases, obsolete variants and unimplemented functionality must be checked separately.

## Evidence labels

- **Developer design:** a named developer says it was planned/discussed. This does not imply surviving implementation.
- **Deferred/shipped later:** not necessarily cut; do not recreate a system already present without checking.
- **Owned-client asset candidate:** recorded asset evidence, not a working feature or redistribution permission.
- **Public backport:** an author published work for another version; contemporary rights, dependencies and compatibility still need checking.
- **Community proposal:** interesting design feedback, not official plans. Kept separate.

Raph Koster's 2015 accounts are primary testimony but retrospective: he explicitly cautions about memory. The assessments and implementation difficulty below are **our inferences**, not his estimates. No original internal design document or lost build is assumed available.

## Named-developer planned systems

### Skill progression, quests and Jedi

Source: Raph Koster, [A Jedi Saga](https://www.raphkoster.com/2015/04/16/a-jedi-saga/), 16 April 2015. Read the author's article, not the comment-section speculation.

| ID | Documented direction | Purpose / maturity then | Our possible implementation and difficulty |
|---|---|---|---|
| F65 | Player quest/contract system | Let players commission one another; not delivered in the intended system | **Medium–High:** start with a fixed courier contract, escrow/reward, accept/cancel/expiry and relog state. Freeform objectives are a larger project |
| F66 | Unequal skill trees and hidden cross-profession combinations | A skill web instead of identical four-branch structures; design abandoned | **Very high** as a whole replacement: client skill UI/data, prerequisites, progression and migration. A single optional cross-skill unlock is a smaller original experiment |
| F67 | Miner profession | Named among removed professions; detailed implementation not supplied | **High/unknown:** design distinct gameplay from existing Artisan resource extraction before adding a tree |
| F68 | Individual mixed-activity Jedi unlock | A documented plan using varied per-character actions; not delivered as planned | **High:** persistent activity tracking, eligibility, discoverability and tests; this would be a new optional ruleset |
| F69 | Separate hardcore Jedi survival mode | Early idea with escalating hunters and irreversible defeat; never progressed into the shipped design | **Very high:** isolated optional mode, progression/reset, encounters and abuse prevention; no change to existing characters |

The same account distinguishes deferred cities/vehicles from cancelled ideas and states spaceflight was not an intended launch feature. Therefore **JTL is later shipped content, not evidence of a lost launch expansion**. Those distinctions help keep our restoration list honest.

### Economy and specialization

Source: Koster, [Designing a Living Society, part one](https://www.raphkoster.com/2015/04/21/designing-a-living-society-in-swg-part-one/), 21 April 2015.

| ID | Documented direction | Purpose / maturity then | Our inference: implementation |
|---|---|---|---|
| F70 | Crafting XP when customers use an item | Reward useful production and offline economic participation; dropped for implementation/database cost | **High:** record maker/item identity, aggregate eligible uses and award bounded rewards without per-use database writes. Define anti-farming and offline delivery before coding |
| F71 | Limit recipes known by a crafter | Discussed specialization to protect lower-tier markets; never adopted | **Medium–High:** UI/training/schematic rules plus migration and economic redesign. Poor default for a small LAN sandbox; optional experiment only |

These are system-design candidates, not things a model converter can recover. Existing harvesting already provides asynchronous resource gathering; this evidence does not establish a separate cancelled crop-farming system.

### Social professions, music and expression

Source: Koster, [Designing a Living Society, part two](https://www.raphkoster.com/2015/04/22/designing-a-living-society-in-swg-part-two/), 22 April 2015.

| ID | Documented direction | Purpose / maturity then | Our inference: implementation |
|---|---|---|---|
| F72 | Composer branch, scores and royalties | Players create music other performers use; replaced amid rights concerns | **Very high** for arbitrary synchronized composition/audio; a fixed original-motif score system is narrower. Needs client/audio design and content policy |
| F73 | Theater profession and craftable scripts | Reward staged player performances; dropped | **Medium** for text scripts/cues/bookable events; **High** for a real profession with automated scene/animation scoring |
| F74 | Writer profession and HoloNet channels | In-game writing/readership income and XP; cut | **Medium** for a local article terminal; **High** for profession/economy/feeds. Start with owner-authored local posts, not a new external feed service |
| F75 | Procedural expression/dance motion | Early animation ambition; simplified to loops/flourishes | **Very high:** client animation/rig integration, not simply generating another mesh |
| F76 | Automatic natural conversation circles | Social positioning/eye-contact idea beyond delivered scope | **High:** client navigation, gaze, interruption and accessibility; no automatic movement of owner characters |

These represent separate levels of ambition. A Newsnet-style local reading terminal could explore the Writer idea without claiming to restore the full cancelled profession.

### Dynamic encounters, creature behavior and visuals

Sources: [SWG's Dynamic World](https://www.raphkoster.com/2015/04/20/swgs-dynamic-world/), 20 April 2015; [A Jedi Saga](https://www.raphkoster.com/2015/04/16/a-jedi-saga/).

| ID | Documented direction | Historical status | Our inference: implementation |
|---|---|---|---|
| F77 | Dynamic POI questlets with spawned structures | Encounter ambition exceeded delivered scripted content; some structure spawning did ship | **Medium–High:** bounded camps/ambushes with objectives, placement checks, cleanup and persistence. Use current Core3 mechanisms rather than recreating original server internals |
| F78 | Emotion-aware creature routes and stampedes | Described alpha/intended behavior degraded before launch | **High:** fear states, slope choices, leash/home rules, pathing and reproducible tests. A simple bounded flee behavior is a smaller slice |
| F79 | Earlier visual richness | Developer describes early lighting/shader/character tradeoffs | **High/unknown:** compare lawful screenshots and current renderer/settings first. No evidence of a redistributable lost shader pack was established |
| F80 | Proper river-generation tooling | Developer states it was never implemented | **Very high** as native terrain-generation tooling; handcrafted terrain rules may be a narrower alternative |

Koster's temporary enemy flagging account is also useful history: [TEFs](https://www.raphkoster.com/2015/04/15/star-wars-galaxies-tefs/). It describes a system that existed and was later changed, not untouched cut content. Recreating earlier PvP behavior would be an explicit balance/version choice, not automatically a restoration.

## A later-era unshipped idea, separated from pre-CU

**F81 — Quest interiors decorated by players:** producer interview describes an omitted Chronicles interior-decoration concept. [Tony Tyson interview, 5 October 2010](https://www.engadget.com/2010-10-05-squaring-off-with-swgs-producer-teesquared-part-2.html).

Our inference: **High–Very high** for reusable player-authored instances, due to scene ownership, object placement, access control, reset and quest state. A single owner-built quest interior could be much smaller. This is later-era design inspiration, not a request to adopt NGE professions/combat. No reusable implementation was verified.

## Legitimate backports and lost-link investigations

| Lead | What the evidence actually establishes | Availability / action | Difficulty |
|---|---|---|---|
| Takhomasak Hoth/Taanab public work | Author described a stacked patch release and known Echo Base/mount caveats in 2016 | [Author's preview-thread page 7](https://modthegalaxy.com/index.php?threads%2Fnew-pre-cu-planet-hoth.697%2Fpage-7=). Historical author statement, not current compatibility proof | High |
| Hoth terrain caveats | Author described bitmap-region instability at high admin speeds in 2017 | [Author's Hoth thread](https://modthegalaxy.com/index.php?threads%2Fnew-planet-hoth.756%2Flatest=). Test current normal movement separately; do not reproduce a known crash by speeding around | High |
| Old Hoth/planet-viewer link | Later replies report unavailable links; no current mirror verified | Same author thread. **Lost-link lead**, not recovered package. Do not substitute a later server download without terms | High; link recovery first |
| Kashyyyk for PreCU | Existing catalogue identifies a creator release and MTG assets | [Resource page](https://modthegalaxy.com/index.php?resources/kashyyyk-for-precu.2/). Direct fetch failed this pass; retain prior provenance, do not call it newly verified | High for area; Very high for full campaign |
| Mustafar for PreCU | Existing catalogue identifies published asset backport | [Resource page](https://modthegalaxy.com/index.php?resources/mustafar-for-precu.3/). Direct fetch failed this pass; complete campaign not established | High–Very high |
| Taanab mini-expansion release URL | Already catalogued public release | Direct opening returned forum homepage, **not the release body**. Need working archived/original thread before validating new details | High |
| Old-AI dungeon/events/backport scripts | Existing Flurry/Bellum catalogue lists candidates | Modern API/AI port and per-module asset license audit. No source pulled or built this session | Medium–Very high |

The Hoth original post was readable as indexed thread content; that is better evidence of author's intent than an anonymous “anyone have files?” reply. A dead URL is not proof of deletion by the creator, availability of a usable mirror, or permission for a derivative server's extra art.

## Owned-client restoration shortlist

These are **existing local inventory findings**, not fresh asset extraction. The dormant-object report counts 131 SOE-client definitions without matching server templates, alongside 13,496 MTG entries. None of those counts is a count of complete missing gameplay systems.

- **Alternate city building styles (F59):** verify hospital/theater/bank/cloning variants and aliases, then deed choices/services. Medium.
- **Morag encounter (F58):** current model/template validation then original Endor quest. Medium. No original quest recovered here.
- **BE additives and dyes (F60):** determine whether existing systems already cover their function before creating recipes. Medium–High.
- **JTL component variants (F61):** confirm templates, compatible stats and intended slot/use in actual flight. High.
- **Otoh Gunga (F62):** legacy terrain alone does not establish an underwater adventure. Very high/unknown.

## What to choose first

For a playable LAN sandbox, the practical low-scope interpretations are an **original dynamic encounter**, a **local HoloNet article terminal**, a **fixed player courier contract**, or **one city-style deed**. These are recommendations inferred from the current architecture, not ready features or authorization to edit the server. Hoth remains the most developed planet direction. Full hidden skill webs, music composition and client procedural animation are research projects.

## Research record and unresolved questions

Queries included `site:raphkoster.com Star Wars Galaxies cut`, `Star Wars Galaxies developer interview cut content original plans`, `site:raphkoster.com "SWG’s Dynamic World"`, `site:raphkoster.com "Designing a Living Society"`, and MTG Hoth/Taanab/Kashyyyk/Mustafar release queries. Primary developer articles opened and read; MTG creator statements and known resource links checked. Search hits about other Star Wars games were discarded.

Open: contemporaneous developer notes corroborating the retrospective concepts; exact status by pre-CU publish; original release terms and valid archived links for backports; whether dormant paths are aliases; legitimate source/art dependency chains. No evidence established playable lost Miner/Writer/Theater packages, a complete cancelled crop-farming system, or a complete official underwater expansion. More archive work can widen this evidence list, but findings above already distinguish designs from usable content.

No screenshots captured: claims here concern text sources and existing inventories. No copyrighted article copied wholesale, no downloads or third-party accounts/services used. Source statements are summarized; effort/implementation suggestions are our own.

