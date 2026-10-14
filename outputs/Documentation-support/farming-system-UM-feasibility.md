# Farming references and SWG feasibility

Research checkpoint: 14 October 2026, ChatGPT. Public author documentation and published source inspected; no mod packages downloaded, no imports or server changes, no in-game verification. F90 remains proposed. This is a bounded reference pass, not a complete source audit.

## Minecraft candidates

| Reference | Verified permission evidence | Useful SWG application (our inference) | Decision |
|---|---|---|---|
| [Farmer's Delight](https://github.com/vectorwing/FarmersDelight), branch 1.21 | [MIT, copyright 2020 vectorwing](https://github.com/vectorwing/FarmersDelight/blob/1.21/LICENSE) | Soil improvement, harvested ingredients and cooking; connects Botanist with Chef | Strong first reference for production and processing |
| [Mystical Agriculture](https://github.com/BlakeBr0/MysticalAgriculture), branch 1.21 | [MIT, copyright 2018 BlakeBr0](https://raw.githubusercontent.com/BlakeBr0/MysticalAgriculture/1.21/LICENSE) | Tiered seeds, watering/growth upgrades, harvesting and seed recycling | Strong progression reference; growing ores/mob drops would be a separate optional gameplay decision |
| [Croptopia](https://github.com/ExcessiveAmountsOfZombies/Croptopia), master | [MIT, copyright 2020 Thonk and Rainbowcraft2](https://github.com/ExcessiveAmountsOfZombies/Croptopia/blob/master/LICENSE) | Broad crop/fruit/food catalogue and recipe structure | Good catalogue reference; pin exact revision before reuse, not an unrestricted claim about every release |
| [AgriCraft](https://github.com/AgriCraft/AgriCraft), master | [MIT, copyright 2014 InfinityRaider](https://raw.githubusercontent.com/AgriCraft/AgriCraft/master/LICENSE) | Later plant customization, breeding/mutation design | Previously identified candidate; detailed genetics implementation not inspected in this pass |
| [Simple Greenhouses](https://github.com/Lamakaio/simplegreenhouses), main | README says mod MIT except borrowed art; [LICENSE.txt explicitly covers NeoForge MDK template files](https://github.com/Lamakaio/simplegreenhouses/blob/main/LICENSE.txt) | Central water/fertilizer inventory and configurable production in a greenhouse | Permission scope needs clarification before copying mod implementation; textures have separate provenance |
| [Botany Pots](https://github.com/Darkhax-Minecraft/BotanyPots), 1.21.1 | Repository and [creator release page](https://www.curseforge.com/minecraft/mc-mods/botany-pots) identify LGPL-2.1 | Compact placeable crop container | Useful reference; not MIT. Review exact licence and integration obligations before code reuse |
| [Bonsai Trees 4](https://github.com/davenonymous/BonsaiTrees), 1.21.1 | [Current LICENSE.md says All Rights Reserved, copyright 2025 Davenonymous](https://github.com/davenonymous/BonsaiTrees/blob/1.21.1/LICENSE.md) | Soil/sapling pot with tool-driven harvest | Current branch not cleared. Older forks indexed MIT do not establish permission for this rewritten branch; old version audit deferred |
| [Farming for Blockheads](https://github.com/TwelveIterations/FarmingForBlockheads) | [Creator release page: All Rights Reserved](https://www.curseforge.com/minecraft/mc-mods/farming-for-blockheads/license) | Seed market, fertilizer and irrigation utility concepts | Mechanics reference only; public source is not a reuse grant |
| [Serene Seasons](https://github.com/Glitchfiend/SereneSeasons) | [Creator release page: All Rights Reserved](https://www.curseforge.com/minecraft/mc-mods/serene-seasons/files/all?version=1.12.2) | Seasonal growing constraints | No code import cleared; planetary climates need an original SWG design |

The Mystical Agriculture [author description](https://www.curseforge.com/minecraft/mc-mods/mystical-agriculture) documents resource crops, growth accelerators, watering cans, automated harvesting and seed reprocessing. It credits xun468 and Quizzly for textures. Farmer's Delight's author README documents cooking and soil improvement. These are documented features, not functions exercised by us.

MIT permits adapting covered code while retaining its copyright and permission notice. That is useful for a Java-to-Lua/C++ rewrite, but Minecraft/Forge APIs do not run in Core3. No art is approved by this table: check chosen files, original contributors, exceptions and any Minecraft-derived material separately. Record exact revision, licence, file hashes and credits before importing anything. Croptopia add-ons have their own terms: [Croptopia Delight is ARR](https://www.curseforge.com/minecraft/mc-mods/croptopia-delight/license).

## Owner's ARK and Skyrim references

| Exact candidate | Findings | Reuse status |
|---|---|---|
| [Seed Farm: Grow Everything, Ascended](https://www.curseforge.com/ark-survival-ascended/mods/seed-farm), project 929334 | Upgradeable production plots, four progression tiers, configurable production. Creator CZSHomer | ARR; public source not located. The [older Evolved SeedFarm](https://steamcommunity.com/sharedfiles/filedetails/?id=1657570103) instead states CC BY-NC-ND 4.0; keep these releases separate |
| [Cannabis Skyrim Creation supplied by owner](https://creations.bethesda.net/zh-TW/skyrim/details/54116a64-83dc-4b0b-a7dd-62d377ac17fd/Cannabis_Skyrim) | Exact Creation page/package details inaccessible. Original creator's [published repository](https://github.com/madnuttah/Cannabis-Skyrim) contains Papyrus source | Original 0.1.6.2a README identifies MadNuttah/Virakotxa and CC BY-NC-SA 4.0. This is not proof of the current SE port's complete rights chain |
| [420 Pub Alien Plants Evolved](https://steamcommunity.com/sharedfiles/filedetails/?id=2080517690) | Wild gathering, grow pots, drying and processing. Supplied link identifies sgtpappybigs and KPInc425 | No explicit reuse grant established |
| [Alien Plants Ascended](https://www.curseforge.com/ark-survival-ascended/mods/alien-plants), project 964434 | KPInc425 credits original author Ugh/BlueShirtGuy. Changelog describes drying, curing, grinding and spoilage. Breeding, grow lights and mass farming remain roadmap/concept entries | ARR. Separately credits Tiko's Weed Leaf under CC BY 4.0; this does not license the whole package |

Original Skyrim source inspected: [CannabisGrowScript.psc](https://github.com/madnuttah/Cannabis-Skyrim/blob/main/Scripts/Source/CannabisGrowScript.psc), repository upload commit `8137b6084934e7d3121922b140c299cb76dfdd7b` (original 0.1.6.2a, not verified SE release). Observed seed consumption, watering to start growth, rainfall watering, successive timed stages with model replacement, mature harvest and resetting the planter. Female/male status affects output; a perk affects yield. Fertilizer menu exists but its action is a stub. Optional plant death follows a ripe period. No breeding implementation verified. Watering in this script is not a continuous moisture simulation. Its single-player global UI state and blocking stage waits should not be copied into a multiplayer server.

Creator [Virakotxa's original artist post](https://tvcgartist.wordpress.com/2015/08/03/cs-cannabis-skyrim/) corroborates placeable planting and processing concepts and lists other art contributors. Restricted licences are not equivalent to public-domain assets; no material from these packages has been cleared for our unrestricted server pipeline. Use original implementation/art or resolve specific permissions first.

## Proposed SWG system

Best combination: AgriCraft for later plant traits; Farmer's Delight for crop-to-crafting production; Mystical Agriculture for equipment/seed progression; Skyrim for visible growth; Alien Plants for processing stations. These are references, not a decision to import them all.

First slice: one owned crafted planter, one original alien crop, three visual stages, manual water input, one harvest stack and one crafting recipe. Then expand to quality, fertilizer, hydroponics, processing and optional automation. Use existing flora art only after identifying valid local templates and permissions; new original art is an alternative.

Proposed implementation requirements (Core3 bindings not yet audited):

- Persistent per-planter server state: owner, crop ID, stage, water/nutrients, growth timestamps, quality and harvest cycle ID.
- Server-authoritative elapsed time and bounded offline catch-up; sparse scheduled updates rather than a thinking NPC per plant.
- Permission checks and atomic harvest so two clients cannot duplicate a crop. Relog/restart must preserve state.
- Radial/SUI actions for planting, watering, inspecting and harvest; remove/pickup cleanup must not leave orphan visual objects.
- Integrate resulting materials with real pre-CU crafting. Preserve surveying, resource rotation and resource quality rather than silently replacing them with unlimited seed production.
- Later raw crop → drying/extraction/refining → Chef/medical/other consumables. Crop lore and names need Wookieepedia Legends sourcing when selected.

Difficulty: medium–high for a narrow planter prototype; high for persistent production, client art and native crafting integration; very high for broad field agriculture, breeding and automation together. Design maturity: researched concept; exact APIs, balance, placement/deed rules and resource representation unresolved. Claude's Botanist skill/trainer feasibility work does not itself implement planting.

## UM route and journal

UM research and reverse-engineering guides used. Published source is preferable to decompiling a compiled mod. UM CLI was not run; it is not on the current PATH. No SDK, cooked package or binary was downloaded. For a selected MIT release, the next engineering step is a pinned source/function audit and an adaptation matrix to Core3, with notices retained. ARK cooked content may expose metadata, but full Blueprint source recovery is not guaranteed; any local inspection needs an authorized copy and a rights decision before import.

Session journal: read shared board/roadmap/inbox; claimed farming research; investigated generic open-source candidates; owner narrowed ARK/Skyrim then added Alien Plants and additional Minecraft candidates; inspected original Skyrim source and author licences; caught template-only and version-specific licence pitfalls; saved this checkpoint. No code copied, no assets imported, no server modifications, no commit (documentation workspace has no Git checkout).

Open checks: choose first reference/version; inspect selected Java functions and transitive dependencies; reconcile Simple Greenhouses licence scope; audit older Bonsai branch only if selected; verify exact Skyrim Creation provenance if it becomes an import candidate. No further broad census needed for a prototype.
