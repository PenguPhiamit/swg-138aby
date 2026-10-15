# Pre-CU resources, crafting and external resource tools

14 Oct 2026 — C29 bounded research checkpoint for Claude. Source inspection and documentation only; no gameplay tests, installs, service setup or public resource submissions.

## What to build on

SWG's core loop is **find a named resource spawn → gather/stockpile it → choose materials for a particular schematic/property → assemble and experiment → make a prototype or manufacturing schematic → produce and trade**. A newer spawn is not automatically better. Scarce past spawns and good components can remain valuable after the resource leaves the world.

For this project use the existing pre-CU implementation as the mechanical baseline. The owner's new materials should enter that loop as raw resources, crafted intermediates, salvage or special items according to what they actually are. Do not make every named ingredient a surveyable ore. The complete owner-book handoff is [owner-ttrpg-resource-handoff.md](owner-ttrpg-resource-handoff.md), with a companion JSON for adaptation tooling.

## Evidence and limits

Read-only local source inspected at `/opt/swg/Core3-gpt`, commit **19f40ab89363d865f4b9d1ae9435a0099c94c595**. This is the prepared source worktree, **not proof of the running test galaxy's build/configuration**, nor an unmodified SOE implementation. Client resource-tree inspection used the existing `tools/owner_content/swg_client_data.py` reader and returned **725 rows** from the client's loaded resource tree; count includes hierarchy entries and is not a count of active spawns or fully usable new resources.

**New coordination update received 18:50:** Claude reports C25/C26 reviewed/cherry-picked/built in dev, bodies relogged 18:37, R2-F1 fixed in `98ad1d1d`, and resource coverage scaling in `3a0b154f` awaiting another test restart. This pass did not independently review those two resource commits or test the new body. Thus earlier pending-build language in related checkpoint documents is historical; the next queue is C24b independent re-review, then C23c runtime acceptance, then the remaining C29 lore work. The formulas here are explicitly from the older pinned source, not a claim to have reviewed the newer resource coverage code.

Evidence files: `C29-source-evidence.json` records hashes and inspected ranges for 15 source files; `C29-source-probe-spec.json` can be replayed with `tools/research/resource_crafting_probe.py`. `C29-client-resource-leads.json` pins the loaded table hash and eight matched class rows. Source text/game assets are not bundled into this handoff.

Technical citations below identify source paths and functions/lines in that local pin. Official upstream comparison entry point: [SWGEmu Core3](https://github.com/swgemu/Core3). Historical player accounts are corroboration of workflow, not authoritative formulas: [archived tailoring guide](https://www.swgemu.com/archive/scrapbookv51/data/20080108200838/tailor_guide.html) and [archived official-forum tailoring FAQ](https://www.swgemu.com/archive/scrapbookv51/data/20070127213347/index.html). The first full-page fetch failed; indexed passages were available. Their discussions of ingredient selection, assembly, experimentation and using the same named resource in a factory agree with the inspected code. Exact era/revision of each archived guide is not established here; do not transfer their numeric advice wholesale.

## Resources and their lifecycle

| Concept | Meaning | Consequence for development/testing |
|---|---|---|
| Resource class/type | Hierarchy and leaf, e.g. metal → ore family or a particular iron | Recipes accept classes; parent classes are not necessarily spawnable leaves |
| Named spawn | A generated unique name, type, attributes, lifetime and placement maps | Preserve spawn identity, not just the generic material label |
| Concentration/density | How much of this spawn is available at a location | Influences gathering throughput; it is not Overall Quality |
| Attributes | The rolled qualities of the spawn | Relevant properties differ by recipe and experimental line |
| Resource container | Units from one spawn in inventory/hopper | Stack splits/merges change container count without changing total units |
| Shift/despawn | Natural availability ends and pools replenish | A stored supply remains distinct from the currently surveyable supply |

`ResourceSpawner.cpp:497–548, 585–637` generates a name, rolls within the resource entry's bounds, sets expiry and creates spawn maps. Name collision checks include the resource map and resource-tree entries. `resource_manager.lua:106–131` defines minimum, random, fixed and planet-native pools. A class existing in the client table is insufficient: a pool must request a spawn and there must be valid placement/acquisition and consumers.

At this source pin, `resource_manager.lua:51–87` sets a two-hour manager scheduling interval, `aveduration=86400`, `spawnThrottling=90`, `lowerGateOverride=1000`, and `maxSpawnQuantity=0`. `ResourceSpawner::getRandomExpirationTime` selects organic lifetimes of 6–22 duration units, JTL 13–22 and other resources 6–11, testing the organic branch first. With the shown duration unit these are days. **Two-hour manager checks do not mean resources rotate every two hours.** This is source configuration, not a runtime export.

Quantity exhaustion is optional here: zero disables `maxSpawnQuantity`. Do not describe every deposit as a universally finite unit reserve. Time-limited availability and hopper capacity are separate limits. The throttle's Lua comment is broader than the implementation: `randomizeValue:606` applies the extra bias only when the throttle is **below 90**. At 90 that branch is skipped. Lower-gate override changes a minimum only when that minimum exceeds the override. Preserve these implementation details when comparing a server's resource quality distribution.

Hoth is a local extension: `resource_manager.lua:49,110–116` adds Hoth to active zones and ten Hoth-only inorganic types to the minimum pool. This does not prove all galaxy-wide resource classes populate Hoth. The separate R2 backfill/idempotence review remains open; see [R2-idempotence-proposal.md](R2-idempotence-proposal.md) and [hoth-release-gate.md](hoth-release-gate.md). Do not advertise full Hoth crafting access from the ten minimum spawns alone.

## Quality, caps and choosing materials

Common stat abbreviations: CD conductivity; CR cold resistance; DR decay resistance; ER entangle resistance; FL flavor; HR heat resistance; MA malleability; OQ overall quality; PE potential energy; SR shock resistance; UT unit toughness. Only the attributes that exist for the class/recipe matter. Resource-tree class gates determine what a spawn can roll; the schematic's experimental weights determine what a crafter values.

Concrete client check: `ore_siliclastic_cortosis` exists. Its leaf reports OQ 1–1000, SR 71–231, MA 382–568, UT 83–269 and other bounds. Thus “only buy 900+ of every stat” is impossible for this resource. Its name does not itself make armor lightsaber-immune. Special behavior requires actual item/combat code.

At the inspected pin, `SharedLabratory::getWeightedValue:73–141` computes a quantity-weighted mean for each requested stat over resource slots and qualifying custom-ingredient components, **omitting zero/missing values from both numerator and denominator**. Ordinary components are handled separately through their contributed properties. `ResourceLabratory::setInitialCraftingValues:61–107` combines those means with the recipe's property weights, sets the resource-limited maximum percentage to `weightedSum / 1000`, initializes the assembly percentage and applies component effects.

Illustration only, not a real recipe: 50% OQ and 50% CD with effective means 900 and 700 produces a weighted sum of 800 and a resource-limited fraction of 0.8 on that experimental property. This is **not** necessarily 80% of a finished weapon's displayed damage: property min/max, component contributions, combination modes and specialized laboratories also matter. The generic resource laboratory is not a complete DNA/Genetic/Droid formula specification.

`ResourceLabratory::experimentRow:120–152` clamps the updated percentage between zero and its resource-limited maximum. More experimentation cannot turn poor input resources into arbitrarily perfect raw-material potential. Good OQ alone is insufficient when a property heavily weights another attribute.

## Gathering and harvesters

Surveying requires an appropriate active survey session/tool, state and resource. Surveying and sampling tasks block incompatible simultaneous operations. `RequestSurveyCommand.h:35–64`, `RequestCoreSampleCommand.h:33–75` and `SurveySessionImplementation.cpp:63–233` handle these checks. The session checks costs, resource/tool compatibility and kneeling for sampling. This pass did not audit every range/skill/minigame/yield formula; use [SWG-professions-and-gameplay-reference.md](SWG-professions-and-gameplay-reference.md) for earlier corpse/survey source findings and verify the relevant deeper resource-manager tasks before changing rates.

Organic acquisition needs its own route. Hunting meat/hide/bone is not the same workflow as placing a flora harvester. The existing corpse review requires harvestable corpse/type/rights and one permitted harvest choice; do not test meat, hide and bone success on the same exhausted corpse. Count total units grouped by spawn, including additions to existing stacks. The owner's husbandry/cultivation ideas are optional extensions, not already-working stock farming.

`InstallationObjectImplementation.cpp:86–97` checks density and power on activation; the shown density threshold is 0.10. `getActualRate:733–740` returns extraction rate × density. `updateHopper:330–425` calculates collected units approximately as:

`elapsed permitted seconds / 60 × extraction rate × density`

It limits production to hopper capacity, keeps fractional extraction remainder, clips the working interval at spawn expiry and shuts down for a depleted spawn/full hopper. `updateMaintenance:275–327` bounds operating time by maintenance and, while active, applicable power reserves. Base rates and self-powered installations differ; read each deed/template rather than inventing one universal credit/power cost.

Illustration: BER 10 at 80% density gives a nominal 8 units/minute, or 480/hour while the installation is permitted to work, with no additional rate changes. Check actual deed extraction rate, density precision, power, maintenance, elapsed time and hopper before diagnosing a lower observed yield. Old collected contents must remain identifiable and recoverable after the spawn shifts; the harvester implementation explicitly sends old hopper spawns to the client (`HarvesterObjectImplementation.cpp:34–40`).

## Crafting, experimentation and factories

| Stage | What the code/workflow does | What a test must record |
|---|---|---|
| Learn/select | Skill-granted draft schematic, correct tool tabs and permitted complexity | Skill box, draft/template, tool, station |
| Fill slots | Required classes, quantities, and any specific component requirements | Spawn identities, unit counts and component serials |
| Assemble | Recipe assembly skill, tool effectiveness and other supported modifiers affect outcome | Actual result and starting properties |
| Experiment | Allocate limited points across experimental groups, with roll outcomes and resource ceilings | Skill mod, points/row, rolls and final properties |
| Finish | Prototype/practice or manufacturing route | Inventory/datapad evidence, actual XP and consumed inputs |
| Manufacture | Installed schematic, matching input stock, output capacity and operating requirements | Number produced, depleted inputs, crate identities and stop reason |

`CraftingSessionImplementation.cpp:129–142` filters schematic access by tool tabs and tool/station complexity and enables experimentation when a station is present. `:763–764` sets total experimentation points to the integer recipe experimentation skill mod divided by ten. `:1075–1133` bounds point spending and processes groups. `SharedLabratory::calculateAssemblySuccess` includes assembly skill, tool effectiveness and supported city/Force/food modifiers. Do not replace these with the TTRPG's d20 checks.

`SharedLabratory::calculateExperimentationValueModifier:21–57` multiplies an outcome adjustment by points attempted: amazing +0.08, great +0.07, good +0.055, moderate +0.015, success +0.01, marginal 0, OK −0.04, barely −0.07, critical −0.08. These enum outcomes are implementation details; avoid treating their names as guarantees of improvement. The failure/risk calculation in `CraftingManagerImplementation.cpp:43–55` uses weighted MA, experimentation skill and points in the attempt; inspect callers and outcome rolls before changing the UI's interpretation of that number.

Example recipe inspected: `bin/scripts/object/draft_schematic/chemistry/med_stimpack_a.lua:44–76` defines Small Stimpack A, complexity 10, medicine tool tab 64, 8 organic + 8 inorganic units, medicine assembly/experimentation skills and nominal 30 medicine-crafting XP. Experimental-property weights are not specified in this Lua override; do not invent them from the two ingredient categories. Resolve inherited/client draft data to pin its actual weights before a numerical quality comparison.

Practice awards a nominal 5% XP adjustment in `CraftingSessionImplementation.cpp:1399–1409`, subject to wider XP award/configuration. Creation normally schedules by complexity × 2 seconds there, but this local source has **`Core3.Sandbox.CraftSeconds`** at `:1422–1424`; if positive it overrides the timer. This is a project customization to identify in runtime checks, not historical pre-CU behavior. No private config was opened during this task.

Factory inputs are particularly important: `FactoryObjectImplementation.cpp:858–895` matches resources to the blueprint's **spawn name**. Components match the server-template CRC and, when the entry requires identical parts, the recorded serial. Merely buying another spawn of the same metal class, or a similarly named handmade component, can fail. Factory crates expose their contained prototype for matching. Preserve this constraint when introducing new reagents and intermediate components; record exact stock and serials during factory tests.

Stockpile premium recipe-relevant spawns for sale/use and use cheap adequate inputs for practice. This supports prospectors, hunters, component specialists, crafters and traders without giving everyone every profession. That is a design implication of the resource/recipe/identity loop, not evidence of current market prices on our private server.

## Galaxy Harvester and SWGAide

These are companion tools; neither name means a built-in remote control of our harvesters.

**Galaxy Harvester — browser resource tracker.** Its [official help](https://galaxyharvester.net/help.py) documents crowdsourced spawn/stat/planet reports, survey-droid mail import, weighted resource searching, waypoint maps, schematic ingredient/experimental references, favorites and alerts. Stock quantities are user-maintained. CSV/XML availability exports are scheduled daily at 17:00 UTC, not live telemetry. Verification ages and incomplete reporting matter. Its capped-range display score must not be substituted for Core3's crafting calculation. Custom schematics can be contributed, including Lua-based inputs, but the site's schematic coverage is incomplete. `/mailsave` saves all mail: select only the intended survey-droid report if an upload is later authorized; never submit an entire private mailbox.

The [official source repository](https://github.com/pwillworth/galaxyharvester) contains CGI web code, database setup, scheduled export/cleanup/alert scripts and experimental Docker setup. Its README lists an older Apache/MySQL-or-MariaDB/Python stack; that is not a validated modern deployment/security recipe. The [licence file](https://raw.githubusercontent.com/pwillworth/galaxyharvester/master/LICENSE.md) contains **GNU GPL v3**. A private self-hosted copy is a plausible option after dependency, database and data-rights review. Retain notices; review corresponding-source obligations before distributing modified software. Code licensing does not automatically license imported community databases or art.

**SWGAide-Unity — desktop companion.** Despite the old repository name `SWGAide-NGE`, its [official installation page](https://swgaide.com/swgaide_download_install.html) says Unity supports pre-CU, NGE and custom schematics. It uses the installed game's directory/mail files and has resource, inventory, schematic and crafting-planning panels. The [official repository](https://github.com/twistedatrocity/SWGAide-NGE) identifies a GPL-2.0 licence; exact file notices and dependency terms still need an import audit before a fork.

Its [harvesting-panel documentation](https://swgaide.com/swgaide_help_resources_harvesting_en.html) describes configured harvester BER, hopper size, concentration, maintenance and power, with estimated fill/exhaustion alerts and optional inventory bookkeeping. These are estimates based on entered information, not proof of an automatic authoritative server feed. That page also includes later-era expertise/entertainer bonuses: do not transplant those to pre-CU. The [class-cap panel](https://swgaide.com/swgaide_help_resources_rinfo_en.html) is useful for examining class bounds, but our custom classes need matching definitions.

The [SWGAide backend description](https://swgaide.com/about.html) says it aggregates feeds and can forward linked-account reports to SWGCraft. For a private/LAN or invite-only test galaxy, do not create accounts, enable linked submissions or publish galaxy spawn/waypoint data without the owner's explicit approval. Nothing was installed, registered or submitted in this pass.

### Proposed integration sequence

1. **Local resource snapshot first:** epoch, observed time, spawn ID/name, exact leaf/parents, attributes, active planet presence and availability. Confirm source commit and effective safe rate settings without exporting private config. Keep archival spawns separate from current availability.
2. **Player-observed map data separately:** locations/concentrations actually surveyed, observation time and character visibility. An admin resource-map export would reveal hidden optimal spots; label it developer-only and keep it separate from tester knowledge.
3. **Own inventory/harvester records:** units, spawn identity, deed extraction/hopper capacity, operating state and observations. Predictions should say estimated; actual receipts should say observed.
4. **Private local reader/planner:** reuse concepts or a reviewed, pinned companion tool. Prefer a minimal local exporter/viewer before running a legacy public web stack. No DB credentials in the browser and no server mutation through the monitor.
5. **Public integration only if desired later:** owner approval, selected galaxy identity, sanitized data and verified feed contract. GH exports and SWGAide consumers have not been compatibility-tested with this galaxy.

Proposed minimal data boundary: C26 inventory-unit/spawn telemetry is for player holdings; it is not a galaxy-wide resource export. C28 fleet position telemetry is another producer. A passive resource snapshot should not seize bot drivers or issue commands during overnight rounds. A test-galaxy restore needs an epoch change so cached spawn identities/locations are not mixed across restored worlds.

## Claude's next ordinary-player checks

These are **proposed**, not executed in C29:

- Record effective source/archive pin and resource-manager settings. Survey one existing planet and Hoth across mineral, gas, chemical, water and flora tools; distinguish no tool, no matching spawn and inaccessible geography.
- Sample a known named spawn at two concentrations. Record actual before/after units, existing-stack merges, time, skill and XP; do not use chat messages/container count as a substitute.
- Hunt separate eligible corpses for meat/hide/bone, checking permissions, nonharvestable corpses and repeated harvest rejection. Test milk/flora through their own acquisition routes.
- Place a normally crafted harvester, supply maintenance/power, measure a short controlled interval and compare to deed BER × concentration. Exercise full hopper, depletion, power/maintenance stops and retained old contents.
- Craft a basic tool and Small Stimpack A normally. Resolve the exact inherited weights, then compare two resource sets while controlling tool/station/skill. Show actual experimentation bounds, practice versus prototype, XP and resource consumption.
- Create one manufacturing schematic and run a small factory batch. Verify exact-spawn substitution rejection and identical-component serial handling where the chosen recipe requires it; verify crate output and stop-on-missing-input behavior.
- Test one survey-droid report and companion-tool import using a synthetic/local fixture first. Public uploads are a separate owner decision.

Readiness dependencies already recorded: Esk setup exception covered gear/skills, not admin permissions or a full crafting stockpile. Lira had mineral/liquid tools but chemical/gas/moisture/flora tools were still missing at last observed checkpoint. Claude now reports C26 built; its acceptance remains pending. The Hoth gameplay gate remains NO-GO pending the independent update. Claude also identifies the armor rejection as ordinary pre-CU cumulative encumbrance; use normal buffs/food or lighter armor, not a stat bypass. Do not label missing prerequisites or unverified telemetry as a proven crafting-system defect.

## Open questions after this pass

Exact running galaxy configuration; inherited weights for representative recipes; all specialized-laboratory formulas; current SWGAide private-server/offline/custom-class import behavior; a pinned Galaxy Harvester deployment's dependency/security audit and data licences; complete class coverage on new planets. These need focused follow-ups, not an assumption that public-server tools are drop-in compatible. No source or in-game behavior was changed by this research.
