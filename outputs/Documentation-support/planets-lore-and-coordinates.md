# Planet lore and galaxy coordinates — C14

13 October 2026 · ChatGPT · bounded first research pass. Wookieepedia search-index extracts were available; direct pages returned robots/402 restrictions. This is not a claim of a full article/citation audit. Unverified details stay null or explicitly pending. All prose below is original; no wiki images or game text were imported.

The [JSON](planets-coordinates.json) contains the same 24 destination records. Hoth first; ten stock SWG destinations; every catalogue planet with local terrain evidence; three additional orientation worlds. A terrain file is not proof of playable content, travel registration or import permission. Jakku is explicitly canon-only here; Legends remains the default.

## Map fitting for Claude

**Hoth: K-18, Outer Rim, Anoat sector.** Use column A=1 through Z=26 and the numeric row as an approximate square centre. It is three columns east and two rows south of Endor's H-16; seven columns west and two rows south of Tatooine's R-16. This is a coarse atlas relationship, not a hyperspace distance.

Fit a 2D affine transform from independent stock system centres to the actual stock UI button/label centres. Record which UI node supplies each pixel anchor, coordinate origin, image scaling and fit residuals. Collapse Corellia/Talus and Naboo/Rori into one anchor per system: their separate UI labels are readability offsets, not different galactic grids. Reserve display offsets for label overlap; preserve the fitted underlying location. Use leave-one-out residuals and a plotted overlay before replacing the provisional Hoth (425,225). If the stock map is stylized and a single fit is poor, report that instead of promising exact geography. No pixel position was computed or client file edited here.

## Coordinates at a glance

| Destination | Grid | Continuity | Region / sector | System | Local terrain evidence |
|---|---|---|---|---|---|
| Hoth | K-18 | Legends | Outer Rim Territories / Greater Javin / Anoat | Hoth system | catalogue evidence |
| Corellia | M-11 | Legends | Core Worlds / Corellian | Corellian system | not established by MTG catalogue |
| Dantooine | L-4 | Legends | Outer Rim Territories / New Territories / Raioballo | Dantooine system | not established by MTG catalogue |
| Dathomir | O-6 | Legends | Outer Rim Territories / New Territories / Quelii | Dathomir system | not established by MTG catalogue |
| Endor | H-16 | Legends | Outer Rim Territories / Moddell (within Zuma) | Endor system | not established by MTG catalogue |
| Lok | Q-17 | Legends | Outer Rim Territories / Trailing Sectors / Karthakk | Karthakk system | not established by MTG catalogue |
| Naboo | O-17 | Legends | Mid Rim / Chommell | Naboo system | not established by MTG catalogue |
| Rori | O-17 | Legends | Mid Rim / Chommell | Naboo system | not established by MTG catalogue |
| Talus | M-11 | Legends | Core Worlds / Corellian | Corellian system | not established by MTG catalogue |
| Tatooine | R-16 | Legends | Outer Rim Territories / Arkanis | Tatoo system | not established by MTG catalogue |
| Yavin 4 | P-6 | Legends | Outer Rim Territories / Gordian Reach | Yavin system | not established by MTG catalogue |
| Taanab | O-8 | Legends | Inner Rim / Trans-Hydian / not verified | Taanab system | catalogue evidence |
| Dromund Kaas | R-5 | Legends | Outer Rim Territories / Esstran / Sith Worlds | Dromund system | catalogue evidence |
| Mandalore | O-7 | Legends | Outer Rim Territories / Mandalore | Mandalore system | catalogue evidence |
| Chandrila | L-9 | Legends | Core Worlds / Ringali Shell / Bormea | Chandrila system | catalogue evidence |
| Coruscant | L-9 | Legends | Core Worlds / Corusca / Coruscant | Coruscant system | catalogue evidence |
| Jakku | I-13 | canon exception | Inner Rim / Western Reaches / Unnamed Jakku sector | Jakku system | catalogue evidence |
| Korriban (MTG zone moraband) | R-5 | Legends | Outer Rim Territories / Trans-Hydian / Esstran / Sith Worlds | Horuset system | catalogue evidence |
| Nal Hutta | S-12 | Legends | Mid Rim / Hutt Space / Sector not verified | Y'Toub system | catalogue evidence |
| Kashyyyk | P-9 | Legends | Mid Rim / Mytaranor | Kashyyyk system | catalogue evidence |
| Mustafar | L-19 | Legends | Outer Rim Territories / Western Reaches / Atravis | Mustafar system | catalogue evidence |
| Dagobah | M-19 | Legends | Outer Rim Territories / Sluis | Dagobah system | not established by MTG catalogue |
| Bespin | K-18 | Legends | Outer Rim Territories / Anoat | Bespin system | not established by MTG catalogue |
| Alderaan | M-10 | Legends | Core Worlds / Alderaan | Alderaan system | not established by MTG catalogue |

## Destination records

### Hoth — K-18

Hoth is a remote frozen world with dangerous wildlife. The Rebels built Echo Base in its caves, then lost it during the Imperial attack in 3 ABY. A local expedition can focus on shelter, supply routes and predator encounters without assuming our snapshot already contains the famous base.

- Region/sector/system: Outer Rim Territories / Greater Javin; Anoat; Hoth system.
- Moons/orbital context: 3 (names not verified).
- Climate/terrain: Frozen ice plains, glaciers and mountains.
- Species/creatures: Wampas; tauntauns.
- Places/content anchors: Echo Base; wampa caves; Clabburn Range.
- Sources: [Hoth/Legends](https://starwars.fandom.com/wiki/Hoth/Legends), [Hoth system/Legends](https://starwars.fandom.com/wiki/Hoth_system/Legends), [Wampa/Legends](https://starwars.fandom.com/wiki/Wampa/Legends), [Tauntaun/Legends](https://starwars.fandom.com/wiki/Tauntaun/Legends), [Echo Base/Legends](https://starwars.fandom.com/wiki/Echo_Base/Legends).

### Corellia — M-11

Corellia is a major inhabited world of the Corellian system. Its communities include Humans, Drall and Selonians, with many inhabitants living outside the capital. Coronet and its surrounding economy suit shipping, investigation and civilian supply stories.

- Region/sector/system: Core Worlds; Corellian; Corellian system.
- Moons/orbital context: Gus Talon and Gus Treta (system source).
- Climate/terrain: Temperate; farms, towns and coasts.
- Species/creatures: Humans, Drall and Selonians (residents; origins differ).
- Places/content anchors: Coronet; Tyrena; Gold Beaches.
- Sources: [Corellia/Legends](https://starwars.fandom.com/wiki/Corellia/Legends), [Corell/Legends](https://starwars.fandom.com/wiki/Corell/Legends), [Talus/Legends](https://starwars.fandom.com/wiki/Talus/Legends).

### Dantooine — L-4

Dantooine is a lightly developed agricultural world away from heavy galactic traffic. Native Dantari share it with settlers and varied wildlife. Ancient structures and abandoned military sites support exploration, but Old Republic story events must not be treated as current happenings.

- Region/sector/system: Outer Rim Territories / New Territories; Raioballo; Dantooine system.
- Moons/orbital context: 2 (names not verified).
- Climate/terrain: Grasslands, rivers, lakes and blba trees.
- Species/creatures: Dantari; kath hounds; kinrath; graul.
- Places/content anchors: Ruined Jedi Enclave; former Rebel base.
- Sources: [Dantooine/Legends](https://starwars.fandom.com/wiki/Dantooine/Legends).

### Dathomir — O-6

Dathomir is a remote world associated with witch clans and rancors. Singing Mountain is an important place for its namesake clan. Clan relationships and dangerous wilderness offer grounded SWG objectives without importing later canon-only landscapes wholesale.

- Region/sector/system: Outer Rim Territories / New Territories; Quelii; Dathomir system.
- Moons/orbital context: 4, including Koratas.
- Climate/terrain: Mountain/river terrain documented at Singing Mountain; broader climate pending.
- Species/creatures: Dathomiri Witches; rancors; gaping spiders; malklocs.
- Places/content anchors: Singing Mountain Clan settlement; Singing Mountain.
- Sources: [Dathomir system/Legends](https://starwars.fandom.com/wiki/Dathomir_system/Legends), [Singing Mountain (Dathomir)/Legends](https://starwars.fandom.com/wiki/Singing_Mountain_(Dathomir)/Legends).

### Endor — H-16

SWG Endor is the forest moon rather than its parent gas giant. It has a broad ecosystem and a history shaped partly by crashed ships. Wilderness and settlement content fit it, while Death Star-era installations need a deliberate timeline check.

- Region/sector/system: Outer Rim Territories; Moddell (within Zuma); Endor system.
- Moons/orbital context: Playable destination is the forest moon of gas giant Endor; giant has 9 moons.
- Climate/terrain: Temperate forests, mountains, lakes and savannas.
- Species/creatures: Ewoks; Duloks; introduced fauna varies by era.
- Places/content anchors: Forest settlements; wilderness crash sites.
- Sources: [Endor/Legends](https://starwars.fandom.com/wiki/Endor/Legends), [Endor system/Legends](https://starwars.fandom.com/wiki/Endor_system/Legends).

### Lok — Q-17

Lok is a harsh world associated with pirates and Nym. Its dangerous terrain and wildlife make travel outside the stronghold consequential. Salvage, contraband and faction-pressure stories fit its established character.

- Region/sector/system: Outer Rim Territories / Trailing Sectors; Karthakk; Karthakk system.
- Moons/orbital context: 2, including Khons.
- Climate/terrain: Arid deserts, jagged ranges, sulfur pools and lava pits.
- Species/creatures: Kimogila; mixed settler/pirate population.
- Places/content anchors: Nym's Stronghold; Kimogila Town.
- Sources: [Lok/Legends](https://starwars.fandom.com/wiki/Lok/Legends).

### Naboo — O-17

Naboo combines extensive natural landscapes with distinctive settled societies. Its native Gungans and Human population have separate histories and communities. Civilian diplomacy and Imperial-era local tensions can coexist without assuming every famous Clone Wars event is occurring now.

- Region/sector/system: Mid Rim; Chommell; Naboo system.
- Moons/orbital context: Rori; Ohma-D'un; unnamed third moon.
- Climate/terrain: Temperate plains, hills, swamps, mountains and seas.
- Species/creatures: Gungans; Human Naboo colonists.
- Places/content anchors: Lake Paonga; Lianorm Swamp; Emperor's Retreat.
- Sources: [Naboo/Legends](https://starwars.fandom.com/wiki/Naboo/Legends), [Rori/Legends](https://starwars.fandom.com/wiki/Rori/Legends), [Third moon of Naboo](https://starwars.fandom.com/wiki/Third_moon_of_Naboo).

### Rori — O-17

Rori is one of Naboo's three moons. Its overgrown terrain makes settlement and travel difficult. Narmle and Restuss are established locations, but their exact state must follow the server's chosen era rather than an assumed later-game event.

- Region/sector/system: Mid Rim; Chommell; Naboo system.
- Moons/orbital context: Rori is a moon of Naboo; submoons not verified.
- Climate/terrain: Swamps, hills, forests and grasslands under gray skies.
- Species/creatures: Bark mites; tortons; borgle bats; Gungan outposts.
- Places/content anchors: Narmle; Restuss; Garyn Raider sites.
- Sources: [Rori/Legends](https://starwars.fandom.com/wiki/Rori/Legends).

### Talus — M-11

Talus and Tralus form the Double Worlds around a shared centre of gravity. Talus has farming, mining and manufacturing communities. Its federal institutions and Imperial scrutiny support civic and industrial stories distinct from Corellia's capital.

- Region/sector/system: Core Worlds; Corellian; Corellian system.
- Moons/orbital context: Several (names not verified); Tralus is a paired planet, not a moon.
- Climate/terrain: Temperate forests, grass plains and mudflats.
- Species/creatures: Humans, Drall, Selonians; Zabrak colony.
- Places/content anchors: Dearic; Nashal; Centerpoint in the system.
- Sources: [Talus/Legends](https://starwars.fandom.com/wiki/Talus/Legends), [Corellian system/Legends](https://starwars.fandom.com/wiki/Corellian_system/Legends).

### Tatooine — R-16

Tatooine is a remote desert world in a binary-star system. Moisture farming and equipment trading sustain many residents. Criminal power and scattered settlements make local survival and transport suitable themes.

- Region/sector/system: Outer Rim Territories; Arkanis; Tatoo system.
- Moons/orbital context: not verified in this pass.
- Climate/terrain: Desert; dry settlements and moisture farms.
- Species/creatures: Jawas; Tusken Raiders; mixed offworld population.
- Places/content anchors: Mos Eisley; Jabba's Palace; Jundland Wastes.
- Sources: [Tatooine/Legends](https://starwars.fandom.com/wiki/Tatooine/Legends), [Category:Locations in grid square R-16](https://starwars.fandom.com/wiki/Category:Locations_in_grid_square_R-16).

### Yavin 4 — P-6

Yavin 4 is a large habitable moon of Yavin Prime. Its jungles conceal structures linked to ancient Sith history and the Rebel base. Exploration should separate those historical layers and avoid placing later Jedi-academy events into an earlier SWG era.

- Region/sector/system: Outer Rim Territories; Gordian Reach; Yavin system.
- Moons/orbital context: Moon of Yavin Prime; submoon counts conflict (0/1/2 in article).
- Climate/terrain: Tropical jungle, low-relief continents, mountains and volcanoes.
- Species/creatures: Massassi heritage; present living native species not established here.
- Places/content anchors: Great Temple; jungle ruins.
- Sources: [Yavin 4/Legends](https://starwars.fandom.com/wiki/Yavin_4/Legends), [Yavin system/Legends](https://starwars.fandom.com/wiki/Yavin_system/Legends).

### Taanab — O-8

Taanab is an agricultural world on useful trade routes. Its commercial farms and imported animals distinguish it from untouched wilderness. Pirate raids and cargo protection are suitable local stories; do not label imported farm animals indigenous.

- Region/sector/system: Inner Rim / Trans-Hydian; sector not verified; Taanab system.
- Moons/orbital context: 1 (unnamed here).
- Climate/terrain: Mild fields, waterways and intensive agriculture.
- Species/creatures: Imported roba, staga, nerfs and banthas; no original animal fauna per article.
- Places/content anchors: Pandath; Banthal Company Docks.
- Sources: [Taanab/Legends](https://starwars.fandom.com/wiki/Taanab/Legends).

### Dromund Kaas — R-5

Dromund Kaas has a long Sith history and extensive swamps. Its Old Republic capital and later forgotten temples belong to different periods. A Galactic Civil War expedition should not simply reproduce the populated SWTOR capital.

- Region/sector/system: Outer Rim Territories; Esstran / Sith Worlds; Dromund system.
- Moons/orbital context: 2 (names not verified).
- Climate/terrain: Sea, swamp and jungle.
- Species/creatures: Local monsters not individually verified in this pass.
- Places/content anchors: Dark Force Temple; historical Kaas City.
- Sources: [Dromund Kaas/Legends](https://starwars.fandom.com/wiki/Dromund_Kaas/Legends), [Dromund system](https://starwars.fandom.com/wiki/Dromund_system), [Category:Locations in grid square R-5](https://starwars.fandom.com/wiki/Category:Locations_in_grid_square_R-5).

### Mandalore — O-7

Mandalore is the cultural homeworld of the Mandalorians. Legends describes northern forests and Keldabe alongside other regional environments. Mining, clan relationships and Imperial pressure suit this period without reducing the entire world to one later television depiction.

- Region/sector/system: Outer Rim Territories; Mandalore; Mandalore system.
- Moons/orbital context: 2, including Concordia.
- Climate/terrain: Northern forests with cold winters; regional variety.
- Species/creatures: Mandalorian residents; shatuals; strills.
- Places/content anchors: Keldabe; Kelita River; Oyu'baat; MandalMotors.
- Sources: [Mandalore/Legends](https://starwars.fandom.com/wiki/Mandalore/Legends), [Concordia/Legends](https://starwars.fandom.com/wiki/Concordia/Legends), [Keldabe/Legends](https://starwars.fandom.com/wiki/Keldabe/Legends).

### Chandrila — L-9

Chandrila is a temperate Core World. Its towns, natural parks and cultural sites offer a less militarized setting than a battlefield planet. Local antiquities, civic and supply stories can use these places without assuming later New Republic institutions already exist.

- Region/sector/system: Core Worlds / Ringali Shell; Bormea; Chandrila system.
- Moons/orbital context: Chandra; Chandrakant.
- Climate/terrain: Temperate forests, hills, plains and seas.
- Species/creatures: Residents/species not individually verified here.
- Places/content anchors: Hanna City; Crystal Canyons; Silver Sea.
- Sources: [Chandrila/Legends](https://starwars.fandom.com/wiki/Chandrila/Legends), [Chandra/Legends](https://starwars.fandom.com/wiki/Chandra/Legends).

### Coruscant — L-9

Coruscant occupies a central political and economic position in galactic history. Its location is also the conventional origin for one coordinate system. Any local urban district needs a defined Imperial-era identity rather than a blend of unrelated historical capitals.

- Region/sector/system: Core Worlds; Corusca / Coruscant; Coruscant system.
- Moons/orbital context: Centax-1, Centax-2, Centax-3; Hesperidium listed as fourth.
- Climate/terrain: Urban world; detailed climate not verified in extract.
- Species/creatures: Cosmopolitan residents; individual native fauna pending.
- Places/content anchors: Political/urban districts (specific target locations pending).
- Sources: [Coruscant/Legends](https://starwars.fandom.com/wiki/Coruscant/Legends), [Coruscant system/Legends](https://starwars.fandom.com/wiki/Coruscant_system/Legends).

### Jakku — I-13

Jakku is a canon world with a desert landscape. Its famous wreck fields and Niima Outpost arose after the Battle of Jakku. A pre-CU-era adaptation must be labelled an optional continuity addition and must not transplant that later aftermath without a deliberate alternate-history choice.

- Region/sector/system: Inner Rim / Western Reaches; Unnamed Jakku sector; Jakku system.
- Moons/orbital context: 2 (names not verified).
- Climate/terrain: Arid badlands, dunes and salt flats.
- Species/creatures: Teedo; Uthuthma; diverse settlers.
- Places/content anchors: Desert settlements; Niima Outpost and graveyard are later-period examples only.
- Sources: [Jakku](https://starwars.fandom.com/wiki/Jakku), [Jakku system](https://starwars.fandom.com/wiki/Jakku_system), [Niima Outpost](https://starwars.fandom.com/wiki/Niima_Outpost).

### Korriban (MTG zone moraband) — R-5

Korriban is an ancient sacred world of the Sith. Its burial sites and dark-side history make it a place for carefully bounded exploration. The MTG zone name moraband is a runtime alias, not permission to blend all canon and Legends events.

- Region/sector/system: Outer Rim Territories / Trans-Hydian; Esstran / Sith Worlds; Horuset system.
- Moons/orbital context: 7 (names not verified).
- Climate/terrain: Dry tomb world; detailed climate pending.
- Species/creatures: Sith species historically; living population depends on era.
- Places/content anchors: Ancient Dark Lord tombs.
- Sources: [Korriban/Legends](https://starwars.fandom.com/wiki/Korriban/Legends).

### Nal Hutta — S-12

Nal Hutta was once called Evocar. The Hutts displaced the native Evocii and made it a centre of their power. Local stories should reflect clan control and that history, rather than describing Hutts as the original native species.

- Region/sector/system: Mid Rim / Hutt Space; Sector not verified; Y'Toub system.
- Moons/orbital context: Nar Shaddaa confirmed; complete moon inventory pending.
- Climate/terrain: Swamp environment; detailed climate pending.
- Species/creatures: Evocii native; Hutts and t'landa Til are arrivals.
- Places/content anchors: Bilbousa; Jiguuna; Nar Shaddaa in orbit.
- Sources: [Nal Hutta/Legends](https://starwars.fandom.com/wiki/Nal_Hutta/Legends), [Hutt Space/Legends](https://starwars.fandom.com/wiki/Hutt_Space/Legends), [Category:Locations in grid square S-12](https://starwars.fandom.com/wiki/Category:Locations_in_grid_square_S-12).

### Kashyyyk — P-9

Kashyyyk is the Wookiee homeworld. Its system also contains Trandosha and several inhabited moons. A bounded forest settlement or rescue story is feasible separately from a complete port of the later SWG expansion campaign.

- Region/sector/system: Mid Rim; Mytaranor; Kashyyyk system.
- Moons/orbital context: 3, including an unnamed farming moon.
- Climate/terrain: Forested world; full climate detail pending.
- Species/creatures: Wookiees; other wildlife pending specific article checks.
- Places/content anchors: Forest communities; Avatar Orbital Platform in system.
- Sources: [Kashyyyk/Legends](https://starwars.fandom.com/wiki/Kashyyyk/Legends), [Kashyyyk system/Legends](https://starwars.fandom.com/wiki/Kashyyyk_system/Legends).

### Mustafar — L-19

Mustafar is a volcanically unstable mining world. Native Mustafarians adapted their work and settlements to its severe conditions. Original mining and rescue objectives can use that setting without implying the complete Trials of Obi-Wan campaign has been backported.

- Region/sector/system: Outer Rim Territories / Western Reaches; Atravis; Mustafar system.
- Moons/orbital context: not verified in this pass.
- Climate/terrain: Volcanic lava rivers, ash and obsidian mountains.
- Species/creatures: Northern/Southern Mustafarians; lava fleas; blistmoks; jundaks.
- Places/content anchors: Fralideja; mining settlements; Berken's Flow.
- Sources: [Mustafar/Legends](https://starwars.fandom.com/wiki/Mustafar/Legends), [Mustafar system/Legends](https://starwars.fandom.com/wiki/Mustafar_system/Legends), [Mustafarian/Legends](https://starwars.fandom.com/wiki/Mustafarian/Legends).

### Dagobah — M-19

Dagobah is a remote swamp world with abundant life and little settlement. It sheltered Yoda after Order 66. Exploration can emphasize navigation and ecology without making access to its hidden resident routine.

- Region/sector/system: Outer Rim Territories; Sluis; Dagobah system.
- Moons/orbital context: 1 (name not verified).
- Climate/terrain: Humid swamps, marshes and dense forests.
- Species/creatures: Hepsalum Tash; bogwings; dragonsnakes; nudj.
- Places/content anchors: Yoda's refuge; cave.
- Sources: [Dagobah/Legends](https://starwars.fandom.com/wiki/Dagobah/Legends).

### Bespin — K-18

Bespin is a gas giant with a habitable atmospheric band. Cloud City occupies that band rather than a solid planetary surface. A port therefore needs convincing platform boundaries and travel rules, not merely a conventional walkable ground terrain.

- Region/sector/system: Outer Rim Territories; Anoat; Bespin system.
- Moons/orbital context: Several (names/count not verified).
- Climate/terrain: Gas giant; narrow habitable atmospheric layer.
- Species/creatures: Humans/Ugnaught residents; airborne algae.
- Places/content anchors: Cloud City; BesGas Three.
- Sources: [Bespin/Legends](https://starwars.fandom.com/wiki/Bespin/Legends), [List of planets B](https://starwars.fandom.com/wiki/List_of_planets_B).

### Alderaan — M-10

Alderaan was destroyed by the first Death Star before the Battle of Yavin. Its former orbit became the Graveyard asteroid field. A living ground-world destination conflicts with an ordinary post-Yavin SWG timeline and would need an explicit flashback or alternate setting.

- Region/sector/system: Core Worlds; Alderaan; Alderaan system.
- Moons/orbital context: One historical moon; destruction chronology requires checking.
- Climate/terrain: Destroyed in normal post-Yavin timeline; pre-destruction terrain not catalogued here.
- Species/creatures: Native species not verified in this pass.
- Places/content anchors: The Graveyard after destruction.
- Sources: [Alderaan system/Legends](https://starwars.fandom.com/wiki/Alderaan_system/Legends), [Moon of Alderaan](https://starwars.fandom.com/wiki/Moon_of_Alderaan).

## Open questions

Confirm server date before Echo Base, Alderaan, Niima Outpost, Restuss or later Jedi institutions. Verify full moon/sector inventories only when a selected content slice needs them; a missing value here does not mean no moons/sector exist. Kaas and moraband are runtime aliases. Native species and later residents are explicitly distinct where the excerpts establish that difference. Compare wiki climate to the actual MTG terrain before designing spawns.

No gameplay, client rendering or map position tested. This pass supplies lore and coarse coordinates for Claude's implementation; it does not authorize new downloads, client installation or live deployment.

## Follow-up: computed UI fit rejected (14 October)

[Calibration evidence](hoth/galaxy-map-calibration.md) now supplies the attempted fit and stock-anchor overlay. Max residual 132.63 px and leave-one-out236.66px make automatic Hoth placement unreliable. No client files changed; all JSON ui_pixel_position values remain null.
