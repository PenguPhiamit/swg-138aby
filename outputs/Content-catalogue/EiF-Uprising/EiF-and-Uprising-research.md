# EiF and Uprising: LAN content research

Researched 13 October 2026. No server or working-client changes made.

## Decisions for this project

- Sentinel’s Republic is excluded from the active content plan. Missing encounters and quests can be written for our own setting.
- The immediate target is a private LAN game. A later public launch is a separate decision; record creator permissions, licenses and any agreed payment against each contribution.
- Published code, downloadable player patches, complete content and permission to redistribute artwork are different findings.

## The significant EiF discovery

The official [EiF public server repository](https://gitlab.com/Empire-In-Flames/EiF-Public) contains an **August 9, 2017** snapshot at `35bdbed4bba3015d592c928ecf30fb0e40e336c6`. Its root COPYING is AGPLv3, and the player Lua files retain LGPL-2-or-later headers. The selected source is available under those notices; preserve credits and applicable corresponding-source requirements. No separate purchase requirement was found for the published code.

**The race header has 66 gender entries representing 47 species/character options: 10 original options plus 37 additions.** Player Lua registration and shared-template declarations were checked. This is source evidence, not a statement that all 47 were enabled in character creation or are playable on today’s EiF.

The public client patch repository also exists. Its pinned manifest lists 23 TRE archives totaling 4,333,368,394 bytes, dated October 19, 2025. One original archive, starsider01.tre, was downloaded into the separate research collection. Its size and MD5 match the published manifest, and its index contains matching player templates for all 37 legacy additions. Sixteen of those additions already have matching MTG player templates. No client patch was installed.

This resolves the earlier uncertainty about whether the additional species files exist. It does **not** establish a blanket artwork license for the entire EiF player patch. Its README has only the project title and no general asset reuse grant. Client-selection data and full appearance/equipment dependencies still require review.

The same server snapshot loads `bin/custom_scripts/screenplays/screenplays.lua`, but the public tree contains only a .gitignore under custom_scripts. Modern heroics and event scripts cannot be recovered merely by downloading its published server tree.

## All 37 legacy additions with source evidence

| Species / character option | Server genders | Already in MTG | EiF matching player template |
|---|---|---|---|
| Hutt | male, female | Yes | Found in starsider01 |
| Nautolan | male | Yes | Found in starsider01 |
| Togruta | female | Yes | Found in starsider01 |
| Chiss | male, female | Yes | Found in starsider01 |
| Devaronian | male | Yes | Found in starsider01 |
| Gran | male | Yes | Found in starsider01 |
| Ishi Tib | male | Yes | Found in starsider01 |
| Nightsister | female | Yes | Found in starsider01 |
| Nikto | male | Yes | Found in starsider01 |
| Quarren | male | Yes | Found in starsider01 |
| Singing Mountain Clan Witch | female | Yes | Found in starsider01 |
| Weequay | male | Yes | Found in starsider01 |
| Aqualish | male, female | Yes | Found in starsider01 |
| Bith | male, female | Yes | Found in starsider01 |
| Gotal | male | Yes | Found in starsider01 |
| Talz | male | Yes | Found in starsider01 |
| Abyssin | male | No matching player template found | Found in starsider01 |
| Arcona | male | No matching player template found | Found in starsider01 |
| Cerean | male | No matching player template found | Found in starsider01 |
| Duros | male | No matching player template found | Found in starsider01 |
| Gungan | male | No matching player template found | Found in starsider01 |
| Iktotchi | male | No matching player template found | Found in starsider01 |
| Jenet | male | No matching player template found | Found in starsider01 |
| Kel Dor | male | No matching player template found | Found in starsider01 |
| Kubaz | male | No matching player template found | Found in starsider01 |
| Sanyassan | male, female | No matching player template found | Found in starsider01 |
| Chadra-Fan | male, female | No matching player template found | Found in starsider01 |
| Droid (NK3 label in source; not verified IG-100) | male | No matching player template found | Found in starsider01 |
| Dug | male | No matching player template found | Found in starsider01 |
| Ewok | male, female | No matching player template found | Found in starsider01 |
| Feeorin | male | No matching player template found | Found in starsider01 |
| Geonosian | male | No matching player template found | Found in starsider01 |
| Ortolan | male | No matching player template found | Found in starsider01 |
| Togorian | male | No matching player template found | Found in starsider01 |
| Toydarian | male | No matching player template found | Found in starsider01 |
| Mirialan | male, female | No matching player template found | Found in starsider01 |
| Zeltron | male, female | No matching player template found | Found in starsider01 |

The authoritative list is the [pinned race header](https://gitlab.com/Empire-In-Flames/EiF-Public/-/blob/35bdbed4bba3015d592c928ecf30fb0e40e336c6/MMOCoreORB/src/server/zone/objects/player/Races.h), paired with its player Lua files. Nightsister and Singing Mountain Clan are character options rather than separate biological species. The droid template refers to `appearance/nk3.sat`; it is not proof of the later IG-100 player implementation.

## Later species and variations

**Arkanian and Echani** were introduced in [March 2022 patch notes](https://www.empireinflames.net/?p=1745); their complete reusable packages are not in this 2017 snapshot. **IG-100** and **female Devaronian** appear in the [August 2017 client-release history](https://www.empireinflames.net/?cat=22). Female Devaronian’s player template is in the inspected client archive, but the old server header includes only male Devaronian. These distinctions prevent treating every modern option as covered by the old code.

## Explicit public EiF releases worth using

| Contribution | Evidence / practical use |
|---|---|
| Original species mod | [Creator release](https://modthegalaxy.com/index.php?resources/new-species-for-swgemu.36/); original ZIP collected earlier, with 16 additions including Togruta. Modern port needed. |
| Multipassenger vehicles | [Creator release](https://modthegalaxy.com/index.php?resources/swgemu-core3-multipassenger.74/); public AGPL source and matching TRE collected. Flash-speeder example; not the complete modern vehicle catalog. |
| Better Astromechs | [Creator release](https://modthegalaxy.com/index.php?resources/better-astromechs.35/); NPC paint customization with EiF credit requested. Original ZIP collected earlier. |
| Useful Newsnet Terminals | [Creator release](https://modthegalaxy.com/index.php?resources/useful-newsnet-terminals.20/); informational terminal scripts. Replace EiF endpoints with local project information; original ZIP collected earlier. |
| Development Datapad | [Creator release](https://modthegalaxy.com/index.php?resources/halyns-datapad.41/); newly collected two-file tool. Uses an existing client appearance. Sample menu calls EiF-specific heroic methods that we must replace; staff checks should be added when adapted. |
| Unstable saber effects | [Halyn and Auri release](https://modthegalaxy.com/index.php?resources/unstable-lightsaber-blades.118/); newly collected 54-file ZIP. Creator explicitly offers use with credit. Selective cosmetic integration and testing needed. |

Abi’s Lamp Pack and the already collected Borrie packs retain their individual public release terms; association with a private server does not undo their separate creator releases.

## Other EiF content and missing material

| Content / family | Finding | Source |
|---|---|---|
| Arkanian and Echani | Later playable species, announced March 2022; not in the collected 2017 server snapshot. | [source](https://www.empireinflames.net/?p=1745) |
| IG-100 and female Devaronian | Later player options; female Devaronian client template is in starsider01, but absent from the inspected server race header. IG-100 is distinct from its NK3 droid. | [source](https://www.empireinflames.net/?cat=22) |
| Sith Shrine, Plasma Mining Facility and EiF Axkva Min | Documented encounters; matching complete server implementation not found in the public snapshot. | [source](https://www.empireinflames.net/?p=1467) |
| Pazaak, click collections and seasonal reward systems | Documented content; complete reusable implementation not established. | [source](https://www.empireinflames.net/?p=1467) |
| Holocomm, Kyber systems, configurable weapons and custom animations | Contributor work identified; no complete standalone release verified. | [source](https://www.empireinflames.com/?p=1789) |
| Kuat Drive Yards, Dac City and related planet revisions | Contributions span EiF and Sunrunner. Obtain the exact package and relevant creators’ terms. | [source](https://www.empireinflames.net/?page_id=985) |
| Taanab Harvest and modern Empire Day missions | Current event descriptions and reward paths exist; they are separate from the original public Taanab terrain release. | [source](https://www.empireinflames.net/?p=2261) |
| Airspeeder/jetpack backend and surveillance tools | Later systems documented in 2022; the 2021 passenger demonstration does not supply this whole backend. | [source](https://www.empireinflames.net/?tag=update-notes) |
| Custom lightsaber hilts, BB droids and starship art | Different authors and third-party licenses apply. Model rights and EiF conversion rights must be traced separately. | [source](https://www.empireinflames.net/?p=1597) |

EiF’s [2018 planet release notes](https://www.empireinflames.com/?m=201809) document Chandrila, Coruscant, Kuat and Mon Calamari; the credits distinguish Levarris’s Coruscant/Chandrila work from Sunrunner contributions. Taanab has its own original public creator release. A server partnership is evidence of collaboration, not a transferable blanket grant to all partner assets.

Its [credits](https://www.empireinflames.net/?page_id=985) identify separate artwork authors: AgentOrangeJuice (including V-wing), MTD/X-Wing Alliance Upgrade (YT-2000 and MC80 Liberty), Admiral Tributon (HWK-290 and Clone Wars Y-wing), and BB-unit model authors/converters. The BB-9E original is linked to CC-BY 4.0; the exact EiF conversion still needs its own provenance. No price list or blanket LAN-use exception was found in the inspected official materials.

EiF’s [profession design](https://www.empireinflames.net/?p=714) deliberately changes the original profession structure and crafting. Our pre-CU project can select content without adopting that entire overhaul. An old guide’s statement that JtL is unavailable is outdated: EiF’s [2026 Empire Day description](https://www.empireinflames.net/?p=1542) includes a space escort activity.

## Uprising findings

Uprising identifies Core3 as its base in the [acknowledgements](https://swguprising.com/#acknowledgements). Its [staff page](https://swguprising.com/#staff) names Idewu for engineering and Avix for project direction. The official website advertised an October 2, 2026 launch and the browser showed recent October updates during this audit; no operational test was performed.

The [feature guide](https://swguprising.com/#whats-different) advertised **311 entries across 18 categories**. These are documented behaviors, not 311 separately licensed original mods. Useful candidates for our project are:

| Priority | Reference |
|---:|---|
| 1 | In-game materials board with recipe comparisons and survey waypoints. |
| 2 | Recipe recovery, larger factory runs, component returns and clear ingredient names. |
| 3 | Furnished-house packing, shared storage, vendor customization and full furniture rotation. |
| 4 | Harvesting droids, enhanced pet genetics and configurable medical assistants. |
| 5 | Exar Kun, Axkva Min, Decrepit Droid Factory, Lost Star Destroyer and roaming bosses. |
| 6 | Grey Jedi and Ronin faction development alongside Light/Dark progression. |

The [overview](https://swguprising.com/#features) also describes three-faction planetary conflict and expanded pre-CU encounters. No official Uprising server-source repository or reusable content package was found in the official links and public repository searches checked. Two third-party client helpers surfaced on GitHub, but neither is the server implementation. No new-planet or species release package was identified. Its [terms page](https://swguprising.com/#terms) was a placeholder during the audit and supplies no content reuse grant.

For Uprising, use the documented behavior to write our own systems unless its authors release the relevant source or grant specific permission. The resource/crafting board is the strongest first design reference for this LAN sandbox.

## LAN use, public use and payment

For published EiF code, follow the included licenses; LAN-only access does not replace their conditions. Keep corresponding source available to users as required by the applicable license. For client art whose terms are unresolved, ask for the specific LAN permission now, and a separate public redistribution/hosting permission if the project later opens to the public.

The willingness to pay can be recorded as an offer for an agreed license, porting work or support. It does not establish that payment is required, that an author will sell a license, or that one team can license another contributor’s artwork. Agree on named files, permitted changes, credits, redistribution, scope and any fee before relying on a custom agreement.

Start with Halyn/the EiF team through their [official contact page](https://www.empireinflames.net/?page_id=220); ask them to route any third-party art questions. Uprising’s [staff page](https://swguprising.com/#staff) and official Discord identify the engineering/project contacts. **No messages were sent, terms accepted or payments arranged.**

Useful questions for the creators:

1. Which of the named species packages and client templates may be reused on a private, noncommercial LAN, and which require separate original-artist permission?
2. Is there a newer public species patch or source release compatible with current Core3, including Arkanian, Echani, IG-100 and female Devaronian?
3. Are any selected encounter, vehicle, housing or utility systems offered as standalone releases? Which exact source revision and asset dependencies belong together?
4. What additional terms, attribution and fees, if any, would apply to a later public free-to-play server and redistribution of its custom patch?

## Retained files and validation

[Selected EiF species source reference](<C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Content-catalogue/EiF-Uprising/EiF-2017-species-source-reference.zip>) — source and licenses only; not a complete install bundle.

[Halyn’s Development Datapad](<C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Content-catalogue/EiF-Uprising/halyns_datapad.zip>); [Unstable saber effects](<C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Content-catalogue/EiF-Uprising/unstable_lightsaber_blade.zip>).

[Original starsider01 research copy](<C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Content-catalogue/EiF-Uprising/EiF-starsider01-reference.tre>) — public player-patch download retained for inspection; no blanket reuse grant established.

[File-level source/package evidence](<C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Content-catalogue/EiF-Uprising/eif-source-audit.json>); [Client archive index and creation-table evidence](<C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Content-catalogue/EiF-Uprising/EiF-starsider01-index.json>); [Updated active catalogue](<C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Content-catalogue/SWG-active-content-catalogue.md>).

Validation: 1,100 selected source files inspected for notices; no proprietary/not-for-distribution marker found in that inspected subset. The selected source ZIP and both new creator ZIPs passed archive-integrity checks. All 37 source options have registered player Lua and matching shared-template names in the inspected EiF archive. These checks do not validate appearance dependencies, character selection, gameplay or modern Core3 behavior.

The bulk remote range-index attempt was unsuccessful; no conclusions rely on it. The successful local starsider01 index is the asset evidence used above. The other 22 required archives were not downloaded or inventoried.

## Recommended next work

1. Adapt the public development datapad into an owner-only tool for our own screenplays.
2. Port the original public species package first; use the broader EiF source as a reference and resolve the remaining client-art terms.
3. Build our own resource/recipe board and missing quests using current Core3 and assets already covered by creator releases.
4. Evaluate public multipassenger support separately from later private vehicles, and test each cosmetic pack in a copied client before deployment.

Nothing in this report authorizes or performs an installation, public launch, external message or payment.
