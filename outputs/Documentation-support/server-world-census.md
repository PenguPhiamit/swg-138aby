# C21 checkpoint 2 — worlds and places

14 October 2026, ChatGPT. Bounded inventory pass; **overall C21 and the full world lore audit remain incomplete**. No server reads/changes, bots, downloads, imports or deployments. Reproduce the local join with `python outputs/tools/research/world_census.py`; [JSON](server-world-census.json) records input hashes and all 25 rows.

## Counts that can be defended

The 24 existing catalogue rows plus owner-selected Ossus represent **20 ground-world candidates, three stations, one city and one test-terrain family**. These are candidate identities, not playable-zone totals. One ground candidate, Jakku, remains an explicit canon exception. Moraband/Korriban and Mon Calamari/Dac are aliases within their existing rows, not extra planets. Otoh Gunga belongs under Naboo; the Umbra/developer row contains multiple files and cannot be counted as one finished world.

Eleven catalogue zones have exact terrain **and** snapshot paths in the saved evidence. That is only file-level evidence, not transitive art closure or functioning travel. Zeltros's empty catalogue evidence array understates possession: separate retained manifests list a 59-member client ZIP and 25-member server ZIP. Those are member counts, not 84 unique usable assets. Ossus has a separate original O1 staging package. Otoh Gunga has a legacy terrain path without a proven finished city package. None of these counts establishes how many planets currently work.

## Implementation matrix

Effort is a comparative estimate for a first playable slice, not person-hours. H = substantial integration; VH = extensive original environment/system work. Confidence is low until dependency closure and real-client checks. Every row needs original gameplay text, licence/art review and travel/relog validation.

| Candidate | What we have in this audit | Remaining implementation / decision | Effort |
|---|---|---|---|
| Taanab | Terrain/snapshot; public mini-expansion lead | Pin package/version, resolve dependencies, adapt NPCs/encounters and zone/travel | H |
| Hoth | Terrain/snapshot; dev/test adaptation and dated bot reports | Resolve latest camp-prop failure, reconcile C22 fixes; real-client cave/terrain/loot/resource/quest acceptance | Medium–H remaining |
| Dromund Kaas | Terrain/snapshot; public release/source leads | Port zone/cities/encounters; decide Legacy-era inhabitants rather than copying an earlier Sith government | H |
| Mandalore | Terrain/snapshot; original world/NPC/cave release lead | Port source/API, verify cave placement and era-appropriate settlements | H |
| Chandrila | Terrain/snapshot; public city/POI script leads | Dependency closure and city gameplay; historical completion claim is not our runtime test | H |
| Coruscant | Terrain/snapshot; district/race script leads | Urban geometry/collision/navigation closure, district gameplay; additional third-party art needs its own permission | H–VH |
| Jakku | Terrain/snapshot | Owner's canon-exception choice; do not silently graft First Order/Rey history into Legends | H |
| Korriban (zone `moraband`) | Terrain/snapshot; inherited lore record | Keep zone key separate from display name; tomb/cave/encounter and chronology audit | H |
| Nal Hutta (zone `hutta`) | Terrain/snapshot | City/swamp traversal, inhabitants, travel and encounters; no imported third-party gameplay assumed | H |
| Kashyyyk | Terrain/snapshot; existing client/mobile families | Decide planetary/subzone layout, reconcile stock expansion assets with pre-CU scripts and era | H–VH |
| Mustafar | Terrain/snapshot; existing client/mobile families | Dungeon/quest/mechanic adaptation and heat/terrain presentation; inspect each dependency | H–VH |
| Dagobah | Advertised third-party implementation only | Creator package/rights hold; original swamp world remains possible | VH original route |
| Mon Calamari / Dac | Advertised third-party implementation only | Package/rights hold; water/city environment and chronology audit | VH |
| Kuat | Advertised third-party implementation only | Package/rights hold; choose playable ground/interior scope rather than presuming shipyards/JTL work | VH |
| Ord Mantell | Advertised third-party implementation only | Package/rights hold; original settlements/encounters and station links | VH |
| Bespin | Advertised third-party implementation only | Package/rights hold; suspended city/interiors, safe falls/spawns and navigation | VH |
| Kessel | Advertised third-party implementation only | Package/rights hold; Legends geography/history, mines and travel | VH |
| Zeltros | Downloaded client/server ZIP manifests | Legacy paths/API and MTG closure; **CC-BY-NC claim conflicts with NC-out policy**: hold import pending owner/licence decision | H, rights held |
| Tansarii Point Station | Station object candidates; no complete usable package established | Interior layout/portals, travel, vendors/quests; ground-interior prototype can be scoped separately from spaceflight | H–VH |
| Nova Orion Station | Advertised third-party implementation; indirect lore evidence | Creator rights/package hold; verify layout independently, not “same design therefore same files” | H–VH |
| Centerpoint Station | Advertised third-party implementation only | Rights hold **and** destroyed in 40 ABY; historical scenario or explicit alternate history, not intact Legacy-era default | VH |
| Otoh Gunga | Legacy `terrain/otoh_gunga.trn` | Naboo city/interior slice; bubble geometry, safe arrivals/portals, water presentation; underwater locomotion unproven | VH |
| Geonosis | Announced intention, no finished public world verified | Original terrain/snapshot, hive/arena/industry art, scripts and travel; Yavin IV bio-lab is a different place | VH |
| Umbra/developer terrains | Historical test-file family | Inspect a finite individual terrain for test utility; not a lore destination or reusable finished world | Unknown |
| Ossus | Original O1 terrain/environment/registration staging | Compose tables with Hoth; validate writer/art closure; snapshot/server zone/navmesh/travel/gameplay and exact 137 ABY story point | H–VH |

Do not reject optional encounters merely because these packages are incomplete: retain concepts as adaptation or original-replacement work. This matrix authorizes neither author contact nor imports. Source release claims and rights labels above are inherited from the saved catalogue, not newly renewed grants.

## Fresh lore checks and access limits

Direct opens of Ossus, Centerpoint and Otoh Gunga returned 402/inaccessible errors; subsequent searches reported robots restrictions. No bypass was attempted. Seven article extracts were available through search. These establish narrow facts below, not full article or underlying-book verification. Existing C14 records remain inherited evidence for the other already-mapped worlds; unvisited articles remain pending.

- **Ossus:** the new academy and its benchland setting fit a playable concept, but the Temple is destroyed in 137 ABY. “Legacy-era” alone does not choose before/after that event. Fable's staged O1 remains story-neutral; its geometry does not decide inhabitants or an intact Temple. [Ossus, Legends](https://starwars.fandom.com/wiki/Ossus/Legends).
- **Centerpoint:** destruction is explicitly dated 40 ABY. An intact station in a 130–138 ABY setting would require an intentional departure or historical instance; a lore entry is not proof that a ruin or replacement exists. Preserve the encounter option without inventing surviving geometry. [Centerpoint Station](https://starwars.fandom.com/wiki/Centerpoint_Station), [Second Galactic Civil War battle](https://starwars.fandom.com/wiki/Battle_of_Centerpoint_Station_%28Second_Galactic_Civil_War%29).
- **Otoh Gunga:** a Gungan city on Naboo, not a new planet. City/interior travel can be considered without claiming a complete underwater simulation. [Otoh Gunga, Legends](https://starwars.fandom.com/wiki/Otoh_Gunga/Legends), [Naboo, Legends](https://starwars.fandom.com/wiki/Naboo/Legends).
- **Tansarii/Nova Orion:** Tansarii is near Ord Mantell and shares the other station's design. Nova Orion's direct article was not retrieved; its identity is supported here only indirectly by Tansarii's article. Do not confuse it with **Nova Station**, a different Carida-system location returned by search. [Tansarii Point Station, Legends](https://starwars.fandom.com/wiki/Tansarii_Point_Station/Legends).
- **Geonosis:** a rocky desert world in the Arkanis sector. Use the Legends article; a separate canon extermination account must not be silently transferred. [Geonosis, Legends](https://starwars.fandom.com/wiki/Geonosis/Legends).
- **Zeltros:** Legends homeworld of Zeltrons; a world package does not supply a cleared playable species package. [Zeltros, Legends](https://starwars.fandom.com/wiki/Zeltros/Legends).
- **Jakku:** the retrieved article describes the canon New Republic/First Order storyline. The existing project treats it as a canon exception; this pass did not establish a Legends history for it. [Jakku](https://starwars.fandom.com/wiki/Jakku).

All descriptions are original paraphrases. No wiki images/text assets were imported. Required credits remain separate from the owner's outbound personal-name redaction rule.

## Dated Hoth and Ossus evidence

`Bot-reports/OVERNIGHT.md` records a 13:27 test restart and a 13:38 Hoth content run summarized at 14:01 as **32/33**, failing salvage-detail props (0). This is a saved bot result, not our own runtime execution or full human-client acceptance. C22's report identifies source issues and explicitly excludes later quest/den fixes; reconcile commit dates before reusing its findings as current defects. Hoth is the strongest integration candidate here, but “all works” is not supported.

`Fable-ossus/README.md` lists 15 staged O1 client files and warns that its four registration tables were based on stock copies. Packing those over Hoth's versions can discard Hoth rows. Compose both planets' entries in one builder and verify both travel/waypoint/CRC/name records. The original terrain uses referenced stock art; neither a binary parse nor that provenance establishes rendering, collision, snapshot placement or playability.

## Research journal and next bounded pass

Queries: exact Wookieepedia URLs for Ossus/Centerpoint/Otoh Gunga; `site:starwars.fandom.com` with Ossus 137 ABY, Centerpoint destruction 40 ABY, Otoh Gunga city Naboo, Nova Orion/Tansarii, Geonosis Legends, Zeltros Legends, Korriban/Moraband, Jakku Legends. A Korriban query returned discussion/tag excerpts; no new authoritative article claim was based on those.

Universal Modder's knowledge-base search was attempted through its installed CLI; it failed because that runtime lacks PyYAML. No install performed. Web research continued with the browser search tool. No screenshots were needed: no visual/geometry claim was verified.

**Next:** refresh the 11 inherited terrain-world lore records and audit the six permission-held planets' exact Legends pages; verify Nova Orion's direct article and individual station asset paths. Then reconcile each candidate's transitive dependencies against selected lawful local packages in finite batches. Checkpoint 2 remains partial. The subsequent species/tames, equipment, professions/resources and systems checkpoints remain open; do not restart the closed KOTOR census.
