# Shared SWG feature register

For the owner, Claude and ChatGPT. Updated 13 October 2026. This is the central list of **recorded proposals and researched candidates**, not authorization to implement every row. Current assignments/lock stay in [SWG-handoff.md](SWG-handoff.md); phases stay in [SWG-roadmap.md](SWG-roadmap.md).

## Reading the estimates

**Maturity:** idea → researched → scoped → implemented → tested (test galaxy) → live. A port may be implemented upstream but only researched here. “Tested” means the stated narrow check, not complete coverage. **Difficulty:** Low = configuration or small script with known APIs; Medium = several connected scripts/UI/data changes; High = client/server work, complex state/persistence or substantial port; Very high = poorly understood client internals, animation/terrain or a large gameplay system. These are preliminary engineering estimates, not promises or calendar schedules. Rights uncertainty is a separate gate and can block even easy code.

**Owners:** Claude engineers `/opt/swg`; ChatGPT researches, reviews and writes outside-server tooling. Both review/test within the shared rules. All live promotions need cross-review and explicit owner OK. LAN-first remains the target.

## Foundation, tools and testing

| ID | Feature / what it is for | Thought-out level / current usability | Difficulty / main remaining work |
|---|---|---|---|
| F01 | Launch/status/log tools: know when the galaxy is ready | Live tools recorded; health checks available | Low; ongoing maintenance |
| F02 | Verified backups and restore rehearsal: recover world/data/code | Implemented; restore rehearsal recorded passed | Medium; rerun after risky backup changes |
| F03 | Isolated dev worktree and disposable test galaxy | Built and exercised; test galaxy currently available | Medium; preserve isolation and build provenance |
| F04 | Upstream check/rebase/rebuild routine | Implemented tools; private git | Medium; resolve conflicts/test changes per update |
| F05 | Warning triage and asset dependency diagnostics | Warning inventory exists; not all warnings resolved | Medium; identify used assets first; JTL warnings need flight testing |
| F06 | Full regression runner and expected outcomes (C3/C5) | Scoped command protocol/checklist; runner pending | Medium–High; assertions and missing body abilities |
| F07 | Five squad test harness (C7) | Implemented; latest one round 30/35 checks in 226 s | Medium; medical prerequisites, safe harvest routes, terminal map, stricter evidence |
| F08 | Fresh non-staff acceptance tests | Several test-only checks passed | Medium; complete loot/craft/trade/housing/tutorial and cross-planet coverage |
| F09 | Real-client two-window/cursor/graphics acceptance | Windows configured historically; capture works; final acceptance open | Low–Medium; owner at PC; exact-window input targeting unresolved |
| F10 | Documentation library and profession reference | Written; sources/era caveats and C7 corrections | Medium; exact loaded skill data/formulas still require extraction and tests |
| F11 | Universal Modder reference and tool readiness | 12 skills/10 groups inventoried; 76 parser entries exported | Medium; external RE integrations and SWG converter not supplied automatically |
| F12 | PDF project record/update | Existing PDF file present; pending later research snapshot deferred | Low–Medium; regenerate only from saved verified records, inspect rendered output |
| F13 | Retention/performance management | Bot report rotation implemented; backup deletion only a proposal | Low–Medium; owner decision before deleting backups/builds; CPU/route-cost measurements |

## Companions, movement and the agent

| ID | Feature / what it is for | Thought-out level / current usability | Difficulty / main remaining work |
|---|---|---|---|
| F14 | Mercenary broker: companions for a small LAN group | Hire/follow/dismiss live; combat assist inconclusive | Medium; prove assist, persistence/logout cleanup and cap behavior |
| F15 | Server `/leash`: assist stuck client follow | Implemented/test-only; latest nine social checks passed including labels and stationary behavior | Medium; `5aadc8b9` re-review, transition/unreachable-route tests, approved promotion, human-client C6 |
| F16 | Proper client follow/pathfinding | Later option; symptoms observed, no client design/prototype | Very high; client steering/input investigation, path data/route integration, version compatibility |
| F17 | Agent navmesh/height/indoor movement | Implemented/test-only; Esk five checks pass | High overall; transition/race/path limits and broader routes; live review/promotion |
| F18 | Agent HAM/combat/death/clone observations/reflex | Implemented; weak combat and cloning tested on test galaxy | Medium–High; survival decisions, wounds/secondary stats, reliable receipts |
| F19 | Inventory/radial/SUI/vehicle interactions | Mostly implemented/test-only; deed/call historically passed | Medium; mounting, device lifecycle and live wrappers still need verification |
| F20 | Mission decode/list/accept | Implemented; cache fixes in new dev commit | Medium; actual terminal mapping and complete objective/payout tests |
| F21 | Survey/sample/forage/harvest automation | Survey/sample recorded passed; harvest scenario blocked before kill | Medium; quantities, safe guard, rights/resource type and persistence |
| F22 | Crafting/experimentation agent protocol | Planned; session not implemented end-to-end | High; schematic slots, resources, assembly, experimentation, final receipt and relog |
| F23 | Secure trade agent protocol | Planned; grouping already tested separately | High; both-party state/accept/cancel, inventory and credit consistency |
| F24 | Private tells/chat protocol | Missing body capability; BLOCKED in C7 | Medium; implement direct-chat messages and delivery/failure observations |
| F25 | Heal/flee/hold/support reflexes | Partial fight reflex only; medical test now honest about refusal | Medium–High; safe priorities, medicine/range/cooldowns, defeat recovery |
| F26 | Dungeon-testing agent/playbooks | Architecture scoped; prerequisites incomplete | High; survive/loot/craft/navigation, bounded resumable runs and route knowledge |
| F27 | Ambient adventurers v1 | Design: ten NPCs with waypoints/idle/chatter, off switch | Medium; AI behaviors, density, resource limits and NPC ownership restrictions |
| F28 | Ambient adventurers v2 | Idea: hunting, apparent groups and persistence | High; behavior/state transitions and performance |
| F29 | Optional local personality model | Idea; deterministic chatter first, local/rate-limited/off by default | High; local runtime, memory, action constraints and scheduling; no model service configured |
| F30 | Optional Discord status/bridge | Research references only; not requested for deployment | Medium; external service/credentials, rate limits, explicit outbound approval |

## Server gameplay and convenience

| ID | Feature / what it is for | Thought-out level / current usability | Difficulty / main remaining work |
|---|---|---|---|
| F31 | Rotating world bosses and Rhea's trail hints | Built/test-only; Rhea talks, advertises trails; boss payout still unverified | Medium; real player damage-credit reward, source credits, reviewed promotion |
| F32 | POI waypoint helpers | Published scripts identified, not ported | Low–Medium; current APIs/coordinates and enabled-world checks |
| F33 | Vendor/bazaar search waypoints | Bellum source candidate | Medium; current search UI/data and waypoint lifecycle |
| F34 | House pack-up service | Bellum candidate | High; ownership, stored items, vendors/pets and recovery behavior |
| F35 | Character name-change service | Bellum candidate | Medium–High; uniqueness, references, social/mail/vendor implications |
| F36 | Additional Jedi abilities | Return of the Force candidates, conditional on Jedi plan | Medium–High; balance, certifications/commands, effects/permissions; no blanket import |
| F37 | Owner developer datapad | Public datapad adaptation idea | Medium; owner permissions, safe menus and screenplay spawn/reset controls |
| F38 | Resource/recipe board terminal | Scoped idea: current spawns/stats/survey waypoints | Medium; live data retrieval, refresh, filters and recipe resource matching |
| F39 | Optional self-hosted Galaxy Harvester | Public tracker/exporter references | Medium–High; schema, exporter, hosting and data freshness; new service needs owner OK |
| F40 | Original three-step quest | Template available; courier/combat chain proposed | Low–Medium; objectives, state/relog/reset, rewards and dialogue |
| F41 | Newsnet terminal | Public script collected, not installed | Medium; replace remote URLs, lua-socket/network behavior; local content option |
| F42 | Multiple vehicle passengers | Public EiF code/assets collected; not integrated | High; current C++ port, state/messages, matching client, mount/group lifecycle |
| F43 | Buff/resource shortcut terminals and solo tuning | Upstream candidates/owner aids; not current blanket gameplay mandate | Low–Medium; owner later choice; preserve normal rules unless explicitly requested |
| F44 | Events/dungeons/Gray Jedi trials/loot ports | Flurry/other published source research, not wholesale usable | Medium–Very high by module; old AI API conversion, rights/dependencies and encounter testing |
| F45 | Account/web portal | Future multi-user candidate only | High; service, authentication, account security; LAN currently does not need it |

## Planets, species, client assets and restoration

| ID | Feature / what it is for | Thought-out level / current usability | Difficulty / main remaining work |
|---|---|---|---|
| F46 | Hoth first playable custom planet | Most scoped planet: MTG terrain/snapshot, Bellum server/tools, proposed bases/caves | High; dependency closure, rights, CRC/travel/map/STF, spawns/resources, return trip/mission checks |
| F47 | Kashyyyk and Mustafar backports | Assets/partial scripts identified; complete expansion campaigns not established | Very high for full campaigns; High for bounded zones; mechanics and quest adaptation |
| F48 | Taanab and Mandalore | Public terrain and substantial screenplay candidates | High; modern AI/API port and asset chain/travel/resources |
| F49 | Other researched worlds/stations | Candidates listed individually below; not approved or installed | High–Very high; layout/assets/permissions, travel and playable objectives |
| F50 | Public original species package, then Zeltron | Packages collected, client terms tracked | High; creation/UI/equipment/animation/bounds and server race mapping |
| F51 | EiF species/vehicle art | Code research available; client contribution permissions unresolved | High plus rights gate; no import until agreement/release terms established |
| F52 | Decoration/light/wall/building packs | Several public packages inspected | Low–High per pack; acquisition schematics/deeds, dependencies, performance and crash exclusions |
| F53 | Modern texture/graphics fixes | Owner settings started; native asset pipeline not accepted yet | Medium–High; renderer compatibility, original-file fallback and multibox performance |
| F54 | Static original prop/converter (cargo crate first) | Format inventory v1; community tooling leads; no SWG export proven | High; MSH/SHT/DDS/APT reader/writer or existing exporter validation, round trip, client proof |
| F55 | Wearable/skinned-species pipeline | Later stage after static prop | Very high; MGN/SKT/ANS mapping, rig/animation/clothing compatibility |
| F56 | Local ComfyUI concepts/textures | Models researched, no local generation benchmark here | Medium; compatible install/model licenses/VRAM, repeatable workflow |
| F57 | Optional local/paid image-to-3D | TripoSR/Hunyuan/fal candidates; no SWG-ready asset generated here | Medium for GLB, High for SWG asset; per-batch fal consent; cleanup/scale/LOD/UVs |
| F58 | Morag/Endor original encounter | Owned-client model evidence recorded; gameplay would be original | Medium; current template verification, spawns/dialogue/rewards; no unavailable original quest source assumed |
| F59 | Alternate player-city building styles | Dormant owned-client paths inventoried | Medium; verify aliases, templates/deeds, placement, medical/civic services |
| F60 | Dormant BE additives/dyes/resource container types | Inventory candidates, not missing-feature proof | Medium–High; distinguish aliases from missing logic; recipes/function and permissions |
| F61 | Dormant JTL components/reactors | Inventory candidates | High; actual ship slot/stats/crafting/RE behavior and flight acceptance |
| F62 | Otoh Gunga/test terrains | Legacy terrain evidence, no complete destination | Very high; underwater/world design, assets, traversal; research only |
| F63 | Official planned/cancelled content restoration | New owner-authorized research: interviews/design history/owned assets/public backports | Unknown–Very high; evidence classification before implementation estimate |
| F64 | Mantis or another bug tracker | Discussed as optional; Markdown reports already work | Low–Medium; extra service not necessary for LAN; only add if owner wants it |

## Priorities and decision gates

The smallest useful next engineering steps are: re-review `5aadc8b9`; get doctor prerequisites and safe fresh-kill harvesting right; map a mission terminal; finish core crafting/trade observations. These unblock reliable testing. Hoth and an original static prop are the most developed content directions. Full client follow, full expansion campaigns and skinned-species tooling remain large projects.

Pending approvals are recorded per action, not blanket gates on research: live deploy/restart, paid fal generation, new external service, outbound posts and unresolved creator permissions. All content keeps central credits. Excluded sources/content remain outside the active plan.

## Catalogue-wide candidates

The following appendix is generated from all 102 entries in the existing **active** content catalogue. It includes researched content and tools that were never selected for implementation. Names/rights summaries inherit that catalogue's 13 October research and are **not newly reverified**. Each has an initial difficulty/maturity label; exact design and estimates need a selected release and dependency audit. Detailed package/provenance information remains in [the active catalogue](Content-catalogue/SWG-active-content-catalogue.md).

| Candidate ID | Name | Purpose/category | Maturity | Preliminary difficulty / gate |
|---|---|---|---|---|
| active-001 | Taanab | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-002 | Hoth | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-003 | Dromund Kaas | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-004 | Mandalore | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-005 | Chandrila | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-006 | Coruscant | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-007 | Jakku | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-008 | Moraband / Korriban | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-009 | Nal Hutta | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-010 | Kashyyyk | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-011 | Mustafar | Planet | Researched; not runtime validated | High–Very high; dependencies/tests required |
| active-012 | Dagobah | Planet | Researched; not runtime validated | High–Very high; rights/release unresolved |
| active-013 | Mon Calamari / Dac | Planet | Researched; not runtime validated | High–Very high; rights/release unresolved |
| active-014 | Kuat | Planet | Researched; not runtime validated | High–Very high; rights/release unresolved |
| active-015 | Ord Mantell | Planet | Researched; not runtime validated | High–Very high; rights/release unresolved |
| active-016 | Bespin | Planet | Researched; not runtime validated | High–Very high; rights/release unresolved |
| active-017 | Kessel | Planet | Researched; not runtime validated | High–Very high; rights/release unresolved |
| active-018 | Zeltros | Planet | Researched; not runtime validated | High–Very high; license conditions apply |
| active-019 | Tansarii Point Station | Station | Researched; not runtime validated | High–Very high; rights/release unresolved |
| active-020 | Nova Orion Station | Station | Researched; not runtime validated | High–Very high; rights/release unresolved |
| active-021 | Centerpoint Station | Station | Researched; not runtime validated | High–Very high; rights/release unresolved |
| active-022 | Otoh Gunga | Candidate world | Researched; not runtime validated | High–Very high; legacy/unfinished |
| active-023 | Geonosis | Candidate world | Researched; not runtime validated | High–Very high; legacy/unfinished |
| active-024 | Umbra and developer terrains | Legacy/test world | Researched; not runtime validated | High–Very high; legacy/unfinished |
| active-025 | Borrie's Torch Pack | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-026 | Borrie's Kitchen Pack | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-027 | Borrie's Dark Interiors | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-028 | Borrie's Naboo Structure Pack | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-029 | Borrie's Light Megapack | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-030 | Borrie's Wall Pack Vol. 1 | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-031 | Abi's Lamp Pack | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-032 | SWGEmu Core3 Multipassenger | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-033 | Useful Newsnet Terminals | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-034 | Better Astromechs | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-035 | Borrie's Wearable Rank Plates | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-036 | Named Saber Crystals | Pack or tool | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-037 | Classic BARC Assets | Pack or tool | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-038 | Post-14.1 House Assets | Pack or tool | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-039 | Borrie's /tool and Jawa object syncing | Pack or tool | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-040 | Sytner IFF Editor (SIE) | Pack or tool | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-041 | SWG Galaxy Map Editor | Pack or tool | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-042 | SWG Forge | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-043 | SWG Mobile Template Viewer | Tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-044 | Housing | MTG family | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-045 | Schematics | MTG family | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-046 | Inventory items / decor / armor / vehicles | MTG family | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-047 | Weapons | MTG family | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-048 | NPC and creature objects | MTG family | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-049 | Ships | MTG family | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-050 | The Beginning | Quest example | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-051 | Sunrunner original Lua quests / encounters | Restricted or unverified family | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-052 | Sunrunner original artwork / planet revisions | Restricted or unverified family | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-053 | EiF custom ship models and converted third-party artwork | Restricted or unverified family | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-054 | Hutt | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-055 | Nautolan | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-056 | Togruta | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-057 | Chiss | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-058 | Devaronian | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-059 | Gran | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-060 | Ishi Tib | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-061 | Nightsister | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-062 | Nikto | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-063 | Quarren | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-064 | Singing Mountain Clan Witch | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-065 | Weequay | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-066 | Aqualish | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-067 | Bith | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-068 | Gotal | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-069 | Talz | Species | Researched; not runtime validated | High; dependencies/tests required |
| active-070 | Abyssin | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-071 | Arcona | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-072 | Cerean | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-073 | Duros | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-074 | Gungan | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-075 | Iktotchi | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-076 | Jenet | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-077 | Kel Dor | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-078 | Kubaz | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-079 | Sanyassan | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-080 | Chadra-Fan | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-081 | Droid (NK3 label in source; not verified IG-100) | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-082 | Dug | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-083 | Ewok | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-084 | Feeorin | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-085 | Geonosian | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-086 | Ortolan | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-087 | Togorian | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-088 | Toydarian | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-089 | Mirialan | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-090 | Zeltron | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-091 | Arkanian | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-092 | Echani | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-093 | IG-100 Droid | Species | Researched; not runtime validated | High; rights/release unresolved |
| active-094 | Halyn's Development Datapad | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-095 | Unstable Lightsaber Blades | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-096 | EiF public server source snapshot | Pack or tool | Researched; not runtime validated | Medium; assess selected package; dependencies/tests required |
| active-097 | Uprising: Resource search and crafting comparisons | Design reference | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-098 | Uprising: Crafting and production conveniences | Design reference | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-099 | Uprising: Housing and vendor conveniences | Design reference | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-100 | Uprising: Companions and service support | Design reference | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-101 | Uprising: Encounters and rewards | Design reference | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |
| active-102 | Uprising: Jedi and faction progression | Design reference | Researched; not runtime validated | Medium; assess selected package; rights/release unresolved |

## New developer-history candidates (F65–F81)

Evidence, dates, access caveats and feasibility: [official plans/cut content/backport research](Documentation-support/SWG-official-plans-cut-content-and-backports.md). These are researched design references; none was implemented here.

| ID | Idea / what it is for | How thought out | Preliminary difficulty |
|---|---|---|---|
| F65 | Player contracts: commission courier/other work | Developer describes an intended system; local scope suggestion only | Medium–High |
| F66 | Skill web/hidden combinations: broader hybrid builds | Historical abandoned design; no local design | Very high |
| F67 | Miner profession: specialized extraction gameplay | Named cut profession; details absent | High/unknown |
| F68 | Varied per-character Jedi unlock: exploration across playstyles | Developer describes a specified but unshipped plan | High |
| F69 | Hardcore Jedi survival mode: escalating pursuit | Early rejected idea, no local design | Very high |
| F70 | Crafter usage XP: reward products people actually use | Developer describes intended economy loop and scalability failure | High |
| F71 | Restricted recipe knowledge: specialization | Discussed idea, not implemented; poor LAN default | Medium–High |
| F72 | Composers/scores/royalties: player-made music economy | Historical spec, legal/technical barriers; no local prototype | Very high |
| F73 | Theater/scripts: rewarded performance events | Historical dropped profession; small local text version suggested | Medium–High |
| F74 | Writer/HoloNet channels: articles/readership | Historical dropped profession; local terminal is a smaller slice | Medium–High |
| F75 | Procedural dances/expression: flexible animation | Historical ambition, replaced by loops | Very high |
| F76 | Conversation circles: social positioning/gaze | Historical discussed behavior; no local design | High |
| F77 | Dynamic encounter questlets: changing wilderness activities | Historical attempted system; original bounded encounter proposed | Medium–High |
| F78 | Fear-aware animal routes/stampedes: richer ecology | Developer describes lost/degraded AI direction | High |
| F79 | Earlier visuals: recover lighting/detail intent | Developer testimony, no verified reusable pack | High/unknown |
| F80 | River-generation tooling: better terrain creation | Developer states it was never implemented | Very high |
| F81 | Player-decorated quest interiors: authored adventures | Later-era producer wish list, not a pre-CU implementation | High–Very high |

## KOTOR, original inspiration and open assets (F82–F86)

Full source/rights/tool research: [KOTOR → SWG feasibility](Documentation-support/KOTOR-to-SWG-and-open-assets-feasibility.md). Research complete; no extraction or conversion tested.

| ID | Feature / purpose | How thought out | Preliminary difficulty / gate |
|---|---|---|---|
| F82 | Stock KOTOR I/II props/areas in SWG | Existing readers/importers and SWG exporter identified; no validated pipeline | Medium–Very high by asset; cross-game rights unresolved |
| F83 | KOTOR modder-created assets in SWG | [56-entry author/permission audit](Documentation-support/KOTOR-mod-reuse-audit.md) with additional-author supplement; no specific import cleared | Medium–Very high; author and underlying-asset terms both apply |
| F84 | Original KOTOR-inspired content | Several small briefs: archive terminal, expedition camp, mining room, droid station, companion story | Medium for prop/quest; High for room; new original art/writing |
| F85 | CC0 sci-fi kit/material adaptation | Creator-verified Quaternius, Kenney and Poly Haven shortlist | Medium for static prop; verify exact pack and SWG export |
| F86 | Blender import/export pipeline validation | KotorBlender + PyKotor and NoStyleGuy SWG add-on identified; compatible-version experiment scoped | Medium–High; try existing exporter before writing converter; rig/animation limitations |

## Owner's SWG x SW5E book and pharmacopoeia: new professions, mats, consumables, farming (F87–F90)

Source and real-SWG mapping: [owner's book guide](Content-catalogue/owner-SWG-SW5E/README.md). The owner wants the book used as a reference only (14 Oct 2026), and real pre-CU SWG wins where the two differ; the SW5E rules are not implemented. Mapped against the client's own skill, resource and schematic tables; nothing built yet.

| ID | Feature / purpose | How thought out | Preliminary difficulty / gate |
|---|---|---|---|
| F87 | Five new professions (Botanist, Pharmacist, Toxicologist, Cyberneticist, Archaeologist) in real SWG shape | Book lines and entries mapped onto real skill boxes and XP types. Entries at IV like every real elite (owner, 14 Oct). Open questions: Botanist needs a planting mechanic; avoid making Doctor/Combat Medic redundant | High per profession (client skills.iff and strings in a shared archive, trainer, schematics); Medium for a Novice-box feasibility test. Cyberneticist needs new art (rights gate) |
| F88 | New mats: biomass, plant resin, filter peat, clay, plasma and sulfur feedstock | 50 book mats for the 10 live planets checked against resource_tree.iff; most already exist under real names, the rest are salvage or these new classes | Medium–High: client resource tree plus Core3 resource spawner; only worth it with schematics that use them (F87) |
| F89 | Consumables from the book and the owner's pharmacopoeia | Pharmacopoeia (85 substances): 14 already exist in SWG, 17 new Smuggler spices, 6 Combat Medic poisons, 22 for the new Pharmacist/Toxicologist/Botanist, and 26 Force or story items that aren't player-crafted; effects to be designed in SWG style later. Core book: only A10 Feed batch, and pre-CU has no pet feeding; 16 book items compared with real schematics (5 exist in kind, 5 have a close equivalent, 6 are new). The armory (a chat artifact) has not been readable yet | Low–Medium per item that reuses a real object type; new mechanics are higher |
| F90 | Farming / agriculture (owner, 14 Oct: research picked up; implementation proposed) | Linked to Botanist (F87), flora mats (F88) and pharmacopoeia. [Reference/rights research](Documentation-support/farming-system-UM-feasibility.md): MIT Minecraft shortlist, Skyrim visible growth, ARK processing; proposed owned planter with persistent stages/water/harvest. Exact Core3 integration and balance unresolved | Medium–high narrow prototype; high full crafting/art/persistence; implementation untested and not started |

## Engine extension, clean-room NGE backports and new endgame (F91–F94)

Owner ideas, 14 Oct 2026. Proposals only; nothing built.

| ID | Feature / purpose | How thought out | Preliminary difficulty / gate |
|---|---|---|---|
| F91 | Server-side "script extender": more Core3 Lua hooks and functions, so content (quests, events, Storyteller tools, new professions) is written in Lua without C++ rebuilds | Owner: "a script extender like bethesda games". Most SWG gameplay runs on the server, and Core3 is open source and already Lua-scripted, so this gives most of what SKSE gives Bethesda modders. Candidates: event hooks (kill, loot, craft, harvest, enter region, skill granted), custom SUI windows, buff and spawn control from screenplays | Medium per hook (C++ binding + Lua API + tests); our own code in our tree |
| F92 | Client-side extender: our own DLL hooked into the SWG client exe (what SKSE literally is) | Only for things the exe hard-codes (new packet types, new UI behaviour, rendering or draw-distance limits); UI layouts, datatables, strings and art are already moddable as archive data | Very high: reverse-engineering a 2005 exe without symbols; a disassembler (e.g. Ghidra) is a new install needing the owner's OK; crash and antivirus risk; feasibility study only when a feature needs it |
| F93 | Clean-room NGE backports from the owner's own disc (SWG Complete Online Adventures, Oct 2006: SOE patches 15–33 and sku1–3, extracted read-only to `/opt/swg/disc-extracted/SWG-group/`, hashed) | Owner: "make our own without their code akin to what swgemu did". Feature specs come from the disc's data (quest, collection, buff, expertise and beast datatables; object templates; strings) plus public sources (SOE patch notes, dev diaries, guides, videos), written in our own words; implementation in Core3 from the spec; leaked server code is never read (AGENTS.md rule 1). Object backports start with Fable's staged batches (`outputs/Fable-backport/`). Found 14 Oct: the client could only name MTG objects once the merged object CRC table (in `local_planets.tre`) was added | Per feature: Medium (decor, vehicles) to Very high (systems such as collections, beast mastery); unpublished numbers (loot tables, formulas) are our own design |
| F94 | Zonama Sekot as an endgame rotating raid (owner idea, 14 Oct) | The living planet jumps through hyperspace, so a rotation is in-lore; it fits the NJO-Legacy direction. Proposal: a raid-sized zone (a small outdoor terrain from Fable's .trn tools, or a large interior like Core3's dungeon zones) rather than a full planet; the entrance and active boss set rotate on a schedule through a screenplay plus our world-boss framework. Sekot-side content can reuse stock art (Ferroan humanoids, recoloured creatures as Sekotan fauna, Kashyyyk-scale trees); there are no Yuuzhan Vong models in any SWG archive (stock, MTG or the owner's disc), so Vong content needs new art (waits on F86). Pre-CU has no instance lockouts: entry rules and timers are scripted | High (zone, encounter scripting, rotation); Very high with Vong art; design brief first |

## Owner-requested saber appearances (14 Oct)

| ID | Feature / purpose | How thought out | Preliminary difficulty / gate |
|---|---|---|---|
| F95 | Darksaber hilt and black blade with white edge | [Asset/format research](Documentation-support/darksaber-ghostfire-feasibility.md), original CC BY model candidate; no imports. Local LSB/shader dependencies observed, rendering behavior unproven | High for functional flat blade, ignition and trails; creator notification/rights and client proof gates |
| F96 | Ghostfire saber with opalescent trails | Same report: dim/translucent blade and pastel afterimage art proposed; CC0 VFX sources found; exact Legends sourcing open, opalescence is owner art direction | High for independent trail material; true iridescence/multiple afterimages uncertain; no stat changes proposed |

## Creature Handler combat direction (owner, 14 Oct)

| ID | Feature / purpose | How thought out | Preliminary difficulty / gate |
|---|---|---|---|
| F97 | Top-tier CH across solo PvE, group PvE and PvP | [Research and benchmark plan](Documentation-support/creature-handler-top-tier-plan.md); local skill costs verified; AI/control, pet roles, sustain and Master-gated balance proposed; no baseline combat measurements | Medium–high for narrow balance changes; high for new AI/abilities/progression. Tames discussion pending; no implementation approved |

## Maintenance

When a feature changes: retain its ID; update maturity, evidence/test link and dependency; split a large row into named subfeatures rather than silently treating it as done. Claude should challenge the preliminary difficulty estimates after reading the actual code. This register aggregates the roadmap, handoff, format inventory, gameplay reports, asset note and active catalogue; public historical feature research is a separate evidence section as it lands.



## Player reporting and mixed-experience QA (owner, 14 Oct)

| ID | Feature / purpose | How thought out | Preliminary difficulty / gate |
|---|---|---|---|
| F98 | In-game problem report -> durable local queue -> agent triage -> Discord tracking; usable by new players while agents are offline | [Scoped source-backed design](Documentation-support/player-bug-inbox-design.md); native ticket route is Mantis-based, categories disabled and receipt commented out. C27 proposed; no implementation/deployment | Medium; native UI/receipt proof, authenticated metadata, concurrent durable spool outside reset path, claim/delivery tracking and Discord setup |
| F99 | Developer friends + experienced/new-player QA onboarding in private Discord | [Server blueprint](Documentation-support/discord-dev-qa-setup.md); add getting-started/help, scoped Developer/Tester roles, test plans/forums; remote testers confirmed | Low-Medium for Discord setup; separate remote game access/persistence proof. No server, accounts or invites created |

## Fleet observability (owner, 14 Oct)

| ID | Feature / purpose | How thought out | Preliminary difficulty / gate |
|---|---|---|---|
| F100 | Browser planet maps with moving squad/fleet markers; optional actual squad video, detail/trails/incidents linked to C27 | [Scoped source-backed monitor design](Documentation-support/bot-fleet-browser-monitor.md), TortoiseBots snapshot reference. Current status is five-minute text, activity lacks positions and bots do not render video. C28; not implemented | Medium map/telemetry/replay; High video/observer tracking; fleet performance and map calibration need measurement. Passive producer, epoch/stale handling, coordinate spaces, rights and remote-access gates |
