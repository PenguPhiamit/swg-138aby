# C21 — server resource and implementation census

Owner request, 14 October 2026: quantify what resources we have, what Wookieepedia covers, and everything we can implement. **Checkpoint 1 complete; further batches remain open.** ChatGPT owns this task; GPT-6.1 Sol, Medium. May span usage resets; save a checkpoint after each bounded research session rather than treating a reset as completion.

## Intended deliverables

1. Count and catalogue local usable resources: client/server content, assets, templates, tools, imported community packages and licensed source material. Include planets, species, creatures/tames, equipment/weapons, vehicles/ships, structures, professions, crafting resources/consumables, encounters and systems. Separate unique objects from variants, duplicate archive copies and references; record a reproducible counting method.
2. Compare against Wookieepedia Legends coverage using cited pages and explicit category boundaries. Record source access/date and coverage gaps. Write original descriptions. A wiki entry establishes lore, not available art or import permission.
3. Build a shared implementation matrix: already working, present but untested, repair/adaptation/backport candidate, original replacement needed, rights hold, excluded. For each candidate record dependencies, available/missing assets and behavior, licence/provenance, concept maturity, effort estimate with uncertainty, and a concrete validation route.
4. Summarize counts by category and readiness, then prioritize feasible vertical slices for owner/Claude discussion. Link existing feature register/catalogues rather than duplicating conflicting plans.

## Scope and checkpoints

- Begin with existing catalogues, download manifests, feature register, client-data probes and handoff reports; preserve closed KOTOR census boundaries and all excluded-source rules.
- Define finite category batches and record totals within their audited scope. Do not claim to enumerate all of Star Wars or every hypothetical implementation.
- Each research pass keeps the existing approximately 30-minute/20%-remaining-usage budget. The owner's request anticipates a usage reset; keep resumable inventory/state and list unfinished batches. Respect any further-pass requirement in AGENTS.md.
- Inventory/research only. Downloads, creator contact/payment, game changes and deployments retain their existing consent/provenance gates.

## Checkpoint

- 2026-10-14 06:13 ChatGPT: task recorded; no census, external research, downloads or imports performed yet.

## Checkpoint 1 - saved local inventory baseline (14 October 2026)

**Boundary:** recompute counts from six existing JSON manifests and establish the next finite batches. No direct server inspection, new web research, downloads, imports, bot commands or game changes. Claude retains the server lock. These are historical inventory counts, not today's installed/usable totals. The current C21 pass stops here.

Reproduce from the project root with `python outputs/tools/research/resource_census.py`. The [machine-readable baseline](server-resource-census-baseline.json) records each input path and SHA-256. The script checks manifest consistency and emits deterministic category totals. It reads saved JSON rather than executing community code. Input hashes identify the evidence inspected; they do not renew the original ZIP or repository integrity checks.

### Counting units and results

| Audited scope | Count | Meaning and limit |
|---|---:|---|
| Active community catalogue | 102 rows | Discovery records; some are families, references or tools rather than assets |
| Named ground-world candidates | 18 | Additional catalogue worlds, not the stock ten; not 18 playable zones |
| Station candidates | 3 | Separate from ground worlds |
| Other world records | 3 | Two candidate worlds and one legacy/test world; do not fold into the 18 |
| Additional species candidates | 40 | Labels/implementations, not verified regular playable species; faction/human variants require classification |
| Catalogue zones with local terrain + snapshot evidence | 11 | Exact zone matches; filenames alone do not prove dependency closure or playability |
| MTG Lua source files | 16,734 | File count at source revision `54deb619e83c2c5e353f6a825a829d56201704f0` |
| Distinct registered MTG object paths | 12,556 | Exact path strings from the Lua manifest's `templates`; variants and shared definitions remain separate |
| MTG archive entry records | 209,201 | Includes repeat archive copies; not a unique-asset total |
| Indexed terrain / snapshot / player-object paths | 64 / 29 / 41 | Distinct paths within the saved summary; includes test terrain, space and subzones |
| Dormant client-object paths | 13,627 | Older client/server comparison: 13,496 MTG + 131 SOE-client-origin records |
| Creator-package records | 13 | 13,175 member records, 20,922,851 ZIP bytes; members are not distinct gameplay objects |
| Inherited C14 lore destination records | 24 | 23 labelled Legends, one canon exception; search-extract evidence, full-page audit outstanding |

The dormant scan compared 29,342 client object paths with 29,180 server templates. Those sets have different naming/shared-template conventions; subtraction of the two totals is invalid. The dormant list itself supplies the 13,627 count. Later backports have changed dev, so this historical list cannot measure today's remaining work.

The 11 local-evidence catalogue zones are `chandrila`, `coruscant`, `hoth`, `hutta`, `jakku`, `kaas`, `kashyyyk`, `mandalore`, `moraband`, `mustafar`, `taanab`. All 11 have matching zone records in C14, but Jakku is explicitly a canon exception. Thus inherited Legends-labelled destination coverage is **10/11 within this local catalogue subset**. This is a mapping of existing records, not a new verification of Wookieepedia pages or an estimate of the whole wiki's coverage. See [C14 evidence and access caveats](planets-lore-and-coordinates.md) and [its JSON](planets-coordinates.json).

### Unique registered paths by technical category

| Prefix | Paths |
|---|---:|
| object/tangible | 6,217 |
| object/mobile | 2,416 |
| object/draft_schematic | 1,533 |
| object/building | 823 |
| object/static | 601 |
| object/intangible | 346 |
| object/ship | 316 |
| object/weapon | 301 |
| object/dungeon | 1 |
| object/installation | 1 |
| object/soundobject | 1 |
| **Total** | **12,556** |

These are mutually exclusive prefixes within this one manifest. Tangibles include equipment, food, furniture, vehicles and quest objects; mobiles include creatures and NPC variants. A schematic does not prove that crafting works, a ship path does not prove JTL, and a pet path does not prove tameability. Later batches must split these prefixes and map related files to an actual implementation. No counts across the active catalogue, MTG registrations and dormant scan are additive.

### Rights and readiness baseline

The active catalogue contains 47 rows labelled published for server use, three published for an identified purpose, one published with explicit conditions, 21 with published server code but unresolved client-art reuse, ten requiring creator permission, eight with release/permission unverified, three later EiF implementations without a verified complete package, six reference-only rows and three development/legacy rows. These sum to 102. The JSON contains the full labels; the short P/U codes alone conceal different decisions. **No blanket import clearance follows from any total.**

All 102 old catalogue rows have `runtime_validated: false`. That is a historical field, not evidence that today's Hoth or other narrow checks failed: newer handoff/game reports supersede it. Runtime maturity must be joined to dated reports per candidate, with separate test-galaxy and live states. No current readiness distribution can honestly be computed yet.

The [C11 audit](../Content-catalogue/archive-record-review.md) records seven pinned checkouts. A6 is an excluded-source hold; A4 has component-specific licences, and D1's donor audit remains open. Do not count those as seven reusable packs. The historical catalogue and excluded sources stay outside the active import pool. Previously downloaded original packs must be checked individually against the owner's exclusions and contributor terms; possession does not clear a pack. The KOTOR census stays closed at 56 releases and is not expanded by C21.

### Initial implementation shortlist - scoped estimates, not authorization

These five rows anchor the eventual matrix to existing plans. They do not enumerate every asset. Effort uses the feature register's qualitative scale, with low confidence until dependencies and acceptance criteria are inspected.

| Candidate / existing plan | Maturity and readiness | Assets, dependencies and rights | Effort / concrete validation |
|---|---|---|---|
| Finish Hoth acceptance, F46 / C12 and Hoth port log | Adaptation already in dev/test according to handoff; complete real-client acceptance outstanding | MTG terrain/snapshot and Bellum scripts recorded; load order, shader closure, creature balance and UI remain acceptance gates. Code notices and client-art provenance separate | Medium-High remaining, uncertain; normal-character round trip, terrain rendering, caves, spawns, quest/loot/resource receipts and relog |
| First regular additional species, roadmap Phase 4 | Published package exists; present but untested in this census | Original species ZIP retained; trace exact selected model's grant and dependencies. Race enum, creation data/UI, skills, appearance and wearables needed; no hybrid species | High, uncertain; create both supported genders, equip/animate, die/clone and relog in real client |
| One original cargo crate, F85-F86 / roadmap Phase 5 | Scoped original replacement; converter unproven | Own mesh or per-asset CC0; need msh/sht/dds/apt conversion and retained provenance. Existing Blender tool evidence does not prove a working SWG export path | High, uncertain; round trip, load/render, collision and persistence in a disposable test slice |
| Resource/recipe board, roadmap Phase 5 | Proposal; stock-art implementation candidate | Existing terminal art could avoid new imported art. Need authoritative spawn/stat queries, UI, permissions and survey waypoint behavior; resource instance totals are still unaudited here | Medium-High, uncertain; compare displayed resource type/stats/location with survey/sample and verify expiry refresh |
| Farming planter, F90 | Researched concept; original implementation candidate | Open-art sources are references until the authorized download batch is audited. Growth/persistence, resource inputs, harvest/recipe rules and pre-CU balance are missing | High, uncertain; one planter survives relog/restart, consumes exact inputs and yields a bounded harvest with no duplication |

Prioritize completion of the existing Hoth slice before a new planet. Discuss the first regular species and the single-prop converter with owner/Claude next. Recipe-board and farming systems remain separate proposed slices. This prioritization does not authorize deployments, downloads or implementation.

### Remaining finite checkpoints and resume instructions

- [x] **1. Saved-manifest baseline:** count units, input hashes, category totals, inherited lore overlap and initial shortlist. Completed this run.
- [ ] **2. Worlds/places:** audit the 18 ground-world + three station + three other-world catalogue records; reconcile current Hoth reports; read/cite Wookieepedia Legends pages with access outcomes. Ossus is a separate owner-selected candidate to add explicitly. Build candidate rows with available/missing terrain, snapshot, art, scripts, rights, maturity and validation. Avoid treating variants as separate planets.
- [ ] **3. Species/creatures/tames:** classify the 40 species records into regular species versus variants; map mobile/pet model families, species restrictions and wild/BE tame rules using client data and dated tests.
- [ ] **4. Equipment/vehicles/structures:** split registered tangibles, weapons, buildings, ships and static props into finite families; select an auditable family per run. Deduplicate appearance variants/archive copies before estimating functional items. Resolve source/client-art permissions separately.
- [ ] **5. Professions/resources/consumables:** extract loaded client tables with the existing owner-content probe; distinguish resource classes, current resource instances, schematics and outputs. The roadmap's historical restore count of 15,020 resources is not a present spawn count. Use the owner's book only within F87-F89's limits.
- [ ] **6. Encounters/systems/tools:** join the feature register, existing test reports and licensed source/package records; retain recoverable encounters as optional adaptation or original-replacement rows.
- [ ] **7. Consolidation:** produce non-overlapping category/readiness totals, source-access gaps and prioritized vertical slices after the per-family audits.

**Next run:** checkpoint 2 only, or a smaller finite subset if its budget requires it. Start by rereading handoff/inbox, claim C21, then inspect the existing planet/catalogue records and dated Hoth evidence. Do not regenerate the dormant scan against /opt/swg while Claude holds the lock. New source reads do not authorize imports. Save any partial world list and return C21 to open again. Overall C21 remains incomplete.

## Checkpoint 2a — world/places identity and implementation matrix (14 Oct 14:16)

[World census](server-world-census.md) and [JSON](server-world-census.json): all 24 catalogue world/place rows plus Ossus normalized into 20 ground-world candidates, 3 stations, 1 Naboo city and 1 test-terrain family. Eleven exact terrain/snapshot pairs; Zeltros ZIP manifests and Ossus staging recorded separately. Seven fresh Wookieepedia search-index article extracts, direct-page access restricted; inherited and pending coverage kept distinct. Centerpoint's 40 ABY destruction, Ossus's 137 ABY Temple loss, Jakku's canon exception and Zeltros's NC licence conflict are explicit gates. No imports/game changes. Reproduce saved-data join with `tools/research/world_census.py`.

Checkpoint 2 remains partial: next pass refreshes inherited worlds/permission-held planet lore and Nova Orion's direct article, then finite dependency closure. Other category checkpoints remain open. Research pass stopped at this saved checkpoint under the AGENTS budget; no automatic additional pass or deployment implied.
